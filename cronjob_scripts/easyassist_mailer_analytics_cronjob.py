import os
import sys
import json
import smtplib

from xlwt import Workbook
from EasyAssistApp.models import *
from EasyAssistApp.utils import logger
from EasyAssistApp.utils_cronjob import get_easyassist_cronjob_tracker_obj, \
    create_easyassist_cronjob_tracker_obj, \
    delete_easyassist_cronjob_tracker_obj, \
    is_cronjob_tracker_object_expired, \
    delete_and_create_cron_tracker_obj
from EasyAssistApp.utils_email_analytics import process_data_according_to_mailer_calendar

from cronjob_scripts.cognoai_cronjob_utils import send_cron_error_report

from zipfile import ZipFile
from datetime import datetime, timedelta
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pytz

from os import path
from os.path import basename

ANALYTICS_FOLDER_PATH = settings.MEDIA_ROOT + "EasyAssistApp/analytics_img/"


def cronjob():

    easyassist_cronjob_tracker_obj = get_easyassist_cronjob_tracker_obj(MAILER_ANALYTICS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    if easyassist_cronjob_tracker_obj:
        if is_cronjob_tracker_object_expired(easyassist_cronjob_tracker_obj):
            delete_and_create_cron_tracker_obj(
                MAILER_ANALYTICS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
        else:
            logger.info("easyassist_mailer_analytics_cronjob is already running!",
                        extra={'AppName': 'EasyAssist'})
            return
    else:
        create_easyassist_cronjob_tracker_obj(MAILER_ANALYTICS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)

    check_and_create_mailer_analytics_directory()
    create_mailer_analytics_email_template()
    delete_easyassist_cronjob_tracker_obj(MAILER_ANALYTICS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)


def check_and_create_mailer_analytics_directory():

    try:
        if not os.path.exists(ANALYTICS_FOLDER_PATH):
            os.makedirs(ANALYTICS_FOLDER_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_and_create_mailer_analytics_directory %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def create_mailer_analytics_email_template():
    try:
        access_token_objs = CobrowseAccessToken.objects.all()

        for access_token in access_token_objs.iterator():
            process_mailer_anlaytics_profile(access_token)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_mailer_analytics_email_template %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def process_mailer_anlaytics_profile(access_token):
    try:
        profile_objs = CobrowseMailerAnalyticsProfile.objects.filter(
            access_token=access_token, is_deleted=False)

        for profile_obj in profile_objs.iterator():
            process_data_according_to_mailer_calendar(profile_obj, access_token, CobrowseVideoAuditTrail)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error process_mailer_anlaytics_profile %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
