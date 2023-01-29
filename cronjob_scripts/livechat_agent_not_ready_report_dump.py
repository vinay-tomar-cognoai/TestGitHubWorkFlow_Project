import os
import sys
import json

from xlwt import Workbook
from LiveChatApp.models import *
from LiveChatApp.utils import logger
from zipfile import ZipFile
from datetime import datetime, timedelta
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

from os import path
from os.path import basename


def get_agents_under_this_user(user_obj):
    agent_obj_list = []
    if user_obj.status == "3" or user_obj.status == "1":
        agent_obj_list.append(user_obj)
    try:
        for user in user_obj.agents.all():
            if user.status == "2":
                for user1 in user.agents.all():
                    agent_obj_list.append(user1)
            elif user.status == "3":
                agent_obj_list.append(user)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_agents_under_this_user: %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return list(set(agent_obj_list))


def cronjob():
    try:
        domain = settings.EASYCHAT_HOST_URL

        message_history_datadump_log = open(
            "log/livechat_agent_not_ready_report_dump.log", "a")

        today = datetime.now()

        try:
            total_x_days = 31

            if not os.path.exists(settings.MEDIA_ROOT + 'livechat-agent-not-ready-report'):
                os.makedirs(settings.MEDIA_ROOT +
                            'livechat-agent-not-ready-report')

            for user in LiveChatUser.objects.filter(is_deleted=False, status__in=["1", "2"]):

                # Check whether directory for given bot id exists or not: If not create
                # one
                agent_list = get_agents_under_this_user(user)
                if not os.path.exists(settings.MEDIA_ROOT + 'livechat-agent-not-ready-report/' + str(user.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + 'livechat-agent-not-ready-report/' +
                                str(user.user.username))

                for last_x_day in range(1, total_x_days + 2):

                    if last_x_day == total_x_days + 1:
                        day_x = today - timedelta(last_x_day)
                        if os.path.exists(settings.MEDIA_ROOT + 'livechat-agent-not-ready-report/' + str(user.user.username) + "/agent_not_ready_report_" + str(day_x.date()) + ".xls"):
                            cmd = "rm " + settings.MEDIA_ROOT + "livechat-agent-not-ready-report/" + \
                                str(user.user.username) + \
                                "/agent_not_ready_report_" + \
                                str(day_x.date()) + ".xls"
                            os.system(cmd)
                        break

                    last_date = today - timedelta(last_x_day)

                    file_already_exists = False
                    if path.exists(settings.MEDIA_ROOT + "livechat-agent-not-ready-report/" + str(user.user.username) + "/agent_not_ready_report_" + str(last_date.date()) + ".xls"):
                        file_already_exists = True

                    # logger.info(file_already_exists, extra={"AppName": "LiveChat"})
                    if not file_already_exists:

                        message_history_yesterday = LiveChatAgentNotReady.objects.filter(
                            not_ready_starts_at__date=last_date.date(), user__in=agent_list)

                        test_wb = Workbook()

                        sheet1 = test_wb.add_sheet("Sheet1")

                        sheet1.write(0, 0, "Date")
                        sheet1.write(0, 1, "Agent Name")
                        sheet1.write(0, 2, "Agent Username")
                        sheet1.write(0, 3, "Reason")
                        sheet1.write(0, 4, "Stop Interaction Duration")
                        sheet1.write(0, 5, "Start Time")
                        sheet1.write(0, 6, "End Time")
                        sheet1.write(0, 7, "Offline Time")
                        row = 1
                        for message in message_history_yesterday:
                            message.not_ready_starts_at = message.not_ready_starts_at + \
                                timedelta(hours=5, minutes=30)
                            message.not_ready_ends_at = message.not_ready_ends_at + \
                                timedelta(hours=5, minutes=30)
                            sheet1.write(row, 0, str(
                                message.not_ready_starts_at.date().strftime("%d-%m-%Y")))
                            sheet1.write(row, 1, str(
                                message.user.user.first_name) + " " + str(message.user.user.last_name))
                            sheet1.write(row, 2, message.user.user.username)
                            sheet1.write(
                                row, 3, message.get_reason_for_offline())
                            sheet1.write(row, 4, message.get_stop_interaction_duration())
                            sheet1.write(
                                row, 5, str(message.not_ready_starts_at.time().strftime("%H:%M:%S")))
                            sheet1.write(
                                row, 6, str(message.not_ready_ends_at.time().strftime("%H:%M:%S")))
                            sheet1.write(row, 7, message.get_offline_duration())
                            row += 1

                        filename = 'livechat-agent-not-ready-report/' + \
                            str(user.user.username) + '/agent_not_ready_report_' + \
                            str(last_date.date()) + '.xls'

                        test_wb.save(settings.MEDIA_ROOT + filename)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Agent Not Ready Report Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'LiveChat'})
            message_history_datadump_log.write(
                str(today) + ": failed: " + str(e))

        for export_date_request in LiveChatDataExportRequest.objects.filter(is_completed=False, report_type="0"):
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]
                agent_list = get_agents_under_this_user(
                    export_date_request.user)

                date_format = "%Y-%m-%d"
                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                temp_date = start_date

                while temp_date <= end_date:

                    file_path = settings.MEDIA_ROOT + "livechat-agent-not-ready-report/" + \
                        str(export_date_request.user.user.username) + "/agent_not_ready_report_" + \
                        str(temp_date) + ".xls"

                    if path.exists(file_path):
                        temp_date = temp_date + timedelta(1)
                        continue

                    message_history_objs = LiveChatAgentNotReady.objects.filter(
                        not_ready_starts_at__date=temp_date, user__in=agent_list)

                    test_wb = Workbook()

                    sheet1 = test_wb.add_sheet("Sheet1")

                    sheet1.write(0, 0, "Date")
                    sheet1.write(0, 1, "Agent Name")
                    sheet1.write(0, 2, "Agent Username")
                    sheet1.write(0, 3, "Reason")
                    sheet1.write(0, 4, "Stop Interaction Duration")
                    sheet1.write(0, 5, "Start Time")
                    sheet1.write(0, 6, "End Time")
                    sheet1.write(0, 7, "Offline Time")
                    row = 1
                    for message in message_history_objs:
                        message.not_ready_starts_at = message.not_ready_starts_at + \
                            timedelta(hours=5, minutes=30)
                        message.not_ready_ends_at = message.not_ready_ends_at + \
                            timedelta(hours=5, minutes=30)
                        sheet1.write(row, 0, str(
                            message.not_ready_starts_at.date().strftime("%d-%m-%Y")))
                        sheet1.write(row, 1, str(
                            message.user.user.first_name) + " " + str(message.user.user.last_name))
                        sheet1.write(row, 2, message.user.user.username)
                        sheet1.write(row, 3, message.get_reason_for_offline())
                        sheet1.write(row, 4, message.get_stop_interaction_duration())
                        sheet1.write(
                            row, 5, str(message.not_ready_starts_at.time().strftime("%H:%M:%S")))
                        sheet1.write(row, 6, str(
                            message.not_ready_ends_at.time().strftime("%H:%M:%S")))
                        sheet1.write(row, 7, message.get_offline_duration())
                        row += 1

                    file_path = "livechat-agent-not-ready-report/" + \
                        str(export_date_request.user.user.username) + \
                        "/agent_not_ready_report_" + str(temp_date) + ".xls"
                    test_wb.save(settings.MEDIA_ROOT + file_path)
                    temp_date = temp_date + timedelta(1)

                export_zip_file_path = "livechat-agent-not-ready-report/" + \
                    str(export_date_request.user.user.username) + "/AgentNotReadyReportCustom-" + \
                    str(export_date_request.pk) + ".zip"

                zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')

                temp_date = start_date

                while temp_date <= end_date:
                    try:
                        file_path = "livechat-agent-not-ready-report/" + \
                            str(export_date_request.user.user.username) + "/agent_not_ready_report_" + \
                            str(temp_date) + '.xls'
                        zip_obj.write(settings.MEDIA_ROOT +
                                      file_path, basename(file_path))
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Agent Not Ready Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
                        pass
                    temp_date = temp_date + timedelta(1)

                zip_obj.close()

                username = export_date_request.user.user.username

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
                            We have received a request to provide you with the LiveChat Agent Not Ready report from {} to {}. Please click on the link below to download the file.
                        </p>
                        <a href="{}/{}">click here</a>
                        <p>&nbsp;</p>
                        """
                developer_console_config = get_developer_console_settings()

                body += developer_console_config.custom_report_template_signature 

                body += """</div></body>"""

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                for email_id in email_list:
                    body = body.format(username, str(start_date), str(
                        end_date), domain, FILES_PATH + export_zip_file_path)
                    email_subject = "LiveChat Agent Not Ready Report For " + \
                        str(username)
                    send_email_to_customer_via_awsses(email_id, email_subject, body)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Agent Not Ready Report Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'LiveChat'})
                message_history_datadump_log.write(
                    str(today) + ": failed: " + e)
                export_date_request.is_completed = False
                export_date_request.save()

        message_history_datadump_log.close()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
