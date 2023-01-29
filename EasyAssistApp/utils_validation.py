from django.conf import settings
from EasyAssistApp.html_parser import strip_html_tags
from EasyAssistApp.constants import *
from lxml.html.clean import Cleaner

import logging
import re
import os
import magic
import base64
import uuid
import imghdr
import mimetypes
import sys
import hashlib

logger = logging.getLogger(__name__)


def check_for_malicious_image_file_from_content(base64_data, file_ext):
    try:
        temp_file_ext = file_ext.split('.')[-1]
        file_name = "temp_" + str(uuid.uuid4()) + '.' + temp_file_ext
        file_path = settings.MEDIA_ROOT + file_name
        fh = open(file_path, "wb")
        fh.write(base64.b64decode(base64_data))
        fh.close()
        temp_file_ext = imghdr.what(file_path)
        if not temp_file_ext:
            file_ext = "None"
        os.remove(file_path)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In check_for_malicious_image_file_from_content: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return file_ext


def remo_html_from_string(raw_str):
    try:
        regex_cleaner = re.compile('<.*?>')
        cleaned_raw_str = re.sub(regex_cleaner, '', raw_str)
        return cleaned_raw_str
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In remo_html_from_string: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})
        return raw_str


def remo_special_html_from_string(raw_str):
    try:
        cleaned_str = raw_str.replace('<', '')
        cleaned_str = cleaned_str.replace('>', '')
        cleaned_str = cleaned_str.replace('"', '')
        cleaned_str = cleaned_str.replace("'", '')
        return cleaned_str
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In remo_special_html_from_string: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})
        return raw_str


def sanitize_input_string(input_string):
    try:
        sanitized_string = strip_html_tags(input_string)
        sanitized_string = remo_html_from_string(sanitized_string)
        sanitized_string = remo_special_html_from_string(sanitized_string)
        return sanitized_string
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In sanitize_input_string: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})
        return input_string


def remo_special_tag_from_string(raw_str):
    try:
        cleaned_raw_str = raw_str.replace(
            "+", "").replace("|", "").replace("-", "").replace("=", "")
        return cleaned_raw_str
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In remo_special_tag_from_string: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})
        return raw_str


def remove_special_chars_from_filename(filename):
    try:
        cleaned_filename = filename.replace(
            "&", "").replace("@", "").replace("<", "").replace(">", "")
        return cleaned_filename
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In remo_special_tag_from_string: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})
        return filename


def check_malicious_file_from_filename(filename, allowed_files_list=None):
    if allowed_files_list == None:
        allowed_files_list = [
            "png", "jpg", "jpeg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg", "jpe",
            "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt", "doc", "docx",
            "flv", "swf", "avchd", "mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip", "xlb"
        ]

    try:
        if len(filename.split('.')) != 2:
            return True

        file_extension = filename.split('.')[-1].lower().strip()

        if file_extension not in allowed_files_list:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In check_malicious_file_from_filename: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})
        return True


def check_malicious_file(uploaded_file):
    return check_malicious_file_from_filename(uploaded_file.name)


def check_malicious_file_from_content(base64_data, allowed_files_list=None):

    # Untill we find any concrete solution for detecting file type
    return False
    
    # decoded = base64.b64decode(base64_data)
    # mime_type = magic.from_buffer(decoded, mime=True)
    # file_ext = mimetypes.guess_extension(mime_type)

    # if file_ext.split('.')[-1].lower() in ALLOWED_IMAGE_FILE_EXTENTIONS:
    #     file_ext = check_for_malicious_image_file_from_content(
    #         base64_data, file_ext)

    # return check_malicious_file_from_filename(file_ext, allowed_files_list)


def validate_user_new_password(active_agent, new_password, old_password, AgentPasswordHistory):
    agent_password_history_objs = AgentPasswordHistory.objects.filter(
        agent=active_agent).order_by('-datetime')[:5]
    old_password_list = [
        item.password_hash for item in agent_password_history_objs]

    new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    old_password_hash = hashlib.sha256(old_password.encode()).hexdigest()

    if old_password_hash not in old_password_list:
        old_password_list.append(old_password_hash)

    if new_password_hash in old_password_list:
        return "SIMILAR_TO_OLD_PASSWORD"

    return "VALID"


def is_url_valid(url):
    try:
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            # domain
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, url) is not None:
            return True
        else:
            return False

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside is_url_valid: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return False


def is_email_valid(email_id):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email_id)):
        return True
    else:
        return False


def remo_unwanted_security_characters(text) -> str:
    try:
        regex_cleaner = re.compile(r'[\(\)<>]')
        cleaned_text = re.sub(regex_cleaner, '', text)

        return cleaned_text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside remo_unwanted_security_characters: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return text


def clean_html(text):
    try:
        text = text.strip()

        if text == "":
            return text

        clean_obj = Cleaner(remove_unknown_tags=False, remove_tags=[
                            'img'], page_structure=False)
        text = clean_obj.clean_html(text)
        text = re.sub("<p>", "", text)
        text = re.sub("</p>", "", text)
        text = remo_unwanted_security_characters(text)
        return text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In clean_html: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return text


def is_mobile_valid(mobile):
    try:
        mobile_regex = r'^[6-9]{1}[0-9]{9}$'
        if(re.fullmatch(mobile_regex, mobile)):
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In is_mobile_valid: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return False


def check_valid_name(name):
    try:
        name_regex = r'^[a-zA-Z ]+$'
        if(re.fullmatch(name_regex, name)):
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In check_valid_name: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return False


def is_password_valid(password):
    try:
        password_regex = r'[A-Za-z0-9!@#$*&]{8,}'
        if(re.fullmatch(password_regex, password)):
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In is_password_valid: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return False


def is_valid_filename(filename):
    try:
        file_name_regex = r'[A-Za-z0-9-_]+$'
        if(re.fullmatch(file_name_regex, filename)):
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In is_valid_filename: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return False


def validate_input_number(input_number):
    try:
        input_number = str(input_number)
        if input_number.isdigit():
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In validate_input_number: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return False
