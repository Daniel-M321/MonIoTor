import unittest
from unittest.mock import patch

from src.eventhandler import text_user, call_user


class FakeMessages:
    def create(self, messaging_service_sid: str, body: str, to: str) -> str:
        sid = "well"
        return sid


class FakeClient:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.messages = FakeMessages()


class TestTwilio(unittest.TestCase):

    @patch("src.eventhandler.Client", return_value=FakeClient(username="user", password="pass"))
    def test_text_user(self, client_mock):
        self.assertIsNone(text_user("Hi there, "))

    # def test_call_user(self):
    #     call_user()
