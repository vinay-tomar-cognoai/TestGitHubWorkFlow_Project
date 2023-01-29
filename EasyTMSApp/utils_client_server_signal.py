from django.conf import settings
from EasyTMSApp.utils_custom_encryption import CustomEncrypt

import sys
import json
import requests
import websocket
import logging
import hashlib
import threading

logger = logging.getLogger(__name__)


def send_data_from_server_to_client(function_name, data, user):

    custom_encrypt_obj = CustomEncrypt()

    try:
        json_string = json.dumps({
            "type": function_name,
            "data": data
        })

        encrypted_response = custom_encrypt_obj.encrypt(json_string)

        encrypted_data = {
            "Request": encrypted_response
        }

        websocket_token = hashlib.md5(user.username.encode()).hexdigest()

        if settings.DEBUG:
            uri = "ws://127.0.0.1:8000/ws/tms-signal/" + str(websocket_token) + "/server/"
        else:
            uri = "wss://" + settings.EASYCHAT_DOMAIN + "/ws/tms-signal/" + str(websocket_token) + "/server/"

        data = json.dumps({
            "message": {
                "header": {
                    "sender": "server"
                },
                "body": encrypted_data
            }
        })

        thread = threading.Thread(target=send_data_to_websocket, args=(
            uri, data), daemon=True)
        thread.start()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_data_from_server_to_client: " + str(e) +
                     " at " + str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})


def send_data_to_websocket(uri, data):
    try:
        cognoai_websocket = websocket.WebSocket()
        cognoai_websocket.connect(uri)
        cognoai_websocket.send(data)
        cognoai_websocket.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_data_to_websocket: " + str(e) +
                     " at " + str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
