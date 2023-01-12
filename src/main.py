import time
from datetime import datetime
from sensors import MySensors       # type: ignore
from src.mq2 import MQ              # type: ignore

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

    print("Performing calibration on sensors, this may take a while...")
    my_sensors = MySensors(calibrate=True)
    mq = MQ()
    while True:
        #fs = my_sensors.check_float_switch()
        time.sleep(1.5)
        my_sensors.humidity_and_temp()

        if my_sensors.alarm and my_sensors.motion_sensor() == 1:
            print("motion detected")
            my_sensors.motion_counter += 1
            if my_sensors.motion_counter == 3 and not my_sensors.user_called:
                my_sensors.motion_counter = 0
                call_user("Motion detected in your house")
                my_sensors.user_called = True
        elif my_sensors.motion_sensor() == 0:
            print("no motion")
        if not my_sensors.alarm and my_sensors.user_called:
            my_sensors.user_called = False
        time.sleep(0.5)

        # my_sensors.check_smoke_level(my_sensors.read_adc(0))
        gas_percents = mq.MQPercentage()
        lpg_val = gas_percents["GAS_LPG"]
        co_val = gas_percents["CO"]
        smoke_val = gas_percents["SMOKE"]
        print("LPG: {lpg} ppm, CO: {co} ppm, Smoke: {smoke} ppm".format(lpg=lpg_val, co=co_val, smoke=smoke_val))
        if lpg_val > 1.5:
            print("LPG values exceeded nominal values")
            call_user("High L.P.G. values detected")
        if co_val > 1.5:
            print("CO values exceeded nominal values")
            call_user("High Carbon dioxide values detected")
        if smoke_val > 1.5:
            print("smoke level exceeded nominal values")
            call_user("High smoke values detected")
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
