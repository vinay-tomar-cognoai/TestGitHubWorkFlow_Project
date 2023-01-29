from CampaignApp.utils import *
from CampaignApp.models import *
from EasyChatApp.models import WhatsAppVendorConfig
from django.conf import settings
from CampaignApp.utils_custom_encryption import CustomEncrypt
import emoji
import time
import json
import sys
import requests
import base64

# CHATBOT APP PHONE NUMBER CREDENTIALS
# domain = "https://cogno2.ameyo.net:9500"
# api_username = "admin"
# api_password = "s&uQ,22$U/gXG>Q4"

# CAMPAIGNAPP PHONE NUMBER CREDENTIALS
domain = "https://cognoai3.ameyo.net:9655"
api_username = "admin"
api_password = "Ameyo@1234"

#   GET AMEYO API KEY:
def get_jwt_token(username, password):
    global domain

    API_KEY = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJpYXQiOjE2NDM3MjExNzgsImV4cCI6MTY0NDMyNTk3OCwid2E6cmFuZCI6IjVmZDlhOGM4OGU5Yjc4MzUwMjgyNTczMGU1NDViZmZmIn0.D7ZqAGCioNVHGl1pOMYy9jW-UujNKakuXLq-zZpN5Oc"
    try:
        logger.info("=== Inside AMEYO_GET_API_KEY API ===",
                    extra={'AppName': 'Campaign'})
        url = domain + "/v1/users/login"

        userAndPass = base64.b64encode(
            (username+":"+password).encode()).decode("ascii")
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic '+userAndPass
        }
        logger.info("AMEYO_GET_API_KEY Headers: %s", str(
            headers), extra={'AppName': 'Campaign'})
        r = requests.request("POST", url, headers=headers,
                             timeout=25, verify=True)
        content = json.loads(r.text)
        logger.info("AMEYO_GET_API_KEY Response: %s", str(
            content), extra={'AppName': 'Campaign'})
        if str(r.status_code) == "200":
            if "users" in content and content["users"] != []:
                API_KEY = content["users"][0]["token"]
        logger.info("AMEYO_GET_API_KEY API Key generated: %s",
                    str(API_KEY), extra={'AppName': 'Campaign'})
    except requests.Timeout as RT:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AMEYO_GET_API_KEY Timeout error: %s at %s", str(
            RT), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AMEYO_GET_API_KEY Failed: %s at %s", str(
            E), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
    return API_KEY


# CACHING AMEYO API KEY:
def get_cached_jwt_token(username, password, vendor_object):
    API_KEY = None
    log_param = {'AppName': 'Campaign'}
    try:
        logger.info(
            "=== Inside get_cached_jwt_token GET_AMEYO_JWT_TOKEN ===", extra=log_param)

        token_obj = vendor_object
        pytz_timezone = pytz.timezone(settings.TIME_ZONE)
        current_datetime_obj = timezone.now().astimezone(pytz_timezone)

        if token_obj.dynamic_token == None or token_obj.dynamic_token == "" or token_obj.dynamic_token == "token":
            API_KEY = get_jwt_token(username, password)
            token_obj.dynamic_token = API_KEY
            token_obj.token_updated_on = current_datetime_obj
            token_obj.save()
        else:
            token_last_created_time = token_obj.token_updated_on + \
                timedelta(days=token_obj.dynamic_token_refresh_time)
            token_datetime_obj = token_last_created_time.astimezone(
                pytz_timezone)

            API_KEY = token_obj.dynamic_token
            if token_datetime_obj < current_datetime_obj:
                API_KEY = get_jwt_token(username, password)
                token_obj.dynamic_token = API_KEY
                token_obj.token_updated_on = current_datetime_obj
                token_obj.save()

    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("GET_CACHED_AMEYO_JWT_TOKEN API  Failed: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)

    logger.info(
        "=== END get_cached_jwt_token GET_AMEYO_JWT_TOKEN ===", extra=log_param)
    return API_KEY


def get_payload_body_media(variable):
    try:
        body = {"type": "body"}

        body["parameters"] = []
        for value in variable:
            body["parameters"].append({"type": "text", "text": value})

        return body
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: get_payload_body_media: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def get_payload_body(variable):
    try:
        body = []
        for value in variable:
            body.append({'text': value})

        return body
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: get_payload_body: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def get_payload_cta_reply(cta_variables, type_of_first_cta_btton):
    try:
        param_dict = {}
        cta_count = 0
        if type_of_first_cta_btton == 'call_us':
            cta_count = 1
        for cta_var in cta_variables:
            param_dict = {
                "type": "button",
                "sub_type": "url",
                "index": cta_count,
                "parameters": [
                        {
                            "type": "text",
                            "text": cta_var
                        }
                ]
            }
        return param_dict
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: get_payload_cta_reply: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
    return param_dict


def get_payload_of_header(media_type, context, document_file_name=""):
    try:
        content = None
        if media_type == 'text':
            content = context
        else:
            content = {"link": context}
            if media_type == 'document':
                content["filename"] = document_file_name

        param_dict = {
                        "type": "header",
                        "parameters": [
                            {
                                "type": media_type,
                                media_type: content
                            }
                        ]
                    }
        return param_dict
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: get_payload_cta_reply: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
    return param_dict


def getTextPayload(mobile_number, template_name, language, variables, header_variable, cta_variables, type_of_first_cta_btton, namespace, language_policy="deterministic"):
    log_param = {'AppName': 'Campaign', 'user_id': 'None',
                 'source': 'en', 'channel': 'WhatsApp', 'bot_id': 'None'}
    try:
        logger.info("inside getTextPayload", extra=log_param)

        payload = {
            "to": mobile_number,
            "type": "template",
            "template": {
                "namespace": namespace,
                "name": template_name,
                "language": {
                    "policy": language_policy,
                    "code": language
                },
                "components": []
            }
        }
        for header_text in header_variable:
            payload['template']['components'].append(get_payload_of_header("text", header_text))

        if len(variables) != 0:
            param_dict = {"type": "body", "parameters": []}
            for var in variables:
                if var.strip() != "":
                    var_dict = {}
                    var_dict["type"] = "text"
                    var_dict["text"] = var
                    param_dict["parameters"].append(var_dict)
            payload['template']['components'].append(param_dict)
        
        if len(cta_variables) != 0:
            payload['template']['components'].append(get_payload_cta_reply(cta_variables, type_of_first_cta_btton))

        logger.info("TextPayload: %s", str(payload), extra=log_param)

        return json.dumps(payload)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: gettextPayload: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def getMediaPayload(mobile_number, template_name, language, variable, link, media_type, cta_variables, type_of_first_cta_btton, namespace, document_file_name, language_policy="deterministic"):
    try:
        if media_type != "" and media_type.lower() in ["image", "video", "document"] and link != "":

            payload = {
                "to": mobile_number,
                "recipient_type": "individual",
                "type": "template",
                "template": {
                    "namespace": namespace,
                    "name": template_name,
                    "language": {
                        "code": language,
                        "policy": language_policy
                    },
                    "components": []
                }
            }
            payload['template']['components'].append(get_payload_of_header(media_type, link, document_file_name))

            if len(variable) != 0:
                payload['template']['components'].append(
                    get_payload_body_media(variable))
            
            if len(cta_variables) != 0:
                payload['template']['components'].append(get_payload_cta_reply(cta_variables, type_of_first_cta_btton))

            logger.info(payload, extra={'AppName': 'Campaign'})

            return json.dumps(payload)
        else:
            logger.error("Error: getMediaPayload: Not valid media type %s",
                         media_type, extra={'AppName': 'Campaign'})
            return json.dumps({})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: getMediaPayload: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def getQuickReplyPayload(mobile_number, template_name, language, variable, media_link, namespace):
    try:
        logger.error("Starts here", extra={'AppName': 'Campaign'})
        variable_payload = []

        for item in variable:
            temp_dict = {"type": "text", "text": item}
            variable_payload.append(temp_dict)
        logger.error(variable_payload, extra={'AppName': 'Campaign'})
        payload = {
            "to": mobile_number,
            "type": "template",
            "template": {
                    "namespace": namespace,
                    "name": template_name,
                    "language": {
                        "policy": "deterministic",
                        "code": language
                    },
                "components": [
                        {
                            "type": "button",
                            "sub_type": "quick_reply",
                            "index": "1",
                            "parameters": [
                                    {
                                        "type": "payload",
                                        "payload": ""
                                    }
                            ]
                        }
                        ],
                "components": [
                        {
                            "type": "body",
                            "parameters": variable_payload
                        }
                        ]
            }
        }
        logger.info(payload, extra={'AppName': 'Campaign'})
        logger.error(payload, extra={'AppName': 'Campaign'})
        return json.dumps(payload)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: getQuickReplyPayload: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def getCTAPayload(mobile_number, template_name, language, variables, namespace, cta_variables=[], media_type="", media_link="", language_policy="deterministic"):
    log_param = {'AppName': 'Campaign', 'user_id': 'None',
                 'source': 'en', 'channel': 'WhatsApp', 'bot_id': 'None'}
    try:
        logger.info("inside getCTAPayload", extra=log_param)
        logger.info("inside getMediaPayload cta_variables: %s",
                    str(cta_variables), extra=log_param)

        payload = {
            "to": mobile_number,
            "type": "template",
            "template": {
                "namespace": namespace,
                "name": template_name,
                "language": {
                    "policy": language_policy,
                    "code": language
                }
            }
        }

        is_cta_media = False
        if media_type != "" and media_type.lower() in ["image", "video", "document"] and media_link != "":
            is_cta_media = True

        if len(variables) != 0 or len(cta_variables) != 0 or is_cta_media == True:
            payload['template']['components'] = []
            if len(variables) != 0:
                param_dict = {"type": "header", "parameters": []}
                for var in variables:
                    if var.strip() != "":
                        var_dict = {}
                        var_dict["type"] = "text"
                        var_dict["text"] = var
                        param_dict["parameters"].append(var_dict)
                payload['template']['components'].append(param_dict)
            if len(cta_variables) != 0:
                cta_count = 0
                for cta_var in cta_variables:
                    param_dict = {
                        "type": "button",
                        "sub_type": "url",
                        "index": cta_count,
                        "parameters": [
                                {
                                    "type": "text",
                                    "text": cta_var
                                }
                        ]
                    }
                    payload['template']['components'].append(param_dict)
                    cta_count += 1
            if is_cta_media == True:
                param_dict = {
                    "type": "header",
                    "parameters": [
                            {
                                "type": media_type,
                                media_type: {
                                    "link": media_link
                                }
                            }
                    ]
                }
                payload['template']['components'].append(param_dict)

        logger.info("getCTAPayload: %s", str(payload), extra=log_param)
        return json.dumps(payload)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: getCTAPayload: %s for %s", str(e),
                     str(exc_tb.tb_lineno), extra=log_param)


def sendWhatsAppMessage(payload, api_key):
    ''' A function to call send whatsapp text message API.'''
    import requests
    import urllib

    global domain

    try:
        JWT_TOKEN = api_key

        url = domain + "/v1/messages"
        headers = {
            "Authorization": "Bearer " + JWT_TOKEN,
            "Content-Type": "application/json"
        }

        logger.info(payload, extra={'AppName': 'Campaign'})

        resp = requests.post(url=url, data=payload, headers=headers)
        resp = json.loads(resp.text)

        logger.info(resp, extra={'AppName': 'Campaign'})

        if "messages" in resp and resp["messages"][0] and "id" in resp["messages"][0]:
            resp["request_id"] = resp["messages"][0]["id"]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: sendWhatsAppMessage: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
    return resp


def check_mobile_number_capability(JWT_TOKEN, mobile_number):
    log_param = {'AppName': 'Campaign', 'user_id': 'None',
                 'source': 'en', 'channel': 'WhatsApp', 'bot_id': 'None'}
    import requests
    capable = False
    check_success = False

    global domain

    try:
        url = domain + "/v1/contacts"

        payload = {
            "blocking": "wait",
            "contacts": [
                "+"+mobile_number
            ],
            "force_check": False
        }
        headers = {
            "Authorization": "Bearer " + JWT_TOKEN,
            "Content-Type": "application/json"
        }
        logger.info("check_mobile_number_capability URL: %s",
                    str(url), extra=log_param)
        logger.info("check_mobile_number_capability Headers: %s",
                    str(headers), extra=log_param)
        logger.info("check_mobile_number_capability Payload: %s",
                    str(payload), extra=log_param)
        resp = requests.post(url=url, data=json.dumps(
            payload), headers=headers, timeout=25)
        logger.info("check_mobile_number_capability Response: %s",
                    str(resp.text), extra=log_param)

        if str(resp.status_code) == "200":
            resp = json.loads(resp.text)
            if "contacts" in resp and resp["contacts"] != []:
                contact_details = resp["contacts"][0]
                check_success = True
                if contact_details["status"] == "valid" and "wa_id" in contact_details:
                    mobile_number = contact_details["wa_id"]
                    capable = True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: check_mobile_number_capability: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra=log_param)
    return mobile_number, capable, check_success


def get_api_key(api_username, api_password):
    global domain
    try:
        vendor_object = None
        try:
            vendor_object = WhatsAppVendorConfig.objects.get(
                session_api_host=domain)
        except Exception:
            vendor_object = WhatsAppVendorConfig.objects.create(wsp_name="1", username=api_username, password=api_password, session_api_host=domain)
 
        if vendor_object == None or len(vendor_object.dynamic_token.strip()) < 100:
            ameyo_api_key = get_jwt_token(
                api_username, api_password)
            
            if vendor_object:
                vendor_object.dynamic_token = ameyo_api_key
                vendor_object.token_updated_on = timezone.now()
                vendor_object.save()
        else:
            ameyo_api_key = get_cached_jwt_token(
                api_username, api_password, vendor_object)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: get_api_key: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
    return ameyo_api_key


def f(x):
    '''
    Format of x:
    x = {
        "mobile_number": '',
        "template": {
            'name': '',
            'type': '',
            'message':'',
            'language': '',
            'link': '',
            'cta_text': ''.
            'cta_link': '',
        },
        "user_details" : [],
        "variables": [],
        "header_variable": [],
        "type_of_first_cta_btton": '',
        "dynamic_cta_url_variable": [],
        "namespace": '',
    }
    '''
    global api_username, api_password

    response = {}
    response['status'] = 500
    response['status_message'] = 'Your request was not executed successfully. Please try again later.'

    try:
        logger.info('x ki value kya h1: %s', str(x),
                    extra={'AppName': 'Campaign'})
        x = json.loads(x)
        response['request'] = x
        logger.info('x ki value kya h2: %s', str(x),
                    extra={'AppName': 'Campaign'})
        response["print"] = str(x)

        if bool(x):
            variable = x['variables']
            dynamic_cta_url_variable = x['dynamic_cta_url_variable']
            type_of_first_cta_btton = x['type_of_first_cta_btton']
            header_variable = x['header_variable']
            log_param = {'AppName': 'Campaign', 'user_id': 'None',
                         'source': 'en', 'channel': 'WhatsApp', 'bot_id': 'None'}
            phone_number = str(x['mobile_number'])
            namespace = str(x['namespace']).strip()
            document_file_name = str(x["document_file_name"]).strip()
            if namespace == "":
                namespace = "6a0e3db4_1820_4ad2_bfa3_200b1c487c98"

            api_key = x['api_key']
            if not api_key:
                api_key = get_api_key(api_username, api_password)

            """ Commenting check_mobile_number_capability() part since we dont allow invalid format numbers now
            logger.info('phone_number: %s', str(phone_number),
                        extra={'AppName': 'Campaign'})
            phone_number, capable, check_success = check_mobile_number_capability(
                api_key, phone_number)
            if check_success == False:
                response["status_message"] = "Failed to check mobile number capability. Please report this error."
                mobile_failure_response = {"errors": [{"code": 500, "title": "Failed to check mobile number capability",
                                                       "details": "Failed to check mobile number capability. Please report this error."}]}
                response['response'] = mobile_failure_response
                return response
            else:
                if capable == False:
                    response["status_code"] = 403
                    mobile_failure_response = {"errors": [{"code": 403, "title": "Mobile Number not available",
                                                           "details": "Mobile Number not available on WhatsApp to receive the message."}]}
                    response["status_message"] = "Mobile Number not available on WhatsApp to receive the message."
                    response['response'] = mobile_failure_response
                    return response
            """
            
            logger.info('phone_number: %s', str(phone_number), extra=log_param)
            if 'text' in x['template']['type'].lower():
                payload = getTextPayload(
                    phone_number, x['template']['name'], x['template']['language'], variable, header_variable, dynamic_cta_url_variable, type_of_first_cta_btton, namespace)
            elif x['template']['type'].lower() in ["image", "video", "document"]:
                payload = getMediaPayload(phone_number, x['template']['name'], x['template']
                                          ['language'], variable, x['template']['link'], x['template']['type'].lower(), dynamic_cta_url_variable, type_of_first_cta_btton, namespace, document_file_name)
            elif 'quick reply' in x['template']['type'].lower():
                payload = getQuickReplyPayload(
                    phone_number, x['template']['name'], x['template']['language'], variable, x['template']['link'], namespace)
            elif 'call to action' in x['template']['type'].lower():
                payload = getCTAPayload(
                    phone_number, x['template']['name'], x['template']['language'], variable, namespace, cta_variables=dynamic_cta_url_variable)

            response['request'] = json.loads(payload)
            logger.info(payload, extra={'AppName': 'Campaign'})
            response['response'] = sendWhatsAppMessage(payload, api_key)

        response['status'] = 200
        response['status_message'] = 'success'
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside api integration code: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
        
        detailed_error = 'ERROR :-  ' + \
            str(e) + ' at line no: ' + str(exc_tb.tb_lineno) + ' in the webhook. Please check, it looks like some internal error. Try updating the webhook or contact with the service provider.'
        response['status_message'] = detailed_error
        
        response['response'] = {"errors": [{"code": 500, "title": "Internal Server Error in the webhook code!", 
                                "details": detailed_error}]}

    return response
