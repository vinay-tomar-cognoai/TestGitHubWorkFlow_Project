CSAT_GET_RATING_PYTHON_CODE_API_TREE = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=int('{/bot_id/}'))) 
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
    response['dynamic_widget_type'] = ''
    response['modes'] = {"list_message_header": "Feedback"}
    response['modes_param'] = {}
    global result_dict
    try:
        #write your code here
        response['status_code'] = '200'
        bot = Bot.objects.get(pk=int('{/bot_id/}'))
        scale_rating_5 = bot.scale_rating_5
        if scale_rating_5:
            list_rec = ['😍$$$Very Happy', '😀$$$Happy', '😕$$$Neutral', '😓$$$Sad', '😡$$$Angry']
        else:
            list_rec = ['😍$$$Very Happy', '😀$$$Happy', '😓$$$Sad', '😡$$$Angry']
        for x in list_rec:
            response['choices'].append({'display':x,'value':x})
            if scale_rating_5:
                response['data']['score_dict'] = {'😍': 5, '😀': 4, '😕': 3, '😓': 2, '😡': 1}
            else:
                response['data']['score_dict'] = {'😍': 4, '😀': 3, '😓': 2, '😡': 1}
                
        response['status_message'] = 'Ok'
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('ApiTreeContent : ' + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response
                """

CSAT_GET_FORM_CHOICE_POST_PROCESSOR = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=int('{/bot_id/}')))
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
        bot_obj = Bot.objects.get(pk=int('{/bot_id/}'))
        score_dict = {/score_dict/}
        if x in score_dict.keys():
            score = score_dict[x]
            json_response['data']['csat_score'] = score
            json_response['status_code'] = '200'
            
            if int(score) in [1,2]:
                json_response['child_choice'] = 'Text Feedback Submit'
            else:
                json_response['child_choice'] = 'Positive Feedback'
            json_response['status_code'] = '200'
        else:
            json_response['status_code'] = '308'
        json_response['status_message'] = 'Ok'
        return json_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("PostProcessorContent : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response
                """

CSAT_SAVE_FEEDBACK_WITHOUT_DETAILS_API_TREE = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=int('{/bot_id/}')))
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
    response['dynamic_widget_type'] = ''
    response['modes'] = {}
    response['modes_param'] = {}
    global result_dict
    try:
        #write your code here
        response['status_code'] = '200'
        score = '{/csat_score/}'
        feedback = '{/text_feedback/}'
        if feedback == None or feedback == 'None':
            feedback = ''
        bot_obj = Bot.objects.get(pk=int('{/bot_id/}'))
        channel = Channel.objects.get(name="{/EasyChatChannel/}")
        Feedback.objects.create(user_id='{/EasyChatUserID/}', bot=bot_obj, rating=score, comments=feedback, channel=channel, scale_rating_5=bot_obj.scale_rating_5)
        response['status_code'] = '200'
        response['status_message'] = 'Ok'
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('ApiTreeContent : ' + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return response
                """

CSAT_SAVE_FEEDBACK_WITHOUT_DETAILS_POST_PROCESSOR = """from EasyChatApp.models import * 
result_dict = {}
try:
    common_utils_obj = CommonUtilsFile.objects.filter(bot=Bot.objects.get(pk=int('{/bot_id/}')))
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
        json_response['data']['text_feedback'] = str(x)
        json_response['child_choice'] = 'Save Final Feedback'
        json_response['status_message'] = 'Ok'
        json_response['status_code'] = '200'
        return json_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("PostProcessorContent : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response
                """
