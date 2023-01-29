import os
import sys
import time
import json
import logging
import requests
import threading
import mimetypes
import datetime
import http.client
import imaplib
import email
import uuid
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from email_reply_parser import EmailReplyParser
from email.header import decode_header
from LiveChatApp.models import LiveChatCategory, LiveChatCustomer, LiveChatAdminConfig, LiveChatUser, LiveChatMISDashboard, LiveChatEmailConfig, LiveChatEmailConfigSetup, LiveChatReportedCustomer, LiveChatMISEmailData
from EasyChatApp.models import Channel, User
from LiveChatApp.utils import get_agents_under_this_user, get_livechat_category_object, get_agent_token, check_is_customer_blocked
from LiveChatApp.livechat_channels_webhook import send_data_to_websocket, create_image_thumbnail
from LiveChatApp.utils_email import *
from LiveChatApp.utils_custom_encryption import *


logger = logging.getLogger(__name__)


def retrieve_livechat_mails():
    try:
        logger.info("---------- Retrieving livechat mails ---------",
                    extra={'AppName': 'LiveChat'})

        email_config_setup_pks = LiveChatEmailConfig.objects.filter(
            is_livechat_enabled_for_email=True, is_successful_authentication_complete=True).values_list('current_email_setup', flat=True)
        email_config_setup_objs = LiveChatEmailConfigSetup.objects.filter(pk__in=email_config_setup_pks)
        email_channel_obj = Channel.objects.filter(name="Email").first()

        for email_config_setup_obj in email_config_setup_objs:
            try:
                custom_encrypt_obj = CustomEncrypt()
                email_config_password = custom_encrypt_obj.decrypt(
                    email_config_setup_obj.password)

                imap_server = imap_server_authentication(email_config_setup_obj.email, email_config_password,
                                                         email_config_setup_obj.server, email_config_setup_obj.security)

                # if authentication fails skip this email config setup
                if not imap_server:
                    continue

                imap_server.select('INBOX')

                agent_objs = get_agents_under_this_user(
                    email_config_setup_obj.admin_config.admin, False)

                last_mail_uid = email_config_setup_obj.last_mail_uid
                last_mail_uid = str(int(last_mail_uid) + 1)
                result, data = imap_server.uid(
                    'search', None, 'UID', last_mail_uid + ':*')

                for mail_uid in data[0].split():

                    if int(mail_uid.decode("utf-8")) < int(last_mail_uid):
                        continue

                    status, email_message = imap_server.uid(
                        'fetch', mail_uid, '(RFC822)')
                    raw_message = email.message_from_bytes(email_message[0][1])

                    from_addr = get_from_addr(raw_message)

                    # skips spam emails where from address is empty
                    if from_addr == "":
                        continue

                    livechat_customer_obj = LiveChatCustomer.objects.filter(agent_id__in=agent_objs, channel=email_channel_obj,
                                                                            email=from_addr, is_session_exp=False).first()

                    if not livechat_customer_obj:
                        livechat_customer_obj = create_customer_obj_and_assign_agent(
                            from_addr, email_channel_obj, email_config_setup_obj.server, agent_objs)

                        # if not able to create customer obj and assign agent then poll for next email
                        if not livechat_customer_obj:
                            continue

                    # To get mail message ID
                    # mail_message_id = get_mail_message_id_from_db(livechat_customer_obj, LiveChatMISDashboard, LiveChatMISEmailData)

                    # if mail_message_id.strip() == "":
                    mail_message_id = get_mail_message_id(raw_message)

                    # get mail subject
                    subject = get_mail_subject(raw_message)

                    # get and store text message from mail
                    text_message = get_text_message(raw_message)

                    if text_message.strip() != "":
                        save_and_send_data_to_agent_via_socket(
                            text_message, "", livechat_customer_obj, mail_uid, mail_message_id, subject, False)

                    # get and store attachments from mail
                    attachment_path_list = save_attachment(raw_message)

                    if len(attachment_path_list):

                        for attachment_path in attachment_path_list:

                            save_and_send_data_to_agent_via_socket(
                                "", attachment_path, livechat_customer_obj, mail_uid, mail_message_id, subject, True)

                email_config_setup_obj.last_mail_uid = mail_uid.decode("utf-8")
                email_config_setup_obj.save()

                imap_server.close()
                imap_server.logout()

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("retrieve_livechat_mails inside email_config_setup_obj loop: %s at %s", e, str(
                    exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("retrieve_livechat_mails: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def create_customer_obj_and_assign_agent(from_addr, email_channel_obj, server, agent_objs):

    try:
        agents_available_for_assignment = LiveChatUser.objects.filter(status="3", user__in=User.objects.filter(username__in=agent_objs),
                                                                      is_deleted=False).order_by('last_email_chat_assigned_time')

        if agents_available_for_assignment.count() == 0:
            return None

        livechat_agent = agents_available_for_assignment.first()
        bot_obj = livechat_agent.bots.filter(is_deleted=False).first()

        active_url = server
        session_id = str(uuid.uuid4())
        category_obj = get_livechat_category_object(
            '-1', livechat_agent.bots.first(), LiveChatCategory)

        customer_details = [{'key': 'Source', 'value': 'Mobile'}]

        customer_obj = LiveChatCustomer.objects.create(session_id=session_id,
                                                       username=from_addr,
                                                       email=from_addr,
                                                       client_id=from_addr,
                                                       is_online=True,
                                                       bot=bot_obj,
                                                       agent_id=livechat_agent,
                                                       channel=email_channel_obj,
                                                       category=category_obj,
                                                       active_url=active_url,
                                                       closing_category=category_obj,
                                                       customer_details=json.dumps(customer_details))

        livechat_agent.last_email_chat_assigned_time = timezone.now()
        livechat_agent.ongoing_chats = livechat_agent.ongoing_chats + 1
        livechat_agent.save()

        customer_obj.agents_group.add(livechat_agent)
        customer_obj.save()

        # adding default system message on chat assign
        text_message = "Customer Name: " + str(customer_obj.username) + " | Agent Name: " + str(customer_obj.agent_id.user.first_name) + " " + str(
            customer_obj.agent_id.user.last_name) + "(" + str(customer_obj.agent_id.user.username) + ")"

        LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                            sender="System",
                                            text_message=text_message,
                                            sender_name="system",
                                            message_time=timezone.now(),
                                            attachment_file_name="",
                                            attachment_file_path="")

        return customer_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_customer_obj_and_assign_agent: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return None


def save_and_send_data_to_agent_via_socket(text_message, path, customer_obj, mail_uid, mail_message_id, subject, is_attachment):
    try:

        attachment_file_name = ""
        thumbnail_url = ""
        if is_attachment:
            attachment_file_name = path.split('/')[-1]
            file_extension = attachment_file_name.split(".")

            image_file_extentions = ["png", "PNG", "JPG", "JPEG", "jpg",
                                     "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif", "jpe"]

            if file_extension[-1].lower() in image_file_extentions:
                thumbnail_url = create_image_thumbnail(
                    path, attachment_file_name)

        livechat_mis_obj = LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                               sender="Customer",
                                                               text_message=text_message,
                                                               sender_name=customer_obj.get_complete_username(),
                                                               message_time=timezone.now(),
                                                               attachment_file_name=attachment_file_name,
                                                               attachment_file_path=path,
                                                               thumbnail_file_path=thumbnail_url)

        LiveChatMISEmailData.objects.create(livechat_mis_obj=livechat_mis_obj,
                                            mail_uid=mail_uid.decode("utf-8"),
                                            mail_message_id=mail_message_id,
                                            mail_subject=subject)

        data = json.dumps({
            "sender": "Customer",
            "message": json.dumps({
                "text_message": text_message,
                "type": "message",
                "channel": customer_obj.channel.name,
                "path": path,
                        "thumbnail_url": thumbnail_url,
                        "session_id": str(customer_obj.session_id),
                        "sender_name": customer_obj.get_complete_username(),
                        "bot_id": str(customer_obj.bot.pk),
                        "message_id": str(livechat_mis_obj.message_id)
            })
        })

        # sending data in one to one socket
        one_to_one_socket_thread = threading.Thread(target=send_data_to_websocket, args=(
            settings.EASYCHAT_DOMAIN, [data], str(customer_obj.session_id)), daemon=True)
        one_to_one_socket_thread.start()

        agent_websocket_token = get_agent_token("")

        # sending data to global socket
        global_socket_thread = threading.Thread(target=send_data_to_websocket, args=(
            settings.EASYCHAT_DOMAIN, [data], agent_websocket_token), daemon=True)
        global_socket_thread.start()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_and_send_data_to_agent_via_socket: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
