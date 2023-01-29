import os
import sys
import json
import requests
import logging
import re
import magic
import mimetypes
from uuid import uuid4
from urllib.parse import urlparse
from EasyChatApp.utils_validation import *

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
    return text


def get_recommendations(recommendations, recipient_id):
    try:

        elements_list = []
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
                "title": title,
                "payload": payload
            }
            elements_list.append(button_dict)

        return elements_list

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("MicrosoftTeamsQueryAPI: Recommendations carousel: " + str(e) + str(exc_tb.tb_lineno),
                     extra={'AppName': 'EasyChat', 'user_id': str(recipient_id), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return []


def save_and_get_microsoft_file_src(attachment, recipient_id):

    try:
        url = attachment["url"]
        req = requests.get(url=url)

        file_content = req.content

        file_name = str(uuid4().hex)
        file_directory = "files/microsoft-teams-attachment/"

        file_ext = file_validation_obj.get_file_extension_from_content(
            file_content)
        file_ext = file_ext.split(".")[-1]

        file_name = file_name + "." + file_ext

        allowed_file_extensions = ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "BMP", "GIF", "TIFF", "EXIF", "JFIF", "WEBM", "MPG", "MP2",
                                   "MPEG", "MPE", "MPV", "OGG", "MP4", "M4P", "M4V", "AVI", "WMV", "MOV", "QT", "FLV", "SWF", "AVCHD", "PDF", "DOCS", "DOCX", "DOC"]

        if file_ext.upper() not in allowed_file_extensions:
            return "FILE_NOT_SUPPORTED"

        full_path = file_directory + file_name

        local_file = open(full_path, 'wb')

        local_file.write(file_content)
        local_file.close()

        full_path = "/files/microsoft-teams-attachment/" + file_name

        return full_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_and_get_microsoft_file_src %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return ""
