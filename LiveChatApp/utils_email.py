import os
import sys
import json
import logging
import time
import requests
import threading
import mimetypes
import datetime
import http.client
import imaplib
import email
import magic
import email.utils
from django.conf import settings
from django.utils import timezone
from django.http import FileResponse
from urllib.parse import quote
from os import path
from os.path import basename
from uuid import uuid4
from django.db.models import Q, Count
from email_reply_parser import EmailReplyParser
from email.header import decode_header
from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils import get_time, get_livechat_date_format
from LiveChatApp.utils_validation import *


logger = logging.getLogger(__name__)
file_validation_obj = LiveChatFileValidation()


def imap_server_authenticate(admin_config, email_config_id, email_config_password, email_config_server, email_config_security):
    try:
        status = "fail"
        import socket
        socket.setdefaulttimeout(2)
        imap_server = None

        if email_config_security == "ssl":
            imap_server = imaplib.IMAP4_SSL(email_config_server)
        elif email_config_security == "tls":
            imap_server = imaplib.IMAP4(email_config_server)
            imap_server.starttls()

        imap_server.login(email_config_id, email_config_password)
        imap_server.logout()

        status = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("imap_server_authenticate %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    socket.setdefaulttimeout(None)
    return status


def get_email_config_obj(admin_config, LiveChatEmailConfig):
    try:

        email_config_obj = LiveChatEmailConfig.objects.filter(
            admin_config=admin_config).first()

        if not email_config_obj:
            email_config_obj = LiveChatEmailConfig.objects.create(
                admin_config=admin_config)

        return email_config_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_email_config_obj %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return None


def imap_server_authentication(email, password, server, security):
    try:
        import socket
        socket.setdefaulttimeout(2)
        imap_server = None

        if security == "ssl":
            imap_server = imaplib.IMAP4_SSL(server)
        elif security == "tls":
            imap_server = imaplib.IMAP4(server)
            imap_server.starttls()

        imap_server.login(email, password)

        return imap_server

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("imap_server_authentication %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return None


def get_text_message(raw_message):
    try:
        text_message = ""
        for part in raw_message.walk():
            if part.get_content_type() == "text/plain":
                text_message = part.get_payload(decode=True).decode()

        text_message = EmailReplyParser.parse_reply(text_message)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_text_message: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        text_message = ""

    return text_message


def save_attachment(raw_message):
    try:
        attachment_path_list = []
        for part in raw_message.walk():

            if part.get_content_maintype() == 'multipart':
                continue

            if part.get('Content-Disposition') is None:
                continue

            file_name = part.get_filename()

            if bool(file_name):
                file_content = part.get_payload(decode=True)
                file_src = save_and_get_email_file_src(file_content)
                if file_src == "":
                    continue

                attachment_path_list.append(file_src)

        return attachment_path_list

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_attachment: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return []


def save_and_get_email_file_src(file_content):
    try:
        file_directory = "files/email-attachment/"
        file_ext = file_validation_obj.get_file_extension_from_content(
            file_content)
        file_ext = file_ext.split(".")[-1]
        file_name = str(uuid4().hex)

        allowed_file_extensions = ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "jpe", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg", "mp2",
                                   "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt", "flv", "swf", "avchd", "pdf", "docs", "docx", "doc", "PDF", "txt", "TXT"]

        if file_ext.lower() not in allowed_file_extensions:
            return ""

        file_name = file_name + "." + file_ext

        full_path = file_directory + file_name

        local_file = open(full_path, 'wb')

        local_file.write(file_content)
        local_file.close()

        full_path = "/files/email-attachment/" + file_name

        return full_path

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_and_get_email_file_src: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return ""


def get_mail_subject(raw_message):
    try:
        subject, encoding = decode_header(raw_message["Subject"])[0]

        # if it's a bytes, decode to str
        if isinstance(subject, bytes):
            subject = subject.decode(encoding)

        return subject
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_mail_subject: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return ""


def get_from_addr(raw_message):
    try:
        from_addr, encoding = decode_header(raw_message.get("From"))[0]

        # if it's a bytes, decode to str
        if isinstance(from_addr, bytes):
            if not encoding:
                return ""
            from_addr = from_addr.decode(encoding)

        from_addr_data = email.utils.parseaddr(from_addr)
        return from_addr_data[1]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_from_addr: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return ""


def get_mail_message_id(raw_message):
    try:
        mail_message_id, encoding = decode_header(raw_message["Message-ID"])[0]

        # if it's a bytes, decode to str
        if isinstance(mail_message_id, bytes):
            mail_message_id = mail_message_id.decode(encoding)

        return mail_message_id
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_mail_message_id: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return ""


def get_mail_message_id_from_db(livechat_customer_obj, LiveChatMISDashboard, LiveChatMISEmailData):
    try:
        mail_message_id = ""

        last_conversation_mail_data = LiveChatMISEmailData.objects.filter(
            livechat_mis_obj__livechat_customer=livechat_customer_obj).last()

        if last_conversation_mail_data:
            mail_message_id = last_conversation_mail_data.mail_message_id

        return mail_message_id
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_mail_message_id_from_db: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return ""


def get_mail_subject_from_db(livechat_customer_obj, LiveChatMISDashboard, LiveChatMISEmailData):
    try:
        subject = ""
        last_conversation_mail_data = LiveChatMISEmailData.objects.filter(
            livechat_mis_obj__livechat_customer=livechat_customer_obj).last()

        if last_conversation_mail_data:
            subject = last_conversation_mail_data.mail_subject

        return subject

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_mail_message_id_from_db: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return ""


def send_email_message_to_customer(message, channel_file_url, customer_obj, livechat_mis_obj, email_config_obj, LiveChatMISDashboard, LiveChatMISEmailData, LiveChatEmailConfigSetup):
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders

        email_config_setup_obj = email_config_obj.current_email_setup

        email_user = email_config_setup_obj.email

        custom_encrypt_obj = CustomEncrypt()
        email_password = custom_encrypt_obj.decrypt(
            email_config_setup_obj.password)

        email_send = customer_obj.email
        email_server = email_config_setup_obj.server

        mail_message = MIMEMultipart()

        mail_message['From'] = email_user
        mail_message['To'] = email_send

        mail_message_id = get_mail_message_id_from_db(
            customer_obj, LiveChatMISDashboard, LiveChatMISEmailData)

        if mail_message_id.strip() == "":
            mail_message_id = email.utils.make_msgid()
            mail_message["Message-ID"] = mail_message_id
        else:
            mail_message["In-Reply-To"] = mail_message_id
            mail_message["References"] = mail_message_id

        subject = get_mail_subject_from_db(
            customer_obj, LiveChatMISDashboard, LiveChatMISEmailData)

        if subject.strip() == "":
            subject = LIVECHAT_EMAIL_CHAT_DEFAULT_SUBJECT

        mail_message['Subject'] = subject

        body = message
        mail_message.attach(MIMEText(body, 'plain'))

        if channel_file_url != "":

            attachment_file_name = channel_file_url.split("/")[-1]
            attachment = open(settings.MEDIA_ROOT +
                              'email-attachment/' + attachment_file_name, 'rb')

            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            "attachment; filename= " + attachment_file_name)

            mail_message.attach(part)

        text = mail_message.as_string()
        smtp_server = smtplib.SMTP(email_server.replace("imap", "smtp"))
        smtp_server.starttls()
        smtp_server.login(email_user, email_password)

        smtp_server.sendmail(email_user, email_send, text)
        smtp_server.quit()

        LiveChatMISEmailData.objects.create(livechat_mis_obj=livechat_mis_obj,
                                            mail_message_id=mail_message_id,
                                            mail_subject=subject)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_email_message_to_customer: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def check_if_email_chat_to_be_resolved(customer_obj, admin_config, LiveChatEmailConfig, LiveChatMISDashboard, LiveChatMISEmailData):
    try:
        if customer_obj.channel.name == "Email":
            email_config_obj = get_email_config_obj(
                admin_config, LiveChatEmailConfig)
            if email_config_obj.is_livechat_enabled_for_email and email_config_obj.is_successful_authentication_complete:

                chat_disposal_duration = int(
                    email_config_obj.chat_disposal_duration)
                latest_message = LiveChatMISDashboard.objects.filter(
                    livechat_customer=customer_obj).last()

                diff = timezone.now() - latest_message.message_time
                livechat_mis_data = LiveChatMISEmailData.objects.filter(
                    livechat_mis_obj__livechat_customer=customer_obj)

                if diff.days >= chat_disposal_duration and livechat_mis_data.exists():
                    return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_if_email_chat_to_be_resolved: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return False


def get_livechat_email_initiated_time(livechat_cust_obj, LiveChatMISEmailData):
    try:
        email_initiated_time = "-"
        livechat_mis_email = LiveChatMISEmailData.objects.filter(
            livechat_mis_obj__livechat_customer=livechat_cust_obj).first()

        if livechat_mis_email:
            email_initiated_time = get_time(
                livechat_mis_email.livechat_mis_obj.message_time)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_livechat_email_initiated_time: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return email_initiated_time


def get_livechat_email_initiated_date(livechat_cust_obj, LiveChatMISEmailData):
    try:
        email_initiated_date = "-"
        livechat_mis_email = LiveChatMISEmailData.objects.filter(
            livechat_mis_obj__livechat_customer=livechat_cust_obj).first()

        if livechat_mis_email:
            email_initiated_date = get_livechat_date_format(
                livechat_mis_email.livechat_mis_obj.message_time)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_livechat_email_initiated_date: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return email_initiated_date
