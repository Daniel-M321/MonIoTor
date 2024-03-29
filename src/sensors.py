import time

from gpiozero import DigitalInputDevice, MotionSensor, MCP3008, Button, LED  # type: ignore
import adafruit_dht                                             # type: ignore
import board                                                    # type: ignore


class MySensors:
    motion_counter: int
    alarm: bool
    user_called: bool
    high_gas: bool
    gas_counter: int

    def __init__(self, event_handler, calibrate: bool = False, calibration_times: int = 30):
        try:
            self.float_sensor = MCP3008(channel=1, clock_pin=18, mosi_pin=15, miso_pin=17, select_pin=14)
            self.pir = MotionSensor(4, queue_len=10, sample_rate=20, threshold=0.5)
            self.dht_sensor = adafruit_dht.DHT11(board.D27, use_pulseio=False)
            self.button = DigitalInputDevice(23)
            self.led = LED(22)
        except Exception as e:
            raise RuntimeError("Issue with initiliasing a sensor: ", e.args)
        self.event_handler = event_handler
        self.motion_counter = 0
        self.alarm = False
        self.led.off()
        self.user_called = False
        self.high_gas = False
        self.gas_counter = 0
        self.pir.when_activated = self.motion_sensor
        self.temp_counter = 0
        self.humid_counter = 0

        if calibrate:
            self.dht_calibration(retries=calibration_times)
            self.pir_calibration(retries=calibration_times)

    def check_alarm(self):
        if self.button.is_active:
            if not self.alarm:
                self.user_called = False
                self.alarm = True
                self.led.on()
        else:
            if self.alarm:
                self.alarm = False
                self.led.off()

    def check_float_sensor(self) -> int:
        if self.float_sensor.voltage >= 0.2:
            # call_user("Water has been detected in your house.") #uncomment later
            print(str(self.float_sensor.voltage)+": Water detected")
            return 1
        else:
            print(str(self.float_sensor.voltage)+": No water")
            return 0

    def motion_sensor(self) -> None:
        print(str(self.pir.value)+": Motion detected")

        if self.alarm:  # motion counter and alarm variable
            self.motion_counter += 1
            if self.motion_counter == 3 and not self.user_called:  # make sure user not already called
                self.motion_counter = 0
                self.event_handler.call_user("Motion detected in your house")
                self.user_called = True

        return None

    def humidity_and_temp(self, retries=15) -> tuple[float, float]:
        humid = None
        temp = None
        error = "DHT failure: Unexpected error, humidity & temperature have no values, check sensor"

        while retries >= 1 and not humid:
            try:
                humid = self.dht_sensor.humidity
                temp = self.dht_sensor.temperature

                if humid:
                    print('Temp: {0:0.1f} C  \tHumidity: {1:0.1f} %'.format(temp, humid))
                    if temp > 30 or temp < 10:
                        self.temp_counter += 1
                        print("abnormal temperature detected in your home: " + str(temp) + " C")
                        if self.temp_counter == 5:
                            self.event_handler.text_user("abnormal temperature detected in your home: "+str(temp)+" C")
                    else:
                        self.temp_counter = 0

                    if humid > 75 or humid < 20:
                        self.humid_counter += 1
                        print("abnormal humidity detected in your home: " + str(humid) + "%")
                        if self.humid_counter == 5:
                            self.event_handler.text_user("abnormal humidity detected in your home: " + str(humid) + "%")
                    else:
                        self.humid_counter = 0
            except RuntimeError as e:
                error = "DHT failure: " + str(e.args)
            time.sleep(1)
            retries -= 1

        if not humid:
            print(error)
            return 0, 0

        return humid, temp      # type: ignore

    def pir_calibration(self, retries: int = 30) -> None:
        print("Calibrating PIR motion sensor...")
        for i in range(1, retries):
            print("PIR VALUE:" + str(self.pir.value))
        print("PIR motion sensor Calibration complete.\n")

    def dht_calibration(self, retries: int) -> None:
        error = 0
        print("Calibrating DHT11 Temperature and Humidity sensor...")
        for i in range(1, retries):
            try:
                self.dht_sensor.measure()
            except RuntimeError:
                error += 1
            time.sleep(1)

        error_rate = (error/30)*100
        print("DHT11 Calibration complete. Error rate: {rate}%".format(rate=error_rate)+"\n")
