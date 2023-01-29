# flake8: noqa
from __future__ import print_function

import urllib2
import json
import re
from pprint import pprint

##########################################################################

SERVER_URL = "http://localhost:8000"
ERROR_RESPONSE = "Oops! Looks like something went wrong. Please try again"
WELCOME_RESPONSE = "Hi! Welcome to EasyChat. I am EasyChat. How can I help you?"
REPEAT_WELCOME_RESPONSE = "Hi! Welcome to EasyChat. I am EasyChat. What would you like to do today?"
SESSION_END_RESPONSE = "Thanks for using EasyChat"
HELP_RESPONSE = WELCOME_RESPONSE

##########################################################################


def get_channel_information(channel_name):

    data = {
        "channel_name": str(channel_name)
    }

    json_resp = get_api_response("/chat/get-channel-details/", data)

    status_code = json_resp["status"]
    initial_message_list = []

    if status_code == 200:

        WELCOME_RESPONSE = json_resp["welcome_message"]
        ERROR_RESPONSE = json_resp["failure_message"]
        REPEAT_WELCOME_RESPONSE = json_resp["reprompt_message"]
        SESSION_END_RESPONSE = json_resp["session_end_message"]
        initial_message_list = json_resp["initial_messages"]["items"]

get_channel_information("Alexa")


def build_speechlet_response(speech_output, card_output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" + speech_output + "</speak>"
        },
        'card': {
            'type': 'Simple',
            'title': "ICICI NRI",
            'content': card_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" + reprompt_text + "</speak>"
            }
        },
        'shouldEndSession': should_end_session,
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_welcome_response():
    session_attributes = {}
    speech_output = WELCOME_RESPONSE
    card_output = WELCOME_RESPONSE
    reprompt_text = REPEAT_WELCOME_RESPONSE
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, card_output, reprompt_text, should_end_session))


def handle_help_request():
    speech_output = HELP_RESPONSE
    card_output = HELP_RESPONSE
    should_end_session = False
    return build_response({}, build_speechlet_response(
        speech_output, card_output, None, should_end_session))


def handle_session_end_request():
    speech_output = SESSION_END_RESPONSE
    card_output = SESSION_END_RESPONSE
    should_end_session = True
    return build_response({}, build_speechlet_response(
        speech_output, card_output, None, should_end_session))


def send_reply(session, speech_output, card_output):
    session_attributes = {}
    reprompt_text = None
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, card_output, reprompt_text, should_end_session))


def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return get_welcome_response()


def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return handle_session_end_request()


def get_api_response(end_point, data):

    request = urllib2.Request(SERVER_URL + end_point, data=json.dumps(data))
    request.add_header("Content-Type", 'application/json')
    request.get_method = lambda: "POST"

    try:
        connection = urllib2.build_opener(urllib2.HTTPHandler()).open(request)
    except urllib2.HTTPError as e:
        connection = e

    if connection.code == 200:
        return json.loads(connection.read())
    else:
        return None


def process(message, session_id, alexa_id, device_id):

    data = {
        "user_id": session_id,
        "message": message,
        "channel": "Alexa",
        "channel_params": {

        }
    }

    response = get_api_response('/chat/query/', data)

    status_code = response["status_code"]

    if status_code == "200":

        text_response = response["response"]["text_response"]["text"]
        speech_response = response["response"]["speech_response"]["text"]
        speech_reprompt_text = response["response"][
            "speech_response"]["reprompt_text"]
        card_details = response["response"]["cards"]

        card_output = ""
        if card_details != []:
            card_output += "Visit " + \
                card_details["link"] + " for " + card_details["title"] + ". "

        if card_output == "":
            card_output = text_response

        return re.sub(r'<[^>]*?>', '', speech_response), re.sub(r'<[^>]*?>', '', card_output)
    else:
        return ERROR_RESPONSE, ERROR_RESPONSE


def lambda_handler(event, context):
    try:
        if event['session']['new']:
            on_session_started({'requestId': event['request']['requestId']},
                               event['session'])

        if event['request']['type'] == "LaunchRequest":
            return on_launch(event['request'], event['session'])

        elif event['request']['type'] == "IntentRequest":

            if event['request']['intent']['name'] == 'AMAZON.StopIntent':
                return handle_session_end_request()
            if event['request']['intent']['name'] == 'AMAZON.HelpIntent':
                return handle_help_request()

            speech_output, card_output = process(event['request']['intent']['slots']['Intent']['value'], event['session'][
                                                 'sessionId'], event['session']['user']['userId'], event['context']['System']['device']['deviceId'])

            return send_reply(event['session'], speech_output, card_output)
        elif event['request']['type'] == "SessionEndedRequest":
            return on_session_ended(event['request'], event['session'])
        else:
            return on_session_ended(event['request'], event['session'])

    except Exception:  # noqa: F841

        return send_reply(event["session"], ERROR_RESPONSE, ERROR_RESPONSE)
