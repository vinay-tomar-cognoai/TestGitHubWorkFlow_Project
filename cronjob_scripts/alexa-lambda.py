from __future__ import print_function

import urllib2
import json
import re
from pprint import pprint
import socket
import ssl
socket.setdefaulttimeout(30)

EASYCHAT_ALEXA_WEBHOOK = "https://easychat.allincall.in/chat/webhook/alexa/?id=4"


def lambda_handler(event, context):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_NONE

        request = urllib2.Request(
            EASYCHAT_ALEXA_WEBHOOK, data=json.dumps(event))
        request.add_header("Content-Type", 'application/json')
        request.get_method = lambda: "POST"

        try:
            connection = urllib2.build_opener(
                urllib2.HTTPSHandler()).open(request, timeout=30)
        except urllib2.HTTPError as err:
            connection = err
        except IOError as err:
            print("Timeout Error!!!!")
            print(err)

        if connection.code == 200:
            return json.loads(connection.read())
        else:
            return None
    except Exception:
        return {
            "alexa": {
                "response": "We are having trouble connecting. Please try again later"
            }
        }
