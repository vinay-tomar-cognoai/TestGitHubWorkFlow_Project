import sys
import json
import logging
import os
import requests
from django.conf import settings
from django.db.models import Q, Count

from bs4 import BeautifulSoup
from AuditTrailApp.utils import add_audit_trail
from LiveChatApp.utils_custom_encryption import *

from LiveChatApp.utils_validation import *
from LiveChatApp.utils import create_image_thumbnail, create_video_thumbnail, get_livechat_request_packet_to_channel, open_file, save_transfer_audit
from LiveChatApp.constants import *
from EasyChatApp.utils_facebook import send_facebook_message, send_facebook_livechat_agent_response
from EasyChatApp.utils_instagram import send_instagram_message, send_instagram_livechat_agent_response
from EasyChatApp.utils_google_buisness_messages import create_recommendation_list, gbm_text_formatting, send_image_response, send_message_with_suggestions, send_text_message, send_gbm_livechat_agent_response
from EasyChatApp.models import EasyChatTranslationCache, GMBDetails, Profile, BotChannel, Bot, TwitterChannelDetails, User, RCSDetails, ViberDetails, WhatsAppWebhook, TelegramDetails
from EasyChatApp.utils_twitter import send_twitter_message, send_twitter_livechat_agent_response, process_recommendations_for_quick_reply, DMAttachment
from LiveChatApp.models import LiveChatBotChannelWebhook, LiveChatProcessors, LiveChatUser, LiveChatCustomer, LiveChatTransferAudit
from businessmessages.businessmessages_v1_messages import BusinessMessagesRepresentative
from EasyChatApp.rcs_business_messaging import messages
from EasyChatApp.utils_rcs import send_rcs_livechat_agent_response
from EasyChatApp.utils_bot import get_emojized_message, get_translated_text
import datetime
import time
import fnmatch
import glob

logger = logging.getLogger(__name__)


def check_if_uploded_livechat_file_is_valid(base64_content, file_name):

    status = 200
    status_message = "File is Valid"
    try:
        file_validation_obj = LiveChatFileValidation()

        file_size = (len(base64_content) * 3) / 4 - \
            base64_content.count('=', -2)

        if file_validation_obj.check_malicious_file(file_name):
            status = 500
            status_message = 'Malicious File'
            return status, status_message

        file_extension = file_name.split(".")[-1].lower()

        allowed_file_extensions = ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "jpe", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg", "mp2",
                                   "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt", "flv", "swf", "avchd", "pdf", "docs", "docx", "doc", "PDF", "txt", "TXT"]

        if file_size > 5000000:
            status = 500
            status_message = 'File Size Bigger Than Expected'
            return status, status_message

        if file_extension not in allowed_file_extensions:
            status = 500
            status_message = 'Malicious File'
            return status, status_message

        if file_validation_obj.check_malicious_file_from_content(base64_content, allowed_file_extensions):
            status = 500
            status_message = 'Malicious File'
            return status, status_message

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_if_uploded_livechat_file_is_valid: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return status, status_message


def check_if_file_name_exist(file_name, path):
    try:
        original_file_name = file_name
        file_name = file_name.rsplit('.', 1)[0]
        file_extension = original_file_name.split(".")[-1].lower()
        num = ''

        file_name_pattern = file_name + "(*)." + file_extension
        files_exist = fnmatch.filter((f for f in os.listdir(path)), original_file_name)
        multiple_files_exist = fnmatch.filter((f for f in os.listdir(path)), file_name_pattern)

        if not files_exist:  
            # is empty
            num = ''
        elif len(multiple_files_exist) == 0:    
            # file with same name exists
            num = '(1)'
        else:   
            # multiple files with same name exists 
            list_of_files = glob.glob(path + file_name_pattern)

            # last updated file
            latest_file = max(list_of_files, key=os.path.getctime)  

            curr_max_count = latest_file.rsplit('(', 1)[1]
            curr_max_count = curr_max_count.rsplit(')', 1)[0]
            curr_max_count = int(curr_max_count)
            num = '(%i)' % (curr_max_count + 1)

        new_file_name = file_name + str(num) + "." + file_extension
        return new_file_name
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_if_file_name_exist: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return file_name


def save_file_and_get_source_file_path_and_thumbnail_path(base64_content, file_name, LiveChatFileAccessManagement):
    file_url = ""
    thumbnail_url = ""
    try:

        path = os.path.join(settings.SECURE_MEDIA_ROOT,
                            "LiveChatApp/attachment/")
        file_extension = file_name.split(".")[-1].lower()

        file_name = check_if_file_name_exist(file_name, path)

        fh = open(path + file_name, "wb")
        fh.write(base64.b64decode(base64_content))
        fh.close()

        path = "/secured_files/LiveChatApp/attachment/" + file_name

        file_access_management_obj = LiveChatFileAccessManagement.objects.create(
            file_path=path, is_public=False)

        file_url = '/livechat/download-file/' + \
            str(file_access_management_obj.key) + '/' + file_name

        thumbnail_file_name = ""
        if file_extension in ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "jfif", "tiff", "exif", "bmp", "gif", "GIF"]:
            thumbnail_file_name = create_image_thumbnail(file_name)
        elif file_extension in ["MPEG", "mpeg", "MP4", "mp4", "MOV", "mov", "AVI", "avi", "flv"]:
            thumbnail_file_name = create_video_thumbnail(file_name)

        thumbnail_url = ""

        if thumbnail_file_name != "":
            path_of_thumbnail = "/secured_files/LiveChatApp/attachment/" + thumbnail_file_name
            file_access_management_obj = LiveChatFileAccessManagement.objects.create(
                file_path=path_of_thumbnail, is_public=False)

            thumbnail_url = '/livechat/download-file/' + \
                str(file_access_management_obj.key) + \
                '/' + thumbnail_file_name

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_file_and_get_source_file_path_and_thumbnail_path: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return file_url, thumbnail_url


def send_agent_livechat_response_based_on_channel(customer_obj, session_id, channel_message, attached_file_src, data, sender_name, translated_text):
    try:
        if customer_obj.channel.name == "WhatsApp":
            channel_webhook = LiveChatBotChannelWebhook.objects.filter(
                bot=customer_obj.bot, channel=customer_obj.channel)[0]
            user_obj = Profile.objects.get(livechat_session_id=session_id)
            if user_obj.livechat_connected == True:
                type = "text"
                if attached_file_src != "":
                    type = "file"
                    if "channel_file_url" in data:
                        attached_file_src = data["channel_file_url"]

                if translated_text == "":
                    translated_text = channel_message

                request_packet = get_livechat_request_packet_to_channel(
                    session_id, type, translated_text, attached_file_src, "WhatsApp", customer_obj.bot.pk, sender_name)
                temp_dictionary = {'open': open_file}
                exec(str(channel_webhook.function), temp_dictionary)
                temp_dictionary['f'](request_packet)

        if customer_obj.channel.name == "GoogleBusinessMessages":

            send_gbm_livechat_agent_response(
                customer_obj, session_id, channel_message, attached_file_src, data, sender_name, Profile, Bot, GMBDetails)

        if customer_obj.channel.name == "Facebook":

            if translated_text == "":
                translated_text = channel_message

            send_facebook_livechat_agent_response(
                translated_text, customer_obj, session_id, attached_file_src, data, BotChannel, Profile)

        if customer_obj.channel.name == "Instagram":

            send_instagram_livechat_agent_response(
                channel_message, customer_obj, session_id, attached_file_src, data, BotChannel, Profile)

        if customer_obj.channel.name == "Twitter":

            twitter_channel_detail_obj = TwitterChannelDetails.objects.filter(
                bot=customer_obj.bot).first()

            send_twitter_livechat_agent_response(
                channel_message, customer_obj, session_id, attached_file_src, data, twitter_channel_detail_obj, Profile)

        if customer_obj.channel.name == "GoogleRCS":

            send_rcs_livechat_agent_response(
                customer_obj, session_id, channel_message, attached_file_src, data, sender_name, Profile, Bot, RCSDetails)

        if customer_obj.channel.name == "Viber":

            from EasyChatApp.utils_viber import send_viber_livechat_agent_response

            if translated_text == "":
                translated_text = channel_message

            send_viber_livechat_agent_response(customer_obj, session_id, translated_text, attached_file_src, data, sender_name, Profile, Bot, ViberDetails)
        
        if customer_obj.channel.name == "Telegram":

            if translated_text == "":
                translated_text = channel_message

            send_telegram_livechat_agent_response(customer_obj, session_id, translated_text, attached_file_src, data, sender_name, Profile)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_agent_livechat_response_based_on_channel: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def auto_assign_agent(transfer_session_data, category_obj, data, request):
    try:
        response = {}
        agent_list = {}

        current_livechat_agent = transfer_session_data["current_livechat_agent"]
        livechat_cust_obj = transfer_session_data["livechat_cust_obj"]
        max_customer_count = transfer_session_data["max_customer_count"]

        livechat_agents = list(LiveChatUser.objects.filter(
            status="3", is_online=True, category__in=[category_obj], bots__in=[livechat_cust_obj.bot]).order_by('last_chat_assigned_time').values_list('user__username', flat=True).exclude(pk=current_livechat_agent.pk))

        for agent in livechat_agents:
            agent_list[agent] = 0

        current_agent_list = LiveChatCustomer.objects.filter(is_session_exp=False, request_raised_date=datetime.datetime.now(
        ).date()).filter(~Q(agent_id=None)).values('agent_id__user__username').annotate(total=Count('agent_id')).order_by("total")

        for agent in current_agent_list:
            if agent["agent_id__user__username"] in livechat_agents:
                agent_list[agent["agent_id__user__username"]
                           ] = agent["total"]
        logger.info("PRINTING ALL LIVECHAT AGENTS",
                    extra={'AppName': 'LiveChat'})
        logger.info(livechat_agents, extra={'AppName': 'LiveChat'})

        for agent in livechat_agents:
            livechat_agent = LiveChatUser.objects.get(
                user=User.objects.get(username=agent))
            logger.info("Agent process started in Transfer Chat %s and last assigned customer was at %s", str(
                agent), str(livechat_agent.last_chat_assigned_time), extra={'AppName': 'LiveChat'})

            logger.info("Agent assigned cutomer count in Transfer Chat %s", str(
                agent_list[agent]), extra={'AppName': 'LiveChat'})

            if max_customer_count > agent_list[agent]:

                update_transfer_session_objects_and_audit_trails(
                    transfer_session_data, livechat_agent, agent_list[agent], request, data)

                response["status_code"] = "200"
                if livechat_cust_obj.channel.name == "Facebook":
                    response["assigned_agent"] = "*" + str(
                        livechat_agent.user.first_name) + " " + str(livechat_agent.user.last_name) + "*"
                else:
                    response["assigned_agent"] = str(
                        livechat_agent.user.first_name) + " " + str(livechat_agent.user.last_name)
                response["assigned_agent_username"] = str(
                    livechat_agent.user.username)
                response["session_id"] = str(
                    livechat_cust_obj.session_id)
                response["previous_assigned_agent"] = str(
                    current_livechat_agent.user.first_name) + " " + str(current_livechat_agent.user.last_name)
            else:
                logger.info(
                    "Into AssignAgentAPI.....max_customer_count exceeded", extra={'AppName': 'LiveChat'})
                response["status_code"] = "300"
                response["assigned_agent"] = "no_agent_online"
                response["assigned_agent_username"] = "None"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside auto_assign_agent %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        logger.info("No agent available.....max_customer_count exceeded", extra={
            'AppName': 'LiveChat'})
        response["status_code"] = "300"
        response["assigned_agent"] = "no_agent_online"
        response["assigned_agent_username"] = "None"

    return response


def assign_selected_agent(transfer_session_data, selected_agent, data, request):
    try:
        response = {}

        current_livechat_agent = transfer_session_data["current_livechat_agent"]
        livechat_cust_obj = transfer_session_data["livechat_cust_obj"]
        max_customer_count = transfer_session_data["max_customer_count"]

        livechat_agent = LiveChatUser.objects.get(
            pk=int(selected_agent), is_deleted=False)
        current_assigned_customer_count = LiveChatCustomer.objects.filter(
            is_session_exp=False, request_raised_date=datetime.datetime.now().date(), agent_id=livechat_agent).count()

        if max_customer_count > current_assigned_customer_count:

            update_transfer_session_objects_and_audit_trails(
                transfer_session_data, livechat_agent, current_assigned_customer_count, request, data)

            response["status_code"] = "200"
            if livechat_cust_obj.channel.name == "Facebook":
                response["assigned_agent"] = "*" + str(
                    livechat_agent.user.first_name) + " " + str(livechat_agent.user.last_name) + "*"
            else:
                response["assigned_agent"] = str(
                    livechat_agent.user.first_name) + " " + str(livechat_agent.user.last_name)

            response["assigned_agent_username"] = str(
                livechat_agent.user.username)
            response["session_id"] = str(livechat_cust_obj.session_id)
            response["previous_assigned_agent"] = str(
                current_livechat_agent.user.first_name) + " " + str(current_livechat_agent.user.last_name)
        else:
            logger.info(
                "Into AssignAgentAPI.....max_customer_count exceeded", extra={'AppName': 'LiveChat'})
            response["status_code"] = "300"
            response["assigned_agent"] = "no_agent_online"
            response["assigned_agent_username"] = "None"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside assign_selected_agent %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        logger.info("Cannot be assigned to the selected agent.....max_customer_count exceeded", extra={
                    'AppName': 'LiveChat'})
        response["status_code"] = "300"
        response["assigned_agent"] = "no_agent_online"
        response["assigned_agent_username"] = "None"

    return response


def update_transfer_session_objects_and_audit_trails(transfer_session_data, livechat_agent, current_ongoing_chat, request, data):
    try:

        transfer_description = ""
        current_livechat_agent = transfer_session_data["current_livechat_agent"]
        livechat_cust_obj = transfer_session_data["livechat_cust_obj"]
        cust_last_app_time = transfer_session_data["cust_last_app_time"]

        livechat_agent.ongoing_chats = current_ongoing_chat + 1
        livechat_agent.resolved_chats += 1
        livechat_agent.save()
        save_transfer_audit(current_livechat_agent, livechat_agent, livechat_cust_obj,
                            transfer_description, LiveChatTransferAudit)
        livechat_cust_obj.last_appearance_date = datetime.datetime.fromtimestamp(
            int(cust_last_app_time) / 1000.0)
        livechat_cust_obj.agent_id = livechat_agent
        livechat_cust_obj.unread_message_count = 1
        livechat_cust_obj.agents_group.add(livechat_agent)
        livechat_cust_obj.save()

        description = "Transferred Chat from agent id" + \
            " (" + str(current_livechat_agent.pk) + \
            " to agent with id " + str(livechat_agent.pk) + ")"
        add_audit_trail(
            "LIVECHATAPP",
            current_livechat_agent.user,
            "Transfer-Chat",
            description,
            json.dumps(data),
            request.META.get("PATH_INFO"),
            request.META.get('HTTP_X_FORWARDED_FOR')
        )

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside update_transfer_session_objects_and_audit_trails: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def push_livechat_event(event_type, customer_obj, extra_details={}):
    try:
        processor_check_dictionary = {'open': open_file}
        processor_obj = LiveChatProcessors.objects.filter(bot=customer_obj.bot)

        if processor_obj:
            processor_obj = processor_obj.first()

            code = processor_obj.push_api.function
            exec(str(code), processor_check_dictionary)
            
            parameter = {
                'event_type': event_type,
                'session_id': str(customer_obj.session_id),
            }

            parameter.update(extra_details)

            response = processor_check_dictionary['f'](parameter)

            if not isinstance(response, (dict)):
                response = json.loads(response)

            if response['status_code'] == 200:
                logger.info(
                    "Event pushed successfully", extra={'AppName': 'LiveChat'})
            else:
                logger.error("Event push failed", extra={'AppName': 'LiveChat'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside push_livechat_event: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        

"""
function: send_text_message_to_telegram
input_params:
    bot_id: 
    message: 
    chat_id: 

This function is used to send text message to telegram user.
"""


def send_text_message_to_telegram(bot_id, message, chat_id):
    try:
        telegram_obj = TelegramDetails.objects.filter(bot__pk=bot_id)[0]
        telegram_url = telegram_obj.telegram_url + telegram_obj.telegram_api_token

        for char in "[]()~`>#+-=|{}.!":
            message = message.replace(char, "\\" + char)

        url = telegram_url + "/sendMessage?chat_id=" + \
            str(chat_id) + "&text=" + str(message) + "&parse_mode=MarkdownV2"

        response = requests.get(url)
        logger.info("Response after sendng messag is %s", str(response.text), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] send_text_message_to_telegram %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: send_media_message_to_telegram
input_params:
    bot_id: 
    file_type: 
    file_path: 
    chat_id: 
    caption

This function is used to send media message to telegram user.
"""


def send_media_message_to_telegram(bot_id, file_type, file_path, chat_id, caption=""):
    try:
        telegram_obj = TelegramDetails.objects.filter(bot__pk=bot_id)[0]
        telegram_url = telegram_obj.telegram_url + telegram_obj.telegram_api_token

        if file_type == "image":
            url = telegram_url + "/sendPhoto?chat_id=" + \
                str(chat_id) + "&photo=" + str(file_path) + \
                "&caption=" + str(caption) + "&parse_mode=MarkdownV2"
        else:
            url = telegram_url + "/sendDocument?chat_id=" + \
                str(chat_id) + "&document=" + \
                str(file_path) + "&caption=" + str(caption) + "&parse_mode=MarkdownV2"

        response = requests.get(url)
        logger.info("Response after sendng messag is %s", str(response.text), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] send_text_message_to_telegram %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_file_type(file_name):
    try:
        file_ext = file_name.split(".")[-1]

        if file_ext.lower() in ["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]:
            return "image"

        elif file_ext.upper() in ["WEBM", "MPG", "MP2", "MPEG", "MPE", "MPV", "OGG", "MP4", "M4P", "M4V", "AVI", "WMV", "MOV", "QT", "FLV", "SWF", "AVCHD"]:
            return "video"

        elif file_ext.lower() in ["pdf", "docs", "docx", "doc", "PDF", "txt", "TXT"]:
            return "file"
        else:
            return "invalid file format"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return "invalid file format"


def send_telegram_livechat_agent_response(customer_obj, session_id, message, attached_file_src, data, sender_name, Profile):
    response = {}
    response["status"] = 200
    try:
        user_obj = Profile.objects.get(livechat_session_id=session_id)
        user_id = user_obj.user_id
        
        if user_obj.livechat_connected:

            if attached_file_src != "":

                if "channel_file_url" in data:

                    attached_file_src = data["channel_file_url"]

                    try:
                        attached_file_src = settings.EASYCHAT_HOST_URL + attached_file_src

                        file_type = get_file_type(attached_file_src)
                        
                        if file_type != "invalid file format":
                            send_media_message_to_telegram(customer_obj.bot.pk, file_type, attached_file_src, user_id)
                    
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("send_viber_livechat_agent_response: %s at %s",
                                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            if message != "":
                send_text_message_to_telegram(customer_obj.bot.pk, message, user_id)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_telegram_livechat_agent_response %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response["status"] = 500

    return response


def send_whatsapp_welcome_message(user_obj):

    try:
        bot_obj = user_obj.bot
        request_packet = {
            "contacts": [
                {
                    "profile": {
                        "name": ""
                    },
                    "wa_id": user_obj.user_id
                }
            ],
            "messages": [
                {
                    "from": user_obj.user_id,
                    "id": "",
                    "text": {
                          "body": "livechat_agent_end_session"
                    },
                    "timestamp": str(int(datetime.datetime.now().timestamp())),
                    "type": "text"
                }
            ],
            "bot_id": bot_obj.id
        }

        if WhatsAppWebhook.objects.all().count() > 0:
            whatsapp_webhook_obj = WhatsAppWebhook.objects.filter(
                bot=bot_obj)
            if whatsapp_webhook_obj:
                result_dict = {}
                exec(str(whatsapp_webhook_obj[
                     0].function), result_dict)
                result_dict['whatsapp_webhook'](request_packet)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_whatsapp_welcome_message: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})   
           
        
def send_googlercs_welcome_message(response, selected_language, sender, service_account_location):
    try:
        text_response = response["response"]["text_response"]["text"]
        recom_list = response['response']['recommendations']
        image_urls = response["response"]["images"]
        videos = response["response"]["videos"]

        validation_obj = LiveChatInputValidation()
        text_response = validation_obj.remo_html_from_string(text_response)
        text_response = validation_obj.unicode_formatter(text_response)

        text_response_list = []

        for small_message in text_response.split("$$$"):
            if small_message != "":
                text_response_list.append(small_message)

        for response in text_response_list:
            #  1st case
            message_text = messages.TextMessage(response)

            # Send text message to the device
            cluster = messages.MessageCluster().append_message(message_text)
            cluster.send_to_msisdn(sender, service_account_location)

        if len(image_urls) > 0:
            for url in image_urls:
                FileMessage = messages.FileMessage(url)
                cluster = messages.MessageCluster().append_message(FileMessage)
                cluster.send_to_msisdn(sender, service_account_location)

        if len(videos) >= 1:
            for url in videos:
                FileMessage = messages.FileMessage(url)

                # Append rich card and send to the user
                cluster = messages.MessageCluster().append_message(FileMessage)
                cluster.send_to_msisdn(sender, service_account_location)
        
        if len(recom_list) > 0:
            text_message = 'suggestions for you'
            translated_text = get_translated_text(text_message, selected_language, EasyChatTranslationCache)
            text_msg = messages.TextMessage(translated_text)
            cluster = messages.MessageCluster().append_message(text_msg)
            recom_list = recom_list[:11]  # max limit is 11 as per rcs guidelines for suggestions
            for recom in recom_list:
                if(type(recom) is dict):
                    if len(recom["name"]) <= 25:
                        cluster.append_suggestion_chip(messages.SuggestedReply(recom["name"], recom["name"]))
                    else:
                        cluster.append_suggestion_chip(messages.SuggestedReply(recom["name"][:23] + "..", recom["name"]))
                else:
                    if len(recom) <= 25:
                        cluster.append_suggestion_chip(messages.SuggestedReply(recom, recom))
                    else:
                        cluster.append_suggestion_chip(messages.SuggestedReply(recom[:23] + "..", recom))
            cluster.send_to_msisdn(sender, service_account_location)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_whatsapp_welcome_message: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})  
        

def send_gbm_welcome_message(response, bot_representative, conversation_id, service_account_location):
    try:
        
        images = response["response"]["images"]
        videos = response["response"]["videos"]
        recommendations = response["response"]["recommendations"]
        recommendation_list = create_recommendation_list(
            recommendations)

        validation_obj = LiveChatInputValidation()

        message = response['response']['text_response']['text']
        message = gbm_text_formatting(message)
        message = validation_obj.remo_html_from_string(message)
        message = validation_obj.unicode_formatter(message)

        if (len(images) > 0):
            for img in images:
                send_image_response(
                    img, conversation_id, bot_representative, service_account_location)
        if (len(videos) > 0):
            for video in videos:
                send_text_message(
                    validation_obj.youtube_link_formatter(video), conversation_id, bot_representative, service_account_location)

        suggestions = recommendation_list

        if (len(suggestions) > 0):
            send_message_with_suggestions(
                message, suggestions, conversation_id, bot_representative, service_account_location)
            
        if (len(suggestions) == 0):

            send_text_message(message, conversation_id,
                                bot_representative, service_account_location)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_gbm_welcome_message: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})  
        

def send_facebook_welcome_message(response, sender, page_access_token):
    try:
        from EasyChatApp.utils_facebook import html_tags_formatter, html_list_formatter, send_recommendations_carousel, send_images

        text_response = response["response"]["text_response"]["text"]
        text_response = html_tags_formatter(text_response)
        text_response = html_list_formatter(text_response)
        text_response = get_emojized_message(text_response)
        recommendations = response['response']['recommendations']
        
        if "</a>" in text_response:
            soup = BeautifulSoup(text_response)
            for a_tag in soup.findAll('a'):
                a_tag.replaceWith(a_tag['href'].replace(" ", "-"))
            text_response = str(soup).replace(
                "<html><body><p>", "").replace("</p></body></html>", "")

        image_urls = response["response"]["images"]

        validation_obj = LiveChatInputValidation()

        text_response = validation_obj.remo_html_from_string(text_response)
        text_response = validation_obj.unicode_formatter(text_response)
        for small_message in text_response.split("$$$"):
            if small_message != "":
                send_facebook_message(sender, small_message, page_access_token)
                time.sleep(0.05)

        videos = response["response"]["videos"]
        if len(videos) > 0:
            for video in videos:
                send_facebook_message(sender, video, page_access_token)

        if len(recommendations) > 0:
            send_recommendations_carousel(
                sender, page_access_token, recommendations=recommendations)
        
        if len(image_urls) > 0:
            send_images(sender, image_urls, page_access_token)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_facebook_welcome_message: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})        


def send_instagram_welcome_message(response, sender, page_access_token):
    try:
        from EasyChatApp.utils_instagram import send_recommendations_carousel, send_images

        text_response = response["response"]["text_response"]["text"]
        recommendations = response['response']['recommendations']

        text_response = text_response.replace("<br>", " ")
        text_response = text_response.replace("<b>", "")
        text_response = text_response.replace("</b>", "")
        text_response = text_response.replace("<i>", "")
        text_response = text_response.replace("</i>", "")
        text_response = text_response.replace("*", "")

        if "</a>" in text_response:
            soup = BeautifulSoup(text_response)
            for a_tag in soup.findAll('a'):
                a_tag.replaceWith(a_tag['href'].replace(" ", "-"))
            text_response = str(soup).replace(
                "<html><body><p>", "").replace("</p></body></html>", "")

        image_urls = response["response"]["images"]

        validation_obj = LiveChatInputValidation()

        text_response = validation_obj.remo_html_from_string(text_response)
        text_response = validation_obj.unicode_formatter(text_response)

        for small_message in text_response.split("$$$"):
            if small_message != "":
                send_instagram_message(sender, small_message, page_access_token)
                time.sleep(0.05)

        videos = response["response"]["videos"]
        if len(videos) > 0:
            for video in videos:
                send_instagram_message(sender, video, page_access_token)

        if len(recommendations) > 0:
            send_recommendations_carousel(
                sender, page_access_token, recommendations=recommendations)

        if len(image_urls) > 0:
            send_images(sender, image_urls, page_access_token)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_instagram_welcome_message: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})  


def send_twitter_welcome_message(response, sender_id, twitter_channel_detail_obj):
    try:

        text_response = response["response"]["text_response"]["text"]
        recommendations = response['response']['recommendations']

        text_response = text_response.replace("<br>", " ")
        text_response = text_response.replace("<b>", "")
        text_response = text_response.replace("</b>", "")
        text_response = text_response.replace("<i>", "")
        text_response = text_response.replace("</i>", "")
        text_response = text_response.replace("*", "")

        if "</a>" in text_response:
            soup = BeautifulSoup(text_response)
            for a_tag in soup.findAll('a'):
                a_tag.replaceWith(a_tag['href'].replace(" ", "-"))
            text_response = str(soup).replace(
                "<html><body><p>", "").replace("</p></body></html>", "")

        image_urls = response["response"]["images"]
        video_urls = response["response"]["videos"]

        validation_obj = LiveChatInputValidation()

        text_response = validation_obj.remo_html_from_string(
            text_response)
        text_response = validation_obj.unicode_formatter(text_response)

        recom_list = []
        if len(recommendations) > 0:
            recom_list += process_recommendations_for_quick_reply(
                recommendations)

        message_list = text_response.split("$$$")

        if len(message_list) > 1:
            for small_message in message_list[:-1]:
                if small_message != "":
                    send_twitter_message(
                        twitter_channel_detail_obj, sender_id, small_message)
                    time.sleep(0.05)

        final_message = message_list[-1]
        send_twitter_message(twitter_channel_detail_obj, sender_id, final_message,
                             recommendation_options=recom_list)

        dm_attachment = DMAttachment()
        if len(image_urls) > 0:
            for image_url in image_urls:
                dm_attachment.send_attachment(twitter_channel_detail_obj, sender_id, image_url)

        if len(video_urls) > 0:
            for video_url in video_urls:
                send_twitter_message(twitter_channel_detail_obj, sender_id, video_url)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_twitter_welcome_message: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})  
