import sys
import json
import requests
import logging
import re
from django.shortcuts import HttpResponse
from django.conf import settings
logger = logging.getLogger(__name__)
from bs4 import BeautifulSoup

from EasyChatApp.utils_bot import get_translated_text

log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'None', 'bot_id': 'None'}


def remove_tags(text):
    text = text.replace("<br>", "")
    text = text.replace("<b>", "")
    text = text.replace("</b>", "")
    text = text.replace("<i>", "")
    text = text.replace("</i>", "")
    text = text.replace("  ", " ")
    return text


def verify_webhook(request, Bot, Channel, BotChannel):
    try:
        logger.info("Request GET " +
                    str(request.GET), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        bot_id = request.GET.get('id')
        bot_obj = Bot.objects.get(pk=bot_id)
        channel_obj = Channel.objects.get(name="Facebook")
        bot_console_obj = BotChannel.objects.get(
            bot=bot_obj, channel=channel_obj)
        logger.info("bot_console_obj: " + str(bot_console_obj), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        verify_token = bot_console_obj.verification_code
        if request.GET['hub.verify_token'] == verify_token:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse("Invalid Token")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "Verify API : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return HttpResponse("Invalid Token")


def send_images(recipient_id, image_urls, page_access_token):
    try:
        for image_url in image_urls:
            access_token = page_access_token
            params = {
                "access_token": access_token}

            headers = {
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "recipient": {
                    "id": recipient_id
                },
                "message": {
                    "attachment": {
                        "type": "image",
                        "payload": {
                            "url": str(image_url),
                            "is_reusable": False
                        }
                    }
                }
            })
            requests.post("https://graph.facebook.com/v10.0/me/messages",
                          params=params, headers=headers, data=data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "send_image : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_livechat_attachment(recipient_id, attached_file_src, page_access_token, attachment_type):
    try:
        access_token = page_access_token
        params = {
            "access_token": access_token}

        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": str(attachment_type),
                    "payload": {
                        "url": str(attached_file_src),
                        "is_reusable": False
                    }
                }
            }
        })
        requests.post("https://graph.facebook.com/v10.0/me/messages",
                      params=params, headers=headers, data=data)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "send_file : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_button_with_msg(recipient_id, message_text, button_list, type_btn, page_access_token):
    try:
        fb_btn_list = []
        access_token = page_access_token
        if type_btn == "choice":
            for element in button_list:
                new_dict = {
                    "content_type": "text",
                    "title": element["display"],
                    "payload": element["display"],
                }
                fb_btn_list.append(new_dict)
        else:
            for element in button_list:
                new_dict = {
                    "content_type": "text",
                    "title": element,
                    "payload": element,
                }
                fb_btn_list.append(new_dict)
        params = {
            "access_token": access_token}

        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "messaging_type": "RESPONSE",
            "message": {
                "text": message_text,
                "quick_replies": fb_btn_list
            }
        })
        requests.post("https://graph.facebook.com/v10.0/me/messages",
                      params=params, headers=headers, data=data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "send_button_with_msg : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_cards(recipient_id, cards_list, page_access_token):
    try:
        fb_cards_list = []
        access_token = page_access_token
        for fb_card in cards_list:
            if fb_card['img_url'].strip() != "":
                temp_dict = {
                    "title": fb_card['title'],
                    "image_url": fb_card['img_url'],
                    "default_action": {
                        "type": "web_url",
                        "url": fb_card['link'],
                        "webview_height_ratio": "tall",
                    },
                }
            else:
                temp_dict = {
                    "title": fb_card['title'],
                    "default_action": {
                        "type": "web_url",
                        "url": fb_card['link'],
                        "webview_height_ratio": "tall",
                    },
                    "buttons": [
                        {
                            "type": "web_url",
                            "url": fb_card['link'],
                            "title":"Click here"
                        }]
                }
            fb_cards_list.append(temp_dict)

        params = {
            "access_token": access_token}

        headers = {
            "Content-Type": "application/json"
        }

        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": fb_cards_list
                    }
                }
            }
        })
        requests.post("https://graph.facebook.com/v10.0/me/messages",
                      params=params, headers=headers, data=data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "send_cards : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_facebook_message(recipient_id, message_text, page_access_token):

    try:
        access_token = page_access_token
        params = {
            "access_token": access_token}

        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "messaging_type": "RESPONSE",
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text
            }
        })
        requests.post("https://graph.facebook.com/v10.0/me/messages",
                      params=params, headers=headers, data=data)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_facebook_message: POST Method: " +
                     str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_recommendations_quick_replies(recipient_id, page_access_token, recommendations=None, text_response=None):
    try:
        access_token = page_access_token        
        try:
            if recommendations:
                buttons = []
                button_dict = {}
                for recommendation in recommendations:
                    if isinstance(recommendation, str) or isinstance(recommendation, int):

                        title = str(recommendation)
                        payload = str(recommendation)
                    elif isinstance(recommendation, dict) and "name" in recommendation:

                        title = str(recommendation["name"])
                        payload = str(recommendation["name"])
                    elif isinstance(recommendation, dict):

                        title = recommendation["display"]
                        payload = recommendation["value"]

                    title = remove_tags(str(title)).replace(
                        "SBI", "").replace("Plan", "").strip()
                    payload = remove_tags(str(payload))
                    button_dict = {
                        "content_type": "text",
                        "title": title,
                        "payload": payload
                    }
                    buttons.append(button_dict)
                params = {
                    "access_token": access_token}

                headers = {
                    "Content-Type": "application/json"
                }
                data = {
                    "messaging_type": "RESPONSE",
                    "recipient": {
                        "id": recipient_id
                    },
                    "message": {
                        "text": text_response,
                        "quick_replies": buttons
                    }
                }
                logger.info(
                    "Inside send_recommendations_quick_replies Facebook" + str(json.dumps(data)), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                requests.post(
                    "https://graph.facebook.com/v15.0/me/messages", params=params, headers=headers, data=json.dumps(data))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                "FacebookWebhookAPI: Recommendations Quick Replies: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "FacebookWebhookAPI: Recommendations Quick Replies: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_recommendations_carousel(recipient_id, page_access_token, recommendations=None):
    try:

        access_token = page_access_token
        recommendations_handled_after = []
        if len(recommendations) > 30:
            # recommendations_handled_now = recommendations[:30]
            recommendations_handled_after = recommendations[30:]

        elements_list = []
        no_of_sugestions = 3
        if len(recommendations) % 3 != 0 and len(recommendations) % 2 == 0 and len(recommendations) <= 20:
            no_of_sugestions = 2
        try:
            if recommendations:
                counter = 0
                element_dict = {}
                buttons = []
                button_dict = {}

                for recommendation in recommendations:

                    if isinstance(recommendation, str) or isinstance(recommendation, int):

                        title = str(recommendation)
                        payload = str(recommendation)
                    elif isinstance(recommendation, dict) and "name" in recommendation:

                        title = str(recommendation["name"])
                        payload = str(recommendation["name"])
                    elif isinstance(recommendation, dict):

                        title = recommendation["display"]
                        payload = recommendation["value"]

                    title = remove_tags(str(title)).replace(
                        "SBI", "").replace("Plan", "").strip()
                    payload = remove_tags(str(payload))

                    if counter == no_of_sugestions:
                        buttons = []
                        counter = 0
                        element_dict = {}

                    if element_dict == {}:
                        element_dict = {
                            "title": "-",
                        }

                    button_dict = {
                        "type": "postback",
                        "title": title,
                        "payload": payload
                    }
                    buttons.append(button_dict)

                    if counter == no_of_sugestions - 1:
                        element_dict["buttons"] = buttons
                        elements_list.append(element_dict)

                    counter += 1

                if counter <= no_of_sugestions - 1:
                    element_dict["buttons"] = buttons
                    elements_list.append(element_dict)

                params = {
                    "access_token": access_token}

                headers = {
                    "Content-Type": "application/json"
                }

                data = {
                    "messaging_type": "RESPONSE",
                    "recipient": {
                        "id": recipient_id
                    },
                    "message": {
                        "attachment": {
                            "type": "template",
                            "payload": {
                                "template_type": "generic"}
                        }
                    }
                }
                data["message"]["attachment"]["payload"][
                    "elements"] = elements_list

                logger.info(
                    "Inside send_recommendations_carousel Facebook" + str(json.dumps(data)), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                requests.post(
                    "https://graph.facebook.com/v10.0/me/messages", params=params, headers=headers, data=json.dumps(data))

            if recommendations_handled_after:
                send_recommendations_carousel(
                    recipient_id, page_access_token, recommendations=recommendations_handled_after)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                "FacebookWebhookAPI: Recommendations carousel: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "FacebookWebhookAPI: Recommendations carousel: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_facebook_livechat_agent_response(message, customer_obj, session_id, attached_file_src, data, BotChannel, Profile):
    try:
        user_obj = Profile.objects.get(livechat_session_id=session_id)
        if user_obj.livechat_connected == True:

            recipient_id = str(user_obj.user_id).replace(
                "facebook_user_", "")
            page_access_token = BotChannel.objects.get(bot=customer_obj.bot,
                                                       channel=customer_obj.channel).page_access_token

            if attached_file_src != "":

                if "channel_file_url" in data:

                    attached_file_src = data["channel_file_url"]

                    try:
                        attached_file_src = settings.EASYCHAT_HOST_URL + attached_file_src

                        file_name = attached_file_src.split("/")[-1]

                        file_type = get_file_type(file_name)

                        if file_type == "invalid file format":
                            # will do something
                            pass
                        else:
                            send_livechat_attachment(recipient_id, attached_file_src,
                                                     page_access_token, file_type)

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("send_facebook_livechat_agent_response: %s at %s",
                                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            if message != "":
                send_facebook_message(recipient_id, message, page_access_token)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_facebook_livechat_agent_response: %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def get_file_type(file_name):
    try:
        file_ext = file_name.split(".")[-1]

        if file_ext.lower() in ["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]:
            return "image"

        elif file_ext.upper() in ["WEBM", "MPG", "MP2", "MPEG", "MPE", "MPV", "OGG", "MP4", "M4P", "M4V", "AVI", "WMV", "MOV", "QT", "FLV", "SWF", "AVCHD"]:
            return "video"

        elif file_ext.lower() in ["pdf", "docs", "docx", "doc", "PDF", "txt", "TXT"]:
            return "file"
        else:
            return "invalid file format"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return "invalid file format"


def save_and_get_facebook_file_src(attachment, recipient_id, page_access_token, selected_language, EasyChatTranslationCache):

    try:
        import os
        from urllib.parse import urlparse

        url = attachment["payload"]["url"]
        req = requests.get(url=url)

        file_name = os.path.basename(urlparse(url).path)
        file_directory = "files/facebook-attachment/"

        file_ext = file_name.split(".")[-1]
        allowed_file_extensions = ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "BMP", "GIF", "TIFF", "EXIF", "JFIF", "WEBM", "MPG", "MP2",
                                   "MPEG", "MPE", "MPV", "OGG", "MP4", "M4P", "M4V", "AVI", "WMV", "MOV", "QT", "FLV", "SWF", "AVCHD", "PDF", "DOCS", "DOCX", "DOC"]

        if file_ext.upper() not in allowed_file_extensions:
            file_not_supported_text = "This file format is not supported"
            if selected_language != "en":
                file_not_supported_text = get_translated_text(file_not_supported_text, selected_language, EasyChatTranslationCache)
                
            send_facebook_message(
                recipient_id, file_not_supported_text, page_access_token)
            return ""
        full_path = file_directory + file_name

        local_file = open(full_path, 'wb')

        local_file.write(req.content)
        local_file.close()

        full_path = "/files/facebook-attachment/" + file_name

        return full_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return ""


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
        
        strong_tag_end_position = 0
        if "<strong>" in message:
            for itr in range(message.count("<strong>")):
                strong_position = message.find("<strong>", strong_tag_end_position)
                strong_tag_end_position = message.find("</strong>", strong_position)
                strong_str = message[strong_position:strong_tag_end_position]
                em_replace = strong_str.replace("<em>", "").replace("</em>", "")
                message = message.replace(strong_str, em_replace)
        
        em_tag_end_position = 0
        if "<em>" in message:
            for itr in range(message.count("<em>")):
                em_position = message.find("<em>", em_tag_end_position)
                em_tag_end_position = message.find("</em>", em_position)
                em_str = message[em_position:em_tag_end_position]
                em_replace = em_str.replace("<strong>", "").replace("</strong>", "")
                message = message.replace(em_str, em_replace)

        for tag in tags:
            message = message.replace(tag, tags[tag])
        if "</a>" in message:
            message = message.replace("mailto:", "").replace("tel:", "")
            soup = BeautifulSoup(message, "html.parser")
            for link in soup.findAll('a'):
                href = link.get('href')
                if not href:
                    continue
                link_name = link.string
                link_element = message[message.find(
                    "<a"):message.find("</a>")] + "</a>"
                if link_name.replace("http://", "").replace("https://", "").replace("*", "").replace("_", "").strip() == href.replace("http://", "").replace("https://", "").strip():
                    message = message.replace(link_element, link_name)
                else:
                    if "*" in link_name and "_" in link_name:
                        message = message.replace(link_element, ' ' + link_name + " _*(" + href + ")*_ ")
                        
                    elif "*" in link_name:
                        message = message.replace(link_element, ' ' + link_name + " *(" + href + ")* ")
                    elif "_" in link_name:
                        message = message.replace(link_element, ' ' + link_name + " _(" + href + ")_ ")
                    else:
                        message = message.replace(link_element, link_name + " (" + href + ")")
        message = message.replace("**", "")
        message = message.replace("__", "")
        message = message.replace("_*", "*")
        message = message.replace("*_", "*")

    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed to format html string format of facebook: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return message


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
        logger.error("Failed to format facebook html list string: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
        # print("Failed to format html list string: %s", str(E))
    return sent
