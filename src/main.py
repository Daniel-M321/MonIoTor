import time
from datetime import datetime

from gpiozero import MCP3008

from sensors import check_float_switch
from sensors import check_smoke_level


# function to create line protocol needed to store in db

def create_line_protocol(sensor: str, reading: str, value):
    line: str = "{} {}={} {}"
    timestamp = str(int(datetime.now().timestamp() * 1000))
    return line.format(sensor, reading, value, timestamp)


# read SPI data from MCP3008 chip,8 possible adc's (0 through 7)

def read_adc(adcnum):
    if (adcnum > 7) or (adcnum < 0):
        return -1

    #sensor_value = MCP3008(channel=adcnum, clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=8)
    sensor_value = 100

    return sensor_value


# main loop
def main():
    while True:
        fs = check_float_switch()
        #float_switch_data(fs)
        time.sleep(0.1)
        check_smoke_level(read_adc(0))
        time.sleep(0.5)


# ---------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------
if __name__ == '__main__':
    try:
        main()
        pass
    except KeyboardInterrupt:
        pass
