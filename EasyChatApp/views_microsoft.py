from bs4 import BeautifulSoup
import logging
import requests
import json
import sys
import time

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from django.conf import settings

from EasyChatApp.utils import *
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.utils_microsoft import save_and_get_microsoft_file_src, get_recommendations
from EasyChatApp.models import Bot, Channel, BotChannel, Config, TimeSpentByUser, Feedback, MISDashboard, Data, Intent, FlowAnalytics, Tree, FormAssist
from EasyChatApp.utils_channels import process_language_change_or_get_response

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class MSTeamsQueryAPI(APIView):

    def post(self, request, *args, **kwargs):

        logger.info("Inside post ", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Instagram', 'bot_id': 'None'})

        response = {}
        response["status"] = 500
        response["data"] = {}
        channel = "Microsoft"
        bot_id = ""

        try:
            payload = request.data

            if not isinstance(payload, dict):
                payload = json.loads(payload)

            validation_obj = EasyChatInputValidation()

            bot_id = request.GET["bot_id"]
            bot_name = 'uat'
            # channel_obj = Channel.objects.get(name="Microsoft")
            # bot_obj = Bot.objects.get(pk=bot_id)
            # bot_console_obj = BotChannel.objects.get(
            #     bot=bot_obj, channel=channel_obj)

            sender = payload["sender"]
            message = ""
            attachments = []

            if payload["type"] == "message":
                message = payload["text"].strip()
                message = validation_obj.remo_html_from_string(message)
                message = validation_obj.remo_unwanted_characters_from_message(
                    message, int(bot_id))
                
            elif payload["type"] == "attachment":
                attachments = json.loads(payload["attachments"])
            else:
                try:
                    if type(payload) != dict:
                        payload = json.loads(payload)
                    meta_data = payload
                except:
                    meta_data = {}
                meta_data["error"] = "MSTeams: Invalid message type"
                check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))
                return Response(data=response)

            user_id = "microsoft_teams_user_" + str(sender)
            user = set_user(user_id, message, "en", "Microsoft", bot_id)
            save_data(user, {
                      "channel_name": "Microsoft"}, "en", "Microsoft", bot_id, is_cache=True)

            channel_params = {}
            file_src = ""
            if len(attachments) > 0:
                attachment = attachments[0]

                file_src = save_and_get_microsoft_file_src(
                    attachment, sender)

                if file_src == "FILE_NOT_SUPPORTED":
                    response_text = "This file format is not supported"
                    response["status"] = 200
                    response["data"] = {
                        "text_response_list": [response_text],
                        "videos": [],
                        "image_urls": [],
                        "recom_list": [],
                        "cards_list": [],
                        "choices_list": [],
                    }
                    return Response(data=response)

                if file_src != "":
                    channel_params = {
                        "attached_file_path": file_src,
                    }

            if file_src == "" and message == "":
                # IF ATTACHMENT IS EMPTY AND MESSAGE IS ALSO EMPTY THEN RETUN
                try:
                    if type(payload) != dict:
                        payload = json.loads(payload)
                    meta_data = payload
                except:
                    meta_data = {}
                meta_data["error"] = "MSTeams: Attachment and Message are empty"
                check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))
                return Response(data=response)

            channel_params = json.dumps(channel_params)

            bot_obj = Bot.objects.get(pk=bot_id)
            terminate, response = process_language_change_or_get_response(user_id, bot_id, None, bot_name, channel, channel_params, message, bot_obj, sender=sender)
            if terminate:
                return Response(data=response)
            query_response = response
            
            save_bot_switch_data_variable_if_availabe(user_id, bot_id, query_response, "Microsoft")

            text_response = query_response["response"]["text_response"]["text"]
            choices_list = query_response['response']['choices']
            cards_list = query_response['response']['cards']
            recom_list = query_response['response']['recommendations']
            image_urls = query_response["response"]["images"]
            videos = query_response["response"]["videos"]

            is_go_back_enabled = query_response['response'].get(
                "is_go_back_enabled", False)

            if is_go_back_enabled:
                recom_list.append({
                    'name': 'Go Back',
                    'id': None
                })

            recom_list = get_recommendations(recom_list, sender)
            choices_list = get_recommendations(choices_list, sender)

            text_response_list = []

            for small_message in text_response.split("$$$"):
                if small_message != "":
                    text_response_list.append(small_message)

            response["status"] = 200
            response["data"] = {
                "text_response_list": text_response_list,
                "videos": videos,
                "image_urls": image_urls,
                "recom_list": recom_list,
                "cards_list": cards_list,
                "choices_list": choices_list,
            }

            return Response(data=response)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "Error MSTeamsQueryAPI {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            try:
                if type(payload) != dict:
                    payload = json.loads(payload)
                meta_data = payload
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))
        return Response(data=response)


MSTeamsQuery = MSTeamsQueryAPI.as_view()


class MSTeamsDownloadConfigAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            bot_id = None

            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            bot_id = data["bot_id"]

            bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            template_config_file_path = "files/microsoft-teams/config/template/config_template.json"
            with open(template_config_file_path, "rb") as in_file:
                template_config_json = json.load(in_file)

            channel = Channel.objects.get(name="Microsoft")
            bot_console_obj = BotChannel.objects.get(bot=bot, channel=channel)

            ms_team_app_password = bot_console_obj.ms_team_app_password
            ms_team_app_code = bot_console_obj.ms_team_app_code
            easychat_query_end_point = settings.EASYCHAT_HOST_URL + \
                "/webhook/microsoft-teams/?bot_id=" + str(bot.pk)

            template_config_json["app_id"] = ms_team_app_code
            template_config_json["app_password"] = ms_team_app_password
            template_config_json["easychat_query_end_point"] = easychat_query_end_point

            config_file_path = "files/microsoft-teams/config/config_bot_{bot_id}.json".format(
                bot_id=str(bot.pk))
            with open(config_file_path, "w", encoding="utf-8") as out_file:
                json.dump(template_config_json, out_file, indent=4)

            config_file_path = "/" + config_file_path

            response["status"] = 200
            response["config_file_path"] = config_file_path
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("MSTeamsDownloadConfigAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'Twitter', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


MSTeamsDownloadConfig = MSTeamsDownloadConfigAPI.as_view()
