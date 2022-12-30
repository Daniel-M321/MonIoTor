from gpiozero import DigitalInputDevice, BadPinFactory, MotionSensor


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
        #email_user("CO2")
        print("Current Gas AD value = " + str("%.2f" % ((co_level / 1024.) * 3.3)) + " V")
        return 0

    else:
        print("Gas not leak")
        return 1


def motion_sensor() -> int:
    pir = MotionSensor(3)

    if pir.is_active:
        return 1
    else:
        return 0
