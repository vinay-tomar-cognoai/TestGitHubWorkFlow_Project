import sys
import json
import uuid
from businessmessages.businessmessages_v1_messages import BusinessMessagesRepresentative
import emoji
import logging
import requests
import datetime
import threading
import websocket
from django.conf import settings
from django.utils import timezone

from EasyChatApp.rcs_business_messaging import messages
from EasyChatApp.models import BotChannel, EasyChatTranslationCache, GMBDetails, Profile, Channel, Bot, RCSDetails, TwitterChannelDetails, ViberDetails, BotInfo, BotFusionConfigurationProcessors
from EasyChatApp.utils_bot import get_translated_text
from EasyChatApp.utils_google_buisness_messages import send_text_message
from EasyChatApp.utils_twitter import send_twitter_message
from LiveChatApp.utils import get_livechat_category_object, check_for_holiday, check_for_non_working_hour, get_agent_token, get_livechat_notification, check_is_customer_blocked, get_livechat_request_packet_to_channel, open_file, get_phone_number_and_country_code, send_event_for_missed_chat, send_event_for_offline_chat
from LiveChatApp.models import LiveChatAdminConfig, LiveChatCustomer, LiveChatUser, LiveChatMISDashboard, LiveChatConfig, LiveChatCalender, LiveChatCategory, LiveChatReportedCustomer, LiveChatBotChannelWebhook, LiveChatFollowupCustomer
from LiveChatApp.constants import APPLICATION_JSON, CUSTOMER_LEFT_THE_CHAT, STOP_CONVERSATION_LIST
from LiveChatApp.utils_agent import send_facebook_message, send_instagram_message, send_whatsapp_welcome_message, send_facebook_welcome_message, send_instagram_welcome_message, send_twitter_welcome_message, send_gbm_welcome_message, send_googlercs_welcome_message, send_text_message_to_telegram
from LiveChatApp.utils_ameyo_fusion import mark_chat_expired_from_customer
from LiveChatApp.utils_custom_encryption import *
from EasyChatApp.easychat_utils_objects import *

logger = logging.getLogger(__name__)

###################         LiveChat    ###########################


def send_notification_to_agent(username, message, livechat_session_id, mobile_number, channel, path, thumbnail_url, message_id="", event_type=None):

    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                 'source': 'None', 'channel': str(channel), 'bot_id': 'None'}
    try:

        logger.info("Inside send_notification_to_agent top", extra=log_param)
        logger.info("message %s", str(message), extra=log_param)

        agent_websocket_token = get_agent_token(username)

        data = json.dumps({
            "sender": "Customer",
            "message": json.dumps({
                "text_message": message,
                "type": "message",
                "channel": channel,
                "path": path,
                "thumbnail_url": thumbnail_url,
                "session_id": livechat_session_id,
                "sender_name": mobile_number,
                "event_type": event_type,
                "message_id": message_id,
            })
        })

        thread = threading.Thread(target=send_data_to_websocket, args=(
            settings.EASYCHAT_DOMAIN, [data], agent_websocket_token), daemon=True)
        thread.start()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_notification_to_agent: " + str(e) +
                     " at " + str(exc_tb.tb_lineno), extra=log_param)


"""
function: check_for_livechat
input params:
    mobile_number: mobile number for easychat user used as user_id
output:

    This function is used to check if user has intiated livechat or not.

"""


def check_for_livechat(easychat_bot_user):
    try:
        import pytz
        import os
        tz = pytz.timezone(settings.TIME_ZONE)
        bot_obj = Bot.objects.get(pk=int(easychat_bot_user.bot_id))
        user_obj = Profile.objects.filter(
            user_id=easychat_bot_user.user_id, bot=bot_obj).order_by("-pk")[0]

        if user_obj.livechat_connected:
            return True
            livechat_session_id = user_obj.livechat_session_id

            customer_obj = LiveChatCustomer.objects.get(
                session_id=livechat_session_id)

            last_customer_message_time = customer_obj.last_appearance_date.astimezone(
                tz)
            current_time = timezone.now().astimezone(tz)

            diff_time = (current_time -
                         last_customer_message_time).total_seconds()

            # we end the livechat if their is gap of more than 5 minutes(300 seconds) between customer messages
            if diff_time <= 300:
                return True

            bot_id = customer_obj.bot.pk

            data = json.dumps({
                "sender": "System",
                "message": json.dumps({
                    "text_message": CUSTOMER_LEFT_THE_CHAT,
                    "file_type": "message",
                    "channel": easychat_bot_user.channel_name,
                    "bot_id": bot_id,
                    "event_type": "ENDBYUSER",
                    "path": "",
                    "thumbnail_url": "",
                })
            })

            thread = threading.Thread(target=send_data_to_websocket, args=(
                settings.EASYCHAT_DOMAIN, [data], livechat_session_id), daemon=True)
            thread.start()

            customer_obj.is_online = False
            customer_obj.save()
            user_obj.livechat_connected = False
            user_obj.save()

            send_notification_to_agent(
                str(customer_obj.agent_id.user.username), CUSTOMER_LEFT_THE_CHAT, livechat_session_id, easychat_bot_user.mobile_number, easychat_bot_user.channel_name, "", "")

        return False
    except Exception:
        logger.warning("LiveChat is not enabled",
                       extra=easychat_bot_user.extra)
        return False


"""
function: get_livechat_userid
input params:
    mobile_number: mobile number for easychat user used as user_id
output:

    This function is used to get livechat session id used for livechat session.
"""


def get_livechat_userid(mobile_number, channel, bot_id):
    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                 'source': 'None', 'channel': str(channel), 'bot_id': 'None'}
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        user_obj = Profile.objects.filter(
            user_id=mobile_number, bot=bot_obj).order_by("-pk")[0]
        return user_obj.livechat_session_id
    except Exception:
        logger.warning("Unable to find Profile object.", extra=log_param)
        return ""


"""
function: customer_end_livechat
input params:
    mobile_number: mobile number for easychat user used as user_id
output:

    This function is used to end livechat session.
"""


def customer_end_livechat(mobile_number, channel, bot_id, is_external=False):
    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                 'source': 'None', 'channel': str(channel), 'bot_id': 'None'}
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        user_obj = Profile.objects.filter(
            user_id=mobile_number, bot=bot_obj).order_by("-pk")[0]

        customer_obj = LiveChatCustomer.objects.get(
            session_id=user_obj.livechat_session_id)

        livechat_agent = customer_obj.agent_id

        if str(livechat_agent.user.first_name).strip() == "":
            agent_fullname = str(
                livechat_agent.user.username).strip()
        else:
            agent_fullname = str(livechat_agent.user.first_name).strip(
            ) + " " + str(livechat_agent.user.last_name).strip()

        customer_language = customer_obj.customer_language
        
        livechat_notification = get_livechat_notification(
            channel, agent_fullname, customer_language, True, EasyChatTranslationCache)

        if is_external:
            return livechat_notification
        else:
            send_channel_based_text_message(
                livechat_notification, customer_obj, user_obj.user_id)
        
        user_obj.livechat_connected = False
        user_obj.save(update_fields=['livechat_connected'])

    except Exception:
        logger.warning("Unable to end livechat.", extra=log_param)


"""
function: create_image_thumbnail
input params:
    filepath: filepath of the image whose thumbnail is to be created
    filename: name of the file
output:

    This function is used to genrate a thumbnail image  of image 
"""


def create_image_thumbnail(filepath, filename):
    thumbnail_file_path = ""
    from PIL import Image

    try:
        # skkiping first slash
        filepath = filepath.replace(settings.EASYCHAT_HOST_URL, "")
        filepath = filepath[1:]

        original_file = Image.open(filepath)

        original_file.thumbnail((80, 80))

        thumbnail_file_name = filename.split(
            '.')[0] + '_thumbnail.' + filename.split('.')[1]

        thumbnail_file_path = filepath.replace(filename, thumbnail_file_name)

        original_file.save(thumbnail_file_path)

        thumbnail_file_path = "/" + thumbnail_file_path
        # adding the first slash again

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_image_thumbnail: %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return thumbnail_file_path


"""
function: get_livechat_response
input params:
    mobile_number: mobile number for easychat user used as user_id,
    message: message sent by easychat user,
    channel: WhatsApp as of now,
    bot_id: bot pk,
    channel_params:
output:

    This function is used to get livechat response and send the message to livechat agent.
"""


def get_livechat_response(mobile_number, message, channel, bot_id, channel_params):

    from EasyChatApp.utils_execute_query import build_channel_welcome_response
    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                 'source': 'None', 'channel': str(channel), 'bot_id': 'None'}
    logger.info("INSIDE GET LIVECHAT RESPONSE top", extra=log_param)
    logger.info("message %s", str(message), extra=log_param)

    json_response = {}
    json_response["mobile_number"] = mobile_number
    json_response["status_code"] = 200
    json_response["status_message"] = "SUCCESS"
    json_response["is_livechat"] = "true"
    try:
        logger.info("INSIDE GET LIVECHAT RESPONSE", extra=log_param)
        livechat_session_id = get_livechat_userid(
            mobile_number, channel, bot_id)
        logger.info("livechat_user_id %s", str(
            livechat_session_id), extra=log_param)

        customer_obj = LiveChatCustomer.objects.get(
            session_id=livechat_session_id)
        easychat_bot_user = channel_params["easychat_bot_user"]
        easychat_params = channel_params["easychat_params"]
        is_attachment_saved = channel_params.get("is_attachment_saved")
        easychat_bot_user.bot_obj = customer_obj.bot
        easychat_params.channel_obj = customer_obj.channel
        if customer_obj.customer_language:
            easychat_bot_user.src = customer_obj.customer_language.lang
        else:
            easychat_bot_user.src = "en"

        file_attachment = None
        to_send_welcome_message = False
        whatsapp_response = {}
        channel_response = {}

        if channel == "WhatsApp" and message == "livechat_agent_end_session":
            whatsapp_response = build_channel_welcome_response(
                easychat_bot_user, easychat_params, False)
            whatsapp_response["response"]["is_whatsapp_welcome_response"] = True
            return whatsapp_response

        check_agent_assigned(customer_obj)

        try:
            if not isinstance(channel_params, dict):
                channel_params = json.loads(channel_params)

            if "attached_file_path" in channel_params:
                file_attachment = channel_params["attached_file_path"]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_livechat_response: " + str(e) +
                         " at " + str(exc_tb.tb_lineno), extra=log_param)
            file_attachment = None

        attachment_file_name = ""
        attachment_file_path = ""
        thumbnail_file_path = ""

        if file_attachment != None:
            if message == 'attachment' and is_attachment_saved is False:
                logger.error("file not saved!", extra=log_param)
                json_response["status_code"] = 500
                json_response["status_message"] = "file not saved"
                return json_response
            elif message == 'attachment':
                if "whatsapp_file_caption" in channel_params and channel_params["whatsapp_file_caption"]:
                    message = channel_params["whatsapp_file_caption"]
                else:
                    message = ""
                
            attachment_file_path = file_attachment
            attachment_file_name = file_attachment.split('/')[-1]

            # currently in livechat we are not allowing customers to send videos
            allowed_file_extensions = ["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif",
                                       "pdf", "docs", "docx", "doc"]

            file_extension = attachment_file_name.split(".")

            if len(file_extension) > 2 or file_extension[-1].lower() not in allowed_file_extensions:
                logger.error("malicious file!", extra=log_param)
                json_response["status_code"] = 500
                json_response["status_message"] = "malicious file"
                return json_response

            image_file_extentions = ["png", "PNG", "JPG", "JPEG", "jpg",
                                     "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]

            if file_extension[-1].lower() in image_file_extentions:
                thumbnail_file_path = create_image_thumbnail(
                    attachment_file_path, attachment_file_name)
            
            if "attached_complete_file_path" in channel_params:
                attachment_file_path = channel_params["attached_complete_file_path"]

        data_to_send = []
        space_filtered_message = " ".join(message.split())

        bot_fusion_config = BotFusionConfigurationProcessors.objects.filter(bot=customer_obj.bot).first()
        bot_info_obj = BotInfo.objects.filter(bot=customer_obj.bot).first()

        parameter = {}
        parameter["customer_obj"] = customer_obj
        parameter["bot_fusion_config"] = bot_fusion_config
        is_chat_disconnected = False
        customer_language = customer_obj.customer_language.lang

        if space_filtered_message.lower().strip() != "end chat" and (not check_close_conversation(space_filtered_message, customer_language)):
            livechat_mis_obj = LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                                   sender="Customer",
                                                                   text_message=message,
                                                                   sender_name=customer_obj.get_username(),
                                                                   message_time=timezone.now(),
                                                                   attachment_file_name=attachment_file_name,
                                                                   attachment_file_path=attachment_file_path,
                                                                   thumbnail_file_path=thumbnail_file_path)
            
            parameter["livechat_mis_obj"] = livechat_mis_obj

            customer_obj.last_appearance_date = datetime.datetime.now()
            customer_obj.save()

            data = json.dumps({
                "sender": "Customer",
                "message": json.dumps({
                    "text_message": message,
                    "file_type": "message",
                    "channel": channel,
                    "bot_id": bot_id,
                    "path": attachment_file_path,
                    "thumbnail_url": thumbnail_file_path,
                    "message_id": str(livechat_mis_obj.message_id),
                })
            })

            data_to_send.append(data)

            send_notification_to_agent(
                str(customer_obj.agent_id.user.username), message, livechat_session_id, mobile_number, channel, attachment_file_path, thumbnail_file_path, str(livechat_mis_obj.message_id))

        else:
            customer_end_livechat(mobile_number, channel, bot_id)
            data = json.dumps({
                "sender": "System",
                "message": json.dumps({
                    "text_message": CUSTOMER_LEFT_THE_CHAT,
                    "file_type": "message",
                    "channel": channel,
                    "bot_id": bot_id,
                    "event_type": "ENDBYUSER",
                    "path": "",
                    "thumbnail_url": "",
                })
            })
            data_to_send.append(data)

            send_notification_to_agent(
                str(customer_obj.agent_id.user.username), CUSTOMER_LEFT_THE_CHAT, livechat_session_id, mobile_number, channel, "", "")
            customer_obj.is_online = False
            customer_obj.chat_ended_by = "Customer"
            customer_obj.save()

            livechat_mis_obj = LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                                   sender="System",
                                                                   text_message=CUSTOMER_LEFT_THE_CHAT,
                                                                   sender_name="system",
                                                                   message_time=timezone.now(),
                                                                   attachment_file_name="",
                                                                   attachment_file_path="",
                                                                   thumbnail_file_path="")

            is_chat_disconnected = True
            parameter["livechat_mis_obj"] = livechat_mis_obj

            if bot_info_obj and bot_info_obj.show_welcome_msg_on_end_chat:
                channel_response = build_channel_welcome_response(
                    easychat_bot_user, easychat_params, False)
                to_send_welcome_message = True

                if channel == "WhatsApp":
                    channel_response["response"]["is_whatsapp_welcome_response"] = True

        if bot_info_obj.livechat_provider == 'ameyo_fusion' and bot_fusion_config and not is_chat_disconnected:
            if file_attachment == None:
                processor_check_dictionary = {'open': open_file}
                code = bot_fusion_config.text_message_processor.function
                exec(str(code), processor_check_dictionary)
                api_status = processor_check_dictionary['f'](parameter)
                logger.info("get_livechat_response text_message_processor api_status: " +
                            str(api_status), extra=log_param)

            else:
                processor_check_dictionary = {'open': open_file}
                code = bot_fusion_config.attachment_message_processor.function
                exec(str(code), processor_check_dictionary)
                api_status = processor_check_dictionary['f'](parameter)
                logger.info("get_livechat_response attachment_message_processor api_status: " +
                            str(api_status), extra=log_param)

        if bot_info_obj.livechat_provider == 'ameyo_fusion' and bot_fusion_config and is_chat_disconnected:

            mark_chat_expired_from_customer(customer_obj)

            processor_check_dictionary = {'open': open_file}
            code = bot_fusion_config.chat_disconnect_processor.function
            exec(str(code), processor_check_dictionary)
            api_status = processor_check_dictionary['f'](parameter)
            logger.info("get_livechat_response chat_disconnect_processor api_status: " +
                        str(api_status), extra=log_param)

        thread = threading.Thread(target=send_data_to_websocket, args=(
            settings.EASYCHAT_DOMAIN, data_to_send, livechat_session_id), daemon=True)
        thread.start()

        if to_send_welcome_message:
            return channel_response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_livechat_response: " + str(e) +
                     " at " + str(exc_tb.tb_lineno), extra=log_param)
        json_response["status_code"] = 500

    return json_response


"""
function: get_mobile_number_based_channel
input params:
    user_id: unique identifier for customer,
    channel: channel from which request was raised,
output:

    This function is returns mobile number from user_id for all channels
"""


def get_mobile_number_based_channel(user_id, channel):
    try:
        if channel in ['WhatsApp', 'GoogleRCS']:
            return user_id[-10:]

        return 'None'
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_mobile_number_based_channel: " + str(e) +
                     " at " + str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return 'None'


"""
function: create_and_enable_livechat
input params:
    mobile_number: mobile number for easychat user used as user_id,
    category: 
    channel: WhatsApp as of now,
    bot_obj:
    message:
output:

    This function is used to check for holiday ro non-working hour. If no holiday or wokring hour then it creates livechat customer.
"""


def create_and_enable_livechat(user_id, category, channel, bot_obj, message):

    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                 'source': 'None', 'channel': str(channel), 'bot_id': 'None'}
    logger.info("INSIDE create and enable livechat", extra=log_param)
    response = {}
    try:
        # Depends if whatsapp vendor provides name of customer
        bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
        mobile_number, country_code, is_valid_number = get_phone_number_and_country_code(str(user_id), channel)
        username = str(user_id)
        email = "None"
        active_url = settings.EASYCHAT_HOST_URL
        session_id = str(uuid.uuid4())

        category_obj = get_livechat_category_object(
            category, bot_obj, LiveChatCategory)

        customer_details = [{'key': 'Source', 'value': 'Others'}]

        customer_obj = None
        if channel == "WhatsApp":
            customer_obj = check_is_whatsapp_reinitiated_customer(user_id, category_obj, bot_obj)

        if not customer_obj:

            customer_obj = LiveChatCustomer.objects.create(session_id=session_id,
                                                           username=username,
                                                           phone=mobile_number,
                                                           phone_country_code=country_code,
                                                           email=email,
                                                           client_id=user_id,
                                                           is_online=True,
                                                           easychat_user_id=user_id,
                                                           bot=bot_obj,
                                                           channel=Channel.objects.get(
                                                               name=channel),
                                                           category=category_obj,
                                                           active_url=active_url,
                                                           message=message,
                                                           closing_category=category_obj,
                                                           customer_details=json.dumps(customer_details),
                                                           source_of_incoming_request='3')

        try:
            agent_unavialable_response = LiveChatConfig.objects.get(
                bot=bot_obj).agent_unavialable_response
        except Exception:
            agent_unavialable_response = "Our chat representatives are unavailable right now. Please try again in some time."

        try:
            if bot_info_obj.livechat_provider == 'cogno_livechat':
                boolian_var, response = check_for_holiday(
                    bot_obj, LiveChatCalender, LiveChatUser)

                if boolian_var:
                    customer_obj.is_denied = True
                    customer_obj.is_session_exp = True
                    customer_obj.system_denied_response = response["message"]
                    customer_obj.is_system_denied = True
                    customer_obj.last_appearance_date = timezone.now()
                    customer_obj.is_online = False
                    customer_obj.save()
                    send_event_for_offline_chat(customer_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
                    logger.error("message for holiday" +
                                 str(response["message"]), extra=log_param)
                    return response["message"], True

                boolian_var, response = check_for_non_working_hour(
                    bot_obj, LiveChatCalender, LiveChatConfig, LiveChatUser)

                if boolian_var:
                    customer_obj.is_denied = True
                    customer_obj.is_session_exp = True
                    customer_obj.system_denied_response = response["message"]
                    customer_obj.is_system_denied = True
                    customer_obj.last_appearance_date = timezone.now()
                    customer_obj.is_online = False
                    customer_obj.save()
                    send_event_for_offline_chat(customer_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
                    logger.error("message for non working hour" +
                                 str(response["message"]), extra=log_param)
                    return response["message"], True

            if check_is_customer_blocked(customer_obj, LiveChatReportedCustomer):
                response["message"] = "Our chat representatives are unavailable right now. Please try again in some time."

                customer_obj.is_denied = True
                customer_obj.is_session_exp = True
                customer_obj.system_denied_response = response["message"]
                customer_obj.is_system_denied = True
                customer_obj.last_appearance_date = timezone.now()
                customer_obj.save()
                send_event_for_offline_chat(customer_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
                logger.info("message for blocked customer" +
                            str(response["message"]), extra=log_param)

                return response["message"], True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("create_and_enable_livechat Holiday check: %s at %s", str(e), str(
                exc_tb.tb_lineno), extra=log_param)

            customer_obj.is_denied = True
            customer_obj.is_session_exp = True
            customer_obj.system_denied_response = agent_unavialable_response
            customer_obj.last_appearance_date = timezone.now()
            customer_obj.is_online = False
            customer_obj.save()
            return agent_unavialable_response, True

        user_obj = Profile.objects.filter(user_id=str(user_id), bot=bot_obj).first()

        # save language in customer_obj
        customer_obj.customer_language = user_obj.selected_language
        customer_obj.save()

        if bot_info_obj.livechat_provider == 'ameyo_fusion':
            customer_obj.is_ameyo_fusion_session = True
            customer_obj.save()

            bot_fusion_config = BotFusionConfigurationProcessors.objects.filter(
                bot=bot_obj).first()

            if bot_fusion_config:
                parameter = {}
                parameter["customer_obj"] = customer_obj
                parameter["bot_fusion_config"] = bot_fusion_config

                processor_check_dictionary = {'open': open_file}

                code = bot_fusion_config.bot_chat_history_processor.function
                exec(str(code), processor_check_dictionary)
                api_status = processor_check_dictionary['f'](parameter)

            if not bot_fusion_config or not api_status:
                response["message"] = "Our chat representatives are unavailable right now. Please try again in some time."

                customer_obj.is_denied = True
                customer_obj.is_session_exp = True
                customer_obj.system_denied_response = response["message"]
                customer_obj.is_system_denied = True
                customer_obj.last_appearance_date = timezone.now()
                customer_obj.save()

                if customer_obj.customer_language:
                    lang_obj = customer_obj.customer_language
                    response["message"] = get_translated_text(
                        response["message"], lang_obj.lang, EasyChatTranslationCache)
                return response["message"], True
        
        user_obj.livechat_connected = True
        user_obj.livechat_session_id = str(customer_obj.session_id)
        user_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_and_enable_livechat Holiday check: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra=log_param)
        return "Our chat representatives are busy right now. Please try again in some time.", True

    return "", False


"""
function: check_agent_assigned
input params:
    livechat_cust_obj: LivechatCustomer object 
output:

    This function is used to check wheter agent is assigned or not. if agent not assigned for longer than queue time it disconnects the livechat  
"""


def check_agent_assigned(livechat_cust_obj):

    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                 'source': 'None', 'channel': '', 'bot_id': 'None'}
    try:
        import time
        import pytz
        user_obj = Profile.objects.get(
            livechat_session_id=livechat_cust_obj.session_id)
        if livechat_cust_obj.is_session_exp:
            user_obj.livechat_connected = False
            user_obj.save(update_fields=['livechat_connected'])
            livechat_agent = livechat_cust_obj.agent_id

            agent_fullname = str(livechat_agent.user.first_name).strip(
            ) + " " + str(livechat_agent.user.last_name).strip()

            left_chat_text = "left the chat"
            unavailable_agent_text = "Our chat representatives are unavailable right now. Please try again in some time."

            customer_language = livechat_cust_obj.customer_language
            if customer_language and customer_language.lang != 'en':
                left_chat_text = get_translated_text(
                    left_chat_text, customer_language.lang, EasyChatTranslationCache)
                unavailable_agent_text = get_translated_text(
                    unavailable_agent_text, customer_language.lang, EasyChatTranslationCache)

            send_channel_based_text_message(
                f'{agent_fullname} {left_chat_text}', livechat_cust_obj, user_obj.user_id)

            send_channel_based_text_message(
                unavailable_agent_text, livechat_cust_obj, user_obj.user_id)

            return False

        if livechat_cust_obj.agent_id != None:
            return True

        tz = pytz.timezone(settings.TIME_ZONE)

        last_updated_time = livechat_cust_obj.joined_date.astimezone(
            tz)

        current_time = timezone.now().astimezone(tz)
        available_time = (
            current_time - last_updated_time).total_seconds()

        customer_language = livechat_cust_obj.customer_language

        if available_time >= LiveChatConfig.objects.filter(bot=livechat_cust_obj.bot)[0].queue_timer:
            send_event_for_missed_chat(livechat_cust_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)

            unavailable_agent_text = "Our chat representatives are unavailable right now. Please try again in some time."
            if customer_language and customer_language.lang != 'en':
                unavailable_agent_text = get_translated_text(
                    unavailable_agent_text, customer_language.lang, EasyChatTranslationCache)

            send_channel_based_text_message(
                unavailable_agent_text, livechat_cust_obj, user_obj.user_id)
            
            send_channel_based_welcome_message(user_obj, livechat_cust_obj)
            
            livechat_cust_obj.is_session_exp = True
            livechat_cust_obj.is_denied = True
            livechat_cust_obj.save(update_fields=['is_session_exp', 'is_denied'])

            user_obj.livechat_connected = False
            user_obj.save(update_fields=['livechat_connected'])
        else:
            assign_agent_text = "An agent will be assigned to you shortly, Please wait."
            if customer_language and customer_language.lang != 'en':
                assign_agent_text = get_translated_text(
                    assign_agent_text, customer_language.lang, EasyChatTranslationCache)

            send_channel_based_text_message(
                assign_agent_text, livechat_cust_obj, user_obj.user_id)

        return False

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Check agent assigned: %s at %s", e, str(
            exc_tb.tb_lineno), extra=log_param)

        return False


"""
function: send_channel_based_message
input params:
    livechat_cust_obj: LivechatCustomer object 
output:

    This function is used to send text reponse to a respective channel  
"""


def send_data_to_websocket(domain, data_to_send, livechat_session_id):
    try:
        ws = websocket.WebSocket()
        custom_encrypt_obj = CustomEncrypt()

        ws.connect("wss://" + domain +
                   "/ws/" + livechat_session_id + "/customer/")

        for data in data_to_send:
            data = custom_encrypt_obj.encrypt(data)
            ws.send(data)

        ws.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_data_to_websocket: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def send_channel_based_text_message(message_to_send, livechat_cust_obj, user_id, is_whatsapp_reinitiation_text=False):
    try:
        if livechat_cust_obj.channel.name == "WhatsApp":
            channel_webhook = LiveChatBotChannelWebhook.objects.filter(
                bot=livechat_cust_obj.bot, channel=livechat_cust_obj.channel)[0]
            user_obj = Profile.objects.get(user_id=user_id, bot=livechat_cust_obj.bot)
            if user_obj.livechat_connected == True or is_whatsapp_reinitiation_text == True:
                type = "text"

                request_packet = get_livechat_request_packet_to_channel(
                    user_obj.livechat_session_id, type, message_to_send, "", "WhatsApp", livechat_cust_obj.bot.pk, "")
                temp_dictionary = {'open': open_file}
                exec(str(channel_webhook.function), temp_dictionary)
                temp_dictionary['f'](request_packet)
            # send_whatsapp_text_message(
            #     message_to_send, user_id)

        if livechat_cust_obj.channel.name == "GoogleBusinessMessages":

            send_googlemybuisness_text_message(
                message_to_send, user_id, livechat_cust_obj)

        if livechat_cust_obj.channel.name == "Facebook":
            recipient_id = str(user_id).replace(
                "facebook_user_", "")
            page_access_token = BotChannel.objects.get(bot=livechat_cust_obj.bot,
                                                       channel=livechat_cust_obj.channel).page_access_token

            send_facebook_message(
                recipient_id, message_to_send, page_access_token)

        if livechat_cust_obj.channel.name == "Instagram":
            recipient_id = str(user_id).replace(
                "instagram_user_", "")
            page_access_token = BotChannel.objects.get(
                bot=livechat_cust_obj.bot, channel=livechat_cust_obj.channel).page_access_token
            send_instagram_message(
                recipient_id, message_to_send, page_access_token)

        if livechat_cust_obj.channel.name == "Twitter":

            recipient_id = str(user_id).replace(
                "twitter_user_", "")

            twitter_channel_detail_obj = TwitterChannelDetails.objects.filter(
                bot=livechat_cust_obj.bot).first()
            send_twitter_message(
                twitter_channel_detail_obj, recipient_id, message_to_send)

        if livechat_cust_obj.channel.name == "GoogleRCS":

            mobile_number = livechat_cust_obj.client_id
            mobile_number = mobile_number.rsplit('_', 1)[1]

            rcs_obj = RCSDetails.objects.filter(bot=livechat_cust_obj.bot)[0]
            service_account_location = rcs_obj.rcs_credentials_file_path

            message_text = messages.TextMessage(message_to_send)
            cluster = messages.MessageCluster().append_message(message_text)
            cluster.send_to_msisdn(mobile_number, service_account_location)

        if livechat_cust_obj.channel.name == "Viber":
            from EasyChatApp.utils_viber import viber_api_configuration, send_text_to_viber
            
            sender_id = livechat_cust_obj.client_id
            viber_obj = ViberDetails.objects.filter(
                bot=livechat_cust_obj.bot).first()

            viber_api_token = viber_obj.viber_api_token

            viber_sender_avatar = None

            viber_sender_avatar_raw = json.loads(viber_obj.viber_bot_logo)
            
            if 'sender_logo' in viber_sender_avatar_raw and len(viber_sender_avatar_raw['sender_logo']) > 0:
                viber_sender_avatar = viber_sender_avatar_raw['sender_logo'][0]

            agent_name = livechat_cust_obj.bot.name
            if livechat_cust_obj.agent_id:
                agent_name = livechat_cust_obj.agent_id.get_agent_name()

            viber_connector = viber_api_configuration(
                viber_api_token, agent_name, viber_sender_avatar)

            send_text_to_viber(viber_connector, sender_id, livechat_cust_obj.bot, message_to_send)
        
        if livechat_cust_obj.channel.name == "Telegram":
            
            send_text_message_to_telegram(livechat_cust_obj.bot.pk, message_to_send, user_id)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_channel_based_message: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def send_channel_based_welcome_message(profile_obj, customer_obj):
    try:
        from EasyChatApp.utils_execute_query import build_channel_welcome_response
        channel_name = customer_obj.channel.name
        user_id = profile_obj.user_id
        
        easychat_bot_user = EasyChatBotUser()
        easychat_bot_user.user_id = user_id
        easychat_bot_user.bot_obj = customer_obj.bot
        if customer_obj.customer_language:
            easychat_bot_user.src = customer_obj.customer_language.lang
        else:
            easychat_bot_user.src = "en"

        easychat_params = EasyChatChannelParams({}, user_id)
        easychat_params.channel_obj = customer_obj.channel

        if channel_name == "WhatsApp":
            send_whatsapp_welcome_message(profile_obj)

        if channel_name == "Telegram":
            # will be fixing this circular error during rafactoring of code base
            from EasyChatApp.telegram.utils_telegram import send_message_to_telegram_user
            bot_id = customer_obj.bot.pk

            response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)
            send_message_to_telegram_user(
                profile_obj, bot_id, response, user_id, {})
        
        if channel_name == "GoogleRCS":
            
            rcs_obj = RCSDetails.objects.filter(bot=customer_obj.bot).first()
            sender = str(user_id).replace("rcs_user_", "")
            service_account_location = rcs_obj.rcs_credentials_file_path
            
            selected_language = "en"
            if customer_obj.customer_language:
                selected_language = customer_obj.customer_language.lang
                
            response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)
            send_googlercs_welcome_message(response, selected_language, sender, service_account_location)
        
        if channel_name == "GoogleBusinessMessages":

            gmb_obj = GMBDetails.objects.filter(bot=customer_obj.bot).first()

            display_name = gmb_obj.bot_display_name
            display_image_url = gmb_obj.bot_display_image_url
            service_account_location = gmb_obj.gmb_credentials_file_path

            bot_representative = BusinessMessagesRepresentative(
                representativeType=BusinessMessagesRepresentative.RepresentativeTypeValueValuesEnum.BOT,
                displayName=display_name,
                avatarImage=display_image_url)
            
            response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)
            send_gbm_welcome_message(response, bot_representative, user_id, service_account_location)
                
        if channel_name == "Facebook":

            response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)

            sender = str(user_id).replace("facebook_user_", "")
            bot_console_obj = BotChannel.objects.filter(
                bot=customer_obj.bot, channel=customer_obj.channel).first()
            page_access_token = bot_console_obj.page_access_token

            send_facebook_welcome_message(response, sender, page_access_token)

        if channel_name == "Instagram":

            response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)

            sender = str(user_id).replace("instagram_user_", "")
            bot_console_obj = BotChannel.objects.filter(
                bot=customer_obj.bot, channel=customer_obj.channel).first()
            page_access_token = bot_console_obj.page_access_token

            send_instagram_welcome_message(response, sender, page_access_token)

        if channel_name == "Twitter":

            response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)

            sender_id = str(user_id).replace("twitter_user_", "")
            twitter_channel_detail_obj = TwitterChannelDetails.objects.filter(bot=customer_obj.bot).first()
            send_twitter_welcome_message(response, sender_id, twitter_channel_detail_obj)

        if channel_name == "Viber":

            from EasyChatApp.utils_viber import viber_api_configuration, send_welcome_message_to_viber

            bot_obj = customer_obj.bot
            viber_obj = ViberDetails.objects.filter(
                bot=bot_obj).first()
            viber_api_token = viber_obj.viber_api_token
            viber_sender_avatar = None
            viber_sender_avatar_raw = json.loads(viber_obj.viber_bot_logo)

            if 'sender_logo' in viber_sender_avatar_raw and len(viber_sender_avatar_raw['sender_logo']) > 0:
                viber_sender_avatar = viber_sender_avatar_raw['sender_logo'][0]

            viber_connector = viber_api_configuration(
                viber_api_token, bot_obj.name, viber_sender_avatar)

            bot_channel = BotChannel.objects.filter(
                bot=bot_obj, channel=customer_obj.channel).first()
            welcome_message = bot_channel.welcome_message
            initial_intent_obj = bot_obj.initial_intent
            initial_intent = ''
            initial_messages = json.loads(bot_channel.initial_messages)

            if initial_intent_obj != None:
                response = build_channel_welcome_response(easychat_bot_user, easychat_params, False)
                initial_intent = response['response']['text_response']['text']
            
            send_welcome_message_to_viber(
                viber_connector, user_id, bot_obj, welcome_message, initial_intent, initial_messages)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_channel_based_welcome_message: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def send_googlemybuisness_text_message(message, conversation_id, livechat_cust_obj):

    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                 'source': 'None', 'channel': 'GoogleBusinessMessages', 'bot_id': 'None'}
    try:

        selected_bot_obj = livechat_cust_obj.bot

        gmb_obj = GMBDetails.objects.filter(bot=selected_bot_obj)[0]

        display_name = gmb_obj.bot_display_name
        display_image_url = gmb_obj.bot_display_image_url
        service_account_location = gmb_obj.gmb_credentials_file_path

        bot_representative = BusinessMessagesRepresentative(
            representativeType=BusinessMessagesRepresentative.RepresentativeTypeValueValuesEnum.BOT,
            displayName=display_name,
            avatarImage=display_image_url)

        send_text_message(message, conversation_id,
                          bot_representative, service_account_location)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("SendGoogleMyBuisness text Failed: %s", str(e),
                     str(exc_tb.tb_lineno), extra=log_param)


def send_whatsapp_text_message(message, phone_number, preview_url=False):
    try:
        # These credentials are used for product whatsapp bot and livechat
        # testing
        log_param = {'AppName': 'LiveChatApp', 'user_id': str(phone_number),
                     'source': 'None', 'channel': 'WhatsApp', 'bot_id': 'None'}

        api_key = get_api_key("RMLBot2", "Product@123")
        logger.info("=== Inside Send WA Text Message API ===",
                    extra=log_param)
        url = "https://apis.rmlconnect.net/wba/v1/messages"
        headers = {
            'Authorization': api_key,
            'Content-Type': APPLICATION_JSON,
            'Accept': APPLICATION_JSON
        }
        if preview_url == True:
            payload = {
                "phone": "+" + phone_number,
                "text": message,
                "preview_url": True
            }
        else:
            payload = {
                "phone": "+" + phone_number,
                "text": message
            }
        logger.info("Whatsapp request packet : %s",
                    str(payload), extra=log_param)
        response = requests.request("POST", url, headers=headers, data=json.dumps(
            payload), timeout=20, verify=True)
        content = json.dumps(response.text)
        logger.info("Send WA Text API Response: %s",
                    str(content), extra=log_param)
        if str(response.status_code) == "200" or str(response.status_code) == "202":
            logger.info("Text message sent succesfully", extra=log_param)
            return True
        else:
            logger.info("Failed to Send Text Message.", extra=log_param)
            return False
    except requests.Timeout as rt:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("SendWhatsAppText API Timeout error: %s at %s",
                     str(rt), str(exc_tb.tb_lineno), extra=log_param)
        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("SendWhatsAppText API Failed: %s", str(e),
                     str(exc_tb.tb_lineno), extra=log_param)
    return False


def get_api_key(username, password):
    log_param = {'AppName': 'LiveChatApp', 'user_id': 'None',
                 'source': 'None', 'channel': 'WhatsApp', 'bot_id': 'None'}
    api_key = ""
    try:
        logger.info("=== Inside RouteMobile_get_api_key API ===",
                    extra=log_param)
        logger.info("RouteMobile Get API KEY", extra=log_param)
        url = "https://apis.rmlconnect.net/auth/v1/login/"
        payload = {
            "username": username,
            "password": password
        }
        headers = {
            'Content-Type': APPLICATION_JSON
        }
        response = requests.request("POST", url, headers=headers, data=json.dumps(
            payload), timeout=25, verify=True)
        content = json.loads(response.text)
        logger.info("RouteMobile_get_api_key Response: %s",
                    str(content), extra=log_param)
        if str(response.status_code) == "200" or str(response.status_code) == "201":
            api_key = content["JWTAUTH"]
        return api_key
    except requests.Timeout as rt:
        logger.error("RouteMobile_get_api_key Timeout error: %s",
                     str(rt), extra=log_param)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("RouteMobile_get_api_key Failed: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
    return api_key


def check_is_whatsapp_reinitiated_customer(user_id, category_obj, bot_obj):
    log_param = {'AppName': 'LiveChatApp', 'user_id': str(user_id),
                 'source': 'None', 'channel': 'WhatsApp', 'bot_id': 'None'}
                 
    try:
        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.filter(livechat_customer__client_id=user_id,
                                                                             livechat_customer__channel=Channel.objects.get(name="WhatsApp"), livechat_customer__category=category_obj,
                                                                             livechat_customer__bot=bot_obj, is_whatsapp_conversation_reinitiated=True, is_completed=False).first()

        if livechat_followup_cust_obj:

            livechat_customer_obj = livechat_followup_cust_obj.livechat_customer

            livechat_customer_obj.is_session_exp = False
            livechat_customer_obj.request_raised_date = timezone.now().date()
            livechat_customer_obj.joined_date = timezone.now()
            livechat_customer_obj.last_appearance_date = timezone.now()
            livechat_customer_obj.abruptly_closed = False
            livechat_customer_obj.is_denied = False
            livechat_customer_obj.save()

            return livechat_customer_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in check_is_whatsapp_reinitiated_customer: %s", str(e),
                     str(exc_tb.tb_lineno), extra=log_param)

    return None


def check_close_conversation(message, language):
    return language in STOP_CONVERSATION_LIST and message == STOP_CONVERSATION_LIST[language]
    
