from EasyChatApp.models import *
from EasyChatApp.utils_google import *
from EasyChatApp.utils_alexa import *
from EasyChatApp.utils_channels import *
from EasyChatApp.utils_execute_query import get_message_list_using_pk
from EasyChatApp.utils_execute_query import save_bot_switch_data_variable_if_availabe, check_and_send_broken_bot_mail

logger = logging.getLogger(__name__)


"""
function: build_google_home_welcome_response
input params:
    bot_id: id of bot
    bot_name: name of bot
output:
    return welcome response for google assistant according to android channel template
"""


def build_google_home_welcome_response(bot_id, bot_name, webhook_request_packet={}):
    logger.info("Into build_google_home_welcome_response...", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
    response = {}
    webhook_response = copy.deepcopy(DEFAULT_WEBHOOK_RESPONSE)
    system_intent = copy.deepcopy(DEFAULT_WEBHOOK_SYSTEM_INTENT)
    channel = "GoogleHome"
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        channel_obj = Channel.objects.get(name="GoogleHome")
        bot_channel_obj = BotChannel.objects.get(
            bot=bot_obj, channel=channel_obj)

        text_response = bot_channel_obj.welcome_message
        speech_response = bot_channel_obj.welcome_message
        initial_recommendations_pks = json.loads(bot_channel_obj.initial_messages)["items"]
        message_list = []
        user_id = ""
        initial_recommendations_mapping = {}
        initial_recommendations_str = ""
        itr = 1
        if "session" in webhook_request_packet:
            user_id = webhook_request_packet["session"].split("/")[-1]
            set_user(user_id, "googlehome", "src", "GoogleHome", bot_id)
        for recommendation_pk in initial_recommendations_pks:
            try:
                int_name = Intent.objects.get(pk=recommendation_pk, is_deleted=False).name
                initial_recommendations_str += GOOGLE_HOME_DEFAULT_RESPONSE["initial_recommendation"].format(
                    str(itr), int_name)
                initial_recommendations_mapping[str(itr)] = int_name
                message_list.append(int_name)
                itr += 1
            except:
                pass

        language_selection_list = []
        # initial questions to be shown in case of inital questions 
        if len(message_list) < 1 and change_language_response_required(user_id, bot_id, bot_obj, "GoogleHome"):
            language_speech_response, language_selection_list = build_google_home_language_choices(
                bot_id, user_id)
            text_response += " Please choose your language " + language_speech_response
            speech_response += " Please choose your language " + language_speech_response
        else:
            speech_response += initial_recommendations_str

        # Text and Speech Repsponse
        webhook_response["fulfillmentText"] = process_string_for_google_alexa(
            text_response)
        webhook_response["payload"]["google"]["richResponse"]["items"][
            0]["simpleResponse"]["textToSpeech"] = process_string_for_google_alexa(speech_response)
        webhook_response["payload"]["google"]["richResponse"]["items"][
            0]["simpleResponse"]["displayText"] = process_string_for_google_alexa(text_response)

        for message in message_list:
            option = message

            list_select_item = {
                "optionInfo": {
                    "key": str(option).strip()
                },
                "title": str(option).strip()
            }

            system_intent["systemIntent"]["data"][
                "listSelect"]["items"].append(list_select_item)

        for selection in language_selection_list:
            key = selection["key"]
            value = selection["value"]

            option_info = {
                "optionInfo": {
                    "key": key
                },
                "title": value
            }
            system_intent["systemIntent"]["data"][
                "listSelect"]["items"].append(option_info)

        if len(message_list) >= 1 or len(language_selection_list) >= 1:
            webhook_response["payload"]["google"][
                "systemIntent"] = system_intent["systemIntent"]

        response = webhook_response
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_message = "[ENGINE]: {} at {}".format(str(e), str(exc_tb.tb_lineno))
        logger.error(error_message, extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
        try:
            if type(webhook_request_packet) != dict:
                webhook_request_packet = json.loads(webhook_request_packet)
            meta_data = webhook_request_packet
        except:
            meta_data = {}
        meta_data["error"] = error_message
        check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))
        response = copy.deepcopy(DEFAULT_WEBHOOK_RESPONSE)

    logger.info("Exit from build_google_home_welcome_response...", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
    return response


"""
function: build_google_home_response
input params:
    webhook_request_packet: request packet from google assistant
    bot_id: id of bot
    bot_name: name of bot
output:
    return response for google assistant according to android channel template
"""


def build_google_home_response(webhook_request_packet, bot_id, bot_name):
    logger.info("Into build_google_home_response...", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
    response = {}
    webhook_response = copy.deepcopy(DEFAULT_WEBHOOK_RESPONSE)
    channel_name_str = "GoogleHome"
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        logger.info("bot_id: %s", str(bot_id), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
        logger.info("bot_name: %s", str(bot_name), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})

        logger.info(webhook_request_packet, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
        selected_bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
        channel = Channel.objects.filter(name="GoogleHome").first()
        google_project_obj = GoogleAlexaProjectDetails.objects.get(
            bot=selected_bot_obj, channel=channel)
        try:
            if webhook_request_packet["queryResult"]["queryText"] == "GOOGLE_ASSISTANT_WELCOME":
                return build_google_home_welcome_response(bot_id, bot_name, webhook_request_packet)
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
            pass

        channel_name = "GoogleHome"
        user_query = str(webhook_request_packet["originalDetectIntentRequest"][
            "payload"]["inputs"][0]["rawInputs"][0]["query"]).strip()
        accesstoken = "None"
        user_params = "None"
        try:
            accesstoken = str(webhook_request_packet["originalDetectIntentRequest"][
                "payload"]["user"]["accessToken"])
            access_token_obj = AccessToken.objects.get(
                token=str(accesstoken), application__name=google_project_obj.name)
            custom_user = access_token_obj.user
            user_params = json.loads(str(CustomUser.objects.get(
                username=custom_user.username).user_params))
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})

        user_id = webhook_request_packet["session"].split("/")[-1]
        if "device" in webhook_request_packet["originalDetectIntentRequest"]["payload"]:
            if "location" in webhook_request_packet["originalDetectIntentRequest"]["payload"]["device"]:
                channel_params = {"google_home_location": webhook_request_packet["originalDetectIntentRequest"]["payload"]["device"]["location"],
                                  "ChannelAccessToken": accesstoken}
        else:
            channel_params = {
                "ChannelAccessToken": accesstoken
            }

        if user_params != "None":
            channel_params.update(user_params)

        logger.info("[ENGINE]: User ID: " + str(user_id), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
        logger.info("[ENGINE]: Channel: GoogleHome", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
        logger.info("[ENGINE]: Query Message: " + str(user_query), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
        logger.info("[ENGINE]: Channel params: %s", channel_params, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})

        try:
            # fetch REVERSE_GOOGLEHOME_MESSAGE_DICT from data model
            message = str(user_query)
            if "arguments" in webhook_request_packet["originalDetectIntentRequest"]["payload"]["inputs"][0]:
                arguments = webhook_request_packet["originalDetectIntentRequest"]["payload"]["inputs"][0]["arguments"][0]
                if "name" in arguments and arguments["name"] == "OPTION":
                    message = arguments["textValue"]
            user = Profile.objects.get(user_id=user_id, bot=bot_obj)
            REVERSE_GOOGLEHOME_MESSAGE_DICT = str(Data.objects.get(
                user=user, variable='REVERSE_GOOGLEHOME_MESSAGE_DICT').get_value())
            REVERSE_GOOGLEHOME_MESSAGE_DICT = json.loads(
                REVERSE_GOOGLEHOME_MESSAGE_DICT)
            if message in REVERSE_GOOGLEHOME_MESSAGE_DICT:
                message = REVERSE_GOOGLEHOME_MESSAGE_DICT[message]
                user_query = message
                logger.info("Reverse mapping message googlehome", extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'GoogleHome', 'bot_id': '1'})
                logger.info(message, extra={'AppName': 'EasyChat', 'user_id': 'None',
                                            'source': 'None', 'channel': 'GoogleHome', 'bot_id': '1'})

        except:
            # logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'GoogleHome', 'bot_id': '1'})
            pass
        terminate, response = process_language_change_or_get_response(
            user_id, bot_id, None, bot_name, channel_name, json.dumps(channel_params), message, bot_obj)
        if terminate:
            return response
        default_response_packet = response

        save_bot_switch_data_variable_if_availabe(
            user_id, bot_id, default_response_packet, channel_name)

        logger.info(default_response_packet, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})

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

        REVERSE_GOOGLEHOME_MESSAGE_DICT = {}
        recommendation_str = ""
        profile_obj = Profile.objects.filter(user_id=user_id, bot=bot_obj).first()

        selected_language = "en"
        if profile_obj and profile_obj.selected_language:
            selected_language = profile_obj.selected_language.lang

        if len(recommendations) > 0:
            recommendation_str = ""
            if default_response_packet["response"]["is_flow_ended"]:
                recom_str_start_text = " You can also ask me queries as follows . "
                recommendation_str += get_translated_text(recom_str_start_text, selected_language, EasyChatTranslationCache)
            else:
                recommendation_str = ""  # " Please ask one of the following . "
                
        for index in range(len(recommendations)):
            REVERSE_GOOGLEHOME_MESSAGE_DICT[str(
                index + 1)] = str(recommendations[index])
            please_say_text = "Please say " + str(index + 1) + " for {/reccomendation_name/} ."
            please_say_text = " " + get_translated_text(please_say_text, selected_language, EasyChatTranslationCache)
            please_say_text = please_say_text.replace("{/reccomendation_name/}", str(recommendations[index]))
            single_recommendation_str = please_say_text + " ."
            recommendation_str += single_recommendation_str

        if profile_obj:
            save_data(profile_obj, {"REVERSE_GOOGLEHOME_MESSAGE_DICT": REVERSE_GOOGLEHOME_MESSAGE_DICT},
                      "en", channel_name, bot_id, True)

        is_authentication_required = default_response_packet[
            "response"]["is_authentication_required"]
        is_user_authenticated = default_response_packet[
            "response"]["is_user_authenticated"]
        if is_authentication_required and not is_user_authenticated:
            logger.info("Google, please link account for this user", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
            return ASK_FOR_SIGNIN_GOOGLE

        if "is_location_required" in default_response_packet["response"]["text_response"]["modes"]:
            is_location_required = default_response_packet["response"][
                "text_response"]["modes"]["is_location_required"]
            if is_location_required == "true":
                logger.info("Google, please ask user for location", extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
                logger.info(ASK_FOR_USER_LOCATION, extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
                return ASK_FOR_USER_LOCATION

        if str(default_response_packet["status_code"]) == "200":

            text_response = default_response_packet[
                "response"]["text_response"]["text"]

            text_response = process_string_for_google_alexa(text_response)

            speech_response = default_response_packet[
                "response"]["speech_response"]["text"]

            speech_response += recommendation_str
            speech_response = process_string_for_google_alexa(speech_response)

            # Google Text and Speech Repsponse
            webhook_response["fulfillmentText"] = text_response
            webhook_response_text_speech_response = build_google_home_text_speech_response(
                text_response, speech_response)
            webhook_response["payload"]["google"]["richResponse"]["items"] = [
                webhook_response_text_speech_response]

            if "tables" in default_response_packet["response"]:
                table_list = default_response_packet["response"]["tables"]
                if len(table_list) > 1:
                    webhook_table_card = build_google_home_table_card_response(
                        table_list)
                    if webhook_table_card != None:
                        webhook_response["payload"]["google"]["richResponse"]["items"].append(
                            webhook_table_card)

            image_list = default_response_packet["response"]["images"]
            video_list = default_response_packet["response"]["videos"]
            if image_list != [] and video_list != []:
                video_url = video_list[0]
                image_url = image_list[0]

                basicCard = {}  # noqa: N806
                basicCard["title"] = ""
                basicCard["image_url"] = image_url
                basicCard["image_accessibility_text"] = ""
                basicCard["button_title"] = "Click here"
                basicCard["button_url"] = video_url

                webhook_response_basic_card = build_google_home_basic_card_response(
                    basicCard)
                if webhook_response_basic_card != None:
                    webhook_response["payload"]["google"]["richResponse"]["items"].append(
                        webhook_response_basic_card)

            elif image_list != [] and video_list == []:
                basicCard = {}  # noqa: N806
                basicCard["title"] = ""
                basicCard["image_url"] = image_list[0]
                basicCard["image_accessibility_text"] = ""

                webhook_response_basic_card = build_google_home_basic_card_response(
                    basicCard)
                if webhook_response_basic_card != None:
                    webhook_response["payload"]["google"]["richResponse"]["items"].append(
                        webhook_response_basic_card)

            elif image_list == [] and video_list != []:

                basicCard = {}  # noqa: N806
                basicCard["title"] = ""
                basicCard[
                    "image_url"] = ""
                basicCard["image_accessibility_text"] = ""
                basicCard["button_title"] = "Click here"
                basicCard["button_url"] = video_list[0]

                webhook_response_basic_card = build_google_home_basic_card_response(
                    basicCard)
                if webhook_response_basic_card != None:
                    webhook_response["payload"]["google"]["richResponse"]["items"].append(
                        webhook_response_basic_card)

            card_list = default_response_packet["response"]["cards"]
            if len(card_list) == 1:
                basicCard = {}  # noqa: N806
                basicCard["title"] = str(card_list[0]["title"])
                basicCard["image_url"] = str(card_list[0]["img_url"])
                basicCard["image_accessibility_text"] = str(
                    card_list[0]["title"])
                basicCard["description"] = str(card_list[0]["content"])
                basicCard["button_title"] = "Click here"
                basicCard["button_url"] = str(card_list[0]["link"])

                webhook_response_basic_card = build_google_home_basic_card_response(
                    basicCard)
                if webhook_response_basic_card != None:
                    webhook_response["payload"]["google"]["richResponse"]["items"].append(
                        webhook_response_basic_card)

            carousel_tiles = []
            for index in range(len(card_list)):
                carousel_tiles.append({
                    "title": str(card_list[index]["title"]),
                    "target_url": str(card_list[index]["link"]),
                    "image_url": str(card_list[index]["img_url"]),
                    "image_accessibility_text": str(card_list[index]["title"])
                })

            webhook_response_carousel_browse = build_google_home_carousel_browse_response(
                carousel_tiles)

            if webhook_response_carousel_browse != None:
                webhook_response["payload"]["google"]["richResponse"]["items"].append(
                    webhook_response_carousel_browse)

            # Google Choice and visual selection list
            choice_list = default_response_packet["response"]["choices"]
            recommendations = default_response_packet[
                "response"]["recommendations"]

            if len(recommendations) > 1:
                selection_list = []
                for recommendation in recommendations:
                    try:
                        selection_list.append({
                            "key": recommendation['name'],
                            "value": recommendation['name']
                        })
                    except:
                        selection_list.append({
                            "key": recommendation,
                            "value": recommendation
                        })

                visual_selection_list_select = build_google_home_visual_selection_list_select(
                    selection_list)

                if visual_selection_list_select != None:
                    webhook_response["payload"]["google"][
                        "systemIntent"] = visual_selection_list_select["systemIntent"]

            elif len(choice_list) > 1 and len(choice_list) < 8:

                is_suggestion_chips = True
                for choice in choice_list:
                    if len(choice["value"]) > 20 or len(choice_list) > 8:
                        is_suggestion_chips = False
                        break

                if is_suggestion_chips:
                    suggestion_list = []
                    for choice in choice_list:
                        suggestion_list.append(str(choice["value"]))

                    suggestion_chips = build_google_home_suggestion_chips(
                        suggestion_list)
                    if suggestion_chips != None:
                        webhook_response["payload"]["google"][
                            "richResponse"]["suggestions"] = suggestion_chips
                else:
                    selection_list = []
                    for choice in choice_list:
                        selection_list.append({
                            "key": choice["value"],
                            "value": choice["display"]
                        })
                    visual_selection_list_select = build_google_home_visual_selection_list_select(
                        selection_list)
                    if visual_selection_list_select != None:
                        webhook_response["payload"]["google"][
                            "systemIntent"] = visual_selection_list_select["systemIntent"]

            response = webhook_response
            logger.info("GoogleHome Bot Response: %s", json.dumps(response), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
        else:
            response = copy.deepcopy(DEFAULT_WEBHOOK_RESPONSE)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error_message = "[ENGINE]: {} at {}".format(str(e), str(exc_tb.tb_lineno))
        logger.error(error_message, extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
        try:
            if type(webhook_request_packet) != dict:
                webhook_request_packet = json.loads(webhook_request_packet)
            meta_data = webhook_request_packet
        except:
            meta_data = {}
        meta_data["error"] = error_message
        check_and_send_broken_bot_mail(bot_id, channel_name_str, "", json.dumps(meta_data))
        response = copy.deepcopy(DEFAULT_WEBHOOK_RESPONSE)

    logger.info("Exit from build_google_home_response...", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'none', 'channel': 'none', 'bot_id': 'none'})
    return response
