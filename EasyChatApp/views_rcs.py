from bs4 import BeautifulSoup
import logging
import requests
import json
import sys
import time
import base64

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from django.conf import settings

from EasyChatApp.rcs_business_messaging import rbm_service
from EasyChatApp.rcs_business_messaging import messages

from EasyChatApp.utils import *
from EasyChatApp.utils_rcs import *
from EasyChatApp.utils_validation import EasyChatInputValidation
from CampaignApp.utils import update_rcs_detailed_analytics
from EasyChatApp.models import Bot, Channel, BotChannel, Config, TimeSpentByUser, Feedback, MISDashboard, Data, Intent, FlowAnalytics, Tree, FormAssist, RCSDetails, RCSMessageDetails
from EasyChatApp.utils_channels import process_language_change_or_get_response, get_message_from_reverse_channel_mapping

import pytz

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class RCSQueryAPI(APIView):
    def post(self, request, *args, **kwargs):

        logger.info("Inside post ", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'GoogleRCS', 'bot_id': 'None'})

        response = {}
        response["status"] = 500
        response["data"] = {}
        bot_id = ""
        channel = "GoogleRCS"
        try:
            payload = request.data
            bot_id = request.GET["id"]
            bot_name = 'uat'
            sender = ""
            bot_obj = Bot.objects.get(pk=int(bot_id))

            if "secret" in payload.keys():
                response = {
                    'secret': payload["secret"]
                }
                return Response(data=response)
            
            selected_bot_obj = Bot.objects.get(
                pk=int(bot_id), is_deleted=False, is_uat=True)
            rcs_obj = RCSDetails.objects.filter(bot=selected_bot_obj)[0]

            service_account_location = rcs_obj.rcs_credentials_file_path
            if payload["message"]["attributes"]["type"] == "event":
                message_response = payload["message"]["data"]
                base64_bytes = message_response.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                message_data = message_bytes.decode('utf-8')

                if not isinstance(message_data, dict):
                    message_data = json.loads(message_data)
                    tz = pytz.timezone(settings.TIME_ZONE)
                    current_time = timezone.now()
                    current_time = current_time.astimezone(tz)
                    status = message_data["eventType"]

                    update_rcs_detailed_analytics(status, message_data, current_time)

            if payload["message"]["attributes"]["type"] == "message":
                message_response = payload["message"]["data"]
                base64_bytes = message_response.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                message_data = message_bytes.decode('utf-8')
                if not isinstance(message_data, dict):
                    message_data = json.loads(message_data)
                sender = message_data["senderPhoneNumber"]
                message_id = message_data["messageId"]
                message = ""
                attachment = ""
                if payload["message"]["attributes"]["message_type"] == "TEXT" or payload["message"]["attributes"]["message_type"] == "SUGGESTION_RESPONSE":
                    if "suggestionResponse" in message_data.keys():
                        message = message_data["suggestionResponse"]["postbackData"]
                    else:
                        message = message_data["text"]
                user_id = "rcs_user_" + str(sender)
                
                set_user(user_id, message, "en", "GoogleRCS", bot_id)

                message_id_obj = RCSMessageDetails.objects.filter(
                    message_id=message_id)
                if message_id_obj.count() > 0:
                    return HttpResponse("message has been already responded")
                
                elif message == "reply:custom_suggestion_link_click":
                    return HttpResponse("message has been already responded")
                else:
                    message_id_obj = RCSMessageDetails.objects.create(
                        message_id=message_id)

                if payload["message"]["attributes"]["message_type"] == "USER_FILE":
                    attachment = message_data["userFile"]["payload"]["fileUri"]
                
                channel_params = {}
                if len(attachment) > 0:
                    
                    file_src = save_and_get_rcs_file_src(
                        attachment)

                    if file_src != "":
                        channel_params = {
                            "attached_file_path": file_src,
                        }
                    else:
                        if message.strip() == "":
                            return HttpResponse("OK")
                            # IF ATTACHMENT IS EMPTY AND MESSAGE IS ALSO EMPTY THEN RETUN
                channel_params = json.dumps(channel_params)
                
                terminate, response = process_language_change_or_get_response(user_id, bot_id, None, bot_name, channel, channel_params, message, bot_obj, service_account_location, sender=sender)
                if terminate:
                    return Response(data=response)
                query_response = response

                profile_obj = Profile.objects.filter(
                    user_id=user_id, bot=bot_obj).first()
                selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
                
                # Authentication
                try:
                    if query_response != {}:
                        if str(query_response['status_code']) == '200' and query_response['response'] != {}:
                            if 'modes' in query_response['response']["text_response"] and query_response['response']["text_response"]['modes'] != {}:
                                if 'auto_trigger_last_intent' in query_response['response']["text_response"]['modes'] and query_response['response']["text_response"]['modes']['auto_trigger_last_intent'] == 'true':
                                    if 'last_identified_intent_name' in query_response['response'] and query_response['response']['last_identified_intent_name'] != '':
                                        message = query_response['response']['last_identified_intent_name']
                                        terminate, query_response = process_language_change_or_get_response(user_id, bot_id, None, bot_name, channel, channel_params, message, bot_obj, service_account_location, sender=sender)
                                        if terminate:
                                            return Response(data=query_response)
                                        logger.info("[GoogleRCS]RCS auto trigger: execute_query after Auth response %s", str(query_response), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'GoogleRCS', 'bot_id': 'None'})
                except Exception as E:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("[GoogleRCS]RCS Cannot identify Last Intent: %s at %s", str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'GoogleRCS', 'bot_id': 'None'})

                if "is_livechat" in query_response and query_response["is_livechat"] == "true":
                    return HttpResponse("OK")
                
                save_bot_switch_data_variable_if_availabe(user_id, bot_id, query_response, "GoogleRCS")

                text_response = query_response["response"]["text_response"]["text"]
                cards_list = query_response['response']['cards']
                recom_list = query_response['response']['recommendations']
                image_urls = query_response["response"]["images"]
                videos = query_response["response"]["videos"]
                choices_list = query_response["response"]["choices"]

                validation_obj = EasyChatInputValidation()
                text_response = rcs_html_tags_formatter(text_response)
                text_response = rcs_html_list_formatter(text_response)
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

                if len(cards_list) > 0:
                    for card in cards_list:
                        title = card["title"]
                        content = card["content"]
                        img_url = card["img_url"]
                        suggestions = [
                            messages.OpenUrlAction('Click Here',
                                                    'reply:custom_suggestion_link_click',
                                                    card['link'])
                        ]
                        
                        rich_card = messages.StandaloneCard('VERTICAL',
                                                            title,
                                                            content,
                                                            suggestions,
                                                            None,
                                                            None,
                                                            None,
                                                            'SHORT')
                        cluster = messages.MessageCluster().append_message(rich_card)
                        cluster.send_to_msisdn(sender, service_account_location)
                        FileMessage = messages.FileMessage(img_url)
                        cluster = messages.MessageCluster().append_message(FileMessage)
                        cluster.send_to_msisdn(sender, service_account_location)

                if len(videos) >= 1:
                    for url in videos:
                        FileMessage = messages.FileMessage(url)

                        # Append rich card and send to the user
                        cluster = messages.MessageCluster().append_message(FileMessage)
                        cluster.send_to_msisdn(sender, service_account_location)
                
                if len(recom_list) > 0 and len(choices_list) > 0:
                    text_message = 'choose one'
                    translated_text = get_translated_text(text_message, selected_language, EasyChatTranslationCache)
                    text_msg = messages.TextMessage(translated_text)
                    cluster = messages.MessageCluster().append_message(text_msg)
                    total_recom = 0
                    for idx, choice in enumerate(choices_list):
                        total_recom = idx
                        if idx < 11:  # max limit is 11 as per rcs guidelines for suggestions
                            if len(choice["display"]) <= 25:
                                cluster.append_suggestion_chip(messages.SuggestedReply(choice["display"], choice["value"]))
                            else:
                                cluster.append_suggestion_chip(messages.SuggestedReply(choice["display"][:23] + "..", choice["value"]))
                        else:
                            break
                    
                    total_recom += 1
                    for idx, recom in enumerate(recom_list):
                        if total_recom + idx < 11:  # max limit is 11 as per rcs guidelines for suggestions
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
                        else:
                            break

                    cluster.send_to_msisdn(sender, service_account_location)

                elif len(recom_list) > 0:
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

                elif len(choices_list) > 0:
                    text_message = "choose one"
                    translated_text = get_translated_text(text_message, selected_language, EasyChatTranslationCache)
                    text_msg = messages.TextMessage(translated_text)
                    cluster = messages.MessageCluster().append_message(text_msg)
                    choices_list = choices_list[:11]  # max limit is 11 as per rcs guidelines for suggestions
                    for choice in choices_list:
                        if len(choice["display"]) <= 25:
                            cluster.append_suggestion_chip(messages.SuggestedReply(choice["display"], choice["value"]))
                        else:
                            cluster.append_suggestion_chip(messages.SuggestedReply(choice["display"][:23] + "..", choice["value"]))
                    cluster.send_to_msisdn(sender, service_account_location)

            return HttpResponse("Message recevied and answered")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "Error RCSQueryAPI {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            try:
                if type(payload) != dict:
                    payload = json.loads(payload)
                meta_data = payload
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))

        return HttpResponse("response")


RCSQuery = RCSQueryAPI.as_view()
