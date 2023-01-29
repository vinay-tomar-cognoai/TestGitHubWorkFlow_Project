import re
import sys
import logging

from django.core.validators import URLValidator
from datetime import datetime, timedelta
from lxml.html.clean import Cleaner


logger = logging.getLogger(__name__)

url_validator = URLValidator()


"""
Description: This class contains methods related to input validation and sanitization
"""


class CampaignInputValidation:

    def __init__(self) -> 'CampaignInputValidation':
        self.extra = {'AppName': 'CampaignApp'}

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

    def remo_special_tag_from_string(self, input: str) -> str:
        try:
            cleaned_input = input.replace(
                "+", "").replace("|", "").replace("-", "").replace("=", "").replace("<", "").replace(">", "")
            return cleaned_input
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In remo_special_tag_from_string: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'CampaignApp'})
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

    def is_valid_url(self, str_val: str) -> bool:
        try:
            url_validator(str_val)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Inside is_valid_url: %s at %s",
                           str(e), str(exc_tb.tb_lineno), extra=self.extra)
            return False

        return True

    def validate_phone_number_without_country_code(self, phone: str) -> bool:
        try:
            regex = re.compile("[6-9][0-9]{9}")

            if re.fullmatch(regex, phone) == None:
                return False

            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside validate_phone_number_without_country_code: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def check_for_special_characters(self, text) -> bool:
        try:
            return bool(re.match('^[\W_ ]+$', text))
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside check_for_special_characters: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def sanitize_input(self, input) -> str:
        try:
            input = str(input).strip()
            input = self.remo_html_from_string(input)
            input = self.remo_special_tag_from_string(input)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside sanitize_input: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra=self.extra)

        return input

    def get_start_and_end_date_time(self, start_date, end_date):
        try:
            date_format = "%Y-%m-%d"
            if start_date == "":
                return "", "", 'The start date cannot be empty.'
            elif end_date == "":
                return "", "", 'The end date cannot be empty.'

            datetime_start = datetime.strptime(
                start_date, date_format).date()
            datetime_end = datetime.strptime(end_date, date_format).date()  # noqa: F841
            today_date = datetime.now().date()

            if datetime_start > today_date:
                return datetime_start, datetime_end, "The start date cannot be greater than the current date."
            elif datetime_end > today_date:
                return datetime_start, datetime_end, "The end date cannot be greater than the current date."
            elif datetime_start > datetime_end:
                return datetime_start, datetime_end, "Start date can not be greater than End date!"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_start_and_end_time: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'Campaign', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            return "", "", "Date formats are not valid!"

        return datetime_start, datetime_end, None

    # This function will remove all the brackets, hiphens and spaces
    def removing_phone_non_digit_element(self, mobile_number):
        return re.sub(r'[/() -]', '', mobile_number)
    
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
    
    def sanitize_html(self, text) -> str:
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
    
    def is_alphanumeric(self, input: str) -> bool:
        try:
            reg = r'^[0-9a-zA-Z &@-]+$'
            if re.match(reg, input.lower()) and not self.check_for_special_characters(input):
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("is_alphanumeric: %s %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return False

    def is_filename_alphanumeric(self, input: str) -> bool:
        try:
            reg = r'^[0-9a-zA-Z @()_=-]+$'
            if re.match(reg, input.lower()) and not self.check_for_special_characters(input):
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("is_filename_alphanumeric: %s %s", str(
                e), str(exc_tb.tb_lineno), extra=self.extra)

        return False
