import time

from gpiozero import DigitalInputDevice, MotionSensor, MCP3008  # type: ignore
import adafruit_dht                                             # type: ignore
import board                                                    # type: ignore

# in main method sleep for seconds, but store in database in minutes
from src.eventhandler import text_user


class MySensors:
    motion_counter: int
    alarm: bool
    user_called: bool

    def __init__(self, calibrate: bool = False, calibration_times: int = 30):
        try:
            self.float_switch = DigitalInputDevice(2)
            self.pir = MotionSensor(4, queue_len=10, sample_rate=20, threshold=0.7)
            self.dht_sensor = adafruit_dht.DHT11(board.D27, use_pulseio=False)
        except Exception as e:
            raise RuntimeError("Issue with initiliasing a sensor: ", e.args)
        self.motion_counter = 0
        self.alarm = False
        self.user_called = False

        if calibrate:
            self.dht_calibration(retries=calibration_times)
            self.pir_calibration(retries=calibration_times)

    def check_float_switch(self) -> str:
        if self.float_switch.is_active:
            # call_user("Water has been detected in your house.")
            # db
            return "There is flood"
        else:
            return "There is no flood"

    def motion_sensor(self) -> int:
        print(self.pir.value)
        if self.pir.motion_detected:  # fixme https://static.raspberrypi.org/files/education/posters/GPIO_Zero_Cheatsheet.pdf
            return 1
        else:
            return 0

    def humidity_and_temp(self, retries=15) -> float:
        humid = None
        error = "DHT failure: Unexpected error, humidity & temperature have no values, check sensor"

        while retries >= 1 and not humid:
            try:
                humid = self.dht_sensor.humidity
                temp = self.dht_sensor.temperature

                if humid:
                    print('Temp: {0:0.1f} C  \tHumidity: {1:0.1f} %'.format(temp, humid))
                    if temp > 40:
                        print("abnormal temperature detected in your home: " + str(temp) + " C")
                        text_user("abnormal temperature detected in your home: "+str(temp) + " C")
            except RuntimeError as e:
                error = "DHT failure: " + str(e.args)
            time.sleep(1)
            retries -= 1

        if not humid:
            print(error)
            return 0

        return 1

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
        print("DHT11 Calibration complete. Error rate: {rate}".format(rate=error_rate)+"\n")
