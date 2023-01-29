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
import time

from PIL import Image
from os.path import basename
from EasyChat import settings
from django.utils import timezone
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart

from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils import create_image_thumbnail, create_video_thumbnail, get_agent_token, open_file, get_livechat_request_packet_to_channel
from LiveChatApp.utils_translation import get_translated_text
from EasyChatApp.models import Profile, LiveChatBotChannelWebhook, WhatsAppWebhook, EasyChatTranslationCache

logger = logging.getLogger(__name__)


def check_if_null_or_blank(field, field_value, status_message, status_code):
    try:
        if field_value == None or field_value == "":
            status_message += " , " + field
            return "401", status_message

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_if_null_or_blank: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})
        return "500", str(e)

    return "200", "Success"


def save_livechat_file_to_system(file_name, attachment_file_ext, attachment_file_url, LiveChatFileAccessManagement):
    try:
        path = os.path.join(settings.SECURE_MEDIA_ROOT, "LiveChatApp/attachment/")
        path = path + file_name

        save_file_from_remoteurl(path, attachment_file_url)

        path = "/secured_files/LiveChatApp/attachment/" + file_name
        file_access_management_obj = LiveChatFileAccessManagement.objects.create(file_path=path, is_public=False)

        file_url = '/livechat/download-file/' + \
            str(file_access_management_obj.key) + '/' + file_name

        thumbnail_file_name = ""
        if attachment_file_ext in ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "jfif", "tiff", "exif", "bmp", "gif", "GIF"]:
            thumbnail_file_name = create_image_thumbnail(file_name)
        elif attachment_file_ext in ["MPEG", "mpeg", "MP4", "mp4", "MOV", "mov", "AVI", "avi", "flv"]:
            thumbnail_file_name = create_video_thumbnail(file_name)

        thumbnail_url = ""

        if thumbnail_file_name != "":
            path_of_thumbnail = "/secured_files/LiveChatApp/attachment/" + thumbnail_file_name
            file_access_management_obj = LiveChatFileAccessManagement.objects.create(
                file_path=path_of_thumbnail, is_public=False)

            thumbnail_url = '/livechat/download-file/' + \
                str(file_access_management_obj.key) + \
                '/' + thumbnail_file_name

        return file_url, file_name, thumbnail_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_livechat_file_to_system: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})


def save_whatsapp_livechat_file_to_system(file_name, attachment_file_ext, attachment_file_url, LiveChatFileAccessManagement):
    try:
        path = os.path.join(settings.MEDIA_ROOT, "WhatsAppMedia/")

        file_name = str(uuid.uuid4()) + '.' + attachment_file_ext
        path = path + file_name

        save_file_from_remoteurl(path, attachment_file_url)

        file_url = "/files/WhatsAppMedia/" + file_name

        return file_url, file_name, ""

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_whatsapp_livechat_file_to_system: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})


def save_file_from_remoteurl(local_path, remote_url):
    try:
        response = requests.get(url=remote_url, timeout=10)
        raw_data = response.content
        file_to_save = open(local_path, "wb")
        file_to_save.write(raw_data)
        file_to_save.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_file_from_remoteurl: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})


def save_and_send_data_to_agent_via_socket(customer_obj, text_message, path, attachment_file_name, thumbnail_url, is_attachment, LiveChatMISDashboard, LiveChatTranslationCache):
    try:

        if not text_message:
            text_message = ""

        # Message translation
        translated_text = ""
        customer_language = customer_obj.customer_language
        if customer_language and customer_language.lang != 'en' and text_message != "":
            translated_text = get_translated_text(text_message, customer_language.lang, LiveChatTranslationCache)

        sender_name = customer_obj.agent_id.get_agent_name()
        message_type = "file" if is_attachment else "text"
        livechat_mis_obj = LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                               sender="Agent",
                                                               text_message=text_message,
                                                               sender_name=sender_name,
                                                               message_time=timezone.now(),
                                                               attachment_file_name=attachment_file_name,
                                                               attachment_file_path=path,
                                                               thumbnail_file_path=thumbnail_url,
                                                               translated_text=translated_text)

        data = json.dumps({
            "sender": "Agent",
            "message": json.dumps({
                "text_message": text_message,
                "type": message_type,
                "channel": customer_obj.channel.name,
                "path": path,
                "thumbnail_url": thumbnail_url,
                "session_id": str(customer_obj.session_id),
                "sender_name": sender_name,
                "bot_id": str(customer_obj.bot.pk),
                "message_id": str(livechat_mis_obj.message_id),
                "translated_text": translated_text,
                "agent_name": sender_name
            })
        })

        # sending data in one to one socket
        one_to_one_socket_thread = threading.Thread(target=send_data_to_websocket, args=(
            settings.EASYCHAT_DOMAIN, [data], str(customer_obj.session_id)), daemon=True)
        one_to_one_socket_thread.start()

        agent_websocket_token = get_agent_token("")

        # sending data to global socket
        global_socket_thread = threading.Thread(target=send_data_to_websocket, args=(
            settings.EASYCHAT_DOMAIN, [data], agent_websocket_token), daemon=True)
        global_socket_thread.start()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_and_send_data_to_agent_via_socket: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})    


def send_data_to_websocket(domain, data_to_send, livechat_session_id):
    try:
        ws = websocket.WebSocket()
        custom_encrypt_obj = CustomEncrypt()

        ws.connect("wss://" + domain +
                   "/ws/" + livechat_session_id + "/agent/")

        for data in data_to_send:
            data = custom_encrypt_obj.encrypt(data)
            ws.send(data)

        ws.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_data_to_websocket: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def mark_chat_expired(customer_obj):
    try:
        if customer_obj.channel.name == 'Web':
            data = json.dumps({
                "sender": "agent_end_session",
                "message": json.dumps({
                    "text_message": "",
                    "type": "text",
                    "channel": customer_obj.channel.name,
                    "path": "",
                    "session_id": str(customer_obj.session_id),
                    "bot_id": str(customer_obj.bot.pk)
                })
            })

            # sending data in one to one socket
            one_to_one_socket_thread = threading.Thread(target=send_data_to_websocket, args=(
                settings.EASYCHAT_DOMAIN, [data], str(customer_obj.session_id)), daemon=True)
            one_to_one_socket_thread.start()

        diff = timezone.now() - customer_obj.joined_date
        customer_obj.is_session_exp = True
        customer_obj.chat_duration = diff.seconds
        customer_obj.last_appearance_date = timezone.now()
        customer_obj.chat_ended_by = "Agent"
        customer_obj.save()

        user_obj = Profile.objects.filter(
            user_id=customer_obj.easychat_user_id, bot=customer_obj.bot).latest("pk")

        if user_obj:
            user_obj.livechat_connected = False
            user_obj.save(update_fields=['livechat_connected'])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("mark_chat_expired: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})


def mark_chat_expired_from_customer(customer_obj):
    try:

        diff = timezone.now() - customer_obj.joined_date
        customer_obj.is_session_exp = True
        customer_obj.chat_duration = diff.seconds
        customer_obj.last_appearance_date = timezone.now()
        customer_obj.chat_ended_by = "Customer"
        customer_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("mark_chat_expired_from_customer: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})


def send_ameyo_system_message(customer_obj, message, identifier):
    try:
        assigned_agent_username = "Agent"
        joined_chat_text = "Agent has joined the chat. Please ask your queries now."

        try:
            assigned_agent = "Agent"
            if str(customer_obj.agent_id.user.first_name) == "":
                assigned_agent = str(
                    customer_obj.agent_id.user.username)
            else:
                assigned_agent = str(
                    customer_obj.agent_id.user.first_name) + " " + str(customer_obj.agent_id.user.last_name)

            joined_chat_text = f"{assigned_agent} has joined the chat. Please ask your queries now."

            if customer_obj.customer_language and customer_obj.customer_language.lang != 'en':
                joined_chat_text = get_translated_text(
                    joined_chat_text, customer_obj.customer_language.lang, EasyChatTranslationCache, False, True)

            assigned_agent_username = str(customer_obj.agent_id.user.username)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ERROR send_ameyo_system_message: not able to fetch agent name or username %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})

        data = json.dumps({
            "sender": "System",
            "message": json.dumps({
                "text_message": message,
                "type": "text",
                "channel": customer_obj.channel.name,
                "path": "",
                "session_id": str(customer_obj.session_id),
                "bot_id": str(customer_obj.bot.pk),
                "event_type": identifier,
                "translated_text": "",
                "joined_chat_text": joined_chat_text,
                "assigned_agent_username": assigned_agent_username
            })
        })

        # sending data in one to one socket
        one_to_one_socket_thread = threading.Thread(target=send_data_to_websocket, args=(
            settings.EASYCHAT_DOMAIN, [data], str(customer_obj.session_id)), daemon=True)
        one_to_one_socket_thread.start()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_ameyo_system_message: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})


def create_ameyo_agent(agent_id, agent_name, bot_obj, LiveChatCategory, LiveChatUser, User):
    try:

        email = "agent_" + random_ameyo_id() + "@ameyo.net"
        password = "Success@123"
        phone_number = "919876543210"

        easychat_user_obj = User.objects.create(email=email, first_name=agent_name, last_name="", username=email, password=password, role="customer_care_agent", status="1")
        user_obj = LiveChatUser.objects.create(
            user=easychat_user_obj, status="3", phone_number=phone_number, ameyo_agent_id=agent_id, ameyo_agent_name=agent_name)
        
        livechat_admin = LiveChatUser.objects.filter(bots__in=[bot_obj]).first() 
        livechat_admin.agents.add(user_obj)

        user_obj.bots.add(bot_obj)

        category_objs = LiveChatCategory.objects.filter(bot=bot_obj, is_deleted=False)
        for category_obj in category_objs:
            user_obj.category.add(category_obj)

        user_obj.is_online = True
        user_obj.is_session_exp = False
        user_obj.save()

        return user_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_ameyo_agent: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})

        return None


def random_ameyo_id():
    try:
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(random.choices(alphabet, k=8))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("random_ameyo_id: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})


def add_fusion_audit_trail(api_name, response, request_packet, customer_obj, FusionAuditTrail):
    try:

        api_status_code = str(response.status_code)
        response_packet = str(response.text)

        user_id = str(customer_obj.easychat_user_id)
        bot_id = str(customer_obj.bot.id)

        FusionAuditTrail.objects.create(user_id=user_id,
                                        bot_id=bot_id,
                                        request_packet=request_packet,
                                        response_packet=response_packet,
                                        api_name=api_name,
                                        api_status_code=api_status_code)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_fusion_audit_trail: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})


def send_whatsapp_welcome_message_ameyo(bot_obj, user_id):
    try:
        logger.info("inside send_whatsapp_welcome_message_ameyo:",
                    extra={'AppName': 'LiveChat'})
        request_packet = {
            "contacts": [
                {
                    "profile": {
                        "name": ""
                    },
                    "wa_id": user_id
                }
            ],
            "messages": [
                {
                    "from": user_id,
                    "id": "",
                    "text": {
                          "body": "livechat_agent_end_session"
                    },
                    "timestamp": str(int(datetime.now().timestamp())),
                    "type": "text"
                }
            ],
            "bot_id": bot_obj.id
        }
        logger.info("send_whatsapp_welcome_message_ameyo request_packet: " + str(request_packet), extra={'AppName': 'LiveChat'})
        if WhatsAppWebhook.objects.all().count() > 0:
            whatsapp_webhook_obj = WhatsAppWebhook.objects.filter(
                bot=bot_obj)
            if whatsapp_webhook_obj:
                result_dict = {}
                exec(str(whatsapp_webhook_obj[
                     0].function), result_dict)
                result_dict['whatsapp_webhook'](request_packet)
        logger.info("send_whatsapp_welcome_message_ameyo final message sent", extra={
            'AppName': 'LiveChat'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_whatsapp_welcome_message_ameyo: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def save_and_send_data_to_agent_via_webhook(customer_obj, text_message, path, attachment_file_name, thumbnail_url, is_attachment, ameyo_identifier, LiveChatMISDashboard, LiveChatTranslationCache):
    try:
        logger.info("inside save_and_send_data_to_agent_via_webhook:",
                    extra={'AppName': 'LiveChat'})
        if not text_message:
            text_message = ""

        # Message translation
        translated_text = ""
        customer_language = customer_obj.customer_language
        if customer_language and customer_language.lang != 'en' and text_message != "":
            translated_text = get_translated_text(
                text_message, customer_language.lang, LiveChatTranslationCache)

        if customer_obj.agent_id == None:
            sender_name = "System"
        else:
            sender_name = customer_obj.agent_id.get_agent_name()

        message_type = "file" if is_attachment else "text"
        LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                            sender="Agent",
                                            text_message=text_message,
                                            sender_name=sender_name,
                                            message_time=timezone.now(),
                                            attachment_file_name=attachment_file_name,
                                            attachment_file_path=path,
                                            thumbnail_file_path=thumbnail_url,
                                            translated_text=translated_text)
        if customer_obj.channel.name == "WhatsApp":
            channel_webhook = LiveChatBotChannelWebhook.objects.filter(
                bot=customer_obj.bot, channel=customer_obj.channel).first()
            user_obj = Profile.objects.filter(
                livechat_session_id=customer_obj.session_id).first()
            if user_obj.livechat_connected == True:

                request_packet = get_livechat_request_packet_to_channel(
                    str(customer_obj.session_id), message_type, text_message, path, "WhatsApp", customer_obj.bot.pk, sender_name)
                temp_dictionary = {'open': open_file}
                exec(str(channel_webhook.function), temp_dictionary)
                temp_dictionary['f'](request_packet)

            if ameyo_identifier == "AGENT_LEFT_CHAT":
                send_whatsapp_welcome_message_ameyo(
                    customer_obj.bot, customer_obj.easychat_user_id)
                return

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_and_send_data_to_agent_via_webhook: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})
