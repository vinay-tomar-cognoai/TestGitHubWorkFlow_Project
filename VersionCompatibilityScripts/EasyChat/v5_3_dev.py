from EasyChatApp.constants_icon import MICROSOFT_ICON
from EasyChatApp.models import *
from EasyChatApp.utils_bot import get_translated_text
import json


def enable_percentage_match():

    bot_info_objs = BotInfo.objects.all()

    for bot_info_obj in bot_info_objs:
        bot_info_obj.is_percentage_match_enabled = True

        console_meta_data = json.loads(bot_info_obj.console_meta_data)
        updated_meta_data = {
            "lead_data_cols": []
        }

        for meta_data in console_meta_data["lead_data_cols"]:
            if meta_data["name"] == "variation_responsible":
                meta_data["selected"] = 'true'
            if meta_data["name"] == "percentage_match":
                meta_data["selected"] = 'true'
            updated_meta_data["lead_data_cols"].append(meta_data)

        bot_info_obj.console_meta_data = json.dumps(updated_meta_data)
        bot_info_obj.save()


def update_microsoft_teams_icon():
    try:
        microsoft_channel = Channel.objects.filter(name="Microsoft")
        if microsoft_channel:
            microsoft_channel = microsoft_channel.first()

            microsoft_channel.icon = MICROSOFT_ICON
            microsoft_channel.save()

    except Exception as e:
        logger.error("Error in update_microsoft_teams_icon: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def add_pdf_searcher_object():
    try:
        access_type_obj = AccessType.objects.filter(name="PDF Searcher", value="access_pdf_searcher")
        if not access_type_obj.exists():
            AccessType.objects.create(name="PDF Searcher", value="access_pdf_searcher")
    except Exception as e:
        logger.error("Error in add_pdf_searcher_object: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_bot_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        livechat_form_text = "Connect with Agent$$$Please fill in these details to connect to our agent$$$Enter your Name$$$Enter Email-ID$$$Enter Phone Number$$$Continue$$$To connect with a LiveChat Agent, please click on \"Continue\" and submit your details.$$$Choose Category$$$Please select a valid category."
        livechat_system_notifications = "Your request is in process$$$has joined the chat. Please ask your queries now.$$$Looks like your internet is weak. Unable to connect.$$$Our chat representatives are unavailable right now. Please try again in some time.$$$Your chat has ended$$$Agent has left the session. LiveChat session ended.$$$Thank you for connecting with us. Hoping to help you in the future again.$$$End Chat"
        livechat_vc_notifications = "Video Call Request has been sent$$$Video Call Started$$$Video Call Ended$$$Please join the following link for video call$$$Agent has accepted the request. Please join the following link$$$Join Now$$$Voice Call$$$Video Call$$$Agent has initated a voice call ,Would you like to connect?$$$Agent has initated a video call ,Would you like to connect?$$$Agent Cancelled the Meet.$$$Request Successfully Sent$$$Please end the ongoing call.$$$has accepted the voice call request$$$has rejected the voice call request$$$Reject$$$Accept$$$Connect$$$OK$$$Resend$$$Agent has accepted the Video Call request.$$$has rejected the video call request"
        livechat_feedback_text = "Feedback$$$On a scale of 0-10, how likely are you to recommend LiveChat to a friend or colleague?$$$No, Thanks$$$Comments (optional)"
        attachment_tooltip_text = "Attachment$$$Please upload/delete the previous attachment.$$$Upload"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.livechat_form_text = get_translated_text(
                livechat_form_text, lang, EasyChatTranslationCache)

            bot_template_obj.livechat_system_notifications = get_translated_text(
                livechat_system_notifications, lang, EasyChatTranslationCache)

            bot_template_obj.livechat_vc_notifications = get_translated_text(
                livechat_vc_notifications, lang, EasyChatTranslationCache)

            bot_template_obj.livechat_feedback_text = get_translated_text(
                livechat_feedback_text, lang, EasyChatTranslationCache)

            bot_template_obj.attachment_tooltip_text = get_translated_text(
                attachment_tooltip_text, lang, EasyChatTranslationCache)
            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_contact_customer_care_response():
    try:
        intent_objs = Intent.objects.filter(name="Contact Customer Care")

        sentence = json.dumps({"items": [{"text_response": "I am here to resolve your queries. How can I help?", "speech_response": "I am here to resolve your queries. How can I help?", "text_reprompt_response": "I am here to resolve your queries. How can I help?", "speech_reprompt_response": "I am here to resolve your queries. How can I help?"}]})

        for intent in intent_objs:
            bot_response_obj = intent.tree.response
            bot_response_obj.sentence = sentence
            bot_response_obj.save()

            language_tuning_objs = LanguageTuningIntentTable.objects.filter(intent=intent, language=Language.objects.get(lang="en"))

            for language_tuning_obj in language_tuning_objs:
                language_tuning_response_obj = language_tuning_obj.tree.response
                language_tuning_response_obj.sentence = sentence
                language_tuning_response_obj.save()

    except Exception as e:
        logger.error("Error in update_contact_customer_care_response: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


enable_percentage_match()
update_microsoft_teams_icon()
add_pdf_searcher_object()
update_old_bot_template_objects()
update_contact_customer_care_response()
