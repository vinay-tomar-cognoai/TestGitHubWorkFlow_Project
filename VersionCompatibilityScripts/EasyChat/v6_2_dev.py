from EasyChatApp.models import *
import json
from EasyChatApp.constants_icon import INSTAGRAM_ICON, VIBER_ICON
from EasyChatApp.utils_bot import get_translated_text
from EasyChatApp.utils_translation_module import translate_given_text_to_english


def update_console_meta_data():
    try:
        bot_info_objs = BotInfo.objects.all()

        for bot_info_obj in bot_info_objs:
            console_meta_data = json.loads(bot_info_obj.console_meta_data)
            console_meta_data["lead_data_cols"].insert(0, {"name": "session_id", "display_name": "Session ID", "selected": "true"})
            bot_info_obj.console_meta_data = json.dumps(console_meta_data)
            bot_info_obj.save(update_fields=['console_meta_data'])

    except Exception as e:
        logger.error("Error in update_console_meta_data: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_instagram_icon():
    try:
        Channel.objects.filter(name="Instagram").update(icon=INSTAGRAM_ICON)
    except Exception as e:
        logger.error("Error in updat_instagram_icon: %s", str(e), extra={
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


def update_all_bot_response_table():
    try:
        bot_response_objs = BotResponse.objects.filter(table="{\"items\":[]}")
        for bot_response_obj in bot_response_objs:
            bot_response_obj.table = '{\"items\": ""}'
            bot_response_obj.save()
    except Exception as e:
        logger.error("Error in update_all_bot_response_table: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_bot_template_query_api_failure_text():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        query_api_failure_text = "We are unable to process your request at this time. Please try again later."

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.query_api_failure_text = get_translated_text(
                query_api_failure_text, lang, EasyChatTranslationCache)

            bot_template_obj.save(update_fields=['query_api_failure_text'])

    except Exception as e:
        logger.error("Error in update_old_bot_template_query_api_failure_text: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_language_tuning_variations():
    try:
        intent_tuning_objs = LanguageTuningIntentTable.objects.all()
        for intent_tuning_obj in intent_tuning_objs:
            intent_obj = intent_tuning_obj.intent
            bot_obj = intent_obj.bots.all().first()

            if not bot_obj or not intent_obj:
                continue

            multilingual_name = intent_tuning_obj.multilingual_name

            training_data_dict = json.loads(intent_obj.training_data)
            training_data = training_data_dict.values()

            english_translated_multilingual_name = translate_given_text_to_english(multilingual_name)
            if english_translated_multilingual_name and english_translated_multilingual_name != multilingual_name:
                if english_translated_multilingual_name.strip().lower() not in training_data:
                    training_data_dict[str(len(training_data_dict))] = english_translated_multilingual_name.strip().lower()
                    intent_obj.training_data = json.dumps(training_data_dict)
                    intent_obj.synced = False
                    intent_obj.trained = False
                    intent_obj.save(update_fields=["training_data", "synced", "trained"])

                    bot_obj.need_to_build = True
                    bot_obj.save(update_fields=["need_to_build"])
                     
        tree_tuning_objs = LanguageTuningTreeTable.objects.all()
        for tree_tuning_obj in tree_tuning_objs:
            tree_obj = tree_tuning_obj.tree

            if not tree_obj:
                continue

            accept_keywords = str(tree_obj.accept_keywords).split(",")
            accept_keywords_list = [accept_keyword for accept_keyword in accept_keywords if accept_keyword.strip() != ""]

            multilingual_name = tree_tuning_obj.multilingual_name
            english_translated_multilingual_name = translate_given_text_to_english(multilingual_name)
            if english_translated_multilingual_name and english_translated_multilingual_name != multilingual_name:
                if english_translated_multilingual_name.strip().lower() not in accept_keywords_list:
                    accept_keywords_list.append(english_translated_multilingual_name.strip().lower())

                    tree_obj.accept_keywords = ",".join(accept_keywords_list)
                    tree_obj.save(update_fields=["accept_keywords"])

    except Exception as e:
        logger.error("Error in update_language_tuning_variations: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})    


def update_check_ticket_status_post_pros():
    try:
        Processor.objects.filter(name__icontains="getuserticket", is_original_message_required=False).update(is_original_message_required=True)
    except Exception as e:
        logger.error("Error in update_check_ticket_status_post_pros: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})    


def update_viber_icon():
    try:
        Channel.objects.filter(name="Viber").update(icon=VIBER_ICON)
    except Exception as e:
        logger.error("Error in update_viber_icon: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running update_console_meta_data...\n")

update_console_meta_data()

print("Running update_instagram_icon... \n")

update_instagram_icon()

print("Running update_all_intents_with_pos_tags...\n")

update_all_intents_with_pos_tags()

print("Running update_all_bot_response_table...\n")

update_all_bot_response_table()

print("Running update_old_bot_template_query_api_failure_text...\n")

update_old_bot_template_query_api_failure_text()

print("Running update_language_tuning_variations...\n")

update_language_tuning_variations()

print("Running update_check_ticket_status_post_pros...\n")

update_check_ticket_status_post_pros()

print("Running update_viber_icon...\n")

update_viber_icon()
