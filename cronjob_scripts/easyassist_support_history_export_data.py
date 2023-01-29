import os
import sys
import json
import base64

from xlwt import Workbook
from EasyAssistApp.models import *
from EasyAssistApp.utils import logger, \
    get_custom_support_history, \
    get_custom_live_chat_history, \
    get_custom_meeting_support_history, \
    get_custom_unattended_leads_history, \
    get_custom_declined_leads_history, \
    get_custom_followup_leads_history, \
    get_custom_manually_converted_leads_history, \
    get_custom_screen_recording_history, \
    get_audit_trail_dump, \
    get_agent_session_count_attended, \
    get_agent_session_count_unattended, \
    get_agent_audit_trail_dump, \
    get_agent_online_audit_trail_dump

from EasyAssistApp.utils_cronjob import get_easyassist_cronjob_tracker_obj, create_easyassist_cronjob_tracker_obj, \
    delete_easyassist_cronjob_tracker_obj, is_cronjob_tracker_object_expired, delete_and_create_cron_tracker_obj

from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

from cronjob_scripts.cognoai_cronjob_utils import send_cron_error_report
from EasyAssistApp.send_email import send_no_data_found_email

from zipfile import ZipFile
from datetime import datetime, timedelta
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

import pytz

from os import path
from os.path import basename


def send_mail(from_email_id, to_emai_id, message_as_string, from_email_id_password):
    import smtplib
    # The actual sending of the e-mail
    server = smtplib.SMTP('smtp.gmail.com:587')
    # Credentials (if needed) for sending the mail
    password = from_email_id_password
    # Start tls handshaking
    server.starttls()
    # Login to server
    server.login(from_email_id, password)
    # Send mail
    server.sendmail(from_email_id, to_emai_id, message_as_string)
    # Close session
    server.quit()


def send_data_over_email(email, start_date, end_date, sender_name, report_type, email_subject, attachment_file_path):
    try:
        body = """
        <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
          <title>Cogno AI</title>
          <style type="text/css" media="screen">
          </style>
        </head>
        <body>
            <div style="padding:1em;border:0.1em black solid;" class="container">
                <p>
                    Dear {},
                </p>
                <p>
                    We have received a request to provide you with the EasyAssist {} report from {} to {}. Please find relevant attachment below:<br>
                </p>
                <p>&nbsp;</p>
                <p>Technology Development</p>
                <p>Cogno AI</p>
                <a href="https://getcogno.ai/">https://getcogno.ai/</a>
            </div>
        </body>"""

        body = body.format(sender_name, report_type, str(start_date), str(end_date))

        attachment_list = []
        attachment_obj = {
            "base64": "",
            "filename": ""
        }

        file_path = attachment_file_path
        filename = file_path.split('/')[-1]
        # open the file to be sent
        attachment = open(file_path, "rb")

        encoded_str = base64.b64encode(attachment.read())
        encoded_str = encoded_str.decode('utf-8')
        attachment_obj["base64"] = encoded_str
        attachment_obj["filename"] = filename
        attachment_list.append(attachment_obj)
        send_email_to_customer_via_awsses(email, email_subject, body, attachment_list=attachment_list)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_data_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_data_file_over_email(email, start_date, end_date, sender_name, report_type, email_subject, attachment_file_path):
    try:
        body = """
            <head>
              <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
              <title>Cogno AI</title>
              <style type="text/css" media="screen">
              </style>
            </head>
            <body>
                <div style="padding:1em;border:0.1em black solid;" class="container">
                    <p>
                        Dear {},
                    </p>
                    <p>
                        We have received a request to provide you with the EasyAssist {} report from {} to {}. Please click on the link below to download the file.
                    </p>
                    <a href="{}/{}">click here</a>
                    <p>&nbsp;</p>
                    <p>Technology Development</p>
                    <p>Cogno AI</p>
                    <a href="https://getcogno.ai/">https://getcogno.ai/</a>
                </div>
            </body>
        """

        domain = settings.EASYCHAT_HOST_URL
        body = body.format(sender_name, report_type, str(start_date), str(
            end_date), domain, attachment_file_path)

        send_email_to_customer_via_awsses(email, email_subject, body)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_data_file_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_cron_error_report_utils(error_list, function_name):
    try:
        file_name = "easyassist_support_history_export_data"
        send_cron_error_report(error_list, function_name, file_name)
    except Exception as e:
        print(e)


def get_requested_data_for_daily():
    # Last day data
    date_format = "%Y-%m-%d"

    start_date = datetime.now() - timedelta(days=1)
    start_date = start_date.strftime(date_format)
    end_date = start_date

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def get_requested_data_for_week():
    # Last 7 days data
    date_format = "%Y-%m-%d"

    start_date = datetime.now() - timedelta(days=7)
    start_date = start_date.strftime(date_format)
    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.strftime(date_format)

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def get_requested_data_for_month():
    # Last 30 days data
    date_format = "%Y-%m-%d"

    start_date = datetime.now() - timedelta(days=30)
    start_date = start_date.strftime(date_format)
    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.strftime(date_format)

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def get_file_download_path(file_relative_path, access_token):

    file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
        file_path="/" + file_relative_path, is_public=True, access_token=access_token)

    return 'easy-assist/download-file/' + str(file_access_management_obj.key)


def cronjob():

    easyassist_cronjob_tracker_obj = get_easyassist_cronjob_tracker_obj(EXPORT_SUPPORT_HISTORY_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    if easyassist_cronjob_tracker_obj:
        if is_cronjob_tracker_object_expired(easyassist_cronjob_tracker_obj):
            delete_and_create_cron_tracker_obj(
                EXPORT_SUPPORT_HISTORY_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
        else:
            logger.info("easyassist_support_history_export_data cronjob is already running!",
                        extra={'AppName': 'EasyAssist'})
            return
    else:
        create_easyassist_cronjob_tracker_obj(EXPORT_SUPPORT_HISTORY_CRONJOB_CONSTANT, EasyAssistCronjobTracker)

    create_excel_sales_support_history_cronjob()
    create_excel_sales_livechat_history_cronjob()
    create_excel_unattended_leads_history_cronjob()
    create_excel_declined_leads_history_cronjob()
    create_excel_followup_leads_history_cronjob()
    create_excel_manually_converted_leads_history_cronjob()
    create_excel_audit_trail_cronjob()
    create_excel_agent_audit_trail_cronjob()
    create_excel_agent_online_audit_trail_cronjob()
    create_excel_screen_recording_history_cronjob()
    create_excel_meeting_support_history_cronjob()
    delete_easyassist_cronjob_tracker_obj(EXPORT_SUPPORT_HISTORY_CRONJOB_CONSTANT, EasyAssistCronjobTracker)


def create_excel_sales_support_history_cronjob():
    cron_error_list = []
    try:

        try:
            print("create_excel_sales_support_history_cronjob")
            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/support-history/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/support-history/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/support-history/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/support-history/' + str(agent.user.username))

                    get_custom_support_history(
                        get_requested_data_for_daily(), agent, CobrowseIO)

                    get_custom_support_history(
                        get_requested_data_for_week(), agent, CobrowseIO)

                    get_custom_support_history(
                        get_requested_data_for_month(), agent, CobrowseIO)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Supprt history Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                 'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Supprt history Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="support-history").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                relative_zip_file_path = get_custom_support_history(filter_param, export_date_request.agent, CobrowseIO)
                if relative_zip_file_path != NO_DATA:
                    file_download_path = get_file_download_path(relative_zip_file_path, export_date_request.agent.get_access_token_obj())
                else:
                    file_download_path = None

                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

                email_str = filter_param["email"]
                email_list = [email.strip() for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    email_subject = "EasyAssist Support History | " + str(username)
                    if file_download_path:
                        send_data_file_over_email(email_id, start_date, end_date, username, "support history", email_subject, file_download_path)
                    else:
                        send_no_data_found_email(email_id, start_date, end_date, username, "support history", email_subject)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Support history! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_sales_support_history_cronjob")


def create_excel_sales_livechat_history_cronjob():
    cron_error_list = []
    try:

        try:
            print("create_excel_sales_livechat_history_cronjob")
            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/live-chat-history/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/live-chat-history/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/live-chat-history/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/live-chat-history/' + str(agent.user.username))

                    get_custom_live_chat_history(
                        get_requested_data_for_daily(), agent, CobrowseIO, CobrowseIOInvitedAgentsDetails, CobrowseIOTransferredAgentsLogs, CobrowseChatHistory)

                    get_custom_live_chat_history(
                        get_requested_data_for_week(), agent, CobrowseIO, CobrowseIOInvitedAgentsDetails, CobrowseIOTransferredAgentsLogs, CobrowseChatHistory)

                    get_custom_live_chat_history(
                        get_requested_data_for_month(), agent, CobrowseIO, CobrowseIOInvitedAgentsDetails, CobrowseIOTransferredAgentsLogs, CobrowseChatHistory)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Livechat history Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                 'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Livechat history Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="live-chat-history").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                relative_zip_file_path = get_custom_live_chat_history(filter_param, export_date_request.agent, CobrowseIO, CobrowseIOInvitedAgentsDetails, CobrowseIOTransferredAgentsLogs, CobrowseChatHistory)
                if relative_zip_file_path != NO_DATA:
                    file_download_path = get_file_download_path(relative_zip_file_path, export_date_request.agent.get_access_token_obj())
                else:
                    file_download_path = None

                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

                email_str = filter_param["email"]
                email_list = [email.strip() for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    email_subject = "EasyAssist Livechat History | " + str(username)
                    if file_download_path:
                        send_data_file_over_email(email_id, start_date, end_date, username, "livechat history", email_subject, file_download_path)
                    else:
                        send_no_data_found_email(email_id, start_date, end_date, username, "livechat history", email_subject)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Livechat history! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_sales_livechat_history_cronjob")


def create_excel_meeting_support_history_cronjob():
    cron_error_list = []
    try:

        try:
            print("create_excel_meeting_support_history_cronjob")
            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/MeetingSupportHistory/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/MeetingSupportHistory/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/MeetingSupportHistory/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/MeetingSupportHistory/' + str(agent.user.username))

                    get_custom_meeting_support_history(
                        get_requested_data_for_daily(), agent, CobrowseVideoConferencing, CobrowseVideoAuditTrail, CobrowsingFileAccessManagement)

                    get_custom_meeting_support_history(
                        get_requested_data_for_week(), agent, CobrowseVideoConferencing, CobrowseVideoAuditTrail, CobrowsingFileAccessManagement)

                    get_custom_meeting_support_history(
                        get_requested_data_for_month(), agent, CobrowseVideoConferencing, CobrowseVideoAuditTrail, CobrowsingFileAccessManagement)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Meeting Support history Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Meeting Support history Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="meeting-support-history").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                relative_zip_file_path = get_custom_meeting_support_history(filter_param, export_date_request.agent, CobrowseVideoConferencing, CobrowseVideoAuditTrail, CobrowsingFileAccessManagement)
                if relative_zip_file_path != NO_DATA:
                    file_download_path = get_file_download_path(relative_zip_file_path, export_date_request.agent.get_access_token_obj())
                else:
                    file_download_path = None

                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

                email_str = filter_param["email"]
                email_list = [email.strip() for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    email_subject = "EasyAssist Support History | " + str(username)
                    if file_download_path:
                        send_data_file_over_email(email_id, start_date, end_date, username, "meeting support history", email_subject, file_download_path)
                    else:
                        send_data_file_over_email(email_id, start_date, end_date, username, "meeting support history", email_subject, file_download_path)
                
                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Meeting Support history! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_meeting_support_history_cronjob")


def create_excel_unattended_leads_history_cronjob():
    cron_error_list = []
    try:

        try:
            print("create_excel_unattended_leads_history_cronjob")

            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/UnattendedLeads/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/UnattendedLeads/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue
                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/UnattendedLeads/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/UnattendedLeads/' + str(agent.user.username))

                    get_custom_unattended_leads_history(
                        get_requested_data_for_daily(), agent, CobrowseIO)

                    get_custom_unattended_leads_history(
                        get_requested_data_for_week(), agent, CobrowseIO)

                    get_custom_unattended_leads_history(
                        get_requested_data_for_month(), agent, CobrowseIO)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Unattended Leads Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Unattended Leads Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="unattended-lead-history").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                relative_zip_file_path = get_custom_unattended_leads_history(filter_param, export_date_request.agent, CobrowseIO)
                if relative_zip_file_path != NO_DATA:
                    file_download_path = get_file_download_path(relative_zip_file_path, export_date_request.agent.get_access_token_obj())
                else:
                    file_download_path = None

                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

                email_str = filter_param["email"]
                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    email_subject = "EasyAssist Support History | " + str(username)
                    if file_download_path:
                        send_data_file_over_email(email_id, start_date, end_date, username, "unattended leads history", email_subject, file_download_path)
                    else:
                        send_no_data_found_email(email_id, start_date, end_date, username, "unattended leads history", email_subject)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Unattended Leads history! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_unattended_leads_history_cronjob")


def create_excel_declined_leads_history_cronjob():
    cron_error_list = []
    try:

        try:
            print("create_excel_declined_leads_history_cronjob")

            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/DeclinedLeads/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/DeclinedLeads/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)

            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/DeclinedLeads/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/DeclinedLeads/' + str(agent.user.username))

                    get_custom_declined_leads_history(
                        get_requested_data_for_daily(), agent, CobrowseIO)

                    get_custom_declined_leads_history(
                        get_requested_data_for_week(), agent, CobrowseIO)

                    get_custom_declined_leads_history(
                        get_requested_data_for_month(), agent, CobrowseIO)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Declined Leads Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Declined Leads Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="declined-lead-history").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                relative_file_path = get_custom_declined_leads_history(filter_param, export_date_request.agent, CobrowseIO)
                if relative_file_path != NO_DATA:
                    file_download_path = get_file_download_path(relative_file_path, export_date_request.agent.get_access_token_obj())
                else:
                    file_download_path = None

                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

                email_str = filter_param["email"]
                email_list = [email.strip() for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    email_subject = "EasyAssist Support History | " + str(username)
                    if file_download_path:
                        send_data_file_over_email(email_id, start_date, end_date, username, "declined leads history", email_subject, file_download_path)
                    else:
                        send_no_data_found_email(email_id, start_date, end_date, username, "declined leads history", email_subject)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Declined Leads history! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_declined_leads_history_cronjob")


def create_excel_followup_leads_history_cronjob():
    cron_error_list = []
    try:

        try:
            print("create_excel_followup_leads_history_cronjob")
            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/FollowupLeads/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/FollowupLeads/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/FollowupLeads/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/FollowupLeads/' + str(agent.user.username))

                    get_custom_followup_leads_history(
                        get_requested_data_for_daily(), agent, CobrowseIO)

                    get_custom_followup_leads_history(
                        get_requested_data_for_week(), agent, CobrowseIO)

                    get_custom_followup_leads_history(
                        get_requested_data_for_month(), agent, CobrowseIO)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("FollowUp Leads Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("FollowUp Leads Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="followup-lead-history").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                relative_zip_file_path = get_custom_followup_leads_history(filter_param, export_date_request.agent, CobrowseIO)
                if relative_zip_file_path != NO_DATA:
                    file_download_path = get_file_download_path(relative_zip_file_path, export_date_request.agent.get_access_token_obj())
                else:
                    file_download_path = None

                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

                email_str = filter_param["email"]
                email_list = [email.strip() for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    email_subject = "EasyAssist Support History | " + str(username)
                    if file_download_path:
                        send_data_file_over_email(email_id, start_date, end_date, username, "follow-up leads history", email_subject, file_download_path)
                    else:
                        send_no_data_found_email(email_id, start_date, end_date, username, "follow-up leads history", email_subject)
                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("FollowUp Leads history! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_followup_leads_history_cronjob")


def create_excel_manually_converted_leads_history_cronjob():
    cron_error_list = []
    try:

        try:
            print("create_excel_manually_converted_leads_history_cronjob")
            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/manually-converted-leads/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/manually-converted-leads/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/manually-converted-leads/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/manually-converted-leads/' + str(agent.user.username))

                    get_custom_manually_converted_leads_history(
                        get_requested_data_for_daily(), agent, CobrowseIO)

                    get_custom_manually_converted_leads_history(
                        get_requested_data_for_week(), agent, CobrowseIO)

                    get_custom_manually_converted_leads_history(
                        get_requested_data_for_month(), agent, CobrowseIO)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Manually Converted Leads Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Manually Converted Leads Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="manually-converted-leads").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                relative_zip_file_path = get_custom_manually_converted_leads_history(filter_param, export_date_request.agent, CobrowseIO)
                if relative_zip_file_path != NO_DATA:
                    file_download_path = get_file_download_path(relative_zip_file_path, export_date_request.agent.get_access_token_obj())
                else:
                    file_download_path = None

                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

                email_str = filter_param["email"]
                email_list = [email.strip() for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    email_subject = "EasyAssist Support History | " + str(username)
                    if file_download_path:
                        send_data_file_over_email(email_id, start_date, end_date, username, "manually converted leads history", email_subject, file_download_path)
                    else:
                        send_no_data_found_email(email_id, start_date, end_date, username, "manually converted leads history", email_subject)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Manually Converted Leads history! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_manually_converted_leads_history_cronjob")


def create_excel_screen_recording_history_cronjob():
    cron_error_list = []
    try:
        try:
            print("create_excel_screen_recording_history_cronjob")
            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/ScreenRecordingHistory/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/ScreenRecordingHistory/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/ScreenRecordingHistory/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/ScreenRecordingHistory/' + str(agent.user.username))

                    get_custom_screen_recording_history(
                        get_requested_data_for_daily(), agent, CobrowseScreenRecordingAuditTrail)

                    get_custom_screen_recording_history(
                        get_requested_data_for_week(), agent, CobrowseScreenRecordingAuditTrail)

                    get_custom_screen_recording_history(
                        get_requested_data_for_month(), agent, CobrowseScreenRecordingAuditTrail)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("FollowUp Leads Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("FollowUp Leads Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="screen-recording-history").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                relative_zip_file_path = get_custom_screen_recording_history(filter_param, export_date_request.agent, CobrowseScreenRecordingAuditTrail)
                file_download_path = get_file_download_path(relative_zip_file_path, export_date_request.agent.get_access_token_obj())

                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

                email_str = filter_param["email"]
                email_list = [email.strip() for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    email_subject = "EasyAssist Support History | " + str(username)
                    send_data_file_over_email(email_id, start_date, end_date, username, "screen recording history", email_subject, file_download_path)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Screen recording history! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_screen_recording_history_cronjob")


def create_excel_audit_trail_cronjob():
    cron_error_list = []
    try:
        try:
            print("create_excel_audit_trail_cronjob")
            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AuditTrail/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AuditTrail/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AuditTrail/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AuditTrail/' + str(agent.user.username))

                    get_audit_trail_dump(
                        get_requested_data_for_daily(), agent, CobrowsingAuditTrail)

                    get_audit_trail_dump(
                        get_requested_data_for_week(), agent, CobrowsingAuditTrail)

                    get_audit_trail_dump(
                        get_requested_data_for_month(), agent, CobrowsingAuditTrail)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Audit Trail Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Audit Trail Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="audit-trail").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                relative_zip_file_path = get_audit_trail_dump(filter_param, export_date_request.agent, CobrowsingAuditTrail)
                file_download_path = get_file_download_path(relative_zip_file_path, export_date_request.agent.get_access_token_obj())

                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

                email_str = filter_param["email"]
                email_list = [email.strip() for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    email_subject = "EasyAssist Audit Trail | " + str(username)
                    send_data_file_over_email(email_id, start_date, end_date, username, "Audit Trail", email_subject, file_download_path)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Audit trail! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_audit_trail_cronjob")


def create_excel_agent_audit_trail_cronjob():
    cron_error_list = []
    try:
        try:
            print("create_excel_agent_audit_trail_cronjob")
            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AgentAuditTrail/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AgentAuditTrail/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AgentAuditTrail/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AgentAuditTrail/' + str(agent.user.username))

                    get_agent_audit_trail_dump(
                        get_requested_data_for_daily(), agent, CobrowsingAuditTrail, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)

                    get_agent_audit_trail_dump(
                        get_requested_data_for_week(), agent, CobrowsingAuditTrail, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)

                    get_agent_audit_trail_dump(
                        get_requested_data_for_month(), agent, CobrowsingAuditTrail, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Agent Audit Trail Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Agent Audit Trail Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="agent-audit-trail").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                relative_zip_file_path = get_agent_audit_trail_dump(filter_param, export_date_request.agent, CobrowsingAuditTrail, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)
                file_download_path = get_file_download_path(relative_zip_file_path, export_date_request.agent.get_access_token_obj())

                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

                email_str = filter_param["email"]
                email_list = [email.strip() for email in email_str.split(",") if email != ""]
                email_subject = "EasyAssist Audit Trail | " + str(username)

                for email_id in email_list:
                    send_data_file_over_email(email_id, start_date, end_date, username, "Agent Audit Trail", email_subject, file_download_path)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Audit trail! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_agent_audit_trail_cronjob")


def create_excel_agent_online_audit_trail_cronjob():
    cron_error_list = []
    try:
        date_format = "%Y-%m-%d"

        try:
            print("create_excel_agent_online_audit_trail_cronjob")

            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AgentOnlineAuditTrail/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AgentOnlineAuditTrail/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    if agent.role not in ["admin", "supervisor", "admin_ally"] and agent.is_switch_allowed == False:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AgentOnlineAuditTrail/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/AgentOnlineAuditTrail/' + str(agent.user.username))

                    # Check whether file exist for last 1, 7 and 30 days. If not create an excel file for the same.
                    date_format = "%Y-%m-%d"
                    for day in [1, 7, 30]:
                        start_date = datetime.now() - timedelta(days=day)
                        start_date = start_date.strftime(date_format)
                        end_date = datetime.now() - timedelta(days=1)
                        end_date = end_date.strftime(date_format)

                        file_path = settings.SECURE_MEDIA_ROOT + "EasyAssistApp/AgentOnlineAuditTrail/" + \
                            str(agent.user.username) + \
                            "/agent_online_audit_trail_" + str(start_date) + "-" + str(end_date) + ".xls"

                        if not os.path.exists(file_path):
                            requested_data = {
                                "startdate": start_date,
                                "enddate": end_date,
                            }
                            get_agent_online_audit_trail_dump(
                                requested_data, agent, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Agent Online Audit Trail Datadump %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Agent Online Audit Trail Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="agent-online-audit-trail").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]

                get_agent_online_audit_trail_dump(
                    filter_param, export_date_request.agent, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)
                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                file_path = "EasyAssistApp/AgentOnlineAuditTrail/" + str(export_date_request.agent.user.username) + \
                    "/agent_online_audit_trail_" + str(start_date) + "-" + str(end_date) + '.xls'
                file_path = settings.SECURE_MEDIA_ROOT + file_path

                if not os.path.exists(file_path):
                    continue

                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")
                email_subject = "Cobrowsing Agent Productivity Report"

                for email_id in email_list:
                    send_data_over_email(email_id, start_date, end_date, username, "agent online", email_subject, file_path)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Agent Online Audit Trail %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(cron_error_list, "create_excel_agent_online_audit_trail_cronjob")
