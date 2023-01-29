from CampaignApp.utils import *
from CampaignApp.models import *
from django.conf import settings
from CampaignApp.utils_custom_encryption import CustomEncrypt
import emoji
import time
import json
import sys
import requests


def get_jwt_token():
    url = "https://apis.rmlconnect.net/auth/v1/login/"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "username": "RMLBot2",
        "password": "Product@123"
    }

    resp = requests.post(url=url, headers=headers, data=json.dumps(payload))
    api_resp = json.loads(resp.text)
    JWT_TOKEN = api_resp["JWTAUTH"]
    return JWT_TOKEN


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


def getTextPayload(mobile_number, template_name, language, variable):
    try:
        logger.info(template_name, extra={'AppName': 'Campaign'})
        logger.info(variable, extra={'AppName': 'Campaign'})

        payload = {
            "phone": mobile_number,
            "extra": "na",
            "media": {
                "type": "media_template",
                "template_name": template_name,
                "lang_code": language,
            }
        }

        if len(variable) != 0:
            payload['media']['body'] = get_payload_body(variable)

        logger.info(payload, extra={'AppName': 'Campaign'})

        return json.dumps(payload)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: getTextPayload: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def getImagePayload(mobile_number, template_name, language, variable, link):
    try:
        payload = {
            "phone": mobile_number,
            "extra": "na",
            "media": {
                "type": "media_template",
                "template_name": template_name,
                "lang_code": language,
                "header": [
                    {
                        "image": {
                            "link": link,
                        }
                    }
                ],
            }
        }

        if len(variable) != 0:
            payload['media']['body'] = get_payload_body(variable)

        logger.info(payload, extra={'AppName': 'Campaign'})

        return json.dumps(payload)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: getImagePayload: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def getVideoPayload(mobile_number, template_name, language, variable, link):
    try:
        payload = {
            "phone": mobile_number,
            "extra": "na",
            "media": {
                "type": "media_template",
                "template_name": template_name,
                "lang_code": language,
                "header": [
                    {
                        "video": {
                            "link": link,
                        }
                    }
                ],
            }
        }

        if len(variable) != 0:
            payload['media']['body'] = get_payload_body(variable)

        logger.info(payload, extra={'AppName': 'Campaign'})

        return json.dumps(payload)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: getVideoPayload: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def getDocumentPayload(mobile_number, template_name, language, variable, link):
    try:
        payload = {
            "phone": mobile_number,
            "extra": "na",
            "media": {
                "type": "media_template",
                "template_name": template_name,
                "lang_code": language,
                "header": [
                    {
                        "document": {
                            "link": link,
                        }
                    }
                ],
            }
        }

        if len(variable) != 0:
            payload['media']['body'] = get_payload_body(variable)

        logger.info(payload, extra={'AppName': 'Campaign'})

        return json.dumps(payload)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: getDocumentPayload: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def getCTAPayload(mobile_number, template_name, language, variable, cta_text, cta_link):
    try:
        payload = {
            "phone": mobile_number,
            "extra": "na",
            "media": {
                "type": "call_to_action",
                "template_name": template_name,
                "lang_code": language,
                "button": [
                  {
                     "button_no": "0",
                     "url": "https://wbs.rmlconnect.net/#e492b7c4-0add-4cf0-877b-96c73df9e844"
                  },
                    {
                      "button_no": "1",
                      "url": "https://wbs.rmlconnect.net/#e492b7c4-0add-4cf0-877b-96c73df9e844"
                  },
                ]
            },
        }

        if len(variable) != 0:
            payload['media']['body'] = get_payload_body(variable)

        logger.info(payload, extra={'AppName': 'Campaign'})

        return json.dumps(payload)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: getCTAPayload: %s for %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def sendWhatsAppMessage(payload):
    ''' A function to call send whatsapp text message API.'''
    import requests
    import urllib
    try:
        JWT_TOKEN = get_jwt_token()

        url = "https://apis.rmlconnect.net/wba/v1/messages"
        headers = {
            "Authorization": JWT_TOKEN,
            "Content-Type": "application/json"
        }

        logger.info(payload, extra={'AppName': 'Campaign'})

        resp = requests.post(url=url, data=payload, headers=headers)
        resp = json.loads(resp.text)

        logger.info(resp, extra={'AppName': 'Campaign'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: sendWhatsAppMessage: %s for %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
    return resp


def f(x):
    '''
    Format of x:
    x = {
        "mobile_number": '',
        "template": {
            'name': '',
            'type': '',
            'language': '',
            'link': '',
            'cta_text': ''.
            'cta_link': '',
        },
        "user_details" : [],
        "variables": [],
    }
    '''

    response = {}
    response['status'] = 500
    response['status_message'] = 'Your request was not executed successfully. Please try again later.'
    try:
        x = json.loads(x)

        if bool(x):
            variable = x['variables']

            phone_number = str(x['mobile_number'])
            phone_number = phone_number[-10:]
            phone_number = "+91" + str(phone_number)

            logger.info('phone_number: %s', str(phone_number),
                        extra={'AppName': 'Campaign'})

            if 'text' in x['template']['type'].lower():
                payload = getTextPayload(
                    phone_number, x['template']['name'], x['template']['language'], variable)
            elif 'image' in x['template']['type'].lower():
                payload = getImagePayload(
                    phone_number, x['template']['name'], x['template']['language'], variable, x['template']['link'])
            elif 'document' in x['template']['type'].lower():
                payload = getDocumentPayload(
                    phone_number, x['template']['name'], x['template']['language'], variable, x['template']['link'])
            elif 'call to action' in x['template']['type'].lower():
                payload = getCTAPayload(phone_number, x['template']['name'], x['template']
                                        ['language'], variable, x['template']['cta_text'], x['template']['cta_link'])

            response['request'] = payload
            response['response'] = sendWhatsAppMessage(payload)

        response['status'] = 200
        response['status_message'] = 'success'

        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside api integration code: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
        response['status_message'] = 'ERROR :-  ' + \
            str(e) + ' at line no: ' + str(exc_tb.tb_lineno)
        response['response'] = {'status': 'failed'}

    return response
