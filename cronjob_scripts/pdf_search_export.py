from EasyChatApp.models import Bot, User
from EasyChatApp.utils_parse_pdf_search import parse_pdf_details

from EasySearchApp.constants import PDF_SEARCH_INDEXING_STATUS
from EasySearchApp.models import EasyPDFSearcher, EasyPDFSearcherAnalytics, PDFSearchExportRequest
from cronjob_scripts.EasyChatAppCronjobUtilityFunctions.utils_cronjob import *

from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

from django.db.models import Q
from django.conf import settings

import os
import sys
import pytz
import json
import base64

from xlwt import Workbook
from EasyChatApp.utils import logger
from zipfile import ZipFile
from datetime import datetime, timedelta

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from os import path
from os.path import basename


def send_mail(from_email_id, to_email_id, message_as_string, from_email_id_password):
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
    server.sendmail(from_email_id, to_email_id, message_as_string)
    # Close session
    server.quit()


def get_email_body(email_id, start_date, end_date, file_path):
    body_sentence = 'We have received a request to provide you with the PDF Search report from {} to {}'

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
                """ + body_sentence + """. Please click on the link below to download the file.
            </p>
            <a href="{}">click here</a>
            <p>&nbsp;</p>"""

    config = get_developer_console_settings()

    body += config.custom_report_template_signature

    body += """</div></body>"""

    start_date = datetime.strftime(start_date, "%d-%m-%Y")
    end_date = datetime.strftime(end_date, "%d-%m-%Y")
    body = body.format(email_id, str(start_date), str(
        end_date), file_path)

    return body


def send_pdf_search_report_over_email(email_id, start_date, end_date, file_path):
    try:
        body = get_email_body(email_id, start_date, end_date, file_path)

        """With this function we send out our html email"""

        attachment_list = []
        attachment_obj = {
            "base64": "",
            "filename": ""
        }

        filename = file_path.split('/')[-1]
        attachment = open(file_path, "rb")

        encoded_str = base64.b64encode(attachment.read())
        encoded_str = encoded_str.decode('utf-8')
        attachment_obj["base64"] = encoded_str
        attachment_obj["filename"] = filename
        attachment_list.append(attachment_obj)

        send_email_to_customer_via_awsses(
            email_id, "PDF Search Report", body, attachment_list=attachment_list)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_pdf_search_report_over_email: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_default_columns(sheet):
    sheet.write(0, 0, "File Name")
    sheet.write(0, 1, "Date and Time")
    sheet.write(0, 2, "Status")
    sheet.write(0, 3, "Click Count")
    sheet.write(0, 4, "Search Count")
    sheet.write(0, 5, "Open Rate")


def get_valid_status(status):
    updated_status = status
    if status == "active":
        updated_status = "Active"
    elif status == "inactive":
        updated_status = "Inactive"
    elif status == "indexing":
        updated_status = "Indexing"
    elif status == "not_indexed":
        updated_status = "Not Indexed"
    elif status == "indexed":
        updated_status = "Indexed"
    return updated_status


def get_pdf_file_source(pdf_search_obj):
    file_src = settings.EASYCHAT_HOST_URL + \
        "/chat/download-file/" + str(pdf_search_obj.file_path)

    return file_src


def add_pdf_search_details(sheet, row_index, pdf_search_obj):

    try:
        pdf_data = parse_pdf_details(pdf_search_obj, EasyPDFSearcherAnalytics)

        name = pdf_data["name"]
        open_rate = pdf_data["open_rate"]
        click_count = pdf_data["click_count"]
        search_count = pdf_data["search_count"]
        create_datetime = pdf_data["create_datetime"]
        status = get_valid_status(pdf_data["status"])

        open_rate = "{open_rate}%".format(open_rate=open_rate)

        sheet.write(row_index, 0, name)
        sheet.write(row_index, 1, create_datetime)
        sheet.write(row_index, 2, status)
        sheet.write(row_index, 3, click_count)
        sheet.write(row_index, 4, search_count)
        sheet.write(row_index, 5, open_rate)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_pdf_search_details: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def generate_report(pdf_search_objs, bot_obj, user_obj, start_date, end_date):
    try:
        user_name = user_obj.username
        bot_id = str(bot_obj.pk)

        relative_folder_path = 'pdf_search_reports/bot-{bot_id}/'.format(
            bot_id=bot_id)
        absolute_folder_path = settings.MEDIA_ROOT + relative_folder_path

        if not os.path.exists(absolute_folder_path):
            os.makedirs(absolute_folder_path)

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("PDF Search Report")

        add_default_columns(sheet1)
        row_index = 1
        for pdf_search_obj in pdf_search_objs:
            add_pdf_search_details(sheet1, row_index, pdf_search_obj)
            row_index += 1

        date_range = "{start_date}__{end_date}".format(
            start_date=str(start_date),
            end_date=str(end_date))

        file_name = "{user_name}_{date_range}.xls".format(
            user_name=user_name,
            date_range=date_range)

        absolute_file_path = absolute_folder_path + file_name

        test_wb.save(absolute_file_path)

        return absolute_file_path
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("generate_report: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def cronjob():
    cronjob_id = "easychat_pdf_search_export_cron"
    cronjob_is_running, cronjob_objs = check_if_cronjob_is_running(cronjob_id)
    if cronjob_is_running:
        return
    try:
        # domain = settings.EASYCHAT_HOST_URL

        message_history_datadump_log = open(
            "log/pdf_search_export.log", "a")

        if not os.path.exists(settings.MEDIA_ROOT + 'pdf_search_reports'):
            os.makedirs(settings.MEDIA_ROOT + 'pdf_search_reports')

        export_requests = PDFSearchExportRequest.objects.filter(
            is_completed=False)

        for export_request in export_requests:
            start_date = export_request.start_date
            end_date = export_request.end_date
            user = export_request.user

            pdf_search_objs = EasyPDFSearcher.objects.filter(
                bot_obj=export_request.bot,
                created_datetime__date__gte=start_date,
                created_datetime__date__lte=end_date,
                is_deleted=False).filter(~Q(status=PDF_SEARCH_INDEXING_STATUS))

            file_path = generate_report(
                pdf_search_objs, export_request.bot, user, start_date, end_date)

            email_id = export_request.email_id

            send_pdf_search_report_over_email(
                email_id, start_date, end_date, file_path)

            export_request.is_completed = True
            export_request.save()

        message_history_datadump_log.close()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    complete_cronjob_execution(cronjob_objs)
