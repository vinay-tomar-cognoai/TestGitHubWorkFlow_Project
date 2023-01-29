from EasyChatApp.constants_processor_validator import DEFAULT_POST_PROCESSOR_LIST
from EasyChatApp.models import Processor, ApiTree, FormWidgetFieldProcessor

import sys
import subprocess
import json
import execjs
import logging

logger = logging.getLogger(__name__)


def create_default_processor_validators(bot_obj, Processor, ProcessorValidator):
    try:
        if ProcessorValidator.objects.filter(bot=bot_obj).count() > 0:
            return

        processor_objs = []
        bot_name = bot_obj.slug

        for default_processor in DEFAULT_POST_PROCESSOR_LIST:
            processor_name = bot_name + "-" + default_processor["name"]
            processor_code = default_processor["processor"]
            processor_lang = default_processor["processor_lang"]

            processor_obj = Processor.objects.create(name=processor_name,
                                                     function=processor_code,
                                                     processor_lang=processor_lang)
            processor_objs.append({
                "name": default_processor["name"],
                "obj": processor_obj
            })

        for processor_dict in processor_objs:

            ProcessorValidator.objects.create(name=processor_dict["name"],
                                              bot=bot_obj,
                                              processor=processor_dict["obj"])
        logger.info("default processor validators created successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_default_processor_validators: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})


def check_duplicate_processor(name, original_processor_name, response, processor):
    try:
        if processor == "field":
            duplicate_processor_bool = FormWidgetFieldProcessor.objects.filter(
                name=name).exclude(name=original_processor_name.strip())
        elif processor != "api":
            duplicate_processor_bool = Processor.objects.filter(
                name=name).exclude(name=original_processor_name.strip())
        else:
            duplicate_processor_bool = ApiTree.objects.filter(
                name=name).exclude(name=original_processor_name.strip())

        if duplicate_processor_bool:
            response["status"] = 300
            response["message"] = "Duplicate name exists."
            return True, response
        else:
            return False, response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_duplicate_processor: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def execute_processor_java_code(cmd, username, parameter):
    try:
        curr_process = subprocess.run(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if curr_process.returncode == 0:
            cmd = "java -cp files/language_support/" + str(username) + "/ EasyChatConsole '" + \
                str(parameter) + "'"
            json_data = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if json_data.returncode == 0:
                cmd = "rm -rf files/language_support/" + \
                    str(username) + "/EasyChatConsole.class"
                subprocess.run(cmd, shell=True)
                json_data = (json_data.stdout).decode('utf-8')
                try:
                    json_data = json.loads(json_data)
                    response_status = 200
                except Exception:
                    json_data = "Some error during parsing."
                    response_status = 300
            else:
                json_data = (json_data.stderr).decode('utf-8')
                response_status = 300
        else:
            json_data = (curr_process.stderr).decode('utf-8')
            response_status = 300

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(" Error execute_processor_java_code: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return json_data, response_status


def execute_processor_python_code(code, open_file, processor, parameter):

    processor_check_dictionary = {'open': open_file}

    exec(str(code), processor_check_dictionary)

    if processor == "post":
        json_data = processor_check_dictionary['f'](parameter)
    elif processor == "pipe":
        json_data = processor_check_dictionary['f'](parameter)
    elif processor == "get_otp":
        json_data = processor_check_dictionary['f'](parameter)
    elif processor == "verify_otp":
        json_data = processor_check_dictionary['f'](parameter)
    elif processor == "field":
        json_data = processor_check_dictionary['f'](parameter)
    else:
        json_data = processor_check_dictionary['f']()
    return json_data


def execute_processor_php_code(code, username):
    try:

        php_file = open("files/language_support/" +
                        str(username) + "/EasyChatConsole.php", 'r+')
        php_file.write(code)
        php_file.close()

        cmd = "php files/language_support/" + \
            str(username) + "/EasyChatConsole.php"

        proc = subprocess.run(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if proc.returncode == 0:
            json_data = (proc.stdout).decode('utf-8')
            json_data = json.loads(json_data)
            response_status = 200
        else:
            json_data = (proc.stdout).decode('utf-8')
            response_status = 300

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(" Error execute_processor_php_code: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return json_data, response_status


def execute_processor_javascript_code(code, parameter):

    fun = execjs.compile(code)
    json_data = fun.call("f", parameter)

    return json_data
