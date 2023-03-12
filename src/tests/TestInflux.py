import unittest
from typing import Any
from unittest.mock import patch

from src.influx import MyDatabase


class FakePoint:
    def __init__(self):
        pass

    def tag(self, key: Any, value: Any) -> None:
        pass

    def field(self, key: Any, value: Any) -> None:
        pass


class WriteApi:
    def __init__(self):
        pass

    def write(self, bucket: str, org: str, record: FakePoint) -> None:
        pass


class FakeClient:
    def __init__(self, url: str, token: str, org: str):
        self.url = url
        self.token = token
        self.org = org

    def write_api(self, write_options: object) -> WriteApi:
        return WriteApi()


class TestInflux(unittest.TestCase):
    fakeClient = FakeClient("test.com", "testToken", "testOrg")

    @patch("src.influx.influxdb_client.InfluxDBClient", return_value=fakeClient)
    @patch("src.eventhandler.os.environ", return_value={"test": "test"})
    def setUp(self, token_mock, db_mock):
        self.my_db = MyDatabase()

    def test_write_db(self):
        self.assertEqual(self.my_db.write_db("dht11", ["place", "kitchen"], "temperature", 20.8), 1)
