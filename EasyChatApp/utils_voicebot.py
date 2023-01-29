import os
import sys
import json
import logging
import re
import copy

from django.conf import settings
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.constants import DEFAULT_VOICE_MODULATION, DEFAULT_RESPONSE

from EasyChatApp.models import MISDashboard, Language, VoiceBotConfiguration, WhitelistedEnglishWords, Bot, Channel, BotChannel
from EasyChatApp.utils_translation_module import get_detected_language_from_text

logger = logging.getLogger(__name__)


def process_string_for_voicebot(text):
    processed_text = text
    try:
        text = text.replace("$$$", " ")
        text = text.replace("@@@", " ")
        processed_text = text.strip()
        validation_obj = EasyChatInputValidation()
        processed_text = validation_obj.remo_html_from_string(processed_text)
        processed_text = processed_text.replace("&nbsp;", " ")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("process_string_for_voicebot: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return processed_text


def get_language_code(selected_language):
    language_dict = {
        "en-IN": "en",
        "hi-IN": "hi"
    }
    return language_dict[selected_language]


def get_voice_modulation_json_data(bot_channel_obj):
    selected_provider = ""
    try:
        try:
            voice_modulation = json.loads(bot_channel_obj.voice_modulation)
        except Exception:
            voice_modulation = DEFAULT_VOICE_MODULATION

        if 'selected_tts_provider' in voice_modulation:
            selected_provider = voice_modulation['selected_tts_provider']
            voice_modulation = voice_modulation[selected_provider]

        logger.warning("\n\n\n sample voice modulation packet " + json.dumps(voice_modulation), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("get_voice_modulation_data: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return voice_modulation, selected_provider


def build_voicebot_response(text_response, speech_response, hints, language, action, disposition_code, bot_channel_obj, allow_barge=False):
    # text_response = process_string_for_voicebot(text_response)
    # speech_response = process_string_for_voicebot(speech_response)

    voice_modulation, tts_provider = get_voice_modulation_json_data(
        bot_channel_obj)

    voice_bot_config_obj = VoiceBotConfiguration.objects.filter(bot_channel=bot_channel_obj).first()

    tts_provider = tts_provider
    tts_language = voice_modulation["tts_language"]
    tts_voice = voice_modulation["tts_voice"]
    tts_speaking_style = voice_modulation["tts_speaking_style"]
    tts_speaking_speed = voice_modulation["tts_speaking_speed"]
    tts_pitch = voice_modulation["tts_pitch"]
    asr_provider = voice_modulation["asr_provider"]

    speech_response = process_speech_response(speech_response)

    ssml_speech_response = get_ssml_bot_response(
        tts_language, tts_voice, tts_speaking_style, tts_speaking_speed, tts_pitch, speech_response, tts_provider)

    asr_hints = []
    if hints != []:
        phrases_hints = [hint for hint in hints if hint != ""]
        asr_hints = [{"phrases": phrases_hints}]

    tts_audio_config = {"audioEncoding": "LINEAR16",
                        "pitch": tts_pitch, "speakingRate": tts_speaking_speed}

    sample_response_packet = {
        "action": action,
        "responseBeforeAction": True,
        "response": {
            "text": text_response,
            "ssml": ssml_speech_response,
            "ttsLanguageCode": tts_language,
            "allowBarge": allow_barge,
            "ttsVoiceProfile": tts_voice,
            "ttsProvider": tts_provider,
            "ttsSpeakingSpeed": tts_speaking_speed,
            "ttsSpeakingStyle": tts_speaking_style,
            "ttsPitch": tts_pitch,
            "asrProvider": asr_provider,
            "asrHints": asr_hints,
            "ttsAudioConfig": tts_audio_config,
            "speechCaptureTimeout": voice_bot_config_obj.silence_event_trigger_timeout
        }
    }

    logger.warning(" sample response packet " + json.dumps(sample_response_packet), extra={
                   'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    if disposition_code != "None" and isinstance(disposition_code, dict):

        sample_response_packet["responseMetadata"] = disposition_code

    elif disposition_code != "None" and isinstance(disposition_code, str):
        try:
            sample_response_packet[
                "responseMetadata"] = json.loads(disposition_code)
        except Exception:
            pass

    return sample_response_packet


def build_voicebot_event_response(speech_response, language, action):
    speech_response = process_string_for_voicebot(speech_response)
    sample_response_packet = {
        "action": action,
        "responseBeforeAction": True,
        "response": {
            "text": speech_response,
            "ssml": speech_response,
            "ttsLanguageCode": language
        }
    }
    return sample_response_packet


def get_ssml_bot_response_for_microsoft(language, voice, speaking_style, speaking_speed, pitch, response):
    speaking_speed = round(float(speaking_speed - 1), 2) * 100
    pitch = round(float((pitch - 1) / 2), 2) * 100
    speaking_style = speaking_style.lower()

    response = re.sub('<prosody.*?>', '', response)
    response = re.sub('</prosody>', '', response)

    if speaking_style == "general":
        ssml_response = """<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:emo="http://www.w3.org/2009/10/emotionml" xmlns:mstts="http://www.w3.org/2001/mstts" version="1.0" xml:lang="en-US">
            <voice name="{0}-{1}">
                <prosody rate="{2}%" pitch="{3}%">{4}</prosody>
            </voice>
        </speak>""".format(language, voice, speaking_speed, pitch, response)
    else:
        ssml_response = """<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">
            <voice name="{0}-{1}">
                <mstts:express-as style="{2}" ><prosody rate="{3}%" pitch="{4}%">{5}</prosody>
                </mstts:express-as>
            </voice>
        </speak>""".format(language, voice, speaking_style, speaking_speed, pitch, response)

    return ssml_response


def get_ssml_bot_response_for_awspolly(speaking_speed, pitch, response):
    ssml_response = """<speak>
                        <prosody rate="{0}%" pitch="{1}%">{2}</prosody>
                    </speak>""".format(speaking_speed, pitch, response)

    return ssml_response


def get_ssml_bot_response(language, voice, speaking_style, speaking_speed, pitch, response, tts_provider):
    try:
        ssml = "<speak>" + response + "</speak>"

        if tts_provider == "Microsoft":
            ssml = get_ssml_bot_response_for_microsoft(
                language, voice, speaking_style, speaking_speed, pitch, response)
        elif tts_provider == "AwsPolly":
            ssml = get_ssml_bot_response_for_awspolly(
                speaking_speed, pitch, response)

        return ssml.replace("\n", "").strip()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_ssml_bot_response: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return "<speak>Looks like I can not answer your query for now. Please try again after some time.</speak>"


def save_asr_training_data_into_file(bot_obj, Intent):
    try:
        intents = Intent.objects.filter(bots__in=[bot_obj], is_deleted=False)
        asr_training_data_list = []
        for intent in intents:
            training_data = json.loads(intent.training_data)
            training_data = training_data.values()
            asr_training_data_list.extend(
                [data.strip() for data in training_data if data != ""])

        if not os.path.isdir(settings.SECURE_MEDIA_ROOT + "EasyChatApp/asr_training_data"):
            os.mkdir(settings.SECURE_MEDIA_ROOT +
                     "EasyChatApp/asr_training_data")

        filename = settings.SECURE_MEDIA_ROOT + \
            "EasyChatApp/asr_training_data/bot-" + str(bot_obj.pk) + ".json"
        asr_training_data_file = open(filename, "w")
        asr_training_data_file.write(json.dumps(asr_training_data_list))
        asr_training_data_file.close()
        return filename
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("save_asr_training_data_into_file: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return None


def get_asr_training_data(bot_obj):
    try:
        filename = settings.SECURE_MEDIA_ROOT + \
            "EasyChatApp/asr_training_data/bot-" + str(bot_obj.pk) + ".json"
        asr_training_data_list = json.loads(open(filename, "r").read())
        return asr_training_data_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("save_asr_training_data_into_file: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return []


def remove_backslash_before_apostrophe(selected_query):
    try:
        if "\\'" not in selected_query:
            return selected_query

        selected_query = selected_query.replace("\\'", "'")

        return remove_backslash_before_apostrophe(selected_query)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("remove_backslash_before_apostrophe: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return selected_query


def get_call_recording_url(user_id, bot_obj, Profile, VoiceBotProfileDetail):
    recording_url = ""
    try:
        profile_obj = Profile.objects.filter(user_id=user_id, bot=bot_obj).first()
        voicebot_profile_obj = VoiceBotProfileDetail.objects.filter(
            profile=profile_obj).first()

        if voicebot_profile_obj != None:
            recording_url = json.loads(voicebot_profile_obj.end_event_meta_data)[
                "requestMetadata"]["Stream"]["RecordingUrl"]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_call_recording_url: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return recording_url


def validate_speed_and_pitch_values(provider, speaking_speed, pitch):
    try:
        provider_values_mapping = {
            'Microsoft': {'speaking_speed': [0, 3], 'pitch': [0, 2]},
            'Google': {'speaking_speed': [0, 4], 'pitch': [-20, 20]},
            'AwsPolly': {'speaking_speed': [20, 200], 'pitch': [-20, 20]},
        }

        speaking_speed_range = provider_values_mapping[provider]['speaking_speed']
        if speaking_speed < speaking_speed_range[0] or speaking_speed > speaking_speed_range[1]:
            return "Please enter a valid Speaking Speed Value!"

        pitch_range = provider_values_mapping[provider]['pitch']
        if pitch < pitch_range[0] or pitch > pitch_range[1]:
            return "Please enter a valid Pitch Value!"

        return None

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("validate_speed_and_pitch_values: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return "Please enter valid Speed and Pitch Values!"


def process_speech_response(speech_response):
    try:
        speech_response = speech_response.replace("\n", "").strip()
        speech_response = re.sub('<speak.*?>', '', speech_response)
        speech_response = re.sub('</speak>', '', speech_response)
        speech_response = re.sub('<voice.*?>', '', speech_response)
        speech_response = re.sub('</voice>', '', speech_response)
        speech_response = speech_response.strip()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("process_speech_response: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return speech_response


def get_selected_tts_provider_name(bot_obj, BotChannel):
    try:
        voice_channel_obj = BotChannel.objects.filter(bot=bot_obj, channel__name="Voice")
        if voice_channel_obj.exists():
            voice_channel_obj = voice_channel_obj.first()
            selected_tts_provider = json.loads(voice_channel_obj.voice_modulation)['selected_tts_provider']
            if selected_tts_provider == 'AwsPolly':
                selected_tts_provider = 'AWS Polly'
            return selected_tts_provider

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("process_speech_response: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return DEFAULT_VOICE_MODULATION['selected_tts_provider']


def save_voice_bot_response_in_mis_dashboard(voicebot_profile_obj, bot_obj, query, bot_response, channel_name, src):
    try:
        from EasyChatApp.utils_execute_query import get_encrypted_message

        encrypted_message = get_encrypted_message(query, bot_obj, src, channel_name, voicebot_profile_obj.profile.user_id, False)
        encrypted_bot_response = get_encrypted_message(bot_response, bot_obj, src, channel_name, voicebot_profile_obj.profile.user_id, False)
        MISDashboard.objects.create(message_received=encrypted_message, bot=bot_obj, bot_response=encrypted_bot_response, user_id=voicebot_profile_obj.profile.user_id, session_id=voicebot_profile_obj.session_id, channel_name=channel_name, selected_language=Language.objects.get(lang=src))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_voice_bot_response_in_mis_dashboard: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_silence_voicebot_response(hints, selected_language, disposition_code, voicebot_profile_obj, bot_channel_obj, Data):
    try:
        from EasyChatApp.utils_execute_query import save_data

        profile_obj = voicebot_profile_obj.profile
        silence_event_obj = Data.objects.filter(user=profile_obj, variable='silence_event_count').first()
        silence_event_count = 0

        voicebot_config_obj = VoiceBotConfiguration.objects.filter(bot_channel=bot_channel_obj).first()

        if silence_event_obj == None:
            save_data(profile_obj, {"silence_event_count": 1}, 'en', 'Voice', bot_channel_obj.bot.pk, is_cache=False)
        else:
            silence_event_count = silence_event_obj.get_value()

        if int(silence_event_count) < voicebot_config_obj.silence_threshold_count:
            save_data(profile_obj, {"silence_event_count": int(silence_event_count) + 1}, 'en', 'Voice', bot_channel_obj.bot.pk, is_cache=False)
            response = build_voicebot_response(voicebot_config_obj.silence_response, voicebot_config_obj.silence_response, hints, selected_language, "continue", disposition_code, bot_channel_obj)
            save_voice_bot_response_in_mis_dashboard(voicebot_profile_obj, voicebot_profile_obj.bot, "silence_response", voicebot_config_obj.silence_response, "Voice", selected_language)
        else:
            response = build_voicebot_response(voicebot_config_obj.silence_termination_response, voicebot_config_obj.silence_termination_response, hints, selected_language, "exit", disposition_code, bot_channel_obj)
            save_voice_bot_response_in_mis_dashboard(voicebot_profile_obj, voicebot_profile_obj.bot, "silence_termination_response", voicebot_config_obj.silence_termination_response, "Voice", selected_language)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_silence_voicebot_response: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response = build_voicebot_response("Sorry, we did not get any response from your side. Thanks for calling us.", "Sorry, we did not get any response from your side. Thanks for calling us.", hints, selected_language, "exit", disposition_code, bot_channel_obj)
    
    return response


def delete_and_update_voice_bot_response_in_mis(voicebot_profile_obj, bot_obj, bot_response, channel_name, src):
    try:
        from EasyChatApp.utils_execute_query import get_encrypted_message

        encrypted_bot_response = get_encrypted_message(bot_response, bot_obj, src, channel_name, voicebot_profile_obj.profile.user_id, False)

        mis_obj = MISDashboard.objects.filter(user_id=voicebot_profile_obj.profile.user_id).order_by("-pk")[0]

        MISDashboard.objects.create(message_received=mis_obj.message_received, bot=mis_obj.bot, bot_response=encrypted_bot_response, user_id=voicebot_profile_obj.profile.user_id, session_id=voicebot_profile_obj.session_id, channel_name=channel_name, selected_language=mis_obj.selected_language)
        mis_obj.delete()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_voice_bot_response_in_mis_dashboard: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def check_is_language_supported_for_voice_bot(easychat_bot_user, language):
    try:
        bot_obj = easychat_bot_user.bot_obj
        channel_name = easychat_bot_user.channel_name

        bot_channel_obj = BotChannel.objects.filter(bot=bot_obj, channel=Channel.objects.get(name=channel_name)).first()

        return bool(bot_channel_obj.languages_supported.filter(lang=language).first())

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_is_langauge_supported_for_voice_bot: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return False


def get_detected_language_for_voice_bot(easychat_bot_user, message):
    try:
        is_language_not_found_response = False
        is_auto_language_change_detected, detected_language = get_detected_language_from_text(easychat_bot_user.src, message, easychat_bot_user.bot_info_obj, WhitelistedEnglishWords)

        if is_auto_language_change_detected and not check_is_language_supported_for_voice_bot(easychat_bot_user, detected_language):
            is_language_not_found_response = True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_detected_language_for_voice_bot: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return is_language_not_found_response, detected_language


def build_voicebot_fallback_response(user, message, easychat_bot_user, easychat_params):
    try:
        from EasyChatApp.utils_execute_query import get_encrypted_message
        response = copy.deepcopy(DEFAULT_RESPONSE)

        bot_obj = easychat_bot_user.bot_obj
        channel_name = easychat_bot_user.channel_name
        bot_channel_obj = BotChannel.objects.filter(bot=bot_obj, channel=Channel.objects.get(name=channel_name)).first()

        voicebot_config_obj = VoiceBotConfiguration.objects.filter(bot_channel=bot_channel_obj).first()

        response["user_id"] = user.user_id
        response["bot_id"] = bot_obj.pk

        response["response"]["speech_response"]["text"] = voicebot_config_obj.fallback_response
        response["response"]["text_response"]["text"] = voicebot_config_obj.fallback_response
        response["response"]["is_exit_tree"] = True

        response["status"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"]["easy_search_results"] = []
        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
        response["response"]["is_response_to_be_language_processed"] = False

        encrypted_message = get_encrypted_message(message, bot_obj, easychat_bot_user.src, "Voice", easychat_bot_user.user_id, False)
        encrypted_bot_response = get_encrypted_message(voicebot_config_obj.fallback_response, bot_obj, easychat_bot_user.src, "Voice", easychat_bot_user.user_id, False)
        MISDashboard.objects.create(message_received=encrypted_message, bot=bot_obj, bot_response=encrypted_bot_response, user_id=easychat_bot_user.user_id, session_id=easychat_params.session_id, channel_name="Voice", selected_language=Language.objects.get(lang=easychat_bot_user.src))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("build_voicebot_fallback_response: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response
