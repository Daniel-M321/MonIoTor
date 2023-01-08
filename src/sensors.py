import time

from gpiozero import DigitalInputDevice, MotionSensor, MCP3008
import adafruit_dht
import board

# in main method sleep for seconds, but store in database in minutes


class MySensors:
    motion_counter: int
    alarm: bool
    user_called: bool

    def __init__(self):
        try:
            self.float_switch = DigitalInputDevice(2)
            self.pir = MotionSensor(4, queue_len=10, sample_rate=20, threshold=0.7)
            self.dht_sensor = adafruit_dht.DHT11(board.D27, use_pulseio=False)
        except Exception as e:
            print("Issue with initiliasing a sensor: ", e.args)
        self.motion_counter = 0
        self.alarm = False
        self.user_called = False

    # read SPI data from MCP3008 chip,8 possible adc's (0 through 7)
    def read_adc(self, adcnum: int) -> float:
        if (adcnum > 7) or (adcnum < 0):
            return -1

        sensor = MCP3008(channel=adcnum, clock_pin=18, mosi_pin=15, miso_pin=17, select_pin=14)

        return sensor.value

    def check_float_switch(self) -> str:
        if self.float_switch.is_active:
            return "There is flood"
        else:
            return "There is no flood"

    def check_smoke_level(self, co_level: float) -> int:
        smoke_trigger = ((co_level / 1024.) * 3.3)

        if smoke_trigger > 1.5:
            print("Gas leakage")
            # call user
            print("Current Gas AD value = " + str("%.2f" % ((co_level / 1024.) * 3.3)) + " V")
            return 0

        else:
            print("Gas not leak: " + str(co_level))
            return 1

    def motion_sensor(self) -> int:
        print(self.pir.value)
        if self.pir.motion_detected:  # fixme https://static.raspberrypi.org/files/education/posters/GPIO_Zero_Cheatsheet.pdf
            return 1
        else:
            return 0

    def humidity_and_temp(self, retries=15) -> float:
        humid = None
        error = "DHT failure: Unexpected error, humidity & temperature have no values, check sensor"

        while retries >= 1 and humid is None:
            try:
                humid = self.dht_sensor.humidity
                temp = self.dht_sensor.temperature

                if humid is not None:
                    print('Temp: {0:0.1f} C  \tHumidity: {1:0.1f} %'.format(temp, humid))
            except RuntimeError as e:
                error = "DHT failure: ", e.args
            time.sleep(1)
            retries -= 1

        if humid is None:
            print(error)
            return 0

        return 1
