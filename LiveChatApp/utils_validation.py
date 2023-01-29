import os
import re
import sys
import uuid
import base64
import imghdr
import magic
import mimetypes
import logging
from urllib.parse import urlparse
from django.conf import settings
from django.core.validators import URLValidator

url_validator = URLValidator()

logger = logging.getLogger(__name__)


"""
Description: This class contains methods related to input validation and sanitization
"""


class LiveChatInputValidation:

    def __init__(self) -> None:
        self.extra = {'AppName': 'LiveChat'}

    def remo_html_from_string(self, input):
        try:
            if input == None or input == 'None':
                return None
            input = str(input)
            regex_cleaner = re.compile(r'<[^>]+>')
            cleaned_raw_str = re.sub(regex_cleaner, '', input)

            return cleaned_raw_str.strip()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_html_from_string: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return input.strip()
    
    def replace_break_tags(self, input):
        try:
            regex_cleaner = re.compile(r'<br/*>')
            cleaned_raw_str = re.sub(regex_cleaner, '\n', input)

            return cleaned_raw_str.strip()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside replace_break_tags: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)
            return input.strip()

    def remo_unwanted_characters_from_agent_message(self, input: str, LiveChatAdminConfig, admin) -> str:
        try:
            unwanted_characters = LiveChatAdminConfig.objects.get(
                admin=admin).agent_message_config
            replace_space = "[" + unwanted_characters + "]"
            cleaned_raw_str = re.sub(replace_space, '', input)

            return cleaned_raw_str
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_unwanted_characters_from_agent_message: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return input

    def remo_special_tag_from_string(self, input):
        try:
            if input == None or input == 'None':
                return None

            cleaned_raw_str = input.replace(
                "+", "").replace("|", "").replace("-", "").replace("=", "")

            return cleaned_raw_str
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_special_tag_from_string: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return input

    def validate_name(self, name: str) -> bool:
        try:
            regex = re.compile("^[a-zA-Z ]{2,30}$")

            if re.fullmatch(regex, name) == None:
                return False

            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside validate_name: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def validate_email(self, email: str) -> bool:
        try:
            regex = re.compile(
                r"^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$")

            if re.fullmatch(regex, email) == None:
                return False

            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside validate_email: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def validate_phone_number(self, phone: str) -> bool:
        try:
            regex = re.compile("[6-9][0-9]{9}")

            if re.fullmatch(regex, phone) == None:
                return False

            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside validate_phone_number: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def validate_phone_number_with_country_code(self, phone: str) -> bool:
        try:
            regex = '\+[0-9]{1,3}[0-9]{4,14}'

            if not re.match(regex, phone):
                return False

            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside validate_phone_number_with_country_code: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def validate_password(self, password: str) -> bool:
        try:
            regex = re.compile(r"^\S*$")

            if re.fullmatch(regex, password) == None:
                return False

            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside validate_password: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def alphanumeric(self, text: str) -> bool:
        try:
            reg = r'^[0-9a-zA-Z &@\',;.-:\n]+$'

            if re.match(reg, text.lower()):
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside alphanumeric: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def validate_keyword(self, keyword: str) -> bool:
        try:
            reg = r'^[a-zA-Z ]+$'

            if re.match(reg, keyword.lower()):
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside validate_keyword: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def validate_canned_response(self, response: str) -> bool:
        try:
            reg = r'<.*?>'

            if not re.match(reg, response.lower()):
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside validate_canned_response: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def is_valid_uuid(self, id: str) -> bool:
        try:
            regex = re.compile(
                '^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)

            if re.fullmatch(regex, id) == None:
                return False

            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_valid_uuid %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def remo_unwanted_characters(self, input: str) -> str:
        try:
            regex_cleaner = re.compile(r'[\(\)\.\*\"\']')
            cleaned_raw_str = re.sub(regex_cleaner, '', str(input))

            return cleaned_raw_str
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_unwanted_characters: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return input

    def youtube_link_formatter(self, message):
        try:
            if "https://www.youtube.com" in message:
                message = message.replace(
                    "embed/", "").replace("www.youtube.com", "youtu.be")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside youtube_link_formatter: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return message
        
    def is_url(self, url) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def sanitize_html(self, text):
        try:
            text = text.replace("&", "&amp;")
            text = text.replace("<", "&lt;")
            text = text.replace(">", "&gt;")
            text = text.replace('"', "&quot;")
            text = text.replace("'", "&#039;")
            return text
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In sanitize_html: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return text

    def original_from_sanitize_html(self, text):
        try:
            text = text.replace("&amp;", "&")
            text = text.replace("&lt;", "<")
            text = text.replace("&gt;", ">")
            text = text.replace("&quot;", '"')
            text = text.replace("&#039;", "'")
            return text
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In sanitize_html: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return text

    def unicode_formatter(self, text):
        try:
            unicodes = {"&nbsp;": " ", "&#39;": "\'", "&rsquo;": "\'", "&amp;": "&",
                        "&hellip;": "...", "&quot;": "\"", "&rdquo;": "\"", "&ldquo;": "\"", "&lt;": "<", "&gt;": ">"}
            for code in unicodes:
                text = text.replace(code, unicodes[code])

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside unicode_formatter: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return text
    
    def remove_special_charater_from_string(self, value):
        try:
            if value == None or value == 'None':
                return None
            input = str(value)
            regex_cleaner = re.compile('[!#$%^&*()<>/\}\';`\[\]\\\{"~:-]')
            cleaned_raw_str = re.sub(regex_cleaner, '', input)

            return cleaned_raw_str.strip()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remove_special_charater_from_string: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return input.strip()
    
    def replace_special_character_in_file_name(self, value):
        try:
            if value == None or value == 'None':
                return None
            input = str(value)
            regex_cleaner = re.compile('[-\'/`~!#*$@%+=,^&(){}[\]|;:<>\"\\\?]')
            cleaned_raw_str = re.sub(regex_cleaner, '_', input)

            return cleaned_raw_str.strip()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside replace_special_character_in_file_name: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return input.strip()
    
    def is_special_character_present_in_file_name(self, value):
        try:
            if value == None or value == 'None':
                return None
            input = str(value)
            regex_cleaner = re.compile('[@!#$%^&*()`<>?/\|\'}{~:]')
            is_match = regex_cleaner.search(input) != None

            return is_match
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside replace_special_character_in_file_name: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return False
    
    def is_valid_url(self, str_val: str) -> bool:
        try:
            url_validator(str_val)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Inside is_valid_url: %s at %s",
                           str(e), str(exc_tb.tb_lineno), extra=self.extra)
            return False

        return True
    
    def remove_malicious_chars(self, html: str) -> str:
        try:
            regex_cleaner = re.compile(r'[<>*?]')
            cleaned_raw_str = re.sub(regex_cleaner, '', str(html))
            return cleaned_raw_str.strip()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remove_malicious_chars: %s at %s",
                            str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return html.strip()


class LiveChatFileValidation:

    def __init__(self) -> 'LiveChatFileValidation':
        self.extra = {'AppName': 'LiveChat'}

        self.allowed_files_list = [
            "png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg",
            "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt",
            "flv", "swf", "avchd", "mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip", "ppt", "pptx", "docx", "doc", "txt", "jpe",
            "bin",
        ]

        self.allowed_images_files_extentions = [
            "png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "jpe", "bmp", "gif", "tiff", "exif", "jfif"
        ]

    def check_malicious_file(self, file_name: str) -> bool:
        try:
            if len(file_name.split('.')) != 2:
                return True

            if file_name.split('.')[-1] not in self.allowed_files_list:
                return True
            else:
                return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside check_malicious_file: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)
            return True

    def check_malicious_file_from_filename(self, filename: str, allowed_files_list=None) -> bool:
        if allowed_files_list == None:
            allowed_files_list = self.allowed_files_list

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
            logger.error("In check_malicious_file_from_filename: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

            return True

    def check_for_malicious_image_file_from_content(self, base64_data, file_ext) -> str:
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
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return file_ext

    def check_malicious_file_from_content(self, base64_data, allowed_files_list=None) -> bool:
        # Untill we find any concrete solution for detecting file type
        return False
        # try:
        #     decoded = base64.b64decode(base64_data)
        #     mime_type = magic.from_buffer(decoded, mime=True)
        #     file_ext = mimetypes.guess_extension(mime_type)

        #     if file_ext.split('.')[-1].lower() in self.allowed_images_files_extentions:
        #         file_ext = self.check_for_malicious_image_file_from_content(base64_data, file_ext)

        #     return self.check_malicious_file_from_filename(file_ext, allowed_files_list)
        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     logger.error("In check_malicious_file_from_content: %s at %s", str(
        #         e), str(exc_tb.tb_lineno), extra=self.extra)

        #     return True

    def get_file_extension_from_content(self, decoded_data):
        # Here we are downloading this data from client side, this is why I am not removing this method of getting file type
        mime_type = magic.from_buffer(decoded_data, mime=True)
        file_ext = mimetypes.guess_extension(mime_type)
        return file_ext
