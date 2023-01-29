import logging

from EasyChatApp.utils import *
from EasyChatApp.models import *
from EasyChatApp.utils_userflow import *
"""
function: create_lead_bot_intent_flow
input params:
    bot_obj: Bot Object
output:
    create flow for lead generation bot
"""


def create_lead_bot_intent_flow(bot_obj):
    try:
        logger.info("Lead generation bot start building flow", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})
        # Python code for Post Processor Name
        save_user_name = ""
        save_user_name = """
import re
def check_valid_name(str):
    pattern = re.compile("^[a-zA-Z ]+$") 
    if pattern.match(str): 
        name = str.split(" ")
        if len(name) <= 2:
            return True
        else:
            return False
    else: 
        return False
def f(x):
    json_response = {}
    json_response["status_code"]="500"
    json_response["status_message"]="Internal Server Error"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        user_name =str(x)
        user_name = user_name.strip()
        if check_valid_name(user_name) == False:
            json_response["status_code"]="308"
            json_response["status_message"]="REDIRECT"
        else:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]=""
            json_response["data"]={"lead_generation_user_name":user_name}
        return json_response
    except Exception:
        return json_response
        """

        # Python code for Post Processor email
        save_user_email = ""
        save_user_email = """
import re
from EasyChatApp.models import LeadGeneration, Bot
def check_valid_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if(re.search(regex,email)):
        return True
    return False
def f(x):
    json_response = {}
    json_response["status_code"]="500"
    json_response["status_message"]="Internal Server Error"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        email =str(x)
        email = email.strip()
        if(check_valid_email(email) == False):
            json_response["status_code"]="308"
            json_response["status_message"]="REDIRECT"
        else:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]=""
            name = "{/lead_generation_user_name/}"
            bot_id = "{/bot_id/}"
            bot_obj = Bot.objects.get(pk=int(bot_id))
            lead_bot_pk = LeadGeneration.objects.create(bot=bot_obj,name=str(name),email_id=str(email))
            json_response["data"]={"lead_generation_user_email":email,"lead_bot_pk":lead_bot_pk.pk}
        return json_response
    except Exception:
        return json_response
        """

        # Python code for Post Processor Phone no
        save_user_phone_no = ""
        save_user_phone_no = """
import re
from EasyChatApp.models import LeadGeneration, Bot
def check_valid_phone(phone_no):
    if re.match(r'[789]\d{9}$',phone_no):   
        return True 
    else:  
        return False
def f(x):
    json_response = {}
    json_response["status_code"]="500"
    json_response["status_message"]="Internal Server Error"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        phone =str(x)
        phone = phone.strip()
        if(check_valid_phone(phone) == False):
            json_response["status_code"]="308"
            json_response["status_message"]="REDIRECT"
        else:
            json_response["status_code"]="200"
            json_response["status_message"]="SUCCESS"
            json_response["child_choice"]=""
            lead_bot_pk = "{/lead_bot_pk/}"
            lead_bot_obj = LeadGeneration.objects.get(pk=int(lead_bot_pk))
            lead_bot_obj.phone_no = phone
            lead_bot_obj.save()
            json_response["data"]={"lead_generation_phone_no":phone}
        return json_response
    except Exception:
        return json_response
        """

        # Python code for pipeprocessor
        save_lead_data = ""
        save_lead_data = """
from EasyChatApp.models import LeadGeneration, Bot
def f():
    json_response = {}
    json_response["status_code"]="500"
    json_response["status_message"]="Internal Server Error"
    json_response["child_choice"]=""
    json_response["data"]={}
    try:
        name = "{/lead_generation_user_name/}"
        email = "{/lead_generation_user_email/}"
        phone_no = "{/lead_generation_phone_no/}"
        bot_id = "{/bot_id/}"
        bot_obj = Bot.objects.get(pk=int(bot_id))
        lead_bot_pk = "{/lead_bot_pk/}"
        lead_obj = LeadGeneration.objects.get(bot=bot_obj,name=str(name),email_id=str(email))
        lead_obj.phone_no = phone_no
        lead_obj.save()
        json_response["status_code"]="200"
        json_response["status_message"]="SUCCESS"
        json_response["child_choice"]=""
        return json_response
    except Exception:
        return json_response
        """

        # Creating Intent Object
        intent_obj = Intent.objects.create(
            name="Learn more about us", training_data=json.dumps({"0": "about us", "1": "learn", "2": "Learn more about us"}))
        intent_obj.bots.add(bot_obj)

        for channel_obj in Channel.objects.filter(is_easychat_channel=True):
            intent_obj.channels.add(channel_obj)

        stem_words = get_stem_words_of_sentence(
            intent_obj.name, None, None, None, bot_obj)

        stem_words.sort()
        hashed_name = ' '.join(stem_words)
        hashed_name = hashlib.md5(hashed_name.encode()).hexdigest()
        intent_obj.intent_hash = hashed_name
        intent_obj.save()

        # Bot response
        bot_response_obj = create_bot_response(
            "Please enter your first name and last name")
        tree_obj = intent_obj.tree
        tree_obj.response = bot_response_obj
        try:
            name_post_processor = Processor.objects.get(name="LeadGenerationSaveUserName",
                                                        function=str(save_user_name))
        except Exception:
            name_post_processor = Processor.objects.create(name="LeadGenerationSaveUserName",
                                                           function=str(save_user_name))
        tree_obj.post_processor = name_post_processor
        tree_obj.save()

        # Creating Email Tree
        try:
            email_post_processor = Processor.objects.get(name="LeadGenerationSaveUserEmail",
                                                         function=str(save_user_email))
            email_tree_obj = Tree.objects.get(name='leademail',
                                              post_processor=email_post_processor)
        except Exception:
            logger.error("Can not find", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})
            email_post_processor = Processor.objects.create(name="LeadGenerationSaveUserEmail",
                                                            function=str(save_user_email))
            email_tree_obj = Tree.objects.create(name='leademail',
                                                 post_processor=email_post_processor)
        email_response_obj = create_bot_response(
            "Please enter your valid email address.")
        email_tree_obj.response = email_response_obj
        email_tree_obj.save()

        # Creating Phone Tree
        try:
            phone_no_post_processor = Processor.objects.get(name="LeadGenerationSaveUserPhoneNumber",
                                                               function=str(save_user_phone_no))
            phone_no_tree_obj = Tree.objects.get(name='leadphone_no',
                                                    post_processor=phone_no_post_processor)
        except Exception:
            phone_no_post_processor = Processor.objects.create(name="LeadGenerationSaveUserPhoneNumber",
                                                               function=str(save_user_phone_no))
            phone_no_tree_obj = Tree.objects.create(name='leadphone_no',
                                                    post_processor=phone_no_post_processor)
        phone_response_obj = create_bot_response(
            "Please enter your 10 digit valid phone number.")
        phone_no_tree_obj.response = phone_response_obj
        phone_no_tree_obj.save()

        # Creating Display Tree
        try:
            display_pre_processor = Processor.objects.get(name="LeadGenerationSaveLeadData",
                                                          function=str(save_lead_data))
            display_tree_obj = Tree.objects.get(name='lead_response',
                                                pre_processor=display_pre_processor)
        except Exception:
            display_pre_processor = Processor.objects.create(name="LeadGenerationSaveLeadData",
                                                             function=str(save_lead_data))
            display_tree_obj = Tree.objects.create(name='lead_response',
                                                   pre_processor=display_pre_processor)
        display_response_obj = create_bot_response(
            "Thank you for filling the details. Our agents will contact you soon.")
        display_tree_obj.response = display_response_obj
        display_tree_obj.save()

        # Adding children in trees
        tree_obj.children.add(email_tree_obj)
        email_tree_obj.children.add(phone_no_tree_obj)
        phone_no_tree_obj.children.add(display_tree_obj)
        tree_obj.save()
        email_tree_obj.save()
        phone_no_tree_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_lead_bot_intent_flow! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})
