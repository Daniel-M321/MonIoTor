import time
from datetime import datetime

from sensors import check_float_switch, read_adc, humidity_and_temp, motion_sensor
from sensors import check_smoke_level
import psutil


# function to create line protocol needed to store in db
def create_line_protocol(sensor: str, reading: str, value):
    line: str = "{} {}={} {}"
    timestamp = str(int(datetime.now().timestamp() * 1000))
    return line.format(sensor, reading, value, timestamp)


# main loop
def main():
    for proc in psutil.process_iter():
        if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
            proc.kill()
    while True:
        #fs = check_float_switch()
        #float_switch_data(fs)
        time.sleep(1.5)
        humidity_and_temp()
        if motion_sensor() == 1:
            print("motion detected")
        elif motion_sensor() == 0:
            print("no motion")
        time.sleep(0.5)
        check_smoke_level(read_adc(0))
        time.sleep(5)


# ---------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------
if __name__ == '__main__':
    try:
        main()
        pass
    except KeyboardInterrupt:
        pass
