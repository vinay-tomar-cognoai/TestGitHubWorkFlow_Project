# from cgitb import text
# import requests
# from bs4 import BeautifulSoup
import logging
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

from EasyChatApp.models import EasyChatTranslationCache, Profile
from EasyChatApp.utils import set_user, save_data, execute_query, check_and_send_broken_bot_mail, save_bot_switch_data_variable_if_availabe
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.utils_facebook import html_tags_formatter, send_images, send_facebook_message, send_cards, send_recommendations_carousel, send_recommendations_quick_replies, verify_webhook, remove_tags, save_and_get_facebook_file_src, html_list_formatter
from EasyChatApp.models import Bot, Channel, BotChannel, Config, TimeSpentByUser, Feedback, MISDashboard, Data, Intent, FlowAnalytics, Tree, FormAssist
from EasyChatApp.utils_channels import process_language_change_or_get_response
from EasyChatApp.utils_bot import get_emojized_message

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class FacebookWebhookAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        logger.info("Inside post ", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        logger.info(request.GET, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response = {}
        response["status"] = 500
        channel = "Facebook"
        bot_id = ""
        try:
            payload = request.data

            bot_id = request.GET["id"]
            bot_name = 'uat'
            selected_language = "en"
            channel_obj = Channel.objects.get(name="Facebook")
            bot_obj = Bot.objects.get(pk=bot_id)
            bot_console_obj = BotChannel.objects.get(
                bot=bot_obj, channel=channel_obj)
            page_access_token = bot_console_obj.page_access_token
            if not isinstance(payload, dict):
                payload = json.loads(payload)
            logger.info(f'FacebookWebhookAPI payload: {str(payload)}', extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Facebook', 'bot_id': 'None'})
            sender = payload["entry"][0]["messaging"][0]["sender"]["id"]
            logger.info("Sender: " + sender, extra={'AppName': 'EasyChat',
                                                    'user_id': 'None', 'source': 'None', 'channel': 'Facebook', 'bot_id': 'None'})
            attachments = []

            message_dict = payload["entry"][0]["messaging"][0]
            message = ""
            terminate = False
            if "message" in message_dict:

                if "attachments" in message_dict["message"]:
                    attachments = message_dict["message"]["attachments"]

                if "text" in message_dict["message"]:
                    message = message_dict["message"]["text"]
                
                if "quick_reply" in message_dict["message"]:
                    message = message_dict["message"]["quick_reply"]["payload"]

                if "is_echo" in message_dict["message"] and message_dict["message"]["is_echo"]:
                    return HttpResponse("OK")
                    
            elif "postback" in message_dict and "payload" in message_dict["postback"]:
                message = message_dict["postback"]["payload"]
            else:
                return HttpResponse("OK")

            user_id = "facebook_user_" + str(sender)
            user = set_user(user_id, message, "en", "Facebook", bot_id)
            save_data(user, {
                      "channel_name": "Facebook"}, "en", "Facebook", bot_id, is_cache=True)

            profile_obj = Profile.objects.filter(user_id=user_id, bot=bot_obj).first()

            if profile_obj and profile_obj.selected_language:
                selected_language = profile_obj.selected_language.lang

            channel_params = {}
            if len(attachments) > 0:
                for attachment in attachments:

                    if attachment["type"] != "fallback":

                        file_src = save_and_get_facebook_file_src(
                            attachment, sender, page_access_token, selected_language, EasyChatTranslationCache)

                        if file_src:
                            channel_params = {
                                "attached_file_path": file_src,
                            }
                        else:
                            if not message.strip():
                                return HttpResponse("OK")
                                # IF ATTACHMENT IS EMPTY AND MESSAGE IS ALSO EMPTY THEN RETUN

                    channel_params = json.dumps(channel_params)
                    terminate, response = process_language_change_or_get_response(user_id, bot_id, None, bot_name, channel, channel_params, message, bot_obj, None, page_access_token, sender=sender)
            else:
                channel_params = json.dumps(channel_params)
                terminate, response = process_language_change_or_get_response(user_id, bot_id, None, bot_name, channel, channel_params, message, bot_obj, None, page_access_token, sender=sender)
                
            if terminate:
                return Response(data=response)

            if "is_livechat" in response and response["is_livechat"] == "true":
                return HttpResponse("OK")
                
            save_bot_switch_data_variable_if_availabe(user_id, bot_id, response, "Facebook")

            if "is_conversation_continue" in response["response"]["text_response"]["modes"] and response["response"]["text_response"]["modes"]["is_conversation_continue"]:
                text_response = response["response"]["text_response"]["text"]
                text_response = html_tags_formatter(text_response)
                text_response = html_list_formatter(text_response)
                text_response = get_emojized_message(text_response)
                send_facebook_message(sender, text_response, page_access_token)
                message = response["response"]["text_response"][
                    "modes"]["message_to_continue_flow"]
                response = execute_query(
                    user_id, bot_id, bot_name, message, "en", "Facebook", json.dumps(
                        {}), message)
            text_response = response["response"]["text_response"]["text"]
            text_response = html_tags_formatter(text_response)
            text_response = html_list_formatter(text_response)
            text_response = get_emojized_message(text_response)
            choices_list = response['response']['choices']
            cards_list = response['response']['cards']
            recom_list = response['response']['recommendations']

            image_urls = response["response"]["images"]

            validation_obj = EasyChatInputValidation()

            list_choice = []
            if len(choices_list) > 0:
                for choice_dict in choices_list: 
                    if "display" in choice_dict:
                        list_choice.append(choice_dict["display"])
            
            recommendations = recom_list + list_choice

            text_response = validation_obj.remo_html_from_string(text_response)
            text_response = validation_obj.unicode_formatter(text_response)
            if len(recommendations) > 13:
                for small_message in text_response.split("$$$"):
                    if small_message != "":
                        send_facebook_message(sender, small_message, page_access_token)
                        time.sleep(0.05)

            videos = response["response"]["videos"]
            if len(videos) > 0:
                for video in videos:
                    send_facebook_message(sender, video, page_access_token)
            
            # Maximum of 13 quick replies are supported.
            if len(recommendations) <= 13:
                if len(image_urls) > 0:
                    send_images(sender, image_urls, page_access_token)
                if len(cards_list) > 0:
                    send_cards(sender, cards_list, page_access_token)
                
                res_text_response = text_response.split("$$$")
                if len(res_text_response) > 1:
                    text_response = res_text_response[-1]
                    res_text_response = res_text_response[:-1]
                    for small_message in res_text_response:
                        if small_message != "":
                            send_facebook_message(sender, small_message, page_access_token)
                            time.sleep(0.05)
                if len(recommendations) > 0:
                    send_recommendations_quick_replies(
                        sender, page_access_token, recommendations=recommendations, text_response=text_response)
                else:
                    send_facebook_message(sender, text_response, page_access_token)
            else:
                send_recommendations_carousel(
                    sender, page_access_token, recommendations=recommendations)
            
                if len(image_urls) > 0:
                    send_images(sender, image_urls, page_access_token)
                if len(cards_list) > 0:
                    send_cards(sender, cards_list, page_access_token)

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "FacebookWebhookAPI: POST Method: {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': ''})
            try:
                if type(payload) != dict:
                    payload = json.loads(payload)
                meta_data = payload
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))

        return HttpResponse("OK")

    def get(self, request, *args):
        response = {}
        response["status"] = 500
        logger.info("Inside get ", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        try:
            response = verify_webhook(
                request, Bot, Channel, BotChannel)
            return response
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FacebookWebhookAPI - Method: GET - " +
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return HttpResponse("Invalid Token")


FacebookWebhook = FacebookWebhookAPI.as_view()
