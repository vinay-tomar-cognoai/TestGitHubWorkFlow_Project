from EasyChatApp.constants import *
from bs4 import BeautifulSoup
from EasyChatApp.easychat_utils_objects import EasyChatBotUser, EasyChatChannelParams
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.models import TelegramDetails, Data, Channel, BotChannel, Profile, EasyChatTranslationCache, Bot
from EasyChatApp.utils_bot import get_emojized_message, get_translated_text
from EasyChatApp.utils_execute_query import get_message_list_using_pk, set_user, save_data, check_and_send_broken_bot_mail, generate_flow_dropoff_object, get_bot_obj_from_data_models, build_channel_welcome_response
from django.conf import settings

import requests
import re
import logging
import sys
import copy
import json
import time
import os
import urllib

logger = logging.getLogger(__name__)
log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'None', 'bot_id': 'None'}

"""
function: save_file_from_remote_server_to_local
input_params:
    remote_url: file path on remote server
    local_path: file path on local system where it will be saved

This function is used to save a file existing on remote url to local system
"""


def save_file_from_remote_server_to_local(remote_url, local_path):
    is_saved = False
    try:
        start_time = time.time()
        response = requests.get(url=remote_url, timeout=10)
        response_time = response.elapsed.total_seconds()
        logger.info("save_file_from_remote_server_to_local: API response time: %s secs", str(
            response_time), extra=log_param)
        raw_data = response.content
        file_to_save = open(local_path, "wb")
        file_to_save.write(raw_data)
        file_to_save.close()
        end_time = time.time()
        response_time = end_time - start_time
        logger.info("save_file_from_remote_server_to_local: Total response time: %s secs", str(
            response_time), extra=log_param)
        is_saved = True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_file_from_remove_server_to_local: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
    return is_saved


"""
function: get_telegram_file_attachment
input_params:
    attachment_packet: attachement response packet when user updload any file
    bot_id: 
    caption: caption provided by user during uploading data
    file_type: file type(image, video, doc etc.)

This function is used to get file path on local system, uploaded by user via telegram
"""


def get_telegram_file_attachment(attachment_packet, bot_id, caption, file_type, max_file_size_allowed_bytes, is_livechat):
    attachment_path = ""
    attachment_full_path = ""
    is_attachment_saved = False
    try:
        if file_type == "photo":
            file_id = attachment_packet[1]["file_id"]
        else:
            file_id = attachment_packet["file_id"]

        telegram_obj = TelegramDetails.objects.filter(bot__pk=bot_id)[0]
        telegram_url = telegram_obj.telegram_url + telegram_obj.telegram_api_token
        url = telegram_url + "/getFile?file_id=" + file_id
        response = requests.get(url)
        logger.info("Response after sendng messag is %s", str(response.text), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = json.loads(response.text)

        if is_livechat and "result" in response and "file_size" in response["result"] and (int(response["result"]["file_size"]) > max_file_size_allowed_bytes):
            logger.info("TelegramQueryAPI: File Size Exceeded, Max Allowed " + str(max_file_size_allowed_bytes),
                        extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return attachment_path, attachment_full_path, is_attachment_saved

        if "ok" in response and response["ok"] == True:
            file_path = telegram_obj.telegram_url + "file/" + \
                telegram_obj.telegram_api_token + "/" + \
                response["result"]["file_path"]
            filename = response["result"]["file_path"].split("/")[-1]
            if not os.path.exists(settings.MEDIA_ROOT + 'TelegramMedia'):
                os.makedirs(settings.MEDIA_ROOT + 'TelegramMedia')
            local_file_path = settings.MEDIA_ROOT + "TelegramMedia/" + filename
            attachment_path = "/files/TelegramMedia/" + filename
            attachment_full_path = settings.EASYCHAT_HOST_URL + "/files/TelegramMedia/" + filename
            save_file_from_remote_server_to_local(file_path, local_file_path)
            is_attachment_saved = True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_telegram_file_attachment: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
    return attachment_path, attachment_full_path, is_attachment_saved


"""
function: get_message_from_reverse_telegram_mapping
input_params:
    user_message: message send by user
    user: profile object

This function is used to reverse map, ex. 1 --> some intent, 2 --> some other intent
"""


def get_message_from_reverse_telegram_mapping(user_message, user):
    message = None
    try:
        logger.info(" === Reverse Message mapping === ", extra=log_param)
        data_obj = Data.objects.filter(
            user=user, variable="REVERSE_TELEGRAM_MESSAGE_DICT")[0]
        data_dict = json.loads(str(data_obj.get_value()))
        user_message = str(user_message).lower().strip()
        if user_message in data_dict:
            message = data_dict[user_message]
        logger.info(str(message), extra=log_param)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_message_from_reverse_telegram_mapping: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
    return message


"""
function: html_tags_formatter
input_params:
    message: 

This function is used as html formatter
"""


def html_tags_formatter(message):
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

        if '<ol style=";text-align:right;direction:rtl">' in message:
            message = html_ol_rtl_formatter_for_telegram(message)

        if '<ul style=";text-align:right;direction:rtl">' in message:
            message = html_ul_rtl_formatter_for_telegram(message)

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
                    message = message.replace(link_element, ' ' + link_name)
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
        logger.error("Failed to format html string format of telegram: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return message


"""
function: html_list_formatter
input_params:
    message_sent: 

"""


def html_list_formatter(sent):
    try:
        logger.info("---Html list string found---", extra=log_param)
        ul_end_position = 0
        ol_end_position = 0
        if "<ul>" in sent:
            for itr in range(sent.count("<ul>")):
                ul_position = sent.find("<ul>", ul_end_position)
                ul_end_position = sent.find("</ul>", ul_position)
                list_str = sent[ul_position:ul_end_position]
                logger.info("HTML LIST STRING %s : %s", str(
                    itr + 1), str(list_str), extra=log_param)
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
                    logger.info("---Html list string formatted---",
                                extra=log_param)
        if "<ol>" in sent:
            for itr in range(sent.count("<ol>")):
                ol_position = sent.find("<ol>", ol_end_position)
                ol_end_position = sent.find("</ol>", ol_position)
                list_str = sent[ol_position:ol_end_position]
                logger.info("HTML LIST STRING %s : %s", str(
                    itr + 1), str(list_str), extra=log_param)
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
                    logger.info("---Html list string formatted---",
                                extra=log_param)
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed to format telegram html list string: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
        # print("Failed to format html list string: %s", str(E))
    return sent


"""
function: youtube_link_formatter
input_params:
    message: message may contain you tube url.

This function is used to embed you tube url.
"""


def youtube_link_formatter(message):
    if "https://www.youtube.com" in message:
        message = message.replace(
            "embed/", "").replace("www.youtube.com", "youtu.be")
    return message


"""
function: is_start_of_conversation
input_params:
    message: message sent by user

This function is used to check if user has initiated the chat first time or not. If user type start then it's tree reseted to null.
"""


def is_start_of_conversation(message):
    try:
        regex = re.compile('[,\.!?/]')
        message = regex.sub('', message)
        if message.lower() == "start":
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside is_start_of_conversation %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return False


"""
function: build_telegram_welcome_response
input_params:
    user_id: user id
    bot_id: 
    chat_id: chat id of user
    src: "en"
    channel: Telegram

This function is return welcome response for telegram channel.
"""


def build_telegram_welcome_response(user_id, bot_obj, data):
    channel = "Telegram"
    try:
        bot_obj_from_data_model = get_bot_obj_from_data_models(
            user_id, bot_obj, log_param)
        if bot_obj_from_data_model:
            bot_obj = bot_obj_from_data_model
        bot_id = bot_obj.pk

        # setting user tree None
        user = set_user(user_id, "telegram", "src", "Telegram", bot_id)
        if user.tree and user.tree.children.filter(is_deleted=False).exists():
            generate_flow_dropoff_object(user, True)
        user.tree = None
        user.save(update_fields=['tree'])

        easychat_bot_user = EasyChatBotUser()
        easychat_bot_user.user_id = user_id
        easychat_bot_user.bot_obj = bot_obj
        if user.selected_language:
            easychat_bot_user.src = user.selected_language.lang
        else:
            easychat_bot_user.src = "en"

        easychat_params = EasyChatChannelParams({}, user_id)
        easychat_params.channel_obj = Channel.objects.get(name="Telegram")

        response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_message = "[ENGINE] build_telegram_welcome_response: {} at {}".format(str(e), str(exc_tb.tb_lineno))
        logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': 'None', 'channel': str(channel), 'bot_id': str(bot_id)})
        try:
            if type(data) != dict:
                data = json.loads(data)
            meta_data = data
        except:
            meta_data = {}
        meta_data["error"] = error_message
        check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))
        response["status_code"] = 500
        response["status_message"] = str(e)

    return user, response


"""
function: set_telegram_webhook
input_params:
    webhook_url: webhook url provided by us
    telegram_url: this value remain fixed
    telegram_api_token: token provided by client

This function is used to set webhook for any bot.
"""


def set_telegram_webhook(webhook_url, telegram_url, telegram_api_token):
    try:

        url = telegram_url + telegram_api_token + "/setWebhook?url=" + webhook_url
        response = requests.get(url)
        logger.info("response after setting webhook: %s", response.text, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response = json.loads(response.text)
        if "ok" in response and response["ok"] == True:
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return False


"""
function: send_text_message_to_telegram
input_params:
    bot_id: 
    message: 
    chat_id: 

This function is used to send text message to telegram user.
"""


def send_text_message_to_telegram(bot_id, message, chat_id):
    try:
        message = urllib.parse.quote_plus(message)
        telegram_obj = TelegramDetails.objects.filter(bot__pk=bot_id)[0]
        telegram_url = telegram_obj.telegram_url + telegram_obj.telegram_api_token

        url = telegram_url + "/sendMessage?chat_id=" + \
            str(chat_id) + "&text=" + str(message) + "&parse_mode=MarkdownV2"

        response = requests.get(url)
        logger.info("Response after sendng messag is %s", str(response.text), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] send_text_message_to_telegram %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: send_media_message_to_telegram
input_params:
    bot_id: 
    file_type: 
    file_path: 
    chat_id: 
    caption

This function is used to send media message to telegram user.
"""


def send_media_message_to_telegram(bot_id, file_type, file_path, chat_id, caption=""):
    try:
        telegram_obj = TelegramDetails.objects.filter(bot__pk=bot_id)[0]
        telegram_url = telegram_obj.telegram_url + telegram_obj.telegram_api_token

        if file_type == "image":
            url = telegram_url + "/sendPhoto?chat_id=" + \
                str(chat_id) + "&photo=" + str(file_path) + \
                "&caption=" + str(caption) + "&parse_mode=MarkdownV2"
        else:
            url = telegram_url + "/sendDocument?chat_id=" + \
                str(chat_id) + "&document=" + \
                str(file_path) + "&caption=" + str(caption) + "&parse_mode=MarkdownV2"

        response = requests.get(url)
        logger.info("Response after sendng messag is %s", str(response.text), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] send_text_message_to_telegram %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_telegram_user_language
input_params:
    user

This function is used to return language selected by user
"""


def get_telegram_user_language(user):
    selected_language = "en"
    language_script_type = "ltr"
    try:
        if user and user.selected_language:
            selected_language = user.selected_language.lang
            language_script_type = user.selected_language.language_script_type
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] get_telegram_user_language %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return selected_language, language_script_type

"""
function: send_message_to_telegram_user
input_params:
    user: 
    bot_id: 
    bot_response: response after intet recognition
    chat_id: 

This function is used to return response to telegram bot user.
"""


def send_message_to_telegram_user(user, bot_id, bot_response, chat_id, data):
    try:
        message = bot_response["response"]["text_response"]["text"]
        modes = bot_response["response"]["text_response"]["modes"]
        recommendations = bot_response["response"]["recommendations"]
        images = bot_response["response"]["images"]
        videos = bot_response["response"]["videos"]
        cards = bot_response["response"]["cards"]

        reverse_telegram_dict = {}
        reverse_mapping_index = 0

        selected_language, language_script_type = get_telegram_user_language(user)

        hand_emoji_direction = ":point_right:"
        if language_script_type == "rtl":
            hand_emoji_direction = ":point_left:"

        please_type_text = get_translated_text("Please type", selected_language, EasyChatTranslationCache)
        
        #   CHOICES:
        choice_dict = {}
        choice_display_list = []
        for choice in bot_response["response"]["choices"]:
            if choice["display"] == "Helpful" or choice["display"] == "Unhelpful":
                continue
            choice_dict[choice["display"]] = choice["value"]
            choice_display_list.append(choice["display"])
        choice_str = ""
        if choice_display_list != []:
            if bot_response["response"]["is_flow_ended"]:
                choice_str += "\n\n"
            for index in range(len(choice_display_list)):
                reverse_telegram_dict[str(
                    index + 1)] = str(choice_dict[choice_display_list[index]])
                enter_text = please_type_text + " *" + str(index + 1) + "* " + hand_emoji_direction + "  " + str(choice_display_list[index]) + "\n\n"
                choice_str += enter_text
            choice_str = get_emojized_message(choice_str) + "\n\n\n"
            reverse_mapping_index = len(choice_display_list)

        for char in "[]()~`>#+-=|{}.!":
            choice_str = choice_str.replace(char, "\\" + char)
        #   RECOMMENDATIONS:
        recommendation_str = ""
        if recommendations != []:
            if bot_response["response"]["is_flow_ended"]:
                recommendation_str += "\n\n"
            if choice_str != "":
                for index in range(len(recommendations)):
                    if index % 10 == 0:
                        recommendation_str += "$$$"

                    recommendation_name = recommendations[index]
                    if isinstance(recommendations[index], dict) and "name" in recommendations[index]:
                        recommendation_name = recommendations[index]["name"]

                    reverse_telegram_dict[str(
                        reverse_mapping_index + index + 1)] = str(recommendation_name)
                    enter_text = please_type_text + " *" + str(reverse_mapping_index + index + 1) + "* " + hand_emoji_direction + "  " + str(recommendation_name) + "\n\n"
                    recommendation_str += enter_text
                
            else:
                for index in range(len(recommendations)):
                    if index % 10 == 0:
                        recommendation_str += "$$$"

                    recommendation_name = recommendations[index]
                    if isinstance(recommendations[index], dict) and "name" in recommendations[index]:
                        recommendation_name = recommendations[index]["name"]

                    reverse_telegram_dict[str(
                        index + 1)] = str(recommendation_name)
                    enter_text = please_type_text + " *" + str(index + 1) + "* " + hand_emoji_direction + "  " + str(recommendation_name) + "\n\n"
                    recommendation_str += enter_text
                
            recommendation_str = get_emojized_message(recommendation_str)
        
        validation_obj = EasyChatInputValidation()

        #   Recommendation text formatting
        for char in "[]()~`>#+-=|{}.!":
            recommendation_str = recommendation_str.replace(char, "\\" + char)

        #   TEXT FORMATTING AND EMOJIZING:
        # message = message.replace("*"," • ")
        for char in "*_":
            message = message.replace(char, "\\" + char)

        message = html_tags_formatter(message)
        message = html_list_formatter(message)
        message = validation_obj.unicode_formatter(message)
        message = get_emojized_message(message)
        message = validation_obj.remo_html_from_string(message)

        for char in "[]()~`>#+-=|{}.!":
            message = message.replace(char, "\\" + char)

        logger.info("Bot Message: %s", str(message), extra=log_param)

        #   RESPONSE MODES:
        # 1.SANDWICH CHOICES: sending choices in between to small texts in a
        # single bubble:
        if "is_sandwich_choice" in modes.keys() and modes['is_sandwich_choice'] == "true":
            choice_position = "1"  # 2nd position
            is_single_message = True
        else:
            choice_position = ""
            is_single_message = False

        #   2.STICKY CHOICES: sending choices and message in same bubble.
        message_with_choice = False
        if "message_with_choice" in modes.keys() and modes["message_with_choice"] == "true":
            message_with_choice = True

        #   3. BOT LINK CARDS: sending cards containing urls/links
        if "card_for_links" in modes.keys() and modes["card_for_links"] == "true":
            card_text = ""
            for card in cards:
                redirect_url = str(
                    card["link"]) if card["link"] is not None else ""
                title = str(card["title"] if card["title"] is not None else "")
                card_text += " " + hand_emoji_direction + " *" + title + "* \n   "
                card_text += " :link: " + redirect_url + "$$$"
            message += get_emojized_message("$$$" + card_text)
            for char in "[]()~`>#+-=|{}.!":
                message = message.replace(char, "\\" + char)
            cards = []

        #   SEND SINGLE BUBBLE TEXT:
        final_text_message = ""
        for count, small_message in enumerate(message.split("$$$"), 0):
            if str(choice_position) != "" and str(choice_position) == str(count):
                # 1. Sandwich choices text:
                if len(choice_str) > 0:
                    final_text_message += choice_str
                if len(recommendation_str) > 0:
                    final_text_message += recommendation_str
                final_text_message += small_message + "$$$"
            else:
                final_text_message += small_message + "$$$"
        if is_single_message:
            final_text_message = final_text_message.replace("$$$", "")
            if final_text_message != "":
                if "http://" in final_text_message or "https://" in final_text_message:
                    final_text_message = youtube_link_formatter(
                        final_text_message)
                    time.sleep(2)
                    send_status = send_text_message_to_telegram(
                        bot_id, final_text_message, chat_id)
                else:
                    time.sleep(2)
                    send_status = send_text_message_to_telegram(
                        bot_id, final_text_message, chat_id)
                recommendation_str = ""
                choice_str = ""
        else:
            if message_with_choice == True:
                # 2. Sticky choices text:
                final_text_message = message.replace("$$$", "\n\n")
                if len(recommendations) > 0:
                    recommendation_str = final_text_message + recommendation_str
                if len(choice_display_list) > 0:
                    choice_str = final_text_message + choice_str
            else:
                # 3. Regular single text:
                for small_message in final_text_message.split("$$$"):
                    small_message = html_list_formatter(small_message)
                    if small_message != "":
                        if "http://" in small_message or "https://" in small_message:
                            small_message = youtube_link_formatter(
                                small_message)
                            time.sleep(1)
                            send_status = send_text_message_to_telegram(
                                bot_id, small_message, chat_id)
                        else:
                            time.sleep(1)
                            send_status = send_text_message_to_telegram(
                                bot_id, small_message, chat_id)

        # SENDING CARDS, IMAGES, VIDEOS:
        logger.info("Cards: %s", str(cards), extra=log_param)
        logger.info("Images: %s", str(images), extra=log_param)
        logger.info("Videos: %s", str(videos), extra=log_param)

        if len(cards) > 0:
            # Cards with documnet links:  Use 'card_with_document:true' in
            # modes
            if "card_with_document" in modes.keys() and modes["card_with_document"] == "true":
                logger.info("Inside Cards with documents", extra=log_param)
                for card in cards:
                    doc_caption = str(card["title"])
                    doc_url = str(card["link"])
                    for char in "[]()~`>#+-=|{}.!":
                        doc_caption = doc_caption.replace(char, "\\" + char)
                    logger.info("DOCUMENT NAME: %s", str(
                        doc_caption), extra=log_param)
                    logger.info("DOCUMENT URL: %s", str(
                        doc_url), extra=log_param)
                    try:
                        send_status = send_media_message_to_telegram(
                            bot_id, "document", str(doc_url), chat_id, caption=str(doc_caption))
                        logger.info("Is Card sent: %s", str(
                            send_status), extra=log_param)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Cannot send card with document: %s at %s", str(
                            e), str(exc_tb.tb_lineno), extra=log_param)
            else:
                for card in cards:
                    logger.info("Inside Regular Card", extra=log_param)
                    title = str(card["title"])
                    content = str("\n" + card["content"] + "\n")
                    image_url = str(card["img_url"])
                    redirect_url = youtube_link_formatter(str(card["link"]))
                    caption = "*" + title + "* " + content + " " + redirect_url
                    for char in "[]()~`>#+-=|{}.!":
                        caption = caption.replace(char, "\\" + char)
                    if image_url != "":
                        logger.info("Card Image available", extra=log_param)
                        send_status = send_media_message_to_telegram(
                            bot_id, 'image', str(image_url), chat_id, caption=caption)
                        logger.info("Is Card with image sent: %s",
                                    str(send_status), extra=log_param)
                    else:
                        send_status = send_text_message_to_telegram(
                            bot_id, get_emojized_message(caption), chat_id)
                        logger.info("Is Card with link sent: %s",
                                    str(send_status), extra=log_param)

        if len(videos) > 0:
            for iterator in range(len(videos)):
                logger.info("== Inside Videos ==", extra=log_param)
                if 'video_link' in str(videos[iterator]):
                    video_url = youtube_link_formatter(
                        str(videos[iterator]['video_link']))  # youtube links
                    
                    for char in "[]()~`>#+-=|{}.!_":
                        video_url = video_url.replace(char, "\\" + char)
                    
                    send_status = send_text_message_to_telegram(
                        bot_id, video_url, chat_id)
                    logger.info("Is Video sent: %s", str(
                        send_status), extra=log_param)
                else:
                    video_url = youtube_link_formatter(
                        str(videos[iterator]))  # youtube links
                    
                    for char in "[]()~`>#+-=|{}.!_":
                        video_url = video_url.replace(char, "\\" + char)
                    
                    send_status = send_text_message_to_telegram(
                        bot_id, video_url, chat_id)
                    logger.info("Is Video sent: %s", str(
                        send_status), extra=log_param)
        if len(images) > 0:
            logger.info("== Inside Images ==", extra=log_param)
            for iterator in range(len(images)):
                if 'content' in str(images[iterator]):
                    logger.info("== Image with caption ==", extra=log_param)
                    send_status = send_media_message_to_telegram(bot_id, 'image', str(
                        images[iterator]["img_url"]), chat_id, caption=str(images[iterator]['content']))
                    logger.info("Is Image sent: %s", str(
                        send_status), extra=log_param)
                else:
                    logger.info("== Image without caption ==", extra=log_param)
                    send_status = send_media_message_to_telegram(
                        bot_id, 'image', str(images[iterator]), chat_id, caption="")
                    logger.info("Is Image sent: %s", str(
                        send_status), extra=log_param)

        #   SENDING CHOICES AND RECOMMENDATIONS BOTH:
        if len(choice_str) > 0 and len(recommendation_str) > 0:
            mixed_choice = choice_str + "" + recommendation_str
            send_status = send_text_message_to_telegram(
                bot_id, mixed_choice.replace("\n\n\n", "").replace("$$$", ""), chat_id)
            logger.info("Is Mixed Choices sent: %s",
                        str(send_status), extra=log_param)
            choice_str = ""
            recommendation_str = ""

        #       SENDING CHOICES:
        if len(choice_str) > 0:
            time.sleep(1.5)
            send_status = send_text_message_to_telegram(
                bot_id, choice_str, chat_id)
            logger.info("Is choices sent: %s", str(
                send_status), extra=log_param)

        #   SENDING RECOMMENDATIONS:
        if len(recommendation_str) > 0:
            if "$$$" in recommendation_str:
                for bubble in recommendation_str.split("$$$"):
                    time.sleep(1)
                    send_status = send_text_message_to_telegram(
                        bot_id, bubble, chat_id)
                    logger.info("Is recommendations sent: %s",
                                str(send_status), extra=log_param)
            else:
                time.sleep(1)
                send_status = send_text_message_to_telegram(
                    bot_id, recommendation_str, chat_id)
                logger.info("Is recommendations sent: %s",
                            str(send_status), extra=log_param)

        logger.info("REVERSE_TELEGRAM_MESSAGE_DICT: %s", str(
            reverse_telegram_dict), extra=log_param)
        save_data(user, json_data={"REVERSE_TELEGRAM_MESSAGE_DICT": reverse_telegram_dict},
                  src="None", channel="Telegram", bot_id=bot_id, is_cache=True)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_message = "[ENGINE] {} at {}".format(str(e), str(exc_tb.tb_lineno))
        logger.error(error_message, extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        try:
            if type(data) != dict:
                data = json.loads(data)
            meta_data = data
        except:
            meta_data = {}
        meta_data["error"] = error_message
        check_and_send_broken_bot_mail(bot_id, "Telegram", "", json.dumps(meta_data))


def html_ol_rtl_formatter_for_telegram(message):
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
        logger.error("Failed html ol rtl formatter for telegram: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return message


def html_ul_rtl_formatter_for_telegram(message):
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
        logger.error("Failed html ul rtl formatter for telegram: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return message


def build_file_not_saved_bot_response(allowed_file_size):
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        invalid_attachment_notification = get_emojized_message(
            ":warning: Failed to send file attachment! \nYour file is either invalid or greater than " + str(allowed_file_size) + " MB.")
        response["response"]["text_response"]["text"] = invalid_attachment_notification
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed build_file_not_saved_bot_resonse for telegram: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return response
