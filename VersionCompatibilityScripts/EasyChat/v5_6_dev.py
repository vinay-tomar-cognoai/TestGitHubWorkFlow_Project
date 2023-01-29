from CampaignApp.models import CampaignChannel, CampaignConfig
from EasyChatApp.models import *
from EasyChatApp.utils_bot import check_and_update_langauge_tuned_bot_configuration, get_translated_text


def update_old_bot_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        do_not_disturb_text = "Do not disturb$$$Are you sure, you want to enable Do not disturb? By clicking Yes, form assistant will be disabled.$$$Great, How may I help you?"
        pdf_view_document_text = "View Document"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.do_not_disturb_text = get_translated_text(
                do_not_disturb_text, lang, EasyChatTranslationCache)
            bot_template_obj.pdf_view_document_text = get_translated_text(
                pdf_view_document_text, lang, EasyChatTranslationCache)

            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_profanity_bot_response_old_bots():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        for bot_obj in bot_objs:
            if ProfanityBotResponse.objects.filter(bot=bot_obj).count() == 0:
                ProfanityBotResponse.objects.create(bot=bot_obj)

            lang_tuned_bot_objs = LanguageTunedBot.objects.filter(bot=bot_obj)
            for lang_obj in lang_tuned_bot_objs:
                check_and_update_langauge_tuned_bot_configuration(
                    bot_obj, lang_obj.language, LanguageTunedBot, EasyChatTranslationCache, EmojiBotResponse)

    except Exception as e:
        logger.error("Error in update_profanity_bot_response_old_bots: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_all_intents_with_pos_tags():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)
        intent_objs = Intent.objects.filter(
            is_deleted=False, bots__in=bot_objs)

        for intent_obj in intent_objs:
            intent_obj.save()
            # save function for intent modal is updated so pos tags will be updates once every intent is saved
    except Exception as e:
        logger.error("Error in update_all_intents_with_pos_tags: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def mark_final_childs_of_flow():
    try:
        tree_objs = Tree.objects.filter(is_deleted=False, is_last_tree=False)

        for tree_obj in tree_objs:
            intent_obj = Intent.objects.filter(tree=tree_obj).first()
            if intent_obj:
                continue

            if not tree_obj.children.filter(is_deleted=False):
                tree_obj.is_last_tree = True
                tree_obj.save()

    except Exception as e:
        logger.error("Error in mark_final_childs_of_flow: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running update_old_bot_template_objects...\n")

update_old_bot_template_objects()

print("Running update_profanity_bot_response_old_bots...\n")

update_profanity_bot_response_old_bots()

print("Running update_all_intents_with_pos_tags...\n")

update_all_intents_with_pos_tags()

print("Running mark_final_childs_of_flow...\n")

mark_final_childs_of_flow()
