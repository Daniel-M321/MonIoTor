import os
from twilio.rest import Client          # type: ignore

from influx import MyDatabase


class MyEventHandler:

    def __init__(self, db: MyDatabase):
        self.influxdb = db
        self.number = os.environ["MY_NUMBER"]

        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.messaging_service_sid = os.environ['MESSAGING_SERVICE_SID']
        self.client = Client(account_sid, auth_token)
        self.calling_number = os.environ['TWILIO_NUMBER']

    def text_user(self, sensor: str) -> None:
        number_query = self.influxdb.query_db("Phone", "User", "number")

        if len(number_query) > 0:
            self.number = number_query.pop()

        sensor += "Join Earth's mightiest heroes. Like Kevin Bacon."

        message = self.client.messages.create(
            messaging_service_sid=self.messaging_service_sid,
            body=sensor,
            to=self.number
        )

    def call_user(self, message: str) -> None:
        number_query = self.influxdb.query_db("Phone", "User", "number")

        if len(number_query) > 0:
            self.number = number_query.pop()

        message = '<Response><Say voice="alice">'+message+'</Say></Response>'

        call = self.client.calls.create(
            twiml=message,
            to=self.number,
            from_=self.calling_number
        )
