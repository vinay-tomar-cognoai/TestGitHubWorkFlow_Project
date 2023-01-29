
CAMPAIGN_DRAFT = "draft"
CAMPAIGN_COMPLETED = "completed"
CAMPAIGN_IN_PROGRESS = "in_progress"
CAMPAIGN_PARTIALLY_COMPLETED = "partially_completed"
CAMPAIGN_SCHEDULED = "scheduled"
CAMPAIGN_SCHEDULE_COMPLETED = "schedule_completed"
CAMPAIGN_FAILED = "failed"
CAMPAIGN_ONGOING = "ongoing"
CAMPAIGN_PROCESSED = "processed"
CAMPAIGN_APP_MAX_TIMEOUT_LIMIT = 10
EXTERNAL_CAMPAIGN_AUTH_TOKEN_VALIDITY_HOURS = 24
EXTERNAL_CAMPAIGN_APP_MAX_TIMEOUT_LIMIT = 30
EXTERNAL_CAMPAIGN_MAXIMUM_AUDIENCE_BATCH_LIMIT = 40000
CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT = 5000
CAMPAIGN_MAXIMUM_AUDIENCE_BATCH_LIMIT = 1048575
CAMPAIGN_MAXIMUM_AUDIENCE_CSV_BATCH_LIMIT = 1048575
CAMPAIGN_MAXIMUM_SCROLLER_LIST_LIMIT = 100
CAMPAIGN_MAXIMUM_SHEET_UPLOAD_TIME_LIMIT = 6000
CAMPAIGN_MAXIMUM_SHEET_UPLOAD_TIME_CSV_LIMIT = 6000
CAMPAIGN_BOT_BSP_FOR_SQS = "1"  # 1 is set by default for Ameyo BSP.
CAMPAIGN_REPORT_MAX_ROWS = 500000

INPROGRESS_CAMPAIGN_ANALYTICS_SCHEDULAR_ID_CONSTANT = "update_inprogress_campaigns_analytics_service"
CAMPAIGN_ANALYTICS_SCHEDULAR_EXPIRY_TIME = 15  # In mins

CAMPAIGN_ANALYTICS_SCHEDULAR_ID_CONSTANT = "update_campaigns_analytics_service"

# Cache Key
CACHE_KEY_CAMPAIGN_BOT_WSP_CONFIG = "CAMPAIGN_BOT_WSP_CONFIG_"
CACHE_KEY_CAMPAIGN_BOT_WSP_CONFIG_OBJ = "CAMPAIGN_BOT_WSP_CONFIG_OBJ_"

OVERALL_DETAILS_SHEET_COLUMNS_LIST = ["Bot Name",
                                      "Campaign Name",
                                      "WhatsApp BSP",
                                      "Campaign Created on",
                                      "Open Rate",
                                      "Source",
                                      "Timezone",
                                      "Total Messages Submitted",
                                      "Sent",
                                      "Failed",
                                      "Delivered",
                                      "Read",
                                      "Replied",
                                      "Audience Batch Name",
                                      "Total Audience Batch Size",
                                      "Template Name",
                                      "Template Type",
                                      "Sent",
                                      "Failed",
                                      ]

OVERALL_TEST_DETAILS_SHEET_COLUMNS_LIST = ["Bot Name",
                                           "Campaign Name",
                                           "WhatsApp BSP",
                                           "Campaign Created on",
                                           "Open Rate",
                                           "Source",
                                           "Timezone",
                                           "Total Submitted",
                                           "Sent",
                                           "Failed",
                                           ]

DETAILED_SHEET_COLUMNS_LIST = ["Phone Number",
                               "Recipient ID",
                               "Sent Time",
                               "Delivered Time",
                               "Read Time",
                               "Reply Time",
                               "Quick Reply",
                               "Status",
                               "Issue",
                               "Failure Reason",
                               "Media URL",
                               "Message Payload",
                               "Response Body"
                               ]

WHATSAPP_AUDIENCE_SHEET_COLUMNS_LIST = ["Phone Number",
                                        "Recipient ID",
                                        "Status",
                                        "Message Type",
                                        "Template Name",
                                        "Failure Reason",
                                        "Quick Reply",
                                        "Sent Time",
                                        "Delivered Time",
                                        "Read Time"
                                        ]

WHATSAPP_TEST_AUDIENCE_SHEET_COLUMNS_LIST = ["Phone Number",
                                             "Recipient ID",
                                             "Template Name",
                                             "Template Type",
                                             "Sent Time",
                                             "Delivered Time",
                                             "Read Time",
                                             "Reply Time",
                                             "Quick Reply",
                                             "Status",
                                             "Issue",
                                             "Failure Reason",
                                             "Media URL",
                                             "Message Payload",
                                             "Response Body"
                                             ]

CAMPAIGN_STATUS = (
    (CAMPAIGN_DRAFT, "Draft"),
    (CAMPAIGN_COMPLETED, "Completed"),
    (CAMPAIGN_PARTIALLY_COMPLETED, "Completed!"),
    (CAMPAIGN_IN_PROGRESS, "In Progress"),
    (CAMPAIGN_SCHEDULED, "Scheduled"),
    (CAMPAIGN_FAILED, "Failed"),
    (CAMPAIGN_ONGOING, "Ongoing"),
    (CAMPAIGN_PROCESSED, "Processed"),
    (CAMPAIGN_SCHEDULE_COMPLETED, "Schedule Completed"),
)

EXPORT_CHOICES = (
    ('1', "Single Export"),
    ('2', "Multi Export"),
    ('3', "Single Date Range Export"),
    ('4', "Test Export")
)

CAMPAIGN_EVENT_CHOICES = (
    ('upload_batch', "Upload Batch"),
)

SCHEDULE_CHOICES = (
    ('does_not_repeat', "does_not_repeat"),
    ('daily', "daily"),
    ('weekly', "weekly"),
    ('monthly', "monthly"),
    ('annually', "annually"),
    ('weekend_or_weekday', "weekend_or_weekday"),
    ('custom', "custom"),
)

VOICE_CAMPAIGN_CALL_STATUS = (
    ('completed', "Completed"),
    ('failed', 'Failed'),
    ('rejected', 'Rejected'),
    ('connected', 'Connected'),
)

CAMPAIGN_BASIC_INFO_STATE = "basic_info"
CAMPAIGN_TAG_AUDIENCE_STATE = "tag_audience"
CAMPAIGN_TEMPLATE_STATE = "template"
CAMPIGN_REVIEW_STATE = "review"
CAMPAIGN_SETTINGS_STATE = "trigger_settings"
CAMPAIGN_VB_REVIEW_STATE = "vb_review"

CAMPAIGN_DOCUMENT_FILE_NAME = "document"

CAMPAIGN_LAST_SAVED_STATES = (
    (CAMPAIGN_BASIC_INFO_STATE, "basic_info"),
    (CAMPAIGN_TAG_AUDIENCE_STATE, "tag_audience"),
    (CAMPAIGN_TEMPLATE_STATE, "template"),
    (CAMPIGN_REVIEW_STATE, "review"),
    (CAMPAIGN_SETTINGS_STATE, "trigger_settings"),
    (CAMPAIGN_VB_REVIEW_STATE, "vb_review"),
)

RCS_MESSAGE_TEMPLATE_CHOICES = (
    ('1', "Text"),
    ('2', "Media"),
    ('3', "Rich Card"),
    ('4', "Carousel"),
)

PAGE_ORDER = {
    CAMPAIGN_BASIC_INFO_STATE: 0,
    CAMPAIGN_TAG_AUDIENCE_STATE: 1,
    CAMPAIGN_TEMPLATE_STATE: 2,
    CAMPIGN_REVIEW_STATE: 3,
    CAMPAIGN_SETTINGS_STATE: 2,
    CAMPAIGN_VB_REVIEW_STATE: 3
}

INTERNATION_PHONE_NUMBER_REGEX = '\+(9[976]\d|8[987530]\d|6[987]\d|5[90]\d|42\d|3[875]\d|2[98654321]\d|9[8543210]|8[6421]|6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)\d{1,14}$'

DEFAULT_AWS_ACCESS_KEY_ID = "AKIA4YAOI4WFDBELYAKQ"

DEFAULT_AWS_SECRET_ACCESS_KEY = "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"

DEFAULT_AWS_SQS = "https://sqs.ap-south-1.amazonaws.com/876203271562/DevCampaignQueue"

DEFAULT_AWS_SQS_DELIVERY_PACKETS = "https://sqs.ap-south-1.amazonaws.com/876203271562/DevCampaignDeliveryPacketQueue"

API_INTEGRATION_SAMPLE_CODE_RML = """



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
            "Content-Type":"application/json",
            }
        payload = {
            "username":"RMLBot2",
            "password":"Product@123"
        }

        resp = requests.post(url=url, headers=headers,data = json.dumps(payload))
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
        logger.error("Error: get_payload_body: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
        
        
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
        logger.error("Error: getTextPayload: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


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
        logger.error("Error: getImagePayload: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


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
        logger.error("Error: getVideoPayload: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


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
        logger.error("Error: getDocumentPayload: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    

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
        logger.error("Error: getCTAPayload: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    
def sendWhatsAppMessage(payload):
    ''' A function to call send whatsapp text message API.'''
    import requests
    import urllib
    try:
        JWT_TOKEN = get_jwt_token()

        url="https://apis.rmlconnect.net/wba/v1/messages"
        headers={
            "Authorization": JWT_TOKEN,
            "Content-Type":"application/json"
        }
        
        logger.info(payload, extra={'AppName': 'Campaign'})
        
        resp=requests.post(url=url,data=payload,headers=headers)
        resp=json.loads(resp.text)
        
        logger.info(resp, extra={'AppName': 'Campaign'})
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: sendWhatsAppMessage: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
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
            
            logger.info('phone_number: %s', str(phone_number), extra={'AppName': 'Campaign'})
    
            if 'text' in x['template']['type'].lower():
                payload = getTextPayload(phone_number, x['template']['name'], x['template']['language'], variable)
            elif 'image' in x['template']['type'].lower():
                payload = getImagePayload(phone_number, x['template']['name'], x['template']['language'], variable, x['template']['link'])
            elif 'document' in x['template']['type'].lower():
                payload = getDocumentPayload(phone_number, x['template']['name'], x['template']['language'], variable, x['template']['link'])
            elif 'call to action' in x['template']['type'].lower():
                payload = getCTAPayload(phone_number, x['template']['name'], x['template']['language'], variable, x['template']['cta_text'], x['template']['cta_link'])
    
            response['request'] = payload
            response['response'] = sendWhatsAppMessage(payload)
            
        response['status'] = 200
        response['status_message'] = 'success'
        
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside api integration code: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        response['response'] = {'status': 'failed'}
    
    return response

"""

RETRY_MECHANISM = (
    ('linear', "Linear"),
    ('exponential', "Exponential"),
)

WORKING_DAYS = (
    ('1', "Every Weekday"),
    ('2', "Daily"),
    ('3', "Custom")
)

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%I:%M %p"
DATE_FORMAT_b_d_y = "%b %d, %Y %I:%M %p"

VOICE_BOT_SAMPLE_API_CODE = """





from CampaignApp.utils import *
from CampaignApp.models import *
from django.conf import settings
from datetime import datetime
from CampaignApp.utils_custom_encryption import CustomEncrypt
from EasyChatApp.models import Bot, Channel, BotChannel, VoiceBotConfiguration
import emoji
import time
import json
import sys
import pytz
import requests

def get_api_info(bot_id):
    bot_channel_obj = BotChannel.objects.filter(bot=Bot.objects.filter(pk=bot_id).first(), channel=Channel.objects.filter(name="Voice").first()).first()
    voice_bot_config_obj = VoiceBotConfiguration.objects.filter(bot_channel=bot_channel_obj).first()

    if voice_bot_config_obj:
        return voice_bot_config_obj.api_key, voice_bot_config_obj.api_token, voice_bot_config_obj.api_sid, voice_bot_config_obj.get_api_subdomain_display()
    
    return "", "", "", ""


def get_date_iso_format(send_date, send_time):
    try:
        send_date = datetime.strptime(send_date, '%Y-%m-%d')
        send_time = datetime.strptime(send_time, '%H:%M:%S')
        iso_date = datetime(send_date.year, send_date.month, send_date.day, send_time.hour, send_time.minute)
        
        tz = pytz.timezone(settings.TIME_ZONE)
        
        iso_date = iso_date.astimezone(tz).isoformat()
        
        return iso_date
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: get_date_iso_format: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def create_campaign(param):
    try:
        param = json.loads(param)
        api_key, api_token, sid, subdomain = get_api_info(param["bot_id"])
        
        cred = api_key + ":" + api_token
        cred = cred.encode('utf-8')
        encoding = base64.b64encode(cred)
        url = "https://" + subdomain + "/v2/accounts/"+sid+"/campaigns"
        
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Basic {}".format(encoding.decode('utf-8'))
        }
        
        send_at = get_date_iso_format(param['send_at_date'], param['send_at_time'])
        end_at = get_date_iso_format(param['end_at_date'], param['end_at_time'])
        
        on_status = []
        if param['is_busy_enabled']:
            on_status.append('busy')

        if param['is_no_answer_enabled']:
            on_status.append('no-answer')

        if param['is_failed_enabled']:
            on_status.append('failed')
            
        data = {
            'campaigns': [
                {
                    'from': param['from'],
                    'caller_id': param['caller_id'],
                    'url': "http://my.exotel.com/{}/exoml/start_voice/{}".format(sid, param['app_id']),
                    'name': param['name'],
                    "schedule": {
                        "send_at": send_at,
                        "end_at": end_at,
                    },
                    "retries": {
                        "number_of_retries": param['no_of_retries'],
                        "interval_mins": param['retry_interval'],
                        "mechanism": param['retry_mechanism'].capitalize(),
                        "on_status": on_status,
                    },
                    "call_status_callback": param['call_status_callback'],
                    "status_callback": param['status_callback'],
                    "call_duplicate_numbers": True,
                }
            ]
        }
        
        logger.info(headers, extra={'AppName': 'Campaign'})
        logger.info(data, extra={'AppName': 'Campaign'})

        response = requests.request("POST", url, data=json.dumps(data), headers=headers)
        response = json.loads(response.text)
        
        logger.info(response, extra={'AppName': 'Campaign'})
        
        response_body = {
            'request': data,
            'response': response,
        }
        
        return response_body

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: create_campaign: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def get_campaign_details(param):
    try:
        param = json.loads(param)
        campaign_sid = param["campaign_sid"]

        api_key, api_token, sid, subdomain = get_api_info(param["bot_id"])
        
        cred = api_key + ":" + api_token
        cred = cred.encode('utf-8')
        encoding = base64.b64encode(cred)
        
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Basic {}".format(encoding.decode('utf-8'))
        }
        
        url = "https://" + subdomain + "/v2/accounts/"+sid+"/campaigns/" + campaign_sid
            
        data = ""
        
        logger.info(headers, extra={'AppName': 'Campaign'})
        logger.info(data, extra={'AppName': 'Campaign'})

        response = requests.request("GET", url, data=data, headers=headers)
        response = json.loads(response.text)
        
        logger.info(response, extra={'AppName': 'Campaign'})
        
        return response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: get_campaign_details: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def pause_running_campaign(param):
    try:
        param = json.loads(param)
        api_key, api_token, sid, subdomain = get_api_info(param["bot_id"])
        
        cred = api_key + ":" + api_token
        cred = cred.encode('utf-8')
        encoding = base64.b64encode(cred)
        
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Basic {}".format(encoding.decode('utf-8'))
        }
        
        url = "https://" + subdomain + "/v2/accounts/"+sid+"/campaigns/" + param['campaign_sid']
            
        data = {
            'campaigns': [
                {
                    'action': 'pause',
                    'url': param['url']
                }
            ]
        }
        
        logger.info(headers, extra={'AppName': 'Campaign'})
        logger.info(data, extra={'AppName': 'Campaign'})

        response = requests.request("PUT", url, data=json.dumps(data), headers=headers)
        response = json.loads(response.text)
        
        logger.info(response, extra={'AppName': 'Campaign'})
        
        return response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: get_campaign_details: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def get_call_details(param):
    try:
        param = json.loads(param)
        call_sid = param["call_sid"]

        api_key, api_token, sid, subdomain = get_api_info(param["bot_id"])
        
        cred = api_key + ":" + api_token
        cred = cred.encode('utf-8')
        encoding = base64.b64encode(cred)
        
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Basic {}".format(encoding.decode('utf-8'))
        }
        
        url = "https://" + subdomain + "/v1/Accounts/"+sid+"/Calls/" + call_sid + ".json"
            
        data = ""
        
        logger.info(headers, extra={'AppName': 'Campaign'})
        logger.info(data, extra={'AppName': 'Campaign'})

        response = requests.request("GET", url, data=data, headers=headers)
        response = json.loads(response.text)
        
        logger.info(response, extra={'AppName': 'Campaign'})
        
        return response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: get_campaign_details: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def update_campaign(param):
    try:
        param = json.loads(param)
        api_key, api_token, sid, subdomain = get_api_info(param["bot_id"])
        
        cred = api_key + ":" + api_token
        cred = cred.encode('utf-8')
        encoding = base64.b64encode(cred)
        url = "https://" + subdomain + "/v2/accounts/"+sid+"/campaigns/" + param['campaign_sid']
        
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Basic {}".format(encoding.decode('utf-8'))
        }
        
        send_at = get_date_iso_format(param['send_at_date'], param['send_at_time'])
        end_at = get_date_iso_format(param['end_at_date'], param['end_at_time'])
        
        on_status = []
        if param['is_busy_enabled']:
            on_status.append('busy')

        if param['is_no_answer_enabled']:
            on_status.append('no-answer')

        if param['is_failed_enabled']:
            on_status.append('failed')
            
        data = {
            'campaigns': [
                {
                    'from': param['from'],
                    'caller_id': param['caller_id'],
                    'url': "http://my.exotel.com/{}/exoml/start_voice/{}".format(sid, param['app_id']),
                    'name': param['name'],
                    "schedule": {
                        "send_at": send_at,
                        "end_at": end_at,
                    },
                    "retries": {
                        "number_of_retries": param['no_of_retries'],
                        "interval_mins": param['retry_interval'],
                        "mechanism": param['retry_mechanism'].capitalize(),
                        "on_status": on_status,
                    },
                    "call_status_callback": param['call_status_callback'],
                    "status_callback": param['status_callback'],
                    "call_duplicate_numbers": True,
                }
            ]
        }
        
        logger.info(headers, extra={'AppName': 'Campaign'})
        logger.info(data, extra={'AppName': 'Campaign'})

        response = requests.request("POST", url, data=json.dumps(data), headers=headers)
        response = json.loads(response.text)
        
        logger.info(response, extra={'AppName': 'Campaign'})
        
        response_body = {
            'request': data,
            'response': response,
        }
        
        return response_body

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: update_campaign: %s for %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

"""
