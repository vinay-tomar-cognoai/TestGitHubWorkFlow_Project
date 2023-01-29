import sys
import json
import uuid
import pytz
import logging
import datetime
import threading

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# Django imports
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from EasyChat import settings
from EasyChatApp.models import Bot, Profile
from LiveChatApp.models import *
from LiveChatApp.utils import get_livechat_category_using_name, check_for_holiday, check_for_non_working_hour, check_is_customer_blocked
from LiveChatApp.livechat_channels_webhook import customer_end_livechat, send_data_to_websocket, send_notification_to_agent
from LiveChatApp.utils_validation import LiveChatInputValidation
from LiveChatApp.utils_exposed_apis import *

User = get_user_model()
IST = pytz.timezone("Asia/Kolkata")

# Logger
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class CreateExternalCustomerRoomAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        try:
            logger.info("inside room creation", extra={'AppName': 'LiveChat'})

            validation_obj = LiveChatInputValidation()
            data = request.data

            is_all_data_available = True
            required_inputs = ["bot_id", "customer_name",
                               "phone", "email", "category", "user_id", "message", "active_url"]
            for required_input in required_inputs:
                if not (required_input in data):
                    is_all_data_available = False

            if not is_all_data_available:
                response["status_code"] = 301
                response["message"] = 'No Content'
                return Response(data=response)

            bot_name = data["bot_id"]
            bot_name = validation_obj.remo_html_from_string(bot_name)

            username = data["customer_name"]
            username = validation_obj.remo_html_from_string(username)

            phone = data["phone"]
            phone = validation_obj.remo_html_from_string(phone)

            email = data["email"]
            email = validation_obj.remo_html_from_string(email)

            livechat_category = data["category"]
            livechat_category = validation_obj.remo_html_from_string(
                livechat_category)

            message = data["message"]
            message = validation_obj.remo_html_from_string(message)

            user_id = data["user_id"]
            user_id = validation_obj.remo_html_from_string(user_id)

            active_url = data["active_url"]

            customer_details = {}
            if 'customer_details' in data:
                customer_details = data['customer_details']

            client_id = user_id
            if "client_id" in data:
                client_id = data["client_id"]
                client_id = validation_obj.remo_html_from_string(client_id)

            channel = "Web"
            if "channel" in data:
                channel = data["channel"]
                channel = validation_obj.remo_html_from_string(channel)

            if not validation_obj.validate_phone_number(phone):
                response["status_code"] = 400
                response['message'] = 'Invalid Phone Number'

            if not validation_obj.validate_email(email):
                response["status_code"] = 400
                response['message'] = 'Invalid Email ID'

            if response["status_code"] == 400:
                return Response(data=response)

            session_id = str(uuid.uuid4())
            bot_obj = Bot.objects.get(name=bot_name)

            Profile.objects.create(
                user_id=user_id, bot=bot_obj, livechat_connected=True, livechat_session_id=session_id)

            category_obj = get_livechat_category_using_name(
                livechat_category, bot_obj, LiveChatCategory)

            livechat_cust_obj = LiveChatCustomer.objects.create(session_id=session_id,
                                                                username=username,
                                                                phone=phone,
                                                                email=email,
                                                                is_online=True,
                                                                easychat_user_id=user_id,
                                                                message=message,
                                                                channel=Channel.objects.get(
                                                                    name=channel),
                                                                category=category_obj,
                                                                bot=bot_obj,
                                                                client_id=client_id,
                                                                customer_details=json.dumps(
                                                                    customer_details),
                                                                is_external=True,
                                                                active_url=active_url)

            livechat_cust_obj.closing_category = livechat_cust_obj.category
            livechat_cust_obj.save()

            try:
                boolian_var, response = check_for_holiday(
                    bot_obj, LiveChatCalender, LiveChatUser)
                if boolian_var:
                    livechat_cust_obj.is_denied = True
                    livechat_cust_obj.is_session_exp = True
                    livechat_cust_obj.system_denied_response = response[
                        "message"]
                    livechat_cust_obj.is_system_denied = True
                    livechat_cust_obj.last_appearance_date = timezone.now()
                    livechat_cust_obj.save()

                    response.pop('assigned_agent', None)
                    response.pop('assigned_agent_username', None)
                    response['message'] = 'holiday'

                    return Response(data=response)

                boolian_var, response = check_for_non_working_hour(
                    bot_obj, LiveChatCalender, LiveChatConfig, LiveChatUser)

                if boolian_var:
                    livechat_cust_obj.is_denied = True
                    livechat_cust_obj.is_session_exp = True
                    livechat_cust_obj.system_denied_response = response[
                        "message"]
                    livechat_cust_obj.is_system_denied = True
                    livechat_cust_obj.last_appearance_date = timezone.now()
                    livechat_cust_obj.save()

                    response.pop('assigned_agent', None)
                    response.pop('assigned_agent_username', None)
                    response['message'] = 'non_working_hour'

                    return Response(data=response)

                if check_is_customer_blocked(livechat_cust_obj, LiveChatReportedCustomer):
                    livechat_cust_obj.is_denied = True
                    livechat_cust_obj.is_session_exp = True
                    livechat_cust_obj.system_denied_response = "Our chat representatives are unavailable right now. Please try again in some time."
                    livechat_cust_obj.is_system_denied = True
                    livechat_cust_obj.last_appearance_date = timezone.now()
                    livechat_cust_obj.save()

                    response["message"] = "customer_blocked"
                    return Response(data=response)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("CreateCustomerRoomAPI Holiday check: %s at %s", e, str(
                    exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                response["status_code"] = "300"
                response["message"] = "no_agent_online"

                livechat_cust_obj.is_denied = True
                livechat_cust_obj.is_session_exp = True
                livechat_cust_obj.system_denied_response = "Our chat representatives are unavailable right now. Please try again in some time."
                livechat_cust_obj.last_appearance_date = timezone.now()
                livechat_cust_obj.save()

            response["status_code"] = "200"
            response['message'] = "request_registered"
            response["session_id"] = session_id

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateExternalCustomerRoom: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        return Response(data=response)


CreateExternalCustomerRoom = CreateExternalCustomerRoomAPI.as_view()


class SaveExternalCustomerChatAPI(APIView):

    def check_required_inputs(self, required_inputs):
        for required_input in required_inputs:
            if not (required_input in self.data):
                return False

        return True

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = request.data
            self.data = data

            validation_obj = LiveChatInputValidation()

            required_inputs = ["session_id", "message_type", "sender"]
            if not self.check_required_inputs(required_inputs):
                response["status_code"] = 301
                response["message"] = 'No Content'
                return Response(data=response)

            session_id = data["session_id"]
            message_type = data["message_type"]
            sender = data["sender"]

            if message_type not in ['text', 'media']:
                response["status_code"] = 300
                response["message"] = 'incorrect message type'
                return Response(data=response)

            attached_file_src = ""
            attachment_file_name = ""
            thumbnail_file_path = ""
            preview_attachment_file_path = ""
            message = ""

            if message_type == 'text':

                required_inputs = ['message']
                if not self.check_required_inputs(required_inputs):
                    response["status_code"] = 301
                    response["message"] = 'No Content'
                    return Response(data=response)

                message = data['message']
                message = validation_obj.remo_html_from_string(message)
                message = validation_obj.remo_special_tag_from_string(message)
            elif message_type == 'media':

                required_inputs = ['attached_file_src']
                if not self.check_required_inputs(required_inputs):
                    response["status_code"] = 301
                    response["message"] = 'No Content'
                    return Response(data=response)

                attached_file_src = data['attached_file_src']
                attached_file_src = validation_obj.remo_html_from_string(
                    attached_file_src)

                attachment_file_name = attached_file_src.split("/")[-1]

                if 'thumbnail_file_path' in data:
                    thumbnail_file_path = data["thumbnail_file_path"]

                if "preview_file_src" in data:
                    preview_attachment_file_path = data["preview_file_src"]

                if 'message' in data:
                    message = data['message']
                    message = validation_obj.remo_html_from_string(message)
                    message = validation_obj.remo_special_tag_from_string(
                        message)

            session_id = validation_obj.remo_html_from_string(session_id)
            sender = validation_obj.remo_html_from_string(sender)

            customer_obj = LiveChatCustomer.objects.filter(
                session_id=session_id)

            if customer_obj:
                customer_obj = customer_obj.first()
            else:
                response["status_code"] = 400
                response["message"] = 'customer does not exist'
                return Response(data=response)

            sender_name = customer_obj.get_username() if sender == "Customer" else "System"

            livechat_mis_obj = LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                                   sender=sender,
                                                                   text_message=message,
                                                                   sender_name=sender_name,
                                                                   message_time=timezone.now(),
                                                                   attachment_file_name=attachment_file_name,
                                                                   attachment_file_path=attached_file_src,
                                                                   thumbnail_file_path=thumbnail_file_path,
                                                                   preview_attachment_file_path=preview_attachment_file_path)
            customer_obj.last_appearance_date = timezone.now()
            customer_obj.unread_message_count += 1
            customer_obj.save()

            data = json.dumps({
                "sender": "Customer",
                "message": json.dumps({
                    "text_message": message,
                    "file_type": "message",
                    "channel": customer_obj.channel.name,
                    "bot_id": customer_obj.bot.pk,
                    "path": attached_file_src,
                    "thumbnail_url": thumbnail_file_path,
                })
            })

            data_to_send = [data]

            send_notification_to_agent(
                str(customer_obj.agent_id.user.username), message, session_id, customer_obj.username, customer_obj.channel.name, attached_file_src, thumbnail_file_path)

            thread = threading.Thread(target=send_data_to_websocket, args=(
                settings.EASYCHAT_DOMAIN, data_to_send, session_id), daemon=True)
            thread.start()

            response["status_code"] = "200"
            response["message"] = "message saved successfully"
            response["message_id"] = str(livechat_mis_obj.message_id)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveExternalCustomerChatAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        return Response(data=response)


SaveExternalCustomerChat = SaveExternalCustomerChatAPI.as_view()


class EndExternalChatAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = request.data

            validation_obj = LiveChatInputValidation()

            is_all_data_available = True
            required_inputs = ["session_id"]
            for required_input in required_inputs:
                if not (required_input in data):
                    is_all_data_available = False

            if not is_all_data_available:
                response["status_code"] = 301
                response["message"] = 'No Content'
                return Response(data=response)

            session_id = data["session_id"]
            session_id = validation_obj.remo_html_from_string(session_id)

            customer_obj = LiveChatCustomer.objects.filter(
                session_id=session_id)

            if customer_obj:
                customer_obj = customer_obj.first()
            else:
                response["status_code"] = 400
                response["message"] = 'customer does not exist'
                return Response(data=response)

            if not customer_obj.is_online and customer_obj.chat_ended_by != "":
                response["status_code"] = 300
                response["message"] = "chat is already ended"
                return Response(data=response)

            message = customer_end_livechat(
                customer_obj.easychat_user_id, customer_obj.channel.name, customer_obj.bot.pk, True)

            customer_obj.is_online = False
            customer_obj.last_appearance_date = datetime.now()
            customer_obj.chat_ended_by = "customer"
            customer_obj.save()

            LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                sender="System",
                                                text_message=CUSTOMER_LEFT_THE_CHAT,
                                                sender_name="system",
                                                message_time=timezone.now(),
                                                attachment_file_name="",
                                                attachment_file_path="",
                                                thumbnail_file_path="")

            data = json.dumps({
                "sender": "System",
                "message": json.dumps({
                    "text_message": CUSTOMER_LEFT_THE_CHAT,
                    "file_type": "message",
                    "channel": customer_obj.channel.name,
                    "bot_id": customer_obj.bot.pk,
                    "event_type": "ENDBYUSER",
                    "path": "",
                    "thumbnail_url": "",
                })
            })

            send_notification_to_agent(
                str(customer_obj.agent_id.user.username), CUSTOMER_LEFT_THE_CHAT, session_id, customer_obj.username, customer_obj.channel.name, "", "")

            thread = threading.Thread(target=send_data_to_websocket, args=(
                settings.EASYCHAT_DOMAIN, [data], session_id), daemon=True)
            thread.start()

            response["status_code"] = "200"
            response["message"] = message

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EndExternalChatAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        return Response(data=response)


EndExternalChat = EndExternalChatAPI.as_view()


class SaveExternalChatFeedbackAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = request.data

            validation_obj = LiveChatInputValidation()

            is_all_data_available = True
            required_inputs = ["session_id", "rating", "text_feedback"]
            for required_input in required_inputs:
                if not (required_input in data):
                    is_all_data_available = False

            if not is_all_data_available:
                response["status_code"] = 301
                response["message"] = 'No Content'
                return Response(data=response)

            session_id = data["session_id"]
            session_id = validation_obj.remo_html_from_string(session_id)

            rate_value = data["rating"]
            rate_value = validation_obj.remo_html_from_string(rate_value)

            text_feedback = data["text_feedback"]
            text_feedback = validation_obj.remo_html_from_string(text_feedback)

            customer_obj = LiveChatCustomer.objects.filter(
                session_id=session_id)

            if customer_obj:
                customer_obj = customer_obj.first()
            else:
                response["status_code"] = 400
                response["message"] = 'customer does not exist'
                return Response(data=response)

            if customer_obj.is_online or customer_obj.chat_ended_by == "":
                response["status_code"] = 300
                response["message"] = "LiveChat session is ongoing"
                return Response(data=response)

            if customer_obj.rate_value != -1:
                response["status_code"] = 300
                response["message"] = "feedback already given"
                return Response(data=response)

            customer_obj.rate_value = rate_value
            customer_obj.last_appearance_date = timezone.now()
            customer_obj.nps_text_feedback = text_feedback
            customer_obj.save()

            response["status_code"] = "200"
            response["message"] = "feedback saved successfully"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveExternalChatFeedbackAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        return Response(data=response)


SaveExternalChatFeedback = SaveExternalChatFeedbackAPI.as_view()


class UpdateLiveChatEventsAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = request.data

            validation_obj = LiveChatInputValidation()

            is_all_data_available = True
            required_inputs = ["session_id", "event_type"]
            for required_input in required_inputs:
                if not (required_input in data):
                    is_all_data_available = False

            if not is_all_data_available:
                response["status_code"] = 301
                response["message"] = 'No Content'
                return Response(data=response)

            session_id = data["session_id"]
            session_id = validation_obj.remo_html_from_string(session_id)

            event_type = data["event_type"]
            event_type = validation_obj.remo_html_from_string(event_type)

            customer_obj = LiveChatCustomer.objects.filter(
                session_id=session_id)

            if customer_obj:
                customer_obj = customer_obj.first()
            else:
                response["status_code"] = 400
                response["message"] = 'customer does not exist'
                return Response(data=response)

            data = json.dumps({
                "sender": "System",
                "message": json.dumps({
                    "channel": customer_obj.channel.name,
                    "bot_id": customer_obj.bot.pk,
                    "event_type": event_type,
                    "session_id": session_id
                })
            })

            send_notification_to_agent(
                str(customer_obj.agent_id.user.username), "", session_id, customer_obj.username, customer_obj.channel.name, "", "", "", event_type)

            thread = threading.Thread(target=send_data_to_websocket, args=(
                settings.EASYCHAT_DOMAIN, [data], session_id), daemon=True)
            thread.start()

            response["status_code"] = "200"
            response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateLiveChatEventsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        return Response(data=response)


UpdateLiveChatEvents = UpdateLiveChatEventsAPI.as_view()


class GetAuthTokenAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = "Internal Server Error"
        external_api_audit_obj = None
        try:
            data = request.data
            tz = pytz.timezone(settings.TIME_ZONE)

            external_api_audit_obj = get_external_api_audit_obj(request, '1')

            response['request_id'] = str(external_api_audit_obj.request_id)
            response['timestamp'] = str(timezone.now().astimezone(tz))

            if 'username' not in data:
                response = get_external_api_response(
                    400, 'Invalid Username!', response, external_api_audit_obj)
                return Response(data=response, status=400)

            if 'password' not in data:
                response = get_external_api_response(
                    400, 'Invalid Password!', response, external_api_audit_obj)
                return Response(data=response, status=400)

            validation_obj = LiveChatInputValidation()
            username = validation_obj.remo_html_from_string(data['username'])
            password = data['password']
            user = authenticate(username=username, password=password)
            if user is None:
                response = get_external_api_response(
                    401, 'Invalid Username or Password!', response, external_api_audit_obj)
                return Response(data=response, status=401)

            livechat_user = LiveChatUser.objects.filter(
                user=user, is_deleted=False).first()

            if not livechat_user or livechat_user.status == '3':
                response = get_external_api_response(
                    401, 'Unauthorized access!', response, external_api_audit_obj)
                return Response(data=response, status=401)                

            existing_token_objs = LiveChatAuthToken.objects.filter(user=livechat_user)
            current_time = datetime.now() - timedelta(minutes=1)

            past_minute_objs = existing_token_objs.filter(
                user=livechat_user, created_datetime__gte=current_time)

            if past_minute_objs.count() >= EXTERNAL_API_TOKEN_CREATION_LIMIT_PER_MINUTE:
                response = get_external_api_response(
                    429, 'Rate Limit Exceeded!', response, external_api_audit_obj)
                return Response(data=response, status=429)

            existing_token_objs.update(is_expired=True)

            auth_token_obj = LiveChatAuthToken.objects.create(user=livechat_user)
            external_api_audit_obj.token = auth_token_obj

            response['auth_token'] = str(auth_token_obj.token)
            response['message'] = "Success"
            response['status'] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetAuthTokenAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        if external_api_audit_obj:
            external_api_audit_obj.response_data = json.dumps(response)
            external_api_audit_obj.status_code = response['status']
            external_api_audit_obj.save()
        return Response(data=response, status=response['status'])


GetAuthToken = GetAuthTokenAPI.as_view()


class GetAnalyticsExternalAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = "Internal Server Error"
        external_api_audit_obj = None
        try:
            data = request.data
            tz = pytz.timezone(settings.TIME_ZONE)

            external_api_audit_obj = get_external_api_audit_obj(request, '2')

            response['request_id'] = str(external_api_audit_obj.request_id)
            response['timestamp'] = str(timezone.now().astimezone(tz))

            livechat_user, status_code, response_message = check_livechat_external_data_is_valid(
                data, external_api_audit_obj)

            if status_code != 200:
                response = get_external_api_response(
                    status_code, response_message, response, external_api_audit_obj)
                return Response(data=response, status=status_code)

            response["livechat_user"] = str(livechat_user.user.username)

            analytics_types_map = {
                'live_analytics': get_live_analytics_external,
                'chat_reports': get_chat_reports_external,
                'average_nps': get_average_nps_external,
                'average_messages_per_chat': get_average_messages_per_chat_external,
                'average_handling_time': get_average_handling_time,
                'average_customer_wait_time': get_average_customer_wait_time_external,
                'customer_reports': get_customer_reports_external,
                'performance_report': get_performance_report_external,
                'daily_interaction': get_daily_interaction_external,
                'hourly_interaction': get_hourly_interaction_external,
                'login_logout_report': get_login_logout_report_external,
                'agent_not_ready_report': get_agent_not_ready_report_external,
                'missed_chats': get_missed_chats_external,
                'offline_chats': get_offline_chats_external,
                'abandoned_chats': get_abandoned_chats_external
            }

            if 'analytics_type' not in data or data['analytics_type'].strip().lower() not in analytics_types_map:
                response = get_external_api_response(
                    400, 'Invalid Analytics type!', response, external_api_audit_obj)
                return Response(data=response, status=400)

            analytics_type = data['analytics_type'].strip().lower()
            response['analytics_type'] = analytics_type

            filter_params = {}
            if 'filter_params' in data:
                filter_params = data['filter_params']
                if not isinstance(filter_params, dict):
                    filter_params = json.loads(filter_params)

            response = get_analytics_data_external(
                response, analytics_types_map, analytics_type, livechat_user, filter_params)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetAnalyticsExternalAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        if external_api_audit_obj:
            external_api_audit_obj.response_data = json.dumps(response)
            external_api_audit_obj.status_code = response['status']
            external_api_audit_obj.save()

        return Response(data=response, status=response['status'])


GetAnalyticsExternal = GetAnalyticsExternalAPI.as_view()
