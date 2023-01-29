from PIL import Image
import re
import os
import sys
import uuid
import magic
import base64
import imghdr
import logging
import mimetypes
from django.conf import settings

from EasyChatApp.constants import ALLOWED_IMAGE_FILE_EXTENTIONS
from EasyChatApp.models import Bot, Config, Intent
from django.core.validators import URLValidator
from lxml.html.clean import Cleaner

from sklearn.feature_extraction import text as sklearn_text

logger = logging.getLogger(__name__)

url_validator = URLValidator()


"""
Description: This class contains methods related to input validation and sanitization
"""


class EasyChatInputValidation:

    def __init__(self) -> 'EasyChatInputValidation':
        self.extra = {'AppName': 'EasyChat', 'user_id': 'None',
                      'source': 'None', 'channel': 'None', 'bot_id': 'None'}

    def is_valid_query(self, query: str) -> bool:
        # Directly returning True from here because this was causing mis-match in analytics
        # Single letter or numeric queries were not being considered in unanswered queries
        # Because is_unidentified_query was not being set to True due to this function
        return True
        string = str(query).strip()

        if len(string.split(" ")) > 1:
            return True
        if len(string) == 1:
            return False
        if string.isdigit():
            return False
        if re.match(r'^[a-z]{5}[0-9]{4}[a-z]$', string.lower()):
            return False
        if re.match(r'^[a-z]{4}0[0-9a-z]{6}$', string.lower()):
            return False
        my_stopword_list = []
        stop_words = sklearn_text.ENGLISH_STOP_WORDS.union(
            my_stopword_list)
        if string in stop_words:
            return False

        return True

    def is_string_only_contains_emoji(self, input_str: str) -> bool:
        try:
            emoji_regex = re.compile(
                "["
                "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F700-\U0001F77F"  # alchemical symbols
                "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                "\U0001FA00-\U0001FA6F"  # Chess Symbols
                "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                "\U00002702-\U000027B0"  # Dingbats
                "\U000024C2-\U0001F251"
                "]+"
            )

            emoji_replaced_string = re.sub(emoji_regex, '', input_str)
            if emoji_replaced_string.strip() == '':
                return True

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("is_string_only_contains_emoji: %s %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def is_valid_password(self, password: str) -> bool:
        try:
            password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$"
            pattern = re.compile(password_regex)

            if re.search(pattern, password):
                return True
            else:
                return False
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("is_valid_password: %s %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def is_valid_email(self, email: str) -> bool:
        try:
            regex = "^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$"
            if(re.search(regex, email)):
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("is_valid_email: %s %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def is_alphanumeric(self, input: str) -> bool:
        try:
            reg = r'^[0-9a-zA-Z &@-]+$'

            if re.match(reg, input.lower()):
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("is_alphanumeric: %s %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def is_numeric(self, input):
        try:
            float(input)
            return True
        except ValueError:
            return False

    def is_valid_name(self, input: str) -> bool:
        try:
            reg = r'^[a-zA-Z ]+$'

            if re.match(reg, input.lower()):
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("is_valid_name: %s %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def is_valid_bot_name(self, input: str) -> bool:
        try:
            regex = r'[`@#$%^*()_+\-=\[\]{};\':"\\|,.<>\/~]'
            emoji_regex = re.compile(
                "["
                "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F700-\U0001F77F"  # alchemical symbols
                "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                "\U0001FA00-\U0001FA6F"  # Chess Symbols
                "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                "\U00002702-\U000027B0"  # Dingbats
                "\U000024C2-\U0001F251"
                "]+"
            )
            if input.strip() == '' or len(input.strip()) > 18:
                return False

            if re.search(regex, input):
                return False

            emoji_replaced_bot_name = re.sub(emoji_regex, '', input)
            if emoji_replaced_bot_name.strip() == '':
                return False

            return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("is_valid_bot_name: %s %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def is_valid_card_name(self, input: str) -> bool:
        try:
            reg = r'[a-zA-Z]'
            if not re.search(reg, input):
                return False

            reg = r'[`#%^*()_+\-=\[\]{};\':"\\|,.<>\/~]'
            if re.search(reg, input):
                return False

            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("is_valid_card_name: %s %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

    def remo_html_from_string(self, html: str) -> str:
        try:
            regex_cleaner = re.compile('<.*?>')
            cleaned_raw_str = re.sub(regex_cleaner, '', str(html))

            return cleaned_raw_str.strip()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_html_from_string: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return html.strip()

    def remo_html_from_string_with_space(self, html: str) -> str:
        try:
            regex_cleaner = re.compile('<.*?>')
            cleaned_raw_str = re.sub(regex_cleaner, ' ', str(html))

            return cleaned_raw_str.strip()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_html_from_string_with_space: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return html.strip()

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

    def remo_unwanted_security_characters(self, input: str) -> str:
        try:
            regex_cleaner = re.compile(r'[\(\)<>]')
            cleaned_raw_str = re.sub(regex_cleaner, '', str(input))

            return cleaned_raw_str
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_unwanted_security_characters: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return input

    def remo_unwanted_characters_from_message(self, input: str, bot_id: int) -> str:
        try:
            if self.is_valid_url(str(input)):
                return input

            unwanted_characters = Bot.objects.get(
                pk=bot_id).autcorrect_replace_bot
            replace_space = "[" + unwanted_characters + "]"
            cleaned_raw_str = re.sub(replace_space, '', input)

            return cleaned_raw_str
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_unwanted_characters_from_message: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return input

    def remo_special_tag_from_string(self, input: str) -> str:
        try:
            configobject = Config.objects.all()[0]
            autocorrect_replace_space = configobject.autocorrect_replace_space
            autocorrect_do_nothing = configobject.autcorrect_do_nothing

            raw_str = input
            if autocorrect_replace_space != "":
                replace_space = "[" + autocorrect_replace_space + "]"
                raw_str = re.sub(replace_space, ' ', raw_str)

            do_nothing = "[^a-zA-Z0-9 " + autocorrect_do_nothing + "]+"
            raw_str = re.sub(do_nothing, '', raw_str)
            cleaned_raw_str = raw_str.strip()

            return cleaned_raw_str
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_special_tag_from_string: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

            return input

    def remo_special_characters_from_string(self, input: str) -> str:
        regex = r'[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]'
        try:
            regex_cleaner = re.compile(regex)
            cleaned_raw_str = re.sub(regex_cleaner, '', str(input))
            return cleaned_raw_str
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_special_characters_from_string: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)
            return input

    def remove_hexabyte_character(self, input) -> str:
        try:
            return re.sub(r'[^\x00-\x7f]', r' ', input)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remove_hexabyte_character: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return input

    def unicode_formatter(self, message):
        try:
            unicodes = {"&nbsp;": " ", "&#39;": "\'", "&rsquo;": "\'", "&amp;": "&",
                        "&hellip;": "...", "&quot;": "\"", "&rdquo;": "\"", "&ldquo;": "\"", "&lt;": "<", "&gt;": ">"}
            for code in unicodes:
                message = message.replace(code, unicodes[code])

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside unicode_formatter: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return message

    def remo_complete_html_and_special_tags(self, str_val: str) -> str:
        try:
            str_val = self.remo_html_from_string(str_val)
            str_val = self.remo_special_tag_from_string(str_val)
            return str_val
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_complete_html_and_special_tags: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

    def remo_complete_html_and_unwanted_characters(self, str_val: str, bot_id: int) -> str:
        try:
            str_val = self.remo_html_from_string(str_val)
            str_val = self.remo_unwanted_characters_from_message(
                str_val, int(bot_id))
            return str_val
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside remo_complete_html_and_unwanted_characters: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

    def is_valid_url(self, str_val: str) -> bool:
        try:
            url_validator(str_val)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Inside is_valid_url: %s at %s",
                           str(e), str(exc_tb.tb_lineno), extra=self.extra)
            return False

        return True

    def custom_remo_html_tags(self, raw_str):
        raw_str = raw_str.replace("&lt;", "<")
        raw_str = raw_str.replace("&gt;", ">")
        raw_str = raw_str.replace("&quot;", "'")
        raw_str = raw_str.replace("<strong>", "||strong||")
        raw_str = raw_str.replace("</strong>", "||/strong||")
        raw_str = raw_str.replace("<u>", "||u||")
        raw_str = raw_str.replace("</u>", "||/u||")
        raw_str = raw_str.replace("<ul>", "||ul||")
        raw_str = raw_str.replace("</ul>", "||/ul||")
        raw_str = raw_str.replace("<li>", "||li||")
        raw_str = raw_str.replace("</li>", "||/li||")
        raw_str = raw_str.replace("<ol>", "||ol||")
        raw_str = raw_str.replace("</ol>", "||/ol||")
        raw_str = raw_str.replace("<p>", "||p||")
        raw_str = raw_str.replace("</p>", "||/p||")
        raw_str = raw_str.replace("<br />", "||br||")
        raw_str = raw_str.replace("<br>", "||br||")
        raw_str = raw_str.replace("<em>", "||em||")
        raw_str = raw_str.replace("</em>", "||/em||")
        raw_str = raw_str.replace("<b>", "||b||")
        raw_str = raw_str.replace("</b>", "||/b||")
        raw_str = raw_str.replace("<i>", "||i||")
        raw_str = raw_str.replace("</i>", "||/i||")
        regex_cleaner = re.compile('<(?!\/?a(?=>|\s.*>))\/?.*?>')
        cleaned_raw_str = re.sub(regex_cleaner, '', raw_str)

        cleaned_raw_str = cleaned_raw_str.replace("||br||", "<br>")
        cleaned_raw_str = cleaned_raw_str.replace("||strong||", "<strong>")
        cleaned_raw_str = cleaned_raw_str.replace("||/strong||", "</strong>")
        cleaned_raw_str = cleaned_raw_str.replace("||ul||", "<ul>")
        cleaned_raw_str = cleaned_raw_str.replace("||/ul||", "</ul>")
        cleaned_raw_str = cleaned_raw_str.replace("||u||", "<u>")
        cleaned_raw_str = cleaned_raw_str.replace("||/u||", "</u>")
        cleaned_raw_str = cleaned_raw_str.replace("||li||", "<li>")
        cleaned_raw_str = cleaned_raw_str.replace("||/li||", "</li>")
        cleaned_raw_str = cleaned_raw_str.replace("||ol||", "<ol>")
        cleaned_raw_str = cleaned_raw_str.replace("||/ol||", "</ol>")
        cleaned_raw_str = cleaned_raw_str.replace("||/p||", "</p>")
        cleaned_raw_str = cleaned_raw_str.replace("||p||", "<p>")
        cleaned_raw_str = cleaned_raw_str.replace("||br||", "<br>")
        cleaned_raw_str = cleaned_raw_str.replace("||/em||", "</em>")
        cleaned_raw_str = cleaned_raw_str.replace("||em||", "<em>")
        cleaned_raw_str = cleaned_raw_str.replace("||b||", "<b>")
        cleaned_raw_str = cleaned_raw_str.replace("||/b||", "</b>")
        cleaned_raw_str = cleaned_raw_str.replace("||/i||", "</i>")
        cleaned_raw_str = cleaned_raw_str.replace("||i||", "<i>")

        return cleaned_raw_str

    def sanitize_html(self, text):
        try:
            text = text.replace("&", "&amp;")
            text = text.replace("<", "&lt;")
            text = text.replace(">", "&gt;")
            text = text.replace("'", "&#39;")
            return text
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In sanitize_html: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return text
    
    def reverse_sanitize_html(self, text):
        try:
            text = text.replace("&amp;", "&")
            text = text.replace("&lt;", "<")
            text = text.replace("&gt;", ">")
            text = text.replace("&#39;", "'")
            return text
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In re_sanitize_html: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return text

    def clean_html(self, text):
        try:
            text = text.strip()

            if text == "":
                return text

            clean_obj = Cleaner(remove_unknown_tags=False, remove_tags=[
                                'img'], page_structure=False)
            text = clean_obj.clean_html(text)
            text = re.sub("<div>", "", text)
            text = re.sub("</div>", "", text)
            return text
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In clean_html: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return text

    def is_valid_latitude(self, coordinates):
        try:
            regex = '^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$'
            if re.match(regex, coordinates):
                return True
            return False

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In is_valid_latitude: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def is_valid_longitude(self, coordinates):
        try:
            regex = '^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$'
            if re.match(regex, coordinates):
                return True
            return False

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In is_valid_longitude: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

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

    def check_for_special_characters(self, text) -> bool:
        try:
            regex = r'[`@#$%^*()_+\-=\[\]{};\':"\\|,.<>\/~]'
            if re.search(regex, text):
                return True

            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside check_for_special_characters: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return True


class EasyChatFileValidation:

    def __init__(self) -> 'EasyChatFileValidation':
        self.extra = {'AppName': 'EasyChat', 'user_id': 'None',
                      'source': 'None', 'channel': 'None', 'bot_id': 'None'}

        self.allowed_files_list = [
            "png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg",
            "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt",
            "flv", "swf", "avchd", "mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip", "ppt", "pptx", "docx", "docs", "txt", "jpe",
            "bin",
        ]

    def check_malicious_file(self, file_name: str) -> bool:
        try:
            # if len(file_name.split('.')) != 2:
            #     return True

            if file_name.lower().split('.')[-1] not in self.allowed_files_list:
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
            # if len(filename.split('.')) != 2:
            #     return True

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

        #     if file_ext.split('.')[-1].lower() in ALLOWED_IMAGE_FILE_EXTENTIONS:
        #         file_ext = self.check_for_malicious_image_file_from_content(
        #             base64_data, file_ext)

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

    def remove_image_exif(self, image):
        try:
            # next 3 lines strip exif
            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)
            return image_without_exif
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In image_exif_remover: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

            return image

    def is_image(self, file_name):

        is_image = False

        try:
            file_ext = file_name.split(".")[-1]

            if file_ext.upper() in ["PNG", "JPG", "JPEG"]:
                is_image = True

            return is_image

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_image %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return is_image

    def is_video(self, file_name):

        is_video = False

        try:
            file_ext = file_name.split(".")[-1]

            if file_ext.upper() in ["GIF", "WEBM", "MP2", "MPEG", "MPE", "MPV", "MP4", "AVI", "MOV"]:
                is_video = True

            return is_video

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_video %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return is_video
