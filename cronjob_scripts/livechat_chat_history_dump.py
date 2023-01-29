import os
import sys
import json

from xlsxwriter import Workbook
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
            "log/message_history_dump.log", "a")

        today = datetime.now()

        try:
            total_x_days = 31

            if not os.path.exists(settings.MEDIA_ROOT + 'livechat-chat-history'):
                os.makedirs(settings.MEDIA_ROOT + 'livechat-chat-history')

            for user in LiveChatUser.objects.filter(is_deleted=False, status__in=["1", "2"]):

                # Check whether directory for given bot id exists or not: If not create
                # one
                agent_list = get_agents_under_this_user(user)
                if not os.path.exists(settings.MEDIA_ROOT + 'livechat-chat-history/' + str(user.user.username)):
                    os.makedirs(settings.MEDIA_ROOT + 'livechat-chat-history/' +
                                str(user.user.username))

                for last_x_day in range(1, total_x_days + 2):

                    if last_x_day == total_x_days + 1:
                        day_x = today - timedelta(last_x_day)
                        if os.path.exists(settings.MEDIA_ROOT + 'livechat-chat-history/' + str(user.user.username) + '/chat_history_' + str(day_x.date()) + '.xls'):
                            cmd = 'rm ' + settings.MEDIA_ROOT + 'livechat-chat-history/' + \
                                str(user.user.username) + '/chat_history_' + \
                                str(day_x.date()) + '.xls'
                            os.system(cmd)
                        break

                    last_date = today - timedelta(last_x_day)

                    file_already_exists = False
                    if path.exists(settings.MEDIA_ROOT + "livechat-chat-history/" + str(user.user.username) + "/chat_history_" + str(last_date.date()) + ".xls"):
                        file_already_exists = True

                    if not file_already_exists:

                        livechat_followup_cust_objs = LiveChatFollowupCustomer.objects.filter(
                            completed_date__date=last_date.date(), agent_id__in=agent_list, is_completed=True).values('livechat_customer')
                        message_history_yesterday = LiveChatCustomer.objects.filter(
                            Q(agent_id__in=agent_list, joined_date__date=last_date.date()) | Q(pk__in=livechat_followup_cust_objs)).order_by('-joined_date')

                        # message_history_yesterday = LiveChatMISDashboard.objects.filter(
                        #     joined_date__date=last_date.date())

                        test_wb = Workbook()

                        sheet1 = test_wb.add_sheet("Sheet1")

                        sheet1.write(0, 0, "Date")
                        sheet1.write(0, 1, "Customer Name")
                        sheet1.write(0, 2, "Mobile Number")
                        sheet1.write(0, 3, "Email")
                        sheet1.write(0, 4, "Chat NPS Score")
                        sheet1.write(0, 5, "Chat NPS Feedback")
                        sheet1.write(0, 6, "Interaction Start Date-Time")
                        sheet1.write(0, 7, "Interaction End Date-Time")
                        sheet1.write(0, 8, "Interaction Duration")
                        sheet1.write(0, 9, "Category")
                        sheet1.write(0, 10, "Agent Name")
                        sheet1.write(0, 11, "User ID")
                        sheet1.write(0, 12, "Channel")
                        sheet1.write(0, 13, "Session ID")
                        sheet1.write(0, 14, "Wait Time")
                        sheet1.write(0, 15, "FTR")
                        sheet1.write(0, 16, "Chat Termination")
                        sheet1.write(0, 17, "Cobrowsing NPS")
                        sheet1.write(0, 18, "Cobrowsing NPS Comment")

                        # For handling single cell Multi-line
                        algn1 = xlwt.Alignment()
                        algn1.wrap = 1
                        style1 = xlwt.XFStyle()
                        style1.alignment = algn1

                        row = 1
                        for message in message_history_yesterday:
                            config_obj = LiveChatConfig.objects.get(bot=message.bot)
                            is_original_information_in_reports_enabled = config_obj.is_original_information_in_reports_enabled
                            joined_date = message.joined_date.strftime("%d/%m/%Y")
                            sheet1.write(row, 0, joined_date)
                            if is_original_information_in_reports_enabled and message.original_username != "" and message.username != message.original_username:
                                sheet1.write(row, 1, str(message.username) + "(original - " + str(message.original_username) + ")")
                            else:
                                sheet1.write(row, 1, message.username)
                            if is_original_information_in_reports_enabled and message.original_phone != "" and message.phone != message.original_phone:
                                sheet1.write(row, 2, str(message.phone) + "(original - " + str(message.original_phone) + ")")
                            else:
                                sheet1.write(row, 2, message.phone)
                            if is_original_information_in_reports_enabled and message.original_email != "" and message.email != message.original_email:
                                sheet1.write(row, 3, str(message.email) + "(original - " + str(message.original_email) + ")")
                            else:
                                sheet1.write(row, 3, message.email)
                            if message.rate_value == -1:
                                sheet1.write(row, 4, "NA")
                            else:
                                sheet1.write(row, 4, message.rate_value)
                            
                            if message.nps_text_feedback == "":
                                sheet1.write(row, 5, "NA")
                            else:
                                sheet1.write(row, 5, message.nps_text_feedback)

                            start_time = (message.joined_date + timedelta(hours=5, minutes=30)).strftime(
                                "%d/%m/%Y, %I:%M:%p")
                            sheet1.write(row, 6, start_time)
                            end_time = (message.last_appearance_date + timedelta(hours=5, minutes=30)).strftime(
                                "%d/%m/%Y, %I:%M:%p")
                            if message.followup_assignment:
                                livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(livechat_customer=message)
                                end_time = (livechat_followup_cust_obj.completed_date + timedelta(hours=5, minutes=30)).strftime(
                                    "%d/%m/%Y, %I:%M:%p")
                            sheet1.write(
                                row, 7, end_time)
                            sheet1.write(row, 8, message.get_chat_duration())
                            try:
                                sheet1.write(row, 9, message.closing_category.title)
                            except Exception:
                                sheet1.write(row, 9, 'None')
                                pass
                            try:
                                sheet1.write(
                                    row, 10, message.get_agent_name())
                                sheet1.write(
                                    row, 11, message.get_agent_username())
                            except Exception:
                                sheet1.write(row, 10, 'None')
                                sheet1.write(row, 11, 'None')
                                pass
                            channel_name = message.channel.name
                            if message.followup_assignment:
                                channel_name = message.channel.name + ' (Follow Up)'
                            sheet1.write(row, 12, channel_name)
                            sheet1.write(row, 13, str(message.session_id))
                            sheet1.write(row, 14, message.get_wait_time())
                            sheet1.write(row, 15, message.get_agent_first_time_response_time())
                            sheet1.write(row, 16, message.chat_ended_by)

                            cobrowsing_nps_rating, cobrowsing_nps_comment = message.get_cobrowsing_nps_data()
                            sheet1.write(row, 17, cobrowsing_nps_rating, style1)
                            sheet1.write(row, 18, cobrowsing_nps_comment, style1)
                            row += 1

                        filename = 'livechat-chat-history/' + \
                            str(user.user.username) + '/chat_history_' + \
                            str(last_date.date()) + '.xls'
                        test_wb.save(settings.MEDIA_ROOT + filename)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Chat History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'LiveChat'})
            message_history_datadump_log.write(
                str(today) + ": failed: " + str(e))

        for export_date_request in LiveChatDataExportRequest.objects.filter(is_completed=False, report_type="2"):
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]
                user = export_date_request.user

                date_format = "%Y-%m-%d"
                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                temp_date = start_date

                while temp_date <= end_date:

                    file_path = settings.MEDIA_ROOT + "livechat-chat-history/" + \
                        str(user.user.username) + "/chat_history_" + \
                        str(temp_date) + ".xls"

                    if path.exists(file_path):
                        temp_date = temp_date + timedelta(1)
                        continue

                    # message_history_objs = LiveChatMISDashboard.objects.filter(
                    #     joined_date__date=temp_date)
                    agent_list = get_agents_under_this_user(user) 
                    livechat_followup_cust_objs = LiveChatFollowupCustomer.objects.filter(
                        completed_date__date=temp_date, agent_id__in=agent_list, is_completed=True).values('livechat_customer')
                    message_history_objs = LiveChatCustomer.objects.filter(
                        Q(agent_id__in=agent_list, joined_date__date=temp_date) | Q(pk__in=livechat_followup_cust_objs)).order_by('-joined_date')

                    test_wb = Workbook()

                    sheet1 = test_wb.add_sheet("Sheet1")

                    sheet1.write(0, 0, "Date")
                    sheet1.write(0, 1, "Customer Name")
                    sheet1.write(0, 2, "Mobile Number")
                    sheet1.write(0, 3, "Email")
                    sheet1.write(0, 4, "Chat NPS Score")
                    sheet1.write(0, 5, "Chat NPS Feedback")
                    sheet1.write(0, 6, "Interaction Start Date-Time")
                    sheet1.write(0, 7, "Interaction End Date-Time")
                    sheet1.write(0, 8, "Interaction Duration")
                    sheet1.write(0, 9, "Category")
                    sheet1.write(0, 10, "Agent Name")
                    sheet1.write(0, 11, "User ID")
                    sheet1.write(0, 12, "Channel")
                    sheet1.write(0, 13, "Session ID")
                    sheet1.write(0, 14, "Wait Time")
                    sheet1.write(0, 15, "FTR")
                    sheet1.write(0, 16, "Chat Termination")
                    sheet1.write(0, 17, "Cobrowsing NPS")
                    sheet1.write(0, 18, "Cobrowsing NPS Comment")

                    # For handling single cell Multi-line
                    algn1 = xlwt.Alignment()
                    algn1.wrap = 1
                    style1 = xlwt.XFStyle()
                    style1.alignment = algn1

                    row = 1
                    for message in message_history_objs:
                        config_obj = LiveChatConfig.objects.get(bot=message.bot)
                        is_original_information_in_reports_enabled = config_obj.is_original_information_in_reports_enabled
                        joined_date = message.joined_date.strftime("%d/%m/%Y")
                        sheet1.write(row, 0, joined_date)
                        if is_original_information_in_reports_enabled and message.original_username != "" and message.username != message.original_username:
                            sheet1.write(row, 1, str(message.username) + "(original - " + str(message.original_username) + ")")
                        else:
                            sheet1.write(row, 1, message.username)
                        if is_original_information_in_reports_enabled and message.original_phone != "" and message.phone != message.original_phone:
                            sheet1.write(row, 2, str(message.phone) + "(original - " + str(message.original_phone) + ")")
                        else:
                            sheet1.write(row, 2, message.phone)
                        if is_original_information_in_reports_enabled and message.original_email != "" and message.email != message.original_email:
                            sheet1.write(row, 3, str(message.email) + "(original - " + str(message.original_email) + ")")
                        else:
                            sheet1.write(row, 3, message.email)
                        if message.rate_value == -1:
                            sheet1.write(row, 4, "NA")
                        else:
                            sheet1.write(row, 4, message.rate_value)
                        
                        if message.nps_text_feedback == "":
                            sheet1.write(row, 5, "NA")
                        else:
                            sheet1.write(row, 5, message.nps_text_feedback)

                        start_time = (message.joined_date + timedelta(hours=5, minutes=30)).strftime(
                            "%d/%m/%Y, %I:%M:%p")
                        sheet1.write(row, 6, start_time)
                        end_time = (message.last_appearance_date + timedelta(hours=5, minutes=30)).strftime(
                            "%d/%m/%Y, %I:%M:%p")
                        if message.followup_assignment:
                            livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(livechat_customer=message)
                            end_time = (livechat_followup_cust_obj.completed_date + timedelta(hours=5, minutes=30)).strftime(
                                "%d/%m/%Y, %I:%M:%p")
                        sheet1.write(
                            row, 7, end_time)
                        sheet1.write(row, 8, message.get_chat_duration())
                        try:
                            sheet1.write(row, 9, message.category.title)
                        except Exception:
                            sheet1.write(row, 9, 'None')
                            pass
                        try:
                            sheet1.write(
                                row, 10, message.get_agent_name())
                            sheet1.write(
                                row, 11, message.get_agent_username())
                        except Exception:
                            sheet1.write(row, 10, 'None')
                            sheet1.write(row, 11, 'None')
                            pass
                        channel_name = message.channel.name
                        if message.followup_assignment:
                            channel_name = message.channel.name + ' (Follow Up)'
                        sheet1.write(row, 12, channel_name)
                        sheet1.write(row, 13, str(message.session_id))
                        sheet1.write(row, 14, message.get_wait_time())
                        sheet1.write(row, 15, message.get_agent_first_time_response_time())
                        sheet1.write(row, 16, message.chat_ended_by)

                        cobrowsing_nps_rating, cobrowsing_nps_comment = message.get_cobrowsing_nps_data()
                        sheet1.write(row, 17, cobrowsing_nps_rating, style1)
                        sheet1.write(row, 18, cobrowsing_nps_comment, style1)

                        row += 1

                    file_path = "livechat-chat-history/" + \
                        str(user.user.username) + "/chat_history_" + \
                        str(temp_date) + ".xls"
                    test_wb.save(settings.MEDIA_ROOT + file_path)

                    temp_date = temp_date + timedelta(1)
                
                if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/livechat-chat-history/' + str(user.user.username)):
                    os.makedirs(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/livechat-chat-history/' + str(user.user.username))

                export_zip_file_path = "LiveChatApp/livechat-chat-history/" + \
                    str(user.user.username) + "/ChatHistoryCustom-" + \
                    str(export_date_request.pk) + ".zip"

                zip_obj = ZipFile(settings.SECURE_MEDIA_ROOT + export_zip_file_path, 'w')

                temp_date = start_date

                while temp_date <= end_date:
                    try:
                        file_path = "livechat-chat-history/" + \
                            str(user.user.username) + "/chat_history_" + \
                            str(temp_date) + '.xls'
                        zip_obj.write(settings.MEDIA_ROOT +
                                      file_path, basename(file_path))
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Chat History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
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
                    str(file_access_management_obj.key) + '/LiveChatHistory.zip'

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
                            We have received a request to provide you with the LiveChat Chat History from {} to {}. Please click on the link below to download the file.
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
                    email_subject = "LiveChat Chat History For " + \
                        str(username)
                    send_email_to_customer_via_awsses(email_id, email_subject, body)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Chat History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'LiveChat'})
                message_history_datadump_log.write(
                    str(today) + ": failed: " + str(e))
                export_date_request.is_completed = False
                export_date_request.save()

        message_history_datadump_log.close()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
