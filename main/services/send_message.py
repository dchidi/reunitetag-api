import os
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv


# find and load possible environment variable file
load_dotenv(find_dotenv())


def send_message(_to=[], _msg=''):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    for phone_number in _to:
        message = client.messages.create(
            messaging_service_sid='MGc6b62bebf30c3dde735366d70edb810e',
            body=_msg,
            to=phone_number
        )
        # save the payload in a log file
        print(message.sid)
