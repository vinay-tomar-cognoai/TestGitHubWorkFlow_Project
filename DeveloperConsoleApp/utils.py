from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

from DeveloperConsoleApp.models import *
from DeveloperConsoleApp.constants import *

import sys
import json
import operator
import logging
import re
import ast
import random
import array
import datetime
import pytz
import threading
import os
import requests
from requests.auth import HTTPBasicAuth

import boto3

logger = logging.getLogger(__name__)


def get_developer_console_settings():
    try:
        config_obj = cache.get("DeveloperConsoleConfigObject")
        if not config_obj:
            config_obj = DeveloperConsoleConfig.objects.all().first()
            if not config_obj:
                config_obj = DeveloperConsoleConfig.objects.create()
            cache.set("DeveloperConsoleConfigObject", config_obj, settings.CACHE_TIME)
        return config_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_developer_console_settings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        return None


def get_save_in_s3_bucket_status():
    try:
        return DeveloperConsoleConfig.objects.all().first().save_file_into_s3_bucket
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_save_in_s3_bucket_status %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        return None


def get_human_readable_time_difference(recent_datetime, older_datetime):
    try:

        months_diff = (recent_datetime.year - older_datetime.year) * 12 + (recent_datetime.month - older_datetime.month)
        if (older_datetime.day > recent_datetime.day):
            months_diff -= 1

        if months_diff > 0:
            if months_diff > 12:
                years = months_diff // 12
                if years == 1:
                    return "1 year"
                return "{} years".format(years)
            elif months_diff == 1:
                return "1 month"
            else:
                return "{} months".format(months_diff)
        else:
            time_diff = recent_datetime - older_datetime

            if time_diff.days == 1:
                return "1 day"
            elif time_diff.days > 1:
                return "{} days".format(time_diff.days)
            else:
                if time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    if hours == 1:
                        return "1 hour"
                    return "{} hours".format(hours)
                elif time_diff.seconds > 60:
                    minutes = time_diff.seconds // 60
                    if minutes == 1:
                        return "1 minute"
                    return "{} minutes".format(minutes)
                else:
                    if time_diff.seconds <= 1:
                        return "{} second".format(time_diff.seconds)
                    return "{} seconds".format(time_diff.seconds)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_human_readable_time_difference %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

    return "None"


def get_developer_console_livechat_settings():
    try:
        config_obj = get_developer_console_settings()

        if config_obj.livechat_config:
            return config_obj.livechat_config

        else:
            livechat_config_obj = LiveChatAppConfig.objects.create()
            config_obj.livechat_config = livechat_config_obj
            config_obj.save()

            return livechat_config_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_developer_console_livechat_settings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

    return None


def get_developer_console_easychat_settings():
    try:
        easychat_config_obj = EasyChatAppConfig.objects.all().order_by("-pk").first()
        if not easychat_config_obj:
            easychat_config_obj = EasyChatAppConfig.objects.create()
            easychat_config_obj.save()

        return easychat_config_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_developer_console_easychat_settings %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})
    
    return None


def get_developer_console_cognodesk_settings():
    try:
        cognodesk_config_obj = CognoDeskAppConfig.objects.all().order_by("-pk").first()
        if not cognodesk_config_obj:
            cognodesk_config_obj = CognoDeskAppConfig.objects.create()
            cognodesk_config_obj.save()

        return cognodesk_config_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_developer_console_cognodesk_settings %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})
    
    return None


def get_developer_console_cobrowsing_settings():
    try:
        cobrowsing_config_obj = CobrowsingAppConfig.objects.all().order_by("-pk").first()
        if not cobrowsing_config_obj:
            cobrowsing_config_obj = CobrowsingAppConfig.objects.create()
            cobrowsing_config_obj.save()

        return cobrowsing_config_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_developer_console_cobrowsing_settings %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})
    
    return None


def get_developer_console_cognomeet_settings():
    try:
        cognomeet_config_obj = CognoMeetAppConfig.objects.all().order_by("-pk").first()
        if not cognomeet_config_obj:
            cognomeet_config_obj = CognoMeetAppConfig.objects.create()
            cognomeet_config_obj.save()

        return cognomeet_config_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_developer_console_cognomeet_settings %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})
    
    return None


def send_email_to_customer_via_awsses(recipient_id, subject, body, cc=None, content_type="html", attachment_list=[]):
    response = {}

    try:
        config_obj = get_developer_console_settings()

        data = {
            "recipient": recipient_id,
            "subject": subject,
            "type": content_type,
            "body": body,
            "cc": cc,
            "attachments": attachment_list
        }

        username = config_obj.email_host_user
        password = config_obj.email_host_password

        response = requests.post(url=config_obj.email_api_end_point,
                                 data=json.dumps(data), headers={"Content-Type": "application/json"}, auth=HTTPBasicAuth(username, password))
        response = json.loads(response.text)
    except Exception as e:
        response["status"] = 500
        response["message"] = str(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_email_to_customer_via_awsses %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})
    return response
