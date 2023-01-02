from gpiozero import DigitalInputDevice, BadPinFactory, MotionSensor, MCP3008
from pigpio_dht import DHT11

# Todo have a class in main loop that initiliases all the sensors to be used
# in main method sleep for seconds, but store in database in minutes


# read SPI data from MCP3008 chip,8 possible adc's (0 through 7)

def read_adc(adcnum):
    if (adcnum > 7) or (adcnum < 0):
        return -1

    sensor_value = MCP3008(channel=adcnum, clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=8)
    sensor_value = 100

    return sensor_value


def check_float_switch() -> str:
    try:
        float_switch = DigitalInputDevice(4)
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
        print("Gas not leak")
        return 1


def motion_sensor() -> int:
    pir = MotionSensor(3)

    if pir.is_active: #fixme https://static.raspberrypi.org/files/education/posters/GPIO_Zero_Cheatsheet.pdf
        return 1
    else:
        return 0


def humidity_and_temp() -> str:
    sensor = DHT11(6)
    result = sensor.read()

    print(result)
    return result
