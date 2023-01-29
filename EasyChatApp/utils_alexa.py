import logging
import sys
from EasyChatApp.utils_validation import EasyChatInputValidation

logger = logging.getLogger(__name__)


def process_string_for_google_alexa(text):
    processed_text = text
    try:
        text = text.replace("$$$", " ")
        text = text.replace("@@@", " ")
        processed_text = text.strip()
        validation_obj = EasyChatInputValidation()
        processed_text = validation_obj.remo_html_from_string(processed_text)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("process_string_for_google_alexa: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return processed_text


def build_alexa_speech_response(welcome_message, is_end_session=False):
    welcome_message = process_string_for_google_alexa(welcome_message)
    response = {
        "version": "1.0",
        "sessionAttributes": {
        },
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": welcome_message
            },
            "reprompt": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": welcome_message
                }
            },
            "shouldEndSession": is_end_session
        }
    }
    return response


def build_alexa_account_linking_response(speech_output):
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "You must authenticate with your Amazon Account to use this skill. I sent instructions for how to do this in your Alexa App"
            },
            "card": {
                "type": "LinkAccount"
            },
            "shouldEndSession": True
        },
        "sessionAttributes": {}
    }
    return response
