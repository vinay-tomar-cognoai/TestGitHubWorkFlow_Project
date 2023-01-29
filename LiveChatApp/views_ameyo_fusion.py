import sys
import json
import uuid
import logging
import datetime
import urllib.parse
import html

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# Django imports
from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from EasyChat import settings
from LiveChatApp.utils import *
from LiveChatApp.models import *
from EasyChatApp.models import User, Bot, Channel, MISDashboard, BotFusionConfigurationProcessors
from LiveChatApp.constants import *
from LiveChatApp.utils_translation import get_translated_text
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils_ameyo_fusion import *
from LiveChatApp.utils_validation import *
 
IST = pytz.timezone("Asia/Kolkata")

# Logger
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class FusionCreateCustomerAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            logger.info("inside room creation for fusion", extra={'AppName': 'LiveChat'})
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            bot_id = data["bot_id"]
            username = data["username"]
            phone = data["phone"]
            email = data["email"]
            livechat_category = data["livechat_category"]
            message = data["message"]
            easychat_user_id = data["easychat_user_id"]
            channel = "Web"
            active_url = data["active_url"]
            customer_details = data['customer_details']
            bot_obj = Bot.objects.get(pk=int(bot_id))
            client_id = phone
            phone_number, country_code, is_valid_number = get_phone_number_and_country_code(phone, channel)

            validation_obj = LiveChatInputValidation()

            language_obj = None
            customer_language = ""
            if "customer_language" in data:
                customer_language = data["customer_language"]
                lang_obj = Language.objects.filter(lang=customer_language)
                if lang_obj.exists():
                    language_obj = lang_obj[0]

            username = username.strip()
            if customer_language == 'en' and not validation_obj.validate_name(username) or not len(username):
                response["status_code"] = "400"
                response["status_message"] = "Please enter a valid name"

            if not validation_obj.validate_email(email):
                response["status_code"] = "400"
                response["status_message"] = "Please enter a valid email."

            if not validation_obj.validate_phone_number_with_country_code(phone) or not is_valid_number:
                response["status_code"] = "400"
                response["status_message"] = "Please enter a valid phone number."
            
            if response["status_code"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)

            if "client_id" in data:
                client_id = data["client_id"]

            if "channel" in data:
                channel = data["channel"]

            session_id = str(uuid.uuid4())

            set_livechat_session_in_profile(
                session_id, channel, phone, bot_obj, Profile)
            category_obj = get_livechat_category_object(
                livechat_category, bot_obj, LiveChatCategory)

            ip_address = get_ip_address(request)
            
            livechat_cust_obj = LiveChatCustomer.objects.create(session_id=session_id,
                                                                username=username.strip(),
                                                                phone=phone_number,
                                                                phone_country_code=country_code,
                                                                email=email,
                                                                is_online=True,
                                                                easychat_user_id=easychat_user_id,
                                                                message=message,
                                                                channel=Channel.objects.get(
                                                                    name=channel),
                                                                category=category_obj,
                                                                active_url=active_url,
                                                                bot=bot_obj,
                                                                client_id=client_id,
                                                                customer_details=json.dumps(customer_details),
                                                                customer_language=language_obj,
                                                                ip_address=ip_address,
                                                                is_ameyo_fusion_session=True)
            livechat_cust_obj.closing_category = livechat_cust_obj.category
            livechat_cust_obj.save()

            bot_fusion_config = BotFusionConfigurationProcessors.objects.filter(bot=bot_obj).first()

            if bot_fusion_config:
                parameter = {}
                parameter["customer_obj"] = livechat_cust_obj
                parameter["bot_fusion_config"] = bot_fusion_config

                processor_check_dictionary = {'open': open_file}

                code = bot_fusion_config.bot_chat_history_processor.function
                exec(str(code), processor_check_dictionary)
                api_status = processor_check_dictionary['f'](parameter)

            if not bot_fusion_config or not api_status:
                response["status_code"] = "300"
                response["message"] = "Our chat representatives are unavailable right now. Please try again in some time."
                response["assigned_agent"] = "fusion_not_configured"
                response["assigned_agent_username"] = "None"

                livechat_cust_obj.is_denied = True
                livechat_cust_obj.is_session_exp = True
                livechat_cust_obj.system_denied_response = response["message"]
                livechat_cust_obj.is_system_denied = True
                livechat_cust_obj.last_appearance_date = timezone.now()
                livechat_cust_obj.save()
                send_event_for_offline_chat(livechat_cust_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)

                if livechat_cust_obj.customer_language:
                    lang_obj = livechat_cust_obj.customer_language
                    response["message"] = get_translated_text(response["message"], lang_obj.lang, LiveChatTranslationCache)

                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)
        
            response["status_code"] = "200"
            response["session_id"] = session_id

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FusionCreateCustomer: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


FusionCreateCustomer = FusionCreateCustomerAPI.as_view()


class SaveFusionCustomerChatAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
    
            validation_obj = LiveChatInputValidation()

            session_id = data["session_id"]
            message = data["message"]
            sender = data["sender"]
            attached_file_src = data["attached_file_src"]
            thumbnail_file_path = data["thumbnail_file_path"]
            preview_attachment_file_path = ""
            if "preview_file_src" in data:
                preview_attachment_file_path = data["preview_file_src"]
            is_chat_disconnected = data["is_chat_disconnected"]

            session_id = validation_obj.remo_html_from_string(session_id)
            message = validation_obj.remo_html_from_string(message)
            message = validation_obj.remo_special_tag_from_string(message)
            sender = validation_obj.remo_html_from_string(sender)
            attached_file_src = validation_obj.remo_html_from_string(
                attached_file_src)

            attachment_file_name = ""
            if attached_file_src != "":
                attachment_file_name = attached_file_src.split("/")[-1]
            logger.info("inside SaveCustomerChatAPI:",
                        extra={'AppName': 'LiveChat'})

            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)

            # Creating chat objects of bot and customer messages if customer starts messaging before
            # agent opens the chat.
            update_message_history_till_now(
                customer_obj, LiveChatMISDashboard, MISDashboard)

            sender_name = customer_obj.get_username() if sender == "Customer" else "System"

            livechat_mis_obj = LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                                   sender=sender,
                                                                   text_message=message,
                                                                   sender_name=sender_name,
                                                                   message_time=timezone.now(),
                                                                   attachment_file_name=attachment_file_name,
                                                                   attachment_file_path=attached_file_src,
                                                                   thumbnail_file_path=thumbnail_file_path,
                                                                   preview_attachment_file_path=preview_attachment_file_path,
                                                                   message_for='customer')
            customer_obj.last_appearance_date = timezone.now()
            customer_obj.unread_message_count += 1
            customer_obj.save()

            if "chat_ended_by" in data and data["chat_ended_by"] != "":
                customer_obj.chat_ended_by = data["chat_ended_by"]
                customer_obj.save()

            bot_fusion_config = BotFusionConfigurationProcessors.objects.filter(bot=customer_obj.bot).first()
            parameter = {}
            parameter["customer_obj"] = customer_obj
            parameter["bot_fusion_config"] = bot_fusion_config
            parameter["livechat_mis_obj"] = livechat_mis_obj

            if bot_fusion_config and not is_chat_disconnected:
                if attached_file_src == "":

                    processor_check_dictionary = {'open': open_file}
                    code = bot_fusion_config.text_message_processor.function
                    exec(str(code), processor_check_dictionary)
                    api_status = processor_check_dictionary['f'](parameter)

                else:
                    processor_check_dictionary = {'open': open_file}
                    code = bot_fusion_config.attachment_message_processor.function
                    exec(str(code), processor_check_dictionary)
                    api_status = processor_check_dictionary['f'](parameter)

            if bot_fusion_config and is_chat_disconnected:

                mark_chat_expired_from_customer(customer_obj)

                processor_check_dictionary = {'open': open_file}
                code = bot_fusion_config.chat_disconnect_processor.function
                exec(str(code), processor_check_dictionary)
                api_status = processor_check_dictionary['f'](parameter)

            if api_status: 
                response["status_code"] = "200"
            else:
                response["status_code"] = "500"
            response["message_id"] = str(livechat_mis_obj.message_id)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveFusionCustomerChatAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveFusionCustomerChat = SaveFusionCustomerChatAPI.as_view()


class PullMessageFromAmeyoAgentAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = "Internal server Error"
        try:
            data = request.data
            logger.error("Pull message data %s", str(data), extra={'AppName': "LiveChat"})
            bot_id = data['bot_id']
            livechat_session_id = data['livechat_session_id']
            agent_id = data['agent_id']
            sender = data['sender']
            message = data['message']
            message_time = data['message_time']
            message_type = data['message_type']
            attachment_file_name = data["attachment_file_name"]
            attachment_file_ext = data["attachment_file_ext"]
            attachment_file_url = data["attachment_file_url"]
            is_agent_online = data["is_agent_online"]
            ameyo_identifier = "None"

            if "identifier" in data:
                ameyo_identifier = data["identifier"]

            status_message = "The following fields cannot be blank or null: "
            status_code = "200"
            status_code, status_message = check_if_null_or_blank("BotID", bot_id, status_message, status_code)
            status_code, status_message = check_if_null_or_blank("Livechat Session Id", livechat_session_id, status_message, status_code)
            status_code, status_message = check_if_null_or_blank("Agent ID", agent_id, status_message, status_code)
            status_code, status_message = check_if_null_or_blank("Sender", sender, status_message, status_code)
            status_code, status_message = check_if_null_or_blank("Message Time", message_time, status_message, status_code)
            status_code, status_message = check_if_null_or_blank("Message Type", message_type, status_message, status_code)
            status_code, status_message = check_if_null_or_blank("Agent Online", is_agent_online, status_message, status_code)

            if status_code == "401":
                response["status_code"] = "401"
                response["status_message"] = status_message
                return Response(data=response)

            try:
                message = html.escape(message)
            except:
                pass

            customer_obj = LiveChatCustomer.objects.filter(session_id=livechat_session_id).first()

            if not customer_obj:
                response["status_code"] = "500"
                response["status_message"] = "This customer livechat session id does not exist."

            if customer_obj.is_session_exp:
                response["status_code"] = "400"
                response["status_message"] = "Chat has already ended"
                return Response(data=response)

            if is_agent_online:

                if message_type == "text":
                    if customer_obj.channel.name == "WhatsApp":
                        save_and_send_data_to_agent_via_webhook(customer_obj, message, "", "", "", False, ameyo_identifier, LiveChatMISDashboard, LiveChatTranslationCache)
                    else:
                        save_and_send_data_to_agent_via_socket(customer_obj, message, "", "", "", False, LiveChatMISDashboard, LiveChatTranslationCache)

                if message_type == "file":
                    if customer_obj.channel.name == "WhatsApp":
                        path, file_name, thumbnail_url = save_whatsapp_livechat_file_to_system(attachment_file_name, attachment_file_ext, attachment_file_url, LiveChatFileAccessManagement) 
                        save_and_send_data_to_agent_via_webhook(customer_obj, message, path, file_name, thumbnail_url, True, ameyo_identifier, LiveChatMISDashboard, LiveChatTranslationCache)
                    else:
                        path, file_name, thumbnail_url = save_livechat_file_to_system(attachment_file_name, attachment_file_ext, attachment_file_url, LiveChatFileAccessManagement) 
                        save_and_send_data_to_agent_via_socket(customer_obj, message, path, file_name, thumbnail_url, True, LiveChatMISDashboard, LiveChatTranslationCache)

            else:
                save_and_send_data_to_agent_via_webhook(customer_obj, message, "", "", "", False, ameyo_identifier, LiveChatMISDashboard, LiveChatTranslationCache)
                mark_chat_expired(customer_obj)

            response["status_code"] = "200"
            response["status_message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("PullMessageFromAmeyoAgent: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})
            response["status_code"] = "500"
            response["status_message"] = str(e)
            response["status_line"] = str(exc_tb.tb_lineno)

        return Response(data=response)


PullMessageFromAmeyoAgent = PullMessageFromAmeyoAgentAPI.as_view()


class AssignAgentRequestAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = "Internal server Error"
        try:
            data = request.data
            logger.error("Assign Agent data %s", str(data), extra={'AppName': "LiveChat"})
            bot_id = data['bot_id']
            livechat_session_id = data['livechat_session_id']
            # customer_name = data['customer_name']
            # customer_phone_number = data['customer_phone_number']
            # customer_email_id = data['customer_email_id']
            customer_channel = data['customer_channel']
            assign_status = data['assign_status']
            agent_name = data['agent_name']
            agent_id = data['agent_id']
            message = data['message']
            identifier = data['identifier']

            status_message = "The following fields cannot be blank or null: "
            status_code = "200"
            status_code, status_message = check_if_null_or_blank("BotID", bot_id, status_message, status_code)
            status_code, status_message = check_if_null_or_blank("Livechat Session Id", livechat_session_id, status_message, status_code)
            status_code, status_message = check_if_null_or_blank("Customer Channel", customer_channel, status_message, status_code)
            status_code, status_message = check_if_null_or_blank("Assign Status", assign_status, status_message, status_code)
            status_code, status_message = check_if_null_or_blank("Message", message, status_message, status_code)

            if status_code == "401":
                response["status_code"] = "401"
                response["status_message"] = status_message
                return Response(data=response)

            customer_obj = LiveChatCustomer.objects.filter(session_id=livechat_session_id).first()

            if not customer_obj:
                response["status_code"] = "500"
                response["status_message"] = "This customer livechat session id does not exist."

            if customer_obj.is_session_exp:
                response["status_code"] = "400"
                response["status_message"] = "Chat has already ended"
                return Response(data=response)

            logger.error("identifier %s", str(identifier), extra={'AppName': "LiveChat"})

            if identifier in ["AGENT_LEFT_CHAT", "ALL_AGENTS_BUSY", "OFFLINE_CHAT_COMPLETION_MESSAGE"]:
                customer_obj.is_session_exp = True
                customer_obj.is_denied = True
                customer_obj.save()
            
            if identifier in ["AGENT_JOINED_CHAT"] and customer_obj.channel.name == "WhatsApp":
                save_and_send_data_to_agent_via_webhook(customer_obj, message, "", "", "", False, "AGENT_JOINED_CHAT", LiveChatMISDashboard, LiveChatTranslationCache)

            if agent_id == "":
                if customer_obj.channel.name == "WhatsApp" and identifier != "SEARCHING_FOR_AGENTS_FOR_NEW_CHAT":
                    save_and_send_data_to_agent_via_webhook(customer_obj, message, "", "", "", False, "AGENT_JOINED_CHAT", LiveChatMISDashboard, LiveChatTranslationCache)

                response["status_code"] = "200"
                response["status_message"] = "waiting for response"
                return Response(data=response)

            livechat_agent = LiveChatUser.objects.filter(ameyo_agent_id=agent_id, is_deleted=False).first()
            if not livechat_agent:
                livechat_agent = create_ameyo_agent(agent_id, agent_name, customer_obj.bot, LiveChatCategory, LiveChatUser, User)

            if not livechat_agent:
                response["status_code"] = "500"
                response["status_message"] = "This agent id does not exist."
                return Response(data=response)

            customer_obj.agent_id = livechat_agent
            customer_obj.agents_group.add(livechat_agent)
            diff = timezone.now() - customer_obj.joined_date
            customer_obj.queue_time = diff.seconds
            customer_obj.save()

            if identifier == "AGENT_JOINED_CHAT":
                send_ameyo_system_message(customer_obj, message, identifier)

            response["status_code"] = "200"
            response["status_message"] = "Success"
            response["assign_status"] = 1
            response["livechat_session_id"] = str(livechat_session_id)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AssignAgentRequestAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': "LiveChat"})
            response["status_code"] = "500"
            response["status_message"] = str(e)
            response["status_line"] = str(exc_tb.tb_lineno)
        return Response(data=response)


AssignAgentRequest = AssignAgentRequestAPI.as_view()
