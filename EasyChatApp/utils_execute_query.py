import re
import ast
import sys
import json
import copy
import uuid
import logging
import wordninja
import subprocess
import execjs
import os
import random
import time
import hashlib
import csv
import linecache
import mimetypes
import magic
import inspect
import difflib
import editdistance
import base64
import threading
import pytz
import func_timeout
from random import randint

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.contrib.auth import logout
from django.db.models import Q, Count

from EasyChatApp.utils_analytics import *
from EasyChatApp.utils_google import *
from EasyChatApp.utils_userflow import create_bot_response
from EasyChatApp.profanityfilter import ProfanityFilter
from EasyChatApp.utils_voicebot import get_detected_language_for_voice_bot, build_voicebot_fallback_response

from EasyChatApp.cryptography import *
from EasyChatApp.utils_custom_encryption import *
from EasyChatApp.utils_translation_module import *
from EasyChatApp.default_intent_constants import *
from EasyChatApp.constants_tms_proccesors import *
from EasyChatApp.easychat_utils_objects import *
from EasyChatApp.utils_bot import get_translated_text, check_query_for_warning_or_block
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.utils_pdf_search import get_easysearch_pdf_result
from EasySearchApp.utils import *
from EasyChatApp.models import *
from EasySearchApp.models import EasyPDFSearcher, EasyPDFSearcherAnalytics
from EasySearchApp.models import SearchUser, EasySearchConfig
from LiveChatApp.models import LiveChatUser, LiveChatCategory, LiveChatAuditTrail, LiveChatSessionManagement, LiveChatConfig, LiveChatAdminConfig, LiveChatCustomer
from LiveChatApp.livechat_channels_webhook import check_for_livechat, create_and_enable_livechat, get_livechat_response
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses
from LiveChatApp.utils import save_audit_trail_data, send_event_for_agent_not_ready
from EasyAssistApp.utils import get_active_agent_obj
from EasyAssistApp.utils import save_audit_trail as save_audit_trail_easyassist
from EasyTMSApp.utils import auto_assign_agent
from AuditTrailApp.utils import add_audit_trail

from EasyChatApp.emoji_detection import *
from EasyChatApp.text_or_emoji_recognition import *

from collections import OrderedDict
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from spellchecker import SpellChecker
from sklearn.feature_extraction import text as sklearn_text

from googletrans import Translator, client
from PIL import Image
from moviepy.editor import *

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from EasyChatApp.utils_advanced_nlp import identify_next_tree_semantic_similarities, check_if_repeat_event_detected
from LiveChatApp.utils import send_event_for_login_logout, send_event_for_performance_report
from LiveChatApp.utils_validation import *

google_translator = Translator()

logger = logging.getLogger(__name__)

spell = SpellChecker()

lm = wordninja.LanguageModel(settings.MEDIA_ROOT + 'wordninja_words.txt.gz')


def check_and_expire_livechat_session(easychat_user):
    try:
        if LiveChatUser.objects.filter(user=easychat_user).count() == 0:
            return
        livechat_user = LiveChatUser.objects.get(user=easychat_user)
        sessions_obj = LiveChatSessionManagement.objects.filter(
            user=livechat_user, session_completed=False)[0]
        if sessions_obj.user.is_online:
            diff = sessions_obj.user.last_updated_time - sessions_obj.session_ends_at
            sessions_obj.online_time += diff.seconds
            sessions_obj.session_ends_at = sessions_obj.user.last_updated_time
            sessions_obj.session_completed = True
            sessions_obj.save()
        else:
            diff = sessions_obj.user.last_updated_time - sessions_obj.session_ends_at
            sessions_obj.offline_time += diff.seconds
            sessions_obj.session_ends_at = sessions_obj.user.last_updated_time
            sessions_obj.session_completed = True
            if sessions_obj.agent_not_ready.all().count():
                agent_not_ready_obj = sessions_obj.agent_not_ready.all().order_by(
                    '-not_ready_starts_at')[0]
                agent_not_ready_obj.not_ready_ends_at = timezone.now()
                agent_not_ready_obj.is_expired = True
                agent_not_ready_obj.save()
                send_event_for_agent_not_ready(livechat_user, agent_not_ready_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot, True)
            sessions_obj.save()
        send_event_for_login_logout(livechat_user, sessions_obj, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot, True)
        send_event_for_performance_report(livechat_user, sessions_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot, True)
        livechat_user.is_online = False
        livechat_user.is_session_exp = True
        livechat_user.resolved_chats = 0
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            agent_id=livechat_user, is_session_exp=False)
        for livechat_cust_obj in livechat_cust_objs:
            diff = datetime.datetime.now(
                timezone.utc) - livechat_cust_obj.joined_date
            livechat_cust_obj.is_session_exp = True
            livechat_cust_obj.abruptly_closed = True
            livechat_cust_obj.chat_duration = diff.seconds
            livechat_cust_obj.last_appearance_date = datetime.datetime.now()
            livechat_cust_obj.chat_ended_by = "System"
            livechat_cust_obj.save()
        livechat_user.ongoing_chats = 0
        livechat_user.save()
        save_audit_trail_data("8", livechat_user, LiveChatAuditTrail)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_expire_livechat_session! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_message_list_using_pk

input_params:
    pk_list: list of pk's
output_params:
    Returns the list of name of intents, taking intent pk list a input.
"""


def get_message_list_using_pk(pk_list):
    message_list = []
    try:
        for pk in pk_list:
            try:
                intent_obj = Intent.objects.get(pk=pk, is_deleted=False)
            except Exception:
                intent_obj = None

            if intent_obj:
                message_list.append(intent_obj.name)
    except Exception:
        message_list = []
        pass

    return message_list


def save_bot_switch_data_variable_if_availabe(user_id, bot_id, response, channel):
    try:
        if "is_bot_switched" in response and response["is_bot_switched"] == "true":
            if "bot_id" in response:
                bot_switched_to = response["bot_id"]
                profile_obj = Profile.objects.filter(
                    user_id=user_id, bot__id=bot_id).first()
                profile_obj.tree = None
                profile_obj.save()
                save_data(profile_obj, {"bot_id": str(bot_switched_to)},
                          "en", channel, bot_id, is_cache=True)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("return_invalid_response: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})


"""
function: get_message_list_using_pk

input_params:
    pk_list: list of pk's
output_params:
    Returns the list of name of intents, taking intent pk list a input.
"""

# this function is temporary, will remove it later


def get_message_list_with_pk(pk_list, new_tag_list=[], enable_intent_icon=False, category_obj=None, channel_obj=None):
    message_list = []
    try:
        for idx, pk in enumerate(pk_list):
            
            intent_obj = Intent.objects.filter(pk=pk, is_deleted=False)
            if category_obj:
                intent_obj = intent_obj.filter(Q(category=category_obj) | Q(category__isnull=True))
            
            if channel_obj:
                intent_obj = intent_obj.filter(channels=channel_obj)
           
            intent_obj = intent_obj.first()

            if intent_obj:
                is_new_tag = False
                if len(new_tag_list) > 0 and new_tag_list[idx]:
                    is_new_tag = new_tag_list[idx][str(intent_obj.pk)]

                intent_icon = ""
                if enable_intent_icon:
                    if intent_obj.build_in_intent_icon:
                        intent_icon = intent_obj.build_in_intent_icon.icon
                    else:
                        intent_icon = '<img width="40px" height="40px" src="' + intent_obj.intent_icon + '">'

                message_list.append({
                    "name": intent_obj.name,
                    "id": intent_obj.pk,
                    "tree_pk": intent_obj.tree.pk,
                    "new_tag": is_new_tag,
                    "intent_icon": intent_icon
                })
    except Exception:
        message_list = []
        pass

    return message_list


"""
function: save_api_data

input_params:
    data: response from processors
    elapsed_time: time taken by processor to execute
output_params:
    Used to save request and response packet of API's in all processors.
"""


def save_api_data(data, elapsed_time, bot_obj, api_name, user, src, channel, new_parameters_list):
    try:

        if bool(data) and "API_REQUEST_PACKET" in data and bool(data["API_REQUEST_PACKET"]) and "API_RESPONSE_PACKET" in data and bool(data["API_RESPONSE_PACKET"]):

            try:
                api_status_code = data["status_code"]
                api_status = "Failed" if str(
                    api_status_code) == "400" else "Passed"
            except Exception:
                api_status = "Passed"
                api_status_code = "200"
                pass

            request_packet = data["API_REQUEST_PACKET"]
            request_packet = json.dumps(request_packet)
            response_packet = data["API_RESPONSE_PACKET"]
            response_packet = json.dumps(response_packet)

            if bot_obj.masking_enabled:
                request_packet = get_masked_data(
                    request_packet, bot_obj, src, channel, user.user_id)
                response_packet = get_masked_data(
                    response_packet, bot_obj, src, channel, user.user_id)

            APIElapsedTime.objects.create(
                bot=bot_obj, user=user, request_packet=request_packet, response_packet=response_packet, api_name=api_name, elapsed_time=elapsed_time, api_status=api_status, api_status_code=api_status_code)

            if api_status == "Failed" and bot_obj.is_api_fail_email_notifiication_enabled:
                check_and_send_api_failed_mail(api_name, json.dumps(
                    data["API_REQUEST_PACKET"], indent=2), json.dumps(data["API_RESPONSE_PACKET"], indent=2), bot_obj, new_parameters_list)
            return data["API_REQUEST_PACKET"], data["API_RESPONSE_PACKET"]
        else:
            return {}, {}

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_api_data! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
        return {}, {}


def return_html_of_mail(bot_name, api_name, api_request_packet, api_response_packet, message, new_parameters_list):
    body = """
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <title>Cogno AI</title>
      <style type="text/css" media="screen">
        table {
            border: 1px solid black;
            border-collapse: collapse;
        }
        
        table tr td,
        table th {
            border: 1px solid black;
            padding: 4px 10px;
            text-align: left;
        }
      </style>
    </head>
    <body>

    <div style="padding:1em;border:0.1em black solid;" class="container">
        <p>
            Hello User,
        </p>
        <p>
            Looks like we received an unexpected API error in the <strong>""" + str(bot_name) + """</strong> Bot. Please find the details of the same below:
        </p>

        <table style="margin-bottom: 10px">
        <thead>
            <th>S.No.</th>
            <th>Parameter Name</th>
            <th>Value</th>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <th>Bot ID</th>
                <td>""" + str(new_parameters_list["bot_id"]) + """</td>
            </tr>
            <tr>
                <td>2</td>
                <th>Intent Name</th>
                <td>""" + str(new_parameters_list["intent_name"]) + """</td>
            </tr>
            <tr>
                <td>3</td>
                <th>Intent ID</th>
                <td>""" + str(new_parameters_list["intent_pk"]) + """</td>
            </tr>
            <tr>
                <td>4</td>
                <th>Tree ID</th>
                <td>""" + str(new_parameters_list["tree_id"]) + """</td>
            </tr>
            <tr>
                <td>5</td>
                <th>Tree Name</th>
                <td>""" + str(new_parameters_list["tree_name"]) + """</td>
            </tr>
            <tr>
                <td>6</td>
                <th>API Name</th>
                <td>""" + str(api_name) + """</td>
            </tr>
        </tbody>
    </table>
        """

    body += """
    <h><b>API Request Packet:</b></h>
    <pre>""" + api_request_packet + """</pre>
    <br>
    <h><b>API Response Packet:</b></h>
    <pre>""" + api_response_packet + """</pre>
    <br>
    <p>""" + message + """</p>
    <p>&nbsp;</p>"""

    config = get_developer_console_settings()

    body += config.custom_report_template_signature

    body += """</div></body>"""

    return body


def return_html_of_bot_break_mail(bot_id, channel, window_location, broken_mail_dump):
    domain_name = settings.EASYCHAT_DOMAIN
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id))
        if bot_obj.exists():
            bot_obj = bot_obj.first()
            bot_name = bot_obj.name
        else:
            bot_name = "None"
    except:
        bot_id = "None"
        bot_name = "None"

    channel_message = ""
    if channel != "None" and channel != "":
        channel_message = channel
        if window_location != "":
            channel_message = channel + "(" + window_location + ")"
    else:
        channel_message = "None"
    header_message = "Erratic behavior of bot detected, please check the same immediately. ⚠️"

    body = """
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <title>Cogno AI</title>
      <style type="text/css" media="screen">
        table {
            border: 1px solid black;
            border-collapse: collapse;
        }
        
        table tr td,
        table th {
            border: 1px solid black;
            padding: 4px 10px;
            text-align: left;
        }
      </style>
    </head>
    <body>

    <div style="padding:1em;border:0.1em black solid;" class="container">
        <p>
            Hello Team,
        </p>
        <p>""" + header_message + """</p>
        <p>Bot name - """ + str(bot_name) + """</p>
        <p>Bot Id - """ + str(bot_id) + """</p>
        <p>Channel - """ + str(channel_message) + """</p>
        <p>Domain link - """ + str(domain_name) + """</p>
        <p>Meta Data - """ + str(broken_mail_dump) + """</p>

        <p></p>
        <p></p>
        <p></p>
        """

    config = get_developer_console_settings()

    body += config.custom_report_template_signature

    body += """</div></body>"""
    if bot_name == "None":
        return body, domain_name
    return body, bot_name


"""
function: send_api_fail_mail
input_params:
    from_email_id,: email id from which email wil be sent
    from_email_id_password: password of email id from which email wil be sent
    to_emai_id: email id to which email wil be sent
    api_name: name of failed api
    api_request_packet: api request packet
    api_response_packet: api response packet
    bot_obj:

send email
"""


def send_api_fail_mail(api_name, api_request_packet, api_response_packet, bot_obj, to_email_id, new_parameters_list):
    message = "Kindly connect with the API Team to look into the issue."
    new_parameters_list = json.loads(new_parameters_list)
    new_parameters_list["bot_id"] = str(bot_obj.id)
    body = return_html_of_mail(
        bot_obj.name, api_name, api_request_packet, api_response_packet, message, new_parameters_list)

    send_email_to_customer_via_awsses(
        to_email_id, "API Error in " + bot_obj.name, body)


"""
function: send_bot_break_mail
input_params:
    to_emai_id: email id to which email wil be sent
    new_parameters_list: consists bot name or domain name and channel
send email
"""


def send_bot_break_mail(to_email_id, bot_id, channel, window_location="", broken_mail_dump="{}", cc=None):
    body, bot_or_domain_name = return_html_of_bot_break_mail(
        bot_id, channel, window_location, broken_mail_dump)
    send_email_to_customer_via_awsses(
        to_email_id, "⚠️ Bot Break detected in " + bot_or_domain_name, body, cc=cc)


"""
function: check_and_send_api_failed_mail
input_params:
    api_name: name of failed api
    api_request_packet: api request packet
    api_response_packet: api response packet
    bot_obj:

Checks the time of last send mail for the same API. If time exceeds mail_sender_time_interval, then sends new mail and update mail sent time
"""


def check_and_send_api_failed_mail(api_name, api_request_packet, api_response_packet, bot_obj, new_parameters_list):
    try:
        config = get_developer_console_settings()
        from_email_id = config.email_host_user

        if EasyChatMAil.objects.filter(bot=bot_obj, api_name=api_name):
            easychat_mail_obj = EasyChatMAil.objects.filter(
                bot=bot_obj, api_name=api_name)[0]
            import pytz
            tz = pytz.timezone(settings.TIME_ZONE)
            timer_value = bot_obj.mail_sender_time_interval
            last_mail_sent_date = easychat_mail_obj.last_mail_sent_date.astimezone(
                tz)
            current_time = timezone.now().astimezone(tz)

            if (current_time - last_mail_sent_date).total_seconds() > int(timer_value) * 60:
                mail_sent_to_list = json.loads(
                    bot_obj.mail_sent_to_list)["items"]

                for item in mail_sent_to_list:
                    thread = threading.Thread(target=send_api_fail_mail, args=(
                        api_name, api_request_packet, api_response_packet, bot_obj, item, new_parameters_list), daemon=True)
                    thread.start()
                    logger.info("Threading started...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

                easychat_mail_obj.last_mail_sent_date = timezone.now()
                easychat_mail_obj.mail_sent_from = from_email_id
                easychat_mail_obj.mail_sent_to = json.dumps(
                    {"items": mail_sent_to_list})
                easychat_mail_obj.save()
        else:
            mail_sent_to_list = json.loads(bot_obj.mail_sent_to_list)["items"]

            for item in mail_sent_to_list:
                thread = threading.Thread(target=send_api_fail_mail, args=(
                    api_name, api_request_packet, api_response_packet, bot_obj, item, new_parameters_list), daemon=True)
                thread.start()
                logger.info("Threading started...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

            EasyChatMAil.objects.create(bot=bot_obj, api_name=api_name, last_mail_sent_date=timezone.now(
            ), mail_sent_from=from_email_id, mail_sent_to=json.dumps({"items": mail_sent_to_list}))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_send_api_failed_mail! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: check_and_send_broken_bot_mail
input_params:
    bot_id: id of bot
    channel: channel name
    request: request of user to check domain

Checks the time of last send mail for the same bot getting broken. If time exceeds mail_sender_time_interval, then sends new mail and update mail sent time
"""


def check_and_send_broken_bot_mail(bot_id, channel, window_location="", broken_mail_dump="{}"):
    try:
        import pytz
        tz = pytz.timezone(settings.TIME_ZONE)
        config = get_developer_console_settings()
        from_email_id = config.email_host_user
        bot_found = True
        bot_obj = None
        domain = settings.EASYCHAT_HOST_URL
        channel_objs = Channel.objects.filter(name=str(channel))
        channel_obj = None
        if channel_objs.exists():
            channel_obj = channel_objs.first()
        try:
            bot_objs = Bot.objects.filter(pk=int(bot_id))
            if bot_objs.exists():
                bot_obj = bot_objs.first()
                broken_bot_mail_objs = BrokenBotMail.objects.filter(
                    bot=bot_obj, domain=domain, channel=channel_obj)
            else:
                bot_found = False
                broken_bot_mail_objs = BrokenBotMail.objects.filter(
                    domain=domain, channel=channel_obj)
        except:
            bot_found = False
            broken_bot_mail_objs = BrokenBotMail.objects.filter(
                domain=domain, channel=channel_obj)

        timer_value = 1
        mail_sent_to_list = []
        mail_sent_to_list.append(str(config.csm_email_id))
        if bot_found:
            bot_info_obj = BotInfo.objects.get(bot=bot_obj)
            if not bot_info_obj.is_bot_break_email_notification_enabled or bot_obj.is_deleted:
                return
            timer_value = bot_info_obj.bot_break_mail_sender_time_interval
            mail_sent_to_list = json.loads(
                bot_info_obj.bot_break_mail_sent_to_list)["items"]

        if broken_bot_mail_objs.exists():
            broken_bot_mail_obj = broken_bot_mail_objs.first()
            last_mail_sent_date = broken_bot_mail_obj.last_mail_sent_date.astimezone(
                tz)
            current_time = timezone.now().astimezone(tz)

            if (current_time - last_mail_sent_date).total_seconds() > int(timer_value) * 60:

                for item in mail_sent_to_list:
                    thread = threading.Thread(target=send_bot_break_mail, args=(
                        item, bot_id, channel, window_location, broken_mail_dump), daemon=True)
                    thread.start()
                    logger.info("Threading started...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

                broken_bot_mail_obj.last_mail_sent_date = timezone.now()
                broken_bot_mail_obj.mail_sent_from = from_email_id
                broken_bot_mail_obj.mail_sent_to = json.dumps(
                    {"items": mail_sent_to_list})
                broken_bot_mail_obj.save()
        else:
            for item in mail_sent_to_list:
                thread = threading.Thread(target=send_bot_break_mail, args=(
                    item, bot_id, channel, window_location, broken_mail_dump), daemon=True)
                thread.start()
                logger.info("Threading started...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

            BrokenBotMail.objects.create(bot=bot_obj, channel=channel_obj, domain=domain, last_mail_sent_date=timezone.now(
            ), mail_sent_from=from_email_id, mail_sent_to=json.dumps({"items": mail_sent_to_list}))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_send_broken_bot_mail! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_masked_data

input_params:
    message: text message.
output_params:
    masked_data: Used to mask all confidential data such as PAN, Adhar, Account number and account balance etc.
"""


def get_masked_data(message, bot_obj, src, channel, user_id):
    final_string = message
    try:
        # pan
        pan_pattern = re.findall(
            r"[a-zA-Z]{3}[pP][a-zA-Z][1-9][0-9]{3}[a-zA-Z]", message)
        for item in pan_pattern:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # email id
        email_pattern = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', message)
        for item in email_pattern:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # dates
        # Regex date format: dd/mm/yyyy
        date_format_ddmmyyyy = re.findall(
            r"[\d]{1,2}/[\d]{1,2}/[\d]{2,4}", message)
        for item in date_format_ddmmyyyy:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # Regex date format: dd-mm-yy
        date_format_ddmmyyyy_two = re.findall(
            r"[\d]{1,2}-[\d]{1,2}-[\d]{2}", message)
        for item in date_format_ddmmyyyy_two:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # Regex date format: dd AUG YYYY
        date_format_ddmonthnameyyyy = re.findall(
            r"[\d]{1,2} [ADFJMNOS]\w* [\d]{2,4}", message)
        for item in date_format_ddmonthnameyyyy:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # Regex date format: AUG dd YYYY
        date_format_monthnameddyyyy = re.findall(
            r"[ADFJMNOS]\w* [\d]{1,2} [\d]{2,4}", message)
        for item in date_format_monthnameddyyyy:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # mobile number, account number, aadhar number (10-12 digits number
        # should have space before and after)
        mobile_pattern = re.findall(r"\b[0-9]{10,12}\b", message)
        for item in mobile_pattern:
            message = message.replace(
                item, "******")

        # age and address (1-3 digits number
        # should have space before and after)
        age_pattern = re.findall(r"\b[0-9]{1,3}\b", message)
        for item in age_pattern:
            message = message.replace(
                item, "******")

        # customer_id (any string that contains atleast 1 digit)
        id_pattern = re.findall(r"\b[A-Za-z0-9]*\d[A-Za-z0-9]*\b", message)
        for item in id_pattern:
            reg = r"\b" + str(item) + r"\b"
            message = re.sub(reg, "******", message)

        final_string = message
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_masked_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    return final_string


"""
function: get_encrypted_message

input_params:
    message: text message, it can be by bot or user.
output_params:
    encrypted_message: encrypted message by RSA ecryption using allincall_public_key key.
"""


def get_encrypted_message(message, bot_obj, src, channel, user_id, translate_message=True):
    try:
        message = get_translated_text(
            message, src, EasyChatTranslationCache, translate_message)
        if bot_obj != None and bot_obj.masking_enabled:
            message = get_masked_data(message, bot_obj, src, channel, user_id)

        custom_encrypt_obj = CustomEncrypt()

        encrypted_message = custom_encrypt_obj.encrypt(message)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_encrypted_message: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        encrypted_message = message

    return encrypted_message


"""
function: preprocessSpellChecker

output_params:
    preprocess the words for auto correct query [CONSTANTS.py]
"""


def preprocess_spell_checker(bot_obj=None):
    try:
        if bot_obj:
            words = EasyChatSpellCheckerWord.objects.filter(bot=bot_obj)
        else:
            bot_objs = Bot.objects.filter(is_deleted=False)
            words = EasyChatSpellCheckerWord.objects.filter(bot__in=bot_objs)

        words = list(words.values_list('word', flat=True))
        spell.word_frequency.load_json(words)

        for word in BANK_KEYWORDS_REMOVE:
            try:
                if word in spell.word_frequency:
                    spell.word_frequency.remove(word)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("preprocess_spell_checker word does not exist: %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                pass

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("preprocess_spell_checker: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def set_user(user_id, message, src, channel, bot_id, easychat_bot_user=None):
    logger.info("Into set_user method...", extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    user = None
    try:
        bot_obj = None
        bot_info_obj = None
        if easychat_bot_user and easychat_bot_user.bot_info_obj and easychat_bot_user.bot_obj:
            bot_info_obj = easychat_bot_user.bot_info_obj
            bot_obj = easychat_bot_user.bot_obj
        elif bot_id != None:
            bot_obj = Bot.objects.get(pk=int(bot_id))
            bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
            
        if easychat_bot_user and easychat_bot_user.translated_message:
            message = easychat_bot_user.translated_message
        else:
            message = check_and_get_message_after_translation(
                message, src, None, WhitelistedEnglishWords, EasyChatTranslationCache, bot_info_obj)
            if easychat_bot_user:
                easychat_bot_user.translated_message = message

        if user_id == "":
            user_id = str(uuid.uuid4())
            user = Profile.objects.create(
                user_id=user_id, user_pipe=message + "|", bot=bot_obj)
            logger.info("user is %s ", str(user), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        else:
            if channel == "WhatsApp":
                channel_obj = Channel.objects.get(name=channel)
                channel_obj = BotChannel.objects.get(
                    bot=bot_obj, channel=channel_obj)
            user = Profile.objects.select_related('tree').filter(user_id=user_id, bot=bot_obj).first()
            if user:
                user.user_pipe += message + "|"
                user.save(update_fields=['user_pipe'])
            else:
                user = Profile.objects.create(user_id=user_id, bot=bot_obj, user_pipe=message + "|")

        logger.info("Exit from set_user method...", extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("set_user %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    logger.info("returning user:%s", str(user), extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return user


"""
function: get_intent_name
input params:
    tree: active user tree
output
    intent_name

returns intent name as "INFLOW-INTENT" for inflow tree and
name of root intent in case of root tree
"""


def get_intent_name(tree, src, channel, bot_id, user_id):

    intent_name = None
    try:
        if tree is not None:
            intent_name = "INFLOW-INTENT"
            intent_obj = Intent.objects.values('name').filter(tree=tree, is_deleted=False, is_hidden=False, bots__pk=bot_id).first()
            if intent_obj:
                intent_name = intent_obj['name']
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    return intent_name


"""
function: execute_api
input params:
    user: active user object
    api_caller: executed code written by developer
    is_cache: True|False (to be saved permanetly in data model or not)
    cache_variable: json data will be saved in this variable
output:
    returns api_response after execution of code
"""


def execute_code_under_time_limit(lang, code_to_execute, easychat_bot_user, parameter, is_parameter_required):
    json_data = None
    try:
        if is_parameter_required:
            json_data = func_timeout.func_timeout(
                settings.EASYCHAT_PROCESSORS_MAX_RUNTIME_LIMIT, execute_code_based_on_language_with_parameter, args=[lang, code_to_execute, easychat_bot_user, parameter])
        else:
            json_data = func_timeout.func_timeout(
                settings.EASYCHAT_PROCESSORS_MAX_RUNTIME_LIMIT, execute_code_based_on_language_without_parameter, args=[lang, code_to_execute, easychat_bot_user])

    except func_timeout.FunctionTimedOut:  # noqa: F841
        logger.error(" processor took more than timelimit to execute_code ", extra={'AppName': 'EasyChat', 'user_id': str(
            easychat_bot_user.user_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return json_data


def execute_code_based_on_language_without_parameter(lang, code_to_execute, easychat_bot_user):
    json_data = None
    try:
        if lang == "1":
            result_dict = {'open': open_file}
            exec(str(code_to_execute), result_dict)
            json_data = result_dict['f']()
        elif lang == "2":
            json_data = get_java_processor_response(
                str(code_to_execute), easychat_bot_user.user, easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_id)
        elif lang == "3":
            json_data = get_php_processor_response(
                str(code_to_execute), easychat_bot_user.user, easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_id)
        else:
            fun = execjs.compile(code_to_execute)
            json_data = fun.call("f")

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("execute_code_based_on_language %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            easychat_bot_user.user_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return json_data


def execute_code_based_on_language_with_parameter(lang, code_to_execute, easychat_bot_user, parameter):
    json_data = None
    try:
        if lang == "1":
            result_dict = {'open': open_file}
            exec(str(code_to_execute), result_dict)
            json_data = result_dict['f'](parameter)
        elif lang == "2":
            json_data = get_java_processor_response(
                str(code_to_execute), easychat_bot_user.user, easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_id, parameter)
        elif lang == "3":
            json_data = get_php_processor_response(
                str(code_to_execute), easychat_bot_user.user, easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_id, parameter)
        else:
            fun = execjs.compile(code_to_execute)
            json_data = fun.call("f", parameter)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("execute_code_based_on_language %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            easychat_bot_user.user_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return json_data


def execute_api(user,
                api_caller,
                is_cache,
                cache_variable,
                src,
                channel,
                bot_id,
                lang="1"):
    logger.info("Into execute_api...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    tz = pytz.timezone(settings.TIME_ZONE)
    api_response = None
    try:
        if is_cache == True and len(Data.objects.filter(user=user,
                                                        variable=cache_variable)) > 0:
            # Allowed Cache Duration
            cached_duration = Config.objects.all()[0].cached_duration
            # Get Data Object
            data_obj = Data.objects.filter(
                user=user, variable=cache_variable).order_by('-pk')[0]
            # Get DateTime Value of cached
            cached_localize_datetime_obj = data_obj.cached_datetime.astimezone(
                tz)
            # Get current datetime value
            current_localize_datetime_obj = timezone.now().astimezone(tz)

            # If difference between cached datetime and current datetime <=
            # allowed cached datetime
            if (current_localize_datetime_obj - cached_localize_datetime_obj).total_seconds() <= int(cached_duration):
                logger.info("[ENGINE]: Retrieving api_response from cache. cache_variable: %s", str(
                    cache_variable), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
                api_response = json.loads(data_obj.get_value())
                logger.info("[ENGINE]: api_response: %s", str(api_response), extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
                logger.info("Exit from execute_api...", extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
                return api_response

        start_time = time.time()
        easychat_bot_user = EasyChatBotUser(
            user=user, src=src, bot_id=bot_id, channel=channel)
        parameter = ""
        is_parameter_required = False
        # run api tree according to programming language
        api_response = execute_code_under_time_limit(
            lang, str(api_caller), easychat_bot_user, parameter, is_parameter_required)

        end_time = time.time()

        elapsed_time = end_time - start_time

        api_response["elapsed_time"] = elapsed_time

        logger.info("[ENGINE]: api_response: %s", str(api_response), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        if is_cache == True:
            try:
                data_obj = Data.objects.get(user=user,
                                            variable=cache_variable)
                data_obj.value = json.dumps(api_response)
                data_obj.cached_datetime = timezone.now()
                data_obj.is_cache = True
                data_obj.save()
            except Exception:  # noqa: F841
                Data.objects.create(user=user,
                                    bot=Bot.objects.get(pk=int(bot_id)),
                                    variable=cache_variable,
                                    value=json.dumps(api_response),
                                    cached_datetime=timezone.now(),
                                    is_cache=True)

        is_api_executed_sucessfully = False
        if "status_code" in api_response and str(api_response["status_code"]) == "200":
            is_api_executed_sucessfully = True

        # If Current Tree API is not executed successfully then reset the flow
        # and set tree to None i.e user is out of the flow
        if not is_api_executed_sucessfully:
            user.tree = None
            user.save()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    logger.info("Exit from execute_api...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return api_response


"""
function: check_user_auth
input params:
    user: active user object
    response_json_data: Authentication API Response

check whether user is authenticated or not.
"""


def check_user_auth(user, response_json_data, src, channel, bot_id):
    try:
        if "AUTHENTICATION" in response_json_data:
            if "status" in response_json_data["AUTHENTICATION"]:
                if response_json_data["AUTHENTICATION"]["status"]:

                    logger.info("User Authentication", extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

                    authetication_type = response_json_data[
                        "AUTHENTICATION"]["type"]

                    logger.info("User Authentication Type: " +
                                str(authetication_type), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

                    user_params = response_json_data[
                        "AUTHENTICATION"]["user_params"]

                    authentication_obj = Authentication.objects.filter(
                        name=authetication_type).order_by('-pk')[0]

                    unique_token = "None"

                    if "unique_token" in response_json_data["AUTHENTICATION"]:
                        unique_token = response_json_data[
                            "AUTHENTICATION"]["unique_token"]
                        user_authentication = UserAuthentication.objects.filter(
                            unique_token=unique_token)
                        if user_authentication:
                            user_authentication = user_authentication[0]
                            tz = pytz.timezone(settings.TIME_ZONE)
                            auth_datetime_obj = user_authentication.last_update_time.astimezone(
                                tz)
                            current_datetime_obj = timezone.now().astimezone(tz)

                            if (current_datetime_obj - auth_datetime_obj).total_seconds() <= 30:
                                return True

                        user_authentication.delete()

                    user_authentication = UserAuthentication.objects.filter(
                        user=user, auth_type=authentication_obj)

                    user_authentication_obj = None
                    if len(user_authentication) == 0:
                        user_authentication_obj = UserAuthentication.objects.create(
                            user=user, auth_type=authentication_obj, unique_token=unique_token)

                        EasyChatUserAuthenticationStatus.objects.create(
                            user=user, is_authenticated=True, unique_token=unique_token, bot=Bot.objects.get(pk=int(bot_id)), channel=Channel.objects.get(name=channel))

                    elif len(user_authentication) == 1:
                        user_authentication_obj = user_authentication[0]

                    user_authentication_obj.start_time = timezone.now()
                    user_authentication_obj.user_params = json.dumps(
                        user_params)
                    user_authentication_obj.save()

                    save_data(user, user_params, src,
                              channel, bot_id, is_cache=True)

        elif "AUTHENTICATION_FAILURE" in response_json_data:
            if "status" in response_json_data["AUTHENTICATION_FAILURE"]:
                if response_json_data["AUTHENTICATION_FAILURE"]["status"]:

                    unique_token = "None"
                    if "unique_token" in response_json_data["AUTHENTICATION_FAILURE"]:
                        unique_token = response_json_data[
                            "AUTHENTICATION_FAILURE"]["unique_token"]

                    EasyChatUserAuthenticationStatus.objects.create(
                        user=user, is_authenticated=False, unique_token=unique_token, bot=Bot.objects.get(pk=int(bot_id)), channel=Channel.objects.get(name=channel))

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_user_auth %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        pass

    return False


"""
function: process_api
input params:
    user: active user object
    tree: active tree (where user is some flow)
output:
    json_response computed after api called.
"""


def process_api(user, tree, src, channel, bot_id):
    logger.info("Into process_api...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': str(
        src), 'channel': str(channel), 'bot_id': str(bot_id)})
    response_json_data = {}

    try:
        if tree is None:
            return response_json_data

        api_tree = tree.api_tree

        if api_tree != None:

            api_cache_variable = "API_TREE_CACHE_" + \
                str(api_tree.name).replace(" ", "").upper()

            try:

                api_caller = replace_data_values(
                    user, api_tree.api_caller, src, channel, bot_id)
                api_response = execute_api(user,
                                           api_caller,
                                           api_tree.is_cache,
                                           api_cache_variable,
                                           src,
                                           channel,
                                           bot_id,
                                           api_tree.processor_lang)

                response_json_data = api_response
                is_cache = api_tree.is_cache
                if "data" in response_json_data:
                    if "is_cache" in response_json_data["data"] and response_json_data["data"]["is_cache"]:
                        is_cache = True
                        api_tree.is_cache = is_cache
                        api_tree.save()

                save_data(user, response_json_data, src,
                          channel, bot_id, is_cache)
                user_auth = check_user_auth(
                    user, response_json_data, src, channel, bot_id)

                response_json_data["user_auth"] = user_auth

            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("[ENGINE]: %s at %s", str(e),
                             str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    logger.info("Exit from process_api...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': str(
        src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return response_json_data


"""
function: is_flow_ended
input params:
    user: active user object
    tree: current active tree
output:
    return True if the flow is ended else return False
"""


def is_flow_ended(user, tree, src, channel, bot_id):
    logger.info("[ENGINE]: Into isFlowEnded...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    if user.tree != None and user.tree.children != None:
        if len(user.tree.children.filter(is_deleted=False)) == 0:
            logger.info("[ENGINE]: Exit from isFlowEnded...", extra={'AppName': 'EasyChat', 'user_id': str(
                user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
            return True
    logger.info("[ENGINE]: Exit from isFlowEnded...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return False


"""
function: build_android_response
input params:
    webhook_request_packet: request packet from android channel
    bot_id: id of bot
    bot_name: name of bot
output:
    return response for android channel according to template
"""


def build_android_response(webhook_request_packet, bot_id, bot_name):
    response = {}
    try:
        channel_name = "Android"
        user_query = webhook_request_packet["query"]

        user_id = webhook_request_packet["user_id"]
        src = webhook_request_packet["src"]
        channel_params = json.loads(webhook_request_packet["channel_params"])
        default_response_packet = execute_query(
            user_id, bot_id, bot_name, user_query, src, channel_name, channel_params, user_query)

        if 'tables' not in default_response_packet['response']:
            default_response_packet['response']['tables'] = []
        if len(default_response_packet['response']['tables']) == 0:
            default_response_packet['response']['tables'] = []
        if str(default_response_packet["status_code"]) == "200" or str(default_response_packet["status_message"]) == "Your file has been successfully uploaded.":
            response = default_response_packet
            if str(default_response_packet["status_code"]) != "200":
                response["status_code"] = 200
        else:
            response = copy.deepcopy(DEFAULT_RESPONSE)
            response["status_code"] = 500
            response["status_message"] = "ERROR"

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        response = copy.deepcopy(DEFAULT_RESPONSE)
        response["status_code"] = 500
        response["status_message"] = str(e)

    return response


"""
function: is_feedback_required
input params:
    user: active user object
output:
    return True if feedback should be taken from user else return False
"""


def is_feedback_required(user, src, channel, bot_id, is_feedback_required=False):
    logger.info("Into is_feedback_required...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': str(
        src), 'channel': str(channel), 'bot_id': str(bot_id)})
    try:
        # Check for global intent feedback
        if is_feedback_required:
            try:
                # check for intent level feedback
                is_feedback_required = Data.objects.filter(
                    user=user, variable="is_feedback_required").order_by('-pk')[0].get_value()
                if str(is_feedback_required) == "true":
                    is_feedback_required = True
                else:
                    is_feedback_required = False
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning(
                    "is_feedback_required: intent level feedback: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
                is_feedback_required = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_feedback_required: %s at %s ", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    logger.info("Exit from is_feedback_required: status: %s",
                str(is_feedback_required), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return is_feedback_required


"""
function: is_authentication_required
input params:
    user: active user object
output:
    return True if identified intent required authentication to process further
    else return False
"""


def is_authentication_required(user, src, channel, bot_id):
    logger.info("Into is_authentication_required...", extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    is_authentication_required = False
    try:
        is_authentication_required = Data.objects.filter(
            user=user, variable="is_authentication_required").order_by('-pk')[0].get_value()
        if str(is_authentication_required) == "true":
            is_authentication_required = True
        else:
            is_authentication_required = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("is_authentication_required: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                       'AppName': 'EasyChat', 'user_id': 'None', 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        is_authentication_required = False

    logger.info("Exit from is_authentication_required: status: %s",
                str(is_authentication_required), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return is_authentication_required


"""
function: is_active_user_authenticated
input params:
    user: active user object
output:
    return True if active user is already authenticated else return False

"""


def is_active_user_authenticated(user, src, channel, bot_id):
    logger.info("Into is_active_user_authenticated...", extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    is_user_authenticated = False
    try:
        is_user_authenticated = Data.objects.filter(
            user=user, variable="is_user_authenticated").order_by('-pk')[0].get_value()
        logger.info(is_user_authenticated, extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        if str(is_user_authenticated) == "true":
            is_user_authenticated = True
        else:
            is_user_authenticated = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("is_active_user_authenticated: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                       'AppName': 'EasyChat', 'user_id': 'None', 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        is_user_authenticated = False

    logger.info("Exit from is_active_user_authenticated: status: %s",
                str(is_user_authenticated), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return is_user_authenticated


"""
function: is_form_assist_activated
input params:
    user: active user object
output:
    return True if form assist is enabled or not
"""


def is_form_assist_activated(user, src, channel, bot_id):
    logger.info("Into is_form_assist_activated...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    is_form_assist = False
    try:
        is_form_assist = Data.objects.filter(
            user=user, variable="is_form_assist").order_by('-pk')

        if not is_form_assist.exists():
            return False

        is_form_assist = is_form_assist.first().get_value()

        if str(is_form_assist) == "true":
            is_form_assist = True
        else:
            is_form_assist = False

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_form_assist_activated: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    logger.info("Exit from is_form_assist_activated: status: %s",
                str(is_form_assist), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return is_form_assist


def get_last_identified_intent_name(user, src, channel, bot_id):
    last_identified_intent_name = None
    try:
        logger.info("Into get_last_identified_intent_name...", extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        last_identified_intent_obj = Data.objects.filter(
            user=user, variable="last_identified_intent_name").order_by('-pk').first()

        last_identified_intent_name = None
        if last_identified_intent_obj:
            last_identified_intent_name = last_identified_intent_obj.get_value()

        # last_identified_intent_name = Data.objects.filter(
        # user=user,
        # variable="last_identified_intent_name").order_by('-pk').first()[0].get_value()

        if last_identified_intent_name is not None:
            last_identified_intent_name = ast.literal_eval(
                last_identified_intent_name)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_last_identified_intent_name: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        last_identified_intent_name = None

    logger.info("Exit from get_last_identified_intent_name: intent name: %s", str(
        last_identified_intent_name), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return str(last_identified_intent_name)


def spell_checker(message, user_id, src, channel, bot_obj, bot_id):
    corrected_message = ""
    logger.info("Running Spell Checker on Bot Query", extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    try:
        query_texts = message.split(" ")
        for query_text in query_texts:
            if len(query_text) >= 20:
                corrected_message += query_text + " "
                continue
            list_of_potential_words = spell.candidates(query_text)
            data_found = False
            spell_checker_word = EasyChatSpellCheckerWord.objects.filter(
                word__in=list_of_potential_words, bot=bot_obj).first()
            if spell_checker_word:
                corrected_message += spell_checker_word.word + " "
                data_found = True
            # for word in list_of_potential_words:
            #     if EasyChatSpellCheckerWord.objects.filter(word=word, bot=bot_obj):
            #         corrected_message += word
            #         corrected_message += " "
            #         data_found = True
            #         break
            
            if not data_found:
                # corrected_message += spell.correction(query_text)
                corrected_message += max(sorted(list_of_potential_words), key=spell.__getitem__)
                corrected_message += " "
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EasyChatApp[utils.py]: Running Spell Checker Failed: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return corrected_message


"""
function: get_easy_search_results
input_params:
    query: user query, bot_obj and user_obj
output_params:
    returns json containig easy search result data based on user query
"""


def get_easy_search_results(query, user, bot_obj, src, channel):
    try:
        corrected_query = ""
        logger.info("Running Spell Checker", extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
        query_texts = query.split(" ")

        for query_text in query_texts:
            corrected_query += spell.correction(query_text)
            corrected_query += " "

        logger.info("INSIDE SEARCHING EASY SEARCH RESULTS", extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})

        corrected_query = corrected_query[:-1]
        res = search_query(corrected_query)
        easysearch_hits = []

        try:
            easysearch_hits = res["hits"]["hits"]
        except Exception:
            pass

        easy_search_results = []

        for easysearch_hit in easysearch_hits:

            source_name = easysearch_hit['_source']['name']

            source_name = source_name.lower()

            if(easysearch_hit['_source']['bot'] == bot_obj.slug):

                if "url_pk" not in easysearch_hit["_source"]:
                    continue

                filter_url = easysearch_hit['_source']['url']
                filter_title = easysearch_hit['_source']['title']
                filter_description = re.sub(
                    '[^A-Za-z0-9]+', ' ', easysearch_hit['_source']['description'][:200])
                filter_description = str(filter_description + "...")
                temp_dict = {}
                temp_dict["link"] = filter_url
                temp_dict["title"] = filter_title
                temp_dict["content"] = filter_description
                temp_dict["img_url"] = ""
                easy_search_results.append(temp_dict)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error Easy Search Results %s at line no> %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
        easy_search_results = []

    return easy_search_results


"""
function: build_web_response
input params:
    user: active user object
    bot_obj: active bot object
    bot_name: bot name passed as user params
    tree: active user tree
    message: user query received
    src: en | hi
    channel_obj: channel object
    status_re_sentence: True|False
    json_api_resp: JSON Response computed after executing api
    is_intent_tree: Designates whether initial intent or not.
output:
    return rich json response
"""


def build_web_response(user,
                       tree,
                       message,
                       status_re_sentence,
                       json_api_resp,
                       easychat_bot_user,
                       easychat_params):

    bot_obj = easychat_bot_user.bot_obj
    if easychat_bot_user.bot_info_obj:
        bot_info_obj = easychat_bot_user.bot_info_obj
    else:
        bot_info_obj = get_bot_info_object(bot_obj)
    validation_obj = EasyChatInputValidation()
    src = easychat_bot_user.src
    channel_obj = easychat_params.channel_obj
    lower_channel_name = channel_obj.name.strip().lower().replace(" ", "_")
    intent_icon_channel_choices_info = bot_info_obj.get_intent_icon_channel_choices_info()
    language_template_obj = easychat_bot_user.language_template_obj
    category_name = easychat_bot_user.category_name
    if easychat_bot_user and easychat_bot_user.category_obj:
        category_obj = easychat_bot_user.category_obj
    else:
        category_obj = get_category_obj(bot_obj, category_name)
        easychat_bot_user.category_obj = category_obj

    logger.info("Into build_web_response...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})
    response = copy.deepcopy(DEFAULT_RESPONSE)
    response["status_code"] = 200
    response["is_attachment_required"] = False
    response["choosen_file_type"] = "none"
    response["status_message"] = "SUCCESS"
    response["user_id"] = user.user_id
    response["bot_id"] = bot_obj.pk
    response["response"]["is_authentication_required"] = False
    response["response"]["is_flow_ended"] = False
    response["response"]["is_bot_switch"] = False
    response["response"]["is_text_to_speech_required"] = False
    response["response"]["google_search_results"] = []
    response["response"]["easy_search_results"] = []
    response["response"]["is_go_back_enabled"] = False
    response["response"][
        "is_enable_intent_icon"] = bot_info_obj.enable_intent_icon
    response["response"]["is_exit_tree"] = False
    response["response"]["enable_transfer_agent"] = False
    response["response"]["barge_in"] = False
    response["response"]["hints"] = []

    try:
        # check user auth
        if "user_auth" in json_api_resp and (json_api_resp["user_auth"] == True or json_api_resp["user_auth"] == "true"):
            return build_continuous_session_running_error_response(user.user_id, src, channel_obj.name, bot_obj.pk, language_template_obj)

        # Check whether intent requires authentication or not
        is_authentication_require = is_authentication_required(
            user, src, channel_obj.name, bot_obj.pk)

        is_user_authenticated = is_active_user_authenticated(
            user, src, channel_obj.name, bot_obj.pk)

        response["response"]["last_identified_intent_name"] = get_last_identified_intent_name(
            user, src, channel_obj.name, bot_obj.pk)

        if is_authentication_require:
            response["response"]["is_authentication_required"] = True

        if is_user_authenticated:
            response["response"]["is_user_authenticated"] = True

        if tree is not None:
            response["response"]["is_exit_tree"] = tree.is_exit_tree

        if tree is not None and channel_obj.name == "Voice":
            response["response"][
                "enable_transfer_agent"] = tree.enable_transfer_agent
            response["response"]["barge_in"] = tree.check_barge_in_enablement()

        if tree is not None:
            child_tree_hints = []
            for child_tree in tree.children.all():
                child_tree_hints.extend(
                    [keyword.strip() for keyword in child_tree.accept_keywords.split(",") if keyword.strip() != ""])
            response["response"]["hints"].extend(child_tree_hints)

        # Check whether feedback is required or not
        is_feedback_require = is_feedback_required(
            user, src, channel_obj.name, bot_obj.pk, bot_obj.is_feedback_required)

        response["response"][
            "is_text_to_speech_required"] = bot_obj.is_text_to_speech_required

        if tree is not None:

            language_obj = Language.objects.get(lang=src)

            tree_tuned_object = LanguageTuningTreeTable.objects.filter(
                tree=tree, language=language_obj)

            if src != "en" and tree_tuned_object.exists():
                tree_tuned_obj = tree_tuned_object.first()
                bot_sentence = replace_data_values(
                    user, str(tree_tuned_obj.response.sentence), src, channel_obj.name, bot_obj.pk, True)
                bot_response = json.loads(
                    str(bot_sentence), strict=False)["items"][0]
            else:
                bot_sentence = replace_data_values(
                    user, str(tree.response.sentence), src, channel_obj.name, bot_obj.pk)
                bot_response = json.loads(
                    str(bot_sentence), strict=False)["items"][0]

            text_response = bot_response["text_response"]
            # text_response = text_response.replace("<p><br></p>", "<p></p>").replace(
            #     "</p><p>", "<br>").replace("</p>", "").replace("<p>", "")
            text_response = str(BeautifulSoup(
                text_response, 'html.parser'))

            speech_response = process_speech_response_query(
                bot_response["text_response"])
            if "speech_response" in bot_response:
                speech_response = bot_response["speech_response"]
            # speech_response = speech_response.replace("<p><br></p>", "<p></p>").replace(
            #     "<p>", "").replace("</p>", "<br>")

            if 'tooltip_response' in bot_response:
                response["response"]["tooltip_response"] = bot_response[
                    'tooltip_response']
            else:
                response["response"]["tooltip_response"] = ""

            if tree.response.is_timed_response_present:
                response["timer_value"] = tree.response.timer_value
                response["auto_response"] = tree.response.auto_response

            if str(src) != "en" and "hinglish_response" in bot_response:
                if bot_response["hinglish_response"].strip() != "":
                    text_response = bot_response["hinglish_response"]
                    speech_response = process_speech_response_query(
                        bot_response["hinglish_response"])

            text_response = validation_obj.reverse_sanitize_html(text_response)
            response["response"]["text_response"][
                "text"] = text_response
            response["response"]["speech_response"][
                "text"] = speech_response
            if "ssml_response" in bot_response:
                response["response"]["ssml_response"][
                    "text"] = bot_response["ssml_response"]
            else:
                response["response"]["ssml_response"][
                    "text"] = speech_response

            if status_re_sentence and "text_reprompt_response" in bot_response:
                response["response"]["text_response"][
                    "text"] = bot_response["text_reprompt_response"]
                bot_reprompt_text = process_speech_response_query(
                    bot_response["text_reprompt_response"])
                response["response"]["speech_response"][
                    "text"] = bot_reprompt_text

                if "speech_reprompt_response" in bot_response:
                    response["response"]["speech_response"][
                        "text"] = bot_response["speech_reprompt_response"]

            if ("dynamic_widget_type" in json_api_resp) and (json_api_resp["dynamic_widget_type"]) and ("modes" in json_api_resp) and (json_api_resp["modes"]) and ("modes_param" in json_api_resp) and (json_api_resp["modes_param"]):
                modes = {}
                modes_param = {}

                try:
                    modes = json.loads(tree.response.modes)
                except:
                    logger.warning("No modes in tree:", extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

                try:
                    modes_param = json.loads(tree.response.modes_param)
                except:
                    logger.warning("No modes_param in tree:", extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})
                modes.update(json_api_resp["modes"])
                modes_param.update(json_api_resp["modes_param"])

                for widget_toggle in WIDGETS_TOGGLE_NAME_MAPPER:
                    if WIDGETS_TOGGLE_NAME_MAPPER[widget_toggle] != json_api_resp["dynamic_widget_type"].strip().lower():
                        modes[widget_toggle] = "false"

                modes = replace_data_values(
                    user, json.dumps(modes), src, channel_obj.name, bot_obj.pk)
                modes_param = replace_data_values(
                    user, json.dumps(modes_param), src, channel_obj.name, bot_obj.pk)
                response["response"]["dynamic_widget_type"] = json_api_resp["dynamic_widget_type"]

            else:
                modes = str(tree.response.modes)

                if "modes" in json_api_resp and "list_message_header" in json_api_resp["modes"]:
                    modes = json.loads(tree.response.modes)
                    modes.update(json_api_resp["modes"])
                    modes = json.dumps(modes)

                modes = replace_data_values(
                    user, modes, src, channel_obj.name, bot_obj.pk)

                modes_param = replace_data_values(
                    user, str(tree.response.modes_param), src, channel_obj.name, bot_obj.pk)

            response["response"]["text_response"][
                "modes"] = json.loads(str(modes))

            response["response"]["text_response"][
                "modes_param"] = json.loads(str(modes_param))

            modes = {}
            modes_param = {}

            modes = response["response"]["text_response"]["modes"]
            modes_param = response["response"]["text_response"]["modes_param"]
            if "is_attachment_required" in modes and str(modes["is_attachment_required"]) == "true":
                response["is_attachment_required"] = True
            else:
                response["is_attachment_required"] = False

            if "choosen_file_type" in modes_param:
                response["choosen_file_type"] = modes_param[
                    "choosen_file_type"]
            else:
                response["choosen_file_type"] = "none"

            response["response"]["choices"] = []
            response["response"]["cards"] = []
            response["response"]["images"] = []
            response["response"]["videos"] = []
            response["response"]["recommendations"] = []
            response["response"]["tables"] = []

            try:
                response["response"]["choices"] = json_api_resp["choices"]
            except Exception:
                logger.warning("No choices from API Response:", extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

            try:
                response["response"]["cards"] = json_api_resp["cards"]
            except Exception:
                logger.warning("No cards from API Response:", extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

            try:
                response["response"]["images"] = json_api_resp["images"]
            except Exception:
                logger.warning("No images from API Response:", extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

            try:
                response["response"]["videos"] = json_api_resp["videos"]
            except Exception:
                logger.warning("No videos from API Response:", extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

            try:
                response["response"]["tables"] = json_api_resp["tables"]
            except Exception:
                logger.warning("No tables from API Response:", extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

            try:
                response["response"]["recommendations"] = json_api_resp[
                    "recommendations"]
            except Exception:  # noqa: F841
                logger.warning("No recommendations from API Response:", extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

            if len(response["response"]["choices"]) == 0:
                choices = tree.response.choices.all()
                response["response"]["choices"] = []
                choices_hints = []

                if len(choices) > 1:
                    for choice in choices:
                        response["response"]["choices"].append(
                            {"value": choice.value, "display": choice.display})
                        choices_hints.append(choice.value)
                else:
                    child_trees = tree.children.filter(is_deleted=False)
                    if len(child_trees) > 1 and tree.is_child_tree_visible == True:
                        for child_tree in child_trees:
                            if str(src) != "en":
                                tuned_tree_obj = LanguageTuningTreeTable.objects.filter(
                                    tree=child_tree, language=language_obj)
                                if tuned_tree_obj.exists():
                                    multilingual_name = tuned_tree_obj.first().multilingual_name
                                    response["response"]["choices"].append({
                                        "value": multilingual_name,
                                        "display": multilingual_name,
                                        "tree_pk": child_tree.pk
                                    })
                                    choices_hints.append(multilingual_name)
                                else:
                                    response["response"]["choices"].append({
                                        "value": child_tree.name,
                                        "display": child_tree.name,
                                        "tree_pk": child_tree.pk
                                    })
                                    choices_hints.append(child_tree.name)
                            else:
                                response["response"]["choices"].append({
                                    "value": child_tree.name,
                                    "display": child_tree.name,
                                    "tree_pk": child_tree.pk
                                })
                                choices_hints.append(child_tree.name)

                response["response"]["hints"].extend(choices_hints)

            if len(response["response"]["recommendations"]) == 0:

                recommended_intent_pk_list = []

                try:
                    recommended_intent_pk_list = json.loads(
                        tree.response.recommendations)["items"]
                except Exception:  # noqa: F841
                    logger.warning("No recommendations in tree:", extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

                recommendations = []
                recommendations_hints = []

                for intent_pk in recommended_intent_pk_list:
                    try:
                        intent_pk = int(intent_pk)
                        intent_obj = Intent.objects.filter(
                            pk=intent_pk, is_deleted=False, is_hidden=False, channels=channel_obj)
                        if category_obj:
                            intent_obj = intent_obj.filter(Q(category=category_obj) | Q(category__isnull=True))
                        
                        intent_obj = intent_obj.first()
                        intent_icon = ""
                        if intent_obj:

                            if bot_info_obj.enable_intent_icon and (lower_channel_name in intent_icon_channel_choices_info) and ("3" in intent_icon_channel_choices_info[lower_channel_name]):
                                if intent_obj.build_in_intent_icon:
                                    intent_icon = intent_obj.build_in_intent_icon.icon
                                else:
                                    intent_icon = '<img width="40px" height="40px" src="' + intent_obj.intent_icon + '">'

                            if str(src) != "en":
                                multilingual_name = get_multilingual_intent_name(
                                    intent_obj, src)
                                if multilingual_name is not None and multilingual_name.strip() != "":
                                    recommendations.append({
                                        "name": multilingual_name,
                                        "id": intent_pk,
                                        "tree_pk": intent_obj.tree.pk,
                                        "intent_icon": intent_icon
                                    })
                                    recommendations_hints.append(
                                        multilingual_name)
                                else:
                                    recommendations.append({
                                        "name": intent_obj.name,
                                        "id": intent_pk,
                                        "tree_pk": intent_obj.tree.pk,
                                        "intent_icon": intent_icon
                                    })
                                    recommendations_hints.append(
                                        intent_obj.name)
                            else:
                                recommendations.append({
                                    "name": intent_obj.name,
                                    "id": intent_pk,
                                    "tree_pk": intent_obj.tree.pk,
                                    "intent_icon": intent_icon
                                })
                                recommendations_hints.append(intent_obj.name)
                    except Exception:  # noqa: F841
                        logger.warning("Unable to get intent name based on intent_pk:", extra={'AppName': 'EasyChat', 'user_id': str(
                            user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

                response["response"]["recommendations"] = recommendations
                response["response"]["hints"].extend(recommendations_hints)

            if channel_obj.name.strip().lower() == "whatsapp":

                whatsapp_menu_sections = []
                total_no_buttons = 0

                if tree.enable_whatsapp_menu_format:

                    whatsapp_menu_section_objs = WhatsAppMenuSection.objects.filter(tree=tree).order_by("pk")

                    for whatsapp_menu_section_obj in whatsapp_menu_section_objs:
                        whatsapp_menu_details = {"buttons": []}
                        whatsapp_menu_details["section_title"] = whatsapp_menu_section_obj.title
                        if src != "en":
                            whatsapp_menu_details["section_title"] = get_translated_text(whatsapp_menu_details["section_title"], src, EasyChatTranslationCache)
                        
                        if tree.is_child_tree_visible and whatsapp_menu_section_obj.child_trees:
                            child_trees = json.loads(whatsapp_menu_section_obj.child_trees)

                            for child_tree in child_trees:
                                child_tree_obj = Tree.objects.filter(pk=child_tree, is_deleted=False).first()
                                if child_tree_obj:
                                    child_tree_details = {}

                                    child_tree_details["name"] = child_tree_obj.get_whatsapp_short_name()
                                    child_tree_details["full_name"] = str(child_tree_obj.name)
                                    child_tree_details["description"] = child_tree_obj.get_whatsapp_description()

                                    if src != "en":
                                        child_tree_details["name"] = get_translated_text(child_tree_details["name"], src, EasyChatTranslationCache)
                                        child_tree_details["full_name"] = get_translated_text(child_tree_details["full_name"], src, EasyChatTranslationCache)
                                        child_tree_details["description"] = get_translated_text(child_tree_details["description"], src, EasyChatTranslationCache)

                                    whatsapp_menu_details["buttons"].append(child_tree_details)
                                    total_no_buttons += 1

                        if whatsapp_menu_section_obj.main_intents:
                            main_intents = json.loads(whatsapp_menu_section_obj.main_intents)

                            for main_intent in main_intents:
                                main_intent_obj = Intent.objects.filter(pk=main_intent, is_deleted=False, is_small_talk=False, is_hidden=False).first()

                                if main_intent_obj:
                                    main_intent_details = {}

                                    main_intent_details["id"] = str(main_intent_obj.pk)
                                    main_intent_details["name"] = main_intent_obj.tree.get_whatsapp_short_name()
                                    main_intent_details["description"] = main_intent_obj.tree.get_whatsapp_description()

                                    if src != "en":
                                        main_intent_details["name"] = get_translated_text(main_intent_details["name"], src, EasyChatTranslationCache)
                                        main_intent_details["description"] = get_translated_text(main_intent_details["description"], src, EasyChatTranslationCache)

                                    whatsapp_menu_details["buttons"].append(main_intent_details)
                                    total_no_buttons += 1

                        if whatsapp_menu_details["buttons"]:
                            whatsapp_menu_sections.append(whatsapp_menu_details)

                total_whatsapp_menu_sections = len(whatsapp_menu_sections)

                if "whatsapp_menu_sections" in json_api_resp:
                    for dynamic_whatsapp_menu_section in json_api_resp["whatsapp_menu_sections"]:
                        menu_section_index = -1
                        for index in range(total_whatsapp_menu_sections):
                            if whatsapp_menu_sections[index]["section_title"] == dynamic_whatsapp_menu_section["section_title"]:
                                menu_section_index = index
                                break

                        if menu_section_index != -1:
                            whatsapp_menu_dict = whatsapp_menu_sections[menu_section_index]
                        else:
                            whatsapp_menu_dict = {}
                            whatsapp_menu_dict["section_title"] = dynamic_whatsapp_menu_section["section_title"]
                            if src != "en":
                                whatsapp_menu_dict["section_title"] = get_translated_text(whatsapp_menu_dict["section_title"], src, EasyChatTranslationCache)

                            whatsapp_menu_dict["buttons"] = []

                        for button in dynamic_whatsapp_menu_section["buttons"]:
                            button_dict = {}
                            if type(button) == dict:
                                button_dict["name"] = button["name"]
                                button_dict["description"] = button["description"]

                            else:
                                button_dict["name"] = button
                                button_dict["description"] = ""

                            if src != "en":
                                button_dict["name"] = get_translated_text(button_dict["name"], src, EasyChatTranslationCache)
                                button_dict["description"] = get_translated_text(button_dict["description"], src, EasyChatTranslationCache)

                            whatsapp_menu_dict["buttons"].append(button_dict)
                            total_no_buttons += 1

                        if menu_section_index == -1:
                            whatsapp_menu_sections.append(whatsapp_menu_dict)

                if whatsapp_menu_sections and total_no_buttons > 3 and total_no_buttons < 11:
                    response["response"]["whatsapp_menu_sections"] = whatsapp_menu_sections
                
            if len(response["response"]["cards"]) == 0:
                try:
                    card_details = []
                    if src != "en" and LanguageTuningTreeTable.objects.filter(tree=tree, language=language_obj).exists():
                        tree_tuned_obj = LanguageTuningTreeTable.objects.filter(
                            tree=tree, language=language_obj).first()
                        card_details = replace_data_values(
                            user, tree_tuned_obj.response.cards, src, channel_obj.name, bot_obj.pk, True)
                    else:
                        card_details = replace_data_values(
                            user, tree.response.cards, src, channel_obj.name, bot_obj.pk)
                    try:
                        response["response"]["cards"] = json.loads(ast.literal_eval(card_details)[
                            "items"])
                    except Exception:
                        response["response"]["cards"] = json.loads(card_details)[
                            "items"]

                except Exception:
                    logger.warning("No cards in tree:", extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})
            if len(response["response"]["images"]) == 0:
                try:
                    image_details = replace_data_values(
                        user, tree.response.images, src, channel_obj.name, bot_obj.pk)
                    response["response"]["images"] = json.loads(image_details)[
                        "items"]
                except Exception:
                    logger.warning("No cards in tree:", extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

            if len(response["response"]["videos"]) == 0:
                try:
                    video_details = replace_data_values(
                        user, tree.response.videos, src, channel_obj.name, bot_obj.pk)
                    response["response"]["videos"] = json.loads(video_details)[
                        "items"]
                except Exception:  # noqa: F841
                    logger.warning("No videos in tree:", extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

            if len(response["response"]["tables"]) == 0:
                try:
                    tables_details = []
                    if src != "en" and LanguageTuningTreeTable.objects.filter(tree=tree, language=language_obj).exists():
                        tree_tuned_obj = LanguageTuningTreeTable.objects.filter(
                            tree=tree, language=language_obj).first()
                        tables_details = replace_data_values(
                            user, tree_tuned_obj.response.table, src, channel_obj.name, bot_obj.pk, True)
                    else:
                        tables_details = replace_data_values(
                            user, tree.response.table, src, channel_obj.name, bot_obj.pk)
                    response["response"]["tables"] = json.loads(tables_details)[
                        "items"]
                except Exception:
                    logger.warning("No tables in tree:", extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})
            if not easychat_params.is_intent_tree:

                if tree.is_go_back_enabled and tree.children.filter(is_deleted=False) and not Intent.objects.filter(tree=tree):
                    recommendations = response["response"]["recommendations"]
                    intent_icon = ""
                    if bot_info_obj.enable_intent_icon and (lower_channel_name in intent_icon_channel_choices_info) and ("5" in intent_icon_channel_choices_info[lower_channel_name]):
                        intent_icon = "true"
                    recommendations.append({
                        "name": "Go Back",
                        "intent_icon": intent_icon
                    })
                    response["response"]["recommendations"] = recommendations
                    response["response"]["is_go_back_enabled"] = True

            response["response"]["is_feedback_required"] = False

            if is_flow_ended(user, tree, src, channel_obj.name, bot_obj.pk):
                response["response"]["is_flow_ended"] = True

                if is_feedback_require:

                    item = {}

                    response["response"]["is_feedback_required"] = True

                    if channel_obj.name in ["Web", "Android", "iOS"]:
                        response["response"][
                            "feedback_id"] = MISDashboard.objects.latest('id').id + 1
                    else:
                        item = {
                            "display": "Helpful",
                            "value": "Helpful"
                        }
                        response["response"]["choices"].append(item)

                        item = {
                            "display": "Unhelpful",
                            "value": "Unhelpful"
                        }

                        response["response"]["choices"].append(item)

                    response["response"]["text_response"][
                        "modes"]["is_button"] = "true"

            if channel_obj.name == "WhatsApp":
                response["response"][
                    "whatsapp_list_message_header"] = "Options"
                if tree.response:
                    response["response"][
                        "whatsapp_list_message_header"] = tree.response.whatsapp_list_message_header

        else:
            response = build_channel_failure_response(
                response, easychat_bot_user, bot_obj, channel_obj, bot_info_obj, category_obj, message, user, language_template_obj, src, easychat_params)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("build_web_response:" + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})
        response = build_internal_server_error_response(
            user.user_id, src, channel_obj.name, bot_obj.pk, language_template_obj)

    logger.info("Exit from build_web_response...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})
    return response


"""
function: successfull_file_upload_response
input params:
    e: error string
output:
    return rich json response containg error string
"""


def successfull_file_upload_response(language_template_obj):
    try:
        return language_template_obj.file_upload_success_text
    except Exception:  # no need to add logger
        return "Your file has been successfully uploaded."


"""
function: successfull_file_upload_response
input params:
    e: error string
output:
    return rich json response containg error string
"""


def success_bot_response(message):
    response = json.dumps(copy.deepcopy(DEFAULT_RESPONSE))
    response = json.loads(response)
    response["status_code"] = "200"
    response["status_message"] = str(message)
    response["response"]["text_response"]["text"] = str(message)
    return response


"""
function: load_old_data
input params:
    user: active user object

This function loads uncached data objects from user's previous_data.
"""


def load_old_data(user, src, channel, bot_id):
    logger.info("Into load_old_data...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    try:
        old_data_json = json.loads(user.previous_data)
        bot_obj = None
        if bot_id:
            bot_obj = Bot.objects.get(pk=int(bot_id))
        for key in old_data_json:
            Data.objects.create(user=user, bot=bot_obj, variable=str(
                key), value=str(old_data_json[key]))
        user.previous_data = "{}"
        logger.info(
            "Successfully loaded user's old data from user.previous_data", extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in load_old_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    logger.info("Exit from load_old_data...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})


"""
function: check_terminal_tree_logic
input params:
    user: active user object

This function deletes uncached data objects at the end of the flow.
"""


def check_terminal_tree_logic(user, src, channel, bot_id):
    try:
        logger.info("Inside check_terminal_tree_logic method...", extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        if user.tree is not None:
            if len(user.tree.children.filter(is_deleted=False)) == 0:
                logger.info(
                    "Terminal Tree logic: Delete uncached data objects", extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
                Data.objects.filter(user=user, is_cache=False).delete()
                if user.previous_tree != None:
                    logger.info("User's previous tree is: %s",
                                str(user.previous_tree), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
                    load_old_data(user, src, channel, bot_id)
                    user.tree = user.previous_tree
                    user.previous_tree = None
                else:
                    user.tree = None
                user.save(update_fields=['tree', 'previous_tree'])
        logger.info("Exit from check_terminal_tree_logic method...", extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: check_terminal_tree_logic: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})


"""
function: execute_pipeprocessor
input params:
    user: active user object

execute given function and save details into data model.
mostly used for processing user pipe
"""


def execute_pipeprocessor(user, bot_obj, src, channel):

    try:
        pipe_processor = replace_data_values(
            user, user.tree.pipe_processor.function, src, channel, bot_obj.pk)
        lang = user.tree.pipe_processor.processor_lang

        start_time = time.time()

        # execute pipe processor according to programming lang
        easychat_bot_user = EasyChatBotUser(
            user=user, src=src, bot_id=bot_obj.pk, channel=channel, bot_obj=bot_obj)
        parameter = user.user_pipe
        is_parameter_required = True
        json_data = execute_code_under_time_limit(
            lang, str(pipe_processor), easychat_bot_user, parameter, is_parameter_required)

        end_time = time.time()
        new_parameters_list = json.dumps({
            "intent_name": "none",
            "intent_pk": "none",
            "tree_name": "none",
            "tree_id": "none"
        })
        elapsed_time = end_time - start_time
        save_api_data(json_data, elapsed_time, bot_obj,
                      user.tree.pipe_processor.name, user, src, channel, new_parameters_list)

        logger.info("PipeProcessor JSON Data: %s", str(json_data), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})

        if json_data["status_code"] == "200":

            if "data" in json_data:
                is_cache = False
                if "is_cache" in json_data["data"] and json_data["data"]["is_cache"]:
                    is_cache = True
                save_data(user, json_data["data"], src,
                          channel, bot_obj.pk, is_cache=is_cache)

            return json_data["message"], json_data["recur_flag"]

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})

    return None, False


"""
function: get_api_elapsed_time
input params:
    json_api_resp: JSON API response

used to get api execution time
"""


def get_api_elapsed_time(json_api_resp, src, channel, bot_id, user_id):
    try:
        if not bool(json_api_resp):
            return {}
        return json_api_resp["elapsed_time"]
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        return {}


"""
function: save_default_parameter_for_flow
input params:
    intent_obj: Intent Object (mandatory)
    user: user identification id (mandatory)
"""


def save_default_parameter_for_flow(intent_obj, user, channel_obj, src, bot_id):
    try:
        modes = json.loads(intent_obj.tree.response.modes)
        modes_param = json.loads(intent_obj.tree.response.modes_param)
        save_data(user, {"is_feedback_required": False}, src,
                  channel_obj.name, bot_id, is_cache=True)

        save_data(user, {"is_attachment_required": False},
                  src, channel_obj.name, bot_id, is_cache=True)

        save_data(user, {"choosen_file_type": "none"}, src,
                  channel_obj.name, bot_id, is_cache=True)

        save_data(user, {"is_authentication_required": False},
                  src, channel_obj.name, bot_id, is_cache=True)

        save_data(user, {"is_user_authenticated": False}, src,
                  channel_obj.name, bot_id, is_cache=True)

        save_data(user, {"last_identified_intent_name": intent_obj.name},
                  src, channel_obj.name, bot_id, is_cache=True)

        if "is_attachment_required" in modes and str(modes["is_attachment_required"]) == "true":
            save_data(user, {"is_attachment_required": True},
                      src, channel_obj.name, bot_id, is_cache=True)
            save_data(user, {
                "choosen_file_type": modes_param["choosen_file_type"]}, src, channel_obj.name, bot_id, is_cache=True)

        if intent_obj.is_feedback_required:
            save_data(user, {"is_feedback_required": True},
                      src, channel_obj.name, bot_id, is_cache=True)

        if intent_obj.is_authentication_required:

            save_data(user, {"is_authentication_required": True},
                      src, channel_obj.name, bot_id, is_cache=True)
            is_authenticated, tree = user.is_user_authenticated(
                intent_obj, channel_obj, src, bot_id)
            if is_authenticated:
                save_data(user, {"is_user_authenticated": True},
                          src, channel_obj.name, bot_id, is_cache=True)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_default_parameter_for_flow: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_id)})


def save_file_to_server(file_base64, file_ext, EasyChatAppFileAccessManagement):
    try:
        if not os.path.exists('secured_files/EasyChatApp/attachment'):
            os.makedirs('secured_files/EasyChatApp/attachment')
        file_name = str(uuid.uuid4())
        file_attachment = open(
            "secured_files/EasyChatApp/attachment/" + file_name + "." + file_ext, "wb")
        file_attachment.write(base64.b64decode(file_base64))
        file_attachment.close()

        path = "/secured_files/EasyChatApp/attachment/" + file_name + "." + file_ext
        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_public=False, is_customer_attachment=True)

        file_url = '/chat/download-file/' + \
            str(file_access_management_obj.key) + '/' + file_name

        return file_url, file_access_management_obj.key
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_default_parameter_for_flow: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
        return None


def save_recorded_video(file_base64):
    try:
        if not os.path.exists("files/attachment/"):
            os.makedirs("files/attachment/")
        video_data_url = file_base64
        video_name = str(uuid.uuid4()) + ".mp4"
        format, videostr = video_data_url.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(videostr), name='temp.' + ext)
        video_path = default_storage.save("attachment/" + video_name, data)
        return "/files/" + video_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_default_parameter_for_flow: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
        return None


################################# Execute query mini functions start #####


"""
function: is_campaign_link_enabled
output:
    if is_campaign_link_enabled, return that message else user message
"""


def is_campaign_link_enabled(channel_params, message, logger_extra, Intent):
    logger.info('Executing is_campaign_link_enabled', extra=logger_extra)

    return_message = message
    try:
        if channel_params["is_campaign_link"]:
            try:
                return_message = Intent.objects.get(pk=int(message))
                return_message = return_message.name
            except Exception:
                logger.warning("Campaign Link Intent Not Found",
                               extra=logger_extra)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("Campaign Link Not Found: %s %s", str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished is_campaign_link_enabled', extra=logger_extra)
    return return_message


"""
Check whether channel from which message has been received is valid channel or not.
"""


def get_channel_obj(channel_name, Channel, logger_extra):
    logger.info('Executing get_channel_obj', extra=logger_extra)
    channel_obj = None
    try:
        channel_obj = Channel.objects.get(name=str(channel_name))
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error at identification of channel. %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished get_channel_obj', extra=logger_extra)
    
    return channel_obj


def get_bot_obj_from_data_models(user_id, bot_obj, logger_extra):
    # if bot_id data model is present then fetching bot id from thier for bot switch logic to work properly
    final_bot_obj = None
    try:
        user = Profile.objects.filter(
            user_id=user_id, bot=bot_obj).first()

        if not user:
            return None
        data_obj = Data.objects.filter(
            user=user, variable="bot_id")

        data_obj = data_obj.first()

        if data_obj:
            bot_id = json.loads(data_obj.get_value())
            bot_id = int(bot_id)
            final_bot_obj = Bot.objects.filter(
                pk=bot_id, is_deleted=False, is_uat=True).first()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error at get_bot_obj_from_data_models. %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    return final_bot_obj


"""
Check whether requested bot_id is valid or not and saves last query time.
"""


def get_bot_object_and_save_last_query_time(user_id, bot_id, bot_name, Bot, logger_extra):
    logger.info('Executing get_bot_object_and_save_last_query_time', extra=logger_extra)
    bot_obj = None
    try:
        if bot_name == 'uat':
            bot_obj = Bot.objects.get(
                pk=bot_id, is_deleted=False, is_uat=True)

            bot_obj_from_data_model = get_bot_obj_from_data_models(
                user_id, bot_obj, logger_extra)
            if bot_obj_from_data_model:
                bot_obj = bot_obj_from_data_model
                logger.info("Bot id from data model is - " + str(bot_obj.pk), extra=logger_extra)
        else:
            bot_obj = Bot.objects.filter(
                slug=bot_name, is_active=True, is_deleted=False).order_by('-pk')[0]
        bot_obj.last_query_time = datetime.datetime.now()
        bot_obj.save(update_fields=['last_query_time'])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error at identification of bot. %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished get_bot_object_and_save_last_query_time', extra=logger_extra)
    return bot_obj


"""
Translation module .
"""


"""
Chck if lead generation is enabled or no.
"""


def is_lead_generation_enabled(is_form_assist, app_config, message, user_id, src, channel, bot_id, bot_obj, logger_extra):
    logger.info('Executing is_lead_generation_enabled', extra=logger_extra)
    try:
        is_message_updated = False
        is_lead_generation = bot_obj.is_lead_generation_enabled
        if is_lead_generation == True:
            is_form_assist = False
            app_config.is_auto_correct_required = False
            app_config.save()

        if is_form_assist == False and does_it_look_english(message):
            validation_obj = EasyChatInputValidation()
            message = validation_obj.remo_html_from_string(message)
            message = process_string(message, user_id, src, channel, bot_id)
            is_message_updated = True
            if is_lead_generation == False and False:
                message = spell_checker(message, "", "", "", "")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in checking lead generation enabled. %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished is_lead_generation_enabled', extra=logger_extra)
    return is_message_updated, is_form_assist, message


"""
Save user details in the middle of the flow.
"""


def save_user_flow_details(user, channel_obj, logger_extra):
    logger.info('Executing save_user_flow_details', extra=logger_extra)
    user_obj = user
    try:
        user_obj.channel = channel_obj
        user_obj.previous_message_date = user_obj.last_message_date
        user_obj.last_message_date = timezone.now()
        user_obj.save(update_fields=['channel', 'previous_message_date', 'last_message_date'])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in saving user flow details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished save_user_flow_details', extra=logger_extra)
    return user_obj


"""
Getting previous bot id to which user has interacted.
"""


def get_previous_bot_id(user, bot_id, channel, logger_extra, Data):
    logger.info('Executing get_previous_bot_id', extra=logger_extra)
    user_obj = user
    try:
        data_obj = Data.objects.filter(user=user_obj, variable="bot_id")
        if data_obj and channel == "WhatsApp":
            if str(data_obj[0].get_value()).replace('"', "") != str(bot_id):
                user_obj.tree = None
                user_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in getting previous bot id. %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished get_previous_bot_id', extra=logger_extra)
    return user_obj


"""
Update TIME SPENT BY USER
"""


def save_and_update_time_spent_user(user_id, easychat_bot_user, logger_extra, TimeSpentByUser, bot_web_page, web_page_source):
    bot_obj = easychat_bot_user.bot_obj
    logger.info('Executing save_and_update_time_spent_user', extra=logger_extra)
    try:
        time_obj = TimeSpentByUser.objects.filter(
            user_id=user_id, bot=bot_obj)

        if time_obj:
            is_new_obj_required = False
            if time_obj[0].end_datetime.date() < timezone.now().date() and easychat_bot_user.channel_name != "WhatsApp":
                is_new_obj_required = True

        if time_obj and not is_new_obj_required:
            time_obj[0].end_datetime = timezone.now()
            time_obj[0].total_time_spent = time_obj[0].time_diff()
            time_obj[0].save(update_fields=['end_datetime', 'total_time_spent'])
        else:
            TimeSpentByUser.objects.create(
                user_id=user_id, bot=bot_obj, web_page=bot_web_page, web_page_source=web_page_source)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in save and update time spent by user. %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished save_and_update_time_spent_user', extra=logger_extra)


"""
Whatsapp nps update module
"""


def whatsapp_nps_update(user, message, bot_obj, logger_extra, Feedback):
    logger.info('Executing whatsapp_nps_update', extra=logger_extra)
    try:
        user_obj = user
        is_whatsapp_nps_rating = False
        is_whatsapp_nps_comment = False
        whatsapp_rating = 0
        if user_obj.channel.name == "WhatsApp":
            if user_obj.is_nps_message_send:
                if message.isdigit():
                    if(int(message) >= 0 and int(message) < 11):
                        Feedback.objects.create(
                            user_id=user.user_id, bot=bot_obj, rating=message, comments="", session_id=user.user_id, channel=user_obj.channel, scale_rating_5=bot_obj.scale_rating_5)
                        is_whatsapp_nps_rating = True
                        whatsapp_rating = int(message)
                        if whatsapp_rating >= 0 and whatsapp_rating <= 8:
                            user_obj.is_comment_needed = True
                            user_obj.save()
                else:
                    if user_obj.is_comment_needed:
                        previous_message_date_time = user_obj.previous_message_date
                        time_diff = timezone.now() - previous_message_date_time
                        time_minutes = time_diff.seconds / 60
                        if int(time_minutes) <= 2:
                            feedback_obj = Feedback.objects.filter(
                                user_id=user.user_id, bot=bot_obj)
                            if feedback_obj:
                                if message.lower() != 'skip':
                                    feedback_obj[0].comments = message
                                    feedback_obj[0].save()
                                is_whatsapp_nps_comment = True
                    user_obj.is_nps_message_send = False
                    user_obj.is_comment_needed = False
                    user_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in whatsapp nps update %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished whatsapp_nps_update', extra=logger_extra)
    return user_obj, message, is_whatsapp_nps_rating, is_whatsapp_nps_comment, whatsapp_rating


"""
If sticky message enabled, user tree = None
"""


def is_sticky_message_enabled(user, channel_params, logger_extra):
    logger.info('Executing is_sticky_message_enabled', extra=logger_extra)
    try:
        user_obj = user
        is_sticky_message_called_in_flow = False
        previous_parent_tree = None
        if "is_sticky_message" in channel_params and channel_params["is_sticky_message"] == True:
            if user_obj.tree is not None:
                is_sticky_message_called_in_flow = True
                previous_parent_tree = user_obj.tree
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in is sticky message enabled. %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished is_sticky_message_enabled', extra=logger_extra)
    return user_obj, is_sticky_message_called_in_flow, previous_parent_tree


"""
Return autocorrected response
"""


def return_autocorrect_response(app_config, user, user_message, logger_extra, bot_id, src, channel):
    logger.info('Executing return_autocorrect_response', extra=logger_extra)
    message = user_message
    if app_config.is_auto_correct_required:
        user_message = user_message.lower()
        if(len(user.user_pipe.split("|")) > 2):
            if(user.user_pipe.split("|")[-3].lower() != user_message):
                message = correct_query(
                    user_message, user.user_id, src, channel, bot_id)
        else:
            message = correct_query(
                user_message, user.user_id, src, channel, bot_id)
    logger.info('Finished return_autocorrect_response', extra=logger_extra)
    return message


"""
Return tree directly if suggestion is clicked
"""


def return_user_tree_based_suggestion(easychat_params: EasyChatChannelParams, easychat_bot_user: EasyChatBotUser, user, tree, message):
    src = easychat_bot_user.src
    channel_of_message = easychat_bot_user.channel_name
    is_manually_typed_query = easychat_params.is_manually_typed_query
    bot_id = easychat_bot_user.bot_id
    logger.info('Executing return_user_tree_based_suggestion', extra=easychat_bot_user.extra)
    try:
        start_intent_msg = ""
        to_check_abort_flow_message = False
        if easychat_params.entered_suggestion:
            try:
                bot_obj = easychat_bot_user.bot_obj
                channel_obj = easychat_params.channel_obj
                if easychat_bot_user and easychat_bot_user.category_obj:
                    category_obj = easychat_bot_user.category_obj
                else:
                    category_obj = get_category_obj(bot_obj, easychat_bot_user.category_name)
                    easychat_bot_user.category_obj = category_obj

                intent_obj = Intent.objects.filter(
                    pk=int(message), channels=channel_obj, is_deleted=False)
                if category_obj and intent_obj.exists():
                    message = intent_obj.first().name
                    intent_obj = intent_obj.filter(Q(category=category_obj) | Q(category__isnull=True))
                
                if intent_obj.exists():
                    intent_obj = intent_obj.first()
                else:
                    return user, start_intent_msg, tree, message, to_check_abort_flow_message, is_manually_typed_query

                if intent_obj and easychat_params.is_sticky_message_called_in_flow:
                    to_check_abort_flow_message = True
                
                message = intent_obj.name

                # If user in the middle of some flow, skipping this check
                if user.tree != None:
                    easychat_bot_user.original_message = message
                    return user, "", tree, message, False, is_manually_typed_query

                # Original tree is the tree of the intent in which authentication is enabled
                # Because if authentication is enabled in an intent 'tree' is set to the tree of authentication intent
                easychat_bot_user.original_tree = intent_obj.tree
                tree = check_if_authentication_reqd(
                    intent_obj, bot_obj, user, channel_of_message, channel_obj, src)

                is_manually_typed_query = False
                save_data(user, {"last_identified_intent_name":
                                 intent_obj.name}, src, channel_of_message, bot_id, is_cache=True)

                save_data(user, {"LanguageSourceUser": str(src)},
                          src, channel_of_message, bot_id, is_cache=True)

                if intent_obj.is_feedback_required:
                    save_data(user, {
                        "is_feedback_required": True}, src, channel_of_message, bot_id, is_cache=True)

                user.tree = tree
                user.save(update_fields=['tree'])
            except Exception:
                tree = None
        if tree == None:
            start_intent_msg = ""
            if user.tree == None:
                start_intent_msg = message
        logger.info('Into return_next_tree...', extra=easychat_bot_user.extra)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in return_user_tree_based_suggestion %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    logger.info('Finished return_user_tree_based_suggestion', extra=easychat_bot_user.extra)
    return user, start_intent_msg, tree, message, to_check_abort_flow_message, is_manually_typed_query


"""
Return tree directly if Intent hash macthes exactly
"""


def return_user_tree_based_on_intent_hash(user, tree, message, easychat_bot_user, easychat_params):
    channel_of_message = easychat_bot_user.channel_name
    bot_obj = easychat_bot_user.bot_obj
    channel_obj = easychat_params.channel_obj
    src = easychat_bot_user.src
    training_question = ""
    logger.info('Executing return_user_tree_based_on_intent_hash', extra=easychat_bot_user.extra)
    try:
        # If user in the middle of some flow, skipping this check
        if user.tree != None:
            return user, "", tree, message, training_question

        # Else check
        start_intent_msg = ""
        bot_id = bot_obj.id
        try:
            stem_words = get_stem_words_of_sentence(
                message, src, channel_of_message, user.user_id, bot_obj)
            stem_words.sort()
            temp_sentence = ' '.join(stem_words)
            stem_word_hash_value = hashlib.md5(
                temp_sentence.encode()).hexdigest()

            hash_objs = IntentTreeHash.objects.select_related('tree').filter(hash_value=stem_word_hash_value)
            hash_tree_pks = hash_objs.values_list("tree", flat=True)
            if easychat_bot_user and easychat_bot_user.category_obj:
                category_obj = easychat_bot_user.category_obj
            else:
                category_obj = get_category_obj(bot_obj, easychat_bot_user.category_name)
                easychat_bot_user.category_obj = category_obj

            intent_obj = Intent.objects.filter(tree__pk__in=hash_tree_pks, bots__in=[bot_obj], is_deleted=False, is_hidden=False, channels__in=[channel_obj])
            
            if intent_obj and category_obj:
                intent_obj = intent_obj.filter(Q(category=category_obj) | Q(category__isnull=True))
            
            if intent_obj.count() == 1:
                intent_obj = intent_obj.first()
                training_question = hash_objs.filter(tree=intent_obj.tree).first().training_question

                easychat_bot_user.original_tree = intent_obj.tree
                tree = check_if_authentication_reqd(
                    intent_obj, bot_obj, user, channel_of_message, channel_obj, src)

                save_data(user, {"last_identified_intent_name":
                                 intent_obj.name}, src, channel_of_message, bot_id, is_cache=True)

                save_data(user, {"LanguageSourceUser": str(src)},
                          src, channel_of_message, bot_obj.pk, is_cache=True)

                if intent_obj.is_feedback_required:
                    save_data(user, {
                        "is_feedback_required": True}, src, channel_of_message, bot_obj.pk, is_cache=True)
                else:
                    save_data(user, {"is_feedback_required": False}, src,
                              channel_of_message, bot_obj.pk, is_cache=True)

                user.tree = tree
                user.save(update_fields=['tree'])
            else:
                tree = None

        except Exception:
            tree = None
        if tree == None:
            start_intent_msg = ""
            if user.tree == None:
                start_intent_msg = message
        logger.info('Into return_user_tree_based_on_intent_hash...', extra=easychat_bot_user.extra)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in return_user_tree_based_on_intent_hash %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    logger.info('Finished return_user_tree_based_on_intent_hash', extra=easychat_bot_user.extra)
    return user, start_intent_msg, tree, message, training_question


def return_intent_object_based_on_suggested_query_hash(user, bot_obj, message, channel_of_message, src):
    intent_obj = None
    word_mapped_message = ""
    stem_words = []
    try:
        word_mapped_message, stem_words = get_list_of_stem_words_after_spell_correction_from_message(
            user, bot_obj, message, channel_of_message, src)

        stem_words.sort()
        stem_words_name = ' '.join(stem_words)
        query_hash = hashlib.md5(stem_words_name.encode()).hexdigest()
        suggested_query_hash_obj = SuggestedQueryHash.objects.filter(
            query_hash=query_hash, bot=bot_obj)
        if suggested_query_hash_obj.exists():
            suggested_query_info_objs = SuggestedQueryInfo.objects.filter(
                hash_info=suggested_query_hash_obj[0])

            suggested_query_info_objs = suggested_query_info_objs.order_by(
                "-count")

            if suggested_query_info_objs.exists():
                suggested_query_info_obj = suggested_query_info_objs[0]

                if suggested_query_info_obj.is_threshold_crossed(bot_obj):
                    intent_obj = suggested_query_info_obj.intent_selected
                    if bot_obj in intent_obj.bots.all() and (not intent_obj.is_deleted):
                        return intent_obj, word_mapped_message, stem_words
                    else:
                        return None, word_mapped_message, stem_words
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("return_intent_object_based_on_suggested_query_hash error:" +
                     str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})

    return intent_obj, word_mapped_message, stem_words


def return_user_tree_based_on_suggested_query_hash(user, tree, message, easychat_bot_user, easychat_params):

    bot_obj = easychat_bot_user.bot_obj
    src = easychat_bot_user.src
    channel_of_message = easychat_bot_user.channel_name
    channel_obj = easychat_params.channel_obj
    logger.info('Executing return_user_tree_based_on_suggested_query_hash', extra=easychat_bot_user.extra)
    if easychat_bot_user and easychat_bot_user.category_obj:
        category_obj = easychat_bot_user.category_obj
    else:
        category_obj = get_category_obj(bot_obj, easychat_bot_user.category_name)
        easychat_bot_user.category_obj = category_obj
    word_mapped_message = ""
    stem_words = []
    try:
        
        bot_info_obj = easychat_bot_user.bot_info_obj

        if not bot_info_obj:
            return user, "", tree, message, word_mapped_message, stem_words

        if not bot_info_obj.is_suggested_intent_learning_on:
            return user, "", tree, message, word_mapped_message, stem_words

        # If user in the middle of some flow, skipping this check
        if user.tree != None:
            return user, "", tree, message, word_mapped_message, stem_words

        # Else check
        start_intent_msg = ""
        bot_id = bot_obj.id
        try:

            intent_obj, word_mapped_message, stem_words = return_intent_object_based_on_suggested_query_hash(
                user, bot_obj, message, channel_of_message, src)
            
            if category_obj and intent_obj:
                if intent_obj.category != category_obj and intent_obj.category != None:
                    intent_obj = None

            if intent_obj:
                easychat_bot_user.original_tree = intent_obj.tree
                tree = check_if_authentication_reqd(
                    intent_obj, bot_obj, user, channel_of_message, channel_obj, src)

                save_data(user, {"last_identified_intent_name":
                                 intent_obj.name}, src, channel_of_message, bot_id, is_cache=True)

                save_data(user, {"LanguageSourceUser": str(src)},
                          src, channel_of_message, bot_obj.pk, is_cache=True)

                if intent_obj.is_feedback_required:
                    save_data(user, {
                        "is_feedback_required": True}, src, channel_of_message, bot_obj.pk, is_cache=True)
                else:
                    save_data(user, {"is_feedback_required": False}, src,
                              channel_of_message, bot_obj.pk, is_cache=True)

                user.tree = tree
                user.save(update_fields=['tree'])
            else:
                tree = None

        except Exception:
            tree = None
        if tree == None:
            start_intent_msg = ""
            if user.tree == None:
                start_intent_msg = message

        logger.info('Into return_user_tree_based_on_suggested_query_hash ...', extra=easychat_bot_user.extra)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in return_user_tree_based_on_suggested_query_hash %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    logger.info('Finished return_user_tree_based_on_suggested_query_hash', extra=easychat_bot_user.extra)
    return user, start_intent_msg, tree, message, word_mapped_message, stem_words


"""
If go back enabled return tree, else return next tree
"""


def return_next_tree_based_is_go_back_enabled(easychat_params, message, original_message, user, easychat_bot_user, word_mapped_message, stem_words):
    training_question = ""
    match_percentage = ""
    tree = None
    status_re_sentence = False
    suggestion_list = []
    extra_params = {}
    logger_extra = easychat_bot_user.extra
    
    bot_obj = easychat_bot_user.bot_obj
    logger.info('Executing return_next_tree_based_is_go_back_enabled', extra=logger_extra)
    try:
        if easychat_params.is_intent_tree and user.tree != None:
            tree_obj = user.tree

            intent_name = get_intent_name(
                tree_obj, easychat_bot_user.src, easychat_bot_user.channel_name, bot_obj.pk, user.user_id)
            intent_obj = Intent.objects.filter(name=intent_name, bots__in=[bot_obj], is_deleted=False).first()

            if intent_obj and intent_obj.is_category_response_allowed:
                data_obj = Data.objects.filter(
                    user=user, variable="category_name").first()
                if data_obj:
                    category_name = str(data_obj.get_value()).lower()
                    category_name = category_name.replace("\"", "")
                    next_tree_obj = intent_obj.tree
                    next_tree_obj = next_tree_obj.children.filter(
                        name__icontains=str(category_name), is_deleted=False).first()
                    if next_tree_obj:
                        easychat_bot_user.is_recur_flag = True
                        easychat_bot_user.parent_tree = intent_obj.tree
                        tree_obj = next_tree_obj

            user.tree = tree_obj
            user.save(update_fields=['tree'])
            return user, tree_obj, status_re_sentence, [], None, training_question, match_percentage, extra_params

        if easychat_params.channel_obj.name == "Voice" and check_if_repeat_event_detected(message, easychat_bot_user.bot_info_obj):
            return user, user.tree, status_re_sentence, [], None, training_question, match_percentage, extra_params

        intent_obj_category_based = None
        user_obj = user

        if user.tree != None and user.tree.is_go_back_enabled and message.strip().lower() == "go back" and user.tree.children.filter(is_deleted=False) and not Intent.objects.filter(tree=user.tree):
            last_tree_pk = Data.objects.filter(
                user=user_obj, variable="last_tree_pk")
            if last_tree_pk.count():
                tree = Tree.objects.get(
                    pk=int(last_tree_pk[0].get_value().replace('"', '')))
                status_re_sentence = False
                suggestion_list = []
            else:
                tree, status_re_sentence, suggestion_list, intent_obj_category_based, training_question, match_percentage, extra_params = return_next_tree(
                    message, user, easychat_bot_user, easychat_params, word_mapped_message, stem_words)
        else:
            tree, status_re_sentence, suggestion_list, intent_obj_category_based, training_question, match_percentage, extra_params = return_next_tree(
                message, user, easychat_bot_user, easychat_params, word_mapped_message, stem_words)
            logger.info('Exit from return next tree', extra=logger_extra)
        user_obj.tree = tree
        user_obj.save(update_fields=['tree'])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in return_next_tree_based_is_go_back_enabled %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    logger.info('Finished return_next_tree_based_is_go_back_enabled', extra=logger_extra)
    return user, tree, status_re_sentence, suggestion_list, None, training_question, match_percentage, extra_params


def update_initial_intent_flow_analytics_data(user, data):
    try:
        initial_intent_flow_analytics_data_obj = Data.objects.filter(user=user, variable="initial_intent_flow_analytics_data").first()
        if not initial_intent_flow_analytics_data_obj:
            initial_intent_flow_analytics_data_obj = Data.objects.create(user=user, variable="initial_intent_flow_analytics_data", value=json.dumps([]))

        initial_intent_flow_analytics_data = json.loads(initial_intent_flow_analytics_data_obj.get_value())
        initial_intent_flow_analytics_data.append(data)
        initial_intent_flow_analytics_data_obj.value = json.dumps(initial_intent_flow_analytics_data)
        initial_intent_flow_analytics_data_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in update_initial_intent_flow_analytics_data %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

"""
Save Flow analytics if pipe processor is none
"""


def save_flow_analytics_data_pipe_processor(message, tree, bot_obj, user, src, channel_obj, bot_id, FlowAnalytics, Data, Tree, logger_extra, easychat_params):
    logger.info('Executing save_flow_analytics_data_pipe_processor', extra=logger_extra)
    try:
        intent_objs = Intent.objects.filter(
            tree=tree, bots__in=[bot_obj])
        if intent_objs.count() == 0:
            flow_analytics_obj = FlowAnalytics.objects.filter(
                user=user).last()
            intent_indentifed = flow_analytics_obj.intent_indentifed
            last_level_tree_pk = Data.objects.filter(
                user=user, variable="last_level_tree_pk")
            if last_level_tree_pk.count():
                parent_tree = Tree.objects.filter(
                    pk=last_level_tree_pk[0].get_value().replace('"', ''))[0]
                save_data(user, {"last_tree_pk": last_level_tree_pk[0].get_value().replace(
                    '"', '')}, src, channel_obj.name, bot_id, is_cache=True)
                save_data(user, {"last_level_tree_pk": tree.pk},
                          src, channel_obj.name, bot_id, is_cache=True)
            else:

                save_data(user, {"last_level_tree_pk": tree.pk},
                          src, channel_obj.name, bot_id, is_cache=True)
                parent_tree = Tree.objects.filter(children__pk=tree.pk)[0]

            if easychat_params.is_initial_intent:
                update_initial_intent_flow_analytics_data(user, {
                    "user_id": user.pk,
                    "previous_tree_id": parent_tree.pk,
                    "current_tree_id": tree.pk,
                    "intent_indentifed_id": intent_indentifed.pk,
                    "user_message": message,
                })
                return

            FlowAnalytics.objects.create(
                user=user, previous_tree=parent_tree, current_tree=tree, intent_indentifed=intent_indentifed, user_message=message)
        else:
            intent_indentifed = intent_objs[0]
            last_level_tree_pk = Data.objects.filter(
                user=user, variable="last_level_tree_pk")
            save_data(user, {"last_level_tree_pk": tree.pk},
                      src, channel_obj.name, bot_id, is_cache=True)

            if easychat_params.is_initial_intent:
                update_initial_intent_flow_analytics_data(user, {
                    "user_id": user.pk,
                    "previous_tree_id": tree.pk,
                    "current_tree_id": tree.pk,
                    "intent_indentifed_id": intent_indentifed.pk,
                    "user_message": message,
                })
                return

            FlowAnalytics.objects.create(user=user, previous_tree=tree, current_tree=tree,
                                         intent_indentifed=intent_indentifed, user_message=message)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in saving flow analytics for pipe %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished save_flow_analytics_data_pipe_processor', extra=logger_extra)


"""
Save Flow analytics if pipe processor is not none
"""


def save_flow_analytics_data_pipe_processor_none(user, message, tree, bot_obj, src, channel_obj, Intent, Data, FlowAnalytics, logger_extra, easychat_params):

    logger.info('Executing save_flow_analytics_data_pipe_processor_none', extra=logger_extra)
    try:
        intent_objs = Intent.objects.filter(
            tree=tree, bots__in=[bot_obj])
        if intent_objs.count() == 0:
            is_intent_tree = False
        else:
            is_intent_tree = True

        last_level_tree_pk = Data.objects.filter(
            user=user, variable="last_level_tree_pk")
        if last_level_tree_pk.count():
            last_level_tree_pk = int(
                last_level_tree_pk[0].get_value().replace('"', ''))
            parent_tree = Tree.objects.filter(
                pk=last_level_tree_pk)[0]
            # if last level tree pk is same as current pk then it should not
            # update variable last_tree_pk
            save_data(user, {"last_level_tree_pk": tree.pk},
                      src, channel_obj.name, bot_obj.pk, is_cache=True)
            if last_level_tree_pk != tree.pk:
                save_data(user, {"last_tree_pk": last_level_tree_pk},
                          src, channel_obj.name, bot_obj.pk, is_cache=True)
    
        else:
            save_data(user, {"last_level_tree_pk": tree.pk},
                      src, channel_obj.name, bot_obj.pk, is_cache=True)
            parent_tree = Tree.objects.filter(children__pk=tree.pk)

            if not parent_tree.exists():
                if easychat_params.is_initial_intent:
                    update_initial_intent_flow_analytics_data(user, {
                        "user_id": user.pk,
                        "previous_tree_id": intent_objs[0].tree.pk,
                        "current_tree_id": intent_objs[0].tree.pk,
                        "intent_indentifed_id": intent_objs[0].pk,
                        "user_message": message,
                    })
                    return
                flow_analytics_obj = FlowAnalytics.objects.create(user=user, previous_tree=intent_objs[
                    0].tree, current_tree=intent_objs[0].tree, intent_indentifed=intent_objs[0], user_message=message)
                return
            parent_tree = parent_tree.first()

        try:
            if easychat_params.is_initial_intent:
                if is_intent_tree == True:
                    intent_indentifed = intent_objs[0].pk
                else:
                    initial_intent_flow_analytics_data_obj = Data.objects.filter(user=user, variable="initial_intent_flow_analytics_data").first()
                    intent_indentifed = json.loads(initial_intent_flow_analytics_data_obj.get_value())[0]["intent_indentifed_id"]
            else:
                flow_analytics_obj = FlowAnalytics.objects.filter(
                    user=user).last()
                if is_intent_tree == True:
                    intent_indentifed = intent_objs[0]
                else:
                    intent_indentifed = flow_analytics_obj.intent_indentifed

            if parent_tree.flow_analytics_variable != "":
                flow_analytics_variable = Data.objects.filter(
                    user=user, variable=parent_tree.flow_analytics_variable).first()
                if flow_analytics_variable:
                    flow_analytics_variable = flow_analytics_variable.get_value()
                    if isinstance(flow_analytics_variable, str):
                        flow_analytics_variable = int(
                            flow_analytics_variable.replace('"', "").replace("'", ""))

                # checks parent tree is an intent
                    if easychat_params.is_initial_intent:
                        update_initial_intent_flow_analytics_data(user, {
                            "user_id": user.pk,
                            "previous_tree_id": parent_tree.pk,
                            "current_tree_id": tree.pk,
                            "intent_indentifed_id": intent_indentifed,
                            "flow_analytics_variable": flow_analytics_variable,
                            "user_message": message,
                        })
                        return
                    FlowAnalytics.objects.create(user=user, previous_tree=parent_tree, current_tree=tree,
                                                    intent_indentifed=intent_indentifed, user_message=message, flow_analytics_variable=flow_analytics_variable)
            else:
                if easychat_params.is_initial_intent:
                    update_initial_intent_flow_analytics_data(user, {
                        "user_id": user.pk,
                        "previous_tree_id": parent_tree.pk,
                        "current_tree_id": tree.pk,
                        "intent_indentifed_id": intent_indentifed,
                        "user_message": message,
                    })
                    return
                FlowAnalytics.objects.create(user=user, previous_tree=parent_tree, current_tree=tree,
                                             intent_indentifed=intent_indentifed, user_message=message)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error in save_flow_analytics_data_pipe_processor_none-I %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=logger_extra)

            if easychat_params.is_initial_intent:
                update_initial_intent_flow_analytics_data(user, {
                    "user_id": user.pk,
                    "previous_tree_id": intent_objs[0].tree.pk,
                    "current_tree_id": intent_objs[0].tree.pk,
                    "intent_indentifed_id": intent_objs[0].pk,
                    "user_message": message,
                })
                return

            flow_analytics_obj = FlowAnalytics.objects.create(
                user=user, previous_tree=intent_objs[0].tree, current_tree=intent_objs[0].tree, intent_indentifed=intent_objs[0], user_message=message)
            pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in save_flow_analytics_data_pipe_processor_none-II %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)

        if easychat_params.is_initial_intent:
            update_initial_intent_flow_analytics_data(user, {
                "user_id": user.pk,
                "previous_tree_id": intent_objs[0].tree.pk,
                "current_tree_id": intent_objs[0].tree.pk,
                "intent_indentifed_id": intent_objs[0].pk,
                "user_message": message,
            })
            return

        flow_analytics_obj = FlowAnalytics.objects.create(user=user, previous_tree=intent_objs[
                                                          0].tree, current_tree=intent_objs[0].tree, intent_indentifed=intent_objs[0], user_message=message)
        pass
    logger.info('Finished save_flow_analytics_data_pipe_processor_none', extra=logger_extra)


"""
Return all the widgets based on modes and modes params
"""


def return_widgets(modes, modes_param, easychat_bot_user, logger_extra):

    logger.info('Executing return_widgets', extra=logger_extra)
    try:
        widgets = []
        if "is_radio_button" in modes and modes["is_radio_button"] == "true":
            widgets = modes_param["radio_button_choices"]

        if "is_check_box" in modes and modes["is_check_box"] == "true":
            widgets = modes_param["check_box_choices"]

        if "is_drop_down" in modes and modes["is_drop_down"] == "true":
            widgets = modes_param["drop_down_choices"]

        if "is_create_form_allowed" in modes and modes["is_create_form_allowed"] == "true":
            form_name = {'form': modes_param["form_name"]}
            widgets.append(form_name)
            form_fields_list = json.loads(modes_param["form_fields_list"])
            for form_field in form_fields_list:
                if form_field['is_dependent'] == 'false':
                    field_processor_obj = FormWidgetFieldProcessor.objects.filter(
                        field_id=form_field['field_id_num'])
                    if field_processor_obj.exists():
                        field_processor_obj = field_processor_obj.first()
                        api_caller = replace_data_values(easychat_bot_user, field_processor_obj.function,
                                                         easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_id)
                        output = execute_code_under_time_limit(
                            field_processor_obj.processor_lang, api_caller, easychat_bot_user.bot_obj, None, True)
                        if form_field['input_type'] == 'checkbox' or form_field['input_type'] == 'radio' or form_field['input_type'] == 'dropdown_list':
                            form_field['placeholder_or_options'] = '$$$'.join(
                                output['options'])
                        if form_field['input_type'] == 'text_field':
                            form_field['text_field_value'] = output['text_field_value']
                        if form_field['input_type'] == 'range':
                            form_field['placeholder_or_options'] = output['range_slider_min_value'] + \
                                '-' + output['range_slider_max_value']
                        if form_field['input_type'] == 'phone_number':
                            form_field['phone_widget_data'] = output['phone_widget_data']

            modes_param["form_fields_list"] = json.dumps(form_fields_list)
            widgets.append(modes_param["form_fields_list"])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in return_widgets %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    logger.info('Finished return_widgets', extra=logger_extra)
    return widgets


def is_session_id_valid(session_id, logger_extra, EasyChatSessionIDGenerator):
    try:
        session_obj = EasyChatSessionIDGenerator.objects.get(token=session_id)
        if session_obj:
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Invalid session id %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
        pass

    return False

################################# Execute query mini functions end #######


def create_intuitive_messages(message, easychat_bot_user, suggestion_list=[]):
    try:
        bot_obj = easychat_bot_user.bot_obj
        channel_name = easychat_bot_user.channel_name
        selected_language = easychat_bot_user.selected_language

        import datetime

        msg_rcvd = message.lower().strip()
        msg_rcvd_hash = hashlib.md5(
            msg_rcvd.encode()).hexdigest()

        intuitive_query = IntuitiveQuestions.objects.filter(
            intuitive_message_query_hash=msg_rcvd_hash, date=datetime.datetime.now().date(), channel=channel_name, bot=bot_obj, selected_language=selected_language).first()

        if intuitive_query:
            intuitive_query.count = intuitive_query.count + 1
            intuitive_query.save(update_fields=['count'])

        else:
            intuitive_query = IntuitiveQuestions.objects.create(
                intuitive_message_query_hash=msg_rcvd_hash, intuitive_message_query=msg_rcvd, count=1, channel=channel_name, bot=bot_obj, selected_language=selected_language)

        intuitive_query.suggested_intents.clear()
        for suggestion in suggestion_list:
            intent_obj = Intent.objects.get(pk=str(suggestion["id"]))
            intuitive_query.suggested_intents.add(intent_obj)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("IntuitiveQuestions %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': '', 'channel': '', 'bot_id': 'None'})
        return []


"""
function: get_intent_category_name
input params:
    tree: active user tree
output
    category_name

returns category name as "" for inflow tree and
name of intent category in case of root tree
"""


def get_intent_category_name(tree, src, channel, bot_id, user):

    category_name = ""
    try:
        if tree is not None:
            bot_obj = Bot.objects.get(pk=bot_id)
            category_name = "Others"
            intent_name = get_last_identified_intent_name(
                user, src, channel, bot_id)
            intent_obj = Intent.objects.filter(
                name__iexact=intent_name, is_deleted=False, bots__in=[bot_obj])
            if intent_obj:
                intent_obj = intent_obj.first()
                if intent_obj.category:
                    category_name = intent_obj.category.name
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    return category_name


"""
function: replace_data_values
input params:
    user: active user object
    sentence: string which contains some functions
output:
    return string after replacement of unknown variables.

eg. This is example of {/api_variable/} replacement. -> This is example of variable_value replacement.
"""


def replace_data_values(user, sentence, src, channel, bot_id, translation_req=False):
    logger.info("Into replace_data_values...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    try:
        left_split_list = sentence.split("{/")
        for left_split in left_split_list:

            if "/}" in left_split:

                data_variable = left_split.split("/}")[0].strip()
                value = "None"

                data_objs = Data.objects.filter(
                    user=user, variable=data_variable).order_by('-pk')

                tagmapper_objs = TagMapper.objects.filter(
                    alias_variable=str(data_variable)).order_by('-pk')

                if len(data_objs) > 0:
                    logger.info("%s is available in data model.", data_variable, extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
                    value = json.loads(data_objs[0].get_value())
                    value = get_translated_text(
                        value, src, EasyChatTranslationCache) if translation_req else value
                elif len(tagmapper_objs) > 0:
                    logger.info("%s is tagmapper. Call API. ", data_variable, extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

                    api_tree = tagmapper_objs[0].api_tree

                    api_cache_variable = "API_TREE_CASHE_" + \
                        str(api_tree.name).replace(" ", "").upper()

                    try:
                        api_caller = replace_data_values(
                            user, api_tree.api_caller, src, channel, bot_id)

                        api_response = execute_api(user,
                                                   api_caller,
                                                   api_tree.is_cache,
                                                   api_cache_variable,
                                                   src,
                                                   channel,
                                                   bot_id,
                                                   api_tree.processor_lang)

                        value = str(api_response[str(data_variable)])
                        save_data(user, api_response)
                    except Exception as e:  # noqa: F841
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("[ENGINE]: %s at %s", str(e),
                                     str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
                else:
                    logger.info("%s is not available in data model.", data_variable, extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

                data_variable = "{/" + data_variable + "/}"
                try:
                    if not isinstance(value, dict) and not isinstance(value, list):
                        value = value.encode("utf8", errors="ignore")
                        value = value.strip()
                    else:
                        value = str(value)
                except Exception:
                    value = str(value)

                if isinstance(value, bytes):
                    sentence = sentence.replace(
                        data_variable, value.decode("utf-8"))
                else:
                    sentence = sentence.replace(data_variable, value)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    logger.info("Exit from replace_data_values...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return sentence


"""
function: save_data
input_params:
    user: active user object (mandatory)
    json_data: input json data which is to be stored in data model. eg. {"name":"nimesh","phone":"1234567890"} (mandatory)
    is_cached: Whether given data to be stored permanently or not. default value is False (optional)
"""


def save_data(user, json_data, src, channel, bot_id, is_cache=False):
    try:
        for key in json_data:
            data_obj = None
            try:
                if key == "data":
                    data = json_data[key]
                    if not isinstance(data, dict):
                        data = json.loads(data)
                    save_data(user, data, src, channel, bot_id, is_cache)
                    continue
            except Exception:
                pass

            try:
                # Already exists
                data_obj = Data.objects.get(user=user, variable=key)
                data_obj.value = json.dumps(json_data[key])
                data_obj.is_cache = is_cache
                data_obj.save()
            except Exception:  # noqa: F841
                bot_obj = None
                if bot_id:
                    bot_obj = Bot.objects.get(pk=int(bot_id))
                # Data objects doesn't exists, so create new object.
                data_obj = Data.objects.create(user=user,
                                               bot=bot_obj,
                                               variable=key,
                                               value=json.dumps(
                                                   json_data[key]),
                                               is_cache=is_cache)
            # bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
            
            # if bot_obj and bot_obj.masking_enabled and key != "attached_file_src":
            #     custom_encrypt_obj = CustomEncrypt()
            #     value = custom_encrypt_obj.encrypt(json.dumps(json_data[key]))
            # # Already exists
            # data_obj = Data.objects.filter(user=user, variable=key, bot=bot_obj).update(value=value, is_cache=is_cache)
            # if not data_obj:
            # # Data objects doesn't exists, so create new object.
            #     Data.objects.create(user=user,
            #                         bot=bot_obj,
            #                         variable=key,
            #                         value=json.dumps(
            #                         json_data[key]),
            #                         is_cache=is_cache)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})


def get_multilingual_intent_name(intent_obj, src):
    try:
        language_obj = Language.objects.get(lang=src)
        return LanguageTuningIntentTable.objects.filter(intent=intent_obj, language=language_obj).first().multilingual_name
    except Exception:
        return str(intent_obj.name).capitalize()


def check_and_update_count_for_suggested_queries(user, bot_obj, tree, channel, src):
    try:
        if tree == None:
            return

        bot_info_obj = get_bot_info_object(bot_obj)
        if not bot_info_obj:
            return

        if not bot_info_obj.is_suggested_intent_learning_on:
            return

        last_suggested_query_hash_obj_pk = Data.objects.filter(
            user=user, variable="last_suggested_query_hash_obj_pk")

        if not last_suggested_query_hash_obj_pk.exists():
            return

        if not last_suggested_query_hash_obj_pk[0].get_value().replace('"', '').isdigit():
            return

        hash_obj = SuggestedQueryHash.objects.filter(
            pk=int(last_suggested_query_hash_obj_pk[0].get_value().replace('"', '')))
        if not hash_obj.exists():
            return

        hash_obj = hash_obj[0]
        intent_name = get_intent_name(
            tree, src, channel, bot_obj.id, user.user_id)

        if intent_name == "INFLOW-INTENT" or intent_name == None:
            return

        intent_obj = Intent.objects.filter(
            name=intent_name, bots__in=[bot_obj])[0]

        suggested_query_info_obj = SuggestedQueryInfo.objects.filter(
            hash_info=hash_obj, intent_selected=intent_obj).update(count=F('count') + 1)
        if not suggested_query_info_obj:
            SuggestedQueryInfo.objects.create(
                hash_info=hash_obj, intent_selected=intent_obj, count=1)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("In check_and_update_count_for_suggested_queries %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                       'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})


def check_and_update_suggested_query_hash(user, bot_obj, message, channel, src, word_mapped_message, stem_words):
    try:

        bot_info_obj = get_bot_info_object(bot_obj)

        if not bot_info_obj:
            return

        if not bot_info_obj.is_suggested_intent_learning_on:
            return

        if word_mapped_message == "" and len(stem_words) == 0:
            message, stem_words = get_list_of_stem_words_after_spell_correction_from_message(
                user, bot_obj, message, channel, src)
        else:
            message = word_mapped_message
        stem_words.sort()
        stem_words_name = ' '.join(stem_words)
        query_hash = hashlib.md5(stem_words_name.encode()).hexdigest()
        suggested_query_hash_obj = SuggestedQueryHash.objects.filter(
            bot=bot_obj, query_hash=query_hash)
        pk = "none"
        if suggested_query_hash_obj.exists():
            pk = suggested_query_hash_obj.first().pk
        else:
            suggested_query_hash_obj = SuggestedQueryHash.objects.create(
                query_hash=query_hash, query_text=message, bot=bot_obj)
            pk = suggested_query_hash_obj.pk

        save_data(user, {"last_suggested_query_hash_obj_pk": str(pk)},
                  src, channel, bot_obj.pk, is_cache=True)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("In  check_and_update_suggested_query_hash %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                       'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})


def get_list_of_stem_words_after_spell_correction_from_message(user, bot_obj, message, channel_of_message, src):
    try:
        message = run_word_mapper(
            WordMapper, message, bot_obj, src, channel_of_message, user.user_id)
        # Get stemmed keywords
        stem_words = get_stem_words_of_sentence(
            message, src, channel_of_message, user.user_id, bot_obj)

        stem_words = set(stem_words)

        # Disabling spell check and word break

        correct_words = get_correct_words(
            stem_words, user.user_id, src, channel_of_message, bot_obj)

        stem_words = correct_words | stem_words
        stem_words = list(stem_words)

        return message, stem_words
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_list_of_stem_words_after_spell_correction_from_message: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})


def get_query_stem_words_with_pos_list(message, bot_obj):
    try:
        user_query_stem_words_with_pos_list = []
        if bot_obj.is_easychat_ner_required:
            try:
                bot_stopwords = ast.literal_eval(bot_obj.stop_keywords)
                if bot_stopwords == "" or bot_stopwords == None:
                    bot_stopwords = stop
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("Error during get_query_stem_words_with_pos_list is %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
                bot_stopwords = stop
            user_query_stem_words_with_pos_list = get_user_query_pos_list(message, bot_stopwords)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_query_stem_words_with_pos_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': str(bot_obj.pk)})

    return user_query_stem_words_with_pos_list


"""
function: identify_intent_tree
input params:
    user: active user object
    bot_obj: active bot object
    message: user message
    channel_of_message: channel from which message has been received
output:
    return (tree, list)
    tree: identified intent tree based on user message
    list: suggestion list of required
"""


def identify_intent_tree(user, bot_obj, message, channel_of_message, src, category_name, word_mapped_message="", stem_words=[], easychat_bot_user=None):
    try:
        if easychat_bot_user and easychat_bot_user.bot_id:
            bot_id = easychat_bot_user.bot_id
        else:
            bot_id = bot_obj.pk
        if easychat_bot_user and easychat_bot_user.bot_id:
            user_id = easychat_bot_user.user_id
        else:
            user_id = user.user_id

        logger.info("Into identify_intent_tree...", extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})
        # replace word mapper
        if word_mapped_message == "" and len(stem_words) == 0:
            message, stem_words = get_list_of_stem_words_after_spell_correction_from_message(
                user, bot_obj, message, channel_of_message, src)
        else:
            message = word_mapped_message
        logger.info("stem_words : %s", stem_words, extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})

        # Get channel object based on channel
        channel_obj = Channel.objects.get(name=str(channel_of_message))

        # Get BotChannel object with channel and bot for respective query
        if easychat_bot_user and easychat_bot_user.bot_channel_obj:
            bot_channel_obj = easychat_bot_user.bot_channel_obj
        else:
            bot_channel_obj = BotChannel.objects.get(
                bot=bot_obj, channel=channel_obj)

        # If active bot is composite then get relative bot objects list
        bot_objs_list = [bot_obj]
        if easychat_bot_user and easychat_bot_user.bot_info_obj:
            bot_info_obj = easychat_bot_user.bot_info_obj
        else:
            bot_info_obj = BotInfo.objects.get(bot=bot_obj)

        lower_channel_name = channel_obj.name.strip().lower().replace(" ", "_")
        intent_icon_channel_choices_info = bot_info_obj.get_intent_icon_channel_choices_info()

        # Filter intents which are supported in given channel and bot list and
        # which is not deleted.
        is_form_assist = is_form_assist_activated(
            user, src, channel_of_message, bot_obj.pk)

        intent_objs = []
        if easychat_bot_user and easychat_bot_user.category_obj:
            category_obj = easychat_bot_user.category_obj
        else:
            category_obj = get_category_obj(bot_obj, category_name)
        if is_form_assist:
            intent_objs = Intent.objects.filter(bots__in=bot_objs_list,
                                                channels__in=[channel_obj],
                                                is_deleted=False,
                                                is_form_assist_enabled=True,
                                                is_hidden=False)

        else:
            intent_objs = Intent.objects.filter(bots__in=bot_objs_list,
                                                channels__in=[channel_obj],
                                                is_deleted=False,
                                                is_form_assist_enabled=False,
                                                is_hidden=False)
        
        if category_obj:
            intent_objs = intent_objs.filter(Q(category=category_obj) | Q(category__isnull=True))
        
        intent_objs = intent_objs.distinct()

        intent_tuple_list = []
        master_intent_tuple_list = []

        max_score = 0

        overall_intent_score_threshold = bot_obj.intent_score_threshold

        training_question = ""

        length_stemed_training_question = 0
        length_stemed_words = len(stem_words)

        match_percentage = ""

        user_query_stem_words_with_pos_list = get_query_stem_words_with_pos_list(message, bot_obj)

        for intent_obj in intent_objs:
            intent_score = intent_obj.get_score(stem_words, src, channel_obj.pk, user.user_id, message, bot_obj, user_query_stem_words_with_pos_list)
            master_intent_tuple_list.append(
                (intent_score[0], intent_score[1], intent_obj, intent_score[3], intent_score[4]))

            if intent_score[0] >= intent_obj.threshold and intent_score[0] >= max_score and intent_score[2]:

                overall_intent_score = float(
                    abs(intent_score[0])) / float((abs(intent_score[0]) + abs(intent_score[1])))

                if intent_obj.is_small_talk:
                    if overall_intent_score != 1:
                        continue
                    if abs(intent_score[0]) != len(stem_words):
                        continue

                if overall_intent_score >= overall_intent_score_threshold:
                    intent_tuple_list.append(
                        (intent_score[0], intent_score[1], intent_obj, intent_score[4]))
                    max_score = intent_score[0]
                    training_question = intent_score[5]
                    length_stemed_training_question = int(intent_score[6])
                    match_percentage = str(
                        round((length_stemed_words / length_stemed_training_question) * 100))

        intent_tuple_list = sorted(
            intent_tuple_list, key=lambda element: (element[0], element[1]))
        intent_tuple_list.reverse()

        master_intent_tuple_list = sorted(
            master_intent_tuple_list, key=lambda element: (element[0], element[4], element[1]))
        master_intent_tuple_list.reverse()

        logger.info("computed intent identification score...", extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})

        logger.info("[NLP]: intent tuple_list: %s", intent_tuple_list, extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})

        save_data(user, {
            "is_feedback_required": False}, src, channel_of_message, bot_id, is_cache=True)

        save_data(user, {
            "is_attachment_required": False}, src, channel_of_message, bot_id, is_cache=True)

        save_data(user, {
            "choosen_file_type": "none"}, src, channel_of_message, bot_id, is_cache=True)

        save_data(user, {
            "is_authentication_required": False}, src, channel_of_message, bot_id, is_cache=True)

        save_data(user, {
            "is_user_authenticated": False}, src, channel_of_message, bot_id, is_cache=True)

        if len(intent_tuple_list) > 0:

            max_matched_score = intent_tuple_list[0][0]

            not_matched_score = intent_tuple_list[0][1]

            filtered_intent_tuple_list = [(x, intent_obj) for (
                x, y, intent_obj, z) in intent_tuple_list if x == max_matched_score and y == not_matched_score and z == 0]

            if len(filtered_intent_tuple_list) == 1 and ((max_matched_score <= 2 and not_matched_score == 0) or (max_matched_score >= 3)):

                intent_score = filtered_intent_tuple_list[0][0]

                intent_obj = filtered_intent_tuple_list[0][1]

                logger.info(intent_obj.tree.response, extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})

                modes = json.loads(intent_obj.tree.response.modes)

                modes_param = json.loads(intent_obj.tree.response.modes_param)

                save_data(user, {"last_identified_intent_name":
                                 intent_obj.name}, src, channel_of_message, bot_id, is_cache=True)

                save_data(user, {"LanguageSourceUser": str(src)},
                          src, channel_of_message, bot_id, is_cache=True)

                if "is_attachment_required" in modes and str(modes["is_attachment_required"]) == "true":
                    save_data(user, {
                        "is_attachment_required": True}, src, channel_of_message, bot_id, is_cache=True)
                    save_data(user, {
                        "choosen_file_type": str(modes_param["choosen_file_type"])}, src, channel_of_message, bot_id, is_cache=True)

                if intent_obj.is_feedback_required:
                    save_data(user, {
                        "is_feedback_required": True}, src, channel_of_message, bot_id, is_cache=True)

                if intent_obj.is_authentication_required:

                    save_data(user, {
                        "is_authentication_required": True}, src, channel_of_message, bot_id, is_cache=True)

                    is_authenticated, next_tree = user.is_user_authenticated(
                        intent_obj, channel_obj, src, bot_id)

                    if is_authenticated:
                        save_data(user, {
                            "is_user_authenticated": True}, src, channel_of_message, bot_id, is_cache=True)

                    logger.info("Exit from identify_intent_tree...", extra={'AppName': 'EasyChat', 'user_id': str(
                        user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})
                    return next_tree, [], training_question, match_percentage

                logger.info("[NLP]: intent selected: %s", intent_obj.name, extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})
                logger.info("[NLP]: intent threshold: %s",
                            intent_obj.threshold, extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
                logger.info("[NLP]: intent score: %s", intent_score, extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})
                logger.info("Exit from identify_intent_tree...", extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})
                return intent_obj.tree, [], training_question, match_percentage

            elif bot_channel_obj.is_nlp_suggestions_required:
                logger.info("[NLP]: suggestions required", extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})

                logger.info("PRINTING MASTER TUPLE LIST", extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})

                logger.info("[NLP]: MASTER TUPLE LIST %s", master_intent_tuple_list, extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})
                suggestion_list, max_suggest_allowed = [], bot_obj.number_of_nlp_suggestion_allowed
                for (score_0, score_1, intent_obj, stopword_score, query_score) in master_intent_tuple_list:
                    if (score_0 - stopword_score) >= 1 and max_suggest_allowed > 0 and not intent_obj.is_small_talk:

                        intent_icon = ""
                        if bot_info_obj.enable_intent_icon and (lower_channel_name in intent_icon_channel_choices_info) and ("4" in intent_icon_channel_choices_info[lower_channel_name]):
                            if intent_obj.build_in_intent_icon:
                                intent_icon = intent_obj.build_in_intent_icon.icon
                            else:
                                intent_icon = '<img width="40px" height="40px" src="' + intent_obj.intent_icon + '">'

                        suggestion_list.append({
                            "name": get_multilingual_intent_name(intent_obj, src),
                            "id": intent_obj.id,
                            "intent_icon": intent_icon
                        })

                        max_suggest_allowed -= 1

                logger.info("Exit from identify_intent_tree...", extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})

                return None, suggestion_list, "", ""
        else:
            if bot_channel_obj.is_nlp_suggestions_required and len(master_intent_tuple_list) > 0 and master_intent_tuple_list[0][0] > 0:

                logger.info(
                    "[NLP]: search for suggestions in master tuple list", extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})

                suggestion_list, max_suggest_allowed = [], bot_obj.number_of_nlp_suggestion_allowed
                for (score_0, score_1, intent_obj, stopword_score, query_score) in master_intent_tuple_list:
                    if (score_0 - stopword_score) >= 1 and max_suggest_allowed > 0 and not intent_obj.is_small_talk:

                        intent_icon = ""
                        if bot_info_obj.enable_intent_icon and (lower_channel_name in intent_icon_channel_choices_info) and ("4" in intent_icon_channel_choices_info[lower_channel_name]):
                            if intent_obj.build_in_intent_icon:
                                intent_icon = intent_obj.build_in_intent_icon.icon
                            else:
                                intent_icon = '<img width="40px" height="40px" src="' + intent_obj.intent_icon + '">'

                        suggestion_list.append({
                            "name": get_multilingual_intent_name(intent_obj, src),
                            "id": intent_obj.id,
                            "intent_icon": intent_icon
                        })
                        max_suggest_allowed -= 1

                logger.info("Exit from identify_intent_tree...", extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})
                return None, suggestion_list, "", ""

        logger.info("[NLP]: No intent found!", extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error identify_intent %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})

    logger.info("Exit from identify_intent_tree...", extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_id)})
    return None, [], training_question, match_percentage


"""
function: return_next_tree_based_on_message
input params:
    easychat_bot_user: EasyChatBotUser object
    message: input user query as string
    current_tree: active tree where user is located.
    recur_Flag: for advanced NLP
output:
    return tree based on tree's accept keywords and user message
"""


def return_next_tree_based_on_message(easychat_bot_user, message, current_tree):
    
    try:
        bot_info_obj = easychat_bot_user.bot_info_obj
        # if semantic similarity is enabled in bot
        if bot_info_obj and bot_info_obj.is_advance_tree_level_nlp_enabled:
            message = identify_next_tree_semantic_similarities(
                message, current_tree, bot_info_obj)

        child_tree_list = current_tree.children.filter(is_deleted=False)
        for child_tree in child_tree_list:

            child_tree_accept_keywords = [str(keyword).strip().lower(
            ) for keyword in child_tree.accept_keywords.split(",") if keyword != ""]

            tree_name = str(child_tree.name).strip().lower()
            tree_name = process_string(
                tree_name, "None", "None", "None", "None")
            # message is processed so as to make a fair comparison tree name should also be processed
            child_tree_accept_keywords.append(tree_name)
            for keywords in child_tree_accept_keywords:
                if sorted(message.strip().lower().split()) == sorted(keywords.split()):
                    return child_tree
        
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error return_next_tree_based_on_message %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return None


"""
function : return_next_tree_based_on_intent_identification
input params:
         user : current user
         bot_obj : current bot
         message : user message
         channel_of_message : channel from where user message has come
         current_tree : current tree object

output:
         next_tree : next selected tree based on user message after intent identification
         status_re_sentence : True | False
         suggestion list : suggestion list
"""


def return_next_tree_based_on_intent_identification(user,
                                                    bot_obj,
                                                    message,
                                                    channel_of_message,
                                                    current_tree,
                                                    src,
                                                    category_name,
                                                    word_mapped_message,
                                                    stem_words,
                                                    easychat_bot_user):

    tree, suggestion_list, training_question, match_percentage = identify_intent_tree(
        user, bot_obj, message, channel_of_message, src, category_name, word_mapped_message, stem_words, easychat_bot_user)

    if tree == None:
        return current_tree, bool(current_tree), suggestion_list, training_question, match_percentage
    else:
        if user.tree != None:
            user.previous_tree = None
            user.save(update_fields=['previous_tree'])

        return tree, False, suggestion_list, training_question, match_percentage


"""
function: execute_postprocessor
input params:
    user: active user object

execute given function and save details into data model.
"""


def execute_postprocessor(tree, message, easychat_bot_user):

    if not tree.post_processor:
        return True

    user = easychat_bot_user.user
    bot_obj = easychat_bot_user.bot_obj
    src = easychat_bot_user.src
    channel = easychat_bot_user.channel_name
    post_processor = replace_data_values(
        user, tree.post_processor.function, src, channel, bot_obj.pk)
    lang = tree.post_processor.processor_lang

    logger.info("PostProcessor Name: %s",
                tree.post_processor.name, extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})

    start_time = time.time()

    # run post processor according to language
    parameter = message.strip()
    if tree.post_processor.is_original_message_required:
        parameter = easychat_bot_user.original_message.strip()
    is_parameter_required = True
    json_data = execute_code_under_time_limit(
        lang, str(post_processor), easychat_bot_user, parameter, is_parameter_required)

    end_time = time.time()

    elapsed_time = end_time - start_time

    intent_name = get_intent_name(
        tree, src, channel, bot_obj.pk, user.user_id)
    if intent_name == "INFLOW-INTENT":
        intent_name = get_last_identified_intent_name(
            user, src, channel, str(bot_obj.pk))

    intent_obj = Intent.objects.filter(name=intent_name, bots__in=[
                                       bot_obj], is_deleted=False)
    new_parameters_list = json.dumps({
        "intent_name": intent_name,
        "intent_pk": str(intent_obj[0].id),
        "tree_name": str(tree.name),
        "tree_id": str(tree.id)
    })
    save_api_data(json_data, elapsed_time, bot_obj,
                  tree.post_processor.name, user, src, channel, new_parameters_list)

    logger.info("[ENGINE]: PostProcessor JSON Data: %s",
                str(json_data), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    status_code = json_data["status_code"]

    status_message = "None"
    if "status_message" in json_data:
        status_message = json_data["status_message"]

    logger.info("[ENGINE]: PostProcessor Status Code: %s",
                str(status_code), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    logger.info(
        "[ENGINE]: PostProcessor Status Message: %s", str(status_message), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})

    if "data" in json_data:
        is_cache = False
        if "is_cache" in json_data["data"] and json_data["data"]["is_cache"]:
            is_cache = True
        save_data(user, json_data["data"],
                  None, None, bot_obj.pk, is_cache=is_cache)

    if str(status_code) == "200" or str(status_code) == "400":

        # Get all child tree list
        child_tree_list = tree.children.filter(
            is_deleted=False)
        # If current tree has zero children tree then return zero
        if len(child_tree_list) == 0:
            return False
        # If current tree has one child tree then return that tree as
        # next tree
        if len(child_tree_list) == 1:
            return True

        if "child_choice" not in json_data:
            logger.info(
                "Multiple child trees but child choice is not defined in post processor", extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
            return True

        child_choice = json_data["child_choice"]
        logger.info("[ENGINE]: Child Choice: %s", str(child_choice), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})

        return True

    else:
        return False


def get_new_parameters_list_from_intent_and_tree_obj(intent_name, intent_obj, current_tree):
    new_parameters_list = ""
    try:
        intent_pk = ""
        tree_name = ""
        tree_id = ""
        if intent_obj:
            intent_pk = str(intent_obj.first().pk)
        if current_tree:
            tree_name = str(current_tree.name)
            tree_id = str(current_tree.id)
        new_parameters_list = json.dumps({
            "intent_name": intent_name,
            "intent_pk": str(intent_pk),
            "tree_name": str(tree_name),
            "tree_id": str(tree_id)
        })
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(" error in return_next_tree [ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return new_parameters_list


"""
function: return_next_tree
input params:
    user : active user object
    bot_obj : active bot object
    message : processed user message
    channel_of_message : channel from which message is received
output:
    return (tree, bool, list)
    tree : next_tree identified based on message
    bool : whether re-sentence is required or not
    list : suggestion list of required
"""


def return_next_tree(message, user, easychat_bot_user, easychat_params, word_mapped_message, stem_words):
    try:
        bot_obj = easychat_bot_user.bot_obj
        original_message = easychat_bot_user.original_message
        channel_of_message = easychat_bot_user.channel_name
        src = easychat_bot_user.src
        current_tree = user.tree
        training_question = ""
        match_percentage = ""
        if easychat_bot_user.bot_info_obj:
            bot_info_obj = easychat_bot_user.bot_info_obj
        else:
            bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
        # Check Whether current tree is none or not
        if current_tree is None:
            # Current tree is none
            logger.info("[ENGINE]: user current tree is none", extra={'AppName': 'EasyChat', 'user_id': str(
                user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
            # Identify intent
            next_tree, status_re_sentence, suggestion_list, training_question, match_percentage = return_next_tree_based_on_intent_identification(
                user, bot_obj, message, channel_of_message, None, src, easychat_bot_user.category_name, word_mapped_message, stem_words, easychat_bot_user)

            try:
                intent_category_based = None
                intent_name = get_intent_name(
                    next_tree, src, channel_of_message, (bot_obj.pk), user.user_id)
                intent_obj = Intent.objects.filter(name=intent_name, bots__in=[
                                                   bot_obj], is_deleted=False)
                if intent_obj[0].is_category_response_allowed:
                    intent_category_based = intent_obj[0]
                    data_obj = Data.objects.filter(
                        user=user, variable="category_name")
                    category_name = str(data_obj[0].get_value()).lower()
                    category_name = category_name.replace("\"", "")
                    next_tree = intent_obj[0].tree
                    next_tree = next_tree.children.filter(
                        name__icontains=str(category_name), is_deleted=False)[0]
                    easychat_bot_user.is_recur_flag = True
                    easychat_bot_user.parent_tree = intent_category_based.tree
            except Exception:
                pass
            return next_tree, status_re_sentence, suggestion_list, intent_category_based, training_question, match_percentage, {}
        else:
            # User is in some flow
            # Check whether post processor is available or not
            # If post processor is None and there are multiple child for
            # current tree

            if easychat_params.response_repeat_needed:
                return current_tree, True, [], None, training_question, match_percentage, {}

            child_trees = current_tree.children.filter(is_deleted=False)

            if current_tree.post_processor == None:

                logger.info("Current Tree PostProcessor is None", extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})

                if current_tree.is_category_response_allowed:
                    data_obj = Data.objects.filter(
                        user=user, variable="category_name")
                    category_name = str(data_obj[0].get_value()).lower()
                    category_name = category_name.replace("\"", "")
                    next_tree = current_tree.children.filter(
                        name__icontains=str(category_name), is_deleted=False)[0]
                    easychat_bot_user.is_recur_flag = True
                    easychat_bot_user.parent_tree = current_tree
                else:
                    next_tree = return_next_tree_based_on_message(easychat_bot_user,
                                                                  message, current_tree)

                if next_tree != None:
                    logger.info("Next Tree selected: %s", str(next_tree), extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
                    return next_tree, False, [], None, training_question, match_percentage, {}
                logger.info(
                    "Next Tree selected is None. Identify next tree based on intent identification.", extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})

                if not bot_info_obj.enable_abort_flow_feature:
                    if easychat_params.entered_suggestion and message.strip().isdigit():
                        selected_intent_obj = Intent.objects.filter(
                            pk=int(message)).first()
                        if selected_intent_obj:
                            next_tree = selected_intent_obj.tree
                            user.tree = next_tree
                            user.save(update_fields=['tree'])
                            return next_tree, False, [], None, training_question, match_percentage, {}

                    next_tree, status_re_sentence, suggestion_list, training_question, match_percentage = return_next_tree_based_on_intent_identification(
                        user, bot_obj, message, channel_of_message, current_tree, src, easychat_bot_user.category_name, word_mapped_message, stem_words, easychat_bot_user)

                    if status_re_sentence and len(child_trees) == 1:
                        return child_trees[0], False, suggestion_list, None, training_question, match_percentage, {}

                    logger.info("Next Tree selected after intent identification: %s", str(next_tree), extra={'AppName': 'EasyChat', 'user_id': str(
                        user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
                    return next_tree, status_re_sentence, suggestion_list, None, training_question, match_percentage, {}

                if len(child_trees) == 1:
                    return child_trees[0], False, [], None, "", "", {}

                return current_tree, True, [], None, training_question, match_percentage, {}

            post_processor = replace_data_values(
                user, current_tree.post_processor.function, src, channel_of_message, bot_obj.pk)
            lang = current_tree.post_processor.processor_lang

            logger.info("PostProcessor Name: %s",
                        current_tree.post_processor.name, extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})

            start_time = time.time()

            # run post processor according to language
            easychat_bot_user.update_easychat_bot_user_details(user=user, src=src, bot_id=bot_obj.pk, channel=channel_of_message, bot_obj=bot_obj)
            parameter = message.strip()
            if current_tree.post_processor.is_original_message_required:
                parameter = original_message.strip()
            is_parameter_required = True

            json_data = execute_code_under_time_limit(
                lang, str(post_processor), easychat_bot_user, parameter, is_parameter_required)

            end_time = time.time()

            elapsed_time = end_time - start_time
            intent_name = get_intent_name(
                current_tree, src, channel_of_message, (bot_obj.pk), user.user_id)

            if intent_name == "INFLOW-INTENT":
                intent_name = get_last_identified_intent_name(
                    user, src, channel_of_message, str(bot_obj.pk))
            intent_obj = Intent.objects.filter(name=intent_name, bots__in=[
                                               bot_obj], is_deleted=False)

            new_parameters_list = get_new_parameters_list_from_intent_and_tree_obj(intent_name, intent_obj, current_tree)
            save_api_data(json_data, elapsed_time, bot_obj,
                          current_tree.post_processor.name, user, src, channel_of_message, new_parameters_list)

            logger.info("[ENGINE]: PostProcessor JSON Data: %s",
                        str(json_data), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
            status_code = json_data["status_code"]

            status_message = "None"
            if "status_message" in json_data:
                status_message = json_data["status_message"]

            logger.info("[ENGINE]: PostProcessor Status Code: %s",
                        str(status_code), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
            logger.info(
                "[ENGINE]: PostProcessor Status Message: %s", str(status_message), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})

            if "data" in json_data:
                is_cache = False
                if "is_cache" in json_data["data"] and json_data["data"]["is_cache"]:
                    is_cache = True
                save_data(user, json_data["data"],
                          None, None, bot_obj.pk, is_cache=is_cache)

            if str(status_code) == "200" or str(status_code) == "400":

                # Get all child tree list
                child_tree_list = current_tree.children.filter(
                    is_deleted=False)
                # If current tree has zero children tree then return zero
                if len(child_tree_list) == 0:
                    return None, False, [], None, training_question, match_percentage, {}
                # If current tree has one child tree then return that tree as
                # next tree
                if len(child_tree_list) == 1:
                    next_tree = child_tree_list[0]
                    return next_tree, False, [], None, training_question, match_percentage, {}

                if "child_choice" not in json_data:
                    logger.info(
                        "Multiple child trees but child choice is not defined in post processor", extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
                    next_tree = return_next_tree_based_on_message(easychat_bot_user,
                                                                  message, current_tree)
                    return next_tree, False, [], None, training_question, match_percentage, {}

                child_choice = json_data["child_choice"]
                logger.info("[ENGINE]: Child Choice: %s", str(child_choice), extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})

                next_tree = return_next_tree_based_on_message(easychat_bot_user,
                                                              str(child_choice), current_tree)
                return next_tree, False, [], None, training_question, match_percentage, {}

            elif str(status_code) == "206":   # Give user another chance
                logger.info("[ENGINE]: Returning same tree %s",
                            str(current_tree), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
                return current_tree, True, [], None, training_question, match_percentage, {"is_repeat_tree": True}
            elif str(status_code) == "308":   # Redirect to another intent
                logger.info("[ENGINE]: Redirecting to another Intent", extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})

                if not bot_info_obj.enable_abort_flow_feature:
                    if easychat_params.entered_suggestion and message.strip().isdigit():
                        selected_intent_obj = Intent.objects.filter(
                            pk=int(message), is_deleted=False).first()
                        if selected_intent_obj:
                            next_tree = selected_intent_obj.tree
                            user.tree = next_tree
                            user.save(update_fields=['tree'])
                            return next_tree, False, [], None, training_question, match_percentage, {}

                next_tree, status_re_sentence, suggestion_list, training_question, match_percentage = return_next_tree_based_on_intent_identification(
                    user, bot_obj, message, channel_of_message, current_tree, src, easychat_bot_user.category_name, word_mapped_message, stem_words, easychat_bot_user)

                intent_category_based = None
                intent_name = get_intent_name(
                    next_tree, src, channel_of_message, (bot_obj.pk), user.user_id)
                intent_obj = Intent.objects.filter(name=intent_name, bots__in=[bot_obj], is_deleted=False).first()
                if intent_obj and intent_obj.is_category_response_allowed:
                    intent_category_based = intent_obj
                    data_obj = Data.objects.filter(user=user, variable="category_name").first()
                    if data_obj:
                        category_name = str(data_obj.get_value()).lower()
                        category_name = category_name.replace("\"", "")
                        next_tree_obj = intent_obj.tree
                        next_tree_obj = next_tree_obj.children.filter(
                            name__icontains=str(category_name), is_deleted=False).first()
                        if next_tree_obj:
                            easychat_bot_user.is_recur_flag = True
                            easychat_bot_user.parent_tree = intent_category_based.tree
                            return next_tree_obj, status_re_sentence, suggestion_list, intent_category_based, training_question, match_percentage, {}

                logger.info(
                    "Next Tree selected after intent identification: %s", str(next_tree), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
                return next_tree, status_re_sentence, suggestion_list, None, training_question, match_percentage, {}
            else:
                logger.error(
                    "[ENGINE]: status_code out of scope for tree %s", str(current_tree.name), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
                return None, False, [], None, training_question, match_percentage, {}

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(" error in return_next_tree [ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': str(src), 'channel': str(channel_of_message), 'bot_id': str(bot_obj.pk)})
        return None, False, [], None, training_question, match_percentage, {}


"""
function: clear_user_data
input params:
    user_id: active user object id

clears user data associated with that id from Data model
"""


def clear_user_data(user_id, bot, channel):
    try:
        if os.path.exists("files/language_support/" + str(user_id)) and user_id != "":
            cmd = "rm -rf files/language_support/" + str(user_id)
            subprocess.run(cmd, shell=True)

        Data.objects.filter(user__user_id=user_id).delete()

        user = Profile.objects.get(user_id=user_id, bot=bot)

        UserAuthentication.objects.filter(user=user).delete()

        if user.tree and user.tree.children.all().count():
            generate_flow_dropoff_object(user)

        user.tree = None
        user.user_pipe = ""
        user.save()

        return user
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_child_tree_objs
input params:
    root_tree_obj: object of root tree
    tree_pk_list: list of child tree objects

output params:
    json_resp: json containing tree_name, tree_pk, subtree information

"""


def get_child_tree_objs(root_tree_obj, tree_pk_list, language_obj):
    try:
        tree_name, lang_tuned_tree_obj = get_multilingual_tree_name(
            root_tree_obj, language_obj)

        if root_tree_obj.pk in tree_pk_list:
            if root_tree_obj.response is None:
                return {
                    "tree_name": tree_name,
                    "tree_pk": root_tree_obj.pk,
                    "tree_resp": "",
                    "subtree": {
                    },
                    "is_repeat": True
                }
            else:
                sentence = get_multilingual_tree_sentence(
                    root_tree_obj, language_obj, lang_tuned_tree_obj)
                return {
                    "tree_name": tree_name,
                    "tree_pk": root_tree_obj.pk,
                    "tree_resp": sentence,
                    "subtree": {
                    },
                    "is_repeat": True
                }

        json_resp = {}

        json_resp["tree_name"] = tree_name
        json_resp["tree_pk"] = root_tree_obj.pk
        if root_tree_obj.pk in tree_pk_list:
            json_resp["is_repeat"] = True
        else:
            json_resp["is_repeat"] = False

        tree_pk_list.append(root_tree_obj.pk)
        if(root_tree_obj.post_processor != None):
            json_resp["post_processor"] = root_tree_obj.post_processor.name
        if root_tree_obj.response is None:
            sentence = ""
        else:
            sentence = get_multilingual_tree_sentence(
                root_tree_obj, language_obj, lang_tuned_tree_obj)
        json_resp["tree_resp"] = sentence
        child_tree_objs = root_tree_obj.children.filter(is_deleted=False)

        count = 1
        temp_json = {}
        for child_tree_obj in child_tree_objs:
            temp_json[str(count)] = get_child_tree_objs(
                child_tree_obj, tree_pk_list, language_obj)
            count += 1

        json_resp["subtree"] = temp_json

        return json_resp

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_child_tree_objs: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_child_pk_list
input params:
    parent_tree_pk: pk of parent tree object

output params:
    pk_list: list of the pk of all the child tree of that parent

"""


def get_child_pk_list(parent_tree_pk):
    try:
        parent_tree_obj = Tree.objects.get(
            pk=int(parent_tree_pk), is_deleted=False)
        child_pk_list = list(
            parent_tree_obj.children.values_list('pk', flat=True))

        pk_list = [int(parent_tree_pk)]
        for pk in child_pk_list:
            pk_list += get_child_pk_list(pk)

        return pk_list
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("get_child_pk_list: %s at %s",
                       str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return []


"""
function: get_google_search_results
input_params:
    query: user query
output_params:
    returns json containig google search result data based on user query
"""


def get_google_search_results(query, search_cx, src, channel, bot_id, user_id):
    try:
        from googleapiclient.discovery import build
        service = build("customsearch", "v1",
                        developerKey=settings.GOOGLE_SEARCH_DEVELOPER_KEY)
        res = service.cse().list(q=query, cx=search_cx).execute()
        google_search_results = []
        for result in res['items']:
            temp_dict = {}
            temp_dict["link"] = result['link']
            temp_dict["title"] = result['title']
            temp_dict["content"] = result['snippet']
            temp_dict["image_url"] = ""
            google_search_results.append(temp_dict)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error Google Search Results %s at line no> %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        google_search_results = []
    return google_search_results


"""
function: load_the_dictionary
Return word dictionary
"""


def load_the_dictionary(user_id, src, channel, bot_id):
    try:
        logger.info("Into load_the_dictionary...", extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        dict_obj = None
        if str(bot_id).isdigit():
            dict_obj = WordDictionary.objects.filter(bot__pk=bot_id).first()
        if not dict_obj:
            logger.warning("Error load_the_dictionary WordDictionary objects does not exist of this bot.", extra={'AppName': 'EasyChat', 'user_id': str(user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
            dict_obj = WordDictionary.objects.all().first()

        word_list = json.loads(dict_obj.word_dict)["items"]
        words_in_dict = set(word_list)
        dictionary = list(word_list)

        logger.info("Exit from load_the_dictionary...", extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        return (dictionary, words_in_dict)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error load_the_dictionary %s at line no> %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        return ([], set())


"""
function: get_edit_distance_threshold
return integer which restrict number of characters of correction allowed
"""


def get_edit_distance_threshold(user_id, src, channel, bot_id):
    return 1


"""
function: correct_query
input params:
    query: input user message as string (might has spelling mistake)
output:
    return string with correct spelling

Function tries to correct query upto certain characters
"""


def correct_query(query, user_id, src, channel, bot_id):
    logger.info("Into correct_query...", extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    logger.info("Query to be corrected: %s", str(query), extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    did_you_mean = ''
    try:
        (dictionary, words_in_dict) = load_the_dictionary(
            user_id, src, channel, bot_id)
        query = query.strip().lower()
        words = query.split(' ')

        for word in words:

            if (word not in words_in_dict) and len(word) > 4:
                if(difflib.get_close_matches(word, dictionary)):
                    corrected_word = str(difflib.get_close_matches(word,
                                                                   dictionary)[0])

                    if(int(editdistance.eval(word, corrected_word)) <= get_edit_distance_threshold(user_id, src, channel, bot_id)):
                        did_you_mean += corrected_word.upper()
                    else:
                        did_you_mean += word
                else:
                    did_you_mean += word
            else:
                did_you_mean += word

            did_you_mean += ' '

        did_you_mean = did_you_mean.strip()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error correct_query %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        return query

    logger.info("Corrected query: %s", str(did_you_mean), extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    logger.info("Exit from correct_query...", extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return did_you_mean


"""
function: process_string
input params:
    sentence: string which contains all types of special character
output:
    output string which contains only a-z, A-Z, 0-9, do_nothing punctuations and
    replace_space punctuations are replaced by space
"""


def process_string(sentence, user_id, src, channel, bot_id):
    try:
        logger.info("Into process_string...", extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        logger.info("Input sentence: %s", sentence, extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        # sentence = re.sub(r"[^a-zA-Z0-9.-/:]+", ' ', sentence)
        # sentence = sentence.strip()
        # sentence = re.sub('(\s+)(a|an|the)(\s+)', ' ', sentence)

        configobject = Config.objects.all()[0]
        autocorrect_replace_space = configobject.autocorrect_replace_space
        autocorrect_do_nothing = configobject.autcorrect_do_nothing
        if autocorrect_replace_space != "":
            replace_space = "[" + autocorrect_replace_space + "]"
            sentence = re.sub(replace_space, ' ', sentence)

        do_nothing = "[^a-zA-Z0-9 " + autocorrect_do_nothing + "]+"
        sentence = re.sub(do_nothing, ' ', sentence)
        sentence = sentence.strip()
        sentence = re.sub('(\s+)(a|an|the)(\s+)', ' ', sentence)
        logger.info("Output processed sentence: %s", sentence, extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        logger.info("Exit from process_string...", extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error process_string %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return sentence


"""
function: save_audit_trail
input params:
    user_obj: active user object
    action: action done by user [choices are defined in constants.py]
    data: data string
Save audit to database
"""


def save_audit_trail(user_obj, action, data):
    try:
        AuditTrail.objects.create(user=user_obj, action=action, data=data)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_audit_trail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_java_processor_response
input params:
    code: processor code written in java
    parameter: It is a default variable. In case of post and pipe processor, it holds a value pass by respective processors.
output:
    response: It is the response packet after execution of processor code in java.

This function is used to run all the processor code written in java.
"""


def get_java_processor_response(code, user, src, channel, bot_id, parameter="no parameter provided"):
    response = {}
    response["status_code"] = "500"
    response["status_message"] = "internal server error."

    try:
        if not os.path.exists('files/language_support/' + str(user.user_id) + "/EasyChatConsole.java"):
            cmd = "mkdir files/language_support/" + str(user.user_id)
            subprocess.run(cmd, shell=True)
            cmd = "touch files/language_support/" + \
                str(user.user_id) + "/EasyChatConsole.java"
            subprocess.run(cmd, shell=True)
            cmd = "mkdir files/language_support/" + str(user.user_id) + "/org"
            subprocess.run(cmd, shell=True)
            cmd = "cp -r files/org/* files/language_support/" + \
                str(user.user_id) + "/org"
            subprocess.run(cmd, shell=True)

        java_file = open("files/language_support/" + str(user.user_id) +
                         "/EasyChatConsole.java", 'r+')
        java_file.write(code)
        java_file.close()
        cmd = "javac files/language_support/" + \
            str(user.user_id) + "/EasyChatConsole.java"

        try:
            curr_process = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if curr_process.returncode == 0:
                cmd = "java -cp files/language_support/" + \
                    str(user.user_id) + "/ EasyChatConsole '" + \
                    str(parameter) + "'"
                json_data = subprocess.run(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if json_data.returncode == 0:
                    cmd = "rm -rf files/language_support/" + \
                        str(user.user_id) + "/EasyChatConsole.class"
                    subprocess.run(cmd, shell=True)
                    json_data = (json_data.stdout).decode('utf-8')
                    try:
                        response = json.loads(json_data)
                        logger.info("Java processor response %s",
                                    str(response), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Java processor error: %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
                else:
                    logger.error("Java Programe: returncode 1." +
                                 (json_data.stderr).decode('utf-8'), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
            else:
                logger.error("Java Programe is not compiling: returncode 1." +
                             (curr_process.stderr).decode('utf-8'), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Java processor error: %s at %s",
                         str(e), str(exc_tb.tb_lineno))

        cmd = 'echo "" > "files/language_support/' + \
            str(user.user_id) + '/EasyChatConsole.java" '
        subprocess.run(cmd, shell=True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("get_java_processor_response: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    return response


"""
function: get_php_processor_response
input params:
    code: processor code written in php
    parameter: It is a default variable. In case of post and pipe processor, it holds a value pass by respective processors.
output:
    response: It is the response packet after execution of processor code in php.

This function is used to run all the processor code written in php.
"""


def get_php_processor_response(code, user, src, channel, bot_id, parameter="no parameter provided"):
    response = {}
    response["status_code"] = "500"
    response["status_message"] = "internal server error."
    try:
        code = code.replace("?>", "")
        code = code + "\n$parameter = '" + parameter + \
            "';\n    print_r(json_encode(f($parameter)));\n?>"

        if not os.path.exists("files/language_support/" + str(user.user_id) + "/EasyChatConsole.php"):
            cmd = "mkdir files/language_support/" + str(user.user_id)
            subprocess.run(cmd, shell=True)
            cmd = "touch files/language_support/" + \
                str(user.user_id) + "/EasyChatConsole.php"
            subprocess.run(cmd, shell=True)

        php_file = open("files/language_support/" +
                        str(user.user_id) + "/EasyChatConsole.php", 'r+')
        php_file.write(code)
        php_file.close()
        cmd = "php files/language_support/" + \
            str(user.user_id) + "/EasyChatConsole.php"

        proc = subprocess.run(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if proc.returncode == 0:
            json_data = (proc.stdout).decode('utf-8')
            response = json.loads(json_data)
        else:
            logger.error(
                "Error during processor execution written in php: " + (proc.stdout).decode('utf-8'), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
            response["status_message"] = (proc.stdout).decode('utf-8')

        cmd = ' echo "" > "files/language_support/' + \
            str(user.user_id) + '/EasyChatConsole.php" '
        subprocess.run(cmd, shell=True)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("get_php_processor_response: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    return response


"""
function: save_form_assist_analytics
input params:
    code: It will save the details of the lead who is assisted by form
    parameter: channel_params (is_form_assist), bot_id, user, form_assist_id
"""


def save_form_assist_analytics(channel_params, easychat_bot_user, user, form_assist_id):
    try:

        if "is_form_assist" not in channel_params or channel_params["is_form_assist"] == False:
            return

        bot_obj = easychat_bot_user.bot_obj
        channel = easychat_bot_user.channel_name
        src = easychat_bot_user.src
        language_obj = easychat_bot_user.selected_language
        form_assist_obj = FormAssist.objects.get(pk=int(form_assist_id))
        meta_data = json.dumps(channel_params)
        form_assist_analytics_obj = FormAssistAnalytics.objects.create(
            bot=bot_obj, form_assist_field=form_assist_obj, user_id=user.user_id, meta_data=meta_data, selected_language=language_obj)

        save_data(user, {"FormAssistAnalyticsId": form_assist_analytics_obj.pk},
                  src, channel, bot_obj.pk, is_cache=False)
        logger.info("FormAssist Lead has been saved successfully.", extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_form_assist_analytics: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})


def get_hashed_intent_name(intent_name, bot_obj):
    try:
        stem_words = get_stem_words_of_sentence(
            intent_name, None, None, None, bot_obj)
        stem_words.sort()
        hashed_name = ' '.join(stem_words)
        hashed_name = hashlib.md5(hashed_name.encode()).hexdigest()
        return hashed_name
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_form_assist_analytics: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return ""


"""
function: build_channel_welcome_response
input params:
    user: active user object
    bot_obj: bot object which is to be tested
    channe_obj: channel object
    BotChannel
    Data


Generates a welcomes response for the bot that is switched.

"""


def build_channel_welcome_response(easychat_bot_user, easychat_params, is_bot_switch_welcome_message=True):
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        bot_obj = easychat_bot_user.bot_obj
        channel_obj = easychat_params.channel_obj
        bot_channel_obj = BotChannel.objects.get(
            bot=bot_obj, channel=channel_obj)
        initial_questions = json.loads(bot_channel_obj.initial_messages)["items"]
        recommendations, images, videos = [], [], []

        if is_bot_switch_welcome_message:
            easychat_bot_user.src = "en"
        
        language_obj = None
        if easychat_bot_user.src != "en":
            language_obj = Language.objects.filter(lang=easychat_bot_user.src).first()

        for initial_question_pk in initial_questions:
            intent_obj = Intent.objects.filter(pk=initial_question_pk, is_deleted=False).first()

            if intent_obj:
                if easychat_bot_user.src == "en":
                    intent_name = intent_obj.name
                else:
                    lang_tuned_obj = LanguageTuningIntentTable.objects.filter(
                        language=language_obj, intent=intent_obj).first()
                    if lang_tuned_obj:
                        intent_name = lang_tuned_obj.multilingual_name
                    else:
                        intent_name = get_translated_text(
                            intent_obj.name, easychat_bot_user.src, EasyChatTranslationCache)
                recommendations.append({
                    "name": intent_name,
                    "id": intent_obj.pk
                })
        try:
            images = json.loads(bot_channel_obj.initial_messages)["images"]
            images = [settings.EASYCHAT_HOST_URL + image for image in images]
        except Exception:
            pass

        try:
            videos = json.loads(bot_channel_obj.initial_messages)["videos"]
        except Exception:
            pass

        welcome_message = bot_channel_obj.welcome_message
        if easychat_bot_user.src != "en":
            lang_obj = Language.objects.filter(lang=easychat_bot_user.src).first()
            language_tuned_objects = LanguageTunedBotChannel.objects.filter(
                language=lang_obj, bot_channel=bot_channel_obj)
            if language_tuned_objects.exists():
                welcome_message = language_tuned_objects[0].welcome_message
            else:
                welcome_message = get_translated_text(
                    welcome_message, lang_obj.lang, EasyChatTranslationCache)

        response["response"]["is_authentication_required"] = False
        response["response"]["is_response_to_be_language_processed"] = False
        response["response"]["language_src"] = easychat_bot_user.src
        response["user_id"] = easychat_bot_user.user_id
        response["bot_id"] = bot_obj.pk
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"]["recommendations"] = recommendations
        response["response"]["tooltip_response"] = ""
        response["response"]["speech_response"][
            "text"] = welcome_message
        response["response"]["speech_response"][
            "reprompt_text"] = welcome_message
        response["response"]["text_response"][
            "text"] = welcome_message
        response["response"]["images"] = images
        response["response"]["videos"] = videos
        response["response"]["is_flow_ended"] = True
        response["response"]["is_bot_switch"] = False
        response["response"]["is_suggestion_required"] = True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] build_channel_welcome_response: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            easychat_bot_user.user_id), 'source': 'None', 'channel': str(channel_obj), 'bot_id': str(bot_obj.pk)})
        response["status_code"] = 500
        response["status_message"] = str(e)

    return response


def check_bot_switch_logic_for_voice_based_channels(easychat_bot_user, easychat_params):
    try:
        message = easychat_bot_user.message
        bot_obj = easychat_bot_user.bot_obj
        temp_message = message.lower().strip()
        channel = easychat_params.channel_obj

        if "switch to" not in temp_message.lower():
            return False, bot_obj, None

        temp_message = temp_message.replace("switch to", "")

        temp_message = temp_message.strip()

        message_list = temp_message.split(' ')

        if not len(message_list) > 1:
            return False, bot_obj, None

        user_first_name = message_list[0]

        owner_of_requested_bot = User.objects.filter(
            first_name__iexact=user_first_name, is_staff=True, is_bot_invocation_enabled=True).first()

        if owner_of_requested_bot:

            bot_name = " ".join(message_list[1:]).lower().strip()

            switched_bot_obj = Bot.objects.filter(name__iexact=bot_name, users__in=[
                                                  owner_of_requested_bot], is_deleted=False, is_uat=True).first()

            if switched_bot_obj:
                bot_obj = switched_bot_obj
                easychat_bot_user.bot_obj = bot_obj
                easychat_bot_user.bot_id = bot_obj.pk
                user = set_user(easychat_bot_user.user_id, '', easychat_bot_user.src,
                                easychat_bot_user.channel_name, bot_obj.pk, easychat_bot_user)
                bot_response = build_channel_welcome_response(
                    easychat_bot_user, easychat_params)

                save_data(user, {"LAST_SELECTED_BOT": bot_obj.pk}, easychat_bot_user.src,
                          channel, bot_obj.pk, is_cache=True)

                save_data(user, {"bot_id": str(bot_obj.pk)},
                          easychat_bot_user.src, channel, bot_obj.pk, is_cache=True)

                user.tree = None
                user.save(update_fields=['tree'])

                if bot_response:
                    bot_response["is_bot_switched"] = "true"
                    return True, bot_obj, bot_response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] check_bot_switch_logic_for_voice_based_channels: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            easychat_bot_user.user_id), 'source': str(easychat_bot_user.src), 'channel': str(easychat_bot_user.channel_name), 'bot_id': str(easychat_bot_user.bot_id)})

    return False, bot_obj, None


def check_bot_switch_logic(easychat_bot_user, easychat_params: EasyChatChannelParams):
    bot_obj = None
    try:
        channel = easychat_params.channel_obj
        message = easychat_bot_user.message
        src = easychat_bot_user.src
        bot_obj = easychat_bot_user.bot_obj
        channel_name = easychat_bot_user.channel_name

        if channel_name in ["Web", "iOS", "Android"]:
            return False, bot_obj, None

        if bot_obj and bot_obj.is_uat and not bot_obj.is_deleted:

            bot_response = None

            if channel_name in ["Alexa", "GoogleHome", "Voice"]:
                return check_bot_switch_logic_for_voice_based_channels(easychat_bot_user, easychat_params)

            message_list = message.split(' ')
            message_refined = ''

            owner_of_requested_bot = None
            for element in message_list:
                if '@getcogno.ai' in element:
                    owner_of_requested_bot = User.objects.filter(
                        username=element).first()
                    break

            message_list.remove(element)

            for element in message_list:
                if element.strip() != '':
                    message_refined += element + ' '

            message_refined = message_refined.strip()

            if owner_of_requested_bot != None and owner_of_requested_bot.is_bot_invocation_enabled:

                for chatbot_obj in Bot.objects.filter(users__in=[owner_of_requested_bot], is_deleted=False, is_uat=True):

                    if message_refined.lower() in chatbot_obj.get_invocation_name_lower_list():

                        bot_obj = chatbot_obj
                        easychat_bot_user.bot_obj = bot_obj
                        easychat_bot_user.bot_id = bot_obj.pk

                        user = set_user(easychat_bot_user.user_id, '', src,
                                        channel.name, bot_obj.pk, easychat_bot_user)
                        bot_response = build_channel_welcome_response(
                            easychat_bot_user, easychat_params)

                        save_data(user, {"LAST_SELECTED_BOT": bot_obj.pk}, src,
                                  channel, bot_obj.pk, is_cache=True)

                        save_data(user, {"bot_id": str(bot_obj.pk)},
                                  src, channel, bot_obj.pk, is_cache=True)

                        user.tree = None
                        user.save(update_fields=['tree'])

                        if bot_response:
                            bot_response["is_bot_switched"] = "true"

            if bot_response != None:
                return True, bot_obj, bot_response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] check_bot_switch_logic: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            easychat_bot_user.user_id), 'source': str(easychat_bot_user.src), 'channel': str(easychat_bot_user.channel_name), 'bot_id': str(easychat_bot_user.bot_id)})

    return False, bot_obj, None


def check_and_reset_user(user, bot, channel):
    try:
        if not bot.masking_enabled:
            return user

        masking_time = bot.masking_time

        user_last_msg_time = user.previous_message_date
        time_diff = (timezone.now() - user_last_msg_time).total_seconds()

        if time_diff > int(masking_time) * 60:
            user = clear_user_data(user.user_id, bot, channel)
            logger.info("user data cleared", extra={
                'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': 'None', 'channel': 'None', 'bot_id': str(bot.pk)})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_reset_user: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})

    return user


"""

This function returns set of words after running spell checker and split word on stem words

"""


def get_correct_words(stem_words, user_id, src, channel, bot_obj):
    final_words = set()
    bot_id = bot_obj.pk if bot_obj else ""
    _, global_word_dict = load_the_dictionary("", "", "", bot_id)
    for word in stem_words:
        logger.info("input word : %s", word, extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        if word in global_word_dict:
            final_words.add(word)
            continue

        correct_word = spell_checker(word, user_id, src, channel, bot_obj, bot_id)
        correct_word = {correct_word.strip()}

        # this logic was causing problem when a correctly spelled message without space in between was sent by user as spell checker was
        # not marking it incorrect
        # if word in correct_word:
        #     final_words.add(word)
        #     continue

        if correct_word in global_word_dict:
            final_words.add(word)
            continue

        logger.info("output word spellchecker : %s", correct_word, extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        split_word = lm.split(word)

        logger.info("output word wordninja : %s", split_word, extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        final_words = final_words | correct_word | set(split_word)

    return final_words


def open_file(file_dir, method):
    try:
        file_dir = settings.SECURE_MEDIA_ROOT + file_dir

        if '..' in file_dir:
            logger.error("user is trying to access this file: %s", str(file_dir), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("open_file: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return open(file_dir, method)


def get_multilingual_failure_response(bot_channel_obj, src):
    try:
        if src != "en":
            lang_obj = Language.objects.get(lang=src)
            language_tune_obj = LanguageTunedBotChannel.objects.filter(
                language=lang_obj, bot_channel=bot_channel_obj)
            if language_tune_obj.exists():
                return language_tune_obj[0].failure_message
        return bot_channel_obj.failure_message
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_multilingual_failure_response: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return bot_channel_obj.failure_message


def check_is_flow_terminated(message, user, easychat_params, easychat_bot_user, api_request_response_parameters, flow_termination_bot_response):

    bot_obj = easychat_bot_user.bot_obj
    src = easychat_bot_user.src
    channel = easychat_bot_user.channel_name
    bot_id = easychat_bot_user.bot_id

    try:
        easychat_flow_termination_initiated = False
        if Data.objects.filter(user=user, variable="easychat_flow_termination_initiated"):
            easychat_flow_termination_initiated = Data.objects.filter(
                user=user, variable="easychat_flow_termination_initiated").order_by('-pk')[0].get_value().replace('"', '')
            if easychat_flow_termination_initiated == 'true':
                save_data(user, {"easychat_flow_termination_initiated": "false"},
                          src, channel, bot_id, is_cache=True)

        if easychat_flow_termination_initiated == 'true' and str(message).strip().lower() == "yes":

            category_name = get_intent_category_name(
                user.tree, src, channel, bot_id, user)

            easychat_bot_response = EasyChatBotResponse(
                message=message, bot_response=flow_termination_bot_response, category_name=category_name)
            easychat_bot_response.intent_name = (str(message)).lower()
            easychat_bot_response.api_request_response_parameters = api_request_response_parameters
            easychat_params.is_manually_typed_query = False
            create_mis_dashboard_object(
                easychat_bot_user, easychat_params, easychat_bot_response)

            flow_termination_tree_pk = Data.objects.filter(
                user=user, variable="easychat_flow_termination_previous_tree").order_by('-pk')
            if flow_termination_tree_pk.count():
                tree = Tree.objects.filter(
                    pk=flow_termination_tree_pk[0].get_value().replace('"', ''))[0]

            last_flow_termination_message = Data.objects.filter(
                user=user, variable="easychat_flow_termination_message").order_by('-pk')
            if last_flow_termination_message.count():
                termination_message = last_flow_termination_message[0].get_value().replace(
                    '"', '')
                intent_name = get_last_identified_intent_name(
                    user, src, channel, bot_id)
                intent_obj = Intent.objects.get(
                    name=intent_name, bots__in=[bot_obj], is_deleted=False)
                channel_obj = easychat_params.channel_obj
                FlowTerminationData.objects.create(
                    user=user, intent=intent_obj, tree=tree, termination_message=termination_message, channel=channel_obj)
                flow_analytics_obj = FlowAnalytics.objects.filter(user=user).last()
                flow_analytics_obj.is_flow_aborted = True
                flow_analytics_obj.save(update_fields=['is_flow_aborted'])

            return True, easychat_flow_termination_initiated

        return False, easychat_flow_termination_initiated
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_is_flow_terminated! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        return False, easychat_flow_termination_initiated


def check_is_flow_termination_break(message, user, easychat_params, easychat_bot_user, api_request_response_parameters):

    bot_obj = easychat_bot_user.bot_obj
    src = easychat_bot_user.src
    channel = easychat_bot_user.channel_name
    bot_id = easychat_bot_user.bot_id

    try:
        flow_termination_bot_response, flow_termination_confirmation_display_message = get_multilingual_flow_termination_response(
            bot_obj, src)
        flow_termination_keywords = json.loads(
            bot_obj.flow_termination_keywords)["items"]
        display_messsage = flow_termination_confirmation_display_message
        for keyword in flow_termination_keywords:
            if str(keyword).strip().lower() == str(message).strip().lower() and (user.tree.children.all().exists()):

                # Saving a variable easychat_flow_termination_initiated, it
                # will help to move further in flow
                save_data(user, {
                          "easychat_flow_termination_initiated": "true"}, src, channel, bot_id, is_cache=True)
                save_data(user, {
                          "easychat_flow_termination_previous_tree": user.tree.pk}, src, channel, bot_id, is_cache=True)
                save_data(user, {
                          "easychat_flow_termination_message": message.strip().lower()}, src, channel, bot_id, is_cache=True)

                display_messsage = flow_termination_confirmation_display_message

                category_name = get_intent_category_name(
                    user.tree, src, channel, bot_id, user)
                easychat_bot_response = EasyChatBotResponse(
                    message=message, bot_response=flow_termination_confirmation_display_message, category_name=category_name)

                easychat_bot_response.intent_name = (str(message)).lower()
                easychat_bot_response.api_request_response_parameters = api_request_response_parameters
                easychat_params.is_manually_typed_query = False
                create_mis_dashboard_object(
                    easychat_bot_user, easychat_params, easychat_bot_response)

                return True, display_messsage

        return False, display_messsage
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_is_flow_termination_break! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        return False, display_messsage


def return_tree_if_flow_aborted(message, user, easychat_bot_user, easychat_params):

    bot_obj = easychat_bot_user.bot_obj
    src = easychat_bot_user.src
    channel = easychat_bot_user.channel_name

    try:
        easychat_abort_flow_initiated = False
        tree = None
        if Data.objects.filter(user=user, variable="easychat_abort_flow_initiated"):
            easychat_abort_flow_initiated = Data.objects.filter(
                user=user, variable="easychat_abort_flow_initiated").order_by('-pk')[0].get_value().replace('"', '')
            if easychat_abort_flow_initiated == 'true':
                if message.strip().lower() == "no":
                    easychat_params.is_intent_tree = True
                save_data(user, {"easychat_abort_flow_initiated": "false"},
                          src, channel, bot_obj.pk, is_cache=True)

        if easychat_abort_flow_initiated == 'true' and str(message).strip().lower() == "yes":
            abort_flow_intent_pk = Data.objects.filter(
                user=user, variable="easychat_abort_flow_called_intent").order_by('-pk')
            if abort_flow_intent_pk.count():
                abort_flow_intent_obj = Intent.objects.filter(
                    pk=abort_flow_intent_pk[0].get_value().replace('"', ''), channels=easychat_params.channel_obj)[0]
                save_data(user, {"LanguageSourceUser": str(src)},
                          src, channel, bot_obj.pk, is_cache=True)

                if abort_flow_intent_obj.is_feedback_required:
                    save_data(user, {
                        "is_feedback_required": True}, src, channel, bot_obj.pk, is_cache=True)

                abort_flow_tree_pk = Data.objects.filter(
                    user=user, variable="easychat_abort_flow_previous_tree").order_by('-pk')
                if abort_flow_tree_pk.count():
                    tree_obj = Tree.objects.filter(
                        pk=abort_flow_tree_pk[0].get_value().replace('"', ''))[0]

                easychat_bot_user.original_tree = abort_flow_intent_obj.tree
                tree = check_if_authentication_reqd(
                    abort_flow_intent_obj, bot_obj, user, channel, easychat_params.channel_obj, src)

                user.tree = tree
                user.save(update_fields=['tree'])

                last_abort_flow_message = Data.objects.filter(
                    user=user, variable="easychat_abort_flow_message").order_by('-pk')
                if last_abort_flow_message.count():
                    termination_message = last_abort_flow_message[0].get_value().replace(
                        '"', '')
                    intent_name = get_last_identified_intent_name(
                        user, src, channel, bot_obj.pk)
                    intent_obj = Intent.objects.get(
                        name=intent_name, bots__in=[bot_obj], is_deleted=False)
                    channel_obj = easychat_params.channel_obj
                    FlowTerminationData.objects.create(
                        user=user, intent=intent_obj, tree=tree_obj, termination_message=termination_message, channel=channel_obj)
                    flow_analytics_obj = FlowAnalytics.objects.filter(user=user).last()
                    flow_analytics_obj.is_flow_aborted = True
                    flow_analytics_obj.save(update_fields=['is_flow_aborted'])

                save_data(user, {"last_identified_intent_name":
                                 abort_flow_intent_obj.name}, src, channel, bot_obj.pk, is_cache=True)

                easychat_params.is_intent_tree = True
                # marking is intent_tree true so that in further flow it does
                # not do intent identification
        return user, tree, easychat_abort_flow_initiated

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error return_tree_if_flow_aborted! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        return user, tree, easychat_abort_flow_initiated


def check_if_abort_flow_initiated(easychat_bot_user, easychat_params, message, user, flow_termination_confirmation_display_message, previous_parent_tree, api_request_response_parameters):

    channel = easychat_bot_user.channel_name
    src = easychat_bot_user.src
    bot_obj = easychat_bot_user.bot_obj
    category_name = easychat_bot_user.category_name
    suggestion_not_entered = True
    try:
        if easychat_bot_user and easychat_bot_user.category_obj:
            category_obj = easychat_bot_user.category_obj
        else:
            category_obj = get_category_obj(bot_obj, category_name)
            easychat_bot_user.category_obj = category_obj
        is_attachment = check_if_attachment_in_message(user, Data)

        if is_attachment:
            return False, flow_termination_confirmation_display_message

        stem_words = get_stem_words_of_sentence(
            message, src, channel, user.user_id, bot_obj)
        stem_words.sort()
        temp_sentence = ' '.join(stem_words)
        stem_word_hash_value = hashlib.md5(
            temp_sentence.encode()).hexdigest()
        display_messsage = flow_termination_confirmation_display_message

        is_current_tree_hash = IntentTreeHash.objects.filter(
            hash_value=stem_word_hash_value, tree=user.tree, is_tree=True)

        hash_tree_pks = IntentTreeHash.objects.filter(
            hash_value=stem_word_hash_value).values_list("tree", flat=True)

        # suggested_intent_obj = None
        # #  if it is current tree hash then no need to check for suggested intent hashs
        # if not is_current_tree_hash.exists():
        #     suggested_intent_obj = return_intent_object_based_on_suggested_query_hash(
        #         user, bot_obj, message, channel, src)

        intent_obj = Intent.objects.none()
        if hash_tree_pks.exists() and not is_current_tree_hash.exists():
            intent_obj = Intent.objects.filter(tree__pk__in=hash_tree_pks, bots__in=[bot_obj], is_deleted=False, is_hidden=False)

        elif easychat_params.entered_suggestion:
            try:
                intent_obj = Intent.objects.filter(
                    pk=int(message))
                suggestion_not_entered = False
                
            except:
                pass
        
        if category_obj:
            intent_obj = intent_obj.filter(Q(category=category_obj) | Q(category__isnull=True))

        if intent_obj.count() == 1:

            intent_obj = intent_obj.first()
            if not suggestion_not_entered:
                message = intent_obj.name

            save_data(user, {
                "easychat_abort_flow_initiated": "true"}, src, channel, bot_obj.pk, is_cache=True)
            save_data(user, {
                "easychat_abort_flow_previous_tree": previous_parent_tree.pk}, src, channel, bot_obj.pk, is_cache=True)

            save_data(user, {
                "easychat_abort_flow_called_intent": intent_obj.pk}, src, channel, bot_obj.pk, is_cache=True)

            save_data(user, {
                "easychat_abort_flow_message": message.strip().lower()}, src, channel, bot_obj.pk, is_cache=True)

            category_name = get_intent_category_name(
                user.tree, src, channel, bot_obj.pk, user)

            easychat_bot_response = EasyChatBotResponse(
                message=message, bot_response=flow_termination_confirmation_display_message, category_name=category_name)

            easychat_bot_response.intent_name = (str(message)).lower()
            easychat_bot_response.api_request_response_parameters = api_request_response_parameters
            
            return True, display_messsage

        return False, display_messsage

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_if_abort_flow_initiated! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        return False, display_messsage


def check_if_attachment_in_message(user, Data):
    try:
        attachment = Data.objects.filter(
            user=user, variable="attached_file_src")

        if not attachment.exists():
            return False

        attachment = attachment.first().get_value()

        try:
            attachment = json.loads(attachment)
        except Exception:
            pass

        if not (attachment == "null" or attachment == None or attachment == ""):
            return True

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_if_attachment_in_message! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return False


def get_multilingual_flow_termination_response(bot_obj, src):
    try:
        flow_termination_bot_response = bot_obj.flow_termination_bot_response
        flow_termination_confirmation_display_message = bot_obj.flow_termination_confirmation_display_message

        if src == "en":
            return flow_termination_bot_response, flow_termination_confirmation_display_message
        lang_obj = Language.objects.get(lang=src)
        lang_bot_obj = LanguageTunedBot.objects.filter(
            bot=bot_obj, language=lang_obj)

        if lang_bot_obj.exists():
            lang_bot_obj = lang_bot_obj.first()
            return lang_bot_obj.flow_termination_bot_response, lang_bot_obj.flow_termination_confirmation_display_message

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get__multilingual_flow_termination_response! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return flow_termination_bot_response, flow_termination_confirmation_display_message


def get_bot_info_object(bot_obj):

    return BotInfo.objects.filter(bot=bot_obj).first()


def check_and_get_attachment_file_src(user):
    is_attachment_available = False
    attachment_data = ""
    try:
        attachment_data_obj = Data.objects.filter(user=user, variable="attached_file_src").first()
        if not attachment_data_obj:
            return is_attachment_available, attachment_data
        attachment_data_value = attachment_data_obj.get_value()
        attachment_data = json.loads(attachment_data_value)
        if attachment_data != "":
            is_attachment_available = True
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_user_attachament_details! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return is_attachment_available, attachment_data


def check_and_save_attachment_to_server(user, easychat_params, easychat_bot_user):

    file_key = ""
    try:
        is_attachment_available, attachment_data = check_and_get_attachment_file_src(user)

        easychat_params.is_attachment_available = is_attachment_available

        if not is_attachment_available:
            return

        if easychat_params.is_attachment_already_saved_on_server:
            return

        if easychat_params.is_video_recorder_allowed == True:
            if easychat_params.is_save_attachment_required == True:
                res = save_recorded_video(attachment_data)
                easychat_params.is_attachment_already_saved_on_server = True
                attachment = res
            else:
                attachment = None
        else:
            if easychat_params.is_save_attachment_required == True:
                res, file_key = save_file_to_server(
                    attachment_data, easychat_params.file_extention, EasyChatAppFileAccessManagement)
                attachment = res
                easychat_params.is_attachment_already_saved_on_server = True
                save_data(user, {"attached_file_path": str(attachment)},
                            easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_id, is_cache=True)
            else:
                attachment = None
        save_data(user, {"attachment": str(attachment)},
                  easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_id, is_cache=True)
        easychat_params.attachment = attachment
        easychat_params.file_key = file_key  

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_and_save_attachment_to_server! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
    

def get_user_attachament_details(user, easychat_params, easychat_bot_user, tree, response):
    
    is_attachment_successful = False
    language_template_obj = easychat_bot_user.language_template_obj
    try:
        check_and_save_attachment_to_server(user, easychat_params, easychat_bot_user)
        if easychat_params.is_attachment_available:

            if tree == None:
                response = success_bot_response(
                    successfull_file_upload_response(language_template_obj))
            else:
                is_attachment_successful = True
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_user_attachament_details! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    easychat_params.is_attachment_succesfull = is_attachment_successful
    return response


def update_and_get_form_assist_details(user, message, easychat_bot_user, easychat_params):
    logger_extra = easychat_bot_user.extra
    tree = None
    try:
        form_assist_obj = FormAssist.objects.get(pk=int(message))
        intent_obj = form_assist_obj.intent
        logger.info(f'Executing update_and_get_form_assist_details for {intent_obj.name}', extra=logger_extra)
        save_default_parameter_for_flow(
            intent_obj, user, easychat_params.channel_obj, easychat_bot_user.src, easychat_bot_user.bot_id)
        # Tree object
        tree = intent_obj.tree
        message = str(intent_obj.name)
        easychat_bot_user.message = message
        # Save user tree
        user.tree = tree
        user.save(update_fields=['tree'])
        return message, tree
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_and_get_form_assist_details! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        return message, tree


def ensure_element_tree(xlrd):
    try:
        xlrd.xlsx.ensure_elementtree_imported(False, None)
        xlrd.xlsx.Element_has_iter = True
    except Exception:
        pass


def check_and_trigger_livechat(message, bot_obj, suggestion_list, easychat_bot_user):
    try:
        if easychat_bot_user and easychat_bot_user.bot_info_obj:
            bot_info_obj = easychat_bot_user.bot_info_obj
        else:
            bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()

        lower_channel_name = easychat_bot_user.channel_name.strip().lower().replace(" ", "_")
        intent_icon_channel_choices_info = bot_info_obj.get_intent_icon_channel_choices_info()

        if bot_obj.is_livechat_enabled and bot_info_obj:

            if bot_info_obj.is_trigger_livechat_enabled:

                word_count = message.split()

                if len(word_count) >= bot_info_obj.autosuggest_livechat_word_limit:

                    intent_obj = bot_obj.livechat_default_intent

                    intent_icon = ""
                    if bot_info_obj.enable_intent_icon and ((lower_channel_name in intent_icon_channel_choices_info) and ("7" in intent_icon_channel_choices_info[lower_channel_name]) or (suggestion_list and "intent_icon" in suggestion_list[0] and suggestion_list[0]["intent_icon"])):
                        if intent_obj.build_in_intent_icon:
                            intent_icon = intent_obj.build_in_intent_icon.icon
                        else:
                            intent_icon = '<img width="40px" height="40px" src="' + intent_obj.intent_icon + '">'

                    suggestion_list.append({
                        "name": intent_obj.name,
                        "id": intent_obj.pk,
                        "tree_pk": intent_obj.tree.pk,
                        "intent_icon": intent_icon
                    })

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_and_trigger_livechat! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return suggestion_list


def get_web_page_source_details(easychat_params):
    try:
        web_page_source = ""
        bot_web_page = ""

        if easychat_params.channel_name == "Web":
            web_page_source = easychat_params.web_page_source
            bot_web_page = easychat_params.window_location

        return web_page_source, bot_web_page
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_web_page_source_details! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_profanity_text_response(easychat_bot_user, profanity_response):

    try:
        bot_obj = easychat_bot_user.bot_obj
        channel = easychat_bot_user.channel_name

        if easychat_bot_user and easychat_bot_user.bot_info_obj:
            bot_info_obj = easychat_bot_user.bot_info_obj
        else:
            bot_info_obj = BotInfo.objects.get(bot=bot_obj)

        lower_channel_name = channel.strip().lower().replace(" ", "_")
        intent_icon_channel_choices_info = bot_info_obj.get_intent_icon_channel_choices_info()        

        if not bot_obj.is_livechat_enabled:
            return profanity_response

        profanity_bot_response_obj = ProfanityBotResponse.objects.filter(
            bot=bot_obj).first()

        if not profanity_bot_response_obj:
            return profanity_response

        if not profanity_bot_response_obj.is_suggest_livechat_for_profanity_words_enabled:
            return profanity_response

        profanity_response_text = profanity_bot_response_obj.profanity_response_text

        if easychat_bot_user.src != "en":
            lang_bot_obj = LanguageTunedBot.objects.filter(
                bot=bot_obj, language=easychat_bot_user.selected_language).first()

            if lang_bot_obj and lang_bot_obj.profanity_bot_response != "":
                profanity_response_text = lang_bot_obj.profanity_bot_response

        validation_obj = EasyChatInputValidation()
        profanity_response["response"]["speech_response"]["text"] = BeautifulSoup(validation_obj.remo_html_from_string(profanity_response_text)).text.strip()
        profanity_response["response"]["speech_response"][
            "reprompt_text"] = validation_obj.remo_html_from_string(profanity_response_text)
        profanity_response["response"]["text_response"][
            "text"] = profanity_response_text

        if profanity_bot_response_obj.add_livechat_as_quick_recommendation:
            intent_obj = bot_obj.livechat_default_intent
            suggestion_list = []
            intent_icon = ""

            if bot_info_obj.enable_intent_icon and (lower_channel_name in intent_icon_channel_choices_info) and ("7" in intent_icon_channel_choices_info[lower_channel_name]):
                if intent_obj.build_in_intent_icon:
                    intent_icon = intent_obj.build_in_intent_icon.icon
                else:
                    intent_icon = '<img width="40px" height="40px" src="' + intent_obj.intent_icon + '">'

            suggestion_list.append({
                "name": get_multilingual_intent_name(intent_obj, easychat_bot_user.src), 
                "id": intent_obj.pk,
                "intent_icon": intent_icon
            })
            profanity_response["response"]["recommendations"] = suggestion_list

        elif profanity_bot_response_obj.trigger_livechat_intent:

            modes = profanity_response["response"]["text_response"]["modes"]
            modes["is_livechat"] = "true"
            profanity_response["response"]["text_response"]["modes"] = modes

            intent_obj = bot_obj.livechat_default_intent

            livechat_notification = ""

            if intent_obj.tree and intent_obj.tree.response:
                sentence = intent_obj.tree.response.sentence
                sentence = json.loads(sentence)
                livechat_notification = sentence["items"][0]["text_response"]

            if livechat_notification != "":
                profanity_response["response"]["text_response"][
                    "text"] += "$$$" + str(livechat_notification)

            if channel not in ["Web", "iOS", "Android"] and "is_livechat" in modes and modes["is_livechat"] == "true":

                is_welcome_msg = False
                livechat_notification, is_welcome_msg = create_and_enable_livechat(
                    easychat_bot_user.user_id, "-1", channel, bot_obj, easychat_bot_user.original_message)

                if livechat_notification != "":
                    profanity_response["response"]["text_response"][
                        "text"] += "$$$" + str(livechat_notification)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': str(bot_obj.pk)})

    return profanity_response


def check_for_profanity_filter(app_config, easychat_bot_user, easychat_params, user, api_request_response_parameters):

    is_profanity_detected = False
    profanity_filter_response = {}

    message = easychat_bot_user.message
    bot_obj = easychat_bot_user.bot_obj
    language_template_obj = easychat_bot_user.language_template_obj
    channel = easychat_bot_user.channel_name
    src = easychat_bot_user.src
    bot_id = easychat_bot_user.bot_id
    logger_extra = easychat_bot_user.extra

    try:
        if easychat_params.is_form_assist == True:
            return is_profanity_detected, profanity_filter_response

        pf = ProfanityFilter()
        if not pf.is_clean(message, easychat_bot_user.bot_info_obj):

            is_profanity_detected = True

            profanity_filter_response = build_abuse_detected_response(
                user, bot_obj, message, channel, src, language_template_obj)

            profanity_filter_response = update_profanity_text_response(
                easychat_bot_user, profanity_filter_response)

            user_message = pf.censor(message, easychat_bot_user.bot_info_obj)

            bot_response = profanity_filter_response[
                "response"]["text_response"]["text"]

            easychat_params.form_data_widget = ""

            easychat_bot_response = EasyChatBotResponse(
                message=user_message, bot_response=bot_response)
            easychat_bot_response.intent_name = "Profanity Bot Response"
            easychat_bot_response.response_json = json.dumps(
                profanity_filter_response)
            create_mis_dashboard_object(
                easychat_bot_user, easychat_params, easychat_bot_response)

            save_data(user, {"last_suggested_query_hash_obj_pk": "none"},
                      src, channel, bot_obj.pk, is_cache=True)

            return is_profanity_detected, profanity_filter_response

        user_message = message

        autocorrect_response = return_autocorrect_response(
            app_config, user, user_message, logger_extra, bot_id, src, channel)

        if user_message != autocorrect_response:

            is_profanity_detected = True

            save_data(user, {"last_suggested_query_hash_obj_pk": "none"},
                      src, channel, bot_obj.pk, is_cache=True)

            return is_profanity_detected, build_autocorrect_response(user, bot_obj, user_message, message, src, channel, language_template_obj)

        return is_profanity_detected, profanity_filter_response

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_for_profanity_filter! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return False, {}


def return_emoji_response(easychat_bot_user, easychat_params, user, emoji_sentiment_detected, message, broken_mail_dump):

    try:
        bot_id = "None"
        bot_obj = easychat_bot_user.bot_obj
        bot_id = bot_obj.pk
        channel = easychat_bot_user.channel_name
        src = easychat_bot_user.src
        emoji_detected_response = build_emoji_detected_response(
            user, bot_obj, message, src, emoji_sentiment_detected, EmojiBotResponse, LanguageTunedBot, Language)

        user_message = message

        bot_response = emoji_detected_response[
            "response"]["text_response"]["text"]

        easychat_params.form_data_widget = ""
        easychat_bot_response = EasyChatBotResponse(
            message=user_message, bot_response=bot_response)
        easychat_params.match_percentage = 100
        easychat_bot_response.intent_name = "Emoji Bot Response"
        easychat_bot_response.response_json = json.dumps(
            emoji_detected_response)
        create_mis_dashboard_object(
            easychat_bot_user, easychat_params, easychat_bot_response)

        save_data(user, {"last_suggested_query_hash_obj_pk": "none"},
                  src, channel, bot_id, is_cache=True)

        return emoji_detected_response

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_message = "Error return_emoji_response! {} at {}".format(str(e), str(exc_tb.tb_lineno))
        logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        
        broken_mail_dump["error"] = error_message
        check_and_send_broken_bot_mail(
            bot_id, channel, easychat_params.window_location, json.dumps(broken_mail_dump))
        return build_internal_server_error_response(
            easychat_bot_user.user_id, easychat_bot_user.src, channel, bot_id, easychat_bot_user.language_template_obj)


def get_easychat_bot_user_obj(user_id, bot_id, bot_name, message, src, original_message, channel):
    try:
        easychat_bot_user = EasyChatBotUser(
            bot_name=bot_name, message=message, src=src, original_message=original_message)
        easychat_bot_user.user_id = user_id
        easychat_bot_user.bot_id = bot_id
        easychat_bot_user.channel_name = channel
        easychat_bot_user.selected_language = Language.objects.filter(
            lang=src).first()

        return easychat_bot_user
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_easychat_bot_user_obj! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def store_channel_params_in_data_models(user, easychat_bot_user, easychat_params, channel_params):

    logger_extra = easychat_bot_user.extra
    src = easychat_bot_user.src
    bot_id = easychat_bot_user.bot_id
    channel = easychat_bot_user.channel_name
    original_message = easychat_bot_user.original_message

    try:
        save_data(user, channel_params, src,
                  channel, bot_id, is_cache=True)

        save_data(user, {"EasyChatChannel": str(channel)},
                  src, channel, bot_id, is_cache=True)

        save_data(user, {"EasyChatUserID": str(user.user_id)},
                  src, channel, bot_id, is_cache=True)

        save_data(user, {"original_message": str(original_message)},
                  src, channel, bot_id, is_cache=True)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error is storing channel params %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)


def get_parsed_suggestion_list(message, easychat_bot_user, suggestion_list):
    try:
        suggestion_list = check_and_trigger_livechat(
            message, easychat_bot_user.bot_obj, suggestion_list, easychat_bot_user)

        # If other than english, then translate suggestions
        translated_suggestion_list = []
        if easychat_bot_user.src != "en":
            for suggestion in suggestion_list:
                translated_suggestion_list.append(get_translated_text(
                    suggestion, easychat_bot_user.src, EasyChatTranslationCache))

            suggestion_list = translated_suggestion_list
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_parsed_suggestion_list! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra=easychat_bot_user.extra)

    return suggestion_list


def updated_response_to_send_after_language_confirmation(response_to_send, easychat_bot_user):
    response = response_to_send
    try:
        if easychat_bot_user.is_bot_language_change_confirmed:
            response["response"][
                "is_bot_language_change_confirmed"] = easychat_bot_user.is_bot_language_change_confirmed
            response["response"]["language_src"] = easychat_bot_user.src

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_parsed_suggestion_list! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra=easychat_bot_user.extra)

    return response


def build_auto_language_detected_response(user, detected_language, easychat_bot_user, easychat_params):
    bot_obj = easychat_bot_user.bot_obj
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:

        lang_name, language_obj = get_language_display_in_english_from_code(
            detected_language)
        suggestion_list = []
        if is_this_language_supported_by_bot(bot_obj, detected_language, easychat_params.channel_obj):

            language_template_obj = RequiredBotTemplate.objects.get(
                bot=bot_obj, language=language_obj)

            text_response = language_template_obj.get_bot_auto_detected_language_supported_text()

            yes_text, no_text = language_template_obj.get_yes_and_no_text()

            if detected_language != "en":
                yes_text = yes_text + " (Yes)"
                no_text = no_text + " (No)"

            suggestion_list = [yes_text, no_text]
        else:
            list_of_langs = get_list_of_names_of_supported_languages(
                bot_obj, easychat_params.channel_obj)
            text_response = easychat_bot_user.language_template_obj.get_bot_auto_detected_language_not_supported_text(
                lang_name + ", " + lang_name, list_of_langs)
            if easychat_bot_user.channel_name in ["WhatsApp"]:
                language_not_found_text = easychat_bot_user.language_template_obj.auto_language_detection_text.split("$$$")[1]
                text_response = text_response.replace(language_not_found_text.format(lang_name + ", " + lang_name) + "<br> <ul>", language_not_found_text.format(lang_name + ", " + lang_name) + "\n<br><ul>")

        response["is_auto_detected_language_response"] = True
        response["detected_language"] = detected_language
        response["user_id"] = user.user_id
        response["bot_id"] = bot_obj.pk
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"][
            "is_text_to_speech_required"] = bot_obj.is_text_to_speech_required
        response["response"]["recommendations"] = suggestion_list

        response["response"]["tooltip_response"] = ""
        response["response"]["speech_response"][
            "text"] = BeautifulSoup(str(text_response)).text.strip()
        response["response"]["speech_response"][
            "reprompt_text"] = str(text_response)
        response["response"]["text_response"][
            "text"] = str(text_response)

        response["response"]["easy_search_results"] = []
        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
        response["response"]["is_response_to_be_language_processed"] = False

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: build_auto_language_detected_response %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': str(easychat_bot_user.src), 'channel': str(easychat_bot_user.channel_name), 'bot_id': 'None'})
        response["status_code"] = 500
        response["status_message"] = str(e)
    return response


def is_this_language_supported_by_bot(bot_obj, lang_code, channel_obj):

    is_lang_supported = False
    try:
        bot_channel = BotChannel.objects.filter(
            bot=bot_obj, channel=channel_obj).first()
        supported_language = bot_channel.languages_supported.all().filter(lang=lang_code)

        is_lang_supported = supported_language.exists()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_this_language_supported_by_bot! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return is_lang_supported


def get_language_display_in_english_from_code(lang_code):
    display = lang_code
    lang_obj = None
    try:
        lang_obj = Language.objects.filter(lang=lang_code).first()
        display = lang_obj.name_in_english

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_language_display_in_english_from_code! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return display, lang_obj


def get_list_of_names_of_supported_languages(bot_obj, channel_obj):

    list_of_langs = []

    try:
        bot_channel = BotChannel.objects.filter(
            bot=bot_obj, channel=channel_obj).first()

        for lang in bot_channel.languages_supported.all():
            list_of_langs.append(lang.display)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_language_display_in_english_from_code! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        list_of_langs.append("English")

    return list_of_langs


def check_if_auto_language_detection_to_be_checked(bot_channel, easychat_params, easychat_bot_user, user):

    is_language_detection_enabled = False
    bot_obj = easychat_bot_user.bot_obj
    try:
        #  no need for language detection if user is in flow
        if user.tree != None and user.tree.children.filter(is_deleted=False).count() > 0:

            return is_language_detection_enabled

        # if language change confirmation is done no need to detect language
        if easychat_bot_user.is_bot_language_change_confirmed:

            return is_language_detection_enabled
        # if language auto detection is enabled then only auto detection is
        # required
        if bot_channel.is_language_auto_detection_enabled:

            if bot_obj.languages_supported.all().count() > 1:

                return True

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_if_auto_language_detection_to_be_checked! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return is_language_detection_enabled


def is_auto_language_detection_to_be_checked_from_data_model(user, easychat_bot_user, easychat_params):

    is_auto_detection_required = True
    try:
        is_auto_language_change_detection_to_be_checked = Data.objects.filter(
            user=user, variable="is_auto_language_change_detection_to_be_checked").order_by('-pk')

        if is_auto_language_change_detection_to_be_checked:

            is_auto_language_change_detection_to_be_checked = is_auto_language_change_detection_to_be_checked.first(
            ).get_value().replace('"', '')

            if is_auto_language_change_detection_to_be_checked == 'false':
                is_auto_detection_required = False
        else:
            save_data(user, {"is_auto_language_change_detection_to_be_checked": True},
                      easychat_bot_user.src, easychat_params.channel_name, easychat_bot_user.bot_id, is_cache=True)
            # creating obj if not already exists
            is_auto_detection_required = True

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_auto_language_detection_to_be_checked_from_data_model! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return is_auto_detection_required


def check_if_auto_language_change_detected(user, message, easychat_bot_user, easychat_params):

    is_auto_language_change_detected = False
    detected_language = easychat_bot_user.src
    channel_obj = easychat_params.channel_obj

    try:
        if easychat_bot_user.bot_channel_obj:
            bot_channel = easychat_bot_user.bot_channel_obj
        else:
            bot_channel = BotChannel.objects.filter(
                bot=easychat_bot_user.bot_obj, channel=channel_obj).first()
            easychat_bot_user.bot_channel_obj = bot_channel

        if not check_if_auto_language_detection_to_be_checked(bot_channel, easychat_params, easychat_bot_user, user):

            save_data(user, {"is_auto_language_change_detected": is_auto_language_change_detected},
                      easychat_bot_user.src, easychat_params.channel_name, easychat_bot_user.bot_id, is_cache=True)

            return is_auto_language_change_detected, detected_language

        # if sticky message is called or suggestion is entered no need to check
        # for language detection
        if easychat_params.entered_suggestion or easychat_params.is_sticky_message or easychat_params.is_widget_data:

            save_data(user, {"is_auto_language_change_detected": is_auto_language_change_detected},
                      easychat_bot_user.src, easychat_params.channel_name, easychat_bot_user.bot_id, is_cache=True)

            return is_auto_language_change_detected, detected_language

        if not is_auto_language_detection_to_be_checked_from_data_model(user, easychat_bot_user, easychat_params):

            save_data(user, {"is_auto_language_change_detected": is_auto_language_change_detected},
                      easychat_bot_user.src, easychat_params.channel_name, easychat_bot_user.bot_id, is_cache=True)

            return is_auto_language_change_detected, detected_language

        is_auto_language_change_detected, detected_language = get_detected_language_from_text(
            easychat_bot_user.src, message, easychat_bot_user.bot_info_obj, WhitelistedEnglishWords)

        save_data(user, {"is_auto_language_change_detected": is_auto_language_change_detected},
                  easychat_bot_user.src, easychat_params.channel_name, easychat_bot_user.bot_id, is_cache=True)

        if is_auto_language_change_detected:

            save_data(user, {"message_for_which_auto_language_was_detected": str(message)},
                      easychat_bot_user.src, easychat_params.channel_name, easychat_bot_user.bot_id, is_cache=True)

            save_data(user, {"previously_detected_language": str(detected_language)},
                      easychat_bot_user.src, easychat_params.channel_name, easychat_bot_user.bot_id, is_cache=True)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_if_auto_language_change_detected! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra=easychat_bot_user.extra)
    return is_auto_language_change_detected, detected_language


def get_message_and_src_if_auto_language_change_confirmed(user, message, easychat_bot_user, easychat_params):
    final_message = message
    src = easychat_bot_user.src
    channel_obj = easychat_params.channel_obj
    easychat_bot_user.is_bot_language_change_confirmed = False
    initial_message = easychat_bot_user.original_message
    logger.info('Into get_message_and_src_if_auto_language_change_confirmed...', extra=easychat_bot_user.extra)
    try:
        if easychat_bot_user.bot_channel_obj:
            bot_channel = easychat_bot_user.bot_channel_obj
        else:
            bot_channel = BotChannel.objects.filter(
                bot=easychat_bot_user.bot_obj, channel=channel_obj).first()
            easychat_bot_user.bot_channel_obj = bot_channel
        if not check_if_auto_language_detection_to_be_checked(bot_channel, easychat_params, easychat_bot_user, user):

            return final_message, src

        is_auto_language_change_detected = Data.objects.filter(
            user=user, variable="is_auto_language_change_detected").order_by('-pk')

        if not is_auto_language_change_detected:
            return final_message, src

        is_auto_language_change_detected = is_auto_language_change_detected.first(
        ).get_value().replace('"', '')
        # translating message to english because yes no confirmation will be in
        # detected language to check we have to translate it back to english
        if is_auto_language_change_detected == 'true':
            message = translate_given_text_to_english(message)
            easychat_bot_user.translated_message = None
            if message.lower().strip() == "yes" or "(yes)" in initial_message.lower().strip():

                src = Data.objects.filter(
                    user=user, variable="previously_detected_language").order_by('-pk').first().get_value().replace('"', '')

                final_message = Data.objects.filter(
                    user=user, variable="message_for_which_auto_language_was_detected").order_by('-pk').first().get_value()
                try:
                    final_message = json.loads(final_message)
                except:
                    pass
                easychat_bot_user.original_message = final_message
                final_message = translitrate_text_to_target_language(
                    final_message, src)

                # translitarting message to target language for better
                # translation accuracy
                easychat_bot_user.is_bot_language_change_confirmed = True

            # do we have to check for language auto detection again in this
            # session
            if message.lower().strip() == "no" or "(no)" in initial_message.lower().strip():

                final_message = Data.objects.filter(
                    user=user, variable="message_for_which_auto_language_was_detected").order_by('-pk').first().get_value()

                try:
                    final_message = json.loads(final_message)
                except:
                    pass
                easychat_bot_user.original_message = final_message

                save_data(user, {"is_auto_language_change_detection_to_be_checked": False},
                          easychat_bot_user.src, easychat_params.channel_name, easychat_bot_user.bot_id, is_cache=True)

        if is_auto_language_detection_to_be_checked_from_data_model(user, easychat_bot_user, easychat_params):
            save_data(user, {"is_auto_language_change_detection_to_be_checked": True},
                      easychat_bot_user.src, easychat_params.channel_name, easychat_bot_user.bot_id, is_cache=True)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_message_and_src_if_auto_language_change_confirmed! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra=easychat_bot_user.extra)

    logger.info("EXITING get_message_and_src_if_auto_language_change_confirmed... with msg and src" + str(final_message) + str(src), extra=easychat_bot_user.extra)

    return final_message, src


def get_auto_detected_message_and_src_for_other_channels(user, message, easychat_bot_user, easychat_params):

    final_message = message
    src = easychat_bot_user.src
    channel_obj = easychat_params.channel_obj
    easychat_bot_user.is_bot_language_change_confirmed = False
    is_language_not_found_response_to_be_send = False

    logger.info("Into get_auto_detected_message_and_src_for_other_channels...", extra=easychat_bot_user.extra)

    try:
        if easychat_bot_user.bot_channel_obj:
            bot_channel = easychat_bot_user.bot_channel_obj
        else:
            bot_channel = BotChannel.objects.filter(
                bot=easychat_bot_user.bot_obj, channel=channel_obj).first()
            easychat_bot_user.bot_channel_obj = bot_channel

        if not check_if_auto_language_detection_to_be_checked(bot_channel, easychat_params, easychat_bot_user, user):

            return final_message, src, is_language_not_found_response_to_be_send

        is_auto_language_change_detected, detected_language = get_detected_language_from_text(
            src, message, easychat_bot_user.bot_info_obj, WhitelistedEnglishWords)

        if detected_language == "und":

            return final_message, src, is_language_not_found_response_to_be_send

        if is_auto_language_change_detected:

            src = detected_language

            if not is_this_language_supported_by_bot(easychat_bot_user.bot_obj, detected_language, channel_obj):
                is_language_not_found_response_to_be_send = True

            else:
                final_message = translitrate_text_to_target_language(
                    final_message, src)
                # translitarting message to target language for better
                # translation accuracy
                easychat_bot_user.is_bot_language_change_confirmed = True
                easychat_bot_user.translated_message = None
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_message_and_src_if_auto_language_change_confirmed! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra=easychat_bot_user.extra)

    logger.info("EXITING get_auto_detected_message_and_src_for_other_channels... with msg and src" + str(final_message) + str(src), extra=easychat_bot_user.extra)
    return final_message, src, is_language_not_found_response_to_be_send


def set_language_for_whatsapp_welcome_response(user, src, easychat_bot_user, easychat_params):
    try:
        bot_channel = BotChannel.objects.filter(
            bot=easychat_bot_user.bot_obj, channel=easychat_params.channel_obj).first()

        language_objs = bot_channel.languages_supported.filter(lang=src)

        if not language_objs.exists():
            language_objs = Language.objects.filter(lang="en")

        user.selected_language = language_objs.first()
        user.save()
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error set_language_for_whatsapp_welcome_response! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_broken_mail_dump(user_id, bot_id, bot_name, channel, original_message):
    try:
        mail_dump = {}
        mail_dump["user_id"] = user_id
        mail_dump["bot_id"] = bot_id
        mail_dump["bot_name"] = bot_name
        mail_dump["channel"] = channel
        mail_dump["original_message"] = original_message
        return mail_dump
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error set_language_for_whatsapp_welcome_response! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        return {}


def check_for_query_warning_or_block_response(bot_obj, channel, user, easychat_params, easychat_bot_user, original_message, src, response):
    response_to_return = False
    try:
        if channel == "WhatsApp":
            query_status = check_query_for_warning_or_block(bot_obj.pk, easychat_params.session_id, original_message)
            if query_status != "ok":
                whatsapp_spam_response = build_whatsapp_spam_response(
                    user, easychat_params.channel_obj, bot_obj, src, query_status,
                    BlockConfig, BotChannel, Language, LanguageTunedBotChannel)
                bot_response = whatsapp_spam_response["response"]["text_response"]["text"]
                spam_intent_name = whatsapp_spam_response["intent_name"]
                easychat_bot_response = EasyChatBotResponse(
                    message=original_message, bot_response=bot_response)
                easychat_bot_response.intent_name = spam_intent_name
                easychat_bot_response.response_json = json.dumps(
                    whatsapp_spam_response)
                create_mis_dashboard_object(
                    easychat_bot_user, easychat_params, easychat_bot_response)

                save_data(user, {"last_suggested_query_hash_obj_pk": "none"},
                            src, channel, bot_obj.pk, is_cache=True)
                save_data(user, {"is_feedback_required": False}, src,
                            channel, bot_obj.pk, is_cache=True)
                save_data(user, {"is_intent_feedback_asked": False}, src,
                            channel, bot_obj.pk, is_cache=True)

                if response and response["response"].get("is_whatsapp_welcome_response", False) == True:
                    response["whatsapp_spam_response"] = whatsapp_spam_response
                else:
                    response = whatsapp_spam_response

                response_to_return = True
            if response and response["response"].get("is_whatsapp_welcome_response", False) == True:
                response_to_return = True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_for_query_warning_or_block_response! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
    return response_to_return, response


def save_initial_intent_query_details_in_mis(user, session_id):
    try:
        initial_intent_mis_params_data_obj = Data.objects.filter(user=user, variable="initial_intent_mis_params").first()
        if initial_intent_mis_params_data_obj:
            initial_intent_mis_params = json.loads(initial_intent_mis_params_data_obj.get_value())
            initial_intent_mis_params["session_id"] = session_id
            mis_obj = MISDashboard(**initial_intent_mis_params, date=initial_intent_mis_params_data_obj.cached_datetime)
            mis_obj.save()

            initial_intent_mis_params_data_obj.delete()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_initial_intent_query_details_in_mis! %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def save_initial_intent_flow_analytics_data(user):
    try:
        initial_intent_flow_analytics_data_obj = Data.objects.filter(user=user, variable="initial_intent_flow_analytics_data").first()
        if initial_intent_flow_analytics_data_obj:
            initial_intent_flow_analytics_data = json.loads(initial_intent_flow_analytics_data_obj.get_value())
            for data in initial_intent_flow_analytics_data:
                flow_analytics_obj = FlowAnalytics(**data, created_time=initial_intent_flow_analytics_data_obj.cached_datetime)
                flow_analytics_obj.save()

            initial_intent_flow_analytics_data_obj.delete()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_initial_intent_flow_analytics_data! %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def save_initial_intent_livechat_analytics_data(user, easychat_bot_user, easychat_params):
    try:
        initial_livechat_analytics_data_obj = Data.objects.filter(user=user, variable="save_initial_livechat_analytics").first()
        if initial_livechat_analytics_data_obj:
            initial_livechat_analytics_data = json.loads(initial_livechat_analytics_data_obj.get_value())
            if initial_livechat_analytics_data.strip().lower() == "true":
                save_livechat_analytics_details(easychat_bot_user.bot_obj, easychat_params.channel_obj)

            initial_livechat_analytics_data_obj.delete()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_initial_intent_livechat_analytics_data! %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


################################# Execute query starts ###################


def execute_query(user_id,
                  bot_id,
                  bot_name,
                  message,
                  src,
                  channel,
                  channel_params,
                  original_message):

    broken_mail_dump = create_broken_mail_dump(
        user_id, bot_id, bot_name, channel, original_message)
    validation_obj = EasyChatInputValidation()
    livechat_message = message
    message = validation_obj.remo_complete_html_and_unwanted_characters(
        message, int(bot_id))
    original_message = validation_obj.remo_complete_html_and_unwanted_characters(
        original_message, int(bot_id))

    easychat_bot_user = get_easychat_bot_user_obj(
        user_id, bot_id, bot_name, message, src, original_message, channel)

    channel_params = json.loads(channel_params)
    easychat_bot_user.category_name = channel_params.get("category_name")

    easychat_params = EasyChatChannelParams(channel_params, user_id)

    logger_extra = easychat_bot_user.extra
    response = copy.deepcopy(DEFAULT_RESPONSE)
    response["status_code"] = "200"
    response["status_message"] = "SUCCESS"
    try:
        logger.info("Started execute_query...", extra=logger_extra)
        if channel not in ["Web", "Android", "iOS"] and check_for_livechat(easychat_bot_user):
            channel_params["easychat_params"] = easychat_params
            channel_params["easychat_bot_user"] = easychat_bot_user
            livechat_validation_obj = LiveChatInputValidation()
            livechat_message = livechat_validation_obj.remove_malicious_chars(livechat_message)
            return get_livechat_response(user_id, livechat_message, channel, bot_id, channel_params)

        is_form_assist = easychat_params.is_form_assist
        message = is_campaign_link_enabled(
            channel_params, message, logger_extra, Intent)

        easychat_bot_user.message = message

        app_config = Config.objects.all()[0]

        channel_obj = get_channel_obj(str(channel), Channel, logger_extra)

        if channel_obj == None:
            # if channel object is None, return
            broken_mail_dump["error"] = "Channel does not exists."
            check_and_send_broken_bot_mail(
                bot_id, "None", easychat_params.window_location, json.dumps(broken_mail_dump))
            return invalid_channel_response(user_id, src, channel, bot_id)

        easychat_params.channel_obj = channel_obj
        easychat_params.channel_name = channel_obj.name

        bot_obj = get_bot_object_and_save_last_query_time(user_id,
                                                          bot_id, bot_name, Bot, logger_extra)

        if bot_obj == None:
            # if bot object is None, return
            broken_mail_dump["error"] = "Bot does not exists."
            check_and_send_broken_bot_mail(
                bot_id, channel, easychat_params.window_location, json.dumps(broken_mail_dump))
            return build_bot_not_found_response(user_id, src, channel, bot_id)

        easychat_bot_user.bot_obj = bot_obj
        bot_info_obj = get_bot_info_object(bot_obj)
        easychat_bot_user.bot_info_obj = bot_info_obj
        # Save initial intent related data

        # Getting language template object

        language_template_obj = RequiredBotTemplate.objects.filter(
            bot=bot_obj, language=Language.objects.filter(lang=src).first()).first()

        easychat_bot_user.language_template_obj = language_template_obj
        user = set_user(user_id, message, src, channel, bot_id, easychat_bot_user)

        easychat_bot_user.user = user

        if easychat_params.is_first_query and bot_obj.initial_intent and not easychat_params.is_initial_intent:
            save_initial_intent_query_details_in_mis(user, easychat_params.session_id)
            save_initial_intent_flow_analytics_data(user)
            save_initial_intent_livechat_analytics_data(user, easychat_bot_user, easychat_params)

        if channel not in ["Web", "Android", "iOS", "WhatsApp"]:
            easychat_params.session_id = get_or_generate_session_id(user)
        logger_extra['user_id'] = str(user.user_id)
        easychat_bot_user.extra['user_id'] = str(user.user_id)

        user = save_user_flow_details(user, channel_obj, logger_extra)
        user = check_and_reset_user(user, bot_obj, channel)

        # user = get_previous_bot_id(user, bot_id, channel, logger_extra, Data)
        # Save/Update time spent by user on the chatbot.

        web_page_source, bot_web_page = get_web_page_source_details(
            easychat_params)

        save_and_update_time_spent_user(
            user_id, easychat_bot_user, logger_extra, TimeSpentByUser, bot_web_page, web_page_source)
        user, message, is_whatsapp_nps_rating, is_whatsapp_nps_comment, whatsapp_rating = whatsapp_nps_update(
            user, message, bot_obj, logger_extra, Feedback)
        user, is_sticky_message_called_in_flow, previous_parent_tree = is_sticky_message_enabled(
            user, channel_params, logger_extra)
        easychat_params.is_sticky_message_called_in_flow = is_sticky_message_called_in_flow

        if user == None:
            # return if user is None.
            logger_extra['user_id'] = ''
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "Error in identification of user at {}".format(str(exc_tb.tb_lineno))
            logger.error(error_message, extra=logger_extra)
            broken_mail_dump["error"] = error_message
            check_and_send_broken_bot_mail(
                bot_id, channel, easychat_params.window_location, json.dumps(broken_mail_dump))
            return build_internal_server_error_response(user_id, src, channel, bot_id, language_template_obj)

        bot_switch_status, selected_bot_obj, response = check_bot_switch_logic(
            easychat_bot_user, easychat_params)

        if bot_switch_status:
            logger.info("User has requested to switch bot", extra=logger_extra)
            return response
        else:
            logger.info("Currently user is chatting with:" + str(selected_bot_obj.pk), extra=logger_extra)
            bot_obj = selected_bot_obj

        easychat_bot_user.bot_obj = bot_obj
        easychat_bot_user.bot_obj.bot_id = bot_obj.pk

        easychat_bot_user.bot_channel_obj = BotChannel.objects.filter(bot=easychat_bot_user.bot_obj, channel=easychat_params.channel_obj).first()

        is_message_updated, is_form_assist, message = is_lead_generation_enabled(
            is_form_assist, app_config, message, user_id, src, channel, bot_id, bot_obj, logger_extra)
        
        if is_message_updated:
            easychat_bot_user.translated_message = None

        easychat_params.is_form_assist = is_form_assist
        if "is_failure_response_required" in channel_params and channel_params["is_failure_response_required"]:
            if user.tree is None or user.tree.children.filter(is_deleted=False).count() == 0:
                if easychat_bot_user and easychat_bot_user.category_obj:
                    category_obj = easychat_bot_user.category_obj
                else:
                    category_obj = get_category_obj(bot_obj, easychat_bot_user.category_name)
                response = build_channel_failure_response(
                    response, easychat_bot_user, bot_obj, channel_obj, bot_info_obj, category_obj, message, user, language_template_obj, src, easychat_params)
                return response

        if channel == "WhatsApp" and easychat_params.is_new_user and not easychat_bot_user.bot_channel_obj.return_initial_query_response and not user.selected_language:

            set_language_for_whatsapp_welcome_response(
                user, src, easychat_bot_user, easychat_params)

            response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)

            response["response"]["is_whatsapp_welcome_response"] = True

        if not channel_params.get("is_feedback_request", False):
            response_to_return, response = check_for_query_warning_or_block_response(
                bot_obj, channel, user, easychat_params, easychat_bot_user, original_message, src, response)
        else:
            response_to_return = False

        if response_to_return:
            response["response"]["language_src"] = src
            return response

        if easychat_bot_user.channel_name in ["Web", "Android", "iOS"]:
            message, src = get_message_and_src_if_auto_language_change_confirmed(
                user, message, easychat_bot_user, easychat_params)
            easychat_bot_user.update_easychat_bot_user_details(
                src=src, message=message)

            is_auto_language_change_detected, detected_language = check_if_auto_language_change_detected(
                user, message, easychat_bot_user, easychat_params)
            if is_auto_language_change_detected:

                reset_last_suggested_query_hash_in_data_model(
                    easychat_bot_user, user)

                return build_auto_language_detected_response(user, detected_language, easychat_bot_user, easychat_params)

        if easychat_bot_user.channel_name not in ["ET-Source", "Voice", "Web", "Android", "iOS"]:
            message, src, is_language_not_found_response_to_be_send = get_auto_detected_message_and_src_for_other_channels(
                user, message, easychat_bot_user, easychat_params)

            if easychat_bot_user.channel_name == "WhatsApp" and is_language_not_found_response_to_be_send and easychat_params.is_new_user and easychat_bot_user.bot_channel_obj.return_initial_query_response:
                response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)
                response["response"]["is_whatsapp_welcome_response"] = True
                response["response"]["language_src"] = "en"
                return response

            easychat_bot_user.src = src

            if is_language_not_found_response_to_be_send:

                reset_last_suggested_query_hash_in_data_model(
                    easychat_bot_user, user)

                return build_auto_language_detected_response(user, src, easychat_bot_user, easychat_params)

            lang_obj = Language.objects.filter(lang=src).first()
            if easychat_bot_user.channel_name not in ["WhatsApp"]:
                user.selected_language = lang_obj
                user.save(update_fields=['selected_language'])

            easychat_bot_user.update_easychat_bot_user_details(
                src=src, message=message, selected_language=lang_obj)

        if easychat_bot_user.channel_name == "Voice":
            is_language_not_found_response, src = get_detected_language_for_voice_bot(easychat_bot_user, message)

            if is_language_not_found_response:
                return build_voicebot_fallback_response(user, message, easychat_bot_user, easychat_params)

        if easychat_bot_user and easychat_bot_user.translated_message:
            message = easychat_bot_user.translated_message
        else:
            message = check_and_get_message_after_translation(
                message, src, easychat_bot_user, WhitelistedEnglishWords, EasyChatTranslationCache)
        logger.info("message after translation " + message, extra={
            'AppName': logger_extra['AppName'], 'user_id': str(user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        curr_lang_obj = Language.objects.filter(lang=src).first()
        if easychat_bot_user.is_bot_language_change_confirmed:

            language_template_obj = RequiredBotTemplate.objects.filter(
                bot=bot_obj, language=curr_lang_obj).first()

            easychat_bot_user.language_template_obj = language_template_obj

        # updating the language template object if language change confirmed
        # updating the original message in case it was updated in language
        # change
        original_message = easychat_bot_user.original_message
        easychat_bot_user.selected_language = curr_lang_obj
        extracted_text_or_emoji = give_text_or_emoji(message)

        if extracted_text_or_emoji == None or extracted_text_or_emoji.strip() == "":
            if user.tree is None or user.tree.children.filter(is_deleted=False).count() == 0:
                emoji_sentiment_detected = run_emoji_detection(message)
                if emoji_sentiment_detected != None:
                    return return_emoji_response(easychat_bot_user, easychat_params, user, emoji_sentiment_detected, message, broken_mail_dump)

        if extracted_text_or_emoji != None and extracted_text_or_emoji.strip() != "":
            message = process_string(message, user_id, src, channel, bot_id)

        if user.tree is None:
            message = validation_obj.remove_hexabyte_character(message)

        user_id = user.user_id

        # updating details in EasychatBotUser object
        easychat_bot_user.update_easychat_bot_user_details(
            user_id=user_id, message=message)

        logger_extra['user_id'] = user_id

        store_channel_params_in_data_models(
            user, easychat_bot_user, easychat_params, channel_params)

        if channel == "Web":
            if not is_session_id_valid(easychat_params.session_id, logger_extra, EasyChatSessionIDGenerator) and not easychat_params.is_initial_intent:
                response = {}
                response['status_code'] = '500'
                response['status_message'] = 'Invalid session id'
                return updated_response_to_send_after_language_confirmation(response, easychat_bot_user)

        logger.info("Session Id is set to " + easychat_params.session_id, extra=logger_extra)

        logger.info("Request received from " + easychat_params.window_location, extra=logger_extra)
        api_request_response_parameters = [json.dumps(
            {}), json.dumps({}), json.dumps({}), json.dumps({})]

        # profanity filter is used to check if thier are any bad words in user
        # query if found is_prfanity_detected would be true
        is_profanity_detected, profanity_filter_response = check_for_profanity_filter(
            app_config, easychat_bot_user, easychat_params, user, api_request_response_parameters)

        if is_profanity_detected:
            return updated_response_to_send_after_language_confirmation(profanity_filter_response, easychat_bot_user)

        flow_termination_bot_response, flow_termination_confirmation_display_message = get_multilingual_flow_termination_response(
            bot_obj, src)

        # checking if flow termination was initiated or not, if then move ahead
        is_flow_terminated, easychat_flow_termination_initiated = check_is_flow_terminated(
            message, user, easychat_params, easychat_bot_user, api_request_response_parameters, flow_termination_bot_response)

        if is_flow_terminated:

            reset_last_suggested_query_hash_in_data_model(
                easychat_bot_user, user)

            response_to_send = build_flow_break_response(
                user, bot_obj, flow_termination_bot_response, src, channel, termination_confirmed=True)

            return updated_response_to_send_after_language_confirmation(response_to_send, easychat_bot_user)

        # Checking for flow-break
        is_flow_termination_break, display_messsage = check_is_flow_termination_break(
            message, user, easychat_params, easychat_bot_user, api_request_response_parameters)

        if is_flow_termination_break:

            reset_last_suggested_query_hash_in_data_model(
                easychat_bot_user, user)

            response_to_send = build_flow_break_response(
                user, bot_obj, display_messsage, src, channel)

            return updated_response_to_send_after_language_confirmation(response_to_send, easychat_bot_user)

        update_bot_id_in_data_models_if_not_present(user, easychat_bot_user)
        save_form_assist_analytics(
            channel_params, easychat_bot_user, user, message)

        logger.info("user tree at start of conversation is " + str(user.tree), extra=logger_extra)
        # check whether user has reached terminal tree or not.
        check_terminal_tree_logic(user, src, channel, bot_id)

        logger.info("user tree at after terminal tree logic is " + str(user.tree), extra=logger_extra)
        if not easychat_params.is_sticky_message_called_in_flow:
            previous_parent_tree = user.tree

        tree = None
        suggestion_list = []
        status_re_sentence = False
        easychat_abort_flow_initiated = 'false'
        easychat_params.is_intent_tree = True if user.tree == None else False
        training_question = ""
        match_percentage = ""    
        check_and_save_attachment_to_server(user, easychat_params, easychat_bot_user)
        if is_form_assist == False:
            while True:
                message_value_to_check_intent_clicked = message

                # fetch intent response if user clicks suggestion
                user, start_intent_msg, tree, message, to_check_abort_flow_message, is_manually_typed_query = return_user_tree_based_suggestion(
                    easychat_params, easychat_bot_user, user, tree, message)
                # to check
                user_entered_message = original_message
                if message_value_to_check_intent_clicked != message:
                    original_message = message
                    if src != "en":
                        message_from_intent_id = LanguageTuningIntentTable.objects.filter(
                            intent=Intent.objects.filter(pk=int(user_entered_message)).first(),
                            language=curr_lang_obj).first()
                        if message_from_intent_id:
                            message_from_intent_id = message_from_intent_id.multilingual_name
                            original_message = message_from_intent_id
                        else:
                            original_message = get_translated_text(Intent.objects.filter(pk=int(user_entered_message)).first().name, src, EasyChatTranslationCache)
                            
                easychat_params.is_manually_typed_query = is_manually_typed_query
                easychat_bot_user.message = message
                # fetch intent response if user types right intent name
                user, start_intent_msg, tree, message, training_question = return_user_tree_based_on_intent_hash(
                    user, tree, message, easychat_bot_user, easychat_params)
                if training_question != "":
                    match_percentage = 100

                else:
                    if tree != None:
                        training_question = tree.name
                        match_percentage = 100

                # this function checks if for this particular is thier any
                # intent which has crossed the threshold and returns that tree
                user, start_intent_msg, tree, message, word_mapped_message, stem_words = return_user_tree_based_on_suggested_query_hash(
                    user, tree, message, easychat_bot_user, easychat_params)

                # Function checks if flow abort is initiated and returns
                # appropriate intent tree saved in user

                easychat_abort_flow_initiated = "false"

                if bot_info_obj.enable_abort_flow_feature:
                    user, tree, easychat_abort_flow_initiated = return_tree_if_flow_aborted(
                        message, user, easychat_bot_user, easychat_params)

                # intent identified check function

                logger.info("Into return_next_tree...", extra=logger_extra)
                original_training_question = training_question
                # fetch intent response if user misses some words
                if training_question == "":
                    user, tree, status_re_sentence, suggestion_list, intent_obj_category_based, training_question, match_percentage, extra_params = return_next_tree_based_is_go_back_enabled(
                        easychat_params, message, user_entered_message, user, easychat_bot_user, word_mapped_message, stem_words)
                else:
                    user, tree, status_re_sentence, suggestion_list, intent_obj_category_based, training_question, match_percentage, extra_params = return_next_tree_based_is_go_back_enabled(
                        easychat_params, message, user_entered_message, user, easychat_bot_user, word_mapped_message, stem_words)
                    training_question = original_training_question
                    match_percentage = 100

                easychat_params = check_is_percent_match_enabled(
                    easychat_params, easychat_bot_user)

                # to check if any intent is called inside flow
                easychat_bot_user.intent_obj_category_based = intent_obj_category_based
                if not easychat_bot_user.original_tree:
                    easychat_bot_user.original_tree = tree
                check_and_update_count_for_suggested_queries(
                    user, bot_obj, easychat_bot_user.original_tree, channel, src)

                if easychat_abort_flow_initiated == 'true':
                    status_re_sentence = False
                    easychat_params.is_manually_typed_query = False

                if (previous_parent_tree != None or to_check_abort_flow_message) and not ("is_repeat_tree" in extra_params and extra_params["is_repeat_tree"]):
                    if previous_parent_tree.children.all().exists():

                        is_abort_flow_initiated = False

                        if bot_info_obj.enable_abort_flow_feature:
                            is_abort_flow_initiated, display_messsage = check_if_abort_flow_initiated(
                                easychat_bot_user, easychat_params, message, user, flow_termination_confirmation_display_message, previous_parent_tree, api_request_response_parameters)

                        if is_abort_flow_initiated:

                            reset_last_suggested_query_hash_in_data_model(
                                easychat_bot_user, user)
                            
                            # this is bieng done for the case when the tree has only single child in that case irespective of message
                            # the user.tree is updated with child tree so updating it with last level tree data variable
                            update_user_tree_with_last_level_tree(user)

                            response_to_send = build_flow_break_response(
                                user, bot_obj, display_messsage, src, channel, False, True)

                            return updated_response_to_send_after_language_confirmation(response_to_send, easychat_bot_user)

                if not easychat_params.is_new_user and len(suggestion_list) != 0:

                    handle_suggestion_based_response_for_user(
                        user, message, suggestion_list, easychat_bot_user, easychat_params, original_message, word_mapped_message, stem_words)

                    response_to_send = build_suggestion_response(
                        user, bot_obj, suggestion_list, src, channel, language_template_obj)

                    return updated_response_to_send_after_language_confirmation(response_to_send, easychat_bot_user)

                reset_last_suggested_query_hash_in_data_model(
                    easychat_bot_user, user)

                if status_re_sentence:
                    logger.info("status re sentence is true", extra=logger_extra)
                    break
                if tree is not None:
                    if not easychat_bot_user.is_recur_flag:
                        easychat_bot_user.parent_tree = tree
                    easychat_params.is_intent_tree = False
                    if tree.is_automatic_recursion_enabled:
                        flag = execute_postprocessor(
                            tree, start_intent_msg, easychat_bot_user)
                        if flag:
                            try:
                                save_flow_analytics_data_pipe_processor(
                                    message, tree, bot_obj, user, src, channel_obj, bot_id, FlowAnalytics, Data, Tree, logger_extra, easychat_params)
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logger.error("Flow analytics pipe processor error. %s at %s",
                                             str(e), str(exc_tb.tb_lineno), extra=logger_extra)
                                pass
                            easychat_bot_user.is_recur_flag = True
                            message = start_intent_msg
                            continue

                    elif tree.pipe_processor != None:
                        message, flag = execute_pipeprocessor(
                            user, bot_obj, src, channel)
                        if flag == True:
                            easychat_bot_user.is_recur_flag = True
                            try:
                                # save in mis for pipe processor only for intent
                                # otherwise goes into except

                                # Commented these lines because MIS Dasboard was being created 2 times
                                # When Recur flag was set True in Pipe Processor
                
                                # intent_name = get_intent_name(
                                #     tree, src, channel, bot_id, user_id)
                                # category_name = get_intent_category_name(
                                #     tree, src, channel, bot_id, user)
                                # intent_recognized = Intent.objects.get(tree=tree, bots=Bot.objects.get(
                                #     pk=bot_id), is_hidden=False, is_deleted=False)

                                # easychat_bot_response = EasyChatBotResponse(
                                #     message=original_message, intent_name=intent_name, category_name=category_name, intent_recognized=intent_recognized)

                                # create_mis_dashboard_object(
                                #     easychat_bot_user, easychat_params, easychat_bot_response)
                                pass
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logger.error("Pipe processor creation error. %s at %s",
                                             str(e), str(exc_tb.tb_lineno), extra=logger_extra)
                                pass

                            # saving flow analytics objects if pipe processor
                            # is not None.
                            try:
                                save_flow_analytics_data_pipe_processor(
                                    message, tree, bot_obj, user, src, channel_obj, bot_id, FlowAnalytics, Data, Tree, logger_extra, easychat_params)
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logger.error("Flow analytics pipe processor error. %s at %s",
                                             str(e), str(exc_tb.tb_lineno), extra=logger_extra)
                                pass
                            continue
                break

        if easychat_bot_user.channel_name == "WhatsApp" and not tree and easychat_params.is_new_user:
            response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)
            response["response"]["is_whatsapp_welcome_response"] = True
            response["response"]["language_src"] = src
            return response

        # handling if form assist  is enabled
        if easychat_params.is_form_assist:
            message, tree = update_and_get_form_assist_details(
                user, message, easychat_bot_user, easychat_params)
            suggestion_list = []
            status_re_sentence = False

        if easychat_flow_termination_initiated == 'true' and str(message).strip().lower() == "no":
            flow_termination_tree_pk = Data.objects.filter(
                user=user, variable="easychat_flow_termination_previous_tree").order_by('-pk')
            if flow_termination_tree_pk.count():
                tree = Tree.objects.filter(
                    pk=flow_termination_tree_pk[0].get_value().replace('"', ''))[0]
                user.tree = tree
                user.save(update_fields=['tree'])
            easychat_params.is_manually_typed_query = False

        is_abort_flow_cancelled = False
        if easychat_abort_flow_initiated == 'true' and str(message).strip().lower() == "no":
            abort_flow_tree_pk = Data.objects.filter(
                user=user, variable="easychat_abort_flow_previous_tree").order_by('-pk')
            if abort_flow_tree_pk.count():
                tree = Tree.objects.filter(
                    pk=abort_flow_tree_pk[0].get_value().replace('"', ''))[0]
                user.tree = tree
                user.save(update_fields=['tree'])
                is_abort_flow_cancelled = True
            easychat_params.is_manually_typed_query = False
        if tree is not None:
            save_flow_analytics_data_pipe_processor_none(
                user, message, tree, bot_obj, src, channel_obj, Intent, Data, FlowAnalytics, logger_extra, easychat_params)

            # We mark user's latest whatsapp catalogue cart as purchased
            # if they reach a tree with is_catalogue_purchased true
            if tree.is_catalogue_purchased:
                catalogue_cart_obj = WhatsappCatalogueCart.objects.filter(
                    bot=bot_obj, user=user, is_purchased=False).last()
                if catalogue_cart_obj:
                    catalogue_cart_obj.is_purchased = True
                    catalogue_cart_obj.save(update_fields=['is_purchased'])

            # Save livechat analytics
            if not is_abort_flow_cancelled and not status_re_sentence and bot_obj.livechat_default_intent and bot_obj.livechat_default_intent.tree == easychat_bot_user.parent_tree:
                if easychat_params.is_initial_intent:
                    save_data(user, {"save_initial_livechat_analytics": "true"}, src, channel_obj.name, bot_id, is_cache=True)
                else:
                    save_livechat_analytics_details(bot_obj, channel_obj)

        else:
            save_data(user, {"last_tree_pk": "None"}, src,
                      channel_obj.name, bot_id, is_cache=True)

        # attachment is will store attached file src in case of succesfull
        # upload else none
        response = get_user_attachament_details(
            user, easychat_params, easychat_bot_user, tree, response)

        json_api_resp = process_api(user, tree, src, channel, bot_id)

        response = build_web_response(user,
                                      tree,
                                      message,
                                      status_re_sentence,
                                      json_api_resp,
                                      easychat_bot_user,
                                      easychat_params)

        if original_message.strip() == "":
            message_to_save = user_entered_message
        else:
            message_to_save = original_message

        easychat_params.training_question = training_question
        easychat_params.match_percentage = match_percentage
        response = parse_and_save_user_query_details_in_mis(
            response, easychat_params, easychat_bot_user, user, tree, message_to_save, json_api_resp, status_re_sentence)

        modes = response["response"]["text_response"]["modes"]

        # LiveChat Check
        if channel not in ["Web", "iOS", "Android"] and "is_livechat" in modes and modes["is_livechat"] == "true":
            # LiveChat Check
            is_welcome_msg = False
            welcome_msg_text = ""
            livechat_notification, is_welcome_msg = create_and_enable_livechat(
                user_id, "-1", channel, bot_obj, original_message)

            if livechat_notification != "":
                response["response"]["text_response"][
                    "text"] += "$$$" + str(livechat_notification)
                welcome_msg_text = response["response"]["text_response"]["text"]
                
            if is_welcome_msg:
                response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)
                response["response"]["text_response"]["text"] = welcome_msg_text + "$$$" + response["response"]["text_response"]["text"]

        response = updated_response_to_send_after_language_confirmation(
            response, easychat_bot_user)

        response_str = json.dumps(response)

        logger.info('updated_response_to_send_after_language_confirmation response:' + response_str, extra=logger_extra)
        sensitive_filter_obj = SensitiveDataFilter()
        response_str = sensitive_filter_obj.remove_easychat_sensitive_tags(
            response_str)

        response = json.loads(response_str)

        response = check_and_update_response_object_based_on_attachment(
            response, easychat_params, easychat_bot_user)

        response = check_and_update_response_object_based_on_whatsapp_nps(
            response, is_whatsapp_nps_rating, whatsapp_rating, is_whatsapp_nps_comment, language_template_obj)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_message = "Error in execute_query {} in line no {}".format(str(e), str(exc_tb.tb_lineno))
        logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        broken_mail_dump["error"] = error_message
        check_and_send_broken_bot_mail(
            bot_id, channel, easychat_params.window_location, json.dumps(broken_mail_dump))
        response = build_internal_server_error_response(
            user_id, src, channel, bot_id, language_template_obj)

    return response


def save_livechat_analytics_details(bot_obj, channel_obj):
    try:
        daily_livechat_analytics_obj = DailyLiveChatAnalytics.objects.filter(bot=bot_obj, channel=channel_obj, date=datetime.datetime.now().date()).first()

        if not daily_livechat_analytics_obj:
            daily_livechat_analytics_obj = DailyLiveChatAnalytics.objects.create(bot=bot_obj, channel=channel_obj)

        daily_livechat_analytics_obj.count += 1
        daily_livechat_analytics_obj.save(update_fields=["count"])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_livechat_analytics_details! %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


################################# Execute query ends #####################


def update_user_tree_with_last_level_tree(user):
    try:
        last_level_tree = Data.objects.filter(user=user, variable="last_level_tree_pk").first()

        if last_level_tree:
            last_level_tree_pk = last_level_tree.get_value().replace('"', '')
            tree_obj = Tree.objects.filter(pk=int(last_level_tree_pk)).first()

            if tree_obj:
                user.tree = tree_obj
                user.save(update_fields=["tree"])

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_user_tree_with_last_level_tree! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def get_default_english_language_object():
    try:
        eng_lang = Language.objects.filter(lang="en").first()
        if not eng_lang:
            eng_lang = Language.objects.create(
                name_in_english="English", display="English", lang="en")

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_default_english_language_object! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return eng_lang


def update_custom_order_deatils_in_response(response, is_custom_order_selected, order_of_response_list):

    if (is_custom_order_selected and "dynamic_widget_type" in response["response"] and response["response"]["dynamic_widget_type"] not in order_of_response_list):
        order_of_response_list.append(
            response["response"]["dynamic_widget_type"])

    response['response'][
        'is_custom_order_selected'] = is_custom_order_selected
    response['response']['order_of_response'] = order_of_response_list
    return response


def parse_and_save_user_query_details_in_mis(response, easychat_params, easychat_bot_user, user, tree, message_to_save, json_api_resp, status_re_sentence):
    logger_extra = easychat_bot_user.extra

    src = easychat_bot_user.src
    channel = easychat_bot_user.channel_name
    bot_id = easychat_bot_user.bot_id
    user_id = easychat_bot_user.user_id
    bot_obj = easychat_bot_user.bot_obj
    intent_obj_category_based = easychat_bot_user.intent_obj_category_based
    try:
        intent_name = "INFLOW-INTENT"
        if not status_re_sentence:
            if easychat_bot_user.is_recur_flag:
                intent_name = get_intent_name(easychat_bot_user.parent_tree, src, channel, bot_id, user_id)
            else:
                intent_name = get_intent_name(tree, src, channel, bot_id, user_id)

        if intent_name != "INFLOW-INTENT" and intent_name != None:
            intent_objs = Intent.objects.filter(
                name=intent_name, bots__in=[bot_obj])
            intent_obj = intent_objs.first()
            small_talk_intent = intent_obj.is_small_talk
            is_custom_order_selected = intent_obj.is_custom_order_selected
            if is_custom_order_selected == True:
                order_of_response = json.loads(intent_obj.order_of_response)
            else:
                order_of_response = []

            order_of_response_list = []
            for elements in order_of_response:
                order_of_response_list.append(elements)
            intent_objs.update(intent_click_count=F('intent_click_count') + 1)
        elif intent_name == "INFLOW-INTENT" and tree != None:
            small_talk_intent = False
            is_custom_order_selected = tree.is_custom_order_selected
            if is_custom_order_selected == True:
                order_of_response = json.loads(tree.order_of_response)
            else:
                order_of_response = []

            order_of_response_list = []
            for elements in order_of_response:
                order_of_response_list.append(elements)

        else:
            small_talk_intent = False
            is_custom_order_selected = False
            order_of_response = []
            order_of_response_list = []

        response = update_custom_order_deatils_in_response(
            response, is_custom_order_selected, order_of_response_list)

        try:
            identified_intent_name = intent_name
            if intent_name == "INFLOW-INTENT" and tree != None:
                identified_intent_name = get_last_identified_intent_name(
                    user, src, channel, bot_id)

            intent_obj = Intent.objects.filter(
                name=identified_intent_name, bots__in=[bot_obj], is_deleted=False).first()
            if intent_obj:
                new_parameters_list = json.dumps({
                    "intent_name": identified_intent_name,
                    "intent_pk": str(intent_obj.id),
                    "tree_name": str(tree.name),
                    "tree_id": str(tree.id)
                })
            else:
                new_parameters_list = json.dumps({
                    "intent_name": identified_intent_name,
                    "intent_pk": "none",
                    "tree_name": "none",
                    "tree_id": "none"
                })
            
            json_api_request_packet = {}

            if tree.api_tree:
                api_name = tree.api_tree.name

                json_api_elapsed_time = get_api_elapsed_time(
                    json_api_resp, src, channel, bot_id, user_id)

                json_api_request_packet, json_api_resp = save_api_data(
                    json_api_resp, json_api_elapsed_time, bot_obj, api_name, user, src, channel, new_parameters_list)
            else:
                json_api_resp = {}

        except Exception:
            json_api_request_packet = {}
            json_api_resp = {}
            pass

        recommendations = response['response']["recommendations"]
        choices = response['response']["choices"]
        modes = response["response"]["text_response"]["modes"]

        modes_param = response["response"]["text_response"]["modes_param"]

        widgets = return_widgets(
            modes, modes_param, easychat_bot_user, logger_extra)

        intent_identified_obj_mis = None

        try:
            if easychat_bot_user.is_recur_flag:
                intent_identified_obj_mis = Intent.objects.get(
                    tree=easychat_bot_user.parent_tree, bots__in=[bot_obj], is_hidden=False, is_deleted=False)
            else:
                intent_identified_obj_mis = Intent.objects.get(
                    tree=tree, bots__in=[bot_obj], is_hidden=False, is_deleted=False)    

        except Exception:
            intent_identified_obj_mis = None

        if intent_obj_category_based != None:
            intent_identified_obj_mis = intent_obj_category_based

        if intent_name == "INFLOW-INTENT" and intent_identified_obj_mis != None and not status_re_sentence:
            intent_name = intent_identified_obj_mis.name
        elif intent_name == "INFLOW-INTENT" and status_re_sentence:
            intent_identified_obj_mis = None

        category_name = get_intent_category_name(
            tree, src, channel, bot_id, user)

        api_request_response_parameters = [json.dumps(json_api_request_packet), json.dumps(
            json_api_resp), json.dumps(json_api_request_packet), json.dumps(json_api_resp)]

        # Translating choices related text
        choices = get_parsed_translated_choices_list(
            choices, easychat_bot_user.src, easychat_bot_user.bot_info_obj)

        recommendations = get_parsed_translated_recommendation_list(
            recommendations, easychat_bot_user.src, easychat_bot_user.bot_info_obj)

        easychat_bot_response = EasyChatBotResponse(
            message=message_to_save, intent_name=intent_name, category_name=category_name)
        easychat_bot_response.bot_response = response[
            'response']['text_response']['text']
        easychat_bot_response.recommendations = json.dumps(recommendations)
        easychat_bot_response.api_request_response_parameters = api_request_response_parameters
        easychat_bot_response.choices = choices
        easychat_bot_response.response_json = json.dumps(response)
        easychat_bot_response.widgets = widgets
        easychat_bot_response.small_talk_intent = small_talk_intent
        easychat_bot_response.intent_recognized = intent_identified_obj_mis

        user_id = easychat_bot_user.user_id
        file_key = easychat_params.file_key
        if easychat_params.is_attachment_succesfull and file_key != "":
            easychat_bot_response.attachment = '/chat/access-file/' + \
                str(file_key) + "/?user_id=" + user_id

        if easychat_params.attached_file_path != "":
            easychat_bot_response.attachment = easychat_params.attached_file_path
        create_mis_dashboard_object(
            easychat_bot_user, easychat_params, easychat_bot_response)

        logger.info('conversation saved in mis dashboard', extra=logger_extra)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in parse_and_save_user_query_details_in_mis %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)

    return response


def get_parsed_translated_choices_list(choices, src, bot_info_obj=None):

    translated_choices = []
    for choice in choices:
        choice["value"] = get_translated_text(
            choice["value"], src, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
        choice["display"] = get_translated_text(
            choice["display"], src, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
        translated_choices.append(choice)

    return translated_choices


def get_parsed_translated_recommendation_list(recommendations, src, bot_info_obj=None):
    translated_recommendations = []

    for recommendation in recommendations:
        if type(recommendation) == dict and "name" in recommendation:
            recommendation["name"] = get_translated_text(recommendation["name"], src, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            translated_recommendations.append(recommendations)
        else:
            translated_recommendations.append(get_translated_text(recommendation, src, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

    return translated_recommendations


def check_and_update_response_object_based_on_attachment(response, easychat_params, easychat_bot_user):
    logger_extra = easychat_bot_user.extra
    user_id = easychat_bot_user.user_id
    file_key = easychat_params.file_key
    try:
        if easychat_params.is_attachment_succesfull:
            if file_key != "":
                response["response"]["attached_file_src"] = '/chat/access-file/' + \
                    str(file_key) + "/?user_id=" + user_id
                response["response"]["attached_file_name"] = easychat_params.attachment.split(
                    "/")[-1] + "." + easychat_params.file_extention
            else:
                response["response"]["video_recorder_file_src"] = easychat_params.attachment
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in check_and_update_response_object_based_on_attachment %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)

    return response


def check_and_update_response_object_based_on_whatsapp_nps(response, is_whatsapp_nps_rating, whatsapp_rating, is_whatsapp_nps_comment, language_template_obj):

    try:
        if is_whatsapp_nps_rating:

            if whatsapp_rating >= 0 and whatsapp_rating <= 8:
                response["response"]["speech_response"][
                    "text"] = language_template_obj.get_negative_feedback_text()
                response["response"]["text_response"][
                    "text"] = language_template_obj.get_negative_feedback_text()

            else:
                response["response"]["speech_response"][
                    "text"] = language_template_obj.get_positive_feedback_text()
                response["response"]["text_response"][
                    "text"] = language_template_obj.get_positive_feedback_text()

        elif is_whatsapp_nps_comment:
            response["response"]["speech_response"][
                "text"] = language_template_obj.get_feedback_text()
            response["response"]["text_response"][
                "text"] = language_template_obj.get_feedback_text()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_and_update_response_object_based_on_whatsapp_nps! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return response


def check_is_percent_match_enabled(easychat_params, easychat_bot_user):
    try:
        bot_info_obj = easychat_bot_user.bot_info_obj
        if not bot_info_obj.is_percentage_match_enabled:
            easychat_params.match_percentage = -1
            easychat_params.training_question = ""

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_is_percent_match_enabled! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return easychat_params


def create_mis_dashboard_object(easychat_bot_user, easychat_params, easychat_bot_response):
    try:
        encrypted_message = get_encrypted_message(
            easychat_bot_response.message_received, easychat_bot_user.bot_obj, easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.user_id, False)
        encrypted_bot_response = get_encrypted_message(
            easychat_bot_response.bot_response, easychat_bot_user.bot_obj, easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.user_id, True)
        if easychat_params.match_percentage == "":
            easychat_params.match_percentage = -1

        easychat_params = check_is_percent_match_enabled(
            easychat_params, easychat_bot_user)

        selected_language = easychat_bot_user.selected_language

        if not selected_language:
            selected_language = get_default_english_language_object()

        category_obj = None
        if easychat_bot_user and easychat_bot_user.category_obj:
            category_obj = easychat_bot_user.category_obj
        else:
            category_obj = get_category_obj(easychat_bot_user.bot_obj, easychat_bot_response.category_name)
            easychat_bot_user.category_obj = category_obj
        
        validation_obj = EasyChatInputValidation()
        is_unidentified_query = False
        if easychat_bot_response.intent_name == None and validation_obj.is_valid_query(easychat_bot_response.message_received):
            is_unidentified_query = True

        if easychat_params.is_initial_intent:
            initial_intent_mis_params = {}
            initial_intent_mis_params["message_received"] = encrypted_message
            initial_intent_mis_params["bot_id"] = easychat_bot_user.bot_obj.pk if easychat_bot_user.bot_obj else None
            initial_intent_mis_params["bot_response"] = encrypted_bot_response
            initial_intent_mis_params["intent_name"] = easychat_bot_response.intent_name
            initial_intent_mis_params["training_question"] = easychat_params.training_question
            initial_intent_mis_params["match_percentage"] = easychat_params.match_percentage
            initial_intent_mis_params["user_id"] = easychat_bot_user.user_id
            initial_intent_mis_params["category_name"] = easychat_bot_response.category_name
            initial_intent_mis_params["session_id"] = easychat_params.session_id
            initial_intent_mis_params["channel_name"] = easychat_bot_user.channel_name
            initial_intent_mis_params["api_request_packet"] = easychat_bot_response.api_request_response_parameters[0]
            initial_intent_mis_params["api_response_packet"] = easychat_bot_response.api_request_response_parameters[1]
            initial_intent_mis_params["api_request_parameter_used"] = easychat_bot_response.api_request_response_parameters[2]
            initial_intent_mis_params["api_response_parameter_used"] = easychat_bot_response.api_request_response_parameters[3]
            initial_intent_mis_params["window_location"] = easychat_params.window_location
            initial_intent_mis_params["attachment"] = easychat_bot_response.attachment
            initial_intent_mis_params["small_talk_intent"] = easychat_bot_response.small_talk_intent
            initial_intent_mis_params["recommendations"] = easychat_bot_response.recommendations
            initial_intent_mis_params["choices"] = easychat_bot_response.choices
            initial_intent_mis_params["response_json"] = easychat_bot_response.response_json
            initial_intent_mis_params["widgets"] = easychat_bot_response.widgets
            initial_intent_mis_params["intent_recognized_id"] = easychat_bot_response.intent_recognized.pk if easychat_bot_response.intent_recognized else None
            initial_intent_mis_params["form_data_widget"] = easychat_params.form_data_widget
            initial_intent_mis_params["client_city"] = easychat_params.client_city
            initial_intent_mis_params["client_state"] = easychat_params.client_state
            initial_intent_mis_params["client_pincode"] = easychat_params.client_pincode
            initial_intent_mis_params["is_manually_typed_query"] = easychat_params.is_manually_typed_query
            initial_intent_mis_params["is_session_started"] = easychat_params.is_session_started
            initial_intent_mis_params["selected_language_id"] = selected_language.pk if selected_language else None
            initial_intent_mis_params["category_id"] = category_obj.pk if category_obj else None
            initial_intent_mis_params["is_intiuitive_query"] = easychat_params.is_intiuitive_query
            initial_intent_mis_params["is_business_initiated_session"] = easychat_params.is_business_initiated_session
            initial_intent_mis_params["is_unidentified_query"] = is_unidentified_query
            initial_intent_mis_params["is_mobile"] = easychat_params.is_mobile
            
            save_data(easychat_bot_user.user, {"initial_intent_mis_params": initial_intent_mis_params}, easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_obj.pk, is_cache=True)
            return

        MISDashboard.objects.create(message_received=encrypted_message,
                                    bot=easychat_bot_user.bot_obj,
                                    bot_response=encrypted_bot_response,
                                    intent_name=easychat_bot_response.intent_name,
                                    training_question=easychat_params.training_question,
                                    match_percentage=easychat_params.match_percentage,
                                    user_id=easychat_bot_user.user_id,
                                    category_name=easychat_bot_response.category_name,
                                    session_id=easychat_params.session_id,
                                    channel_name=easychat_bot_user.channel_name,
                                    api_request_packet=easychat_bot_response.api_request_response_parameters[
                                        0],
                                    api_response_packet=easychat_bot_response.api_request_response_parameters[
                                        1],
                                    api_request_parameter_used=easychat_bot_response.api_request_response_parameters[
                                        2],
                                    api_response_parameter_used=easychat_bot_response.api_request_response_parameters[
                                        3],
                                    window_location=easychat_params.window_location,
                                    attachment=easychat_bot_response.attachment,
                                    small_talk_intent=easychat_bot_response.small_talk_intent,
                                    recommendations=easychat_bot_response.recommendations,
                                    choices=easychat_bot_response.choices,
                                    response_json=easychat_bot_response.response_json,
                                    widgets=easychat_bot_response.widgets,
                                    intent_recognized=easychat_bot_response.intent_recognized,
                                    form_data_widget=easychat_params.form_data_widget,
                                    client_city=easychat_params.client_city,
                                    client_state=easychat_params.client_state,
                                    client_pincode=easychat_params.client_pincode,
                                    is_manually_typed_query=easychat_params.is_manually_typed_query,
                                    is_session_started=easychat_params.is_session_started,
                                    selected_language=selected_language,
                                    category=category_obj,
                                    is_intiuitive_query=easychat_params.is_intiuitive_query,
                                    is_business_initiated_session=easychat_params.is_business_initiated_session,
                                    is_unidentified_query=is_unidentified_query,
                                    is_mobile=easychat_params.is_mobile)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_mis_dashboard_object! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def handle_suggestion_based_response_for_user(user, message, suggestion_list, easychat_bot_user, easychat_params, original_message, word_mapped_message, stem_words):

    try:
        logger.info('User requires suggestion based on entered message.', extra=easychat_bot_user.extra)
        suggestion_list = check_and_trigger_livechat(
            message, easychat_bot_user.bot_obj, suggestion_list, easychat_bot_user)

        easychat_bot_response = EasyChatBotResponse(
            message=original_message, recommendations=suggestion_list)

        easychat_bot_response.bot_response = easychat_bot_user.language_template_obj.get_did_you_mean_text()
        easychat_params.is_intiuitive_query = True
        easychat_params.form_data_widget = ""
        create_mis_dashboard_object(
            easychat_bot_user, easychat_params, easychat_bot_response)

        check_and_update_suggested_query_hash(
            user, easychat_bot_user.bot_obj, message, easychat_bot_user.channel_name, easychat_bot_user.src, word_mapped_message, stem_words)

        create_intuitive_messages(
            message, easychat_bot_user, suggestion_list)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in creating handle suggestion based response %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=easychat_bot_user.extra)


def reset_last_suggested_query_hash_in_data_model(easychat_bot_user, user):

    save_data(user, {"last_suggested_query_hash_obj_pk": "none"},
              easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_obj.pk, is_cache=True)


def update_bot_id_in_data_models_if_not_present(user, easychat_bot_user):

    if not Data.objects.filter(user=user, variable="bot_id"):
        save_data(user, {"bot_id": str(easychat_bot_user.bot_id)},
                  easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_id, is_cache=True)

    if easychat_bot_user.language_template_obj:
        save_data(user, {"bot_name": str(easychat_bot_user.language_template_obj.bot_name)}, easychat_bot_user.src, easychat_bot_user.channel_name, easychat_bot_user.bot_id, is_cache=True)


def check_if_authentication_reqd(intent_obj, bot_obj, user, channel_of_message, channel_obj, src):
    try:
        if intent_obj.is_authentication_required:

            save_data(user, {
                "is_authentication_required": True}, src, channel_of_message, bot_obj.pk, is_cache=True)

            is_authenticated, next_tree = user.is_user_authenticated(
                intent_obj, channel_obj, src, bot_obj.pk)

            if is_authenticated:
                save_data(user, {
                    "is_user_authenticated": True}, src, channel_of_message, bot_obj.pk, is_cache=True)

            return next_tree

        else:
            return intent_obj.tree

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_if_authentication_reqd! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return intent_obj.tree


def get_voicebot_disposition_code_details(user, src, channel, bot_id):
    disposition_code = None
    try:
        logger.info("Into get_voicebot_disposition_code_details...", extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        disposition_code_obj = Data.objects.filter(
            user=user, variable="disposition_code").order_by('-pk').first()

        disposition_code = None
        if disposition_code_obj:
            disposition_code = disposition_code_obj.get_value()

        # last_identified_intent_name = Data.objects.filter(
        # user=user,
        # variable="last_identified_intent_name").order_by('-pk').first()[0].get_value()

        if disposition_code is not None:
            disposition_code = ast.literal_eval(
                disposition_code)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_voicebot_disposition_code_details: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        disposition_code = None

    logger.info("Exit from get_voicebot_disposition_code_details: intent name: %s", str(
        disposition_code), extra={'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
    return str(disposition_code)


def check_if_trigger_livechat_enabled_for_profanity_words(bot_obj):
    is_livechat_profanity_words_enabled = False
    profanity_obj = None
    try:
        profanity_obj = ProfanityBotResponse.objects.filter(
            bot=bot_obj).first()

        if not profanity_obj:
            profanity_obj = ProfanityBotResponse.objects.create(bot=bot_obj)

        return profanity_obj.is_suggest_livechat_for_profanity_words_enabled, profanity_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_if_trigger_livechat_enabled_for_profanity_words: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

    return is_livechat_profanity_words_enabled, None


def generate_flow_dropoff_object(user, is_miscellaneous=False):
    try:
        flow_analytics_obj = FlowAnalytics.objects.filter(user=user).last()
        if not flow_analytics_obj.is_flow_aborted:
            parent_tree_list = flow_analytics_obj.current_tree.tree_set.all()
            if parent_tree_list.count() == 0:
                parent_tree = flow_analytics_obj.current_tree
            else:
                parent_tree = parent_tree_list[0]
            dropoff_type = 2
            if flow_analytics_obj.channel.name in ["Web", "Android", "iOS"] or is_miscellaneous:
                dropoff_type = 3
            UserFlowDropOffAnalytics.objects.create(created_datetime=flow_analytics_obj.created_time, user=flow_analytics_obj.user, previous_tree=parent_tree,
                                                    current_tree=flow_analytics_obj.current_tree, intent_indentifed=flow_analytics_obj.intent_indentifed, dropoff_type=dropoff_type, channel=flow_analytics_obj.channel, intent_name="-")
            flow_analytics_obj.is_flow_aborted = True
            flow_analytics_obj.save()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("generate_flow_dropoff_object: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_faq_intents(bot_obj, language_obj, selected_language):
    try:
        faq_intents = []
        faq_intent_objs = Intent.objects.filter(
            bots__in=[bot_obj], is_deleted=False, is_faq_intent=True, is_hidden=False).order_by("-intent_click_count")
        for faq_intent_obj in faq_intent_objs:
            if selected_language == "en":
                intent_name = faq_intent_obj.name
            else:
                lang_tuned_obj = LanguageTuningIntentTable.objects.filter(
                    language=language_obj, intent=faq_intent_obj).first()
                if lang_tuned_obj:
                    intent_name = lang_tuned_obj.multilingual_name
                else:
                    intent_name = get_translated_text(
                        faq_intent_obj.name, selected_language, EasyChatTranslationCache)
            faq_intents.append({
                "name": intent_name,
                "id": faq_intent_obj.pk
            })

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_faq_intents: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    
    return faq_intents

    
def get_category_obj(bot_obj, category_name):
    try:
        category_obj = None
        if category_name != None and category_name.strip() != "":
            category_obj = Category.objects.filter(name=category_name, bot=bot_obj).first()

        return category_obj

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_category_obj: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    
    return category_obj


def get_or_generate_session_id(user):
    try:
        session_obj = EasyChatSessionIDGenerator.objects.filter(
            user=user, is_expired=False).order_by('session_start_date_time').last()
        if session_obj and not session_obj.is_session_expired():
            return str(session_obj.token)
        session_obj = EasyChatSessionIDGenerator.objects.create(user=user)
        return str(session_obj.token)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_or_generate_session_id: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    
    return user.user_id


def build_channel_failure_response(response, easychat_bot_user, bot_obj, channel_obj, bot_info_obj, category_obj, message, user, language_template_obj, src, easychat_params):
    try:
        if response is None:
            response = copy.deepcopy(DEFAULT_RESPONSE)
            response["status_code"] = "200"
            response["status_message"] = "SUCCESS"
        if easychat_bot_user.bot_channel_obj:
            bot_channel_obj = easychat_bot_user.bot_channel_obj
        else:
            bot_channel_obj = BotChannel.objects.filter(
                bot=bot_obj, channel=channel_obj).first()
            easychat_bot_user.bot_channel_obj = bot_channel_obj

        lower_channel_name = channel_obj.name.strip().lower().replace(" ", "_")
        intent_icon_channel_choices_info = bot_info_obj.get_intent_icon_channel_choices_info()

        text = get_multilingual_failure_response(bot_channel_obj, src)
        trigger_livechat_suggestion = True

        if bot_obj.is_text_to_speech_required == True:
            speech_failure_message = text.replace("</p><p>", " ")
            speech_failure_message = process_speech_response_query(
                speech_failure_message)

        easy_search_results = []
        pdf_search_results = []
        google_search_results = []

        if bot_obj.is_easy_search_allowed:
            try:
                easy_search_config = EasySearchConfig.objects.get(
                    bot=bot_obj)
                search_method = easy_search_config.feature
                if search_method == "1":
                    easy_search_results = get_easy_search_results(
                        message, user, bot_obj, src, channel_obj.name)
                    if len(easy_search_results) > 0:
                        text = language_template_obj.get_easysearch_text()
                    else:
                        easy_search_results = []
                elif search_method == "2":
                    search_cx = easy_search_config.search_cx
                    google_search_results = get_google_search_results(
                        message, search_cx, src, channel_obj.name, bot_obj.pk, user.user_id)
                    google_search_results = list(google_search_results)
                    if len(google_search_results) > 0:
                        text = language_template_obj.get_easysearch_text()
                    else:
                        google_search_results = []

            except Exception:
                easy_search_results = []
                google_search_results = []
                pass

        if bot_obj.is_pdf_search_allowed and channel_obj.name in ["Web", "Android", "iOS", "Viber"]:
            try:
                pdf_search_results = get_easysearch_pdf_result(
                    bot_obj, message, EasyPDFSearcher, EasyPDFSearcherAnalytics)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("build_web_response:" + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                    user.user_id), 'source': str(src), 'channel': str(channel_obj.name), 'bot_id': str(bot_obj.pk)})

                pdf_search_results = []

        if len(pdf_search_results) > 0:
            text = "PDF Response"

        # We mark PDF/G-Search/E-Search results as intuitive instead of unanswered
        if len(pdf_search_results) or len(easy_search_results) or len(google_search_results):
            easychat_params.is_intiuitive_query = True
            create_intuitive_messages(message, easychat_bot_user, [])

        # if Config.objects.all()[0].is_google_search_allowed:
        #     google_search_results = get_google_search_results(message)

        #     if len(google_search_results) > 0:
        #         text = "Looks like I don't have an answer to that. Here's what I found on Google."
        # else:
        #     google_search_results = []

        response["response"]["speech_response"]["text"] = text
        if bot_obj.is_text_to_speech_required == True:
            response["response"]["speech_response"][
                "text"] = speech_failure_message

        response["bot_id"] = bot_obj.pk
        response["response"][
            "google_search_results"] = google_search_results[:10]
        response["response"][
            "easy_search_results"] = easy_search_results[:10]
        response["response"][
            "pdf_search_results"] = pdf_search_results
        response["response"]["is_flow_ended"] = True
        response["response"]["text_response"]["text"] = text

        response["response"]["speech_response"]["reprompt_text"] = None

        enable_intent_icon = False
        if bot_info_obj.enable_intent_icon and (lower_channel_name in intent_icon_channel_choices_info) and ("2" in intent_icon_channel_choices_info[lower_channel_name]):
            enable_intent_icon = True

        response["response"]["recommendations"] = get_message_list_with_pk(json.loads(
            bot_channel_obj.failure_recommendations)["items"], enable_intent_icon=enable_intent_icon, category_obj=category_obj, channel_obj=channel_obj)
        if trigger_livechat_suggestion:
            response["response"]["recommendations"] = check_and_trigger_livechat(
                message, bot_obj, response["response"]["recommendations"], easychat_bot_user)

        if channel_obj.name == "WhatsApp":
            response["response"][
                "whatsapp_list_message_header"] = "Options"

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("build_channel_failure_response: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response
