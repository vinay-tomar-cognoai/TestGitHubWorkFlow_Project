NAME_POST_PROCESSOR_TMS_PYTHON_CODE = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
import sys
def f(x):
    json_response = {}
    json_response['status_code'] = '500'
    json_response['status_message'] = 'Internal server error.'
    json_response['child_choice'] = ''
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    global result_dict
    json_response['data'] = {}
    try:
        #write your code here
        json_response['data']['full_name'] = str(x)
        json_response['status_code'] = '200'
        json_response['print'] = 'Hello World'
        return json_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("PostProcessorContent : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response
"""
ISSUE_POST_PROCESSOR_TMS_PYTHON_CODE = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
import sys
def f(x):
    json_response = {}
    json_response['status_code'] = '500'
    json_response['status_message'] = 'Internal server error.'
    json_response['child_choice'] = ''
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    global result_dict
    json_response['data'] = {}
    try:
        #write your code here
        json_response['data']['user_issue'] = '{/original_message/}'
        json_response['status_code'] = '200'
        json_response['print'] = 'Hello World'
        return json_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("PostProcessorContent : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response
"""
TICKETID_POST_PROCESSOR_TMS_PYTHON_CODE = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5)) 
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger, check_tms_ticket_exists
import sys
def f(x):
    json_response = {}
    json_response['status_code'] = '308'
    json_response['status_message'] = 'User is talking about something else.'
    json_response['child_choice'] = ''
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    global result_dict
    json_response['data'] = {}
    try:
        is_ticket_exists = check_tms_ticket_exists(str(x).strip())
        if is_ticket_exists:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response['data']['ticket_id'] = str(x).strip()

        return json_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("PostProcessorContent : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response"""
API_TREE_WHATSAPP_CREATE_TICKET = """from EasyChatApp.models import * 
from EasyTMSApp.models import  *
from EasyChatApp.utils import create_an_issue_tms
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
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
        #write your code here
        customer_email_id = '{/customer_email_id/}'
        full_name = '{/full_name/}'
        issue ='{/user_issue/}'
        user_id = '{/user_id/}'
        bot_id = '{/LAST_SELECTED_BOT/}'
        category_name = '{/category_name/}'
        attached_file_path = '{/attached_file_path/}'
        try:
            channel_name = Profile.objects.filter(user_id=user_id)[0].channel.name
        except Exception:
            channel_name = "WhatsApp"
        other_information = ""
        response['data']['ticket_id'] = create_an_issue_tms(customer_email_id, user_id, full_name, issue, bot_id, attached_file_path, channel_name, category_name, other_information)["ticket_id"]
        response['status_code'] = '200'      
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ApiTreeContent API_TREE_WHATSAPP_CREATE_TICKET : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response
"""
API_TREE_CHECK_TICKET_STATUS = """from EasyChatApp.models import * 
from EasyTMSApp.models import  Ticket
from EasyChatApp.utils import check_tms_ticket_status
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
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
        #write your code here
        ticket_id = '{/ticket_id/}'
        ticket_status_response = check_tms_ticket_status(ticket_id)
        response['data']['ticket_status'] = ticket_status_response['ticket_status_message_response']
        if ticket_status_response['agent_issue_id']:
            response['data']['agent_issue_id'] = ticket_status_response['agent_issue_id']
        response['status_code'] = '200'
        response['print'] = 'Hello world!'
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ApiTreeContent API_TREE_CHECK_TICKET_STATUS: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response
"""
API_TREE_TMS_ATTACHMENT = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
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
        #write your code here
        response['recommendations'] =  [{ 'name': 'Skip', 'id': '0' }]
        channel = "{/EasyChatChannel/}"
        response["data"]["upload_image_note"] = ""
        if channel.lower() != "web":
            response["data"]["upload_image_note"] = "(Please Note: Only one image or screenshot should be added)"
            
        response['status_code'] = '200'
        response['print'] = 'Hello world!'
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ApiTreeContent API_TREE_TMS_ATTACHMENT: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response
"""
EMAIL_ID_POST_PROCESSOR_TMS_PYTHON_CODE = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=1))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
 
def is_email_valid(email):
    emailRegex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if(re.fullmatch(emailRegex, email)):
        return True
    else:
        return False

import sys
def f(x):
    json_response = {}
    json_response['status_code'] = '308'
    json_response['status_message'] = 'User is talking about something else.'
    json_response['child_choice'] = ''
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    global result_dict
    json_response['data'] = {}
    try:
        #write your code here
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.lower()

        if is_email_valid(user_message) == True:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]=""
            json_response["data"]={
                "customer_email_id": user_message
            }

        return json_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("PostProcessorContent : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response
"""
PHONE_NO_POST_PROCESSOR_TMS_PYTHON_CODE = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
import sys
def f(x):
    json_response = {}
    json_response['status_code'] = '308'
    json_response['status_message'] = 'User is talking about something else.'
    json_response['child_choice'] = ''
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    global result_dict
    json_response['data'] = {}
    try:
        #write your code here
        user_message = x.encode("ascii", errors="ignore").decode("ascii")
        user_message = user_message.lower()

        b = ""
        for i in user_message:
            if i in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                b += i
        mobile_number = b
        
        if len(str(mobile_number))==10:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]=""
            json_response["data"]={
                "MobileNumber":mobile_number
            }
        return json_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("PostProcessorContent : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response
"""
API_TREE_TMS_CREATE_TICKET = """from EasyChatApp.models import * 
from EasyChatApp.utils import create_an_issue_tms
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
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
        #write your code here
        full_name = '{/full_name/}'
        issue ='{/user_issue/}'
        phone_no = '{/MobileNumber/}'
        customer_email_id = '{/customer_email_id/}'
        bot_id = '{/bot_id/}'
        user_id = '{/EasyChatUserID/}'
        attached_file_path = '{/attached_file_path/}'
        category_name = '{/category_name/}'
        other_informations = ""
        channel_name = '{/EasyChatChannel/}'

        response['data']['ticket_id'] = create_an_issue_tms(customer_email_id, phone_no, full_name, issue, bot_id, attached_file_path, channel_name, category_name, other_informations)["ticket_id"]
        response['status_code'] = '200'      
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ApiTreeContent API_TREE_TMS_CREATE_TICKET: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response
"""
API_TREE_WHATSAPP_CATEGORIES_RECOMMENDATION = """
from EasyChatApp.models import *
from EasyTMSApp.models import TicketCategory
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
import sys
def get_category_list(bot_id):
    try:
        bot_obj = Bot.objects.filter(id=bot_id, is_deleted=False)[0]
        categories_list = list(TicketCategory.objects.filter(bot=bot_obj,is_deleted=False).values_list('ticket_category'))
        categories_list = [item[0] for item in categories_list]
        return categories_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ApiTreeContent get_category_list : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return []


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
        #write your code here
        bot_id = '{/LAST_SELECTED_BOT/}'
        response['recommendations'] = get_category_list(bot_id)
        response['status_code'] = '200'      
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ApiTreeContent API_TREE_WHATSAPP_CATEGORIES_RECOMMENDATION: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response
"""
CATEGORY_NAME_POST_PROCESSOR_TMS_PYTHON_CODE = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
import sys
def f(x):
    json_response = {}
    json_response['status_code'] = '500'
    json_response['status_message'] = 'Internal server error.'
    json_response['child_choice'] = ''
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    global result_dict
    json_response['data'] = {}
    try:
        #write your code here
        json_response['data']['category_name'] = str(x)
        json_response['status_code'] = '200'
        json_response['print'] = 'Hello World'
        return json_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("PostProcessorContent : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response
"""
GET_CUSTOMER_NAME__POST__TMS__CHECK_STATUS_INTENT = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=2))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
import sys
def f(x):
    json_response = {}
    json_response['status_code'] = '500'
    json_response['status_message'] = 'Internal server error.'
    json_response['child_choice'] = ''
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    global result_dict
    json_response['data'] = {}
    try:
        #write your code here
        json_response["data"]["customer_message"] = str(x)
        json_response['status_code'] = '200'
        json_response['print'] = 'Hello world!'
        return json_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('PostProcessorContent : ' + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return json_response
"""

API_TREE_TMS_ATTACHMENT__CHECK_STATUS_INTENT = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=5))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
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
        #write your code here
        response['recommendations'] =  [{ 'name': 'Skip', 'id': '0' }]
        response["data"]["attached_file_path"] = ""
        response['status_code'] = '200'
        response['print'] = 'Hello world!'
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ApiTreeContent API_TREE_TMS_ATTACHMENT__CHECK_STATUS_INTENT: " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response
"""

API_TREE_THANK_YOU__CHECK_STATUS_INTENT = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=2))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 
from EasyChatApp.utils import logger
from EasyTMSApp.utils import save_customer_reply_on_agent_query, mark_agent_customer_query_resolved

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
        #write your code here
        ticket_id = '{/ticket_id/}'
        customer_message = '{/customer_message/}'
        attachment = '{/attached_file_path/}'
        agent_issue_id = '{/agent_issue_id/}'

        save_customer_reply_on_agent_query(ticket_id, customer_message, attachment)
        
        if agent_issue_id:
            mark_agent_customer_query_resolved(agent_issue_id)

        response['status_code'] = '200'
        response['print'] = 'Hello world!'
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('ApiTreeContent API_TREE_THANK_YOU__CHECK_STATUS_INTENT: ' + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response
"""

API_TREE_FOR_CATEGORY_AS_RECOMMENDATION = """from EasyChatApp.models import * 
from EasyTMSApp.models import TicketCategory
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=284))
    exec(str(common_utils_obj[0].code), result_dict) 
except Exception:
    pass 

def get_category_list(bot_id):
    try:
        bot_obj = Bot.objects.filter(id=bot_id, is_deleted=False)[0]
        categories_list = list(TicketCategory.objects.filter(bot=bot_obj,is_deleted=False).values_list('ticket_category'))
        categories_list = [item[0] for item in categories_list]
        return categories_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ApiTreeContent get_category_list : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return []
        
from EasyChatApp.utils import logger
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
        channel_name = '{/EasyChatChannel/}'
        bot_id = '{/bot_id/}'
        if str(channel_name) not in ["Web", "iOS", "Android"]:
             response['recommendations'] = get_category_list(bot_id)
        response['status_code'] = '200'
        response['print'] = 'Hello world!'
        
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('ApiTreeContent : ' + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response
"""
