import os
import requests
from dotenv import load_dotenv, find_dotenv

# find and load possible environment variable file
load_dotenv(find_dotenv())


def send_message(_to=[], _msg=''):
    endpoint = os.getenv('SEND_MODE_ENDPOINT')
    auth_token = os.getenv('SEND_MODE_API_KEY')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_token
    }
    data = {"messagetext": _msg,
            "senderid": "ReuniteTag",
            "recipients": _to
            }
    response = requests.post(endpoint, data=data, headers=headers)

    # Print response
    print(response.text)
