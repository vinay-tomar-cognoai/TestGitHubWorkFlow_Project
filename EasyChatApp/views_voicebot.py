from django.http import JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.utils_bot import process_response_based_on_language
from EasyChatApp.utils_voicebot import *
from EasyChatApp.utils_execute_query import get_voicebot_disposition_code_details

from CampaignApp.models import CampaignConfig, VoiceBotCallerID, Campaign, CampaignVoiceBotSetting, CampaignVoiceUser

import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def VoiceBotInitializeAPI(request, bot_id):
    response = {}
    if request.method == "POST":
        bot_obj = Bot.objects.get(pk=int(bot_id))

        request_meta_data = None
        try:
            request_meta_data = json.loads(request.body)["requestMetadata"]
        except Exception:
            pass

        logger.info("VoiceBotInitializeAPI : %s", str(request_meta_data), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        voicebot_profile_obj = VoiceBotProfileDetail.objects.create(
            bot=bot_obj)
        if request_meta_data != None:
            voicebot_profile_obj.meta_data = json.dumps(request_meta_data)
            voicebot_profile_obj.save()

        if request_meta_data["Direction"] == "outbound-dial":
            in_progress_campaign_objs = Campaign.objects.filter(channel__name="Voice Bot", status="in_progress", bot=bot_obj, is_deleted=False)
            voice_campaign_objs = CampaignVoiceBotSetting.objects.filter(campaign__in=in_progress_campaign_objs)

            if voice_campaign_objs:
                voice_campaign_user = CampaignVoiceUser.objects.filter(mobile_number=request_meta_data["CallFrom"][-10:], voice_campaign__in=voice_campaign_objs).first()
                if voice_campaign_user:
                    voice_campaign_user.voice_bot_profile = voicebot_profile_obj
                    voice_campaign_user.status = "connected"
                    voice_campaign_user.save()

        response["session_id"] = str(voicebot_profile_obj.session_id)
        response["preferredLanguageCode"] = "en-IN"
    else:
        response["status"] = 404
        response["message"] = "Invalid request"

    return JsonResponse(response)


@csrf_exempt
def VoiceBotEventAPI(request, bot_id, session_id):
    response = {}
    if request.method == "POST":
        voicebot_profile_obj = VoiceBotProfileDetail.objects.get(
            session_id=session_id)
        bot_obj = voicebot_profile_obj.bot
        request_packet = json.loads(request.body)

        event = request_packet["event"].lower()
        speech_response = "Request you to rephrase your query"
        language = get_language_code("en-IN")
        action = "continue"
        channel_name = "Voice"
        hints = []
        selected_language = "en"
        disposition_code = "None"
        bot_channel_obj = BotChannel.objects.get(
            bot=bot_obj, channel__name=channel_name)

        if event == "start":

            channel_name = "Voice"
            channel_params = voicebot_profile_obj.meta_data

            user_id = ""
            if "callerId" in json.loads(channel_params) and bot_obj.masking_enabled:
                user_id = json.loads(channel_params)["callerId"]
                user_id = hashlib.md5(
                    user_id.encode()).hexdigest() + "-" + session_id
            elif "callerId" in json.loads(channel_params):
                user_id = json.loads(channel_params)["callerId"]
                user_id = str(user_id) + "-" + session_id

            selected_query, selected_language = None, "en-IN"
            selected_query = "hello"
            barge_in = False

            if selected_query != None:

                bot_id, bot_name, channel, language = bot_obj.pk, "uat", channel_name, get_language_code(
                    selected_language)

                bot_response = execute_query(
                    user_id, bot_id, bot_name, selected_query, language, channel, channel_params, selected_query)

                text_response = bot_response["response"][
                    "text_response"]["text"]

                speech_response = bot_response[
                    "response"]["speech_response"]["text"]

                if "ssml_response" in bot_response["response"] and bot_response["response"]["ssml_response"]["text"] != "":
                    text_response = bot_response["response"]["ssml_response"]["text"]
                    speech_response = bot_response["response"]["ssml_response"]["text"]

                hints = []
                if bot_response["response"]["is_flow_ended"]:
                    hints = get_asr_training_data(bot_obj)
                elif "hints" in bot_response["response"]:
                    hints = bot_response["response"]["hints"]

                action = "continue"

                if "enable_transfer_agent" in bot_response["response"] and bot_response["response"]["enable_transfer_agent"]:
                    action = "transfer"

                if "is_exit_tree" in bot_response["response"] and bot_response["response"]["is_exit_tree"]:
                    action = "exit"

                if "barge_in" in bot_response["response"] and (bot_response["response"]["barge_in"] == True or str(bot_response["response"]["barge_in"]) == "true"):
                    barge_in = True

                profile_obj = Profile.objects.get(
                    user_id=bot_response["user_id"])

                save_data(profile_obj, {"loop_event_count": 1}, 'en', 'Voice', bot_id, is_cache=False)

                disposition_code = 'None'
                try:
                    disposition_code = get_voicebot_disposition_code_details(
                        profile_obj, "en", channel, str(bot_obj.pk))
                except Exception as e:
                    logger.error("Voicebot Disposition error: %s", e, extra={
                                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                response = build_voicebot_response(text_response, speech_response, hints, selected_language, action, disposition_code, bot_channel_obj, barge_in)

                if voicebot_profile_obj.profile == None:
                    voicebot_profile_obj.profile = profile_obj
                    voicebot_profile_obj.save()
            else:
                response["status"] = 101
                response["message"] = "Invalid query identified"
        elif event == "hungup":
            speech_response = "Thank you for connecting with us. See you soon!"
        elif event == "loop":
            speech_response = "Sorry, I am not able to understand your query. Please rephrase it."
        elif event == "end":
            logger.info("Voicebot end event: %s", str(request_packet), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            voicebot_profile_obj.end_event_meta_data = json.dumps(
                request_packet)
            voicebot_profile_obj.save()
            response = build_voicebot_response("Conversation Ended. Data recieved.", "Conversation Ended. Data recieved.",
                                               hints, selected_language, "exit", disposition_code, bot_channel_obj)
        elif event == "silence":
            logger.info("Voicebot silence event: %s", str(request_packet), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response = get_silence_voicebot_response(hints, selected_language, disposition_code, voicebot_profile_obj, bot_channel_obj, Data)
        else:
            pass

        # response = build_voicebot_event_response(
        #    speech_response, language, action)
    else:
        response["status"] = 404
        response["message"] = "Invalid request"

    logger.info("Final Response: %s", str(response), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return JsonResponse(response)


@csrf_exempt
def VoiceBotQueryAPI(request, bot_id, session_id):
    try:
        response = {}
        if request.method == "POST":
            voicebot_profile_obj = VoiceBotProfileDetail.objects.get(
                session_id=session_id)
            bot_obj = voicebot_profile_obj.bot
            profile_obj = voicebot_profile_obj.profile
            request_packet = json.loads(request.body)
            channel_name = "Voice"
            bot_channel_obj = BotChannel.objects.get(
                bot=bot_obj, channel__name=channel_name)
            voicebot_config_obj = VoiceBotConfiguration.objects.filter(bot_channel=bot_channel_obj).first()

            user_tree_at_start = None
            action = "continue"
            loop_response = ""
            barge_in = False

            query_responses = request_packet["query"]["responses"]
            channel_params = voicebot_profile_obj.meta_data

            logger.info("VoiceBotQueryAPI : %s", request.body, extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            selected_query, selected_language, max_confidence = None, "en-IN", -1
            for query_response in query_responses:
                if query_response["confidence"] > max_confidence:
                    max_confidence = query_response["confidence"]
                    selected_query = query_response["text"]

            if selected_query != None:

                user_id, bot_id, bot_name, channel, language = "", bot_obj.pk, "uat", channel_name, get_language_code(
                    selected_language)
                if profile_obj != None:
                    user_id = profile_obj.user_id
                    user_tree_at_start = profile_obj.tree
                    silence_event_obj = Data.objects.filter(user=profile_obj, variable='silence_event_count').first()
                    if silence_event_obj != None and int(silence_event_obj.get_value()) > 0:
                        temp_channel_params = json.loads(channel_params)
                        temp_channel_params["response_repeat_needed"] = True
                        channel_params = json.dumps(temp_channel_params)
                    save_data(profile_obj, {"silence_event_count": 0}, 'en', 'Voice', bot_id, is_cache=False)

                selected_query = remove_backslash_before_apostrophe(
                    selected_query)
                bot_response = execute_query(
                    user_id, bot_id, bot_name, selected_query, language, channel, channel_params, selected_query)

                profile_obj = Profile.objects.get(user_id=profile_obj.user_id)

                loop_event_obj = Data.objects.filter(user=profile_obj, variable='loop_event_count').first()
                if loop_event_obj != None and profile_obj.tree == user_tree_at_start:
                    save_data(profile_obj, {"loop_event_count": int(loop_event_obj.get_value()) + 1}, 'en', 'Voice', bot_id, is_cache=False)
                    if int(loop_event_obj.get_value()) > voicebot_config_obj.loop_threshold_count:
                        if voicebot_config_obj.is_agent_handover:
                            action = "transfer"
                            loop_response = voicebot_config_obj.loop_handover_response
                        else:
                            action = "exit"
                            loop_response = voicebot_config_obj.loop_termination_response
                else:
                    save_data(profile_obj, {"loop_event_count": 1}, 'en', 'Voice', bot_id, is_cache=False)
                
                save_bot_switch_data_variable_if_availabe(user_id, bot_id, bot_response, channel)

                text_response = bot_response["response"][
                    "text_response"]["text"]

                speech_response = bot_response[
                    "response"]["speech_response"]["text"]

                if "ssml_response" in bot_response["response"] and bot_response["response"]["ssml_response"]["text"] != "":
                    text_response = bot_response["response"]["ssml_response"]["text"]
                    speech_response = bot_response["response"]["ssml_response"]["text"]
                    delete_and_update_voice_bot_response_in_mis(voicebot_profile_obj, bot_obj, text_response, channel_name, "en")

                if loop_response != "":
                    text_response = loop_response
                    speech_response = loop_response
                    delete_and_update_voice_bot_response_in_mis(voicebot_profile_obj, bot_obj, loop_response, channel_name, "en")

                hints = []
                if bot_response["response"]["is_flow_ended"]:
                    hints = get_asr_training_data(bot_obj)
                elif "hints" in bot_response["response"]:
                    hints = bot_response["response"]["hints"]

                if "enable_transfer_agent" in bot_response["response"] and bot_response["response"]["enable_transfer_agent"]:
                    action = "transfer"

                if "is_exit_tree" in bot_response["response"] and bot_response["response"]["is_exit_tree"]:
                    action = "exit"

                if "barge_in" in bot_response["response"] and (bot_response["response"]["barge_in"] == True or str(bot_response["response"]["barge_in"]) == "true"):
                    barge_in = True

                profile_obj = Profile.objects.filter(
                    user_id=bot_response["user_id"], bot__id=bot_id).first()

                disposition_code = 'None'
                try:
                    disposition_code = get_voicebot_disposition_code_details(
                        profile_obj, "en", channel, str(bot_obj.pk))
                except Exception as e:
                    logger.error("Voicebot Disposition error: %s", e, extra={
                                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                response = build_voicebot_response(
                    text_response, speech_response, hints, selected_language, action, disposition_code, bot_channel_obj, barge_in)

                if voicebot_profile_obj.profile == None:
                    voicebot_profile_obj.profile = profile_obj
                    voicebot_profile_obj.save()
            else:
                response["status"] = 101
                response["message"] = "Invalid query identified"
        else:
            response["status"] = 404
            response["message"] = "Invalid request"

        return JsonResponse(response)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Voicebot Query error: %s and %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response = {}
        response["status"] = 500
        response["message"] = "Internal server error"

    logger.info("Voicebot response: %s", json.dumps(response), extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return JsonResponse(response)


def VoiceChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")

                selected_language = "en"
                try:
                    selected_language = request.GET['selected_lang']
                except:
                    selected_language = "en"

                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                bot_channel_obj = BotChannel.objects.get(
                    bot=selected_bot_obj, channel__name="Voice")

                voicebot_config_obj = VoiceBotConfiguration.objects.filter(bot_channel=bot_channel_obj).first()
                if not voicebot_config_obj:
                    voicebot_config_obj = VoiceBotConfiguration.objects.create(bot_channel=bot_channel_obj)

                repeat_variations_list = []
                config_obj = Config.objects.all().first()
                if config_obj:
                    repeat_variations_list = json.loads(config_obj.repeat_event_variations)["items"]

                repeat_variations_json = []
                for repeat_variation in repeat_variations_list:
                    repeat_variations_json.append(repeat_variation.lower())

                campaign_config_obj = CampaignConfig.objects.filter(bot=selected_bot_obj).first()

                if not campaign_config_obj:
                    campaign_config_obj = CampaignConfig.objects.create()

                voice_bot_caller_objs = VoiceBotCallerID.objects.filter(bot=selected_bot_obj)

                return render(request, 'EasyChatApp/channels/voice_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_channel_obj": bot_channel_obj,
                    "selected_language": selected_language,
                    "bot_id": bot_pk,
                    "voice_modulation_details": bot_channel_obj.voice_modulation,
                    "default_voice_modulation": json.dumps(DEFAULT_VOICE_MODULATION),
                    "voicebot_config_obj": voicebot_config_obj,
                    "threshold_range": range(2, 9),
                    "repeat_variations_list": enumerate(repeat_variations_list),
                    "repeat_variations_json": json.dumps(repeat_variations_json),
                    "languages_supported": bot_channel_obj.languages_supported.all().values_list("lang", flat=True),
                    "voice_bot_caller_objs": voice_bot_caller_objs,
                    "voice_bot_subdomains": VOICE_BOT_SUBDOMAIN_CHOICES,
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("VoiceChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'Voice', 'bot_id': str(request.GET['id'])})
        # return HttpResponseNotFound("500")
        return render(request, 'EasyChatApp/error_500.html')


class SaveVoiceChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            bot_id = data["bot_id"]
            bot_obj = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot_obj:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = 'You are not authorised to create this campaign'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            api_key = validation_obj.remo_html_from_string(data["api_key"])
            api_token = validation_obj.remo_html_from_string(data["api_token"])
            api_subdomain = validation_obj.remo_html_from_string(data["api_subdomain"])
            api_sid = validation_obj.remo_html_from_string(data["api_sid"])

            selected_tts_provider = validation_obj.remo_html_from_string(
                data["selected_tts_provider"])
            tts_language = validation_obj.remo_html_from_string(
                data["tts_language"])
            tts_speaking_style = validation_obj.remo_html_from_string(
                data["tts_speaking_style"])
            tts_voice = validation_obj.remo_html_from_string(
                data["tts_voice"])
            tts_speaking_speed = data["tts_speaking_speed"]
            tts_pitch = data["tts_pitch"]
            asr_provider = validation_obj.remo_html_from_string(
                data["asr_provider"])
            
            silence_threshold_count = data["silence_threshold_count"]
            silence_threshold_count = validation_obj.remo_html_from_string(silence_threshold_count)

            silence_response = data["silence_response"]
            silence_response = validation_obj.remo_html_from_string(silence_response)

            silence_termination_response = data["silence_termination_response"]
            silence_termination_response = validation_obj.remo_html_from_string(silence_termination_response)

            loop_threshold_count = data["loop_threshold_count"]
            loop_threshold_count = validation_obj.remo_html_from_string(loop_threshold_count)

            is_agent_handover = data["is_agent_handover"]
            is_agent_handover = validation_obj.remo_html_from_string(is_agent_handover)

            loop_termination_response = data["loop_termination_response"]
            loop_termination_response = validation_obj.remo_html_from_string(loop_termination_response)

            loop_handover_response = data["loop_handover_response"]
            loop_handover_response = validation_obj.remo_html_from_string(loop_handover_response)

            languages_supported = data["languages_supported"]
            languages_supported = validation_obj.remo_html_from_string(languages_supported)
            languages_supported = [language for language in languages_supported.split(",") if language.strip() != ""]

            fallback_response = data["fallback_response"]
            fallback_response = validation_obj.remo_html_from_string(fallback_response)

            validation_message = validate_speed_and_pitch_values(
                selected_tts_provider, tts_speaking_speed, tts_pitch)

            if validation_message is not None:
                response["status"] = 301
                response["message"] = validation_message
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_channel_obj = BotChannel.objects.get(
                bot=bot_obj, channel__name="Voice")
            bot_channel_obj.welcome_message = welcome_message
            bot_channel_obj.failure_message = failure_message
            bot_channel_obj.authentication_message = authentication_message

            bot_channel_obj.languages_supported.clear()
            for language in languages_supported:
                lang_obj = Language.objects.filter(lang=language).first()
                if lang_obj:
                    bot_channel_obj.languages_supported.add(lang_obj)

            voicebot_config_obj = VoiceBotConfiguration.objects.filter(bot_channel=bot_channel_obj).first()
            if not voicebot_config_obj:
                voicebot_config_obj = VoiceBotConfiguration.objects.create(bot_channel=bot_channel_obj)

            voicebot_config_obj.api_key = api_key
            voicebot_config_obj.api_token = api_token
            voicebot_config_obj.api_subdomain = api_subdomain
            voicebot_config_obj.api_sid = api_sid

            voicebot_config_obj.silence_threshold_count = silence_threshold_count
            voicebot_config_obj.silence_response = silence_response
            voicebot_config_obj.silence_termination_response = silence_termination_response
            voicebot_config_obj.loop_threshold_count = loop_threshold_count
            voicebot_config_obj.is_agent_handover = is_agent_handover
            voicebot_config_obj.loop_termination_response = loop_termination_response
            voicebot_config_obj.loop_handover_response = loop_handover_response
            voicebot_config_obj.fallback_response = fallback_response
            voicebot_config_obj.save()

            voice_modulation_data = json.loads(
                bot_channel_obj.voice_modulation)

            voice_modulation_data["selected_tts_provider"] = selected_tts_provider
            voice_modulation_data[selected_tts_provider]['tts_language'] = tts_language
            voice_modulation_data[selected_tts_provider]['tts_speaking_style'] = tts_speaking_style
            voice_modulation_data[selected_tts_provider]['tts_voice'] = tts_voice
            voice_modulation_data[selected_tts_provider]['tts_speaking_speed'] = tts_speaking_speed
            voice_modulation_data[selected_tts_provider]['tts_pitch'] = tts_pitch
            voice_modulation_data[selected_tts_provider]['asr_provider'] = asr_provider
            
            bot_channel_obj.voice_modulation = json.dumps(
                voice_modulation_data)
            bot_channel_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveVoiceChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveVoiceChannelDetails = SaveVoiceChannelDetailsAPI.as_view()


class AddRepeatVariationsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)

            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            repeat_variation = data["repeat_variation"]
            repeat_variation = validation_obj.remo_html_from_string(repeat_variation)

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = 'You are not authorised to add repeat variations.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            config_obj = Config.objects.all().first()
            repeat_event_variations = json.loads(config_obj.repeat_event_variations)["items"]
            repeat_event_variations.append(repeat_variation)
            config_obj.repeat_event_variations = json.dumps({"items": repeat_event_variations})
            config_obj.save()

            response["status"] = 200
            response["message"] = "Successfully added variation."

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AddRepeatVariationsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteRepeatVariationsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)

            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            repeat_variation = data["repeat_variation"]
            repeat_variation = validation_obj.remo_html_from_string(repeat_variation)

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = 'You are not authorised to delete repeat variations.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            config_obj = Config.objects.all().first()
            repeat_event_variations = json.loads(config_obj.repeat_event_variations)["items"]

            if repeat_variation in repeat_event_variations:
                repeat_event_variations.remove(repeat_variation)

            config_obj.repeat_event_variations = json.dumps({"items": repeat_event_variations})
            config_obj.save()

            response["status"] = 200
            response["message"] = "Successfully deleted variation."

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteRepeatVariationsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AddRepeatVariations = AddRepeatVariationsAPI.as_view()
DeleteRepeatVariations = DeleteRepeatVariationsAPI.as_view()


class SaveVoiceBotCallerAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal Server Error"
        try:

            data = request.data["json_string"]
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_obj = Bot.objects.filter(pk=bot_id, is_deleted=False).first()

            caller_id = data["caller_id"]
            caller_id = validation_obj.remo_html_from_string(caller_id)

            app_id = data["app_id"]
            app_id = validation_obj.remo_html_from_string(app_id)

            user = User.objects.get(username=request.user.username)

            if bot_obj and user in bot_obj.users.all():
                if len(caller_id) == 10 and caller_id.isdigit() and len(app_id) == 4 and app_id.isdigit():

                    if VoiceBotCallerID.objects.filter(bot=bot_obj, caller_id=caller_id, app_id=app_id).exists():
                        response["status"] = "501"
                        response["message"] = "Caller ID and App ID already exists."
                    elif VoiceBotCallerID.objects.filter(bot=bot_obj, caller_id=caller_id).exists():
                        response["status"] = "502"
                        response["message"] = "Caller ID already exists."
                    elif VoiceBotCallerID.objects.filter(bot=bot_obj, app_id=app_id).exists():
                        response["status"] = "503"
                        response["message"] = "App ID already exists."
                    else:
                        voice_bot_caller_obj = VoiceBotCallerID.objects.create(bot=bot_obj, caller_id=caller_id, app_id=app_id)
                        voice_bot_caller_obj.save()

                        response["status"] = "200"
                        response["message"] = "Success"
                        response["caller_id"] = voice_bot_caller_obj.caller_id
                        response["app_id"] = voice_bot_caller_obj.app_id
                        response["voice_bot_caller_id"] = voice_bot_caller_obj.pk
                else:
                    response["message"] = "Please enter valid caller id and app id."
            else:
                response["message"] = "You do not have the access to add the caller."

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveVoiceBotCallerAPI %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteVoiceBotCallerAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal Server Error"
        try:

            data = request.data["json_string"]
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_obj = Bot.objects.filter(pk=bot_id, is_deleted=False).first()

            voice_bot_caller_id = data["voice_bot_caller_id"]
            voice_bot_caller_id = validation_obj.remo_html_from_string(voice_bot_caller_id)

            user = User.objects.get(username=request.user.username)

            if bot_obj and user in bot_obj.users.all():
                voice_bot_caller_obj = VoiceBotCallerID.objects.filter(pk=voice_bot_caller_id).first()
                if voice_bot_caller_obj:
                    voice_bot_caller_obj.delete()
                    response["status"] = "200"
                    response["message"] = "Success"
                else:
                    response["message"] = "Invalid voice caller"
            else:
                response["message"] = "You do not have access to delete the caller."

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteVoiceBotCallerAPI %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveVoiceBotCaller = SaveVoiceBotCallerAPI.as_view()
DeleteVoiceBotCaller = DeleteVoiceBotCallerAPI.as_view()
