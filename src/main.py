import time
from datetime import datetime
from sensors import MySensors       # type: ignore
from src.influx import MyDatabase   # type: ignore
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

    database_counter = 0

    print("Performing calibration on sensors, this may take a while...")
    my_sensors = MySensors(calibrate=True)
    mq = MQ()
    time.sleep(5)
    myDB = MyDatabase()
    while True:
        database_counter += 1
        print("----------------------------------------")
        my_sensors.check_float_sensor()
        time.sleep(0.5)
        humid, temp = my_sensors.humidity_and_temp()

        motion = my_sensors.motion_sensor()
        if my_sensors.alarm and motion == 1:  # motion counter and alarm variable
            my_sensors.motion_counter += 1
            if my_sensors.motion_counter == 3 and not my_sensors.user_called:  # make sure user not already called
                my_sensors.motion_counter = 0
                call_user("Motion detected in your house")
                my_sensors.user_called = True
        if not my_sensors.alarm and my_sensors.user_called:  # removes potential previous tag
            my_sensors.user_called = False
        time.sleep(0.5)

        gas_percents = mq.MQPercentage()
        lpg_val = gas_percents["GAS_LPG"]
        co_val = gas_percents["CO"]
        smoke_val = gas_percents["SMOKE"]
        print("LPG: {lpg} ppm, CO: {co} ppm, Smoke: {smoke} ppm".format(lpg=lpg_val, co=co_val, smoke=smoke_val))
        if lpg_val > 100:
            #my_sensors.gas_counter += 1
            print("LPG values exceeded nominal values")
            call_user("High L.P.G. values detected")
        if co_val > 25:
            print("CO values exceeded nominal values")
            call_user("High Carbon dioxide values detected")
        if smoke_val > 200:
            print("smoke level exceeded nominal values")
            call_user("High smoke values detected")

        if database_counter == 300:
            if humid != 0:
                myDB.write_db("Temperature", ["tag0", "Kitchen"], "temperature", temp)
                myDB.write_db("Humidity", ["tag0", "Kitchen"], "humidity", humid)

            myDB.write_db("CO", ["tag0", "Kitchen"], "carbon monoxide", co_val)
            myDB.write_db("LPG", ["tag0", "Kitchen"], "lpg", lpg_val)
            myDB.write_db("Smoke", ["tag0", "Kitchen"], "smoke", smoke_val)

            database_counter = 0

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
