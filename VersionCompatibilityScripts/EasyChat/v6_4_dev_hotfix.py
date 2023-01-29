from EasyChatApp.models import Bot, EasyChatTranslationCache, RequiredBotTemplate
from EasyChatApp.utils_bot import get_translated_text
from EasyChatApp.utils import logger


def update_old_bot_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)
        
        livechat_exceed_file_size_text = "Please Select a file _ 5MB*"
        
        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.livechat_validation_text += "$$$" + get_translated_text(livechat_exceed_file_size_text, lang, EasyChatTranslationCache)

            bot_template_obj.save(update_fields=['livechat_validation_text'])

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running update_old_bot_template_objects...\n")

update_old_bot_template_objects()
