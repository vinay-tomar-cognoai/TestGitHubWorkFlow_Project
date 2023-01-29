from EasyChatApp.constants import *
from AutomatedAPIApp.constants import *
from EasyChatApp.utils import is_allowed
from AutomatedAPIApp.encrypt import CustomEncrypt

import sys
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
from requests_oauthlib import OAuth1
import re

import logging

logger = logging.getLogger(__name__)


def reverse_tree_objects(tree_obj, tree_objs, Tree):
    try:
        parent_tree_list = tree_obj.tree_set.all()

        if parent_tree_list.count() == 0:
            return

        for parent_tree in parent_tree_list:
            tree_objs.append(parent_tree)
            reverse_tree_objects(parent_tree, tree_objs, Tree)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("reverse_tree_objects: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})


def get_tree_associated_automated_api_integration_obj(tree_obj, Tree, AutomatedAPIIntegration):
    automated_api_integration_obj = None
    try:
        automated_api_integration_obj = AutomatedAPIIntegration.objects.get(
            tree=tree_obj)
    except Exception:
        automated_api_integration_obj = AutomatedAPIIntegration.objects.create(
            tree=tree_obj)

    return automated_api_integration_obj


def generate_automated_api_integration_code(automated_api_obj):

    def api_response_variable_pattern_header_auth(regex_obj):
        try:
            raw_data = regex_obj.group()
            return raw_data[3: -3]
        except Exception:
            return None

    def api_response_variable_pattern_body(regex_obj):
        try:
            raw_data = regex_obj.group()
            raw_data = raw_data[2: -2]
            raw_data = "\\\"\"\"\" + " + raw_data + " + \"\"\"\\\""
            return raw_data
        except Exception:
            return None

    def api_response_variable_pattern_url(regex_obj):
        try:
            raw_data = regex_obj.group()
            raw_data = raw_data[2: -2]
            raw_data = "\" + " + raw_data + " + \""
            return raw_data
        except Exception:
            return None

    try:
        request_url = automated_api_obj.request_url
        request_url = re.sub(
            r"({{([^}]*)}})", api_response_variable_pattern_url, request_url)

        request_type = automated_api_obj.request_type
        request_body = automated_api_obj.request_packet

        request_body = re.sub(
            r"({{([^}]*)}})", api_response_variable_pattern_body, request_body)

        request_header = automated_api_obj.headers
        request_authorization = json.loads(automated_api_obj.authorization)

        api_call = ""

        if request_authorization["type"] == "bearer-token":
            api_call = """
        request_header["Authorization"] = "Bearer " + authorization["params"]["token"]

        api_response = requests.request(request_type,
                                        url=request_url,
                                        data=request_body,
                                        headers=request_header,
                                        timeout=10)
            """
        elif request_authorization["type"] == "basic-auth":
            api_call = """
        username = authorization["params"]["username"]
        password = authorization["params"]["password"]
        api_response = requests.request(request_type,
                                        url=request_url,
                                        data=request_body,
                                        headers=request_header,
                                        auth=HTTPBasicAuth(username, password),
                                        timeout=10)
            """
        elif request_authorization["type"] == "digest-auth":
            api_call = """
        username = authorization["params"]["username"]
        password = authorization["params"]["password"]

        api_response = requests.request(request_type,
                                        url=request_url,
                                        data=request_body,
                                        headers=request_header,
                                        auth=HTTPDigestAuth(username, password),
                                        timeout=10)
            """
        elif request_authorization["type"] == "oauth-1.0-auth":
            api_call = """
        consumer_key = authorization["params"]["consumer-key"]
        consumer_secret = authorization["params"]["consumer-secret"]
        access_token = authorization["params"]["access-token"]
        token_secret = authorization["params"]["token-secret"]

        api_response = requests.request(request_type,
                                        url=request_url,
                                        data=request_body,
                                        headers=request_header,
                                        auth=OAuth1(consumer_key, consumer_secret, access_token, token_secret),
                                        timeout=10)
            """
        else:
            api_call = """
        api_response = requests.request(request_type,
                                        url=request_url,
                                        data=request_body,
                                        headers=request_header,
                                        timeout=10)
            """

        response_variables = json.loads(automated_api_obj.variables)
        response_variables_save = ""

        for key, value in response_variables.items():
            response_variables_save += """
        {key} = None
        try:
            {key} = {value}
        except Exception:
            pass
            """.format(key=key, value=value)
            # response_variables_save += "\n        " + key + " = " + value + " if " + key + " in api_response_data else None"

        data = SINGLE_API_CODE

        if not is_content_type_x_url_form_encoded(request_header):
            request_body = request_body.strip()
            request_body = '\"""' + request_body + '\"""'

        data = data.replace("{{/request_url/}}", request_url)
        data = data.replace("{{/request_type/}}", request_type)
        data = data.replace("{{/request_body/}}", request_body)
        data = data.replace("{{/request_header/}}", request_header)
        data = data.replace("{{/request_authorization/}}",
                            json.dumps(request_authorization))
        data = data.replace("{{/response_variables/}}",
                            response_variables_save)
        data = data.replace("{{/API_CALL/}}", api_call)

        data = re.sub(r"(\"{{([^}]*)}}\")",
                      api_response_variable_pattern_header_auth, data)

        return data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("generate_automated_api_integration_code: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

    return None


def generate_automated_api_integration_code_recursive(automated_api_obj):
    try:
        if automated_api_obj == None:
            return None
        if automated_api_obj.next_api == None:
            return generate_automated_api_integration_code(automated_api_obj)
        else:
            return generate_automated_api_integration_code(automated_api_obj) + generate_automated_api_integration_code_recursive(automated_api_obj.next_api)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("generate_automated_api_integration_code_recursive: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})
    return None


def generate_automated_api_code(automated_api_integration_obj):
    try:
        multiple_api_code = generate_automated_api_integration_code_recursive(
            automated_api_integration_obj.initial_api)

        if multiple_api_code:
            data = API_TREE_DEFAULT_CALL
            data = data.replace("{{/MULTIPLE_API_CODE/}}", multiple_api_code)
        else:
            data = None
        return data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("generate_automated_api_code: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})
    return None


def get_function_name_list(automated_api_obj, index=1):
    def parse_automated_api():
        return {
            "index": index,
            "pk": automated_api_obj.pk,
        }

    try:
        if automated_api_obj == None:
            return []

        if automated_api_obj.next_api == None:
            return [parse_automated_api()]
        else:
            function_names = [parse_automated_api()]
            function_names += get_function_name_list(
                automated_api_obj.next_api, index + 1)
            return function_names
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_functions_name: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})
    return []


def get_automated_api_objs(automated_api_obj):
    try:
        if automated_api_obj == None:
            return []

        if automated_api_obj.next_api == None:
            return [automated_api_obj]
        else:
            automated_api_objs = [automated_api_obj]
            automated_api_objs += get_automated_api_objs(
                automated_api_obj.next_api)
            return automated_api_objs
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_automated_api_objs: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})
    return []


def get_automated_api_obj(automated_api_integration_obj, api_pk):
    try:
        automated_api_objs = get_automated_api_objs(
            automated_api_integration_obj.initial_api)

        for automated_api_obj in automated_api_objs:
            if automated_api_obj.pk == api_pk:
                return automated_api_obj

        return None
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_automated_api_obj: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})
    return None


"""
update_request_body_based_on_content_type
input params:
    request_body
    headers
output 
    request_body

update_request_body_based_on_content_type this function updates the request body from headers if content type is x-www-form-urlencoded
"""


def is_content_type_x_url_form_encoded(headers):
    try:
        if isinstance(headers, str):
            headers = json.loads(headers)

        if "Content-Type" in headers and headers["Content-Type"] == "application/x-www-form-urlencoded":
            return True

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("return_is_content_type_x_url_form_encoded: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'AutomatedApiAPP'})

    return False


def update_request_body_based_on_content_type(headers, request_body, is_updated_request_body_required_in_dict_format):
    new_header = headers
    try:
        if is_content_type_x_url_form_encoded(headers):
            request_body = headers
            new_header = {}
            if isinstance(request_body, str):
                request_body = json.loads(request_body)
            new_header["Content-Type"] = request_body.pop("Content-Type")

            if not is_updated_request_body_required_in_dict_format:
                request_body = json.dumps(request_body)
                
            if isinstance(headers, str):
                new_header = json.dumps(new_header)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_request_body_based_on_content_type: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'AutomatedApiAPP'})

    return request_body, new_header
