from EasyChatApp.models import RequiredBotTemplate, EasyChatTranslationCache, BotInfo

from EasyChatApp.utils_bot import get_translated_text
from EasyChatApp.utils import logger

import json


def update_bot_language_template_objs_placeholders():
    try:
        language_bot_template_objs = RequiredBotTemplate.objects.all()

        widgets_placeholder_text = "Choose from the above options$$$Attach a file to submit$$$Provide a number above$$$Select a value above$$$Record a video to send$$$Choose a date and time above$$$Fill the form and submit"

        for language_bot_template_obj in language_bot_template_objs:
            language_bot_template_obj.widgets_placeholder_text = get_translated_text(widgets_placeholder_text, language_bot_template_obj.language.lang, EasyChatTranslationCache)
            language_bot_template_obj.save(update_fields=["widgets_placeholder_text"])

    except Exception as e:
        logger.error("Error in update_bot_language_template_objs: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running update_bot_language_template_objs_placeholders...\n")

update_bot_language_template_objs_placeholders()


def update_video_upload_success_text():
    try:
        language_bot_template_objs = RequiredBotTemplate.objects.all()

        video_upload_success = "Your video is uploaded successfully"

        for language_bot_template_obj in language_bot_template_objs:
            language_bot_template_obj.uploading_video_text = get_translated_text(video_upload_success, language_bot_template_obj.language.lang, EasyChatTranslationCache)
            language_bot_template_obj.save(update_fields=["uploading_video_text"])

    except Exception as e:
        logger.error("Error in update_video_upload_success_text: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})    


print("Running update_bot_language_template_objs_placeholders...\n")

update_video_upload_success_text()


def update_range_slider_error_text():
    try:
        language_bot_template_objs = RequiredBotTemplate.objects.all()

        range_slider_error_messages = "Please select a valid value in given range$$$Please select a valid value in given range$$$Please enter a valid input$$$Please enter a valid minimum value$$$Please enter a valid maximum value$$$Mimimum value cannot be less than given range$$$Minimum value cannot be greater than given range$$$Maximum value cannot be greater than given range$$$Maximum value cannot be lesser than given range$$$Minimum value cannot be greater than maximum value"

        for language_bot_template_obj in language_bot_template_objs:
            language_bot_template_obj.range_slider_error_messages = get_translated_text(range_slider_error_messages, language_bot_template_obj.language.lang, EasyChatTranslationCache)
            language_bot_template_obj.save(update_fields=["range_slider_error_messages"])
    except Exception as e:
        logger.error("Error in update_range_slider_error_text: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})    


print("Running update_range_slider_error_text...\n")

update_range_slider_error_text()
