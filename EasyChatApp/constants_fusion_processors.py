FUSION_BOT_CHAT_HISTORY_PROCESSOR_NAME = "Fusion Bot Chat History API"

FUSION_BOT_CHAT_HISTORY_PROCESSOR = """
import sys
import re
import os
import json
import uuid
import random
import string
import logging
import hashlib
import mimetypes
import threading
import magic
import requests
import websocket

from PIL import Image
from os.path import basename
from EasyChat import settings
from django.utils import timezone
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart

from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils import create_image_thumbnail, create_video_thumbnail, get_agent_token
from EasyChatApp.models import MISDashboard
from LiveChatApp.models import FusionAuditTrail
from LiveChatApp.utils_ameyo_fusion import add_fusion_audit_trail
import time

from LiveChatApp.utils import logger

def generate_customer_bot_history(customer_obj, MISDashboard):
    try:
        message_history = []
        mis_objs = MISDashboard.objects.filter(user_id=customer_obj.easychat_user_id)

        for mis_obj in mis_objs:

            message_history.append({"source":"user", "sentTime":get_epoch_date(mis_obj), "message":mis_obj.get_message_received()})
            message_history.append({"source":"bot", "sentTime":get_epoch_date(mis_obj), "message":mis_obj.get_bot_response()})

        return json.dumps(message_history)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("generate_customer_bot_history: %s at %s", str(e), str( exc_tb.tb_lineno), extra={'AppName': "LiveChat"})


def get_epoch_date(mis_obj):
    try:
        return str(round(mis_obj.date.astimezone().timestamp()*1000))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_epoch_date: %s at %s", str(e), str( exc_tb.tb_lineno), extra={'AppName': "LiveChat"})


def f(x):
    try:
        customer_obj = x["customer_obj"]
        bot_fusion_config = x["bot_fusion_config"]

        app_id = bot_fusion_config.app_id
        url = "https://" + bot_fusion_config.host_name + "/v2/amfApi/" + app_id + "/receive"

        bot_chat_history = generate_customer_bot_history(customer_obj, MISDashboard)

        additional_parameters = {"customer_phone":customer_obj.phone,"customer_email":customer_obj.email,"customer_active_url":customer_obj.active_url}
        additional_parameters = json.dumps(additional_parameters)

        payload = json.dumps({
          "trigger": "message:appUser",
          "app": {
            "_id": app_id
          },
          "messages": [
            {
              "type": "text",
              "role": "appUser",
              "text": bot_chat_history,
              "name": customer_obj.username,
              "_id": customer_obj.easychat_user_id,
              "mediaUrl": "",
              "metadata": {
                "messageType": "botChat",
                "messageSource": AMEYO_CHANNELS[customer_obj.channel.name]
              },
              "source": {
                "type": "api"
              }
            }
          ],
          "appUser": {
            "_id": str(customer_obj.session_id),
            "surName": customer_obj.username,
            "givenName": customer_obj.username,
            "email": customer_obj.email,
            "phone" : customer_obj.phone,
            "clients": [
              {
                "displayName": customer_obj.username,
                "lastSeen": str(int(customer_obj.last_appearance_date.timestamp())),
                "platform": AMEYO_CHANNELS[customer_obj.channel.name]
              }
            ],
            "properties": {
              "phone_number" : customer_obj.phone,
              "additionalParameters": additional_parameters
            }
          }
        })

        headers = {
          'Content-Type': 'application/json',
          'Cookie': '__METADATA__=ec8c0bcb-8b92-45a4-b624-1d5c568df6f8; __METADATA__=ec8c0bcb-8b92-45a4-b624-1d5c568df6f8'
        }

        response = requests.request("POST", url, headers=headers, data=payload, verify=False)

        request_packet = json.dumps(headers) + payload
        add_fusion_audit_trail("Fusion Bot Chat History API", response, request_packet, customer_obj, FusionAuditTrail)

        return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_bot_chat_history_fusion: %s at %s", str(e), str( exc_tb.tb_lineno), extra={'AppName': "LiveChat"})

        return False """

FUSION_TEXT_MESSAGE_PROCESSOR_NAME = "Fusion Text Message API"

FUSION_TEXT_MESSAGE_PROCESSOR = """
import sys
import re
import os
import json
import uuid
import random
import string
import logging
import hashlib
import mimetypes
import threading
import magic
import requests
import websocket

from PIL import Image
from os.path import basename
from EasyChat import settings
from django.utils import timezone
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart

from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils import create_image_thumbnail, create_video_thumbnail, get_agent_token
from LiveChatApp.models import FusionAuditTrail
from LiveChatApp.utils_ameyo_fusion import add_fusion_audit_trail
import time

from LiveChatApp.utils import logger

def f(x):
    try:
        customer_obj = x["customer_obj"]
        bot_fusion_config = x["bot_fusion_config"]
        livechat_mis_obj = x["livechat_mis_obj"]

        app_id = bot_fusion_config.app_id
        url = "https://" + bot_fusion_config.host_name + "/v2/amfApi/" + app_id + "/receive"

        additional_parameters = {"customer_phone":customer_obj.phone,"customer_email":customer_obj.email,"customer_active_url":customer_obj.active_url}
        additional_parameters = json.dumps(additional_parameters)

        payload = json.dumps({
          "trigger": "message:appUser",
          "app": {
            "_id": app_id
          },
          "messages": [
            {
              "type": "text",
              "role": "appUser",
              "text": livechat_mis_obj.text_message,
              "name": customer_obj.username,
              "_id": str(livechat_mis_obj.message_id),
              "mediaUrl": "",
              "metadata": {
                "messageType": "chat",
                "messageSource": AMEYO_CHANNELS[customer_obj.channel.name]
              },
              "source": {
                "type": "api"
              }
            }
          ],
          "appUser": {
            "_id": str(customer_obj.session_id),
            "surName": customer_obj.username,
            "givenName": customer_obj.username,
            "clients": [
              {
              "displayName": customer_obj.username,
                "lastSeen": str(int(customer_obj.last_appearance_date.timestamp())),
                "platform": AMEYO_CHANNELS[customer_obj.channel.name]
              }
            ],
            "properties": {
              "additionalParameters": additional_parameters
            }
          }
        })

        headers = {
          'Content-Type': 'application/json',
          'Cookie': '__METADATA__=ec8c0bcb-8b92-45a4-b624-1d5c568df6f8; __METADATA__=ec8c0bcb-8b92-45a4-b624-1d5c568df6f8'
        }

        response = requests.request("POST", url, headers=headers, data=payload, timeout=10, verify=False)

        request_packet = json.dumps(headers) + payload
        add_fusion_audit_trail("Fusion Text Message API", response, request_packet, customer_obj, FusionAuditTrail)

        return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_text_message_fusion: %s at %s", str(e), str( exc_tb.tb_lineno), extra={'AppName': "LiveChat"})

        return False """

FUSION_ATTACHMENT_MESSAGE_PROCESSOR_NAME = "Fusion Attachment Message API"

FUSION_ATTACHMENT_MESSAGE_PROCESSOR = """
import sys
import re
import os
import json
import uuid
import random
import string
import logging
import hashlib
import mimetypes
import threading
import magic
import requests
import websocket

from PIL import Image
from os.path import basename
from EasyChat import settings
from django.utils import timezone
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart

from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils import create_image_thumbnail, create_video_thumbnail, get_agent_token
from LiveChatApp.models import FusionAuditTrail
from LiveChatApp.utils_ameyo_fusion import add_fusion_audit_trail
import time

from LiveChatApp.utils import logger

def f(x):
    try:
        customer_obj = x["customer_obj"]
        bot_fusion_config = x["bot_fusion_config"]
        livechat_mis_obj = x["livechat_mis_obj"]

        app_id = bot_fusion_config.app_id
        url = "https://" + bot_fusion_config.host_name + "/v2/amfApi/" + app_id + "/receive"

        extension = livechat_mis_obj.attachment_file_path.split(".")[-1]
        extension = "application/" + extension

        media_id = livechat_mis_obj.attachment_file_path.split("/")[-2]

        if customer_obj.channel.name == 'WhatsApp':
            livechat_media_url = livechat_mis_obj.attachment_file_path
        else:
            livechat_media_url = settings.EASYCHAT_HOST_URL + "/chat/access-file/" + media_id

        additional_parameters = {"customer_phone":customer_obj.phone,"customer_email":customer_obj.email,"customer_active_url":customer_obj.active_url}
        additional_parameters = json.dumps(additional_parameters)

        payload = json.dumps({
          "trigger": "message:appUser",
          "app": {
            "_id": app_id
          },
          "messages": [
            {
              "type": "file",
              "role": "appUser",
              "text": "",
              "name": customer_obj.username,
              "_id": str(livechat_mis_obj.message_id),
              "mediaUrl": livechat_media_url,
              "mediaType": extension,
              "metadata": {
                "messageType": "chat",
                "messageSource": AMEYO_CHANNELS[customer_obj.channel.name]
              },
              "source": {
                "type": "api"
              }
            }
          ],
          "appUser": {
            "_id": str(customer_obj.session_id),
            "surName": customer_obj.username,
            "givenName": customer_obj.username,
            "clients": [
              {
              "displayName": customer_obj.username,
                "lastSeen": str(int(customer_obj.last_appearance_date.timestamp())),
                "platform": AMEYO_CHANNELS[customer_obj.channel.name]
              }
            ],
            "properties": {
              "additionalParameters": additional_parameters
            }
          }
        })

        headers = {
          'Content-Type': 'application/json',
          'Cookie': '__METADATA__=ec8c0bcb-8b92-45a4-b624-1d5c568df6f8; __METADATA__=ec8c0bcb-8b92-45a4-b624-1d5c568df6f8'
        }

        response = requests.request("POST", url, headers=headers, data=payload, timeout=30, verify=False)

        request_packet = json.dumps(headers) + payload
        add_fusion_audit_trail("Fusion Attachment Message API", response, request_packet, customer_obj, FusionAuditTrail)

        return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_attachment_message_fusion: %s at %s", str(e), str( exc_tb.tb_lineno), extra={'AppName': "LiveChat"})

        return False """

FUSION_CHAT_DISCONNECTED_PROCESSOR_NAME = "Fusion Chat Disconnected API"

FUSION_CHAT_DISCONNECTED_PROCESSOR = """ 
import sys
import re
import os
import json
import uuid
import random
import string
import logging
import hashlib
import mimetypes
import threading
import magic
import requests
import websocket

from PIL import Image
from os.path import basename
from EasyChat import settings
from django.utils import timezone
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart

from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils import create_image_thumbnail, create_video_thumbnail, get_agent_token
from LiveChatApp.models import FusionAuditTrail
from LiveChatApp.utils_ameyo_fusion import add_fusion_audit_trail
import time

from LiveChatApp.utils import logger

def f(x):
    try:
        customer_obj = x["customer_obj"]
        bot_fusion_config = x["bot_fusion_config"]
        livechat_mis_obj = x["livechat_mis_obj"]

        app_id = bot_fusion_config.app_id
        url = "https://" + bot_fusion_config.host_name + "/v2/amfApi/" + app_id + "/receive"

        additional_parameters = {"customer_phone":customer_obj.phone,"customer_email":customer_obj.email,"customer_active_url":customer_obj.active_url}
        additional_parameters = json.dumps(additional_parameters)

        payload = json.dumps({
          "trigger": "message:appUser",
          "app": {
            "_id": app_id
          },
          "messages": [
            {
              "type": "session",
              "subType": "disconnected",
              "role": "appUser",
              "text": livechat_mis_obj.text_message,
              "name": "System",
              "_id": str(livechat_mis_obj.message_id),
              "mediaUrl": "",
              "metadata": {
                "messageType": "chat",
                "messageSource": AMEYO_CHANNELS[customer_obj.channel.name]
              },
              "source": {
                "type": "api"
              }
            }
          ],
          "appUser": {
            "_id": str(customer_obj.session_id),
            "surName": "System",
            "givenName": "System",
            "clients": [
              {
              "displayName": "System",
                "lastSeen": str(int(customer_obj.last_appearance_date.timestamp())),
                "platform": AMEYO_CHANNELS[customer_obj.channel.name]
              }
            ],
            "properties": {
              "additionalParameters": additional_parameters
            }
          }
        })

        headers = {
          'Content-Type': 'application/json',
          'Cookie': '__METADATA__=ec8c0bcb-8b92-45a4-b624-1d5c568df6f8; __METADATA__=ec8c0bcb-8b92-45a4-b624-1d5c568df6f8'
        }

        response = requests.request("POST", url, headers=headers, data=payload, timeout=10, verify=False)

        request_packet = json.dumps(headers) + payload
        add_fusion_audit_trail("Fusion Chat Disconnected API", response, request_packet, customer_obj, FusionAuditTrail)

        return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_disconnected_status_fusion: %s at %s", str(e), str( exc_tb.tb_lineno), extra={'AppName': "LiveChat"})

        return False """
