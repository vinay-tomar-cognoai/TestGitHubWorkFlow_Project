from EasyChatApp.models import *
from EasyChatApp.utils_bot import get_translated_text
from EasyChatApp.utils_bot import get_supported_languages
import html
from EasyChatApp.utils import logger


def update_bot_language_template_objs_livechat_vc_notifications():
    try:
        language_bot_template_objs = RequiredBotTemplate.objects.all()
        livechat_vc_notifications = "Video Call Request has been sent$$$Video Call Started$$$Video Call Ended$$$Please join the following link for video call$$$Agent has accepted the request. Please join the following link$$$Join Now$$$Voice Call$$$Video Call$$$Agent has initiated a voice call. Would you like to connect?$$$Agent has initiated a video call. Would you like to connect?$$$Agent Cancelled the Meet.$$$Request Successfully Sent$$$Please end the ongoing call.$$$has accepted the voice call request$$$has rejected the voice call request$$$Reject$$$Accept$$$Connect$$$OK$$$Resend$$$Agent has accepted the Video Call request.$$$has rejected the video call request"
        for language_bot_template_obj in language_bot_template_objs:
            language_bot_template_obj.livechat_vc_notifications = get_translated_text(livechat_vc_notifications, language_bot_template_obj.language.lang, EasyChatTranslationCache)
            language_bot_template_obj.save(update_fields=["livechat_vc_notifications"])

    except Exception as e:
        logger.error("Error in update_bot_language_template_objs_livechat_vc_notifications: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_bot_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        livechat_validation_text = "Malicious File not accepted$$$File type not supported. Please try again with supported file (_ etc)$$$File size is large. Please try again with file size less than 5 MB"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.livechat_validation_text = get_translated_text(
                livechat_validation_text, lang, EasyChatTranslationCache)

            bot_template_obj.save(update_fields=['livechat_validation_text'])

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_bot_template_livechat_transcript_text():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        livechat_transcript_text = "Goodbye, Hope I was able to help you!$$$If you want a transcript of the chat above on your mail$$$CLICK HERE$$$To get your conversation on mail$$$The transcript will be sent over mail$$$Click on check box to get chat transcript on your mail"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.livechat_transcript_text = get_translated_text(
                livechat_transcript_text, lang, EasyChatTranslationCache)

            bot_template_obj.save(update_fields=['livechat_transcript_text'])

    except Exception as e:
        logger.error("Error in update_old_bot_template_livechat_transcript_text: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_bot_template_livechat_feedback_text():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        livechat_feedback_text = "Feedback$$$On a scale of 0-10, how likely are you to recommend LiveChat to a friend or colleague?$$$No, Thanks$$$Comments (optional)$$$Remarks$$$Submit$$$Your video call has been ended."

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.livechat_feedback_text = get_translated_text(
                livechat_feedback_text, lang, EasyChatTranslationCache)

            bot_template_obj.save(update_fields=['livechat_feedback_text'])

    except Exception as e:
        logger.error("Error in update_old_bot_template_livechat_feedback_text: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_language_script_type():
    try:
        Language.objects.filter(lang="ku").update(language_script_type="ltr")
        rtl_Language_List = ["ar", "he", "fa", "ur", "ps", "sd", "ug", "yi"]
        for language in rtl_Language_List:
            Language.objects.filter(lang=language).update(language_script_type="rtl")
    except Exception as e:
        logger.error("Error in update_language_script_type: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_easychat_translation_cache_objs():
    try:
        translation_cache_objs = EasyChatTranslationCache.objects.all()
        translation_cache_objs = translation_cache_objs.iterator()

        for translation_cache_obj in translation_cache_objs:
            translation_cache_obj.translated_data = html.unescape(translation_cache_obj.translated_data)
            translation_cache_obj.save(update_fields=["translated_data"])

    except Exception as e:
        logger.error("Error in update_old_bot_template_livechat_feedback_text: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_android_related_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        end_chat = "Do you want to resume the chat later or end the chat?$$$Resume Later$$$End Chat"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.end_chat = get_translated_text(
                end_chat, lang, EasyChatTranslationCache)

            bot_template_obj.save(update_fields=['end_chat'])

    except Exception as e:
        logger.error("Error in update_old_android_related_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def message_analytics_daily_cronjob_intuitive_data():
    from datetime import datetime, timedelta
    from EasyChatApp.utils import logger
    from EasyChatApp.utils_validation import EasyChatInputValidation
    from django.conf import settings
    import sys
    try:
        today = datetime.now()
        last_date = today.date() - timedelta(days=60)
        while(last_date < today.date()):
            for bot in Bot.objects.filter(is_deleted=False):
                supported_languages = get_supported_languages(bot, BotChannel)
                # Some messages are assigned under None category
                category_list = [None]
                category_list = [bot_category for bot_category in Category.objects.filter(bot=bot)]
                for channel in Channel.objects.filter(is_easychat_channel=True):
                    for category in category_list:
                        for language in supported_languages:
                            date_filtered_mis_objects = MISDashboard.objects.filter(
                                creation_date=str(last_date), channel_name=channel.name, bot=bot, category=category, selected_language=language)
                     
                            # Unanswered messages
                            total_unanswered_messages = date_filtered_mis_objects.filter(
                                intent_name=None, is_unidentified_query=True, is_intiuitive_query=False).exclude(message_received="")
                            total_unanswered_messages_count = total_unanswered_messages.count()
                            total_unanswered_messages_mobile_count = total_unanswered_messages.filter(is_mobile=True).count()
                            # intuitive messages
                            total_intuitive_messages = date_filtered_mis_objects.filter(
                                intent_name=None, is_intiuitive_query=True)
                            total_intuitive_messages_count = total_intuitive_messages.count()
                            total_intuitive_messages_mobile_count = total_intuitive_messages.filter(is_mobile=True).count()
                            previous_mis_objects = MessageAnalyticsDaily.objects.filter(bot=bot, date_message_analytics=str(last_date), channel_message=channel, category=category, selected_language=language).first()
                            if previous_mis_objects:
                                previous_mis_objects.intuitive_query_count = total_intuitive_messages_count
                                previous_mis_objects.intuitive_query_count_mobile = total_intuitive_messages_mobile_count
                                previous_mis_objects.unanswered_query_count = total_unanswered_messages_count
                                previous_mis_objects.unanswered_query_count_mobile = total_unanswered_messages_mobile_count
                                previous_mis_objects.save()
            last_date = last_date + timedelta(days=1)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("MessageAnalyticsDaily! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_ios_related_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        livechat_system_notifications_ios = "To avoid disconnecting with the agent, please don't minimize the browser during interaction$$$Your Internet connection was weak (or you minimised the app). Chat is disconnected"

        for bot_template_obj in bot_template_objs.iterator():

            lang = bot_template_obj.language.lang

            bot_template_obj.livechat_system_notifications_ios = get_translated_text(
                livechat_system_notifications_ios, lang, EasyChatTranslationCache)

            bot_template_obj.save(update_fields=['livechat_system_notifications_ios'])

    except Exception as e:
        logger.error("Error in update_ios_related_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_blocked_mis_objs_session():
    try:
        blocked_session_objs = UserSessionHealth.objects.filter(is_blocked=True).order_by("-unblock_time")
        for blocked_session_obj in blocked_session_objs.iterator():
            MISDashboard.objects.filter(session_id=blocked_session_obj.session_id, date__lte=blocked_session_obj.unblock_time, is_session_blocked=False).update(is_session_blocked=True)
    except Exception as e:
        logger.error("Error in update_blocked_mis_session_objs: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_livechat_analytics_data():
    try:
        start_date = MISDashboard.objects.last().creation_date
        today_date = datetime.datetime.now().date()

        bot_objs = Bot.objects.filter(is_deleted=False)
        channel_objs = Channel.objects.all()

        while start_date <= today_date:
            mis_objs = MISDashboard.objects.filter(creation_date=start_date)
            for bot in bot_objs.iterator():

                if not bot.livechat_default_intent:
                    continue
                
                bot_mis_objs = mis_objs.filter(bot=bot, intent_recognized=bot.livechat_default_intent)
                for channel in channel_objs.iterator():
                    total_livechat_intents = bot_mis_objs.filter(channel_name=channel.name).count()
                    if total_livechat_intents:
                        daily_livechat_analytics_obj = DailyLiveChatAnalytics.objects.filter(bot=bot, channel=channel, date=start_date).first()
                        if not daily_livechat_analytics_obj:
                            DailyLiveChatAnalytics.objects.create(bot=bot, channel=channel, date=start_date, count=total_livechat_intents)
                        else:
                            daily_livechat_analytics_obj.count = total_livechat_intents
                            daily_livechat_analytics_obj.save(update_fields=["count"])

            start_date += datetime.timedelta(days=1)

    except Exception as e:
        logger.error("Error in update_livechat_analytics_data: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_easychatapp_whatsapp_webhook():
    try:
        easychatapp_channel_webhooks = WhatsAppWebhook.objects.all()
        for webhook_obj in easychatapp_channel_webhooks:
            if webhook_obj.function.find("use_aliases=True") != -1:
                webhook_obj.function = webhook_obj.function.replace("use_aliases=True", "language='alias'")
                webhook_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in update_easychatapp_whatsapp_webhook! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        

print("Running update_bot_language_template_objs_livechat_vc_notifications...\n")

update_bot_language_template_objs_livechat_vc_notifications()

print("Running update_old_android_related_template_objects...\n")

update_old_android_related_template_objects()

print("Running update_old_bot_template_objects...\n")

update_old_bot_template_objects()

print("Running update_old_bot_template_livechat_transcript_text...\n")

update_old_bot_template_livechat_transcript_text()

print("Running update_old_bot_template_livechat_feedback_text...\n")

update_old_bot_template_livechat_feedback_text()

print("Running update_language_script_type ...\n")

update_language_script_type()

print("Running update_easychat_translation_cache_objs...\n")

update_easychat_translation_cache_objs()

print("Running update_ios_related_template_objects...\n")

update_ios_related_template_objects()

print("Running update_intuitive_data ...\n")

message_analytics_daily_cronjob_intuitive_data()

print("Running update_blocked_mis_objs_session ...\n")

update_blocked_mis_objs_session()

print("Running update_livechat_analytics_data ...\n")

update_livechat_analytics_data()

print("Running update_easychatapp_whatsapp_webhook ...\n")

update_easychatapp_whatsapp_webhook()
