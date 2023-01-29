import logging
from bs4 import BeautifulSoup
import emoji
import hashlib
import enchant
import sys
import os
import requests
import json
import html
from google.cloud import translate_v2 as translate
from textblob import TextBlob
from EasyChatApp.text_or_emoji_recognition import *
from EasyChatApp.constants import OLDER_NEWER_LANGUAGE_CODE_MAPPING

translate_client = translate.Client()
logger = logging.getLogger(__name__)


##################################### HINDI IDENTIFICATION MODULE ####################
"""
  To check if there are no hindi characters in the sentence.
  If it does, then no need to call hinglish to hindi api.
"""
"""
# commented
def does_it_look_english(phrase):
    import re
    pattern = "[a-zA-Z]"
    result = bool(re.search(pattern, phrase))
    return result
"""


def does_it_look_english(phrase):
    try:
        phrase.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


"""
  To check if a sentence is in english.
"""


def is_english(sentence, WhitelistedEnglishWords):

    try:
        # Checking if sentence is in devanagri
        english_words = ""
        final_flag = True
        if not does_it_look_english(sentence):
            return False, english_words, sentence

        # whitelisted words to be considered as english
        whitelisted_words = []
        if WhitelistedEnglishWords.objects.all().count():
            whitelisted_words = [word.lower().strip(
            ) for word in WhitelistedEnglishWords.objects.all()[0].keywords.split(',')]
        logger.info("is_english whitelisted_words: %s", str(whitelisted_words), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        # check if splited keyword is in english or not
        enchant_obj = enchant.Dict("en_UK")
        sentence_array = sentence.split(" ")
        sentence = ""
        for word in sentence_array:

            if word == "":
                continue

            if not word.isalpha() or word.lower() in whitelisted_words or word in emoji.UNICODE_EMOJI or enchant_obj.check(word):
                english_words += " " + word
                # sentence = sentence.replace(word, " ") will not work --> it will remove "I" from "SBI", if sentence is "I want SBI credit card."
            else:
                sentence += " " + word
                final_flag = False

        logger.info("is_english sentence: %s", str(sentence), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        logger.info("is_english Flag: %s", str(final_flag), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return final_flag, english_words, sentence
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('is_english! Error:  %s at %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return final_flag, english_words, sentence


"""
  translitrate_text_to_target_language
  this function  will convert  "mera naam kya hai" to "मेरा नाम क्या है"
"""


def translitrate_text_to_target_language(text, to_convert_into):
    try:
        url = "https://www.google.com/inputtools/request?text=" + text + \
            "&ime=transliteration_en_" + to_convert_into + \
            "&num=1&cp=0&cs=1&ie=utf-8&oe=utf-8&app=test"
        payload = {}
        headers = {}
        response = requests.request(
            "GET", url, headers=headers, data=payload, timeout=20)
        content = json.loads(response.text)
        translitrated_phrase = content[1][0][1][0]
        return str(translitrated_phrase)
    except requests.Timeout as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('translitrate_text_to_target_language! API Timeout:  %s %s',
                     str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return text
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('translitrate_text_to_target_language! Error:  %s at %s',
                     str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return text


"""

Checking if the current text has been translated before to english
"""


def check_for_translated_data(message, selected_language, EasyChatTranslationCache):
    try:

        input_text_hash_data = hashlib.md5(message.encode()).hexdigest()
        translated_objs = EasyChatTranslationCache.objects.filter(
            input_text_hash_data=input_text_hash_data, lang=selected_language)

        if translated_objs.exists():
            return True, translated_objs.first().translated_data

        return False, message
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('check_for_translated_data! Error:  %s at %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False, message


def translate_given_text_to_english(message):
    translated_text = message
    try:
        result = translate_client.translate(message, target_language='en')
        translated_text = result['translatedText']
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('translate_given_text_to_english! Error:  %s at %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        meta_data = "translate_given_text_to_english! Error " + str(e)
        create_translation_api_failure_log(message, meta_data)
    return translated_text


def process_string_for_other_languages(message, src, bot_info_obj, WhitelistedEnglishWords):
    try:
        if src == "en":
            return message
        is_lang_diff, detected_language = get_detected_language_from_text(
            src, message, bot_info_obj, WhitelistedEnglishWords)

        if detected_language == "en":
            return message

        if not is_lang_diff:
            message = translitrate_text_to_target_language(
                message, detected_language)
        # for better translation acurracy we are first translitrating text then translating it into english for eg namaste is detected hindi but
        # translating it will give us namaste only so converting namste into नमस्ते then its translation will be Hi which is required

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('process_string_for_other_languages! Error:  %s at %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return message


def is_words_whitelisted(message, bot_info_obj, WhitelistedEnglishWords):
    try:
        message_without_english_words = remove_whitelisted_english_words(
            message, bot_info_obj.bot, WhitelistedEnglishWords).strip()

        return message_without_english_words == ""

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('is_words_whitelisted! Error:  %s at %s', str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return False


def check_and_get_if_reverse_translation_cache_exists(message, src, EasyChatTranslationCache):
    translated_english_message = ""
    try:
        output_text_hash_data = hashlib.md5(message.encode()).hexdigest()
        translated_cache_obj = EasyChatTranslationCache.objects.filter(output_text_hash_data=output_text_hash_data, lang=src).first()
        if translated_cache_obj:
            translated_english_message = translated_cache_obj.input_text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('check_and_get_if_reverse_translation_cache_exists! Error:  %s at %s', str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return translated_english_message


def check_and_get_message_after_translation(message, src, easychat_bot_user, WhitelistedEnglishWords, EasyChatTranslationCache, bot_info_obj=None):
    translated_text = message
    if easychat_bot_user:
        bot_info_obj = easychat_bot_user.bot_info_obj
    try:
        if src == "en":
            return translated_text

        if not is_message_to_be_translated(message, bot_info_obj):
            return translated_text

        if is_words_whitelisted(message, bot_info_obj, WhitelistedEnglishWords):
            return translated_text

        translated_english_message = check_and_get_if_reverse_translation_cache_exists(message, src, EasyChatTranslationCache)
        if translated_english_message:
            return translated_english_message

        message = process_string_for_other_languages(
            message, src, bot_info_obj, WhitelistedEnglishWords)
        translated_text = message

        translation_check, translated_text = check_for_translated_data(
            message, "en", EasyChatTranslationCache)

        if not translation_check:
            translated_text = translate_given_text_to_english(message)

            if message != translated_text:
                input_text_hash_data = hashlib.md5(message.encode()).hexdigest()
                output_text_hash_data = hashlib.md5(translated_text.encode()).hexdigest()
                EasyChatTranslationCache.objects.create(input_text_hash_data=input_text_hash_data, output_text_hash_data=output_text_hash_data, input_text=message, translated_data=translated_text, lang="en")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('check_and_get_message_after_translation! Error:  %s at %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return translated_text

# def google_translate_text(message, src, WhitelistedEnglishWords, EasyChatTranslationCache):
#     translated_text = message
#     english_words = ""
#     try:
#         try:
#             english_flag, english_words, sentence = is_english(
#                 message, WhitelistedEnglishWords)
#             if english_flag:
#                 language_detected = "en"
#             else:
#                 language_detected = src
#                 translated_text = sentence

#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error('is_english! %s %s',
#                          str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#             blob = TextBlob('   ' + str(message))
#             language_detected = blob.detect_language()

#         if language_detected != 'en':
#             if does_it_look_english(translated_text):
#                 message = translitrate_text_to_target_language(
#                     translated_text, src)
#                 print(message)
#                 message = BeautifulSoup(message).text.strip()

#             translation_check, translated_text = check_for_translated_data(message, src, EasyChatTranslationCache)
#             print(translation_check , translated_text)
#             if not translation_check:
#                 result = translate_client.translate(message, target_language='en')
#                 translated_text = result['translatedText'] + " " + english_words
#                 translated_text = BeautifulSoup(translated_text).text.strip()

#         else:
#             translated_text = sentence + english_words

#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error('google_translate_text! %s %s',
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#     return translated_text


"""
This function helps to translate text to selected lanaguage using google translate API.
"""


def translat_via_api(text, selected_language):
    try:
        extracted_text_or_emoji = give_text_or_emoji(text)
        # this condition checks if only have emojis as text then return it as it is
        if extracted_text_or_emoji == None or extracted_text_or_emoji.strip() == "":
            return text, True
        if not is_message_to_be_translated(text):
            return text, True
        result = translate_client.translate(
            text, target_language=selected_language, format_='html')
        translated_text = result['translatedText']

        # translated_text = BeautifulSoup(translated_text).text.strip() # Translation was working fine with html tags without striping
        if translated_text.strip() == "":
            return text, False

        # Adding html.unescape because translation api is returning encoded text for e.g. for "'" it is returning "&#39;"
        return html.unescape(translated_text), True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('translat_via_api! %s %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        meta_data = "translate via api! Error " + str(e)
        create_translation_api_failure_log(text, meta_data)
        return text, False


def remove_whitelisted_english_words(sentence, bot_obj, WhitelistedEnglishWords):

    try:
        sanatized_sentence = " " + sentence.lower() + " "
        # adding empty space in front and end for our removing whitlist word algorithm to work properly
        whitelisted_words = []
        whiltlisted_eng_words_obj = WhitelistedEnglishWords.objects.filter(
            bot_obj=bot_obj)
        if whiltlisted_eng_words_obj.exists():
            whitelisted_words = [word.lower().strip(
            ) for word in whiltlisted_eng_words_obj.first().keywords.split(',')]

        for word in whitelisted_words:
            word = " " + word.strip().lower() + " "
            # adding space on right and left so that consisting words dont get replaced for eg if cool is whitelisted and sentence  is "coolness is great"
            #  it does not change it to "ness is great" adding spaces so that if complete words is thier then only replace it
            if word in sanatized_sentence:
                sanatized_sentence = sanatized_sentence.replace(word, " ")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('remove_whitelisted_english_words! %s %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return sanatized_sentence.strip()


"""
  To get detetcted language from text and is language diffrent from expected langauge or not
"""


def get_detected_language_from_text(src, message, bot_info_obj, WhitelistedEnglishWords):
    is_language_diffrent = False

    detected_language = src
    try:
        message_without_english_words = remove_whitelisted_english_words(
            message, bot_info_obj.bot, WhitelistedEnglishWords)

        logger.info("message after removal of english words is - " + str(message_without_english_words), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        result = translate_client.detect_language(
            message_without_english_words)
        confidence = result["confidence"]

        # Below lines of code is added because sometimes google api's give us older language code for the language but our database has new language codes
        # e.g. "iw" for Hebrew instead of "he"
        if result["language"] in OLDER_NEWER_LANGUAGE_CODE_MAPPING:
            result["language"] = OLDER_NEWER_LANGUAGE_CODE_MAPPING[result["language"]]

        logger.info("confidence is - " + str(confidence) + " for detected language " + str(result["language"]), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        if confidence >= bot_info_obj.threshold_confidence_for_language_detection and result["language"] != "und":
            detected_language = result["language"]
            if "-" in detected_language:
                # In some cases language code can be in form of hi-Latn, so we split it with - to get language code
                detected_language = detected_language.split("-")[0]

        logger.info("Detected Language for text - " + str(message) + " is " + str(detected_language), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        is_language_diffrent = not (detected_language == src)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('get_detected_language_from_text! %s %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        meta_data = "get_detected_language_from_text! Error " + str(e)
        create_translation_api_failure_log(message, meta_data)

    return is_language_diffrent, detected_language


"""
    Checks if message is only number/email/PAN/date
"""


def is_message_to_be_translated(message, bot_info_obj=None):
    import re

    temp_message = message.replace(" ", "")
    if re.match('[\d!-\/:-@[-`{-~]+$', temp_message):
        return False

    # Wrapping message inside div tag as BeautifulSoup returns empty string if closing tag is present at the begining
    # for e.g --> "</p><p><em>I am here to help you</em></p>"
    soup = BeautifulSoup("<div>" + message + "</div>")

    if soup.get_text().strip() == "":
        return False

    pan_pattern = re.compile(r"[a-zA-Z]{3}[pP][a-zA-Z][1-9][0-9]{3}[a-zA-Z]")
    if re.sub(pan_pattern, '', message) == '':
        return False

    email_pattern = re.compile(r"\S+@\S+")
    if re.sub(email_pattern, '', message) == '':
        return False

    # Regex date format: dd AUG YYYY
    date_format_ddmonthnameyyyy = re.compile(
        r"[\d]{1,2} [ADFJMNOS]\w* [\d]{2,4}")
    if re.sub(date_format_ddmonthnameyyyy, '', message) == '':
        return False

    # Regex date format: AUG dd YYYY
    date_format_monthnameddyyyy = re.compile(
        r"[ADFJMNOS]\w* [\d]{1,2} [\d]{2,4}")
    if re.sub(date_format_monthnameddyyyy, '', message) == '':
        return False

    if bot_info_obj:
        do_not_translate_regex_list = bot_info_obj.get_do_not_translate_regex_list()
        for regex in do_not_translate_regex_list:
            re_format = re.compile(str(regex))
            if re.sub(re_format, '', message) == '':
                return False

    return True


def create_translation_api_failure_log(text, meta_data):
    try:
        from EasyChatApp.models import LanguageApiFailureLogs

        LanguageApiFailureLogs.objects.create(text=text, meta_data=meta_data)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('create_translation_api_failure_log! %s %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
  To update whitelisted english words
"""

# will be used later to add white listed words
# from frontend module
# def update_WhitelistedEnglishWords(sentence):
#     is_updated = False
#     try:
#         logger.info("Inside update_WhitelistedEnglishWords",extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id':'None'})
#         logger.info("update_WhitelistedEnglishWords sentence: %s", str(sentence), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id':'None'})
#         sentence = sentence.lower()
#         wenw_objs = WhitelistedEnglishWords.objects.all()
#         if wenw_objs.count() == 0:
#             wenw_obj = WhitelistedEnglishWords.objects.create(keywords="hii, hie")
#         else:
#             wenw_obj = wenw_objs[0]
#         whitelisted_words = [word.strip() for word in wenw_obj.keywords.split(',')]
#         for word in sentence.split():
#             if not is_english(word) and word.lower().strip() not in whitelisted_words:
#                 whitelisted_words.append(word.lower().strip())
#         whitelisted_str = ", ".join(whitelisted_words)
#         wenw_obj.keywords = whitelisted_str
#         wenw_obj.save()
#         logger.info("update_WhitelistedEnglishWords: %s", str(wenw_obj.keywords), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id':'None'})
#         is_updated = True
#     except Exception as E:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("update_WhitelistedEnglishWords error: %s at %s",str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id':'None'})
#     return is_updated

################################# END IDENTIFICATION MODULE ##########################
