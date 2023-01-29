from django.conf import settings

import os
import re
import sys
import json
import xlrd
import time
import base64
import logging
import requests

from TestingApp.html_parser import strip_html_tags
from TestingApp.encrypt import CustomEncrypt, generate_random_key
from TestingApp.constants import APP_NAME

logger = logging.getLogger(__name__)


def remo_html_from_string(raw_str):
    try:
        regex_cleaner = re.compile('<.*?>')
        cleaned_raw_str = re.sub(regex_cleaner, '', raw_str)
        return cleaned_raw_str.strip()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("remo_html_from_string: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})
        return raw_str.strip()


def check_malicious_file_from_filename(filename):
    allowed_files_list = [
        "png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg",
        "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt",
        "flv", "swf", "avchd", "mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip"
    ]

    try:
        if len(filename.split('.')) != 2:
            return True

        if filename.split('.')[-1] not in allowed_files_list:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_malicious_file_from_filename: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})
        return True


def validate_testcase_excel_sheet(qa_bot_testcase, BotQATestCase, BotQATestCaseFlow):
    try:
        testcase_file_path = qa_bot_testcase.uploaded_excel
        testcase_file_obj = open(testcase_file_path, "r")
        testcase_file_content = testcase_file_obj.read()
        testcase_file_content = testcase_file_content.split("\n")

        matrix_data = []
        for testcase_row in testcase_file_content:
            testcase_row = testcase_row.split(",")
            testcase_row_cell = [cell.strip() for cell in testcase_row]
            matrix_data.append(testcase_row_cell)

        total_rows = len(matrix_data)

        if len(matrix_data) >= 2:

            flow_list, total_number_of_flows = [], len(matrix_data[0]) - 1

            for index in range(1, total_number_of_flows + 1):

                flow_dict, is_flow_ended, row = {}, False, 2
                flow_dict["flow"] = matrix_data[0][index]
                flow_dict["intent_pk"] = matrix_data[1][index]
                flow_dict["serial_inputs"] = []

                while not is_flow_ended:
                    flow_dict["serial_inputs"].append(matrix_data[row][index])
                    row += 1
                    if row >= total_rows:
                        is_flow_ended = True
                    elif matrix_data[row][index] == "":
                        is_flow_ended = True

                BotQATestCaseFlow.objects.create(qa_testcase=qa_bot_testcase,
                                                 parsed_json=json.dumps(flow_dict))

                flow_list.append(flow_dict)

            qa_bot_testcase.parsed_json = json.dumps(flow_list)
            qa_bot_testcase.is_parsed = True
            qa_bot_testcase.save()
            return flow_list
        else:
            return None
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("validate_testcase_excel_sheet: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

    return None


def execute_bot_query(qa_testcase_flow_obj, message):
    error = None
    try:
        start_time = time.time()

        qa_testcase = qa_testcase_flow_obj.qa_testcase

        bot_id = qa_testcase.bot.bot_id

        bot_domain = qa_testcase.bot.bot_domain

        user_id = "QAAutomationToolUser" + \
            str(qa_testcase.bot.pk) + str(qa_testcase.pk) + \
            str(qa_testcase_flow_obj.pk)

        chatbot_query_url = bot_domain + "/chat/webhook/automation/query/"

        logger.info("chatbot_query_url: %s", chatbot_query_url,
                    extra={'AppName': APP_NAME})

        params = {
            "bot_id": str(bot_id),
            "user_id": user_id,
            "message": message,
            "channel": "Web",
            "channel_params": "{}"
        }

        logger.info("params: %s", json.dumps(
            params), extra={'AppName': APP_NAME})

        response = requests.post(url=chatbot_query_url, data=json.dumps(
            params), headers={"Content-Type": "application/json"}, timeout=settings.QUERY_API_TIMEOUT)

        end_time = time.time()

        logger.info("Total execution time: %s", str(
            end_time - start_time), extra={'AppName': APP_NAME})
        logger.info("Response: %s", response.text, extra={'AppName': APP_NAME})

        return json.loads(response.text)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("execute_bot_query: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})
        error = str(e)

    response = {}
    response["internal_status"] = 500
    response["error"] = error
    return response


def execute_testcase_flow(qa_testcase_flow_obj):
    try:
        parsed_json = json.loads(qa_testcase_flow_obj.parsed_json)
        serial_inputs = parsed_json["serial_inputs"]
        is_flow_testing_failed = False

        minimized_output_flow = []
        output_flow = []

        for input_message in serial_inputs:

            query_response = execute_bot_query(
                qa_testcase_flow_obj, input_message)

            output_flow.append({
                "query": input_message,
                "output": query_response
            })

            if "internal_status" in query_response and query_response["internal_status"] == 500:
                is_flow_testing_failed = True
                minimized_output_flow.append({
                    "query": input_message,
                    "output": {
                        "text_response": query_response["error"],
                        "recommendations": [],
                        "choices": []
                    }
                })
                break
            else:
                minimized_output_flow.append({
                    "query": input_message,
                    "output": {
                        "text_response": query_response["response"]["text_response"]["text"],
                        "recommendations": query_response["response"]["recommendations"],
                        "choices": query_response["response"]["choices"]
                    }
                })

        qa_testcase_flow_obj.output_flow = json.dumps(output_flow, indent=4)
        qa_testcase_flow_obj.minimized_output_flow = json.dumps(
            minimized_output_flow, indent=4)
        qa_testcase_flow_obj.is_flow_tested = True
        qa_testcase_flow_obj.is_flow_testing_failed = is_flow_testing_failed
        qa_testcase_flow_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("execute_testcase_flow: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})


# def sso_pre_login_check(user_params):
#     try:
#         email_id = user_params["EmailID"][0]
#         user_obj = User.objects.get(username=email_id)

#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("sso_pre_login_check: error %s at %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})


def test_automation_query_api(qa_bot_obj, message):
    try:
        start_time = time.time()

        bot_id = qa_bot_obj.bot_id

        bot_domain = qa_bot_obj.bot_domain

        user_id = "QAAutomationToolUser" + str(qa_bot_obj.pk)

        chatbot_query_url = bot_domain + "/chat/webhook/automation/query/"

        logger.info("chatbot_query_url: %s", chatbot_query_url,
                    extra={'AppName': APP_NAME})

        params = {
            "bot_id": str(bot_id),
            "user_id": user_id,
            "message": message,
            "channel": "Web",
            "channel_params": "{}"
        }

        logger.info("params: %s", json.dumps(
            params), extra={'AppName': APP_NAME})

        response = requests.post(url=chatbot_query_url, data=json.dumps(
            params), headers={"Content-Type": "application/json"}, timeout=settings.QUERY_API_TIMEOUT)

        end_time = time.time()

        logger.info("Total execution time: %s", str(
            end_time - start_time), extra={'AppName': APP_NAME})

        if response.status_code == 200:
            query_response = json.loads(response.text)
            if str(query_response["status_code"]) == "200":
                return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("test_automation_query_api: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

    return False
