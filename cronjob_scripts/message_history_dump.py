import os
import sys
import json
import csv
import pandas as pd
from django.conf import settings
from EasyChatApp.utils import logger
from email.mime.text import MIMEText
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from EasyChatApp.models import Bot, ExportMessageHistoryRequest, MISDashboard, Config, UserSessionHealth
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses
from EasyChatApp.utils_analytics import return_mis_objects_excluding_blocked_sessions


def add_default_values(writer):

    try:
        headings = ["TimeStamp",
                    "User Query",
                    "Bot",
                    "Bot Response",
                    "Message Time",
                    "Intent Recognized",
                    "User ID",
                    "Session ID",
                    "Channel",
                    "User Feedback",
                    "Intent Feedback",
                    "Client City",
                    "Client State",
                    "Client Pincode",
                    "Sentiment",
                    "Type-in query",
                    "Variation Responsible",
                    "Match Percentage",
                    "Tags",
                    ]
        writer.writerow(headings)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("message history dump add_default_values! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_data(writter, message_history, bot_name):
    try:
        for message in message_history:
            add_data_row_into_csv(writter, message, bot_name)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_last_day_data %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_data_row_into_csv(writer, message, bot_name):
    try:
        message_date = message.date.date()

        row_data = [message_date]

        row_data.append(message.get_message_received())
        row_data.append(bot_name)
        row_data.append(message.get_bot_response())
        row_data.append(message.get_datetime())

        intent_name = message.intent_name
        if intent_name:
            row_data.append(intent_name)
        else:
            profanity_response = message.get_intent_name_for_profanity_or_emoji_response()
            if profanity_response:
                row_data.append(
                    profanity_response)
            else:
                row_data.append('-')

        row_data.append(message.get_user_id())
        row_data.append(message.session_id)
        row_data.append(message.get_channel_name())

        if message.feedback_comment:
            row_data.append(message.feedback_comment)
        else:
            row_data.append('-')

        if message.is_helpful_field == "1":
            row_data.append('Positive')
        elif message.is_helpful_field == "-1":
            row_data.append('Negative')
        else:
            row_data.append('-')

        if message.client_city:
            row_data.append(message.client_city)
        else:
            row_data.append('-')

        if message.client_state:
            row_data.append(message.client_state)
        else:
            row_data.append('-')

        if message.client_pincode:
            row_data.append(message.client_pincode)
        else:
            row_data.append('-')

        row_data.append(message.get_sentiment())
        row_data.append(str(message.is_manually_typed_query).upper())
        row_data.append(message.training_question)

        if message.match_percentage == -1:
            message.match_percentage = ""
        row_data.append(message.match_percentage)

        if not message.flagged_queries_positive_type:
            message.flagged_queries_positive_type = "-"

        row_data.append(message.get_flagged_queries_positive_type_display())

        writer.writerow(row_data)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_data_row_into_csv %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_single_day_file_path(bot_obj, day):

    file_path = settings.MEDIA_ROOT + 'message-history/bot-' + \
        str(bot_obj.pk) + "/message_history_of_date_" + str(day.date()) + ".csv"

    return file_path


def create_single_messgae_history_csv_file(file_path, message_history_objs, bot_obj, date_of_file):
    try:
        last_day_file = open(file_path, 'w')

        writer = csv.writer(last_day_file)

        add_default_values(writer)

        add_data(writer, message_history_objs, bot_obj.name)

        last_day_file.close()

        logger.info("message history dump file created for bot and date" + str(bot_obj.name) + str(date_of_file), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_single_day_messgae_history_csv_file %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def maintain_last_30_days_message_history_csv_files(bot_obj):
    try:
        if not os.path.exists(settings.MEDIA_ROOT + 'message-history/bot-' + str(bot_obj.pk)):
            os.makedirs(settings.MEDIA_ROOT +
                        'message-history/bot-' + str(bot_obj.pk))

        total_x_days = 31
        today = datetime.now()

        for last_x_day in range(1, total_x_days + 2):

            if last_x_day == total_x_days + 1:
                day_x = today - timedelta(last_x_day)
                day_x_file_path = get_single_day_file_path(bot_obj, day_x)

                if os.path.exists(day_x_file_path):
                    cmd = "rm " + day_x_file_path
                    os.system(cmd)
                break

            last_date = today - timedelta(last_x_day)
            last_date_file_path = get_single_day_file_path(bot_obj, last_date)
            file_already_exists = False

            if os.path.exists(last_date_file_path):
                file_already_exists = True

            if file_already_exists:
                continue

            message_history_objs = MISDashboard.objects.filter(
                bot=bot_obj, creation_date=last_date.date()).order_by('pk')

            message_history_objs = return_mis_objects_excluding_blocked_sessions(message_history_objs, UserSessionHealth)

            create_single_messgae_history_csv_file(
                last_date_file_path, message_history_objs.iterator(), bot_obj, last_date.date())

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_last_31_days_csv_files %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def merge_list_of_files_in_a_given_file(existing_file_list, merged_file_path):
    try:
        import time
        start_time = time.time()

        with open(merged_file_path, "wb") as fout:
            # first file:
            with open(existing_file_list[0], "rb") as f:
                fout.write(f.read())
            # now the rest:
            for file_no in range(1, len(existing_file_list)):
                with open(existing_file_list[file_no], "rb") as f:
                    next(f)  # skip the header
                    fout.write(f.read())

        logger.info("total time taken for merge_list_of_files_in_a_given_file  %s", str(time.time() - start_time), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("merge_list_of_files_in_a_given_file %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_last_one_day_file(bot_obj, today):
    try:

        yesterday = today - timedelta(1)

        yest_file_path = get_single_day_file_path(bot_obj, yesterday)

        dir_path = settings.MEDIA_ROOT + \
            'message-history/bot-' + str(bot_obj.pk)

        last_one_day_file_path = dir_path + "/MessageHistoryLastOneDay_" + \
            yesterday.strftime("%d-%m-%Y") + ".csv"

        if not os.path.exists(yest_file_path):

            message_history_objs = MISDashboard.objects.filter(
                bot=bot_obj, creation_date=yesterday.date()).order_by('pk')

            message_history_objs = return_mis_objects_excluding_blocked_sessions(message_history_objs, UserSessionHealth)

            create_single_messgae_history_csv_file(
                last_one_day_file_path, message_history_objs.iterator(), bot_obj, yesterday)

        merge_list_of_files_in_a_given_file(
            [yest_file_path], last_one_day_file_path)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("merge_list_of_files_in_a_given_file %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_last_n_days_files(bot_obj, today, no_of_days, no_of_days_in_words):
    try:
        start_date = today - timedelta(no_of_days)
        end_date = today - timedelta(1)

        dir_path = settings.MEDIA_ROOT + \
            'message-history/bot-' + str(bot_obj.pk)

        last_n_day_file_path = dir_path + "/MessageHistoryLast" + no_of_days_in_words + "Days_from_" + \
            start_date.strftime("%d-%m-%Y") + "_to_" + \
            end_date.strftime("%d-%m-%Y") + ".csv"

        curr_date = start_date
        list_of_files_to_be_merged = []

        while curr_date.date() <= end_date.date():

            curr_day_file_path = get_single_day_file_path(bot_obj, curr_date)

            if os.path.exists(curr_day_file_path):
                list_of_files_to_be_merged.append(curr_day_file_path)

            curr_date = curr_date + timedelta(days=1)

        merge_list_of_files_in_a_given_file(
            list_of_files_to_be_merged, last_n_day_file_path)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("merge_list_of_files_in_a_given_file %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def cronjob():
    try:
        domain = settings.EASYCHAT_HOST_URL

        message_history_datadump_log = open(
            "log/message_history_dump.log", "a")

        today = datetime.now()

        try:
            if not os.path.exists(settings.MEDIA_ROOT + 'message-history'):
                os.makedirs(settings.MEDIA_ROOT + 'message-history')

            for bot_obj in Bot.objects.filter(is_deleted=False):
                # Check whether directory for given bot id exists or not: If not create
                if not os.path.exists(settings.MEDIA_ROOT + 'message-history/bot-' + str(bot_obj.pk)):
                    os.makedirs(settings.MEDIA_ROOT +
                                'message-history/bot-' + str(bot_obj.pk))
                import time
                st_time = time.time()
                maintain_last_30_days_message_history_csv_files(bot_obj)
                logger.info("total time taken for maintaing last 31 days files are  %s", str(time.time() - st_time), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                update_last_one_day_file(bot_obj, today)

                update_last_n_days_files(bot_obj, today, 7, "Seven")

                update_last_n_days_files(bot_obj, today, 30, "Thirty")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        for export_date_request in ExportMessageHistoryRequest.objects.filter(is_completed=False):
            if export_date_request.request_type == "message-history":
                try:
                    filter_param = json.loads(export_date_request.filter_param)
                    start_date = filter_param["startdate"]
                    end_date = filter_param["enddate"]
                    email_str = filter_param["email"]
                    custom_filter = filter_param["filter"]

                    date_format = "%Y-%m-%d"
                    email_list = [email.strip()
                                  for email in email_str.split(",") if email != ""]

                    start_date = datetime.strptime(
                        start_date, date_format).date()
                    end_date = datetime.strptime(end_date, date_format).date()

                    bot_obj = export_date_request.bot

                    message_history_objs = MISDashboard.objects.filter(bot=bot_obj,
                                                                       creation_date__gte=start_date, creation_date__lte=end_date)

                    message_history_objs = return_mis_objects_excluding_blocked_sessions(message_history_objs, UserSessionHealth)

                    if custom_filter == "1":
                        message_history_objs = message_history_objs.filter(
                            intent_name=None)
                    elif custom_filter == "2":
                        message_history_objs = message_history_objs.filter(
                            is_helpful_field="1")
                    elif custom_filter == "3":
                        message_history_objs = message_history_objs.filter(
                            is_helpful_field="-1")

                    message_history_objs = message_history_objs.iterator()

                    start_date = datetime.strftime(start_date, "%d-%m-%Y")
                    end_date = datetime.strftime(end_date, "%d-%m-%Y")

                    date_string = start_date + "_to_" + end_date

                    export_file_path = ("message-history/bot-" +
                                        str(bot_obj.pk) + "/MessageHistoryCustom-" +
                                        str(export_date_request.pk) + "custom_filter_" +
                                        str(custom_filter) + "_from_" + date_string + ".csv")

                    temp_export_file_path = settings.MEDIA_ROOT + export_file_path

                    create_single_messgae_history_csv_file(
                        temp_export_file_path, message_history_objs, bot_obj, date_string)

                    username = export_date_request.user.username

                    send_custom_export_email(
                        username, email_list, bot_obj, start_date, end_date, domain, export_file_path)

                    export_date_request.is_completed = True
                    export_date_request.save()

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Message History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                    message_history_datadump_log.write(
                        str(today) + ": failed: " + e)

                    export_date_request.is_completed = False
                    export_date_request.save()

        message_history_datadump_log.close()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_custom_export_email(username, email_list, bot_obj, start_date, end_date, domain, export_file_path):

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
                We have received a request to provide you with the Message History for <b>{}</b> Bot from {} to {}. Please click on the link below to download the file.
            </p>
            <a href="{}/{}">click here</a>
            <p>&nbsp;</p>"""

    config = get_developer_console_settings()

    body += config.custom_report_template_signature

    body += """</div></body>"""

    for email_id in email_list:
        body = body.format(username, bot_obj.name, str(start_date), str(
            end_date), domain, 'files/' + export_file_path)
        send_email_to_customer_via_awsses(
            email_id, "Message History for " + str(bot_obj.name) + " Bot", body)
