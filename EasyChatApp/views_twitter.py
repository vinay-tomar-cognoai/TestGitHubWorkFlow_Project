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
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.conf import settings

from EasyChatApp.utils import *
from EasyChatApp.models import *
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.utils_twitter import *
from EasyChatApp.utils_channels import *
from EasyChatApp.utils_bot import *

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def TwitterChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")

                selected_language = "en"
                try:
                    selected_language = request.GET['selected_lang']
                except:
                    selected_language = "en"

                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                channel_obj = Channel.objects.get(name="Twitter")

                bot_channel_obj = BotChannel.objects.get(
                    bot=selected_bot_obj, channel=channel_obj)

                twitter_channel_detail_obj = TwitterChannelDetails.objects.filter(
                    bot=selected_bot_obj).first()

                if twitter_channel_detail_obj == None:
                    twitter_channel_detail_obj = TwitterChannelDetails.objects.create(
                        bot=selected_bot_obj)

                failure_messages_pk_list = json.loads(
                    bot_channel_obj.failure_recommendations)["items"]

                intent_name_list_failure = []

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)

                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                initial_messages = json.loads(bot_channel_obj.initial_messages)

                initial_messages_images = None
                initial_messages_videos = None

                if "images" in initial_messages and len(initial_messages["images"]) > 0:
                    initial_messages_images = initial_messages["images"][0]

                if "videos" in initial_messages and len(initial_messages["videos"]) > 0:
                    initial_messages_videos = initial_messages["videos"][0]

                master_languages = Language.objects.all()
                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                twitter_app_id = twitter_channel_detail_obj.twitter_app_id
                twitter_api_key = twitter_channel_detail_obj.twitter_api_key
                twitter_key_api_secret = twitter_channel_detail_obj.twitter_key_api_secret
                twitter_access_token = twitter_channel_detail_obj.twitter_access_token
                twitter_access_token_secret = twitter_channel_detail_obj.twitter_access_token_secret
                twitter_bearer_token = twitter_channel_detail_obj.twitter_bearer_token
                twitter_dev_env_label = twitter_channel_detail_obj.twitter_dev_env_label
                twitter_webhook_id = twitter_channel_detail_obj.twitter_webhook_id

                twitter_webhook_url = get_twitter_webhook_url(bot_pk)

                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                return render(request, 'EasyChatApp/channels/twitter_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": bot_pk,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_channel_obj": bot_channel_obj,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "initial_messages_images": initial_messages_images,
                    "initial_messages_videos": initial_messages_videos,
                    "twitter_app_id": twitter_app_id,
                    "twitter_api_key": twitter_api_key,
                    "twitter_key_api_secret": twitter_key_api_secret,
                    "twitter_access_token": twitter_access_token,
                    "twitter_access_token_secret": twitter_access_token_secret,
                    "twitter_bearer_token": twitter_bearer_token,
                    "twitter_dev_env_label": twitter_dev_env_label,
                    "twitter_webhook_url": twitter_webhook_url,
                    "twitter_webhook_id": twitter_webhook_id,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("TwitterChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'Twitter', 'bot_id': str(request.GET['id'])})
        # return HttpResponseNotFound("500")
        return render(request, 'EasyChatApp/error_500.html')


class TwitterQueryAPI(APIView):

    # authentication_classes = (
    #     CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args):
        response = {}
        response["status"] = 500
        logger.info("Inside get ", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})
        try:
            logger.info("\nTwitterQueryAPI\n", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})
            logger.info("\nrequest.GET : {request_get}".format(
                request_get=request.GET
            ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

            crc_token = request.GET['crc_token']
            # nonce = request.GET['nonce']
            bot_id = request.GET['bot_id']

            bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            twitter_channel_detail_obj = TwitterChannelDetails.objects.get(
                bot=bot)

            twitter_key_api_secret = twitter_channel_detail_obj.twitter_key_api_secret

            response = verify_webhook(crc_token, twitter_key_api_secret)

            logger.info("\n\nresponse: {response}\n".format(
                response=json.dumps(response, indent=4)
            ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

            return Response(data=response)
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TwitterWebhookAPI - Method: GET - %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        return HttpResponse("Invalid Token")

    def post(self, request, *args, **kwargs):

        logger.info("Inside post ", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})
        logger.info(request.GET, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})
        response = {}
        response["status"] = 500
        channel = "Twitter"
        bot_id = ""

        try:
            request_packet = request.data

            logger.info("\nrequest_packet : {request_packet}".format(
                request_packet=json.dumps(request_packet, indent=4)
            ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

            bot_id = request.GET["bot_id"]
            bot_name = 'uat'
            bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            # channel = Channel.objects.get(name="Twitter")
            # bot_channel = BotChannel.objects.get(bot=bot, channel=channel)

            message_id = request_packet["direct_message_events"][0]["id"]

            if TwitterTracker.objects.filter(id_of_message=message_id).exists():
                return HttpResponse("Duplicate Request")
            else:
                TwitterTracker.objects.create(id_of_message=message_id, text_message=request_packet["direct_message_events"][0]["message_create"]["message_data"]["text"])

            twitter_channel_detail_obj = TwitterChannelDetails.objects.get(
                bot=bot)

            dm_attachment = DMAttachment()

            if "direct_message_events" in request_packet and "apps" not in request_packet:
                sender_id = request_packet["direct_message_events"][0]["message_create"]["sender_id"]

                logger.info("sender_id: " + str(sender_id), extra={'AppName': 'EasyChat',
                                                                   'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

                # created_timestamp = request_packet["direct_message_events"][0]["created_timestamp"]
                # target_recipient_id = request_packet["direct_message_events"][
                #     0]["message_create"]["target"]["recipient_id"]
                message_data = request_packet["direct_message_events"][0]["message_create"]["message_data"]
                message = message_data["text"]

                user_id = "twitter_user_" + str(sender_id)
                user = set_user(user_id, message, "en", "Instagram", bot_id)
                save_data(user, {
                          "channel_name": "Twitter"}, "en", "Instagram", bot_id, is_cache=True)

                channel_params = {}

                if "attachment" in message_data:
                    if message_data["attachment"]["media"]["type"] == "video":
                        media_url_https = message_data["attachment"]["media"]["video_info"]["variants"][1]["url"]
                        twitter_file_src = save_and_get_twitter_gif_src(
                            twitter_channel_detail_obj, media_url_https)
                    elif message_data["attachment"]["media"]["type"] == "animated_gif":
                        media_url_https = message_data["attachment"]["media"]["video_info"]["variants"][0]["url"]
                        twitter_file_src = save_and_get_twitter_gif_src(
                            twitter_channel_detail_obj, media_url_https)
                    else:
                        media_url_https = message_data["attachment"]["media"]["media_url_https"]
                        twitter_file_src = save_and_get_twitter_file_src(
                            twitter_channel_detail_obj, media_url_https)

                    logger.info("\ntwitter_file_src {twitter_file_src}".format(twitter_file_src=twitter_file_src), extra={
                                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

                    url = ""
                    if "url" in message_data["attachment"]["media"]:
                        url = message_data["attachment"]["media"]["url"]
                        message = message.replace(url, "")
                        message = message.strip()

                    if twitter_file_src == "FORMAT_NOT_SUPPORTED":
                        send_twitter_message(
                            twitter_channel_detail_obj, sender_id, "This file format is not supported")
                        return HttpResponse("OK")
                    elif twitter_file_src == "":
                        return HttpResponse("OK")
                    else:
                        # twiiter sends msg as well the url of media so emptying this field
                        channel_params = {
                            "attached_file_path": twitter_file_src,
                        }

                if "quick_reply_response" in message_data:
                    message = message_data["quick_reply_response"]["metadata"]

                channel_params = json.dumps(channel_params)

                terminate, response = process_language_change_or_get_response(user_id, bot_id, None, bot_name, channel, channel_params, message, bot, twitter_channel_detail_obj=twitter_channel_detail_obj, sender=sender_id)
                if terminate:
                    return Response(data=response)

                logger.info("execute_query response: {response}".format(
                    response=json.dumps(response, indent=4)
                ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

                if "is_livechat" in response and response["is_livechat"] == "true":
                    return HttpResponse("OK")

                save_bot_switch_data_variable_if_availabe(user_id, bot_id, response, "Twitter")

                text_response = response["response"]["text_response"]["text"]
                choices_list = response['response']['choices']
                cards = response['response']['cards']
                recommendations = response['response']['recommendations']

                try:
                    is_go_back_enabled = response['response']['is_go_back_enabled']
                except Exception:
                    is_go_back_enabled = False

                recom_list = []

                if is_go_back_enabled:
                    recom_list.append(
                        create_recommendation_option_object("Go Back", "Go Back"))

                text_response = remove_tags(text_response)
                text_response = text_link_format(text_response)

                image_urls = response["response"]["images"]
                video_urls = response["response"]["videos"]

                validation_obj = EasyChatInputValidation()

                text_response = validation_obj.remo_html_from_string(
                    text_response)
                text_response = validation_obj.unicode_formatter(text_response)

                if len(choices_list) > 0:
                    recom_list += process_recommendations_for_quick_reply(
                        choices_list)
                if len(recommendations) > 0:
                    recom_list += process_recommendations_for_quick_reply(
                        recommendations)

                button_list = []
                if len(cards) > 0:
                    button_list += process_card_for_twitter_button(cards)

                message_list = text_response.split("$$$")

                if len(message_list) > 1:
                    for small_message in message_list[:-1]:
                        if small_message != "":
                            send_twitter_message(
                                twitter_channel_detail_obj, sender_id, small_message)
                            time.sleep(0.05)

                final_message = message_list[-1]
                send_twitter_message(twitter_channel_detail_obj, sender_id, final_message,
                                     recommendation_options=recom_list, buttons=button_list)

                if len(image_urls) > 0:
                    for image_url in image_urls:
                        dm_attachment.send_attachment(twitter_channel_detail_obj, sender_id, image_url)

                if len(video_urls) > 0:
                    for video_url in video_urls:
                        send_twitter_message(twitter_channel_detail_obj, sender_id, video_url)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "Error TwitterQueryAPI {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

            try:
                if type(request_packet) != dict:
                    request_packet = json.loads(request_packet)
                meta_data = request_packet
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))
        return HttpResponse("OK")


TwitterQuery = TwitterQueryAPI.as_view()


class SaveTwitterChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = data["image_url"]
            video_url = data["video_url"]

            welcome_message = validation_obj.remo_html_from_string(
                welcome_message)
            images = []
            if image_url != "":
                images = [image_url]

            videos = []
            if video_url != "":
                videos = [video_url]

            initial_message_list = []

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if user_obj not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")
            channel = Channel.objects.get(name="Twitter")
            bot_channel = BotChannel.objects.get(bot=bot, channel=channel)
            
            ## Language specific
            language_specific_action(data, bot_channel, bot, welcome_message, failure_message, authentication_message)

            bot_channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})

            bot_channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})

            bot_channel.save()

            twitter_channel_detail_obj = TwitterChannelDetails.objects.get(
                bot=bot)

            twitter_channel_detail_obj.twitter_app_id = data["twitter_app_id"]
            twitter_channel_detail_obj.twitter_api_key = data["twitter_api_key"]
            twitter_channel_detail_obj.twitter_key_api_secret = data["twitter_key_api_secret"]
            twitter_channel_detail_obj.twitter_access_token = data["twitter_access_token"]
            twitter_channel_detail_obj.twitter_access_token_secret = data[
                "twitter_access_token_secret"]
            twitter_channel_detail_obj.twitter_bearer_token = data["twitter_bearer_token"]
            twitter_channel_detail_obj.twitter_dev_env_label = data["twitter_dev_env_label"]

            twitter_channel_detail_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveTwitterChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'Twitter', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveTwitterChannelDetails = SaveTwitterChannelDetailsAPI.as_view()


class TwitterSubscribeWebhookAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            # validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]

            bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            # channel = Channel.objects.get(name="Twitter")

            # bot_channel = BotChannel.objects.get(bot=bot, channel=channel)

            twitter_channel_detail_obj = TwitterChannelDetails.objects.get(
                bot=bot)

            twitter_webhook_configs(twitter_channel_detail_obj)
            thread = threading.Thread(target=register_twitter_webhook, args=(
                twitter_channel_detail_obj, ), daemon=True)
            thread.start()

            response_message = "Processing"

            response["status"] = 200
            response["message"] = response_message
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TwitterSubscribeWebhookAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'Twitter', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


TwitterSubscribeWebhook = TwitterSubscribeWebhookAPI.as_view()


class TwitterDeleteWebhookAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            # validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]

            bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            # channel = Channel.objects.get(name="Twitter")

            # bot_channel = BotChannel.objects.get(bot=bot, channel=channel)

            twitter_channel_detail_obj = TwitterChannelDetails.objects.get(
                bot=bot)

            response_message = delete_twitter_webhook(
                twitter_channel_detail_obj)

            response["status"] = 200
            response["message"] = response_message
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TwitterDeleteWebhookAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'Twitter', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


TwitterDeleteWebhook = TwitterDeleteWebhookAPI.as_view()


class TwitterResetConfigAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            bot_id = data["bot_id"]

            bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            twitter_channel_detail_obj = TwitterChannelDetails.objects.get(
                bot=bot)

            if twitter_channel_detail_obj.twitter_webhook_id:
                delete_twitter_webhook(
                    twitter_channel_detail_obj)

            twitter_channel_detail_obj.twitter_app_id = ""
            twitter_channel_detail_obj.twitter_api_key = ""
            twitter_channel_detail_obj.twitter_key_api_secret = ""
            twitter_channel_detail_obj.twitter_access_token = ""
            twitter_channel_detail_obj.twitter_access_token_secret = ""
            twitter_channel_detail_obj.twitter_bearer_token = ""
            twitter_channel_detail_obj.twitter_dev_env_label = ""
            twitter_channel_detail_obj.twitter_webhook_id = ""

            twitter_channel_detail_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TwitterResetConfigAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'Twitter', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


TwitterResetConfig = TwitterResetConfigAPI.as_view()
