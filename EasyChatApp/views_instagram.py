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

from EasyChatApp.utils import set_user, save_data, execute_query, check_and_send_broken_bot_mail, save_bot_switch_data_variable_if_availabe
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.utils_instagram import remove_tags, verify_webhook, send_instagram_message,\
    save_and_get_instagram_file_src, send_instagram_reaction_message, send_images, send_cards, send_recommendations_carousel
from EasyChatApp.models import Bot, Channel, BotChannel, Config, TimeSpentByUser, Feedback, MISDashboard, Data, Intent, FlowAnalytics, Tree, FormAssist
from EasyChatApp.utils_channels import process_language_change_or_get_response, text_link_format

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class InstagramQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args):
        response = {}
        response["status"] = 500
        logger.info("Inside get ", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Instagram', 'bot_id': 'None'})
        try:
            response = verify_webhook(
                request, Bot, Channel, BotChannel)
            return response
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("InstagramWebhookAPI - Method: GET - " +
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return HttpResponse("Invalid Token")

    def post(self, request, *args, **kwargs):

        logger.info("Inside post ", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Instagram', 'bot_id': 'None'})
        logger.info(request.GET, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Instagram', 'bot_id': 'None'})
        response = {}
        response["status"] = 500
        channel = "Instagram"
        story_mention = False
        try:
            payload = request.data

            bot_id = request.GET["id"]
            bot_name = 'uat'
            channel_obj = Channel.objects.get(name="Instagram")
            bot_obj = Bot.objects.get(pk=bot_id)
            bot_console_obj = BotChannel.objects.get(
                bot=bot_obj, channel=channel_obj)
            page_access_token = bot_console_obj.page_access_token

            if not isinstance(payload, dict):
                payload = json.loads(payload)

            sender = ""
            if "messaging" in payload["entry"][0]:
                sender = payload["entry"][0]["messaging"][0]["sender"]["id"]
            elif "standby" in payload["entry"][0]:
                sender = payload["entry"][0]["standby"][0]["sender"]["id"]

            logger.info("Sender: " + sender, extra={'AppName': 'EasyChat',
                                                    'user_id': 'None', 'source': 'None', 'channel': 'Instagram', 'bot_id': 'None'})

            validation_obj = EasyChatInputValidation()           

            attachments = []
            message_dict = {}
            if "messaging" in payload["entry"][0]:
                message_dict = payload["entry"][0]["messaging"][0]
            elif "standby" in payload["entry"][0]:
                message_dict = payload["entry"][0]["standby"][0]
            message = ""
            if "message" in message_dict:

                if "is_deleted" in message_dict["message"] and message_dict["message"]["is_deleted"]:
                    return HttpResponse("OK")

                if "is_echo" in message_dict["message"]:
                    return HttpResponse("OK")

                if "attachments" in message_dict["message"]:
                    attachments = message_dict["message"]["attachments"]

                if "text" in message_dict["message"]:
                    message = message_dict["message"]["text"]
                    message = validation_obj.remo_complete_html_and_unwanted_characters(
                        message, int(bot_id))
            elif "postback" in message_dict and "payload" in message_dict["postback"]:
                message = message_dict["postback"]["payload"]
            else:
                return HttpResponse("OK")
                    
            user_id = "instagram_user_" + str(sender)
            user = set_user(user_id, message, "en", "Instagram", bot_id)
            save_data(user, {
                      "channel_name": "Instagram"}, "en", "Instagram", bot_id, is_cache=True)
            
            channel_params = {}
            if len(attachments) > 0:
                attachment = attachments[0]

                if attachment['type'] == 'story_mention':
                    story_mention = True

                file_src = save_and_get_instagram_file_src(
                    attachment, sender, page_access_token)

                if file_src != "":
                    channel_params = {
                        "attached_file_path": file_src,
                    }
                else:
                    if message.strip() == "":
                        return HttpResponse("OK")
                        # IF ATTACHMENT IS EMPTY AND MESSAGE IS ALSO EMPTY THEN RETUN
            if story_mention:
                text_response = "Thank you for mentioning us in your story 😊"
                send_instagram_message(sender, text_response, page_access_token)
                return HttpResponse("Ok")
            channel_params = json.dumps(channel_params)

            terminate, response = process_language_change_or_get_response(user_id, bot_id, None, bot_name, channel, channel_params, message, bot_obj, None, page_access_token, sender=sender)
            if terminate:
                return Response(data=response)
            
            save_bot_switch_data_variable_if_availabe(user_id, bot_id, response, "Instagram")

            text_response = response["response"]["text_response"]["text"]
            choices_list = response['response']['choices']
            cards_list = response['response']['cards']
            recom_list = response['response']['recommendations']
            is_go_back_enabled = False
            if "is_go_back_enabled" in response["response"]:
                is_go_back_enabled = response['response']['is_go_back_enabled']

            if is_go_back_enabled:
                recom_list.append({
                    'name': 'Go Back',
                    'id': None
                })

            text_response = remove_tags(text_response)
            text_response = text_link_format(text_response)

            image_urls = response["response"]["images"]

            validation_obj = EasyChatInputValidation()

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

            list_choice = []
            if len(choices_list) > 0:
                for choice_dict in choices_list: 
                    if "display" in choice_dict:
                        list_choice.append(choice_dict["display"])
                
            recommendations = recom_list + list_choice

            if len(recommendations) > 0:
                send_recommendations_carousel(
                    sender, page_access_token, recommendations=recommendations)

            if len(image_urls) > 0:
                send_images(sender, image_urls, page_access_token)

            if len(cards_list) > 0:
                send_cards(sender, cards_list, page_access_token)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "Error InstagramQueryAPI {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            try:
                if type(payload) != dict:
                    payload = json.loads(payload)
                meta_data = payload
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))
        return HttpResponse("OK")


InstagramQuery = InstagramQueryAPI.as_view()
