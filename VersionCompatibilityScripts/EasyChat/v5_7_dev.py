from EasyChatApp.models import *
from EasyChatApp.constants_icon import EMAIL_ICON
from EasyChatApp.utils import get_translated_text


def add_ameyo_whatsapp_bsp():
    try:
        ameyo_chatbot_bsp = WhatsAppServiceProvider.objects.filter(name=1).first()
        
        if not ameyo_chatbot_bsp:
            WhatsAppServiceProvider.objects.create(name="1", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_ameyo_webhook.py")

    except Exception as e:
        logger.error("Error in add_ameyo_whatsapp_bsp: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_bot_invocation_for_all_staff_users():
    try:
        user_objs = User.objects.filter(is_staff=True)
        
        if user_objs.exists():
            for user in user_objs:
                user.is_bot_invocation_enabled = True
                user.save()

    except Exception as e:
        logger.error("Error in update_bot_invocation_for_all_staff_users: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def add_email_channel():
    try:

        email_channel_obj = Channel.objects.filter(name="Email").first()
        if not email_channel_obj:
            Channel.objects.create(name="Email", icon=EMAIL_ICON, is_easychat_channel=False)

    except Exception as e:
        logger.error("Error in add_email_channel: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_required_template_obj():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        back_text = "Back"
        livechat_form_text = 'Connect with Agent$$$Please fill in these details to connect to our agent$$$Enter your Name$$$Enter Email-ID$$$Enter Phone Number$$$Continue$$$To connect with LiveChat Agent, please Click "Continue" and submit your details or Click "Back" to end the conversation.$$$Choose Category$$$Please select a valid category.'

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang
            bot_template_obj.back_text = get_translated_text(
                back_text, lang, EasyChatTranslationCache)
            bot_template_obj.livechat_form_text = get_translated_text(
                livechat_form_text, lang, EasyChatTranslationCache)
            bot_template_obj.save()  
    except Exception as e:
        logger.error("Error in update_required_template_obj: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})  


print("Running add_ameyo_whatsapp_bsp...\n")

add_ameyo_whatsapp_bsp()

print("Running update_bot_invocation_for_all_staff_users...\n")

update_bot_invocation_for_all_staff_users()

print("Running add_email_channel...\n")

add_email_channel()

print("Running update_required_template_obj...\n")

update_required_template_obj()
