import unittest

from unittest.mock import patch
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
        self.voltage = 2

    def inactivity(self) -> None:
        self.is_active = False
        self.value = 0
        self.motion_detected = False
        self.humidity = 0
        self.voltage = 0

    def activity(self) -> None:
        self.is_active = True
        self.value = 0.9
        self.motion_detected = True
        self.humidity = 50
        self.voltage = 2

    def measure(self) -> None:
        print("measured")

    def wait_for_motion(self, timeout: float) -> None:
        pass

    def on(self):
        self.is_active = True

    def off(self):
        self.is_active = False

    def text_user(self, message) -> None:
        pass

    def call_user(self, message) -> None:
        pass


class TestSensors(unittest.TestCase):
    fakeDevice = FakeDevice(4)

    @patch("src.sensors.MotionSensor", return_value=fakeDevice)
    @patch("src.sensors.MCP3008", return_value=fakeDevice)
    @patch("src.sensors.adafruit_dht.DHT11", return_value=fakeDevice)
    @patch("src.sensors.board", return_value=fakeDevice)
    @patch("src.sensors.LED", return_value=fakeDevice)
    @patch("src.sensors.DigitalInputDevice", return_value=fakeDevice)
    def setUp(self, button_mock, led_mock, board_mock, dht_mock, device_mock, pir_mock):
        self.my_sensors = MySensors(self.fakeDevice)

    # @patch("src.sensors.adafruit_dht.DHT11", return_value=fakeDevice)
    # @patch("src.sensors.board", return_value=testingg())
    # @patch("src.sensors.MotionSensor", return_value=fakeDevice)
    # @patch("src.sensors.MCP3008", return_value=fakeDevice)
    # def test_sensor_error(self, adc_mock, pir_mock, board_mock, dht_mock):
    #     MySensors()
    #     with self.assertRaises(RuntimeError) as context:
    #         MySensors()
    #     self.assertEqual(
    #         context.exception.args,
    #         ('Issue with initiliasing a sensor: ', ("module 'board' has no attribute 'D27'",))
    #     )

    @patch("src.sensors.MotionSensor", return_value=fakeDevice)
    @patch("src.sensors.MCP3008", return_value=fakeDevice)
    @patch("src.sensors.adafruit_dht.DHT11", return_value=fakeDevice)
    @patch("src.sensors.board", return_value=fakeDevice)
    @patch("src.sensors.LED", return_value=fakeDevice)
    @patch("src.sensors.DigitalInputDevice", return_value=fakeDevice)
    def test_sensor_calibration(self, button_mock, led_mock, board_mock, dht_mock, device_mock, pir_mock):
        MySensors(self.fakeDevice, calibrate=True, calibration_times=2)

    # float switch tests #########
    def test_float_switch_flood(self):
        self.assertEqual(self.my_sensors.check_float_sensor(), 1)

    def test_float_switch_noflood(self):
        self.fakeDevice.inactivity()
        self.assertEqual(self.my_sensors.check_float_sensor(), 0)
        self.fakeDevice.activity()

    # smoke level tests #########
    @patch("src.mq2.MCP3008", return_value=fakeDevice)
    def test_mq(self, mcp_mock):
        mq = MQ(READ_SAMPLE_INTERVAL=5, CALIBRATION_SAMPLE_INTERVAL=5)
        self.assertEqual(
            mq.MQPercentage(),
            {'CO': 1.1974650056252536e-14, 'GAS_LPG': 3.0200902411295455e-11, 'SMOKE': 2.153788711294011e-11}
        )

    # motion sensor tests ########
    def test_motion_sensor_motion(self):
        self.assertEqual(self.my_sensors.motion_sensor(), None)

    def test_motion_sensor_inactive(self):
        self.fakeDevice.inactivity()
        self.assertEqual(self.my_sensors.motion_sensor(), None)
        self.fakeDevice.activity()

    # dht sensor tests ###########
    def test_dht_ok(self):
        self.assertEqual(self.my_sensors.humidity_and_temp(retries=1), (50, 20))

    def test_dht_high_temp(self):
        self.fakeDevice.temperature = 50
        self.assertEqual(self.my_sensors.humidity_and_temp(), (50, 50))
        self.fakeDevice.temperature = 20

    def test_dht_inactive(self):
        self.fakeDevice.inactivity()
        self.assertEqual(self.my_sensors.humidity_and_temp(retries=1), (0, 0))
        self.fakeDevice.activity()
