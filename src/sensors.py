import time

from gpiozero import DigitalInputDevice, BadPinFactory, MotionSensor, MCP3008
import adafruit_dht
import board

# Todo have a class in main loop that initiliases all the sensors to be used
# in main method sleep for seconds, but store in database in minutes


class mySensors:
    def __init__(self):
        try:
            self.float_switch = DigitalInputDevice(2)
            self.pir = MotionSensor(4, queue_len=10, sample_rate=20, threshold=0.7)
            self.dht_sensor = adafruit_dht.DHT11(board.D27, use_pulseio=False)
        except Exception as e:
            print("Issue with initiliasing a sensor: ", e.args)



# read SPI data from MCP3008 chip,8 possible adc's (0 through 7)
def read_adc(adcnum: int) -> float:
    if (adcnum > 7) or (adcnum < 0):
        return -1

    sensor = MCP3008(channel=adcnum, clock_pin=18, mosi_pin=15, miso_pin=17, select_pin=14)

    return sensor.value


def check_float_switch() -> str:
    try:
        float_switch = DigitalInputDevice(2)
    except BadPinFactory as e:
        print(e)
        return "no float switch"

    if float_switch.is_active:
        return "There is flood"
    else:
        return "There is no flood"


def check_smoke_level(co_level: float) -> int:
    smoke_trigger = ((co_level / 1024.) * 3.3)

    if smoke_trigger > 1.5:
        print("Gas leakage")
        # call user
        print("Current Gas AD value = " + str("%.2f" % ((co_level / 1024.) * 3.3)) + " V")
        return 0

    else:
        print("Gas not leak: "+str(co_level))
        return 1


def motion_sensor() -> int:
    try:
        pir = MotionSensor(4, queue_len=10, sample_rate=20, threshold=0.7)
    except Exception as e:
        print("motion sensor not detected I think", e.args)
        return -1

    print(pir.value)
    if pir.motion_detected:  # fixme https://static.raspberrypi.org/files/education/posters/GPIO_Zero_Cheatsheet.pdf
        return 1
    else:
        return 0


def humidity_and_temp() -> float:
    sensor = adafruit_dht.DHT11(board.D27, use_pulseio=False)
    hum = None
    retries = 15
    error = None

    while retries >= 1 and hum is None:
        try:
            hum = sensor.humidity
            temp = sensor.temperature

            if hum is not None:
                print('Temp=' + str(temp) + '*C \tHumidity=' + str(hum) + '%')
        except RuntimeError as e:
            error = "DHT failure: ", e.args
        time.sleep(1)
        retries -= 1

    if hum is None and error:
        print(error)

    return 1
