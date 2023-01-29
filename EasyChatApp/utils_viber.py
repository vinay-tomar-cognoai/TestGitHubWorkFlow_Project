from EasyChatApp.utils_validation import EasyChatInputValidation, EasyChatFileValidation
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import (
    TextMessage,
    FileMessage,
    KeyboardMessage,
    URLMessage,
    PictureMessage
)
import logging
import sys
import json
import requests
import os
from django.conf import settings
from django.shortcuts import HttpResponse
from EasyChatApp.utils_bot import get_translated_text
from EasyChatApp.models import Bot, Profile, EasyChatTranslationCache, Data, Channel, BotChannel, Intent
from EasyChatApp.utils_execute_query import save_bot_switch_data_variable_if_availabe, save_data
from EasyChatApp.utils import get_dot_replaced_file_name
from rest_framework.response import Response
import base64
import time
from bs4 import BeautifulSoup
import magic
import mimetypes
import re

file_validation_obj = EasyChatFileValidation()
logger = logging.getLogger(__name__)
log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'None', 'bot_id': 'None'}


def viber_api_configuration(viber_outh_token, bot_name, viber_sender_avatar):
    logger.info('Into viber_api_configuration process', extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    try:
        if viber_sender_avatar is not None:
            viber_sender_avatar = settings.EASYCHAT_HOST_URL + viber_sender_avatar
        else:
            viber_sender_avatar = 'http://viber.com/avatar.jpg'

        bot_configuration = BotConfiguration(
            name=bot_name, avatar=viber_sender_avatar, auth_token=viber_outh_token)

        viber_configuration = Api(bot_configuration)
        logger.info('Successfully completed viber_api_configuration', extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return viber_configuration
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("viber_api_configuration ! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return None


def viber_web_hook_connector(viber_webhook_url, viber_outh_token, bot_name):
    logger.info('Started Connecting to Viber Webhook', extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    try:
        viber_api_connector = viber_api_configuration(
            viber_outh_token, bot_name, None)
        viber_api_connector.set_webhook(viber_webhook_url)
        logger.info('Successfully connected to Viber Webhook', extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ViberWebhook ! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        raise Exception(str("Viber Configuration issue"))


def get_translated_text_for_viber(bot_id, sender_id, message):
    translated_text = message
    right_to_left = "left"
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        profile_obj = Profile.objects.filter(
            user_id=str(sender_id), bot=bot_obj).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        if selected_language in ['ar', 'he', 'ku', 'ur', 'fa']:
            right_to_left = "right"
        translated_text = get_translated_text(
            message, selected_language, EasyChatTranslationCache)
        return translated_text, right_to_left
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_translated_text_for_viber: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Viber', 'bot_id': 'None'})
    return translated_text, right_to_left


def html_ul_formatter_for_viber(message):
    ul_end_position = 0
    for iterator in range(message.count("<ul>")):
        ul_position = message.find("<ul>", ul_end_position)
        ul_end_position = message.find("</ul>", ul_position)
        list_str = message[ul_position:ul_end_position]
        logger.info("HTML UL LIST STRING %s : %s", str(
            iterator + 1), str(list_str), extra=log_param)
        items = list_str.split("</li>")
        formatted_list_str = ""
        for index, item in enumerate(items):
            if item.strip() != "":
                if index == 0:
                    formatted_list_str += "• " + item.strip()
                elif index < len(items) - 1:
                    formatted_list_str += "\n• " + item.strip()
        formatted_list_str += "\n"
        message = message.replace(list_str, formatted_list_str)
        message = message.strip()
        logger.info("---Html ul list string formatted---",
                    extra=log_param)
    return message


def html_ol_formatter_for_viber(message):
    ol_end_position = 0
    for iterator in range(message.count("<ol>")):
        ol_position = message.find("<ol>", ol_end_position)
        ol_end_position = message.find("</ol>", ol_position)
        list_str = message[ol_position:ol_end_position]
        logger.info("HTML OL LIST STRING %s : %s", str(
            iterator + 1), str(list_str), extra=log_param)
        items = list_str.split("</li>")
        formatted_list_str = ""
        for index, item in enumerate(items[:-1]):
            if item.strip() != "":
                if index == 0:
                    formatted_list_str += str(index + 1) + ". " + item.strip()
                elif index < len(items) - 1:
                    formatted_list_str += "\n" + str(index + 1) + ". " + item.strip()
        formatted_list_str += "\n"
        message = message.replace(list_str, formatted_list_str)
        message = message.strip()
        logger.info("---Html ol list string formatted---",
                    extra=log_param)
    return message


def html_ol_rtl_formatter_for_viber(message):
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
    return message


def html_ul_rtl_formatter_for_viber(message):
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
    return message


def html_tags_formatter_for_viber(message):
    try:
        message = message.replace(' ', ' ')
        message = message.replace('&nbsp;', ' ')
        message = message.replace('<br/>', '')
        message = message.replace('<br>', '')
        message = message.replace('<u>', '')
        message = message.replace('</u>', '')
        message = message.replace("<i>", "<em>")
        message = message.replace("</i>", "</em>")
        message = message.replace("<b>", "<strong>")
        message = message.replace("</b>", "</strong>")

        if "<ul>" in message:
            message = html_ul_formatter_for_viber(message)

        if "<ol>" in message:
            message = html_ol_formatter_for_viber(message)

        if '<ol style=";text-align:right;direction:rtl">' in message:
            message = html_ol_rtl_formatter_for_viber(message)

        if '<ul style=";text-align:right;direction:rtl">' in message:
            message = html_ul_rtl_formatter_for_viber(message)

        tags = {
            "<p>": "", "</p>": "\n",
            "<strong></strong>": "",
            "</strong><strong>": "",
            '<p style=";text-align:right;direction:rtl">': "",
            "<span>": "", "</span>": "",
            '<li style=";text-align:right;direction:rtl">': "",
            '<em><br></em>': '<br>',
            '<strong><br></strong>': '<br>',
            '<em><em>': '<em>', '</em></em>': '</em>',
            '<strong><strong>': '<strong>', '</strong></strong>': '</strong>',
            "<em></em>": "",
            "</em><em>": "",
            "<b>": "*", "</b>": "*",
            "<strong>": "*", "</strong>": "*",
            "<i>": "_", "</i>": "_",
            "<em>": "_", "</em>": "_",
        }
        message = BeautifulSoup(message, "html.parser")
        child_soup = message.find_all('p')
        for tag in child_soup:
            if len(tag.text) == 0 and tag.find_all("span"):
                tag.decompose()
        message = str(message)
        message_list = message.split("</em>")
        if len(message_list) > 1:
            for index, msg in enumerate(message_list):
                if len(msg) - len(msg.rstrip()) > 0:
                    message_list[index] = msg.rstrip() + "</em>" + " " * (len(msg) - len(msg.rstrip()))
                elif index < len(message_list) - 1: 
                    message_list[index] = msg + "</em>"
            message = "".join(message_list)
    
        message_list = message.split("</strong>")
        if len(message_list) > 1:
            for index, msg in enumerate(message_list):
                if len(msg) - len(msg.rstrip()) > 0:
                    message_list[index] = msg.rstrip() + "</strong>" + " " * (len(msg) - len(msg.rstrip()))
                elif index < len(message_list) - 1: 
                    message_list[index] = msg + "</strong>"
            message = "".join(message_list)
    
        message_list = message.split("<em>")
        if len(message_list) > 1:
            for index, msg in enumerate(message_list):
                if len(msg) - len(msg.lstrip()) > 0:
                    message_list[index] = " " * (len(msg) - len(msg.lstrip())) + "<em>" + msg.lstrip()
                elif index > 0: 
                    message_list[index] = "<em>" + msg
            message = "".join(message_list)
    
        message_list = message.split("<strong>")

        if len(message_list) > 1:
            for index, msg in enumerate(message_list):
                if len(msg) - len(msg.lstrip()) > 0:
                    message_list[index] = " " * (len(msg) - len(msg.lstrip())) + "<strong>" + msg.lstrip()
                elif index > 0: 
                    message_list[index] = "<strong>" + msg
            message = "".join(message_list)
        
        for tag in tags:
            message = message.replace(tag, tags[tag])
        message = message.replace("**", "")
        message = message.replace("__", "")
        if "</a>" in message:
            message = message.replace("mailto:", "").replace("tel:", "")
            soup = BeautifulSoup(message, "html.parser")
            for link in soup.findAll('a'):
                href = link.get('href')
                link_name = link.string
                link_element = message[message.find(
                    "<a"):message.find("</a>")] + "</a>"
                if link_name.replace("http://", "").replace("https://", "").replace("*", "").replace("_", "").strip() == href.replace("http://", "").replace("https://", "").strip():
                    message = message.replace(link_element, link_name)
                else:
                    if "*" in link_name and "_" in link_name:
                        message = message.replace(link_element, ' ' + link_name + " *_(" + href + ")_* ")
                        
                    elif "*" in link_name:
                        message = message.replace(link_element, ' ' + link_name + " *(" + href + ")* ")
                    elif "_" in link_name:
                        message = message.replace(link_element, ' ' + link_name + " _(" + href + ")_ ")
                    else:
                        message = message.replace(link_element, link_name + " (" + href + ")")
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed to format html string format of viber: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return message


def process_string_for_viber(messages):
    treated_messages = []
    logger.info('Started process_string_for_viber', extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    try:
        validation_obj = EasyChatInputValidation()
        messages = validation_obj.clean_html(messages)
        messages = html_tags_formatter_for_viber(messages)
        messages = unicode_formatter(messages)
        messages = validation_obj.remo_html_from_string(messages)
        messages = messages.split("$$$")
        for message in messages:
            treated_messages.append(message)
            logger.info('Ending process_string_for_viber', extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("process_string_for_viber: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Viber', 'bot_id': 'None'})
    return treated_messages


def save_file_from_remote_server_to_local(attachment, file_path, viber_api_token, max_file_size_mb=5.0):
    is_saved = False
    try:
        start_time = time.time()
        headers = {
            'Content-Type': 'application/json',
            "X-Viber-Auth-Token": viber_api_token,
        }
        response = requests.get(
            url=attachment['media'], headers=headers, timeout=20)
        file_to_save = open(file_path, "wb")
        file_to_save.write(response.content)
        file_to_save.close()
        end_time = time.time()
        response_time = end_time - start_time
        logger.info("save_file_from_remote_server_to_local: Total response time: %s secs", str(
            response_time), extra=log_param)
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        is_saved = True
        if file_size > max_file_size_mb:
            os.remove(file_path)
            logger.info("save_file_from_remote_server_to_local: File Size Exceeded, Max Allowed: %s", str(
                max_file_size_mb), extra=log_param)
            is_saved = False
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_file_from_remote_server_to_local: %s at %s", str(
            E), str(exc_tb.tb_lineno), extra=log_param)
    return is_saved, response.content


def check_file_requirement_attachment_type(file_extension, user_id, bot_obj):
    is_required_extension = False
    try:
        user = Profile.objects.get(user_id=str(user_id), bot=bot_obj)
        data_obj = Data.objects.filter(
            user=user, variable="viber_file_type_to_save").first()
        if data_obj:
            try:
                data_value = json.loads(str(data_obj.value))
            except Exception:
                data_value = json.loads(str(data_obj.get_value()))
            logger.info(str(data_value), extra=log_param)
            accepted_extension = []
            if 'video' in data_value:
                accepted_extension = ['mp4']
            elif 'image' in data_value:
                accepted_extension = ['png', 'jpeg', 'jpg']
            elif 'word' in data_value:
                accepted_extension = ['doc', 'docx', 'pdf', 'xls', 'ppt']
            elif 'compressed' in data_value:
                accepted_extension = ['zip']
            is_required_extension = file_extension in accepted_extension
            if is_required_extension:
                data_obj.delete()
        else:
            is_required_extension = True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_file_requirement_attachment_type: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra=log_param)
    return is_required_extension


def save_and_get_viber_file_src(sender_id, bot_obj, attachment, viber_api_token):
    attachment_path = None
    is_saved = False
    try:
        logger.info('Started saving viber attachments', extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        file_name = attachment['file_name']
        file_name = file_name.replace(" ", "-")
        file_name = get_dot_replaced_file_name(file_name)
        file_directory = settings.MEDIA_ROOT + 'ViberMedia'
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)

        file_path = file_directory + '/' + file_name
        file_path_rel = "files/ViberMedia/" + file_name
        is_saved, viber_media = save_file_from_remote_server_to_local(
            attachment, file_path, viber_api_token)
        attachment_path = '/' + file_path_rel

        logger.info("is_viber_file_attachment: Filename %s",
                    file_name, extra=log_param)
        logger.info("is_viber_file_attachment: Filepath %s",
                    attachment_path, extra=log_param)

        file_ext = file_validation_obj.get_file_extension_from_content(
            viber_media)
        file_ext = file_name.split(".")[-1]
        allowed_file_extensions = ["jpg", "png", "jpeg",
                                   "doc", "docx", "ppt", "xls", "pdf", "mp4", "zip"]

        file_validator_obj = EasyChatFileValidation()
        is_malicious_file_name = file_validator_obj.check_malicious_file_from_filename(
            filename=file_name)
        encoded_viber_media = base64.b64encode(viber_media)
        is_malicious_file_from_content = file_validator_obj.check_malicious_file_from_content(
            encoded_viber_media)
        if file_ext.lower() not in allowed_file_extensions or not check_file_requirement_attachment_type(file_ext, sender_id, bot_obj) or is_malicious_file_name or is_malicious_file_from_content:
            is_saved = False

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_and_get_viber_file_src %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Viber', 'bot_id': 'None'})

    return attachment_path, is_saved


def send_recomendations_to_viber(viber_connector, sender_id, recommendations):
    logger.info('Started sending recommendations to viber', extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    try:
        recommendation = []
        recommendation_value = []
        for recommend in recommendations:
            if isinstance(recommend, dict):
                if 'name' in recommend:
                    if '$$$' in recommend['name']:
                        recommend_split = recommend['name'].split('$$$')
                        recommend['name'] = ' '.join(recommend_split)
                    recommendation.append(recommend['name'])
                    recommendation_value.append(recommend['name'])
                elif 'display' in recommend:
                    if '$$$' in recommend['display']:
                        recommend_split = recommend['display'].split('$$$')
                        recommend['display'] = ' '.join(recommend_split)
                        recommendation.append(recommend['display'])
                        if recommend_split[0] in ['😍', '😀', '😕', '😓', '😡']:
                            recommendation_value.append(recommend_split[0])
                        else:
                            recommendation.append(recommend['value'])
                    else:
                        recommendation.append(recommend['display'])
                        recommendation_value.append(recommend['value'])
            else:
                if '$$$' in recommend:
                    recommend_split = recommend.split('$$$')
                    recommend = ' '.join(recommend_split)
                recommendation.append(recommend)
                recommendation_value.append(recommend)

        button_in_viber = []
        for recommended_iter in range(len(recommendation)):
            button_in_viber.append({
                "Columns": 3,
                "Rows": 1,
                "BgColor": "#2db9b9",
                "BgLoop": False,
                "ActionBody": recommendation_value[recommended_iter],
                "Text": recommendation[recommended_iter],
                "TextVAlign": "middle",
                "TextHAlign": "center",
                "TextOpacity": 60,
                "TextSize": "regular",
            })
        KEYBOARD_OPTIONS = {
            "Type": "keyboard",
            "Buttons": button_in_viber
        }
        viber_connector.send_messages(sender_id, [KeyboardMessage(
            tracking_data='tracking_data', keyboard=KEYBOARD_OPTIONS)])
        logger.info('Recommendations sent to viber', extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_recomendations_to_viber %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Viber', 'bot_id': 'None'})


def send_text_to_viber(viber_connector, sender_id, bot_obj, message):
    logger.info('Started sending message to viber', extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': bot_obj.pk})
    try:
        messages = process_string_for_viber(message)
        for message in messages:
            viber_connector.send_messages(
                sender_id, [TextMessage(text=str(message))])
        logger.info('Message sent to viber', extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': bot_obj.pk})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_text_to_viber %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Viber', 'bot_id': bot_obj.pk})


def send_image_response_to_viber(viber_connector, sender_id, bot_obj, images):
    logger.info('Started sending images to viber', extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': bot_obj.pk})
    try:
        for image in images:
            if 'http' not in image:
                image = settings.EASYCHAT_HOST_URL + image
            viber_connector.send_messages(
                sender_id, [PictureMessage(text="", media=image)])
        logger.info('Successfully sent images to viber', extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': bot_obj.pk})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_and_get_viber_file_src %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Viber', 'bot_id': bot_obj.pk})


def send_cards_response_to_viber(sender_id, viber_outh_token, bot_obj, cards, viber_sender_avatar, is_pdf_search_results):
    logger.info('Started sending Cards to viber', extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': bot_obj.pk})
    try:
        if viber_sender_avatar is not None:
            viber_sender_avatar = settings.EASYCHAT_HOST_URL + viber_sender_avatar
        else:
            viber_sender_avatar = 'http://viber.com/avatar.jpg'
        if len(cards) > 6:
            cards = cards[:6]
        card_items = []
        if is_pdf_search_results:
            PDFIMAGE = "/static/EasyChatApp/img/PDF_icon.jpeg"
            click_here, right_to_left = get_translated_text_for_viber(
                bot_obj.pk, sender_id, "Click here")
            for_more_info, right_to_left = get_translated_text_for_viber(
                bot_obj.pk, sender_id, "For more information ")
            page_no, right_to_left = get_translated_text_for_viber(
                bot_obj.pk, sender_id, "Number of pages")
            for card in cards:

                card_items.append({
                    "Columns": 6,
                    "Rows": 2,
                    "ActionType": "none",
                    "Image": settings.EASYCHAT_HOST_URL + PDFIMAGE
                })
                card_items.append({
                    "Columns": 6,
                    "Rows": 1,
                    "ActionType": "none",
                    "Text": "<font color=#323232><b>" + card['title'] + "</b></font>" + "<br><font color=#6fc133> " + page_no + " : " + str(card['page_number']) + "</font>",
                    "TextSize": "medium",
                    "TextVAlign": "middle",
                    "TextHAlign": right_to_left
                })
                card_items.append({
                    "Columns": 6,
                    "Rows": 3,
                    "ActionType": "none",
                    "Text": "<font color=#808080>" + card['content'] + "</font>",
                    "TextSize": "small",
                    "TextVAlign": "middle",
                    "TextHAlign": right_to_left
                })
                card_items.append({
                    "Columns": 6,
                    "Rows": 1,
                    "ActionType": "open-url",
                    "ActionBody": card['link'],
                    "Text": "<font color=#323232>" + for_more_info + " </font><font color=#8367db> " + click_here + "</font>",
                    "TextSize": "small",
                    "TextVAlign": "middle",
                    "TextHAlign": right_to_left
                })
        else:
            DEFAULTIMAGE = "/static/EasyChatApp/img/picture_default.jpg"
            know_more, right_to_left = get_translated_text_for_viber(
                bot_obj.pk, sender_id, "KNOW MORE")
            for card in cards:
                if 'img_url' in card:
                    card_items.append({
                        "Columns": 6,
                        "Rows": 4,
                        "ActionType": "open-url",
                        "ActionBody": card['link'],
                        "Image": card['img_url']
                    })
                else:
                    card_items.append({
                        "Columns": 6,
                        "Rows": 4,
                        "ActionType": "open-url",
                        "ActionBody": card['link'],
                        "Image": settings.EASYCHAT_HOST_URL + DEFAULTIMAGE
                    })
                card_items.append({
                    "Columns": 6,
                    "Rows": 2,
                    "Text": "<font color=#323232><b>" + card['title'] + "</b></font>" + "<br><font color=#6fc133>" + card['content'] + "</font>",
                    "ActionType": "open-url",
                    "ActionBody": card['link'],
                    "TextSize": "medium",
                    "TextVAlign": "middle",
                    "TextHAlign": "middle"
                })
                card_items.append({
                    "Columns": 6,
                    "Rows": 1,
                    "ActionType": "open-url",
                    "ActionBody": card['link'],
                    "Text": "<font color=#8367db>" + know_more + "</font>",
                    "TextSize": "small",
                    "TextVAlign": "middle",
                    "TextHAlign": "middle"
                })

        headers = {
            "Content-Type": "application/json",
            "X-Viber-Auth-Token": viber_outh_token,
        }
        data = json.dumps({
            "receiver": sender_id,
            "type": "rich_media",
            "min_api_version": 7,
            "sender": {
                "name": bot_obj.name,
                "avatar": viber_sender_avatar
            },
            "rich_media": {
                "Type": "rich_media",
                "ButtonsGroupColumns": 6,
                "ButtonsGroupRows": 7,
                "BgColor": "#FFFFFF",
                "Buttons": card_items
            }
        })
        requests.post("https://chatapi.viber.com/pa/send_message",
                      headers=headers, data=data)
        logger.info('Successfully sent Cards to viber', extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': bot_obj.pk})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_cards_response_to_viber %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Viber', 'bot_id': 'None'})


def send_video_response_to_viber(viber_connector, sender_id, bot_obj, videos):
    try:
        logger.info('Starting to send videos to viber', extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': bot_obj.pk})

        for video in videos:
            viber_connector.send_messages(sender_id, [URLMessage(media=video)])

        logger.info('Successfully sent video to viber', extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_video_response_to_viber %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Viber', 'bot_id': bot_obj.pk})


def is_change_language_response_required(sender, bot_obj):
    try:
        channel = Channel.objects.filter(name='Viber')[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        profile_obj = Profile.objects.filter(
            user_id=str(sender), bot=bot_obj).first()

        if not bot_channel_obj.is_enable_choose_language_flow_enabled_for_welcome_response:
            default_lang = languages_supported.filter(lang="en").first()
            profile_obj.selected_language = default_lang
            profile_obj.save()
            return False

        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("change_language_response_required: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return False


def send_welcome_message_to_viber(viber_connector, sender_id, bot_obj, welcome_message, initial_intent, initial_messages):
    logger.info('Sending Welcome Message', extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    try:
        send_text_to_viber(viber_connector, sender_id,
                           bot_obj, welcome_message)
        if len(initial_intent) > 0:
            send_text_to_viber(
                viber_connector, sender_id, bot_obj, initial_intent)
        if "images" in initial_messages and len(initial_messages["images"]) > 0:
            send_image_response_to_viber(
                viber_connector, sender_id, bot_obj, initial_messages['images'])
        if "videos" in initial_messages and len(initial_messages["videos"]) > 0:
            send_video_response_to_viber(
                viber_connector, sender_id, bot_obj, initial_messages['videos'])
        choices = []
        if is_change_language_response_required(sender_id, bot_obj):
            choices.append('Change Language')
        if "items" in initial_messages and len(initial_messages["items"]) > 0:

            for choice in initial_messages["items"]:
                intent_obj = Intent.objects.filter(pk=int(choice)).first()
                if intent_obj:
                    choices.append(intent_obj.name)
        if len(choices) > 0:
            send_recomendations_to_viber(viber_connector, sender_id, choices)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_welcome_message_to_viber %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Viber', 'bot_id': 'None'})


def processing_text_and_attachments(viber_connector, extract_message, sender_id, viber_api_token, bot_obj, viber_sender_avatar):
    try:
        message = ''
        attachments = []
        if extract_message['type'] == 'text':
            message = extract_message['text']
            validation_obj = EasyChatInputValidation()
            valid_message = validation_obj.is_valid_url(message)
            message = '' if valid_message else message
        elif extract_message['type'] == 'picture':
            attachments.append(extract_message)

        elif extract_message['type'] == 'video':
            attachments.append(extract_message)

        elif extract_message['type'] == 'file':
            attachments.append(extract_message)

        elif extract_message['type'] == 'sticker':
            attachments.append(extract_message)

        channel_params = {}
        channel_name = "Viber"
        if len(attachments) > 0:
            attachment = attachments[0]

            file_src, is_saved = save_and_get_viber_file_src(
                sender_id, bot_obj, attachment, viber_api_token)

            if not is_saved:
                warning_text, rtl = get_translated_text_for_viber(
                    bot_obj.pk, sender_id, ": warning : <br> <i>Failed to send file attachment!</i> <br> Your file is either invalid or greater than 5.0 MB.")
                send_text_to_viber(
                    viber_connector, sender_id, bot_obj, html_tags_formatter_for_viber(warning_text))
                return HttpResponse("OK")

            if file_src != "":
                channel_params = {
                    "attached_file_path": file_src,
                }
        else:
            if message.strip() == "":
                return HttpResponse("OK")
                # IF ATTACHMENT IS EMPTY AND MESSAGE IS ALSO EMPTY THEN RETUN

        channel_params = json.dumps(channel_params)
        response = []
        from EasyChatApp.utils_channels import process_language_change_or_get_response
        terminate, response = process_language_change_or_get_response(
            sender_id, bot_obj.pk, None, "uat", channel_name, channel_params, message, bot_obj, None, viber_api_token, sender=viber_connector)

        if terminate:
            return Response(data=response)

        if 'response' in response:
            default_order_of_response = json.loads(
                bot_obj.default_order_of_response)
            order_of_response = ['text', 'image', 'video', 'link_cards']
            if 'is_custom_order_selected' in response['response'] and response['response']['is_custom_order_selected']:
                order_of_response = response['response']['order_of_response']
            elif len(default_order_of_response) > 0:
                order_of_response = default_order_of_response
            save_bot_switch_data_variable_if_availabe(
                sender_id, bot_obj.pk, response, channel_name)

            user = Profile.objects.get(user_id=str(sender_id), bot=bot_obj)
            if 'is_attachment_required' in response['response']['text_response']['modes'] and response['response']['text_response']['modes']['is_attachment_required'] == 'true':
                save_data(user, json_data={"viber_file_type_to_save": response['response']['text_response'][
                          'modes_param']['choosen_file_type']}, src="en", channel="Viber", bot_id=bot_obj.pk, is_cache=True)

            recommendations = response['response']['recommendations']

            if len(response['response']['choices']) > 0:
                for recommendation in response['response']['choices']:
                    recommendations.append(recommendation)
            for order in order_of_response:

                if order == 'text' and 'text_response' in response['response'] and 'text' in response['response']['text_response']:
                    send_text_to_viber(
                        viber_connector, sender_id, bot_obj, response['response']['text_response']['text'])

                elif order == 'image' and len(response['response']['images']) > 0:
                    send_image_response_to_viber(
                        viber_connector, sender_id, bot_obj, response['response']['images'])

                elif order == 'video' and len(response['response']['videos']) > 0:
                    send_video_response_to_viber(
                        viber_connector, sender_id, bot_obj, response['response']['videos'])

                elif order == 'link_cards' and len(response['response']['cards']) > 0:
                    send_cards_response_to_viber(
                        sender_id, viber_api_token, bot_obj, response['response']['cards'], viber_sender_avatar, False)

            if 'pdf_search_results' in response['response'] and len(response['response']['pdf_search_results']) > 0:
                send_cards_response_to_viber(
                    sender_id, viber_api_token, bot_obj, response['response']['pdf_search_results'], viber_sender_avatar, True)
                recommendations = []

            if 'google_search_results' in response['response'] and len(response['response']['google_search_results']) > 0:
                send_cards_response_to_viber(
                    sender_id, viber_api_token, bot_obj, response['response']['google_search_results'], viber_sender_avatar, False)
                recommendations = []

            if 'easy_search_results' in response['response'] and len(response['response']['easy_search_results']) > 0:
                send_cards_response_to_viber(
                    sender_id, viber_api_token, bot_obj, response['response']['easy_search_results'], viber_sender_avatar, False)
                recommendations = []

            if len(recommendations) > 0:
                send_recomendations_to_viber(
                    viber_connector, sender_id, recommendations)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("processing_text_and_attachments %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        raise(e)


def send_viber_livechat_agent_response(customer_obj, session_id, message, attached_file_src, data, sender_name, Profile, Bot, ViberDetails):

    response = {}
    response["status"] = 200
    try:
        user_obj = Profile.objects.get(livechat_session_id=session_id)

        if user_obj.livechat_connected:

            selected_bot_obj = customer_obj.bot
            sender_id = customer_obj.client_id

            viber_obj = ViberDetails.objects.filter(
                bot=selected_bot_obj).first()

            viber_api_token = viber_obj.viber_api_token

            viber_sender_avatar = None

            viber_sender_avatar_raw = json.loads(viber_obj.viber_bot_logo)

            if 'sender_logo' in viber_sender_avatar_raw and len(viber_sender_avatar_raw['sender_logo']) > 0:
                viber_sender_avatar = viber_sender_avatar_raw['sender_logo'][0]

            agent_name = selected_bot_obj.name
            if customer_obj.agent_id:
                agent_name = customer_obj.agent_id.get_agent_name()

            viber_connector = viber_api_configuration(
                viber_api_token, agent_name, viber_sender_avatar)

            if attached_file_src != "":

                if "channel_file_url" in data:

                    attached_file_src = data["channel_file_url"]

                    try:
                        attached_file_src = settings.EASYCHAT_HOST_URL + attached_file_src

                        file_name = attached_file_src.split("/")[-1]

                        file_validation = EasyChatFileValidation()

                        if file_validation.is_image(file_name):
                            send_image_response_to_viber(
                                viber_connector, sender_id, selected_bot_obj, [attached_file_src])

                        elif file_validation.is_video(file_name):
                            send_video_response_to_viber(
                                viber_connector, sender_id, selected_bot_obj, [attached_file_src])

                        else:
                            send_file_response_to_viber(
                                viber_connector, sender_id, selected_bot_obj, [attached_file_src])

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("send_viber_livechat_agent_response: %s at %s",
                                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            if message != "":
                send_text_to_viber(viber_connector, sender_id,
                                   selected_bot_obj, message)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_viber_livechat_agent_response %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response["status"] = 500

    return response


def send_file_response_to_viber(viber_connector, sender_id, bot_obj, files):
    logger.info('Started sending files to viber', extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': bot_obj.pk})
    try:
        for file_url in files:
            if 'http' not in file_url:
                file_url = settings.EASYCHAT_HOST_URL + file_url
            viber_connector.send_messages(
                sender_id, [URLMessage(media=file_url)])
        logger.info('Successfully sent images to viber', extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': bot_obj.pk})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_file_response_to_viber %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Viber', 'bot_id': bot_obj.pk})


def unicode_formatter(message):
    try:
        unicodes = {"&nbsp;": " ", "&#39;": "\'", "&rsquo;": "\'", "&amp;": "&", "&hellip;": "...", "&quot;": "\"", "\\n": "\n",
                    "\\u2019": "'", "\\u2013": "'", "\\u2018": "'", "&ldquo": "\"", "&rdquo;": "\""}
        for code in unicodes:
            message = message.replace(code, unicodes[code])
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed unicode formatter: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return message
