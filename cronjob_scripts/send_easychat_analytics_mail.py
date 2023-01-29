from EasyChatApp.constants_mailer_analytics import DEFAULT_TIME_INTERVAL_GRAPH
from EasyChatApp.models import (
    Channel, EasyChatMailerAnalyticsProfile, EasyChatMailerAuditTrail)

from EasyChatApp.utils_mailer_analytics import get_graph_html, get_table_html, get_attachment_html, generate_mail

import os
import sys
import pytz
import json
from django.conf import settings
from datetime import date, datetime, timedelta
from urllib.parse import quote
from EasyChatApp.utils import logger


def is_send_mail_required(frequency, profile_obj):
    try:
        last_mail_obj = EasyChatMailerAuditTrail.objects.filter(
            profile=profile_obj, email_frequency=frequency).order_by('-pk')

        if last_mail_obj:
            tz = pytz.timezone(settings.TIME_ZONE)
            mail_sent_datetime = last_mail_obj[0].sent_datetime.astimezone(tz).date()

            if frequency == 'Daily':
                diff = 1
            else:
                diff = int(frequency.replace('days', ''))
            
            if (datetime.now().astimezone(tz).date() - mail_sent_datetime).days >= diff:
                return True
        else:
            return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_send_mail_required! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return False


def get_start_date(frequency):
    try:
        if frequency == 'Daily':
            diff = 1
        else:
            diff = int(frequency.replace('days', ''))

        return datetime.now().date() - timedelta(days=diff)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_start_date! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def cronjob():
    try:
        profile_objs = EasyChatMailerAnalyticsProfile.objects.filter(
            is_deleted=False).iterator()

        for profile_obj in profile_objs:
            bot_obj = profile_obj.bot
            if not bot_obj or bot_obj.is_deleted or not bot_obj.is_email_notifiication_enabled:
                continue
            
            email_receivers = json.loads(profile_obj.email_address)
            email_frequency = json.loads(profile_obj.email_frequency)

            if len(email_receivers) == 0 or len(email_frequency) == 0:
                continue
            
            for frequency in email_frequency:
                if not is_send_mail_required(frequency, profile_obj):
                    continue

                analytics_html = ''
                if profile_obj.is_graph_enabled:
                    start_date = (
                        datetime.now() - timedelta(days=DEFAULT_TIME_INTERVAL_GRAPH)).date()
                    end_date = (datetime.now() - timedelta(days=1)).date()
                    date_str = "(" + start_date.strftime('%d/%m/%y') + \
                        " - " + end_date.strftime('%d/%m/%y') + ")"

                    analytics_html += get_graph_html(
                        profile_obj, False, date_str)
                export_summary_path = ""
                if profile_obj.is_table_enabled:
                    start_date = get_start_date(frequency)
                    end_date = datetime.now().date()
                    end_date_to_show = (datetime.now() - timedelta(days=1)).date()
                    date_str = "(" + start_date.strftime('%d/%m/%y') + \
                        " - " + end_date_to_show.strftime('%d/%m/%y') + ")"
                    export_file_name_time = start_date.strftime('%d_%m_%y') + "_" + datetime.now().strftime("%H:%M:%S") + "_To_" + end_date_to_show.strftime('%d_%m_%y') + "_" + datetime.now().strftime("%H:%M:%S")
                    table_analytics_html, export_summary_path = get_table_html(
                        profile_obj, False, start_date, end_date, date_str, export_file_name_time)

                    analytics_html += table_analytics_html
                if profile_obj.is_attachment_enabled or profile_obj.is_table_enabled:
                    start_date = get_start_date(frequency)
                    end_date = datetime.now().date()
                    
                    analytics_html += get_attachment_html(
                        profile_obj, start_date, end_date, Channel.objects.filter(is_easychat_channel=True), False, export_summary_path)
                    
                email_subject = profile_obj.email_subject
                for email in email_receivers:
                    try:
                        generate_mail(bot_obj.name, analytics_html, email, email_subject, datetime.now(
                        ).date().strftime('%B %d, %Y'))

                        EasyChatMailerAuditTrail.objects.create(
                            profile=profile_obj, email_frequency=frequency)
                    except Exception:
                        logger.error("send mail failed!", extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        continue
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_easychat_analytics_mail! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        pass
