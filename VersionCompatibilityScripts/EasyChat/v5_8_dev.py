from EasyChatApp.utils_models import sync_tree_object_training_data
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.models import *

from EasyChatApp.utils_bot import get_translated_text
import json

from EasyChatApp.constants_icon import ET_SOURCE_ICON


def sync_all_tree_objects_training_data():

    tree_objs = Tree.objects.filter(is_deleted=False)

    print("total tree_objects to be synced ->", tree_objs.count())
    for tree in tree_objs:
        sync_tree_object_training_data(tree, TrainingData, Config)


def update_voice_modulation_response():
    try:
        voice_channel_objects = BotChannel.objects.filter(
            channel__name="Voice")

        for voice_channel_object in voice_channel_objects:
            current_voice_modulation = json.loads(
                voice_channel_object.voice_modulation)
            if 'selected_tts_provider' in current_voice_modulation:
                continue
            updated_voice_modulation = DEFAULT_VOICE_MODULATION
            tts_provider = current_voice_modulation['tts_provider']
            updated_voice_modulation['selected_tts_provider'] = tts_provider
            updated_voice_modulation[tts_provider]['tts_language'] = current_voice_modulation['tts_language']
            updated_voice_modulation[tts_provider]['tts_speaking_style'] = current_voice_modulation['tts_speaking_style']
            updated_voice_modulation[tts_provider]['tts_voice'] = current_voice_modulation['tts_voice']
            updated_voice_modulation[tts_provider]['tts_speaking_speed'] = current_voice_modulation['tts_speaking_speed']
            updated_voice_modulation[tts_provider]['tts_pitch'] = current_voice_modulation['tts_pitch']
            updated_voice_modulation[tts_provider]['asr_provider'] = current_voice_modulation['asr_provider']
            updated_voice_modulation[tts_provider]['allow_barge'] = 'true' if current_voice_modulation['allow_barge'] else 'false'

            voice_channel_object.voice_modulation = json.dumps(
                updated_voice_modulation)
            voice_channel_object.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_voice_modulation_response %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def populate_ssml_response_for_intents():
    try:
        intent_objs = Intent.objects.all()
        for intent_obj in intent_objs:
            if intent_obj.tree.response == None:
                response_obj = BotResponse.objects.create()
            else:
                response_obj = intent_obj.tree.response
            sentence = json.loads(response_obj.sentence)
            if "ssml_response" in sentence["items"][0] and sentence["items"][0]["ssml_response"] != "":
                continue
            validation_obj = EasyChatInputValidation()
            if sentence["items"][0]["speech_response"] != "":
                sentence["items"][0]["ssml_response"] = sentence["items"][0]["speech_response"]
            else:
                sentence["items"][0]["ssml_response"] = validation_obj.remo_html_from_string(
                    sentence["items"][0]["text_response"])
            response_obj.sentence = json.dumps(sentence)
            response_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error populate_ssml_response_for_intents %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_rtl_languages():
    try:
        rtl_languages = ["ar", "he", "fa", "ur", "ps", "sd", "ug", "yi"]

        for rtl_language in rtl_languages:
            language = Language.objects.filter(lang=rtl_language).first()
            if language:
                language.language_script_type = "rtl"
                language.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_rtl_languages %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_default_order_of_response():
    try:
        bots = Bot.objects.filter(is_deleted=False).exclude(
            default_order_of_response=[])
        for bot in bots:
            if "phone_number" not in bot.default_order_of_response:
                default_order_of_response = json.loads(
                    bot.default_order_of_response)
                default_order_of_response.append("phone_number")
                bot.default_order_of_response = json.dumps(
                    default_order_of_response)
                bot.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_default_order_of_response %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_default_order_of_response_intent_level_feedback():
    try:
        bots = Bot.objects.filter(is_deleted=False).exclude(
            default_order_of_response=[])
        for bot in bots:
            if "intent_level_feedback" not in bot.default_order_of_response:
                default_order_of_response = json.loads(
                    bot.default_order_of_response)
                index = default_order_of_response.index("link_cards")
                if index == len(default_order_of_response) - 1:
                    default_order_of_response.append("intent_level_feedback")
                else:
                    default_order_of_response.insert(
                        index + 1, "intent_level_feedback")
                bot.default_order_of_response = json.dumps(
                    default_order_of_response)
                bot.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_default_order_of_response_intent_level_feedback %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_bot_template_objects_genreal_text():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        general_text = "Did you mean one of the following?$$$There are some internal issue, please try again later. Sorry for your inconvenience.$$$Looks like I don't have answer for selected bot query.$$$Looks like I don't have support for this channel.$$$Session is running in another tab. Please end running sessions and try again.$$$I can tell you are upset. If my answers were not helpful, you can reach out to our customer care team.$$$Sorry to hear that, we would appreciate if you could give your comments on what went wrong. Please type 'Skip' in case you don't wish to give a comment.$$$Glad that you liked our service. Hope to see you again.$$$Thanks, we would try to improve.$$$Looks like I don't have an answer to that. Here's what I found on the web.$$$Sure, How may I assist you now?$$$Looks like, I can not answer your query for now. Please try again after some time.$$$Read More$$$Read Less$$$Show Less$$$View more$$$speak now"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.general_text = get_translated_text(
                general_text, lang, EasyChatTranslationCache)

            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_bot_template_objects_genreal_text: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def livechat_RequiredBotTemplate_objects_livechat_form_text():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        livechat_form_text = "Connect with Agent$$$Please fill in these details to connect to our agent$$$Enter your Name$$$Enter Email-ID$$$Enter Phone Number$$$Continue$$$To connect with LiveChat Agent, please Click \"Continue\" and submit your details or Click \"Back\" to end the conversation.$$$Choose Category$$$Please select a valid category.$$$Unable to raise request, try once again. Please make sure you are not in an authenticated window."

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.livechat_form_text = get_translated_text(
                livechat_form_text, lang, EasyChatTranslationCache)

            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in livechat_RequiredBotTemplate_objects_livechat_form_text: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_ET_Source_icon():
    try:
        et_channel = Channel.objects.get(name="ET-Source")
        if et_channel:
            et_channel.icon = ET_SOURCE_ICON
            et_channel.save()
    except Exception as e:
        logger.error("Error in updating ET-Source icon: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running update_bot_template_objects_genreal_text...\n")

update_bot_template_objects_genreal_text()

print("Running update_rtl_languages...\n")

update_rtl_languages()

print("Running update_voice_modulation_response...\n")

update_voice_modulation_response()

print("Running populate_ssml_response_for_intents...\n")

populate_ssml_response_for_intents()

print("Running sync_all_tree_objects_training_data...\n")

sync_all_tree_objects_training_data()

print("Running update_default_order_of_response...\n")

update_default_order_of_response()

print("Running update_default_order_of_response_intent_level_feedback...\n")

update_default_order_of_response_intent_level_feedback()

print("Running update_ET_Source_icon...\n")

update_ET_Source_icon()

print("Running livechat_RequiredBotTemplate_objects_livechat_form_text...\n")

livechat_RequiredBotTemplate_objects_livechat_form_text()
