# flake8: noqa
from django.conf import settings

import re
import logging

compiled_regex = re.compile(settings.EASYCHAT_SENSITIVE_REGEX)

class SensitiveDataFilter(logging.Filter):

    def remove_easychat_sensitive_tags(self, message):
        modified_message = message
        try:
            modified_message = message.replace("<easychat:sensitive>", "")
            modified_message = modified_message.replace("</easychat:sensitive>", "")
        except Exception:
            pass

        return modified_message

    def replace(self, arg):
        try:
            sensitive_data = compiled_regex.findall(arg.group())[0][1]
            return "*"*len(sensitive_data)
        except Exception:
            return "*"*5

    def get_masked_data(self, message):
        final_string = message
        try:
            pat = "([a-zA-Z]){5}([0-9]){4}([a-zA-Z]){1}?"
            message = re.sub(pat, "**********", message)
            if re.search("\d+[A-Za-z]+|\d+:", message):
                return final_string
            pat = r"(^\d)((\d+((?:\,|)(?:\.|))+)+)"
            message = re.sub(pat, " **********", message)
            pat = r"([\s\"\'])((\d+((?:\,|)(?:\.|))+)+)"
            message = re.sub(pat, " **********", message)
            return message
        except Exception:
            return final_string


    def hide_sensitive_text(self, msg):
        try:
            sensitive_msg = re.sub(settings.EASYCHAT_SENSITIVE_REGEX, self.replace, msg)
            sensitive_msg = self.get_masked_data(sensitive_msg)
            return sensitive_msg
        except Exception:
            return msg

    def filter(self, record):
        record_message = record.msg
        record_args = record.args
        args = ()
        for arg in record_args:
            args+=(self.hide_sensitive_text(str(arg)),)
        record.msg = self.hide_sensitive_text(record_message)
        record.args = args
        return True
