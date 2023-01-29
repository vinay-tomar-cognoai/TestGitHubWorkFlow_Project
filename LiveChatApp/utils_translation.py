import logging
from bs4 import BeautifulSoup
import emoji
import hashlib
import enchant
import sys
import os
import requests
import json
import re
from google.cloud import translate_v2 as translate
from textblob import TextBlob
from LiveChatApp.utils import get_time, get_miniseconds_datetime

translate_client = translate.Client()
logger = logging.getLogger(__name__)


def get_translated_message_history(livechat_cust_obj, selected_language, LiveChatMISDashboard, LiveChatTranslationCache):
    message_history = []
    try:
        livechat_mis_objs = LiveChatMISDashboard.objects.filter(
            livechat_customer=livechat_cust_obj).order_by('message_time', 'pk')

        for livechat_mis_obj in livechat_mis_objs:
            if (livechat_mis_obj.text_message != None and livechat_mis_obj.text_message.strip()) or (livechat_mis_obj.attachment_file_path != None and livechat_mis_obj.attachment_file_path.strip()):
                message_history.append({
                    "message": get_translated_text(livechat_mis_obj.text_message, selected_language, LiveChatTranslationCache),
                    "sender": livechat_mis_obj.sender,
                    "sender_name": livechat_mis_obj.sender_name,
                    "time": str(get_time(livechat_mis_obj.message_time)),
                    "time_in_minisec": str(get_miniseconds_datetime(livechat_mis_obj.message_time)),
                    "attached_file_src": livechat_mis_obj.attachment_file_path,
                    "file": livechat_mis_obj.thumbnail_file_path,
                    "preview_attachment_file_path": livechat_mis_obj.preview_attachment_file_path,
                    "is_guest_agent_message": livechat_mis_obj.is_guest_agent_message,
                    "message_id": str(livechat_mis_obj.message_id),
                    "reply_message_id": livechat_mis_obj.reply_message_id,
                    "sender_username": livechat_mis_obj.sender_username,
                    "language": selected_language,
                    "is_customer_warning_message": livechat_mis_obj.is_customer_warning_message,
                    "is_customer_report_message_notification": livechat_mis_obj.is_customer_report_message_notification,
                    "is_voice_call_message": livechat_mis_obj.is_voice_call_message,
                    "is_video_call_message": livechat_mis_obj.is_video_call_message,
                    "is_cobrowsing_message": livechat_mis_obj.is_cobrowsing_message,
                    "original_message": livechat_mis_obj.text_message,
                    "message_for": livechat_mis_obj.message_for,
                })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_translated_message_history %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return message_history


def get_translated_text(text, selected_language, LiveChatTranslationCache, remove_whitespace=False, is_agent_name=False):
    try:
        input_text_hash_data = hashlib.md5(text.encode()).hexdigest()
        if LiveChatTranslationCache.objects.filter(input_text_hash_data=input_text_hash_data, lang=selected_language):
            translated_text = LiveChatTranslationCache.objects.filter(
                input_text_hash_data=input_text_hash_data, lang=selected_language).first().translated_data

            return translated_text

        # We didn't have translated data
        if is_agent_name:
            translated_text, is_translation_api_passed = translate_via_api_agent_name(
                text, selected_language, remove_whitespace)
        else:
            translated_text, is_translation_api_passed = translat_via_api(
                text, selected_language)
        if not is_translation_api_passed:
            return text

        LiveChatTranslationCache.objects.create(input_text_hash_data=input_text_hash_data,
                                                input_text=text, translated_data=translated_text, lang=selected_language)
        
        return translated_text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_translated_text %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return text


def translat_via_api(text, selected_language):
    try:
        result = translate_client.translate(
            text, target_language=selected_language)
        translated_text = result['translatedText']
        translated_text = BeautifulSoup(
            translated_text, "html.parser").text.strip()
        return translated_text, True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('translat_via_api! %s %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return text, False


def translate_via_api_agent_name(text, selected_language, remove_whitespace):
    try:
        result = translate_client.translate(
            text, target_language=selected_language)
        translated_text = result['translatedText']
        translated_text = unwrap_do_not_translate_keywords(translated_text, remove_whitespace)
        return translated_text, True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('translat_via_api! %s %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return text, False


def unwrap_do_not_translate_keywords(text, remove_whitespace):
    try:
        if remove_whitespace:
            span_pattern = "\s?<span[^>]*>|<\/span>\s?"
        else:
            span_pattern = "<span[^>]*>|<\/span>"
        tags = re.findall(span_pattern, text)
        for tag in tags:
            text = text.replace(tag, "")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('unwrap_do_not_translate_keywords! %s %s',
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return text.strip()
