from EasyChatApp.utils_validation import EasyChatInputValidation
from googletrans import client
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from django.http import HttpResponseNotFound

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_bot import *
from EasyChatApp.utils_channels import *
from EasyChatApp.utils_viber import viber_web_hook_connector, viber_api_configuration, send_welcome_message_to_viber, processing_text_and_attachments
from EasyChatApp.constants import *
from django.conf import settings
from EasyChatApp.constants_language import *
import json
import sys
from django.views.decorators.csrf import csrf_exempt


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def ViberChannel(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return render(request, 'EasyChatApp/unauthorized.html')

            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return render(request, 'EasyChatApp/unauthorized.html')
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                # Viber api token
                viber_obj = ViberDetails.objects.filter(
                    bot=selected_bot_obj).first()

                if not viber_obj:
                    viber_obj = ViberDetails.objects.create(
                        bot=selected_bot_obj)
                    logger.info("Creating new ViberDetails objects", extra={
                                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                viber_auth_token = (
                    viber_obj.viber_api_token) if viber_obj.is_active else ""
                
                viber_sender_logo_raw = json.loads(viber_obj.viber_bot_logo)

                viber_sender_logo = None

                if "sender_logo" in viber_sender_logo_raw and len(viber_sender_logo_raw["sender_logo"]) > 0:
                    viber_sender_logo = viber_sender_logo_raw["sender_logo"][0]

                channel_obj = Channel.objects.get(name="Viber")

                try:
                    bot_channel_obj = BotChannel.objects.filter(
                        bot=selected_bot_obj, channel=channel_obj)[0]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("ViberChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                        request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})

                initial_messages_pk_list = json.loads(
                    bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(
                    bot_channel_obj.failure_recommendations)["items"]

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False).first()
                    if intent_objs:
                        small_talk = intent_objs.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_objs.name,
                                "intent_pk": intent_objs.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False).first()
                    if intent_objs:
                        small_talk = intent_objs.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_objs.name,
                                "intent_pk": intent_objs.pk
                            })

                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                viber_url = settings.EASYCHAT_HOST_URL + \
                    "/chat/webhook/viber/?id=" + str(bot_pk)
                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(
                    bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                initial_messages = json.loads(bot_channel_obj.initial_messages)

                initial_messages_images = None
                initial_messages_videos = None

                if "images" in initial_messages and len(initial_messages["images"]) > 0:
                    initial_messages_images = initial_messages["images"][0]

                if "videos" in initial_messages and len(initial_messages["videos"]) > 0:
                    initial_messages_videos = initial_messages["videos"][0]

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
                        language=lang_obj, bot_channel=bot_channel_obj).first()

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                return render(request, 'EasyChatApp/channels/viber.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_channel_obj": bot_channel_obj,
                    "viber_url": viber_url,
                    "viber_auth_token": viber_auth_token,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                    "selected_language": selected_language,
                    "initial_messages_videos": initial_messages_videos,
                    "initial_messages_images": initial_messages_images,
                    "viber_sender_logo": viber_sender_logo,


                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/unauthorized.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ViberChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        return render(request, 'EasyChatApp/error_404.html')


class SaveViberChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            logger.info("Saving details of viber channel", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]

            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]

            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data['authentication_message']

            authentication_message = validation_obj.clean_html(
                authentication_message)

            initial_message_list = data["initial_message_list"]
            failure_recommendation_list = data["failure_recommendation_list"]

            is_language_auto_detection_enabled = data["is_language_auto_detection_enabled"]

            is_enable_choose_language_flow_enabled_for_welcome_response = data[
                "is_enable_choose_language_flow_enabled_for_welcome_response"]

            image_url = data["image_url"]
            video_url = data["video_url"]
            viber_sender_logo_url = data["viber_sender_logo_url"]
            bot_id = data["bot_id"]

            bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if request.user not in bot.users.all():
                response["status"] = 401
                response['status_message'] = 'You are not authorised to perform this operation.'
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            images = []
            if image_url != "":
                images = [image_url]

            videos = []
            if video_url != "":
                videos = [video_url]
            
            viber_sender_logo = []
            if viber_sender_logo_url != "":
                viber_sender_logo = [viber_sender_logo_url]

            initial_message_list = [
                str(message) for message in initial_message_list if message != ""]

            channel = Channel.objects.get(name="Viber")
            channel = BotChannel.objects.get(bot=bot, channel=channel)

            viber_obj = ViberDetails.objects.get(bot=bot)

            # Language specific
            language_specific_action(
                data, channel, bot, welcome_message, failure_message, authentication_message)

            channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})
            channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})
            channel.is_language_auto_detection_enabled = is_language_auto_detection_enabled
            channel.is_enable_choose_language_flow_enabled_for_welcome_response = is_enable_choose_language_flow_enabled_for_welcome_response
            channel.save()

            viber_obj.viber_bot_logo = json.dumps(
                {"sender_logo": viber_sender_logo})
            viber_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841

            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveViberChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'Viber', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveViberChannelDetails = SaveViberChannelDetailsAPI.as_view()


class ViberWebhookSetupAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            logger.info("Saving webhook details", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            viber_auth_token = data["viber_auth_token"]
            viber_auth_token = validation_obj.remo_html_from_string(
                viber_auth_token)
            bot_id = data["bot_id"]

            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            
            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            viber_obj = ViberDetails.objects.filter(bot=bot_obj).first()
            
            viber_webhook_url = data['viber_url']
            viber_webhook_url = settings.EASYCHAT_HOST_URL + \
                    "/chat/webhook/viber/?id=" + str(bot_id)
            viber_connection_details = viber_web_hook_connector(
                viber_webhook_url, viber_auth_token, bot_obj.name)
            if viber_connection_details:
                viber_obj.viber_api_token = viber_auth_token
                viber_obj.is_active = True
                viber_obj.save()
                response["status"] = 200
                response["message"] = str(viber_auth_token)
                response['viber_auth_token'] = viber_auth_token
                response['viber_url'] = viber_webhook_url
            else:
                response["status"] = 402
                response['message'] = 'Viber Integration was unsuccessful. Please re-verify auth token'
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ViberWebhookSetupAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ViberWebhookSetup = ViberWebhookSetupAPI.as_view()


class ViberQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        response["status_message"] = "Internal Server Error"
        channel_name = "Viber"
        try:
            logger.info("Started ViberQueryAPI", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            payload = request.data

            bot_obj = Bot.objects.get(pk=request.GET["id"], is_deleted=False)

            message_id = str(payload['message_token'])

            message_id_obj = ViberMessageDetails.objects.filter(
                message_id=message_id)

            if message_id_obj.count() > 0:
                return HttpResponse("message has been already responded")
            else:
                message_id_obj = ViberMessageDetails.objects.create(
                    message_id=message_id)

            viber_obj = ViberDetails.objects.filter(
                bot=bot_obj).first()

            viber_api_token = viber_obj.viber_api_token

            viber_sender_avatar = None

            viber_sender_avatar_raw = json.loads(viber_obj.viber_bot_logo)
            
            if 'sender_logo' in viber_sender_avatar_raw and len(viber_sender_avatar_raw['sender_logo']) > 0:
                viber_sender_avatar = viber_sender_avatar_raw['sender_logo'][0]

            viber_connector = viber_api_configuration(
                viber_api_token, bot_obj.name, viber_sender_avatar)

            channel_obj = Channel.objects.get(name="Viber")

            bot_channel = BotChannel.objects.get(
                bot=bot_obj, channel=channel_obj)

            if 'user' in payload:
                send_id = payload['user']['id']

                if payload['event'] == 'conversation_started':
                    user_obj = Profile.objects.filter(user_id=send_id, bot=bot_obj)
                    if user_obj.first().tree and user_obj.first().tree.children.all().count():
                        generate_flow_dropoff_object(user_obj.first(), True)
                    user_obj.update(tree=None, selected_language=Language.objects.filter(lang="en").first())
                    EasyChatSessionIDGenerator.objects.filter(
                        user=user_obj.first(), is_expired=False).update(is_expired=True)

                    welcome_message = bot_channel.welcome_message

                    initial_intent_obj = bot_obj.initial_intent

                    initial_intent = ''

                    initial_messages = json.loads(bot_channel.initial_messages)

                    channel_params = json.dumps({})

                    if initial_intent_obj != None:
                        
                        terminate, response = process_language_change_or_get_response(
                            send_id, bot_obj.pk, None, "uat", channel_name, channel_params, initial_intent_obj.name, bot_obj, None, viber_api_token, sender=viber_connector)

                        initial_intent = response['response']['text_response']['text']

                        if terminate:
                            return Response(data=response)
                    
                    send_welcome_message_to_viber(
                        viber_connector, send_id, bot_obj, welcome_message, initial_intent, initial_messages)

            if 'message' in payload and 'sender' in payload:
                sender_id = payload['sender']['id']

                extract_message = payload['message']
                
                processing_text_and_attachments(viber_connector, extract_message, sender_id, viber_api_token, bot_obj, viber_sender_avatar)

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "ViberQueryAPI {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            try:
                if type(payload) != dict:
                    payload = json.loads(payload)
                meta_data = payload
            except:
                meta_data = {}

            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(
                bot_obj.pk, channel_name, "", json.dumps(meta_data))

        return Response(data=response)


ViberQuery = ViberQueryAPI.as_view()
