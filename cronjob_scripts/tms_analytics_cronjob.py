import os
import sys
import json

from EasyTMSApp.models import *
from EasyTMSApp.utils import logger, get_custom_analytics_export
from cronjob_scripts.EasyChatAppCronjobUtilityFunctions.utils_cronjob import *

from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

from cronjob_scripts.cognoai_cronjob_utils import send_cron_error_report

from datetime import datetime, timedelta
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


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


def send_cron_error_report_utils(error_list, function_name):
    try:
        file_name = "tms_analytics_cronjob"
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


def get_requested_data_custom(start_date, end_date):
    date_format = "%Y-%m-%d"

    start_date = start_date.strftime(date_format)
    end_date = end_date.strftime(date_format)

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def get_file_download_path(file_relative_path):
    file_access_management_obj = FileAccessManagement.objects.create(
        file_path="/" + file_relative_path)

    return 'tms/download-file/' + str(file_access_management_obj.key)


def cronjob():
    create_tms_analytics_excel()


def create_tms_analytics_excel():
    cronjob_id = "easychat_tms_analytics_cron"
    cronjob_is_running, cronjob_objs = check_if_cronjob_is_running(cronjob_id)
    if cronjob_is_running:
        return
    cron_error_list = []
    try:
        domain = settings.EASYCHAT_HOST_URL

        config_obj = get_developer_console_settings()

        try:
            agents = Agent.objects.filter(role__in=["admin", "supervisor"])

            for agent in agents:
                get_custom_analytics_export(
                    get_requested_data_for_daily(), agent)
                get_custom_analytics_export(
                    get_requested_data_for_week(), agent)
                get_custom_analytics_export(
                    get_requested_data_for_month(), agent)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Analytics Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyTMS'})

        for export_date_request in ExportRequest.objects.filter(is_completed=False, export_type="AnalyticsExport"):
            try:
                requested_data = get_requested_data_custom(export_date_request.start_date, export_date_request.end_date)
                relative_file_path = get_custom_analytics_export(requested_data, export_date_request.agent)
                file_download_path = get_file_download_path(relative_file_path)

                start_date = datetime.strftime(export_date_request.start_date, "%d-%m-%Y")
                end_date = datetime.strftime(export_date_request.end_date, "%d-%m-%Y")

                username = export_date_request.agent.user.username

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
                                We have received a request to provide you with the Cogno Desk Analytics from {} to {}. Please click on the link below to download the file.
                            </p>
                            <a href="{}/{}">click here</a>
                            <p>&nbsp;</p>"""
                        
                body += config_obj.custom_report_template_signature

                body += """</div></body>"""

                email_str = export_date_request.email_id
                email_list = [email.strip() for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    body = body.format(username, str(start_date), str(
                        end_date), domain, file_download_path)
                    send_email_to_customer_via_awsses(email_id, "Cogno Desk Analytics | " + str(username), body)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Analytics Dump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'EasyTMS'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

    send_cron_error_report_utils(cron_error_list, "create_tms_analytics_excel")
    complete_cronjob_execution(cronjob_objs)
