import datetime

DEFAULT_TMS_FILTER_START_DATETIME = (
    datetime.datetime.today() - datetime.timedelta(7)).date()

DEFAULT_TMS_FILTER_END_DATETIME = datetime.datetime.today().date()

TMS_DEFAULT_LOGO = [
    "/static/EasyTMSApp/img/cognoDeskLarge.svg",
    "/static/EasyTMSApp/img/cognoDeskSmall.svg"
]

month_to_num_dict = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

DEFAULT_LEAD_TABLE_COL = [
    {
        'name': 'ticket_id',
        'display_name': ' Ticket ID',
        'index': 0,
        'selected': True,
    },
    {
        'name': 'query_description',
        'display_name': 'Issue description',
        'index': 1,
        'selected': True,
    },
    {
        'name': 'customer_name',
        'display_name': 'Customer Details',
        'index': 2,
        'selected': True,
    },
    {
        'name': 'ticket_status',
        'display_name': 'Ticket Status',
        'index': 3,
        'selected': True,
    },
    {
        'name': 'agent_name',
        'display_name': 'Agent',
        'index': 4,
        'selected': True,
    },
    {
        'name': 'bot_channel',
        'display_name': 'Channel',
        'index': 5,
        'selected': True,
    },
    {
        'name': 'bot',
        'display_name': 'Bot',
        'index': 6,
        'selected': True,
    },
    {
        'name': 'issue_date_time',
        'display_name': 'Ticket Issue Date',
        'index': 7,
        'selected': True,
    },
    {
        'name': 'ticket_category',
        'display_name': 'Ticket Category',
        'index': 8,
        'selected': True,
    },
    {
        'name': 'ticket_priority',
        'display_name': 'Ticket Priority',
        'index': 9,
        'selected': True,
    },
    
    {
        'name': 'query_attachment',
        'display_name': 'Issue Attachment',
        'index': 10,
        'selected': False,
    },
]

AGENT_LEVELS = (
    ("L1", "L1"),
    ("L2", "L2"),
    ("L3", "L3"),
)

AGENT_ROLES = (
    ("admin", "admin"),
    ("supervisor", "supervisor"),
    ("agent", "agent"),
)

RESEND_PASSWORD_THRESHOLD = 5

DEFAULT_TMS_CONSOLE_THEME_COLOR = '{"red": 67, "green": 163.99999999999997, "blue": 108.99999999999997, "rgb": "rgb(' \
                                  '67,164,109)", "hex": "#43A46D"} '

EXPORT_CHOICES = (
    ("AnalyticsExport", "AnalyticsExport"),
)

CRM_DOCUMENTS = {
    "auth-token": {
        "url_suffix": "auth-token",
        "original_file_name": "Auth_Token_Generation_API.docx",
        "display_file_name": "Auth Token Generation API.docx",
    },
    "ticket_generation": {
        "url_suffix": "generate-ticket",
        "original_file_name": "Generate_Ticket_API.docx",
        "display_file_name": "Generate Ticket API.docx",
    },
    "ticket_details": {
        "url_suffix": "ticket-info",
        "original_file_name": "Get_Ticket_Activity_API.docx",
        "display_file_name": "Get Ticket Activity API.docx",
    },
    "ticket_activity": {
        "url_suffix": "ticket-activity",
        "original_file_name": "Get_Ticket_Details_API.docx",
        "display_file_name": "Get Ticket Details API.docx",
    }
}

WHATSAPP_API_PROCESSOR_CODE = """from EasyTMSApp.utils import logger
from EasyTMSApp.utils_custom_encryption import *

from django.conf import settings
import json
import sys
import requests
from bs4 import BeautifulSoup

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


def sendWhatsAppMessage(payload):
    ''' A function to call send whatsapp text message API. '''
    import requests
    import urllib
    try:
        JWT_TOKEN = get_jwt_token()

        url = "https://apis.rmlconnect.net/wba/v1/messages"
        headers = {
            "Authorization": JWT_TOKEN,
            "Content-Type": "application/json"
        }

        logger.info(payload, extra={'AppName': 'EasyTMS'})

        resp = requests.post(url=url, data=payload, headers=headers, timeout=20, verify=True)
        resp = json.loads(resp.text)

        logger.info(resp, extra={'AppName': 'EasyTMS'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: sendWhatsAppMessage: %s for %s", str(e), str(exc_tb.tb_lineno),
                     extra={'AppName': 'EasyTMS'})
    return resp


def f(x):
    '''
    Format of x:
    x = {
        "agent_comment": '',
        "ticket_id": '',
        "customer_email_id": '',
    }
    '''

    response = {'status': 500, 'status_message': 'Your request was not executed successfully. Please try again later.'}
    try:
        logger.info("Into Whatsapp API data = %s ", json.dumps(x), extra={'AppName': 'EasyTMS'})

        if bool(x):
            phone_number = str(x['customer_mobile_number'])
            phone_number = phone_number[-10:]
            phone_number = "+91" + str(phone_number)

            logger.info('phone_number: %s', str(phone_number), extra={'AppName': 'EasyTMS'})
            
            message = str(x['agent_comment'])
            message = BeautifulSoup(message).text.strip()

            payload = {
                "phone": phone_number,
                "text": message
            }

            payload = json.dumps(payload)

            logger.info("payload = %s ", payload, extra={'AppName': 'EasyTMS'})

            response['request'] = payload
            response['response'] = sendWhatsAppMessage(payload)

        response['status'] = 200
        response['status_message'] = 'success'

        logger.info("response = %s ", json.dumps(response), extra={'AppName': 'EasyTMS'})

        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside api integration code: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
        response['status_message'] = 'ERROR :-  ' + str(e) + ' at line no: ' + str(exc_tb.tb_lineno)
        response['response'] = {'status': 'failed'}

    return response
"""

YEAR_TIME_AM_PM_FORMAT = "%d %b %Y %I:%M %p"
YYYY_MM_DD_FORMAT = "%Y-%m-%d"
