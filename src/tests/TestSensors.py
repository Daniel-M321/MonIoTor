import unittest

from unittest.mock import patch
from src.sensors import MySensors


class FakeDevice:
    def __init__(self, number: int):
        self.number = number
        self.is_active = True
        self.value = 0.9
        self.motion_detected = True
        self.pin = number
        self.humidity = 50
        self.temperature = 20
        self.D27 = 4

    def inactivity(self) -> None:
        self.is_active = False
        self.value = 0
        self.motion_detected = False

    def activity(self) -> None:
        self.is_active = True
        self.value = 0.9
        self.motion_detected = True


class TestSensors(unittest.TestCase):
    fakeDevice = FakeDevice(4)

    @patch("src.sensors.MotionSensor", return_value=fakeDevice)
    @patch("src.sensors.DigitalInputDevice", return_value=fakeDevice)
    @patch("src.sensors.adafruit_dht.DHT11", return_value=fakeDevice)
    @patch("src.sensors.board", return_value=fakeDevice)
    def setUp(self, board_mock, dht_mock, device_mock, pir_mock):
        self.my_sensors = MySensors()

    # fixme takes a while and accesses some internal files
    # @patch("src.sensors.MotionSensor", return_value=fakeDevice)
    # @patch("src.sensors.adafruit_dht.DHT11", return_value=FakeDHT(pin=4))
    # def test_no_sensors(self, dht_mock, pir_mock):
    #     self.assertRaises(Exception, MySensors())

    # float switch tests #########
    def test_float_switch_flood(self):
        self.assertEqual(self.my_sensors.check_float_switch(), "There is flood")

    def test_float_switch_noflood(self):
        self.fakeDevice.inactivity()
        self.assertEqual(self.my_sensors.check_float_switch(), "There is no flood")
        self.fakeDevice.activity()

    # smoke level tests #########
    def test_smoke_level_ok(self):
        self.assertEqual(self.my_sensors.check_smoke_level(100), 1)

    def test_smoke_level_bad(self):
        self.assertEqual(self.my_sensors.check_smoke_level(500), 0)

    # motion sensor tests ########
    def test_motion_sensor_motion(self):
        self.assertEqual(self.my_sensors.motion_sensor(), 1)

    def test_motion_sensor_inactive(self):
        self.fakeDevice.inactivity()
        self.assertEqual(self.my_sensors.motion_sensor(), 0)
        self.fakeDevice.activity()

    # dht sensor tests ###########
    def test_dht_ok(self):
        self.assertEqual(self.my_sensors.humidity_and_temp(), 1)

    # def test_dht_failure(self):
    #     #self.fakeDht.inactive()
    #     with self.assertRaises(RuntimeError) as context:
    #         self.my_sensors.humidity_and_temp(retries=1)

    # adc tests ##################
    @patch("src.sensors.MCP3008", return_value=FakeDevice(0))
    def test_adc(self, adc_mock):
        self.assertEqual(self.my_sensors.read_adc(0), 0.9)

    def test_adc_incorrect_pin(self):
        self.assertEqual(self.my_sensors.read_adc(9), -1)
