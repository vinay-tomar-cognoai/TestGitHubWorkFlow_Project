import os
import sys
import json

from xlsxwriter import Workbook
from LiveChatApp.models import *
from EasyChatApp.models import Channel
from LiveChatApp.utils import logger, get_agents_under_this_user
from LiveChatApp.utils_analytics import *
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
        from pytz import timezone
        ist = timezone('Asia/Kolkata')
        domain = settings.EASYCHAT_HOST_URL

        analytics_datadump_log = open(
            "log/analytics_data_dump.log", "a")

        today = datetime.now()
        channel_objs = Channel.objects.all()

        try:
            total_x_days = 31

            if not os.path.exists(settings.MEDIA_ROOT + 'livechat-analytics-data'):
                os.makedirs(settings.MEDIA_ROOT + 'livechat-analytics-data')

            for user in LiveChatUser.objects.filter(is_deleted=False, status__in=["1", "2"]):

                bot_objs = user.bots.all().filter(is_deleted=False)
                category_objs = user.category.all().filter(
                    bot__in=bot_objs, is_deleted=False)

                user_obj_list = get_agents_under_this_user(user)
                if not os.path.exists(settings.MEDIA_ROOT + 'livechat-analytics-data/' + str(user.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + 'livechat-analytics-data/' +
                                str(user.user.username))

                for last_x_day in range(1, total_x_days + 2):

                    if last_x_day == total_x_days + 1:
                        day_x = today - timedelta(last_x_day)
                        if os.path.exists(settings.MEDIA_ROOT + 'livechat-analytics-data/' + str(user.user.username) + '/analytics_' + str(day_x.date()) + '.xls'):
                            cmd = 'rm ' + settings.MEDIA_ROOT + 'livechat-analytics-data/' + \
                                str(user.user.username) + '/analytics_' + \
                                str(day_x.date()) + '.xls'
                            os.system(cmd)
                        break

                    last_date = today - timedelta(last_x_day)

                    file_already_exists = False
                    if path.exists(settings.MEDIA_ROOT + "livechat-analytics-data/" + str(user.user.username) + "/analytics_" + str(last_date.date()) + ".xls"):
                        file_already_exists = True

                    if not file_already_exists:

                        test_wb = Workbook()

                        sheet1 = test_wb.add_sheet("Sheet1")

                        sheet1.write(0, 0, "Total Chats Raised")
                        sheet1.write(0, 1, "Total Resolved Chats")
                        sheet1.write(0, 2, "Offline Chats")
                        sheet1.write(0, 3, "Abandoned Chats")
                        sheet1.write(0, 4, "Customer Declined Chats")
                        sheet1.write(0, 5, "Customer Waiting Time")
                        sheet1.write(0, 6, "Average NPS")
                        sheet1.write(0, 7, "Interactions Per Chat")
                        sheet1.write(0, 8, "Average Handle Time")
                        sheet1.write(0, 9, "Voice Calls Initiated")
                        sheet1.write(0, 10, "Average Call Duration")
                        sheet1.write(0, 11, "Total Tickets Raised")
                        sheet1.write(0, 12, "Average Cobrowsing Sessions Duration")
                        sheet1.write(0, 13, "Total Customers Reported")
                        sheet1.write(0, 14, "Leads followed up on email")

                        datetime_start = last_date
                        datetime_end = last_date
                        total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats = get_chat_analytics_filter(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, Bot, LiveChatCustomer, LiveChatConfig)
                        average_handle_time = get_livechat_avh_filter(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, LiveChatCustomer)
                        average_queue_time = get_livechat_avg_queue_time_filter(
                            user_obj_list, datetime_start.date(), datetime_end.date(), category_objs, LiveChatCustomer)
                        average_interactions = get_livechat_avg_interaction_per_chat_filter(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, LiveChatCustomer, LiveChatMISDashboard)
                        nps_avg = get_nps_avg_filter(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, LiveChatCustomer)

                        voice_calls_initiated = get_voice_calls_initiated_filtered(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, LiveChatVoIPData)
                        avg_call_duration = get_average_call_duration_filtered(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, LiveChatVoIPData)
                        total_tickets_raised = get_total_tickets_raised_filtered(user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, LiveChatTicketAudit)
                        avg_cobrowsing_duration = get_average_cobrowsing_duration_filtered(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, LiveChatCobrowsingData)
                        total_customers_reported = get_total_customers_reported_filtered(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, LiveChatReportedCustomer)
                        followup_leads_via_email = get_followup_leads_via_email_filtered(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, Channel, LiveChatFollowupCustomer)
                        row = 1

                        sheet1.write(row, 0, total_entered_chat)
                        sheet1.write(row, 1, total_closed_chat)
                        sheet1.write(row, 2, denied_chats)
                        sheet1.write(row, 3, abandon_chats)
                        sheet1.write(row, 4, customer_declined_chats)
                        sheet1.write(row, 5, average_queue_time)
                        sheet1.write(row, 6, nps_avg)
                        sheet1.write(row, 7, average_interactions)
                        sheet1.write(row, 8, average_handle_time)
                        sheet1.write(row, 9, voice_calls_initiated)
                        sheet1.write(row, 10, avg_call_duration)
                        sheet1.write(row, 11, total_tickets_raised)
                        sheet1.write(row, 12, avg_cobrowsing_duration)
                        sheet1.write(row, 13, total_customers_reported)
                        sheet1.write(row, 14, followup_leads_via_email)

                        filename = 'livechat-analytics-data/' + \
                            str(user.user.username) + '/analytics_' + \
                            str(last_date.date()) + '.xls'
                        test_wb.save(settings.MEDIA_ROOT + filename)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Chat History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'LiveChat'})

        for export_date_request in LiveChatDataExportRequest.objects.filter(is_completed=False, report_type="7"):
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]
                category_ids = filter_param["category_pk_list"]
                user = export_date_request.user
                user_obj_list = get_agents_under_this_user(user)

                date_format = "%Y-%m-%d"
                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format)
                end_date = datetime.strptime(end_date, date_format)
                request_time = export_date_request.request_datetime.astimezone(ist).time()

                if len(category_ids) > 1:
                    category_ids.insert(0, "All")

                temp_date = start_date

                while temp_date <= end_date:

                    file_path = settings.MEDIA_ROOT + "livechat-analytics-data/" + \
                        str(user.user.username) + "/analytics_" + \
                        str(temp_date.date()) + "_" + str(request_time) + ".xls"

                    if path.exists(file_path):
                        temp_date = temp_date + timedelta(1)
                        continue

                    test_wb = Workbook()

                    for category_indx in range(len(category_ids)):

                        if len(category_ids) == 1:
                            category_obj = LiveChatCategory.objects.filter(pk=int(category_ids[category_indx]))
                            sheet1 = test_wb.add_sheet(category_obj.first().title)
                        elif category_ids[category_indx] == "All":
                            sheet1 = test_wb.add_sheet("Overall")
                            bot_objs = user.bots.all().filter(is_deleted=False)
                            category_obj = user.category.all().filter(
                                bot__in=bot_objs, is_deleted=False)
                        else:
                            category_obj = LiveChatCategory.objects.filter(pk=int(category_ids[category_indx]))
                            sheet1 = test_wb.add_sheet(category_obj.first().title)

                        sheet1.write(0, 0, "Total Chats Raised")
                        sheet1.write(0, 1, "Total Resolved Chats")
                        sheet1.write(0, 2, "Offline Chats")
                        sheet1.write(0, 3, "Abandoned Chats")
                        sheet1.write(0, 4, "Customer Declined Chats")
                        sheet1.write(0, 5, "Customer Waiting Time")
                        sheet1.write(0, 6, "Average NPS")
                        sheet1.write(0, 7, "Interactions Per Chat")
                        sheet1.write(0, 8, "Average Handle Time")
                        sheet1.write(0, 9, "Voice Calls Initiated")
                        sheet1.write(0, 10, "Average Call Duration")
                        sheet1.write(0, 11, "Total Tickets Raised")
                        sheet1.write(0, 12, "Average Cobrowsing Sessions Duration")
                        sheet1.write(0, 13, "Total Customers Reported")
                        sheet1.write(0, 14, "Leads followed up on email")

                        datetime_start = temp_date
                        datetime_end = temp_date

                        total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats = get_chat_analytics_filter(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_obj, Bot, LiveChatCustomer, LiveChatConfig)
                        average_handle_time = get_livechat_avh_filter(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_obj, LiveChatCustomer)
                        average_queue_time = get_livechat_avg_queue_time_filter(
                            user_obj_list, datetime_start.date(), datetime_end.date(), category_obj, LiveChatCustomer)
                        average_interactions = get_livechat_avg_interaction_per_chat_filter(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_obj, LiveChatCustomer, LiveChatMISDashboard)
                        nps_avg = get_nps_avg_filter(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_obj, LiveChatCustomer)

                        voice_calls_initiated = get_voice_calls_initiated_filtered(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_obj, LiveChatVoIPData)
                        avg_call_duration = get_average_call_duration_filtered(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_obj, LiveChatVoIPData)
                        total_tickets_raised = get_total_tickets_raised_filtered(user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_obj, LiveChatTicketAudit)
                        avg_cobrowsing_duration = get_average_cobrowsing_duration_filtered(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_obj, LiveChatCobrowsingData)
                        total_customers_reported = get_total_customers_reported_filtered(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, LiveChatReportedCustomer)
                        followup_leads_via_email = get_followup_leads_via_email_filtered(
                            user_obj_list, datetime_start.date(), datetime_end.date(), channel_objs, category_objs, Channel, LiveChatFollowupCustomer)

                        row = 1

                        sheet1.write(row, 0, total_entered_chat)
                        sheet1.write(row, 1, total_closed_chat)
                        sheet1.write(row, 2, denied_chats)
                        sheet1.write(row, 3, abandon_chats)
                        sheet1.write(row, 4, customer_declined_chats)
                        sheet1.write(row, 5, average_queue_time)
                        sheet1.write(row, 6, nps_avg)
                        sheet1.write(row, 7, average_interactions)
                        sheet1.write(row, 8, average_handle_time)
                        sheet1.write(row, 9, voice_calls_initiated)
                        sheet1.write(row, 10, avg_call_duration)
                        sheet1.write(row, 11, total_tickets_raised)
                        sheet1.write(row, 12, avg_cobrowsing_duration)
                        sheet1.write(row, 13, total_customers_reported)
                        sheet1.write(row, 14, followup_leads_via_email)

                    file_path = "livechat-analytics-data/" + \
                        str(user.user.username) + "/analytics_" + \
                        str(temp_date.date()) + "_" + str(request_time) + ".xls"
                    test_wb.save(settings.MEDIA_ROOT + file_path)

                    temp_date = temp_date + timedelta(1)

                if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/livechat-analytics-data/' + str(user.user.username)):
                    os.makedirs(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/livechat-analytics-data/' + str(user.user.username))

                export_zip_file_path = "LiveChatApp/livechat-analytics-data/" + \
                    str(user.user.username) + "/AnalyticsCustom-" + \
                    str(export_date_request.pk) + ".zip"

                zip_obj = ZipFile(settings.SECURE_MEDIA_ROOT + export_zip_file_path, 'w')

                temp_date = start_date

                while temp_date <= end_date:
                    try:
                        file_path = "livechat-analytics-data/" + \
                            str(user.user.username) + "/analytics_" + \
                            str(temp_date.date()) + "_" + str(request_time) + ".xls"
                        zip_obj.write(settings.MEDIA_ROOT +
                                      file_path, basename(file_path))
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Agent Analytics Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})
                        pass
                    temp_date = temp_date + timedelta(1)

                zip_obj.close()

                export_zip_file_path = SECURED_FILES_PATH + export_zip_file_path
                file_access_management_obj = LiveChatFileAccessManagement.objects.create(
                    file_path=export_zip_file_path, is_public=False)
                file_access_management_obj.file_access_type = "personal_access"
                file_access_management_obj.users.add(user)
                file_access_management_obj.save()

                export_zip_file_path = 'livechat/download-file/' + \
                    str(file_access_management_obj.key) + '/LiveChatAnalytics.zip'

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
                            We have received a request to provide you with the LiveChat Analytics Data from {} to {}. Please click on the link below to download the file.
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
                        end_date), domain, export_zip_file_path)
                    email_subject = "LiveChat Analytics For " + \
                        str(username)
                    send_email_to_customer_via_awsses(email_id, email_subject, body)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Analytics Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'LiveChat'})
                analytics_datadump_log.write(
                    str(today) + ": failed: " + str(e))
                export_date_request.is_completed = False
                export_date_request.save()

        analytics_datadump_log.close()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
