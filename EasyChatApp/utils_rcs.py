from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from django.conf import settings

from bs4 import BeautifulSoup
import logging
import requests
import json
import sys
import time
import base64
import mimetypes
from uuid import uuid4

from EasyChatApp.rcs_business_messaging import messages
from EasyChatApp.utils_validation import *

logger = logging.getLogger(__name__)
file_validation_obj = EasyChatFileValidation()

log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'WhatsApp', 'bot_id': 'None'}


def is_image_or_video(file_name):

    is_image_or_video = False

    try:
        file_ext = file_name.split(".")[-1]

        if file_ext.upper() in ["PNG", "JPG", "JPEG", "GIF", "WEBM", "MP2",
                                   "MPEG", "MPE", "MPV", "MP4", "AVI", "MOV"]:
            is_image_or_video = True

        return is_image_or_video

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_image_or_doc %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return is_image_or_video


def is_doc(file_name):

    is_doc = False

    try:
        file_ext = file_name.split(".")[-1]

        if file_ext.upper() in ["PDF", "DOCS", "DOCX", "DOC"]:
            is_doc = True

        return is_doc

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_image_or_doc %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return is_doc


def send_rcs_livechat_agent_response(customer_obj, session_id, message, attached_file_src, data, sender_name, Profile, Bot, RCSDetails):

    response = {}
    response["status"] = 200
    try:
        user_obj = Profile.objects.get(livechat_session_id=session_id)

        if user_obj.livechat_connected == True:

            selected_bot_obj = Bot.objects.get(
                pk=int(customer_obj.bot.pk), is_deleted=False, is_uat=True)

            rcs_obj = RCSDetails.objects.filter(bot=selected_bot_obj)[0]
            service_account_location = rcs_obj.rcs_credentials_file_path

            sender = customer_obj.client_id
            sender = sender.rsplit('_', 1)[1]

            if attached_file_src != "":

                if "channel_file_url" in data:

                    attached_file_src = data["channel_file_url"]

                    try:
                        attached_file_src = settings.EASYCHAT_HOST_URL + attached_file_src

                        file_name = attached_file_src.split("/")[-1]
                        if is_image_or_video(file_name):
                            FileMessage = messages.FileMessage(attached_file_src)
                            cluster = messages.MessageCluster().append_message(FileMessage)
                            cluster.send_to_msisdn(sender, service_account_location)

                        elif is_doc(file_name):
                            suggestions = [messages.OpenUrlAction('Open Document',
                                           'reply:postback_data_1234', attached_file_src)]
                            text_msg = messages.TextMessage('agent has sent a document')
                            cluster = messages.MessageCluster().append_message(text_msg)
                            for suggestion in suggestions:
                                cluster.append_suggestion_chip(suggestion)
                            cluster.send_to_msisdn(sender, service_account_location)

                        else:
                            img_url = settings.EASYCHAT_HOST_URL + "/static/LiveChatApp/img/gbm_doc.jpg"
                            FileMessage = messages.FileMessage(img_url)
                            cluster = messages.MessageCluster().append_message(FileMessage)
                            cluster.send_to_msisdn(sender, service_account_location)
                    
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("send_rcs_livechat_agent_response: %s at %s",
                                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            if message != "":
                message_text = messages.TextMessage(message)
                cluster = messages.MessageCluster().append_message(message_text)
                cluster.send_to_msisdn(sender, service_account_location)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_rcs_livechat_agent_response %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response["status"] = 500

    return response


def save_and_get_rcs_file_src(attachment):
    try:
        import os
        from urllib.parse import urlparse

        url = attachment
        req = requests.get(url=url)

        file_content = req.content

        file_name = str(uuid4().hex)
        file_directory = "files/googlercs-attachment/"

        file_ext = get_file_extension_from_content(file_content)
        file_ext = file_ext.split(".")[-1]

        file_name = file_name + "." + file_ext

        allowed_file_extensions = ["PNG", "JPG", "JPEG", "GIF", "PDF", "DOCS", "DOCX", "DOC", "XLS"]

        if file_ext.upper() not in allowed_file_extensions:
            return ""

        full_path = file_directory + file_name
        local_file = open(full_path, 'wb')
        local_file.write(file_content)
        local_file.close()

        full_path = "/files/googlercs-attachment/" + file_name

        return full_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_and_get_rcs_file_src %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return ""


def rcs_html_tags_formatter(message):
    try:    
        message = message.replace(' ', ' ')
        message = message.replace('&nbsp;', ' ')

        if '<ol style=";text-align:right;direction:rtl">' in message:
            message = html_ol_rtl_formatter_for_rcs(message)

        if '<ul style=";text-align:right;direction:rtl">' in message:
            message = html_ul_rtl_formatter_for_rcs(message)

        tags = {
            "<p>": "", "</p>": "\n",
        }

        for tag in tags:
            message = message.replace(tag, tags[tag])
        if "</a>" in message:
            message = message.replace("mailto:", "").replace("tel:", "")
            soup = BeautifulSoup(message, "html.parser")
            for link in soup.findAll('a'):
                href = link.get('href')
                link_name = link.string
                link_element = message[message.find(
                    "<a"):message.find("</a>")] + "</a>"
                if link_name.replace("http://", "").replace("https://", "").replace("*", "").replace("_", "").strip() == href.replace("http://", "").replace("https://", "").strip():
                    message = message.replace(link_element, ' ' + link_name)
                else:
                    message = message.replace(
                        link_element, link_name + " (" + href + ")")
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed rcs html tags formatter: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return message


def rcs_html_list_formatter(sent):
    try:
        logger.info("---Rcs html list string found---", extra=log_param)
        ul_end_position = 0
        ol_end_position = 0
        if "<ul>" in sent:
            for idx in range(sent.count("<ul>")):
                ul_position = sent.find("<ul>", ul_end_position)
                ul_end_position = sent.find("</ul>", ul_position)
                list_str = sent[ul_position:ul_end_position]
                logger.info("RCS HTML UL LIST STRING %s : %s", str(
                    idx + 1), str(list_str), extra=log_param)
                items = list_str.split("</li>")
                if len(items) > 1:
                    formatted_list_str = ""
                    for index, item in enumerate(items):
                        if item.strip() != "":
                            if index == 0:
                                formatted_list_str += "• " + item.strip()
                            elif index < len(items) - 1:
                                formatted_list_str += "\n• " + item.strip()
                    formatted_list_str += "\n"
                    sent = sent.replace(list_str, formatted_list_str)
                    sent = sent.strip()
                    logger.info("---Rcs html ul list string formatted---",
                                extra=log_param)
        if "<ol>" in sent:
            for idx in range(sent.count("<ol>")):
                ol_position = sent.find("<ol>", ol_end_position)
                ol_end_position = sent.find("</ol>", ol_position)
                list_str = sent[ol_position:ol_end_position]
                logger.info("RCS HTML OL LIST STRING %s : %s", str(
                    idx + 1), str(list_str), extra=log_param)
                items = list_str.split("</li>")
                if len(items) > 1:
                    formatted_list_str = ""
                    for index, item in enumerate(items[:-1]):
                        if item.strip() != "":
                            if index == 0:
                                formatted_list_str += str(index + 1) + ". " + item.strip()
                            elif index < len(items) - 1:
                                formatted_list_str += "\n" + str(index + 1) + ". " + item.strip()
                    formatted_list_str += "\n"
                    sent = sent.replace(list_str, formatted_list_str)
                    sent = sent.strip()
                    logger.info("---Rcs html ol list string formatted---",
                                extra=log_param)
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed rcs html list formatter: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return sent


def html_ol_rtl_formatter_for_rcs(message):
    try:
        ol_end_position = 0
        for iterator in range(message.count('<ol style=";text-align:right;direction:rtl">')):
            ol_position = message.find(
                '<ol style=";text-align:right;direction:rtl">', ol_end_position)
            ol_end_position = message.find("</ol>", ol_position)
            list_str = message[ol_position:ol_end_position + 5]
            list_str1 = list_str.replace("<li>", "").replace(
                '<ol style=";text-align:right;direction:rtl">', "").replace("</ol>", "")
            items = list_str1.split("</li>")
            formatted_list_str = ""
            for index, item in enumerate(items[:-1]):
                if item.strip() != "":
                    if index == 0:
                        formatted_list_str += str(index + 1) + ". " + item.strip()
                    elif index < len(items) - 1:
                        formatted_list_str += "\n" + \
                            str(index + 1) + ". " + item.strip()
            formatted_list_str += "\n"
            message = message.replace(
                list_str, formatted_list_str)
            message = message.strip()
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed html ol rtl formatter for rcs: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return message


def html_ul_rtl_formatter_for_rcs(message):
    try:
        ul_end_position = 0
        for iterator in range(message.count('<ul style=";text-align:right;direction:rtl">')):
            ul_position = message.find(
                '<ul style=";text-align:right;direction:rtl">', ul_end_position)
            ul_end_position = message.find("</ul>", ul_position)
            list_str = message[ul_position:ul_end_position + 5]
            list_str1 = list_str.replace('<ul style=";text-align:right;direction:rtl">', "").replace(
                "</ul>", "").replace("<li>", "")
            items = list_str1.split("</li>")
            formatted_list_str = ""
            for index, item in enumerate(items):
                if item.strip() != "":
                    if index == 0:
                        formatted_list_str += "• " + item.strip()
                    elif index < len(items) - 1:
                        formatted_list_str += "\n" + "• " + item.strip()
            formatted_list_str += "\n"
            message = message.replace(
                list_str, formatted_list_str)
            message = message.strip()

    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed html ul rtl formatter for rcs %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    
    return message
