from EasyChatApp.models import *

from EasyChatApp.utils_bot import get_translated_text


def livechat_RequiredBotTemplate_objects_livechat_voicecall_notif():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        livechat_voicecall_notif_text = "Voice Call Request has been sent$$$Voice Call Started$$$Voice Call Ended$$$Request Successfully Sent"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.livechat_voicecall_notifications = get_translated_text(
                livechat_voicecall_notif_text, lang, EasyChatTranslationCache)
            
            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in livechat_RequiredBotTemplate_objects_livechat_form_text: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_voice_bot_configuration_objects():
    channel_obj = Channel.objects.get(name="Voice")
    bot_channel_objs = BotChannel.objects.filter(channel=channel_obj)

    for bot_channel_obj in bot_channel_objs:
        voice_bot_config_obj = VoiceBotConfiguration.objects.filter(bot_channel=bot_channel_obj).first()
        if not voice_bot_config_obj:
            VoiceBotConfiguration.objects.create(bot_channel=bot_channel_obj)


def update_old_bot_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        genreal_text = "Did you mean one of the following?$$$There are some internal issue, please try again later. Sorry for your inconvenience.$$$Looks like I don't have answer for selected bot query.$$$Looks like I don't have support for this channel.$$$Session is running in another tab. Please end running sessions and try again.$$$I can tell you are upset. If my answers were not helpful, you can reach out to our customer care team.$$$Sorry to hear that, we would appreciate if you could give your comments on what went wrong. Please type 'Skip' in case you don't wish to give a comment.$$$Glad that you liked our service. Hope to see you again.$$$Thanks, we would try to improve.$$$Looks like I don't have an answer to that. Here's what I found on the web.$$$Sure, How may I assist you now?$$$Looks like, I can not answer your query for now. Please try again after some time.$$$Read More$$$Read Less$$$Show Less$$$View more$$$speak now"
        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.general_text = get_translated_text(
                genreal_text, lang, EasyChatTranslationCache)
            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running livechat_RequiredBotTemplate_objects_livechat_voicecall_notif...\n")

livechat_RequiredBotTemplate_objects_livechat_voicecall_notif()

print("Running create_voice_bot_configuration_objects...\n")

create_voice_bot_configuration_objects()

print("Running update_old_bot_template_objects...\n")

update_old_bot_template_objects()
