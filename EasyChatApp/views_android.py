from EasyChatApp.utils_validation import EasyChatInputValidation
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password

from django.contrib.auth import authenticate, login
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from django.http import HttpResponseNotFound

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.constants import *
from LiveChatApp.models import LiveChatConfig

import datetime
import re
import json
import uuid
import logging
import sys
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class VerifyBotAccessTokenAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            bot_id = data["bot_id"]
            access_token = data["access_token"]
            selected_bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            if BotChannel.objects.filter(bot=selected_bot_obj, api_key=access_token):
                response["status"] = 200
            else:
                response["status"] = 300
            
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("VerifyBotAccessTokenAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        return Response(data=response)


VerifyBotAccessToken = VerifyBotAccessTokenAPI.as_view()


class CheckLiveChatSessionAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            session_id = data["livechat_session_id"]
            livechat_cust_obj = LiveChatCustomer.objects.filter(
                session_id=session_id).first()
            if (livechat_cust_obj.is_session_exp or len(livechat_cust_obj.chat_ended_by.strip()) > 0) and (livechat_cust_obj.channel.name.lower() == "android" or livechat_cust_obj.channel.name.lower() == "ios"):
                response["status"] = 440
            else:
                response["status"] = 200
            
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CheckLiveChatSessionAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        return Response(data=response)


CheckLiveChatSession = CheckLiveChatSessionAPI.as_view()


class GetAndroidChannelDetailsAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            dont_update_session = False
            data = request.data
            channel_name = data["channel_name"]
            bot_id = data["bot_id"]
            bot_name = data["bot_name"]
            user_id = data["user_id"]
            session_id = data["session_id"]
            dont_update_session = data["dont_update_session"]
            channel_obj = Channel.objects.get(name=str(channel_name))

            bot_obj = None

            start_datetime = datetime.datetime.now()

            if(bot_name == 'uat'):
                bot_obj = Bot.objects.get(
                    pk=bot_id, is_uat=True, is_deleted=False)
            else:
                bot_obj = Bot.objects.filter(
                    slug=bot_name, is_active=True, is_deleted=False).order_by('-pk')[0]

            # checking wheter we have to update the session or not
            if dont_update_session:
                pass
            else:
                session_id = str(uuid.uuid4())
                TimeSpentByUser.objects.create(
                    user_id=user_id, session_id=session_id, start_datetime=start_datetime, end_datetime=start_datetime, bot=bot_obj)

            response["session_id"] = session_id

            channel_obj = BotChannel.objects.filter(
                bot=bot_obj, channel=channel_obj)[0]

            regex_compiler = re.compile(r'<.*?>')

            response["speech_message"] = regex_compiler.sub(
                "", channel_obj.speech_message)

            if(str(channel_name) == "Web"):

                welcome_message = channel_obj.welcome_message
                
                response["welcome_message"] = BeautifulSoup(
                    welcome_message).text.strip()

                response["speech_welcome_message"] = BeautifulSoup(
                    channel_obj.welcome_message).text
            else:
                response["welcome_message"] = regex_compiler.sub(
                    "", channel_obj.welcome_message)

            response["failure_message"] = regex_compiler.sub(
                "", channel_obj.failure_message)

            response["reprompt_message"] = regex_compiler.sub(
                "", channel_obj.reprompt_message)

            response["session_end_message"] = regex_compiler.sub(
                "", channel_obj.session_end_message)

            initial_messages = json.loads(channel_obj.initial_messages)

            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])

            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}
            response["initial_messages"] = initial_messages

            response["carousel_img_url_list"] = json.loads(
                channel_obj.image_url)
            response["redirect_url_list"] = json.loads(
                channel_obj.redirection_url)

            response[
                "is_text_to_speech_required"] = bot_obj.is_text_to_speech_required
            response["is_powered_by_required"] = bot_obj.is_powered_by_required
            response["show_brand_name"] = bot_obj.show_brand_name
            response[
                "bot_inactivity_detection_enabled"] = bot_obj.is_inactivity_timer_enabled
            response["bot_inactivity_msg"] = bot_obj.bot_inactivity_response
            response["bot_inactivity_time"] = bot_obj.bot_inactivity_timer

            response[
                "bot_response_delay_allowed"] = bot_obj.bot_response_delay_allowed
            response["bot_response_delay_timer"] = bot_obj.bot_response_delay_timer
            response[
                "bot_response_delay_message"] = bot_obj.bot_response_delay_message

            response['bot_start_conversation_intent'] = None
            if bot_obj.start_conversation != None and bot_obj.start_conversation != "":
                response[
                    "bot_start_conversation_intent"] = bot_obj.start_conversation

            sticky_intents = json.loads(channel_obj.sticky_intent)
            sticky_intent_list = get_message_list_using_pk(
                sticky_intents["items"])

            sticky_intents_menu = json.loads(channel_obj.sticky_intent_menu)
            sticky_intent_list_menu = get_message_list_and_icon_name(
                sticky_intents_menu["items"], Intent)

            bot_theme_obj = bot_obj.default_theme
            try:
                bot_theme = bot_theme_obj.name
            except Exception:
                bot_theme = ""

            if(str(channel_name) == "Web"):
                try:
                    response[
                        "is_automatic_carousel_enabled"] = channel_obj.is_automatic_carousel_enabled
                    response["carousel_time"] = channel_obj.carousel_time
                except Exception:
                    response["is_automatic_carousel_enabled"] = False

                response[
                    "is_bot_notification_sound_enabled"] = channel_obj.is_bot_notification_sound_enabled

            try:
                livechat_obj = LiveChatConfig.objects.get(bot=bot_obj)
                response['queue_timer'] = livechat_obj.queue_timer
            except Exception:
                response['queue_timer'] = 30
                pass

            response["bot_theme"] = bot_theme
            response["sticky_intents_list"] = sticky_intent_list
            response["sticky_intents_list_menu"] = sticky_intent_list_menu
            response[
                "sticky_button_display_format"] = channel_obj.sticky_button_display_format
            response["status"] = 200
            response["query_token_id"] = generate_query_token()

            response[
                "web_url_initial_intent_present"] = bot_obj.web_url_initial_intent_present
            response[
                "web_url_is_welcome_message_present"] = bot_obj.web_url_is_welcome_message_present
            response[
                "web_url_initial_image_present"] = bot_obj.web_url_initial_image_present
            response[
                "web_url_initial_videos_present"] = bot_obj.web_url_initial_videos_present
            response[
                "web_url_is_welcome_banner_present"] = bot_obj.web_url_is_welcome_banner_present

            # initial intent trigger
            response["initial_intent"] = None
            if bot_obj.initial_intent != None:
                response["initial_intent"] = bot_obj.initial_intent.name

            csat_object = CSATFeedBackDetails.objects.filter(bot_obj=bot_obj)

            if csat_object:
                csat_object = csat_object[0]
                response['mark_all_fields_mandatory'] = csat_object.mark_all_fields_mandatory
                response['collect_email_id'] = csat_object.collect_email_id
                response['collect_phone_number'] = csat_object.collect_phone_number

                all_feedbacks_str = ""
                for items in json.loads(csat_object.all_feedbacks):
                    all_feedbacks_str += items + ",,,"
                response['all_feedbacks'] = all_feedbacks_str
            else:
                response['mark_all_fields_mandatory'] = False
                response['collect_email_id'] = False
                response['collect_phone_number'] = False
                response['all_feedbacks'] = ""
            response['csat_feedback_form_enabled'] = bot_obj.csat_feedback_form_enabled

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAndroidChannelDetailsAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        return Response(data=response)


GetAndroidChannelDetails = GetAndroidChannelDetailsAPI.as_view()


class GetAndroidTrainingDataAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            bot_id = data["bot_id"]
            web_page = data["web_page"]

            page_url_without_params = web_page.split('?')[0]

            traffic_source = TrafficSources.objects.filter(
                web_page=page_url_without_params, visiting_date=datetime.datetime.today().date(), bot=Bot.objects.get(pk=bot_id))
            if traffic_source:
                traffic_source[0].bot_clicked_count = traffic_source[
                    0].bot_clicked_count + 1
                traffic_source[0].save()
            else:
                origin = urlparse(web_page)
                if origin.netloc not in settings.ALLOWED_HOSTS:
                    TrafficSources.objects.create(
                        web_page=page_url_without_params, web_page_visited=1, bot=Bot.objects.get(pk=bot_id))

            bot_obj = Bot.objects.get(pk=bot_id, is_deleted=False, is_uat=True)

            word_mapper_list = []
            word_mapper_objs = WordMapper.objects.filter(bots__in=[bot_obj])

            for word_mapper in word_mapper_objs:
                word_mapper_list.append({
                    "keyword": word_mapper.keyword,
                    "similar_words": word_mapper.get_similar_word_list()
                })

            sentence_list = []
            channel_obj = Channel.objects.get(name='Android')
            intent_objs = Intent.objects.filter(
                bots__in=[bot_obj], is_part_of_suggestion_list=True, is_deleted=False, is_form_assist_enabled=False, is_hidden=False, channels__in=[channel_obj]).distinct()

            for intent_obj in intent_objs:
                training_data_dict = json.loads(intent_obj.training_data)
                intent_name = intent_obj.name
                intent_click_count = intent_obj.intent_click_count

                sentence_list.append({
                    "key": intent_name,
                    "value": intent_name,
                    "count": intent_click_count
                })

                for key in training_data_dict:
                    training_sentence_lower_str = training_data_dict[key].lower(
                    )
                    if training_sentence_lower_str not in sentence_list:
                        sentence_list.append({
                            "key": training_sentence_lower_str,
                            "value": intent_name,
                            "count": intent_click_count
                        })

            response["sentence_list"] = sentence_list
            response["max_suggestions"] = bot_obj.max_suggestions
            response["word_mapper_list"] = word_mapper_list
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetTrainingDataAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        encrypted_response = custom_encrypt_obj.encrypt(json.dumps(response))
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAndroidTrainingData = GetAndroidTrainingDataAPI.as_view()


class GetAndroidBotMessageImageAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(str(bot_id))
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            bot_message_image_url = bot_obj.message_image.name
            bot_theme_color = bot_obj.bot_theme_color
            bot_display_name = bot_obj.bot_display_name
            bot_terms_and_conditions = bot_obj.terms_and_condition

            response['bot_theme_color'] = bot_theme_color
            response['bot_display_name'] = bot_display_name
            response['bot_message_image_url'] = bot_message_image_url
            response['bot_terms_and_conditions'] = bot_terms_and_conditions
            response["bot_font"] = str(bot_obj.font)
            response["bot_font_size"] = str(bot_obj.font_size)
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetBotMessageImageAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        encrypted_response = custom_encrypt_obj.encrypt(json.dumps(response))
        response = {"Response": encrypted_response}
        return Response(data=response)


class SaveAndroidFormDataAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)
            user_id = data['user_id']
            form_name = data['form_name']
            form_values = data['form_data']

            # bot id to be updated if required

            user = Profile.objects.get(user_id=user_id)

            try:
                data_obj = Data.objects.get(user=user, variable=form_name)
                data_obj.value = json.dumps(form_values)
                data_obj.cached_datetime = timezone.now()
                data_obj.is_cache = True
                data_obj.save()
            except Exception:
                data_obj = Data.objects.create(user=user, variable=form_name)
                data_obj.value = json.dumps(form_values)
                data_obj.cached_datetime = timezone.now()
                data_obj.is_cache = True
                data_obj.save()

            response['status'] = 200
            response['status_message'] = "success"
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveFormDataAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response['status_message'] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        encrypted_response = custom_encrypt_obj.encrypt(json.dumps(response))
        response = {"Response": encrypted_response}
        return Response(data=response)


class AndroidQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        try:
            logger.info("Into QueryAPI...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            bot_id = str(request.GET["id"])
            bot_name = 'uat'
            webhook_request_packet = request.data

            file_attachment = json.loads(
                webhook_request_packet["channel_params"])

            if file_attachment["attached_file_src"] != None and file_attachment["attached_file_src"] != "":
                if str(file_attachment["file_extension"].lower()) not in ['png', 'jpeg', 'jpg', 'doc', 'docx', 'pdf', 'zip', 'mp4']:
                    response["status_code"] = 500
                    response = build_error_response(
                        "This file format is not supported. Please try uploading some other file.")
                    return Response(data=response)
            webhook_response_packet = build_android_response(
                webhook_request_packet, bot_id, bot_name)

            response = webhook_response_packet

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[ENGINE] %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
            response = copy.deepcopy(DEFAULT_RESPONSE)
            response["status_code"] = 500
            response["status_message"] = str(e)
        response["status_code"] = str(response["status_code"])
        logger.info("Android Response : %s", json.dumps(response), extra={
                    'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
        return Response(data=response)


class SaveEasyChatAndroidIntentFeedbackAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:

            data = request.data['json_string']
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            feedback_id = data['feedback_id']
            feedback_id = validation_obj.remo_html_from_string(str(feedback_id))
            feedback_type = data['feedback_type']
            feedback_type = validation_obj.remo_html_from_string(str(feedback_type))
            feedback_cmt = data['feedback_cmt']
            feedback_cmt = validation_obj.remo_html_from_string(feedback_cmt)
            mis_objs = MISDashboard.objects.filter(pk=feedback_id)
            if len(mis_objs) > 0:
                mis_objs[0].is_helpful_field = feedback_type
                mis_objs[0].feedback_comment = str(feedback_cmt)
                mis_objs[0].save()
                response['status'] = 200
            else:
                response['status'] = 302

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveEasyChatIntentFeedbackAPI: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        encrypted_response = custom_encrypt_obj.encrypt(json.dumps(response))
        response = {"Response": encrypted_response}
        return Response(data=response)


class SaveAndroidFeedbackAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data['json_string']
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_id = data['user_id']
            user_id = validation_obj.remo_html_from_string(str(user_id))
            session_id = data['session_id']
            session_id = validation_obj.remo_html_from_string(session_id)
            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(str(bot_id))
            rating = data['rating']
            rating = validation_obj.remo_html_from_string(str(rating))
            comments = data['comments']
            comments = validation_obj.remo_html_from_string(comments)

            bot_obj = Bot.objects.filter(pk=bot_id)[0]
            channel = Channel.objects.get(name="Android")
            Feedback.objects.create(
                user_id=user_id, bot=bot_obj, rating=rating, comments=comments, session_id=session_id, channel=channel, scale_rating_5=bot_obj.scale_rating_5)

            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveFeedbackAPI: " + str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        encrypted_response = custom_encrypt_obj.encrypt(json.dumps(response))
        response = {"Response": encrypted_response}
        return Response(data=response)


class ClearAndroidUserDataAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_id = data['user_id']
            user_id = validation_obj.remo_html_from_string(user_id)
            logger.info("[ENGINE]: user_id: %s", str(user_id), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            clear_user_data(user_id, None, 'Android')
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ClearAndroidUserDataAPI %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        encrypted_response = custom_encrypt_obj.encrypt(json.dumps(response))
        response = {"Response": encrypted_response}
        return Response(data=response)


class SaveAndroidTimeSpentAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_id = data['user_id']
            session_id = data["session_id"]

            user_id = validation_obj.remo_html_from_string(user_id)
            session_id = validation_obj.remo_html_from_string(session_id)
            
            end_datetime = datetime.datetime.now()

            item_obj = TimeSpentByUser.objects.filter(
                user_id=user_id, session_id=session_id).last()

            item_obj.end_datetime = end_datetime
            item_obj.save()

            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveAndroidTimeSpentAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return Response(data=response)


SaveAndroidTimeSpent = SaveAndroidTimeSpentAPI.as_view()
ClearAndroidUserData = ClearAndroidUserDataAPI.as_view()
SaveAndroidFeedback = SaveAndroidFeedbackAPI.as_view()
SaveEasyChatAndroidIntentFeedback = SaveEasyChatAndroidIntentFeedbackAPI.as_view()
AndroidQuery = AndroidQueryAPI.as_view()
GetAndroidBotMessageImage = GetAndroidBotMessageImageAPI.as_view()
SaveAndroidFormData = SaveAndroidFormDataAPI.as_view()
