import os
import sys
import json
import xlwt
import pytz
import time

from xlwt import Formula, Workbook
from LiveChatApp.models import *
from LiveChatApp.utils import logger
from zipfile import ZipFile
from datetime import datetime, timedelta
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


def create_livechat_conversation_file_for_last_day(user, bot_obj, agent_list):
    try:
        today = datetime.now()
        last_day_wb = Workbook()
        last_date = today - timedelta(1)

        last_day_wb = add_conversations_sheet(last_day_wb, last_date, bot_obj, agent_list)

        file_date_range = (today - timedelta(1)).strftime("%d-%m-%Y") + \
            " - " + (today - timedelta(1)).strftime("%d-%m-%Y")

        filename = 'livechat-conversations/' + \
            str(user.user.username) + '/LiveChat Conversations_' + \
            str(bot_obj.name) + '_' + file_date_range + '.xls'

        last_day_wb.save(settings.MEDIA_ROOT + filename)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_livechat_conversation_file_for_last_day cronjob : %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def create_livechat_conversation_file_for_last_week(user, bot_obj, agent_list):
    try:
        today = datetime.now()
        last_week_wb = Workbook()

        for last_x_day in range(7, 0, -1):
            last_date = today - timedelta(last_x_day)
            last_week_wb = add_conversations_sheet(
                last_week_wb, last_date, bot_obj, agent_list)

        file_date_range = (today - timedelta(7)).strftime("%d-%m-%Y") + \
            " - " + (today - timedelta(1)).strftime("%d-%m-%Y")

        filename = 'livechat-conversations/' + \
            str(user.user.username) + '/LiveChat Conversations_' + \
            str(bot_obj.name) + '_' + file_date_range + '.xls'
        last_week_wb.save(settings.MEDIA_ROOT + filename)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_livechat_conversation_file_for_last_week cronjob : %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def create_livechat_conversation_file_for_last_month(user, bot_obj, agent_list):
    try:
        today = datetime.now()
        last_month_wb = Workbook()

        for last_x_day in range(30, 0, -1):
            last_date = today - timedelta(last_x_day)
            last_month_wb = add_conversations_sheet(
                last_month_wb, last_date, bot_obj, agent_list)

        file_date_range = (today - timedelta(30)).strftime("%d-%m-%Y") + \
            " - " + (today - timedelta(1)).strftime("%d-%m-%Y")

        filename = 'livechat-conversations/' + \
            str(user.user.username) + '/LiveChat Conversations_' + \
            str(bot_obj.name) + '_' + file_date_range + '.xls'
        last_month_wb.save(settings.MEDIA_ROOT + filename)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_livechat_conversation_file_for_last_month cronjob : %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def cronjob():
    try:
        start_time = time.time()
        total_x_days = 31
        today = datetime.now()

        if not os.path.exists(settings.MEDIA_ROOT + "livechat-conversations"):
            os.makedirs(settings.MEDIA_ROOT + "livechat-conversations")

        user_objs = LiveChatUser.objects.filter(is_deleted=False, status__in=["1", "2"])

        for user in user_objs.iterator():
            bot_objs = user.bots.all()
            for bot_obj in bot_objs.iterator():
                bot_name = bot_obj.name.strip().replace(" ", "_")

                agent_list = get_agents_under_this_user(user)
                user_dir_absolute_path = settings.MEDIA_ROOT + LIVECHAT_CONVERSATION_PATH + str(user.user.username)
                if not os.path.exists(user_dir_absolute_path):
                    os.makedirs(user_dir_absolute_path)

                for last_x_day in range(1, total_x_days + 2):

                    if last_x_day == total_x_days + 1:
                        day_x = today - timedelta(last_x_day)
                        if os.path.exists(user_dir_absolute_path + LIVECHAT_CONVERSATION_FILE_NAME + str(bot_name) + "_" + str(day_x.date().strftime(DATE_DD_MM_YYYY)) + ".xls"):
                            cmd = "rm " + user_dir_absolute_path + LIVECHAT_CONVERSATION_FILE_NAME + str(bot_name) + "_" + str(day_x.date().strftime(DATE_DD_MM_YYYY)) + ".xls"
                            os.system(cmd)
                        break

                    last_date = today - timedelta(last_x_day)

                    file_already_exists = False
                    if path.exists(user_dir_absolute_path + LIVECHAT_CONVERSATION_FILE_NAME + str(bot_name) + "_" + str(last_date.date().strftime(DATE_DD_MM_YYYY)) + ".xls"):
                        file_already_exists = True

                    if not file_already_exists:
                        new_wb = Workbook()
                        add_conversations_sheet(
                            new_wb, last_date, bot_obj, agent_list)

                        filename = LIVECHAT_CONVERSATION_PATH + str(user.user.username) + LIVECHAT_CONVERSATION_FILE_NAME + str(bot_name) + "_" + str(last_date.date().strftime(DATE_DD_MM_YYYY)) + ".xls"
                        new_wb.save(settings.MEDIA_ROOT + filename)

        logger.info("Time taken to generate LiveChat_Conversations report: " + str(time.time() - start_time) + " secs", extra={'AppName': 'LiveChat'})
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def add_conversations_sheet(workbook, last_date, bot_obj, agent_list):

    try:
        from LiveChatApp.models import LiveChatConfig
        livechat_followup_cust_objs = LiveChatFollowupCustomer.objects.filter(
            completed_date__date=last_date.date(), agent_id__in=agent_list, is_completed=True).values('livechat_customer')
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            Q(agent_id__in=agent_list, joined_date__date=last_date.date()) | Q(pk__in=livechat_followup_cust_objs)).filter(bot=bot_obj).order_by('joined_date')

        client_ids = []
        time_zone = pytz.timezone(settings.TIME_ZONE)

        for livechat_cust_obj in livechat_cust_objs.iterator():
            if livechat_cust_obj.client_id not in client_ids:
                client_ids.append(livechat_cust_obj.client_id)

        sheet = workbook.add_sheet(last_date.strftime("%d-%m-%Y"))
        style = xlwt.XFStyle()
        alignment_style = xlwt.XFStyle()
        conversation_history_style = xlwt.XFStyle()
        config_obj = LiveChatConfig.objects.get(bot=bot_obj)

        # font
        font = xlwt.Font()
        font.bold = True
        style.font = font
        conversation_history_style.font = font

        alignment = xlwt.Alignment()
        alignment.vert = xlwt.Alignment.VERT_TOP
        alignment_style.alignment = alignment
        conversation_history_style.alignment = alignment

        sheet.write(0, 0, "Sr. No.", style=style)
        sheet.write(0, 1, "Name", style=style)
        sheet.write(0, 2, "Email ID", style=style)
        sheet.write(0, 3, "Phone", style=style)
        sheet.write(0, 4, "Client ID", style=style)
        sheet.write(0, 5, "Bot Name", style=style)
        sheet.write(0, 6, "Assigned Agent", style=style)
        sheet.write(0, 7, "Chat initiated on", style=style)
        sheet.write(0, 8, "Chat initiated at", style=style)
        sheet.write(0, 9, "Chat re-initiated at", style=style)
        sheet.write(0, 10, "Chat initiated from(URL)", style=style)
        sheet.write(0, 11, "Wait Time", style=style)
        sheet.write(0, 12, "")
        sheet.write(0, 13, "Date", style=style)
        sheet.write(0, 14, "Time", style=style)
        sheet.write(0, 15, "User", style=style)
        sheet.write(0, 16, "Name", style=style)
        sheet.write(0, 17, "Message", style=style)
        sheet.write(0, 18, "Attachment", style=style)
        row = 1
        client_count = 1

        for client_id in client_ids:

            customer_objs = LiveChatCustomer.objects.filter(
                client_id=client_id).filter(Q(joined_date__date=last_date.date()) | Q(pk__in=livechat_followup_cust_objs)).exclude(Q(agent_id=None) & Q(followup_assignment=False)).order_by("joined_date")
            customer_name = ""
            customer_email = ""
            customer_phone = ""
            assigned_agent = ""
            chat_reinitiated = ""
            chat_initiated_url = ""
            wait_time = ""

            is_chat_reinitiated = False
            for customer_obj in customer_objs.iterator():
                original_name = ""
                original_phone = ""
                original_email = ""
                if config_obj.is_original_information_in_reports_enabled:
                    if customer_obj.original_username != "" and customer_obj.original_username != customer_obj.username:
                        original_name = " (original - " + customer_obj.original_username + ")"
                    if customer_obj.original_email != "" and customer_obj.original_email != customer_obj.email:
                        original_email = " (original - " + customer_obj.original_email + ")"
                    if customer_obj.original_phone != "" and customer_obj.original_phone != customer_obj.phone:
                        original_phone = " (original - " + customer_obj.original_phone + ")"

                customer_name += str(
                    customer_obj.username) + original_name + ", "
                customer_email += str(
                    customer_obj.email) + original_email + ", "
                customer_phone += str(
                    customer_obj.phone) + original_phone + ", "
                assigned_agent += str(
                    customer_obj.get_agent_username()) + ", "
                chat_initiated_url += str(
                    customer_obj.active_url) + ", "
                wait_time += str(customer_obj.queue_time) + ", "
                if is_chat_reinitiated:
                    chat_reinitiated += (customer_obj.joined_date.astimezone(time_zone)).strftime("%I:%M %p") + ", "
                is_chat_reinitiated = True

            livechat_messages = LiveChatMISDashboard.objects.filter(
                livechat_customer__in=customer_objs).order_by('message_time')

            livechat_messages_count = livechat_messages.values("message_id").count()
            sheet.write_merge(row, row + livechat_messages_count, 0, 0, client_count, style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 1, 1, customer_name[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 2, 2, customer_email[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 3, 3, customer_phone[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 4, 4, client_id, style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 5, 5, bot_obj.name, style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 6, 6, assigned_agent[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 7, 7, last_date.strftime("%d-%b-%Y"), style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 8, 8, (customer_obj.joined_date.astimezone(time_zone)).strftime("%I:%M %p"), style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 9, 9, chat_reinitiated[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 10, 10, chat_initiated_url[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 11, 11, wait_time[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages_count, 12, 12, "Conversation History >>", style=conversation_history_style)

            for livechat_message in livechat_messages.iterator():
                if livechat_message.message_for == "customer" and livechat_message.sender == "System" and (livechat_message.is_voice_call_message or livechat_message.is_cobrowsing_message or livechat_message.is_file_not_support_message):
                    continue

                sheet.write(
                    row, 13, (livechat_message.message_time).strftime("%d-%b-%Y"))
                sheet.write(row, 14, (livechat_message.message_time.astimezone(time_zone)).strftime("%I:%M %p"))
                sheet.write(row, 15, str(livechat_message.sender))
                sheet.write(row, 16, str(livechat_message.sender_name))
                if livechat_message.text_message != "":
                    sheet.write(row, 17, str(livechat_message.text_message))
                if livechat_message.attachment_file_path != "":
                    attachment_file_path = '"' + str(settings.EASYCHAT_HOST_URL) + \
                        str(livechat_message.attachment_file_path) + \
                        "/?source=excel" + '"'
                    try:
                        sheet.write(
                            row, 18, Formula('HYPERLINK(%s;"Attachment Link")' % attachment_file_path))
                    except Exception as exc:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("in add_conversations_sheet HYPERLINK too long %s at %s", str(exc), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                        sheet.write(row, 18, attachment_file_path)

                row += 1

            client_count += 1
            row += 1

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_conversations_sheet: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return workbook
