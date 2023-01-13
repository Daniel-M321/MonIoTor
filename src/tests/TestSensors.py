import unittest

from unittest.mock import patch, Mock
from src.mq2 import MQ
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
        self.humidity = 0

    def activity(self) -> None:
        self.is_active = True
        self.value = 0.9
        self.motion_detected = True
        self.humidity = 50

    def read(self, pin: int) -> float:
        return 50

    def measure(self) -> None:
        print("measured")


class TestSensors(unittest.TestCase):
    fakeDevice = FakeDevice(4)

    @patch("src.sensors.MotionSensor", return_value=fakeDevice)
    @patch("src.sensors.DigitalInputDevice", return_value=fakeDevice)
    @patch("src.sensors.adafruit_dht.DHT11", return_value=fakeDevice)
    @patch("src.sensors.board", return_value=fakeDevice)
    def setUp(self, board_mock, dht_mock, device_mock, pir_mock):
        self.my_sensors = MySensors()

    # @patch("src.sensors.MotionSensor", return_value=fakeDevice)
    # @patch("src.sensors.DigitalInputDevice", return_value=fakeDevice)
    # def test_sensor_error(self, dht_mock):
    #     with self.assertRaises(RuntimeError) as context:
    #         MySensors()
    #     self.assertEqual(
    #         context.exception.args,
    #         ('Issue with initiliasing a sensor: ', ("module 'board' has no attribute 'D27'",))
    #     )

    @patch("src.sensors.MotionSensor", return_value=fakeDevice)
    @patch("src.sensors.DigitalInputDevice", return_value=fakeDevice)
    @patch("src.sensors.adafruit_dht.DHT11", return_value=fakeDevice)
    @patch("src.sensors.board", return_value=fakeDevice)
    def test_sensor_calibration(self, board_mock, dht_mock, device_mock, pir_mock):
        MySensors(calibrate=True, calibration_times=2)

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

    @patch("src.sensors.call_user", return_value=None)
    def test_smoke_level_bad(self, call_mock):
        self.assertEqual(self.my_sensors.check_smoke_level(500), 0)

    @patch("src.mq2.MCP3008", return_value=fakeDevice)
    def test_mq(self, mcp_mock):
        mq = MQ(READ_SAMPLE_INTERVAL=5, CALIBRATION_SAMPLE_INTERVAL=5)
        self.assertEqual(
            mq.MQPercentage(),
            {'CO': 0.004963269307602389, 'GAS_LPG': 0.007659007247994245, 'SMOKE': 0.02043459613031669}
        )

    # motion sensor tests ########
    def test_motion_sensor_motion(self):
        self.assertEqual(self.my_sensors.motion_sensor(), 1)

    def test_motion_sensor_inactive(self):
        self.fakeDevice.inactivity()
        self.assertEqual(self.my_sensors.motion_sensor(), 0)
        self.fakeDevice.activity()

    # dht sensor tests ###########
    def test_dht_ok(self):
        self.assertEqual(self.my_sensors.humidity_and_temp(retries=1), 1)

    @patch("src.sensors.text_user", return_value=None)
    def test_dht_high_temp(self, text_mock):
        self.fakeDevice.temperature = 50
        self.assertEqual(self.my_sensors.humidity_and_temp(), 1)
        self.fakeDevice.temperature = 20

    def test_dht_inactive(self):
        self.fakeDevice.inactivity()
        self.assertEqual(self.my_sensors.humidity_and_temp(retries=1), 0)
        self.fakeDevice.activity()

    # adc tests ##################
    @patch("src.sensors.MCP3008", return_value=FakeDevice(0))
    def test_adc(self, adc_mock):
        self.assertEqual(self.my_sensors.read_adc(0), 0.9)

    def test_adc_incorrect_pin(self):
        self.assertEqual(self.my_sensors.read_adc(9), -1)
