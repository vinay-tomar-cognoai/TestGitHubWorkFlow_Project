import os
import sys
import json
import pytz
from xlsxwriter import Workbook
from LiveChatApp.models import *
from LiveChatApp.utils import logger, get_agents_under_this_user
from zipfile import ZipFile
from datetime import datetime, timedelta
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

from os import path
from os.path import basename


def cronjob():
    try:
        domain = settings.EASYCHAT_HOST_URL
        vc_history_datadump_log = open(
            "log/vc_history_dump.log", "a")

        today = datetime.now()

        try:
            total_x_days = 31

            if not os.path.exists(settings.MEDIA_ROOT + 'livechat-vc-history'):
                os.makedirs(settings.MEDIA_ROOT + 'livechat-vc-history')

            for user in LiveChatUser.objects.filter(is_deleted=False, status__in=["1", "2"]):

                # Check whether directory for given bot id exists or not: If not create
                # one
                agent_list = get_agents_under_this_user(user)
                if not os.path.exists(settings.MEDIA_ROOT + 'livechat-vc-history/' + str(user.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + 'livechat-vc-history/' +
                                str(user.user.username))

                for last_x_day in range(1, total_x_days + 2):

                    if last_x_day == total_x_days + 1:
                        day_x = today - timedelta(last_x_day)
                        if os.path.exists(settings.MEDIA_ROOT + 'livechat-vc-history/' + str(user.user.username) + '/vc_history_' + str(day_x.date()) + '.xls'):
                            cmd = 'rm ' + settings.MEDIA_ROOT + 'livechat-vc-history/' + \
                                str(user.user.username) + '/vc_history_' + \
                                str(day_x.date()) + '.xls'
                            os.system(cmd)
                        break

                    last_date = today - timedelta(last_x_day)

                    file_already_exists = False
                    if path.exists(settings.MEDIA_ROOT + "livechat-vc-history/" + str(user.user.username) + "/vc_history_" + str(last_date.date()) + ".xls"):
                        file_already_exists = True

                    if not file_already_exists:

                        tz = pytz.timezone(settings.TIME_ZONE)

                        vc_history_objs = LiveChatVoIPData.objects.filter(request_datetime__date=last_date.date(), call_type='video_call', agent__in=agent_list, is_completed=True, is_interrupted=False).order_by("-request_datetime")
                        
                        test_wb = Workbook()
                        
                        sheet1 = test_wb.add_sheet("Sheet1")

                        sheet1.write(0, 0, "Customer Name")
                        sheet1.write(0, 1, "Agent Username")
                        sheet1.write(0, 2, "Start Date-Time")
                        sheet1.write(0, 3, "End Date-Time")
                        sheet1.write(0, 4, "Total Duration")
                        sheet1.write(0, 5, "Meeting Status")

                        row = 1
                        for vc_data in vc_history_objs:

                            sheet1.write(row, 0, vc_data.customer.get_username())
                            sheet1.write(row, 1, vc_data.agent.user.username)

                            sheet1.write(row, 2, vc_data.start_datetime.astimezone(tz).strftime('%d-%b-%Y, %I:%M %p'))
                            sheet1.write(row, 3, vc_data.end_datetime.astimezone(tz).strftime('%d-%b-%Y, %I:%M %p'))

                            sheet1.write(row, 4, vc_data.get_call_duration())
                            sheet1.write(row, 5, "Completed")

                            row += 1

                        filename = 'livechat-vc-history/' + \
                            str(user.user.username) + '/vc_history_' + \
                            str(last_date.date()) + '.xls'
                        test_wb.save(settings.MEDIA_ROOT + filename)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("vc History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'LiveChat'})
            vc_history_datadump_log.write(
                str(today) + ": failed: " + str(e))

        for export_date_request in LiveChatDataExportRequest.objects.filter(is_completed=False, report_type="11"):
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]
                user = export_date_request.user
                agent_list = get_agents_under_this_user(user)

                date_format = "%Y-%m-%d"
                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                temp_date = start_date

                while temp_date <= end_date:

                    file_path = settings.MEDIA_ROOT + "livechat-vc-history/" + \
                        str(user.user.username) + "/vc_history_" + \
                        str(temp_date) + ".xls"

                    if path.exists(file_path):
                        temp_date = temp_date + timedelta(1)
                        continue

                    tz = pytz.timezone(settings.TIME_ZONE)

                    vc_history_objs = LiveChatVoIPData.objects.filter(request_datetime__date=temp_date, call_type='video_call', agent__in=agent_list, is_completed=True, is_interrupted=False).order_by("-request_datetime")
                    
                    test_wb = Workbook()
                    
                    sheet1 = test_wb.add_sheet("Sheet1")

                    sheet1.write(0, 0, "Customer Name")
                    sheet1.write(0, 1, "Agent Username")
                    sheet1.write(0, 2, "Start Date-Time")
                    sheet1.write(0, 3, "End Date-Time")
                    sheet1.write(0, 4, "Total Duration")
                    sheet1.write(0, 5, "Meeting Status")

                    row = 1
                    for vc_data in vc_history_objs:

                        sheet1.write(row, 0, vc_data.customer.get_username())
                        sheet1.write(row, 1, vc_data.agent.user.username)

                        sheet1.write(row, 2, vc_data.start_datetime.astimezone(tz).strftime('%d-%b-%Y, %I:%M %p'))
                        sheet1.write(row, 3, vc_data.end_datetime.astimezone(tz).strftime('%d-%b-%Y, %I:%M %p'))

                        sheet1.write(row, 4, vc_data.get_call_duration())
                        sheet1.write(row, 5, "Completed")

                        row += 1

                    file_path = "livechat-vc-history/" + \
                        str(user.user.username) + "/vc_history_" + \
                        str(temp_date) + ".xls"
                    test_wb.save(settings.MEDIA_ROOT + file_path)

                    temp_date = temp_date + timedelta(1)

                export_zip_file_path = "livechat-vc-history/" + \
                    str(user.user.username) + "/ChatHistoryCustom-" + \
                    str(export_date_request.pk) + ".zip"

                zip_obj = ZipFile(settings.MEDIA_ROOT + export_zip_file_path, 'w')

                temp_date = start_date

                while temp_date <= end_date:
                    try:
                        file_path = "livechat-vc-history/" + \
                            str(user.user.username) + "/vc_history_" + \
                            str(temp_date) + '.xls'
                        zip_obj.write(settings.MEDIA_ROOT +
                                      file_path, basename(file_path))
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("vc History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
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
                            We have received a request to provide you with the LiveChat VC History from {} to {}. Please click on the link below to download the file.
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
                    email_subject = "LiveChat VC History For " + \
                        str(username)
                    send_email_to_customer_via_awsses(email_id, email_subject, body)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("vc History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'LiveChat'})
                vc_history_datadump_log.write(
                    str(today) + ": failed: " + str(e))
                export_date_request.is_completed = False
                export_date_request.save()

        vc_history_datadump_log.close()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
