from OAuthApp.models import REMOTE_ACCESS_URL
from OAuthApp.utils_encrypt import CustomEncrypt

import random
import sys
import json
import requests
import logging
from ast import literal_eval

logger = logging.getLogger(__name__)


def generate_password(password_prefix):
    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['@', '#', '$', '&']

    password_digits = ""
    for value in range(0, 6):
        password_digits = password_digits + random.choice(digits)
    password = password_prefix + \
        random.choice(symbols) + password_digits + random.choice(symbols)
    return password


def custom_request_decrypt(data):
    custom_encrypt_obj = CustomEncrypt()
    if "Request" in data:
        data = data["Request"]
    else:
        data = data["Response"]
    data = custom_encrypt_obj.decrypt(data)
    data = json.loads(data)
    return data


def allow_incoming_request(request):
    try:
        data = request.data
        data = custom_request_decrypt(data)
        token = data["token"]

        custom_encrypt_obj = CustomEncrypt()
        request_packet = json.dumps({"token": token})

        encrypted_response = custom_encrypt_obj.encrypt(request_packet)
        request_packet = {"Request": encrypted_response}
        validate_token_response = requests.post(url=REMOTE_ACCESS_URL + "/remote-access/oauth/token/validate/",
                                                data=json.dumps(request_packet), headers={"Content-Type": "application/json"})

        json_response = json.loads(validate_token_response.text)
        json_response = custom_request_decrypt(json_response)

        if json_response["status"] == 200:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_incoming_ip %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'OAuthApp'})

    return False
