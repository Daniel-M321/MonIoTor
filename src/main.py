import time
from datetime import datetime

from sensors import check_float_switch, read_adc
from sensors import check_smoke_level


# function to create line protocol needed to store in db

def create_line_protocol(sensor: str, reading: str, value):
    line: str = "{} {}={} {}"
    timestamp = str(int(datetime.now().timestamp() * 1000))
    return line.format(sensor, reading, value, timestamp)


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
