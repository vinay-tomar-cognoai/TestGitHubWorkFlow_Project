import sys
import json
import requests
import logging
import re
import os
import magic
import mimetypes
from uuid import uuid4
from EasyChatApp.utils_validation import *
from urllib.parse import urlparse

from django.shortcuts import HttpResponse
from django.conf import settings
logger = logging.getLogger(__name__)
file_validation_obj = EasyChatFileValidation()


def remove_tags(text):
    text = text.replace("<br>", "")
    text = text.replace("<b>", "")
    text = text.replace("</b>", "")
    text = text.replace("<i>", "")
    text = text.replace("</i>", "")
    text = text.replace("  ", " ")
    text = text.replace("*", "")
    return text


def verify_webhook(request, Bot, Channel, BotChannel):
    try:
        logger.info("Request GET " +
                    str(request.GET), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        bot_id = request.GET.get('id')
        bot_obj = Bot.objects.get(pk=bot_id)
        channel_obj = Channel.objects.get(name="Instagram")
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
            requests.post("https://graph.facebook.com/v12.0/me/messages",
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
        requests.post("https://graph.facebook.com/v12.0/me/messages",
                      params=params, headers=headers, data=data)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "send_cards : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_instagram_message(recipient_id, message_text, page_access_token):

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
        requests.post("https://graph.facebook.com/v12.0/me/messages",
                      params=params, headers=headers, data=data)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_instagram_message: POST Method: " +
                     str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_instagram_reaction_message(recipient_id, mid, page_access_token):

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
            "sender_action": "react",
            "payload": {
                "message_id": mid,
                "reaction": "love",
            }
        })
        requests.post("https://graph.facebook.com/v12.0/me/messages",
                      params=params, headers=headers, data=data)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_instagram_message: POST Method: " +
                     str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


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
                    "Inside send_recommendations_carousel Instagram" + str(json.dumps(data)), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                requests.post(
                    "https://graph.facebook.com/v12.0/me/messages", params=params, headers=headers, data=json.dumps(data))

            if recommendations_handled_after:
                send_recommendations_carousel(
                    recipient_id, page_access_token, recommendations=recommendations_handled_after)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                "InstagramWebhookAPI: Recommendations carousel: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "InstagramWebhookAPI: Recommendations carousel: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_instagram_livechat_agent_response(message, customer_obj, session_id, attached_file_src, data, BotChannel, Profile):
    try:
        user_obj = Profile.objects.get(livechat_session_id=session_id)
        if user_obj.livechat_connected == True:

            recipient_id = str(user_obj.user_id).replace(
                "instagram_user_", "")
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
                        logger.error("send_instagram_livechat_agent_response: %s at %s",
                                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            if message != "":
                send_instagram_message(
                    recipient_id, message, page_access_token)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_instagram_livechat_agent_response: %s at %s",
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


def save_and_get_instagram_file_src(attachment, recipient_id, page_access_token):

    try:
        url = attachment["payload"]["url"]
        req = requests.get(url=url)

        file_content = req.content

        file_name = str(uuid4().hex)
        file_directory = "files/instagram-attachment/"

        file_ext = file_validation_obj.get_file_extension_from_content(
            file_content)
        file_ext = file_ext.split(".")[-1]

        file_name = file_name + "." + file_ext

        allowed_file_extensions = ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "BMP", "GIF", "TIFF", "EXIF", "JFIF", "WEBM", "MPG", "MP2",
                                   "MPEG", "MPE", "MPV", "OGG", "MP4", "M4P", "M4V", "AVI", "WMV", "MOV", "QT", "FLV", "SWF", "AVCHD", "PDF", "DOCS", "DOCX", "DOC"]

        if file_ext.upper() not in allowed_file_extensions:
            send_instagram_message(
                recipient_id, "This file format is not supported", page_access_token)
            return ""

        full_path = file_directory + file_name

        local_file = open(full_path, 'wb')

        local_file.write(file_content)
        local_file.close()

        full_path = "/files/instagram-attachment/" + file_name

        return full_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_and_get_instagram_file_src %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return ""
