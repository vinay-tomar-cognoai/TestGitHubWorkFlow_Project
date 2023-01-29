from django.conf import settings
from EasyTMSApp.utils_custom_encryption import CustomEncrypt

import sys
import json
import requests
import websocket
import logging
import hashlib

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

        cognoai_websocket = websocket.WebSocket()

        if settings.DEBUG:
            cognoai_websocket.connect(
                "ws://127.0.0.1:8000/ws/tms-signal/" + str(websocket_token) + "/server/")
        else:
            cognoai_websocket.connect("wss://" + settings.EASYCHAT_DOMAIN +
                                      "/ws/tms-signal/" + str(websocket_token) + "/server/")

        data = json.dumps({
            "message": {
                "header": {
                    "sender": "server"
                },
                "body": encrypted_data
            }
        })
        cognoai_websocket.send(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_data_from_server_to_client: " + str(e) +
                     " at " + str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
