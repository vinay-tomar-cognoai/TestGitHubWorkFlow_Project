import json
import logging
import sys
import threading
import os.path

from EasyChatApp.utils_validation import EasyChatFileValidation, EasyChatInputValidation
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect, redirect

from EasyChatApp.models import *
from EasyChatApp.utils import is_allowed

from EasyChatApp.constants_fusion_processors import *

logger = logging.getLogger(__name__)


def FusionEditor(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):

            user_obj = User.objects.get(username=str(request.user.username))

            bot_pk = request.GET["bot_pk"]
            type_of_processor = request.GET["editor_id"]

            if type_of_processor not in ["1", "2", "3", "4"]:
                type_of_processor = "1"

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            processor_obj = BotFusionConfigurationProcessors.objects.filter(bot=bot_obj).first()

            if not processor_obj:
                processor_obj = BotFusionConfigurationProcessors.objects.create(bot=bot_obj)
                
                processor_obj.bot_chat_history_processor = FusionProcessor.objects.create(
                    name=FUSION_BOT_CHAT_HISTORY_PROCESSOR_NAME, function=FUSION_BOT_CHAT_HISTORY_PROCESSOR)

                processor_obj.text_message_processor = FusionProcessor.objects.create(
                    name=FUSION_TEXT_MESSAGE_PROCESSOR_NAME, function=FUSION_TEXT_MESSAGE_PROCESSOR)

                processor_obj.attachment_message_processor = FusionProcessor.objects.create(
                    name=FUSION_ATTACHMENT_MESSAGE_PROCESSOR_NAME, function=FUSION_ATTACHMENT_MESSAGE_PROCESSOR)

                processor_obj.chat_disconnect_processor = FusionProcessor.objects.create(
                    name=FUSION_CHAT_DISCONNECTED_PROCESSOR_NAME, function=FUSION_CHAT_DISCONNECTED_PROCESSOR)
                
                processor_obj.save()

            if type_of_processor == "1":

                if not processor_obj.bot_chat_history_processor:
                    processor_obj.bot_chat_history_processor = FusionProcessor.objects.create(
                        name=FUSION_BOT_CHAT_HISTORY_PROCESSOR_NAME, function=FUSION_BOT_CHAT_HISTORY_PROCESSOR)
                    processor_obj.save()

                code = processor_obj.bot_chat_history_processor.function
                name = processor_obj.bot_chat_history_processor.name
            elif type_of_processor == "2":

                if not processor_obj.text_message_processor:
                    processor_obj.text_message_processor = FusionProcessor.objects.create(
                        name=FUSION_TEXT_MESSAGE_PROCESSOR_NAME, function=FUSION_TEXT_MESSAGE_PROCESSOR)
                    processor_obj.save()

                code = processor_obj.text_message_processor.function
                name = processor_obj.text_message_processor.name
            elif type_of_processor == '3':

                if not processor_obj.attachment_message_processor:
                    processor_obj.attachment_message_processor = FusionProcessor.objects.create(
                        name=FUSION_ATTACHMENT_MESSAGE_PROCESSOR_NAME, function=FUSION_ATTACHMENT_MESSAGE_PROCESSOR)
                    processor_obj.save()

                code = processor_obj.attachment_message_processor.function
                name = processor_obj.attachment_message_processor.name
            elif type_of_processor == '4':

                if not processor_obj.chat_disconnect_processor:
                    processor_obj.chat_disconnect_processor = FusionProcessor.objects.create(
                        name=FUSION_CHAT_DISCONNECTED_PROCESSOR_NAME, function=FUSION_CHAT_DISCONNECTED_PROCESSOR)
                    processor_obj.save()

                code = processor_obj.chat_disconnect_processor.function
                name = processor_obj.chat_disconnect_processor.name

            return render(request, 'EasyChatApp/fusion_editor.html', {'user_obj': user_obj, 'selected_bot_obj': bot_obj, 'processor_obj': processor_obj, 'code': code, 'name': name, 'type_of_processor': type_of_processor})

        else:
            return HttpResponseRedirect("/chat/login")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("FusionEditor error: %s at line no: %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return HttpResponseRedirect("/chat/home")


class SaveFusionConfigAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data['bot_pk']
            app_id = data['app_id']
            host_name = data['host_name']

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            app_id = validation_obj.remo_html_from_string(app_id)
            app_id = validation_obj.remo_unwanted_characters(app_id)

            host_name = validation_obj.remo_html_from_string(host_name)

            if app_id.strip() == "":
                response["status"] = 400
                response["message"] = "APP ID cannot be empty."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if host_name.strip() == "":
                response["status"] = 400
                response["message"] = "Host Name cannot be empty."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            bot_fusion_config = BotFusionConfigurationProcessors.objects.filter(bot=bot_obj).first()
            bot_fusion_config.app_id = app_id
            bot_fusion_config.host_name = host_name
            bot_fusion_config.save()

            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveFusionConfigAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveFusionConfig = SaveFusionConfigAPI.as_view()


class SaveFusionProcessorAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data['bot_pk']
            type_of_processor = data['type_of_processor']
            code = data['code']
            is_reset = data['is_reset']

            validation_obj = EasyChatInputValidation()
            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            bot_obj = Bot.objects.get(pk=int(bot_pk))
            bot_fusion_config = BotFusionConfigurationProcessors.objects.filter(bot=bot_obj).first()

            if type_of_processor == "1":

                if is_reset:
                    bot_fusion_config.bot_chat_history_processor.function = FUSION_BOT_CHAT_HISTORY_PROCESSOR
                else:
                    bot_fusion_config.bot_chat_history_processor.function = code

                bot_fusion_config.bot_chat_history_processor.save()

            elif type_of_processor == "2":

                if is_reset:
                    bot_fusion_config.text_message_processor.function = FUSION_TEXT_MESSAGE_PROCESSOR
                else:
                    bot_fusion_config.text_message_processor.function = code

                bot_fusion_config.text_message_processor.save()

            elif type_of_processor == "3":

                if is_reset:
                    bot_fusion_config.attachment_message_processor.function = FUSION_ATTACHMENT_MESSAGE_PROCESSOR
                else:
                    bot_fusion_config.attachment_message_processor.function = code

                bot_fusion_config.attachment_message_processor.save()

            elif type_of_processor == "4":

                if is_reset:
                    bot_fusion_config.chat_disconnect_processor.function = FUSION_CHAT_DISCONNECTED_PROCESSOR
                else:
                    bot_fusion_config.chat_disconnect_processor.function = code

                bot_fusion_config.chat_disconnect_processor.save()
            
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveFusionProcessorAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveFusionProcessor = SaveFusionProcessorAPI.as_view()
