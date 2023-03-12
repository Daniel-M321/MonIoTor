import unittest
from unittest.mock import patch

from src.eventhandler import MyEventHandler
from src.influx import MyDatabase
from src.tests.TestInflux import FakeClient


class FakeMessages:
    def create(self, messaging_service_sid: str, body: str, to: str) -> str:
        sid = "well"
        return sid


class FakeCalls:
    def create(self, twiml: str, to: str, from_: str) -> str:
        sid = "well"
        return sid


class FakeClientTwil:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.messages = FakeMessages()
        self.calls = FakeCalls()


class TestTwilio(unittest.TestCase):

    @patch("src.influx.influxdb_client.InfluxDBClient", return_value=FakeClient("test", "test", "test"))
    @patch("src.eventhandler.os.environ", return_value={"test": "test"})
    @patch("src.eventhandler.Client", return_value=FakeClientTwil(username="user", password="pass"))
    def setUp(self, handler_mock, token_mock, db_mock):
        self.my_eh = MyEventHandler(MyDatabase())

    def test_text_user(self):
        self.assertIsNone(self.my_eh.text_user("Hi there, "))

    def test_call_user(self):
        self.assertIsNone(self.my_eh.call_user(""))
