APP_NAME = "AutomatedAPIApp"

API_TREE_DEFAULT_CALL = """from EasyChatApp.models import * 
result_dict = {}

try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=202)) 
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 

import requests
from EasyChatApp.utils import logger
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
from requests_oauthlib import OAuth1

import sys

def f():
    response = {}
    response['status_code'] = 500
    response['status_message'] = 'Internal server error.'
    response['data'] = {}
    response['cards'] = []
    response['choices'] = []
    response['images'] = []
    response['videos'] = []
    response['recommendations'] = []
    response['API_REQUEST_PACKET'] = {}
    response['API_RESPONSE_PACKET'] = {}
    global result_dict
    try:
        request_packet_list = []
        response_packet_list = []
{{/MULTIPLE_API_CODE/}}
        api_request_dict = {}
        
        for index, single_request_packet in enumerate(request_packet_list):
            api_request_dict["api_request_packet_" + str(index + 1)] = single_request_packet
    
        response['API_REQUEST_PACKET'] = api_request_dict

        api_response_dict = {}
        
        for index, single_response_packet in enumerate(response_packet_list):
            api_response_dict["api_response_packet_" + str(index + 1)] = single_response_packet
    
        response['API_RESPONSE_PACKET'] = api_response_dict
        # write your code here
        response['status_code'] = '200'
        response['status_message'] = 'success'
        response['api_response'] = api_response.text
        return response
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('ApiTreeContent: %s at %s',str(E), str(exc_tb.tb_lineno), 
            extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response"""

SINGLE_API_CODE = """\n        request_url = "{{/request_url/}}"
        request_type = "{{/request_type/}}"
        request_body = {{/request_body/}}
        request_header = {{/request_header/}}
        authorization = {{/request_authorization/}}

        {{/API_CALL/}}

        api_response_data = {}
        api_response_text = ""
        try:
            api_response_text = api_response.text
            api_response_data = json.loads(api_response.text)
        except Exception:
            pass
        {{/response_variables/}}

        if api_response.status_code == 200:
            print("write your success code here")
        else:
            print("write your failure code here")

        temp_request_dict = { 
            "url": request_url,
            "data": request_body,
            "header": request_header
        }
        request_packet_list.append(temp_request_dict)

        temp_response_dict = {
            "response": api_response_text
        }

        response_packet_list.append(temp_response_dict)

"""
