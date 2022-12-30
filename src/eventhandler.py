import os
from twilio.rest import Client

# from dotenv import load_dotenv
# load_dotenv()


def text_user(sensor: str) -> None:
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    sensor += "Join Earth's mightiest heroes. Like Kevin Bacon."

    message = client.messages.create(
        messaging_service_sid='MGe9d3e7b051d7fe7ec71ba682ff2cd059',  # Todo place in env variable
        body=sensor,
        to='+353870934553'  # Todo take user input and save
    )


def call_user() -> None:
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = '<Response><Say voice="alice">'+'Hello there, this is your message'+'</Say></Response>'

    call = client.calls.create(
        twiml=message,
        to='+353870934553',
        from_='+19785033669'
    )
