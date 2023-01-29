from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication  # noqa F401

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_channels import process_language_change_or_get_response
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.utils_bot import process_response_based_on_language

import json
import logging

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class ETSourceWebhookQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        channel = "ET-Source"
        bot_id = ""
        try:
            logger.info("Into ETSourceWebhookQueryAPI...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            api_key = request.META.get("HTTP_X_API_KEY", None)

            validation_obj = EasyChatInputValidation()

            data = request.data
            user_id = data['user_id']
            user_id = validation_obj.remo_html_from_string(user_id)
            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(str(bot_id))

            bot_obj = None
            try:
                bot_obj = Bot.objects.get(pk=int(bot_id))
            except Exception:
                response["status"] = 101
                response["message"] = "Matching bot id doesn't exist"
                return Response(data=response)

            channel_obj = None
            try:
                channel_obj = Channel.objects.get(name=channel)
            except Exception:
                response["status"] = 102
                response["message"] = "Matching channel doesn't exist"

            bot_channel_obj = BotChannel.objects.get(
                bot=bot_obj, channel=channel_obj)

            if str(bot_channel_obj.api_key) != api_key:
                response["status"] = 403
                response["message"] = "Unauthorized request"
                return Response(data=response)

            message = data['message']
            message = validation_obj.remo_html_from_string(message)
            message = validation_obj.remo_unwanted_characters_from_message(message, bot_id)
            channel_params = data['channel_params']
            channel_params = json.dumps(channel_params)

            selected_language = "en"
            if "language" in data:
                selected_language = data["language"]
                selected_language = validation_obj.remo_html_from_string(selected_language)

            original_message = message

            restriction_of_characters_on_message = Bot.objects.get(
                pk=int(bot_id)).number_of_words_in_user_message

            try:
                original_message = original_message[
                    :restriction_of_characters_on_message]
                message = message[:restriction_of_characters_on_message]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error Restricting characters to 200 words %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
                pass

            logger.info("bot_id: %s", str(bot_id), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})
            logger.info("message: %s", str(message.encode("utf-8")), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})
            logger.info("selected_language: %s", str(selected_language), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})
            logger.info("channel: %s", str(channel), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})
            logger.info("channel_params: %s", str(channel_params), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})

            # Valid easychat session id
            response = execute_query(
                user_id, bot_id, "uat", message, selected_language, channel, channel_params, original_message)

            logger.info("Exit from ETSourceWebhookQueryAPI", extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})

            if selected_language != "en":
                response = process_response_based_on_language(
                    response, selected_language, EasyChatTranslationCache)

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "[ENGINE] {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={
                         'AppName': 'EasyChat', 'user_id': "None", 'source': 'None', 'channel': '', 'bot_id': 'None'})
            response["status"] = 500
            response[
                "message"] = "Unable to process request due to some internal server error."
            try:
                if type(data) != dict:
                    data = json.loads(data)
                meta_data = data
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))

        return Response(data=response)

ETSourceWebhookQuery = ETSourceWebhookQueryAPI.as_view()


class ETSourceWelcomeMessageAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        bot_id = ""
        channel = "ET-Source"
        try:
            api_key = request.META.get("HTTP_X_API_KEY", None)

            data = request.data

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(str(bot_id))

            channel_name = "ET-Source"
            channel_obj = Channel.objects.get(name=channel_name)

            bot_obj = Bot.objects.get(
                pk=bot_id, is_uat=True, is_deleted=False)

            bot_channel_obj = BotChannel.objects.get(
                bot=bot_obj, channel=channel_obj)

            if str(bot_channel_obj.api_key) != api_key:
                response["status"] = 403
                response["message"] = "Unauthorized request"
                return Response(data=response)

            regex_compiler = re.compile(r'<.*?>')

            response["text_welcome_message"] = regex_compiler.sub(
                "", bot_channel_obj.welcome_message)
            response["speech_welcome_message"] = BeautifulSoup(
                bot_channel_obj.welcome_message).text

            initial_messages = json.loads(bot_channel_obj.initial_messages)
            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])
            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}

            response["initial_message"] = initial_messages
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "Error ETSourceWelcomeMessageAPI {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            try:
                if type(data) != dict:
                    data = json.loads(data)
                meta_data = data
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))
            
        return Response(data=response)


ETSourceWelcomeMessage = ETSourceWelcomeMessageAPI.as_view()
