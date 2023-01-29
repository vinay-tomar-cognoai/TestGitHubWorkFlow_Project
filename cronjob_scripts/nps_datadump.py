import os
import sys
import json
from django.conf import settings
from EasyChatApp.utils import logger
from datetime import datetime, timedelta
import csv
import time
from EasyChatApp.models import Bot, ExportMessageHistoryRequest, Feedback
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


def add_default_values(writer):
    try:
        headings = ["TimeStamp",
                    "User ID",
                    "Channel",
                    "Rating",
                    "Comments",
                    "Feedback 1",
                    "Feedback 2",
                    "Feedback 3",
                    "Feedback 4",
                    "Feedback 5",
                    "Feedback 6",
                    "Phone Number",
                    "Email ID",
                    "Link to Chat History"]
        writer.writerow(headings)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CSAT data dump add_default_values! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_feedback_into_CSV(writer, feedback, feedback_date, bot_obj):
    try:
        row_data = [str(feedback_date), feedback.user_id, feedback.channel.name, str(feedback.rating)]

        if feedback.comments and feedback.comments != "":
            row_data.append(feedback.comments)
        else:
            row_data.append('-')

        all_feedbacks = feedback.all_feedbacks
        column = 6
        if all_feedbacks:
            all_feedbacks = all_feedbacks.split(',')
            for feedback_str in all_feedbacks:
                row_data.append(str(feedback_str))
                column += 1

        for col in range(column, 12):
            row_data.append('-')

        if feedback.phone_number and feedback.phone_number != "":
            row_data.append(feedback.phone_number)
        else:
            row_data.append('-')

        if feedback.email_id and feedback.email_id != "":
            row_data.append(feedback.email_id)
        else:
            row_data.append('-')

        link = (settings.EASYCHAT_HOST_URL + '/chat/user-filtered/?bot_id=' +
                str(bot_obj.pk) + '&user_id=' + feedback.user_id)
        
        row_data.append('=HYPERLINK(\"' + link + '\";"Click here")')

        writer.writerow(row_data)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_feedback_into_CSV %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_data(writer, bot_obj, feedback_objs):
    try:
        for feedback in feedback_objs.iterator():
            add_feedback_into_CSV(
                writer, feedback, feedback.date.date(), bot_obj)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_data %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_single_day_file_path(bot_obj, day):

    file_path = settings.MEDIA_ROOT + 'csat-data/bot-' + \
        str(bot_obj.pk) + "/CSATData_of_date_" + str(day.date()) + ".csv"

    return file_path


def create_single_CSAT_data_csv_file(file_path, feedback_objs, bot_obj, date_of_file):
    try:
        last_day_file = open(file_path, 'w')

        writer = csv.writer(last_day_file)

        add_default_values(writer)

        add_data(writer, bot_obj, feedback_objs)

        last_day_file.close()

        logger.info("CSAT Data dump file created for bot and date" + str(bot_obj.name) + str(date_of_file), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_single_CSAT_data_csv_file %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def maintain_last_90_days_CSAT_data_csv_files(bot_obj):
    try:
        if not os.path.exists(settings.MEDIA_ROOT + 'csat-data/bot-' + str(bot_obj.pk)):
            os.makedirs(settings.MEDIA_ROOT +
                        'csat-data/bot-' + str(bot_obj.pk))

        total_x_days = 91
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

            feedback_yesterday = Feedback.objects.filter(
                date__date=last_date.date(), bot=bot_obj).order_by('pk')
            
            create_single_CSAT_data_csv_file(
                last_date_file_path, feedback_yesterday, bot_obj, last_date.date())

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("maintain_last_90_days_CSAT_data_csv_files %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def merge_list_of_files_in_a_given_file(existing_file_list, merged_file_path):
    try:
        with open(merged_file_path, "wb") as fout:
            # first file:
            with open(existing_file_list[0], "rb") as f:
                fout.write(f.read())
            # now the rest:
            for file_no in range(1, len(existing_file_list)):
                with open(existing_file_list[file_no], "rb") as f:
                    next(f)
                    fout.write(f.read())

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("merge_list_of_files_in_a_given_file %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_last_one_day_file(bot_obj, today):
    try:

        yesterday = today - timedelta(1)

        yest_file_path = get_single_day_file_path(bot_obj, yesterday)

        dir_path = settings.MEDIA_ROOT + \
            'csat-data/bot-' + str(bot_obj.pk)

        last_one_day_file_path = dir_path + "/CSATDataLastOneDay_" + \
            yesterday.strftime("%d-%m-%Y") + ".csv"

        if not os.path.exists(yest_file_path):

            feedback_yesterday = Feedback.objects.filter(
                date__date=yesterday.date(), bot=bot_obj).order_by('pk')
            
            create_single_CSAT_data_csv_file(
                yest_file_path, feedback_yesterday, bot_obj, yesterday.date())

        merge_list_of_files_in_a_given_file(
            [yest_file_path], last_one_day_file_path)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_last_one_day_file %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_last_n_days_files(bot_obj, today, no_of_days, no_of_days_in_words):
    try:
        start_date = today - timedelta(no_of_days)
        end_date = today - timedelta(1)

        dir_path = settings.MEDIA_ROOT + \
            'csat-data/bot-' + str(bot_obj.pk)

        last_n_day_file_path = dir_path + "/CSATDataLast" + no_of_days_in_words + "Days_from_" + \
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
        logger.error("update_last_n_days_files %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def cronjob():
    try:
        domain = settings.EASYCHAT_HOST_URL

        nps_datadump_log = open(
            "log/nps_data_dump.log", "a")

        today = datetime.now()

        try:
            if not os.path.exists(settings.MEDIA_ROOT + 'csat-data'):
                os.makedirs(settings.MEDIA_ROOT + 'csat-data')

            for bot_obj in Bot.objects.filter(is_deleted=False):

                # Check whether directory for given bot id exists or not: If not create
                # one
                if not os.path.exists(settings.MEDIA_ROOT + 'csat-data/bot-' + str(bot_obj.pk)):
                    os.makedirs(settings.MEDIA_ROOT +
                                'csat-data/bot-' + str(bot_obj.pk))
                
                st_time = time.time()
                maintain_last_90_days_CSAT_data_csv_files(bot_obj)
                logger.info("total time taken for maintaing last 90 days files are  %s", str(time.time() - st_time), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                # for last day
                update_last_one_day_file(bot_obj, today)

                # last 7 days
                update_last_n_days_files(bot_obj, today, 7, "Seven")

                # last 15 days
                update_last_n_days_files(bot_obj, today, 15, "Fifteen")

                # last 30 days
                update_last_n_days_files(bot_obj, today, 30, "Thirty")
                
                # last 60 days
                update_last_n_days_files(bot_obj, today, 60, "Sixty")

                # last 90 days
                update_last_n_days_files(bot_obj, today, 90, "Ninty")
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        for export_date_request in ExportMessageHistoryRequest.objects.filter(is_completed=False):
            if export_date_request.request_type == "NPS":
                try:
                    filter_param = json.loads(export_date_request.filter_param)
                    start_date = filter_param["startdate"]
                    end_date = filter_param["enddate"]
                    email_str = filter_param["email"]

                    date_format = "%Y-%m-%d"
                    email_list = [email.strip()
                                  for email in email_str.split(",") if email != ""]

                    start_date = datetime.strptime(
                        start_date, date_format).date()
                    end_date = datetime.strptime(end_date, date_format).date()

                    bot_obj = export_date_request.bot

                    date_str = str(start_date) + "_to_" + str(end_date)

                    feedback_objs = Feedback.objects.filter(bot=bot_obj,
                                                            date__date__gte=start_date, date__date__lte=end_date)

                    export_file_path = "csat-data/bot-" + \
                        str(bot_obj.pk) + "/CSATDataCustom-" + \
                        str(export_date_request.pk) + ".csv"

                    temp_export_file_path = settings.MEDIA_ROOT + export_file_path

                    create_single_CSAT_data_csv_file(temp_export_file_path, feedback_objs, bot_obj, date_str)

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
                                We have received a request to provide you with the CSAT Data for <b>{}</b> Bot from {} to {}. Please click on the link below to download the file.
                            </p>
                            <a href="{}/{}">click here</a>
                            <p>&nbsp;</p>"""

                    config = get_developer_console_settings()

                    body += config.custom_report_template_signature

                    body += """</div></body>"""

                    start_date = datetime.strftime(start_date, "%d-%m-%Y")
                    end_date = datetime.strftime(end_date, "%d-%m-%Y")

                    for email_id in email_list:
                        body = body.format(username, bot_obj.name, str(start_date), str(
                            end_date), domain, 'files/' + export_file_path)
                        send_email_to_customer_via_awsses(email_id, "CSAT Data for " + str(bot_obj.name) + " Bot", body)

                    export_date_request.is_completed = True
                    export_date_request.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("CSAT Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    nps_datadump_log.write(str(today) + ": failed: " + e)
                    export_date_request.is_completed = False
                    export_date_request.save()

        nps_datadump_log.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
