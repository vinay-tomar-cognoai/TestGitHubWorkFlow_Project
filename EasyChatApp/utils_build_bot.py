import re
import os
import sys
import json
import logging
import time
import wordninja
from datetime import datetime
import requests
import hashlib
from bs4 import BeautifulSoup

from django.conf import settings
from EasyChatApp.utils import get_word_mapper_dictionary, preprocess_spell_checker, build_suggestions_and_word_mapper
from EasyChatApp.models import Config, Intent, LanguageTuningIntentTable, WordMapper, EasyChatSpellCheckerWord, ChunksOfSuggestions, Bot, Channel, BotInfo, WordDictionary, EasyChatTranslationCache
from DeveloperConsoleApp.utils import get_developer_console_settings
from EasyChatApp.utils_translation_module import translate_given_text_to_english
from EasyChatApp.utils_bot import get_translated_text

logger = logging.getLogger(__name__)

lm = wordninja.LanguageModel(settings.MEDIA_ROOT + 'wordninja_words.txt.gz')


def update_file_version():
    try:
        config_obj = Config.objects.all()[0]

        version = float(config_obj.static_file_version)
        version = version + 0.1
        version = round(version, 1)

        config_obj.static_file_version = version
        config_obj.save()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_file_version %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def sync_word_mapper_and_intent(bot_obj):
    try:
        sync_word_mapper_with_intent(bot_obj, True)
        sync_word_mapper_with_intent(bot_obj, False)

        Intent.objects.filter(
            bots__in=[bot_obj], is_deleted=False, is_hidden=False, synced=False).update(synced=True)

        WordMapper.objects.filter(
            bots__in=[bot_obj], synced=False).update(synced=True)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("sync_word_mapper_and_intent %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def sync_word_mapper_with_intent(bot_obj, update_all_intent):
    try:
        if update_all_intent:
            intent_objs = Intent.objects.filter(
                bots__in=[bot_obj], is_deleted=False, is_hidden=False)
            sync_all_word_mapper = False
        else:
            intent_objs = Intent.objects.filter(
                bots__in=[bot_obj], is_deleted=False, is_hidden=False, synced=False)
            sync_all_word_mapper = True

        word_mapper_dict = get_word_mapper_dictionary(
            WordMapper, bot_obj, '', '', '', sync_all_word_mapper)

        if not bool(word_mapper_dict):
            return

        for intent_obj in intent_objs:
            training_data_dict = json.loads(intent_obj.training_data)

            training_data_arr = []
            for index in training_data_dict:
                training_data_arr.append(training_data_dict[index])

            length = len(training_data_arr)
            for index in range(0, length):
                word_mapper_sentence = ''

                for word in training_data_arr[index].strip().split(" "):

                    strip_word = word.strip().lower()
                    if strip_word in word_mapper_dict:
                        word_mapper_sentence += word_mapper_dict[strip_word]
                    else:
                        word_mapper_sentence += word
                    word_mapper_sentence += ' '

                word_mapper_sentence = word_mapper_sentence.strip()

                if word_mapper_sentence not in training_data_arr:
                    training_data_arr.append(word_mapper_sentence)

            training_data_dict = {}
            for index, sentence in enumerate(training_data_arr):
                training_data_dict[str(index)] = sentence

            intent_obj.training_data = json.dumps(training_data_dict)
            intent_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("sync_word_mapper_with_intent: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_custom_words_to_spell_check_api(bot_obj, words_list):
    try:
        config_obj = get_developer_console_settings()

        url = config_obj.add_spell_check_words_api_endpoint
        headers = {
            "content-type": "application/json"
        }

        spell_check_id = get_hash_value(bot_obj.pk, settings.EASYCHAT_DOMAIN)

        data = {
            "custom_words": words_list,
            "spell_check_id": spell_check_id,
        }

        response = requests.post(url=url, headers=headers, data=json.dumps(data), auth=(config_obj.spell_check_api_username, config_obj.spell_check_api_password), timeout=10)
        response = json.loads(response.text)
        if response["status"] == 200:
            logger.info("Add custom words api passed: {}".format(response), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        else:
            logger.error("Add custom words api failed: {}".format(response), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_custom_word_via_api: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def remove_custom_words_from_spell_check_api(bot_obj):
    try:
        words_list = list(EasyChatSpellCheckerWord.objects.filter(bot=bot_obj).values_list("word", flat=True))

        config_obj = get_developer_console_settings()

        url = config_obj.remove_spell_check_words_api_endpoint
        headers = {
            "content-type": "application/json"
        }

        spell_check_id = get_hash_value(bot_obj.pk, settings.EASYCHAT_DOMAIN)

        data = {
            "custom_words": words_list,
            "spell_check_id": spell_check_id
        }

        response = requests.post(url=url, headers=headers, data=json.dumps(data), auth=(config_obj.spell_check_api_username, config_obj.spell_check_api_password), timeout=10)
        response = json.loads(response.text)
        if response["status"] == 200:
            logger.info("Remove custom words api passed: {}".format(response), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        else:
            logger.error("Remove custom words api failed: {}".format(response), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("remove_custom_words_from_spell_check_api: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_word_dictionary(bot_obj):
    intent_words = []
    try:
        intent_objs = Intent.objects.filter(bots__in=[bot_obj], is_deleted=False)

        word_dictionary_obj = WordDictionary.objects.filter(bot=bot_obj).first()
        if not word_dictionary_obj:
            word_dictionary_obj = WordDictionary.objects.create(bot=bot_obj)

        word_dictionary_set = set()
        
        for intent_obj in intent_objs:
            keywords = json.loads(intent_obj.keywords)
            for key in keywords:
                for word in keywords[key].split(","):
                    word_dictionary_set.add(word.strip())

        intent_words = list(word_dictionary_set)

        word_dictionary_obj.word_dict = json.dumps({"items": list(word_dictionary_set)})
        word_dictionary_obj.save()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_word_dictionary %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return intent_words


def train_intents(bot_obj):
    try:
        intent_objs = Intent.objects.filter(
            bots__in=[bot_obj], trained=False, is_deleted=False, is_hidden=False)

        cmd = 'gzip -d ' + settings.MEDIA_ROOT + 'wordninja_words.txt.gz'
        os.system(cmd)

        added_words = set()
        already_checked_words = set()

        for intent_obj in intent_objs.iterator():
            keyword_dict = json.loads(intent_obj.keywords)

            for index_key in keyword_dict.keys():
                stem_words = set(keyword_dict[index_key].split(","))

                already_checked_words = add_word_to_spell_checker(
                    stem_words, already_checked_words, bot_obj)
                added_words = add_word_to_word_splitter(
                    stem_words, added_words)

            intent_obj.trained = True
            intent_obj.save(update_fields=['trained'])

        write_to_file(added_words)

        cmd = 'gzip ' + settings.MEDIA_ROOT + 'wordninja_words.txt'
        os.system(cmd)

        # Updating spell defined in utils
        preprocess_spell_checker(bot_obj)
        words_to_add = update_word_dictionary(bot_obj)

        bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
        if bot_info_obj and bot_info_obj.enable_spell_check_while_typing:
            remove_custom_words_from_spell_check_api(bot_obj)
            add_custom_words_to_spell_check_api(bot_obj, words_to_add)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("train_intents %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_word_to_spell_checker(words, already_checked_words, bot_obj):
    try:
        for word in words:
            if word in already_checked_words:
                continue

            already_checked_words.add(word)

            if EasyChatSpellCheckerWord.objects.filter(word=word.lower().strip(), bot=bot_obj):
                continue

            # output_word = spell.correction(word)
            # output_word = output_word.strip()

            # if word != output_word:
            EasyChatSpellCheckerWord.objects.create(
                word=word.lower().strip(), bot=bot_obj)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_word_to_spell_checker: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return already_checked_words


def add_word_to_word_splitter(words, added_words):
    try:
        for word in words:
            if word in added_words:
                continue

            word_split = lm.split(word)

            if word != word_split[0]:
                added_words.add(word)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_word_to_word_splitter: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return added_words


def write_to_file(added_words):
    try:
        with open(settings.MEDIA_ROOT + 'wordninja_words.txt', 'r+') as f:
            content = f.read()

            for word in added_words:
                f.seek(0, 0)
                f.write(word.rstrip('\r\n') + '\n' + content)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("write_to_file: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_suggestions_and_word_mapper(bot_obj):
    try:
        if ChunksOfSuggestions.objects.filter(bot=bot_obj):
            ChunksOfSuggestions.objects.filter(
                bot=bot_obj).delete()

        build_suggestions_and_word_mapper(
            bot_obj.pk, Bot, WordMapper, Channel, Intent, ChunksOfSuggestions)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_suggestions_and_word_mapper %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def build_bot(bot_obj, event_obj):
    try:
        start_time = time.time()
        update_file_version()

        event_obj.event_progress += 20
        event_obj.save(update_fields=['event_progress'])

        # Here we transate intent names in all available languages in bot and then translate them back in English
        # And add the result in that intent's training question and then we do the same for language tuned intents.
        # This is done because translation may result in change of words/sentence so this help us in generating more variations
        # And increase accuracy in other languages as well.
        add_training_questions_based_on_translation(bot_obj)

        event_obj.event_progress += 20
        event_obj.save(update_fields=['event_progress'])

        sync_word_mapper_and_intent(bot_obj)

        event_obj.event_progress += 20
        event_obj.save(update_fields=['event_progress'])

        train_intents(bot_obj)

        event_obj.event_progress += 20
        event_obj.save(update_fields=['event_progress'])

        update_suggestions_and_word_mapper(bot_obj)

        event_obj.event_progress += 20
        event_obj.completed_datetime = datetime.now()
        event_obj.is_completed = True
        event_obj.time_taken = time.time() - start_time
        event_obj.save()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("build_bot %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        event_obj.is_failed = True
        event_obj.save()


def get_hash_value(bot_pk, console_url):
    hashed_value = ""
    try:
        final_key = console_url + "_" + str(bot_pk)
        hashed_value = hashlib.md5(final_key.encode()).hexdigest()

        return hashed_value
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_hash_value: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_training_questions_based_on_translation(bot_obj):
    try:

        add_training_questions_based_on_available_languages(bot_obj)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_training_questions_based_on_translation: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_training_questions_based_on_available_languages(bot_obj):
    try:
        languages_supported_by_bot = bot_obj.languages_supported.exclude(lang="en")
        if not languages_supported_by_bot.exists():
            return
        intent_objs = Intent.objects.filter(
            bots__in=[bot_obj], is_deleted=False, is_hidden=False, trained=False)
        training_questions_regex = r'[`@#$%^*()_+\-=\[\]{};\':"\\|,<>\/~]'
        training_questions_regex = re.compile(training_questions_regex)
        for intent in intent_objs.iterator():
            try:
                intent_name = intent.name
                training_questions = []
                training_data_dict = json.loads(intent.training_data)
                for index in range(len(training_data_dict)):
                    training_questions.append(training_data_dict[str(index)])
                for language in languages_supported_by_bot:
                    multilingual_name = get_translated_text(
                        intent_name, language.lang, EasyChatTranslationCache)
                    english_name_from_multilingual = translate_given_text_to_english(multilingual_name)
                    soup = BeautifulSoup(english_name_from_multilingual)
                    english_name_from_multilingual = soup.get_text()
                    english_name_from_multilingual = re.sub(training_questions_regex, '', str(english_name_from_multilingual))
                    if english_name_from_multilingual != intent_name:
                        if english_name_from_multilingual not in training_questions:
                            training_questions.append(
                                english_name_from_multilingual)
                training_questions_set = set(training_questions)
                unique_training_questions_list = (list(training_questions_set))
                training_data_dict = {}
                for index, sentence in enumerate(unique_training_questions_list):
                    training_data_dict[str(index)] = sentence

                intent.training_data = json.dumps(training_data_dict)
                intent.save(update_fields=['training_data'])
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("add_training_questions_based_on_available_languages: %s %s in intent %s", str(e), str(exc_tb.tb_lineno), str(intent.pk), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_training_questions_based_on_available_languages: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
