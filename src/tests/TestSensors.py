import unittest

from unittest.mock import patch
from src.sensors import check_float_switch, check_smoke_level, motion_sensor


class FakeDevice:
    def __init__(self, number: int):
        self.number = number
        if self.number == 4:
            self.is_active = True
        else:
            self.is_active = False


class TestSensors(unittest.TestCase):

    # float switch tests #########
    @patch("src.sensors.DigitalInputDevice", return_value=FakeDevice(number=4))
    def test_float_switch_flood(self, device_mock):
        self.assertEqual(check_float_switch(), "There is flood")

    @patch("src.sensors.DigitalInputDevice", return_value=FakeDevice(number=5))
    def test_float_switch_noflood(self, device_mock):
        self.assertEqual(check_float_switch(), "There is no flood")

    def test_float_switch_inactive(self):
        self.assertEqual(check_float_switch(), "no float switch")

    # smoke level tests #########
    def test_smoke_level_ok(self):
        self.assertEqual(check_smoke_level(100), 1)

    def test_smoke_level_bad(self):
        self.assertEqual(check_smoke_level(500), 0)

    # motion sensor tests ########
    @patch("src.sensors.MotionSensor", return_value=FakeDevice(number=4))
    def test_motion_sensor_motion(self, sensor_mock):
        self.assertEqual(motion_sensor(), 1)

    @patch("src.sensors.MotionSensor", return_value=FakeDevice(number=5))
    def test_motion_sensor_inactive(self, sensor_mock):
        self.assertEqual(motion_sensor(), 0)
