import os
import sys
import json
import base64

from AuditTrailApp.models import *
from AuditTrailApp.utils import logger, \
    get_custom_audit_trail_dump
from EasyChatApp.models import User

from cronjob_scripts.cognoai_cronjob_utils import send_cron_error_report

from datetime import datetime, timedelta
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses


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


def send_data_over_email(email, start_date, end_date, sender_name, report_type, attachment_file_path):
    try:

        config_obj = get_developer_console_settings()

        body = """<head> <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> <title>Cogno AI</title> 
        <style type="text/css" media="screen"> </style> </head> <body> <div style="padding:1em;border:0.1em black 
        solid;" class="container"> <p> Dear {}, </p> <p> We have received a request to provide you with the 
        AuditTrail {} report from {} to {}. Please find relevant attachment below:<br> </p> <p>&nbsp;</p>"""

        body += config_obj.custom_report_template_signature

        body += """</div></body>"""

        body = body.format(sender_name, report_type, str(start_date), str(end_date))

        """With this function we send out our html email"""
        to_email_id = email

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

        send_email_to_customer_via_awsses(to_email_id, "Cobrowsing Agent Productivity Report", body, attachment_list=attachment_list)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_data_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})


def send_cron_error_report_utils(error_list, function_name):
    try:
        file_name = "audit_trail_app_cronjob"
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

    return 'audit-trail/download-file/' + str(file_access_management_obj.key)


def cronjob():
    create_excel_audit_trail_history()


def create_excel_audit_trail_history():
    cron_error_list = []
    try:
        domain = settings.EASYCHAT_HOST_URL

        try:
            print("create_excel_audit_trail_history")

            user_objs = User.objects.filter(is_staff=True)
            user_objs |= User.objects.filter(username__endswith="@getcogno.ai")
            user_objs |= User.objects.filter(username__endswith="@allincall.in")

            for user_obj in user_objs:
                get_custom_audit_trail_dump(
                    get_requested_data_for_daily(), user_obj, CognoAIAuditTrail)
                get_custom_audit_trail_dump(
                    get_requested_data_for_week(), user_obj, CognoAIAuditTrail)
                get_custom_audit_trail_dump(
                    get_requested_data_for_month(), user_obj, CognoAIAuditTrail)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Audit Trail Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'AuditTrailApp'})

        for export_date_request in ExportRequest.objects.filter(is_completed=False, export_type="AuditTrailExport"):
            try:
                requested_data = get_requested_data_custom(export_date_request.start_date, export_date_request.end_date)
                relative_file_path = get_custom_audit_trail_dump(requested_data, export_date_request.user,
                                                                 CognoAIAuditTrail)
                file_download_path = get_file_download_path(relative_file_path)

                start_date = datetime.strftime(export_date_request.start_date, "%d-%m-%Y")
                end_date = datetime.strftime(export_date_request.end_date, "%d-%m-%Y")

                username = export_date_request.user.username

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
                                We have received a request to provide you with the Audit Trail data dump from {} to {}. Please click on the link below to download the file.
                            </p>
                            <a href="{}/{}">click here</a>
                            <p>&nbsp;</p>"""

                config_obj = get_developer_console_settings()

                body += config_obj.custom_report_template_signature
                
                body += """</div></body>"""

                email_str = export_date_request.email_id
                email_list = [email.strip() for email in email_str.split(",") if email != ""]

                for email_id in email_list:
                    body = body.format(username, str(start_date), str(
                        end_date), domain, file_download_path)

                    send_email_to_customer_via_awsses(email_id, "Audit Trail | " + str(username), body)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Audit Trail! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'AuditTrailApp'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})

    send_cron_error_report_utils(cron_error_list, "create_excel_audit_trail_history")
