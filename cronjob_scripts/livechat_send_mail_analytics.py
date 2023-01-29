import os
import sys
import json
import pytz
from xlwt import Workbook
from LiveChatApp.constants import LIVECHAT_SEND_MAIL_CRONJOB_CONSTANT
from LiveChatApp.utils import create_livechat_cronjob_tracker_obj, delete_livechat_cronjob_tracker_obj, get_livechat_cronjob_tracker_obj, logger, get_agents_under_this_user
from LiveChatApp.utils_email_profile import get_graph_chart_reports, get_graph_interaction_data, get_avg_handle_time_data, get_date_wise_table_records_data, get_channel_wise_table_records_data, get_performance_report_path,\
    get_graph_chart_reports_config, get_html_for_graph_chart_reports, get_graph_interactions_config, \
    get_html_for_graph_interactions, get_graph_avg_handle_time_config, get_html_for_graph_avg_handle_time, \
    get_table_records_html, generate_mail, get_analytical_report_path, get_agent_connection_rate, get_mailer_report_path, get_customer_report_path
from datetime import datetime, timedelta, date
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from LiveChatApp.models import LiveChatCronjobTracker, LiveChatCustomer, LiveChatMISDashboard, LiveChatGuestAgentAudit, LiveChatSessionManagement, LiveChatEmailProfile, LiveChatMailerAuditTrail, LiveChatAdminConfig
from EasyChatApp.models import Bot, Channel
from LiveChatApp.constants_email_html import *
from LiveChatApp.constants_email_profile import *

from os import path
from os.path import basename
from urllib.parse import quote


def is_send_mail_required(frequency, email_profile_obj):
    try:
        last_mail_obj = LiveChatMailerAuditTrail.objects.filter(
            profile=email_profile_obj, email_frequency=frequency).order_by('-pk')

        if last_mail_obj:
            tz = pytz.timezone(settings.TIME_ZONE)
            mail_sent_datetime = last_mail_obj[0].sent_datetime.astimezone(
                tz).date()

            if frequency == '5':
                diff = 1
            elif frequency == '1':
                diff = 7
            elif frequency == '2':
                diff = 30
            elif frequency == '3':
                diff = 60
            else:
                diff = 90

            if (datetime.now().astimezone(tz).date() - mail_sent_datetime).days >= diff:
                return True
        else:
            return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_send_mail_required! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return False


def get_start_date(frequency):
    try:
        if frequency == '5':
            diff = 1
        elif frequency == '1':
            diff = 7
        elif frequency == '2':
            diff = 30
        elif frequency == '3':
            diff = 60
        else:
            diff = 90

        return (datetime.now() - timedelta(days=diff)).date()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_start_date! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def cronjob():
    try:

        cronjob_tracker_obj = get_livechat_cronjob_tracker_obj(LIVECHAT_SEND_MAIL_CRONJOB_CONSTANT, LiveChatCronjobTracker)
    
        if cronjob_tracker_obj:
            logger.info("send mail analytics cronjob is already running!",
                        extra={'AppName': 'LiveChat'})
            return
        else:
            create_livechat_cronjob_tracker_obj(LIVECHAT_SEND_MAIL_CRONJOB_CONSTANT, LiveChatCronjobTracker)
        
        email_profile_objs = LiveChatEmailProfile.objects.filter(
            is_deleted=False)

        for email_profile_obj in email_profile_objs:
            try:
                user_obj = email_profile_obj.livechat_user
                admin_config = LiveChatAdminConfig.objects.filter(admin=user_obj)[
                    0]
                if user_obj.is_deleted:
                    continue

                email_receivers = json.loads(email_profile_obj.email_address)
                email_frequency = json.loads(email_profile_obj.email_frequency)

                if len(email_receivers) == 0 or len(email_frequency) == 0:
                    continue

                if admin_config.is_email_notification_enabled:
                    user_obj_list = get_agents_under_this_user(user_obj)

                    for frequency in email_frequency:
                        if not is_send_mail_required(frequency, email_profile_obj):
                            continue

                        mail_html = ""
                        if email_profile_obj.is_graph_parameters_enabled:
                            start_date = (datetime.now() - timedelta(days=7))
                            end_date = (datetime.now() - timedelta(days=1))
                            html_date = "(" + start_date.strftime("%d/%m/%y") + \
                                " - " + \
                                end_date.strftime("%d/%m/%y") + ")"

                            if email_profile_obj.graph_parameters.is_graph_chart_reports_enabled:
                                graph_chart_reports = email_profile_obj.graph_parameters.graph_chart_reports

                                graph_chart_reports_config = get_graph_chart_reports_config(
                                    email_profile_obj, start_date, end_date, user_obj_list, graph_chart_reports, False)

                                encoded_config = quote(
                                    json.dumps(graph_chart_reports_config))
                                graph_chart_reports_url = f'https://quickchart.io/chart?c={encoded_config}'

                                graph_chart_reports_html = get_html_for_graph_chart_reports(
                                    graph_chart_reports_url, "Chat Reports", html_date)

                                mail_html += graph_chart_reports_html

                            if email_profile_obj.graph_parameters.is_graph_interaction_enabled:

                                graph_interactions_config = get_graph_interactions_config(
                                    email_profile_obj, start_date, end_date, user_obj_list, False)

                                encoded_config = quote(
                                    json.dumps(graph_interactions_config))
                                graph_interactions_url = f'https://quickchart.io/chart?c={encoded_config}'

                                graph_interactions_html = get_html_for_graph_interactions(
                                    graph_interactions_url, "Interaction Per Chat", html_date)

                                mail_html += graph_interactions_html

                            if email_profile_obj.graph_parameters.is_graph_avg_handle_time_enabled:

                                graph_avg_handle_time_config = get_graph_avg_handle_time_config(
                                    email_profile_obj, start_date, end_date, user_obj_list, False)

                                encoded_config = quote(json.dumps(
                                    graph_avg_handle_time_config))
                                graph_avg_handle_time_url = f'https://quickchart.io/chart?c={encoded_config}'

                                graph_avg_handle_time_html = get_html_for_graph_avg_handle_time(
                                    graph_avg_handle_time_url, "Average Handle Time", html_date)

                                mail_html += graph_avg_handle_time_html

                        if email_profile_obj.is_table_parameters_enabled:
                            count_variation = json.loads(
                                email_profile_obj.table_parameters.count_variation)

                            channel_list = json.loads(
                                email_profile_obj.table_parameters.channel)
                            table_records = json.loads(
                                email_profile_obj.table_parameters.table_records)

                            if len(table_records) > 0:
                                if len(count_variation) > 0:
                                    mail_html += EMAIL_TABLE_HEADING.replace(
                                        '{}', 'Record Parameters')
                                    mail_html += EMAIL_TABLE_PARAMETERS_START
                                    mail_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                                        '{}', 'Count')

                                    for count in count_variation:
                                        if count == '1':
                                            count_header = 'Daily'
                                        if count == '2':
                                            count_header = 'WTD'
                                        if count == '3':
                                            count_header = 'MTD'
                                        if count == '4':
                                            count_header = 'YTD'
                                        if count == '5':
                                            count_header = 'LMSD'
                                        mail_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                                            '{}', count_header)

                                    mail_html += EMAIL_TABLE_PARAMETERS_HEAD_END

                                    date_wise_table_records_data = get_date_wise_table_records_data(
                                        count_variation, table_records, user_obj_list)

                                    mail_html += get_table_records_html(
                                        table_records, count_variation, TABLE_RECORD_HEADERS, date_wise_table_records_data)

                                    mail_html += EMAIL_TABLE_PARAMETERS_END

                                if len(channel_list) > 0:
                                    if len(count_variation) == 0:
                                        mail_html += EMAIL_TABLE_HEADING.replace(
                                            '{}', 'Record Parameters')
                                    start_date = get_start_date(frequency)
                                    end_date = (datetime.now() -
                                                timedelta(days=1))
                                    html_date = "(" + start_date.strftime("%d/%m/%y") + \
                                        " - " + \
                                        end_date.strftime(
                                        "%d/%m/%y") + ")"
                                    mail_html += EMAIL_TABLE_PARAMETERS_START
                                    mail_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                                        '{}', 'Channel ' + html_date)

                                    for channel in channel_list:
                                        mail_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                                            '{}', channel)

                                    mail_html += EMAIL_TABLE_PARAMETERS_HEAD_END

                                    channel_wise_table_records_data = get_channel_wise_table_records_data(
                                        start_date, end_date, channel_list, table_records, user_obj_list)

                                    mail_html += get_table_records_html(
                                        table_records, channel_list, TABLE_RECORD_HEADERS, channel_wise_table_records_data)

                                    mail_html += EMAIL_TABLE_PARAMETERS_END

                        if email_profile_obj.is_attachment_parameters_enabled or email_profile_obj.is_table_parameters_enabled:
                            attachment_params = json.loads(
                                email_profile_obj.attachment_parameters.attachment_parameters)

                            if len(attachment_params) > 0:
                                start_date = get_start_date(frequency)
                                end_date = (datetime.now() -
                                            timedelta(days=1)).date()
                                mail_html += EMAIL_DOWNLOAD_REPORTS_START
                                if 'performance_report' in attachment_params:

                                    performance_report_path = get_performance_report_path(
                                        start_date, end_date, user_obj, user_obj_list)

                                    mail_html += EMAIL_REPORT_BUTTON.replace(
                                        '()', str(performance_report_path)).replace('{}', 'Performance Report')

                                if 'analytical_report' in attachment_params:
                                    analytical_report_path = get_analytical_report_path(
                                        start_date, end_date, user_obj, user_obj_list)

                                    mail_html += EMAIL_REPORT_BUTTON.replace(
                                        '()', str(analytical_report_path)).replace('{}', 'Combined Analytical Report')

                                if 'customer_report' in attachment_params:
                                    customer_report_path = get_customer_report_path(
                                        start_date, end_date, user_obj, user_obj_list)

                                    mail_html += EMAIL_REPORT_BUTTON.replace(
                                        '()', str(customer_report_path)).replace('{}', 'Customer Centric Report')

                                if email_profile_obj.is_table_parameters_enabled:
                                    mailer_summary_path = get_mailer_report_path(start_date, end_date, user_obj, user_obj_list, email_profile_obj)
                                    mail_html += EMAIL_REPORT_BUTTON.replace(
                                        '()', mailer_summary_path).replace('{}', "Mail Summary")

                                mail_html += EMAIL_DOWNLOAD_REPORTS_END

                            elif email_profile_obj.is_table_parameters_enabled:

                                mail_html += EMAIL_DOWNLOAD_REPORTS_START

                                mailer_summary_path = get_mailer_report_path(start_date, end_date, user_obj, user_obj_list, email_profile_obj)
                                mail_html += EMAIL_REPORT_BUTTON.replace(
                                    '()', mailer_summary_path).replace('{}', "Mail Summary")

                                mail_html += EMAIL_DOWNLOAD_REPORTS_END

                        email_subject = email_profile_obj.email_subject
                        start_date = get_start_date(frequency)
                        end_date = (datetime.now() -
                                    timedelta(days=1)).date()
                        agent_connection_rate = get_agent_connection_rate(
                            email_profile_obj, start_date, end_date, user_obj_list)

                        for email in email_receivers:
                            try:
                                display_date = datetime.now().strftime("%d %B, %Y")

                                email_profile_html = mail_html
                                if email_profile_obj.agent_connection_rate != '':
                                    if agent_connection_rate < int(email_profile_obj.agent_connection_rate):
                                        if(email.find("getcogno.ai") != -1):
                                            email_profile_html = LIVECHAT_AGENT_CONNECTION_RATE.replace(
                                                '{}', str(agent_connection_rate)) + mail_html

                                generate_mail(email_profile_html,
                                              email, email_subject, display_date)
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logger.error("LiveChat Send Mail Analytics > genrate mail: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                    'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                                pass

                        LiveChatMailerAuditTrail.objects.create(
                            profile=email_profile_obj, email_frequency=frequency)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("LiveChat Send Mail Analytics! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                continue
        
        delete_livechat_cronjob_tracker_obj(LIVECHAT_SEND_MAIL_CRONJOB_CONSTANT, LiveChatCronjobTracker)

    except Exception as e:
        delete_livechat_cronjob_tracker_obj(LIVECHAT_SEND_MAIL_CRONJOB_CONSTANT, LiveChatCronjobTracker)
        
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("LiveChat Send Mail Analytics! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        pass
