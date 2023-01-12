import os
from twilio.rest import Client          # type: ignore


def text_user(sensor: str) -> None:
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    messaging_service_sid = os.environ['MESSAGING_SERVICE_SID']
    client = Client(account_sid, auth_token)

    sensor += "Join Earth's mightiest heroes. Like Kevin Bacon."

    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        body=sensor,
        to='+353870934553'  # Todo take user input and save
    )


def call_user(message: str) -> None:
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    calling_number = os.environ['TWILIO_NUMBER']
    client = Client(account_sid, auth_token)

    message = '<Response><Say voice="alice">'+message+'</Say></Response>'

    call = client.calls.create(
        twiml=message,
        to='+353870934553',
        from_=calling_number
    )
