import time
from datetime import datetime
from sensors import MySensors       # type: ignore

import psutil

from src.eventhandler import call_user


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

    my_sensors = MySensors()
    while True:
        #fs = my_sensors.check_float_switch()
        time.sleep(1.5)
        my_sensors.humidity_and_temp()

        if my_sensors.motion_sensor() == 1 and my_sensors.alarm:
            print("motion detected")
            my_sensors.motion_counter += 1
            if my_sensors.motion_counter == 3 and not my_sensors.user_called:
                my_sensors.motion_counter = 0  # fixme need to reset after user has been called
                call_user("Motion detected in your house")
        elif my_sensors.motion_sensor() == 0:
            print("no motion")
        time.sleep(0.5)

        my_sensors.check_smoke_level(my_sensors.read_adc(0))
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
