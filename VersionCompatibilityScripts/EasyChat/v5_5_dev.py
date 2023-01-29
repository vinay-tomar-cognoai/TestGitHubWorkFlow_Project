from EasyChatApp.models import *
from EasyChatApp.utils_bot import check_and_update_langauge_tuned_bot_configuration, get_translated_text
from EasyChatApp.utils_build_bot import update_word_dictionary
from LiveChatApp.assign_followup_leads import assign_followup_leads_to_agents

import json
import threading


def update_emoji_bot_response_old_bots():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)
        
        for bot_obj in bot_objs:
            if EmojiBotResponse.objects.filter(bot=bot_obj).count() == 0:
                EmojiBotResponse.objects.create(bot=bot_obj)

            lang_objs = LanguageTunedBot.objects.filter(bot=bot_obj)
            for lang_obj in lang_objs:
                check_and_update_langauge_tuned_bot_configuration(
                    bot_obj, lang_obj.language, LanguageTunedBot, EasyChatTranslationCache, EmojiBotResponse)

    except Exception as e:
        logger.error("Error in update_emoji_bot_response_old_bots: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_order_of_response_names():

    bot_objs = Bot.objects.all()
    for bot_obj in bot_objs:
        try:
            default_order_of_response = json.loads(bot_obj.default_order_of_response)

            order_of_resp = []
            for order in default_order_of_response:
                if order == "Calender Picker":
                    order_of_resp.append("calendar_picker")
                else:
                    order_of_resp.append(order.replace(" ", "_").lower())

            bot_obj.default_order_of_response = json.dumps(order_of_resp)
            bot_obj.save()
        except Exception as e:
            logger.error("Error in update_order_of_response_names in bot {} : {}".format(bot_obj.pk, str(e)), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    intent_objs = Intent.objects.all()
    for intent_obj in intent_objs:
        try:
            order_of_response = json.loads(intent_obj.order_of_response)

            order_of_resp = []
            for order in order_of_response:
                if order == "Calender Picker":
                    order_of_resp.append("calendar_picker")
                else:
                    order_of_resp.append(order.replace(" ", "_").lower())

            intent_obj.order_of_response = json.dumps(order_of_resp)
            intent_obj.save()
        except Exception as e:
            logger.error("Error in update_order_of_response_names in intent {} : {}".format(intent_obj.pk, str(e)), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    tree_objs = Tree.objects.all()
    for tree_obj in tree_objs:
        try:
            order_of_response = json.loads(tree_obj.order_of_response)

            order_of_resp = []
            for order in order_of_response:
                if order == "Calender Picker":
                    order_of_resp.append("calendar_picker")
                else:
                    order_of_resp.append(order.replace(" ", "_").lower())

            tree_obj.order_of_response = json.dumps(order_of_resp)
            tree_obj.save()
        except Exception as e:
            logger.error("Error in update_order_of_response_names in tree {} : {}".format(tree_obj.pk, str(e)), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_category_of_mis_objects():
    mis_objs = MISDashboard.objects.all()

    for mis_obj in mis_objs:
        if mis_obj.bot and mis_obj.category_name:
            category_obj = Category.objects.filter(name=mis_obj.category_name, bot=mis_obj.bot).first()
            if not category_obj:
                category_obj = Category.objects.create(name=mis_obj.category_name, bot=mis_obj.bot)
                category_obj.save()

            mis_obj.category = category_obj
            mis_obj.save()
            

def update_old_bot_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        form_widget_error_text = "Please enter a valid 6 digit OTP.$$$Please enter a valid 4 digit OTP.$$$Please enter a valid Email Id.$$$Invalid PAN number$$$Please enter a valid name.$$$Save$$$Reset$$$Mobile number is invalid. Please try again."
        livechat_vc_notifications = "Video Call Request has been sent$$$Video Call Started$$$Video Call Ended$$$Please join the following link for video call$$$Agent has accepted the request. Please join the following link$$$Join Now$$$Voice Call$$$Video Call$$$Agent has initiated a voice call ,Would you like to connect?$$$Agent has initiated a video call ,Would you like to connect?$$$Agent Cancelled the Meet.$$$Request Successfully Sent$$$Please end the ongoing call.$$$has accepted the voice call request$$$has rejected the voice call request$$$Reject$$$Accept$$$Connect$$$OK$$$Resend$$$Agent has accepted the Video Call request.$$$has rejected the video call request"
        livechat_cb_notifications = "Cobrowsing Session$$$Cobrowsing Session Started$$$Cobrowsing Session Ended$$$Please end the ongoing Cobrowsing Session."

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.form_widget_error_text = get_translated_text(form_widget_error_text, lang, EasyChatTranslationCache)
            bot_template_obj.livechat_vc_notifications = get_translated_text(
                livechat_vc_notifications, lang, EasyChatTranslationCache)
            bot_template_obj.livechat_cb_notifications = get_translated_text(
                livechat_cb_notifications, lang, EasyChatTranslationCache)

            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_bot_word_dictionary_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)
        for bot_obj in bot_objs:
            update_word_dictionary(bot_obj)

        WordDictionary.objects.filter(bot=None).delete()
    except Exception as e:
        logger.error("Error in create_bot_word_dictionary_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_ivr_channel():
    try:
        channel_obj = Channel.objects.get(name="IVR")
        channel_obj.name = "Voice"
        channel_obj.save()
    except Exception as e:
        logger.error("Error in update_ivr_channel: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_bot_template_objects_genreal_text():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        general_text = "Did you mean one of the following?$$$There are some internal issue, please try again later. Sorry for your inconvenience.$$$Looks like I don't have answer for selected bot query.$$$Looks like I don't have support for this channel.$$$Session is running in another tab. Please end running sessions and try again.$$$I can tell you are upset. If my answers were not helpful, you can reach out to our customer care team.$$$Sorry to hear that, we would appreciate if you could give your comments on what went wrong. Please type 'Skip' in case you don't wish to give a comment.$$$Glad that you liked our service. Hope to see you again.$$$Thanks, we would try to improve.$$$Looks like I don't have an answer to that. Here's what I found on the web.$$$Sure, How may I assist you now?$$$Looks like, I can not not answer your query for now. Please try again after some time.$$$Read More$$$Read Less$$$Show Less$$$View more$$$speak now"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.general_text = get_translated_text(general_text, lang, EasyChatTranslationCache)
            
            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

              
print("Running update_emoji_bot_response_old_bots...\n")

update_emoji_bot_response_old_bots()

print("Running update_old_bot_template_objects...\n")

update_old_bot_template_objects()

print("Running update_order_of_response_names in Thread...\n")

t1 = threading.Thread(target=update_order_of_response_names)
t1.daemon = True
t1.start()

print("Running update_category_of_mis_objects in Thread..\n")

t2 = threading.Thread(target=update_category_of_mis_objects)
t2.daemon = True
t2.start()

assign_followup_leads_to_agents()

print("Running create_bot_word_dictionary_objects in Thread..\n")

t3 = threading.Thread(target=create_bot_word_dictionary_objects)
t3.daemon = True
t3.start()

print("Running update_ivr_channel..\n")
update_ivr_channel()

print("Runing update bot template general text... \n")
update_bot_template_objects_genreal_text()
