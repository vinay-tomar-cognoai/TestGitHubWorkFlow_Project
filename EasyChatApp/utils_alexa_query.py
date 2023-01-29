from EasyChatApp.models import *
from EasyChatApp.utils_alexa import *
from EasyChatApp.utils_channels import *
from EasyChatApp.utils_execute_query import save_bot_switch_data_variable_if_availabe, check_and_send_broken_bot_mail
from EasyChatApp.constants import ALEXA_DEFAULT_RESPONSE
from EasyChatApp.utils_channels import build_alexa_language_change_response, change_language_response_required

logger = logging.getLogger(__name__)


def build_alexa_response(request_packet, bot_id, bot_name):
    response = {}
    channel_name = "Alexa"
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        logger.info("Alexa Request Packet", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        logger.info(request_packet, extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        if request_packet["request"]["type"] == "LaunchRequest":
            channel_obj = Channel.objects.get(name=channel_name)
            bot_channel_obj = BotChannel.objects.get(
                bot=bot_obj, channel=channel_obj)

            try:
                user = Profile.objects.get(
                    user_id=request_packet["session"]["sessionId"], bot=bot_obj)
            except:
                user = Profile.objects.create(
                    user_id=request_packet["session"]["sessionId"], bot=bot_obj)

            initial_recommendations_mapping = {}
            initial_recommendations_pks = []
            initial_recommendations_str = ""
            itr = 1

            try:
                initial_recommendations_pks = json.loads(
                    bot_channel_obj.initial_messages)["items"]

            except Exception:
                pass

            for recommendation_pk in initial_recommendations_pks:
                try:
                    int_name = Intent.objects.get(pk=recommendation_pk).name
                    initial_recommendations_str += ALEXA_DEFAULT_RESPONSE["initial_recommendation"].format(
                        str(itr), int_name)
                    initial_recommendations_mapping[str(itr)] = int_name
                    itr += 1
                except:
                    pass

            user_id = ""

            if "session" in request_packet and "sessionId" in request_packet["session"]:
                user_id = request_packet["session"]["sessionId"]
                set_user(user_id, "alexa", "src", "Alexa", bot_id)

            is_change_language_triggered = change_language_response_required(
                user_id, bot_id, bot_obj, "Alexa")
            # in case if inital questions are also added then in case of alexa and google home no need to show change language response because of bad ux
            # instead one can add "change language text in alexa welcome message"
            if is_change_language_triggered and len(initial_recommendations_pks) < 1:
                language_change_message = build_alexa_language_change_response(
                    user_id, bot_id)
                response = build_alexa_speech_response(
                    bot_channel_obj.welcome_message + initial_recommendations_str + language_change_message)
            else:
                response = build_alexa_speech_response(
                    bot_channel_obj.welcome_message + initial_recommendations_str)

                save_data(user, {"REVERSE_ALEXA_MESSAGE_DICT": initial_recommendations_mapping},
                          "en", channel_name, bot_id, True)

        elif request_packet["request"]["type"] == "SessionEndedRequest":
            response = build_alexa_speech_response(
                "Thank you for connecting with Cogno AI. See you soon!", True)
        elif request_packet["request"]["intent"]["name"] == "AMAZON.StopIntent":
            response = build_alexa_speech_response(
                "Thank you for connecting with Cogno AI. See you soon!", True)
        elif request_packet["request"]["intent"]["name"] == "ChatBot":
            user_id = request_packet["session"]["sessionId"]
            message = request_packet["request"][
                "intent"]["slots"]["Intent"]["value"]

            accesstoken = "None"
            user_params = "None"
            try:
                accesstoken = request_packet["session"]["user"]["accessToken"]
                access_token_obj = AccessToken.objects.get(
                    token=str(accesstoken), application__name="Alexa")
                custom_user = access_token_obj.user
                user_params = json.loads(str(CustomUser.objects.get(
                    username=custom_user.username).user_params))
            except Exception:
                pass

            channel_params = {
                "ChannelAccessToken": accesstoken
            }

            if user_params != "None":
                channel_params.update(user_params)

            logger.info("[ENGINE]: User ID: " + str(user_id), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            logger.info("[ENGINE]: Channel: Alexa", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            logger.info("[ENGINE]: Query Message: " + str(message), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            logger.info("[ENGINE]: Channel params: %s", channel_params, extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            try:
                # fetch REVERSE_ALEXA_MESSAGE_DICT from data model
                user = Profile.objects.filter(
                    user_id=user_id, bot=bot_obj).first()
                REVERSE_ALEXA_MESSAGE_DICT = str(Data.objects.get(
                    user=user, variable='REVERSE_ALEXA_MESSAGE_DICT').get_value())
                REVERSE_ALEXA_MESSAGE_DICT = json.loads(
                    REVERSE_ALEXA_MESSAGE_DICT)
                if message in REVERSE_ALEXA_MESSAGE_DICT:
                    message = REVERSE_ALEXA_MESSAGE_DICT[message]
            except:
                pass

            channel_params = {}
            terminate, response = process_language_change_or_get_response(
                user_id, bot_id, None, bot_name, channel_name, json.dumps(channel_params), message, bot_obj)
            if terminate:
                return response
            default_response_packet = response

            save_bot_switch_data_variable_if_availabe(
                user_id, bot_id, default_response_packet, channel_name)

            is_authentication_required = default_response_packet[
                "response"]["is_authentication_required"]
            is_user_authenticated = default_response_packet[
                "response"]["is_user_authenticated"]

            if is_authentication_required and not is_user_authenticated:
                logger.info("Alexa, please link account for this user", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                response = build_alexa_account_linking_response(
                    ALEXA_DEFAULT_RESPONSE["authentication"])
                # response = build_alexa_speech_response("To use this service,
                # kindly link your account with Cogno AI")
                logger.info(response, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                return response

            text_response = default_response_packet[
                "response"]["text_response"]["text"]
            text_response = text_response.replace("<br>", "\n")

            default_recommendations = default_response_packet[
                "response"]["recommendations"]

            recommendations = []
            for recommendation in default_recommendations:
                try:
                    recommendations.append(recommendation['name'])
                except:
                    recommendations.append(recommendation)

            for choice in default_response_packet["response"]["choices"]:
                if choice['display'] != "":
                    recommendations.append(choice["display"])

            REVERSE_ALEXA_MESSAGE_DICT = {}
            recommendation_str = ""

            profile_obj = Profile.objects.filter(user_id=user_id, bot=bot_obj).first()

            selected_language = "en"
            if profile_obj and profile_obj.selected_language:
                selected_language = profile_obj.selected_language.lang

            if len(recommendations) > 0:
                recommendation_str = ""
                if default_response_packet["response"]["is_flow_ended"]:
                    recom_str_start_text = ALEXA_DEFAULT_RESPONSE["recommendation"]
                    recommendation_str += get_translated_text(recom_str_start_text, selected_language, EasyChatTranslationCache)
                else:
                    recommendation_str = ""

            for index in range(len(recommendations)):
                REVERSE_ALEXA_MESSAGE_DICT[str(
                    index + 1)] = str(recommendations[index])
                please_say_text = ALEXA_DEFAULT_RESPONSE["choice"] + str(index + 1) + " for {/reccomendation_name/} ."
                please_say_text = " " + get_translated_text(please_say_text, selected_language, EasyChatTranslationCache)
                please_say_text = please_say_text.replace("{/reccomendation_name/}", str(recommendations[index]))
                single_recommendation_str = please_say_text + " ."
                recommendation_str += single_recommendation_str

            if profile_obj:
                save_data(profile_obj, {"REVERSE_ALEXA_MESSAGE_DICT": REVERSE_ALEXA_MESSAGE_DICT},
                            "en", channel_name, bot_id, True)

            speech_response = default_response_packet[
                "response"]["speech_response"]["text"]

            response = build_alexa_speech_response(
                speech_response + recommendation_str)

            image_list = default_response_packet["response"]["images"]
            if len(image_list) > 0:
                image_url = image_list[0]
                response["response"]["card"] = {}
                response["response"]["card"]["type"] = "Standard"
                response["response"]["card"]["title"] = "Cogno AI"
                response["response"]["card"]["image"] = {}
                response["response"]["card"]["image"][
                    "smallImageUrl"] = image_url
                response["response"]["card"]["image"][
                    "largeImageUrl"] = image_url
            else:
                response["response"]["card"] = {}
                response["response"]["card"]["type"] = "Simple"
                response["response"]["card"]["title"] = "Cogno AI"
                response["response"]["card"]["text"] = text_response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_message = "build_alexa_response: no videos: {} at {}".format(str(e), str(exc_tb.tb_lineno))
        logger.warning(error_message, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        try:
            if type(request_packet) != dict:
                request_packet = json.loads(request_packet)
            meta_data = request_packet
        except:
            meta_data = {}
        meta_data["error"] = error_message
        check_and_send_broken_bot_mail(bot_id, "Alexa", "", json.dumps(meta_data))
        response = build_alexa_speech_response(
            ALEXA_DEFAULT_RESPONSE["error"], True)

    logger.info("Alexa Response Packet:", extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    logger.info(json.dumps(response), extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return response
