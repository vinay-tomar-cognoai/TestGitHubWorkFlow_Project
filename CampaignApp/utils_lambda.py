import json
import sys
from CampaignApp.utils import get_unique_template_variable_body
from EasyChatApp.models import Bot, BotChannel, EasyChatSessionIDGenerator, TimeSpentByUser, WhatsAppUserSessionMapper
from django.utils import timezone
import re

import logging
logger = logging.getLogger(__name__)

log_param = {'AppName': 'Campaign', 'user_id': 'None',
             'source': 'None', 'channel': 'WhatsApp', 'bot_id': 'None'}


def convert_timestamp_to_normal(timestamp):
    from datetime import datetime
    dt_object = datetime.fromtimestamp(timestamp)
    return dt_object


def get_bot_id_from_audience_log_obj(audience_log_obj, default_bot_id):
    try:
        bot_id = audience_log_obj.campaign.bot.pk
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in get_bot_id_from_audience_log_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
        bot_id = default_bot_id
    
    return bot_id


def check_and_create_session_if_required(user_id, bot_id):
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
        whatsapp_user_session_obj = WhatsAppUserSessionMapper.objects.filter(
            user_id=user_id, bot=bot_obj).first()

        if (not whatsapp_user_session_obj) or (not whatsapp_user_session_obj.session_obj):

            easychat_session_obj = EasyChatSessionIDGenerator.objects.create()
            session_id = str(easychat_session_obj.token)
            if not whatsapp_user_session_obj:
                WhatsAppUserSessionMapper.objects.create(
                    user_id=user_id, session_obj=easychat_session_obj, is_session_started=True, is_business_initiated_session=True, bot=bot_obj)
            else:
                session_id = update_whatsapp_session_obj(
                    whatsapp_user_session_obj, easychat_session_obj)

        elif whatsapp_user_session_obj.is_current_session_obj_is_longer_than_tweenty_four_hours():
            session_id = update_whatsapp_session_obj(
                whatsapp_user_session_obj, None, True)
        else:
            session_id = whatsapp_user_session_obj.session_obj.token

        check_and_create_time_spent_by_user(
            user_id, session_id, timezone.now(), bot_id)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_create_session_if_required: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)


def update_whatsapp_session_obj(whatsapp_user_session_obj, easychat_session_obj, is_business_initiated=False):
    try:
        if not easychat_session_obj:
            easychat_session_obj = EasyChatSessionIDGenerator.objects.create()

        whatsapp_user_session_obj.session_obj = easychat_session_obj
        whatsapp_user_session_obj.is_session_started = True
        whatsapp_user_session_obj.is_business_initiated_session = is_business_initiated
        whatsapp_user_session_obj.save()

        return str(easychat_session_obj.token)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_whatsapp_session_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
        return ""


def check_and_create_time_spent_by_user(user_id, session_id, start_datetime, bot_id):
    try:
        time_spent_by_user_objs = TimeSpentByUser.objects.filter(
            user_id=user_id, session_id=session_id)

        if time_spent_by_user_objs.exists():
            return

        bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

        TimeSpentByUser.objects.create(user_id=user_id, session_id=session_id,
                                       start_datetime=start_datetime, end_datetime=start_datetime, bot=bot_obj)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_create_time_spent_by_user: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)


def get_session_id_based_on_user_session(user_id, bot_id, is_bot_initiated=False):

    try:
        bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
        whatsapp_user_session_obj = WhatsAppUserSessionMapper.objects.filter(
            user_id=user_id, bot=bot_obj).first()

        if whatsapp_user_session_obj and whatsapp_user_session_obj.session_obj:
            is_business_initiated_session = False
            session_id = whatsapp_user_session_obj.session_obj.token

            if (whatsapp_user_session_obj.is_current_session_obj_is_longer_than_tweenty_four_hours()):
                is_business_initiated_session = True if is_bot_initiated else False
                session_id = update_whatsapp_session_obj(
                    whatsapp_user_session_obj, None, is_business_initiated_session)

            return str(session_id), True, whatsapp_user_session_obj.is_business_initiated_session
        else:
            easychat_session_obj = EasyChatSessionIDGenerator.objects.create()
            is_business_initiated_session = True if is_bot_initiated else False
            if not whatsapp_user_session_obj:
                WhatsAppUserSessionMapper.objects.create(
                    user_id=user_id, session_obj=easychat_session_obj, is_session_started=True, is_business_initiated_session=is_business_initiated_session, bot=bot_obj)
            else:
                whatsapp_user_session_obj.session_obj = easychat_session_obj
                whatsapp_user_session_obj.save()

            session_id = str(easychat_session_obj.token)
            check_and_create_time_spent_by_user(
                user_id, session_id, timezone.now(), bot_id)

            return session_id, False, is_business_initiated_session
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_session_id_based_on_user_session: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

        return "", False, False


# This function retrieves the language source from the campaign template language string Eg: English (UK) (en_GB)
def get_language_from_campaign_template_string(text):
    try:
        res = re.findall(r'\(.*?\)', text)
        res = res[-1][1:-1]
        res = res.split("_")
        return res[0]
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in get_language_from_campaign_template_string: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
        return "en"


def is_this_language_supported_by_bot(bot_obj, lang_code, channel_obj):

    is_lang_supported = False
    try:
        bot_channel = BotChannel.objects.filter(
            bot=bot_obj, channel=channel_obj).first()
        supported_language = bot_channel.languages_supported.all().filter(lang=lang_code)

        is_lang_supported = supported_language.exists()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_this_language_supported_by_bot! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return is_lang_supported


def campaign_json_response_creator(campaign_template_obj, campaign_message_body, campaign_request_packet, response_json):
    try:
        response_json['response']['text'] = campaign_message_body
        response_json['response']['is_video'] = False
        response_json['response']['is_image'] = False
        response_json['response']['is_document'] = False
        response_json['response']['is_cta'] = False
        response_json['response']['is_callus'] = False
        response_json['response']['is_qr'] = False
        response_json['response']['is_header'] = False
        response_json['response']['is_footer'] = False
        template_metadata = json.loads(campaign_template_obj.template_metadata)
        template_callus_text = template_metadata.get('callus_text')
        template_qr_1 = template_metadata.get('template_qr_1')
        template_qr_2 = template_metadata.get('template_qr_2')
        template_qr_3 = template_metadata.get('template_qr_3')
        type_of_first_cta_button = template_metadata.get(
            'type_of_first_cta_btton')
        template_parameters = campaign_request_packet.get(
            "template", {}).get("components", [])[0].get("parameters", [])[0]

        if campaign_template_obj.template_type.title == 'video':
            response_json['response']['is_video'] = True
            response_json['response']['video'] = [
                template_parameters.get("video", {}).get("link", "")]
        if campaign_template_obj.template_type.title == 'image':
            response_json['response']['is_image'] = True
            response_json['response']['image'] = [
                template_parameters.get("image", {}).get("link", "")]
        if campaign_template_obj.template_type.title == 'document':
            response_json['response']['is_document'] = True
            response_json['response']['document'] = [
                template_parameters.get("document", {}).get("link", "")]
            response_json['response']['document_name'] = template_parameters.get(
                "document", {}).get("filename", "Document")
        if campaign_template_obj.cta_text:
            response_json['response']['is_cta'] = True
            response_json['response']['cta_text'] = campaign_template_obj.cta_text
        if template_callus_text:
            response_json['response']['is_callus'] = True
            response_json['response']['callus_text'] = template_callus_text
        if type_of_first_cta_button:
            response_json['response']['type_of_first_cta_button'] = type_of_first_cta_button
        if template_qr_1 or template_qr_2 or template_qr_3:
            response_json['response']['is_qr'] = True
            response_json['response']['template_qr_1'] = template_qr_1
            response_json['response']['template_qr_2'] = template_qr_2
            response_json['response']['template_qr_3'] = template_qr_3
        if campaign_template_obj.template_header:
            response_json['response']['is_header'] = True
            header_text = campaign_template_obj.template_header
            if '{{' in header_text:
                header_variable = []
                if campaign_request_packet['template']['components'][0]['type'] == 'header':
                    header_variable = campaign_request_packet['template']['components'][0]['parameters']
                temp_var = []
                for variables in header_variable:
                    temp_var.append(variables.get('text'))
                header_variable = temp_var
                header_text = get_unique_template_variable_body(
                    header_text, header_variable)
                header_text = header_text.replace("{{", '').replace("}}", '')

            response_json['response']['header_text'] = header_text
        if campaign_template_obj.template_footer:
            response_json['response']['is_footer'] = True
            response_json['response']['footer_text'] = campaign_template_obj.template_footer
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in campaign_json_response_creator: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
    return response_json
