# Copyright 2018 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This class talks directly to the RBM API
endpoint to send and receive messages."""

import json
import os
import re
import uuid
import emoji
import logging

from httplib2 import Http

from EasyChatApp.models import *

# Authenticate with service account
from oauth2client.service_account import ServiceAccountCredentials

# RBM API endpoint
RBM_BASE_ENDPOINT = 'https://rcsbusinessmessaging.googleapis.com/v1/'


def emojize(text):
    """
    Utility function to handle emojis within the message text.

    Args:
        text (str): The text that will be sent to the user.

    Returns:
        A :str: Message text after emoji conversion.
    """
    return_text = text

    return_text = emoji.emojize(return_text, language='alias')
    return_text = return_text.replace(':newline:', '\n')
    return_text = return_text.replace(':quote:', '\"')

    return return_text


def send_message_with_body(msisdn, body, message_id, service_account_location):
    """
    Sends a message represented by the given JSON to the given MSISDN.

    Args:
        msisdn (str): The lmsisdn of the user in
            E.164 format, e.g. '+14155555555'.
        body (dict): Object representing the full post body.
        message_id (str): The ID of the message.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account_location,
        scopes=['https://www.googleapis.com/auth/rcsbusinessmessaging'])

    http_auth = credentials.authorize(Http())
    endpoint_url = (RBM_BASE_ENDPOINT +
                    'phones/' +
                    msisdn +
                    '/agentMessages?messageId=' +
                    message_id)

    body_string = emojize(json.dumps(body))

    resp = http_auth.request(endpoint_url,
                             method="POST",
                             body=body_string,
                             headers={'Content-Type': 'application/json'})

    return resp
    # if resp["message"]["attributes"]["type"] == "event":
    #             message_response = resp["message"]["data"]
    #             base64_bytes = message_response.encode('utf-8')
    #             message_bytes = base64.b64decode(base64_bytes)
    #             message_data = message_bytes.decode('utf-8')
    #             if not isinstance(message_data, dict):
    #                 message_data = json.loads(message_data)
    #             print(message_data)


def send_event_with_body(msisdn, body, message_id):
    """
    Sends an agent event represented by the given JSON to the given MSISDN.

    Args:
        msisdn (str): The lmsisdn of the user in
            E.164 format, e.g. '+14155555555'.
        body (dict): Object representing the full post body.
        message_id (str): The ID of the message.
    """
    endpoint_url = (RBM_BASE_ENDPOINT +
                    'phones/' +
                    msisdn +
                    '/agentEvents?eventId=' +
                    message_id)

    body_string = json.dumps(body)

    http_auth.request(endpoint_url,
                      method="POST",
                      body=body_string,
                      headers={'Content-Type': 'application/json'})


def send_message_with_body_and_suggestion_chip_list(msisdn, body, suggestion_chip_list, message_id, service_account_location):
    """
    Sends a message represented by the given JSON with the
    additional suggestion chip list JSON to the given MSISDN.

    Args:
        msisdn (str): The msisdn of the user in
            E.164 format, e.g. '+14155555555'.
        body (dict): Object representing the full post body.
        suggestionChipList (list): List of Suggestion objects
            representing a suggestion chip list
            (https://devsite.googleplex.com/rcsbusinessmessaging/rest/v1/phones.agentMessages#Suggestion)
        message_id (str): The ID of the message.
    """
    body['contentMessage']['suggestions'] = suggestion_chip_list
    resp = send_message_with_body(
        msisdn, body, message_id, service_account_location)
    return resp


def upload_file(file_url, service_account_location, thumbnail_url=None):
    """
    Uploads a file to the RBM platform.

    Args:
        file_url (str): The publicly available URL of the file.
        thumbnail_url (Optional(str)): The publicly available
            URL of the thumbnail.

    Returns:
        A :str: The file resource identifier in the RBM platform.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account_location,
        scopes=['https://www.googleapis.com/auth/rcsbusinessmessaging'])

    http_auth = credentials.authorize(Http())

    endpoint_url = RBM_BASE_ENDPOINT + 'files'

    body = {
        'fileUrl': file_url,
    }

    if thumbnail_url:
        body['thumbnailUrl'] = thumbnail_url

    body_string = json.dumps(body)

    response, content = http_auth.request(endpoint_url,
                                          method="POST",
                                          body=body_string,
                                          headers={'Content-Type': 'application/json'})

    return json.loads(content)['name']


def get_user_response_text(user_event):
    """
    Returns the user response text, either from a direct user text message or
    encoded in a suggested reply postback data
    in the form: '^.*reply:<non-empty user reply>$'.

    Args:
        user_event (dict): The user event as a dictionary.

    Returns:
        A :str: The user response text or None if
            the UserEvent was for something else.
    """
    response_text = None

    if 'text' in user_event:
        response_text = user_event['text']
    elif 'suggestionResponse' in user_event:
        reply_text_regex = re.compile(r'^.*reply:(.+)$')

        # Assumes reply text is encoded in suggested reply
        # in the format '^.*reply:<non-empty user reply>$'
        match = reply_text_regex.match(
            user_event['suggestionResponse']['postbackData'])

        if match:
            response_text = match.group(1)
    elif 'location' in user_event:  # Special case for location
        response_text = 'location'

    return response_text


def send_read_for_user_event_and_is_typing_if_message(user_event):
    """
    If the given UserEvent represents a user message, sends a READ event for
    the message followed by an IS_TYPING event. Uses the MSISDN in the
    UserEvent. Does nothing if the UserEvent does not represent a user message
    (e.g. is a suggested action postback).

    Args:
        user_event (dict): The user event as a dictionary.
    """

    # Check to see that userEvent was a user message.
    # Note: hacky assumption around format of suggestion reply postback data.
    if get_user_response_text(user_event) and 'messageId' in user_event:

        send_read_event(user_event['senderPhoneNumber'],
                        user_event['messageId'])
        send_is_typing_event(user_event['senderPhoneNumber'])


def send_read_event(msisdn, message_id):
    """
    Sends READ event to the user.

    Args:
        msisdn (str): The msisdn of the user in
            E.164 format, e.g. '+14155555555'.
        message_id (str): The ID of the message that was read.
    """
    agent_event = {
        'eventType': 'READ',
        'messageId': message_id
    }
    send_event_with_body(msisdn,
                         agent_event,
                         str(uuid.uuid4().int) + "a")


def send_is_typing_event(msisdn):
    """
    Sends IS_TYPING event to the user.

    Args:
        msisdn (str): The msisdn of the user in
            E.164 format, e.g. '+14155555555'.
    """
    agent_event = {
        'eventType': 'IS_TYPING'
    }

    send_event_with_body(msisdn, agent_event, str(uuid.uuid4().int) + "a")


def make_batch_cap_request(msisdns, service_account_location):
    """
    Makes a bulk RBM capability request check for the list of msisdns.
    The maximum number of msisdns supported is 10,000.

    Args:
        msisdns (list): List of msisdns for users in
            E.164 format, e.g. '+14155555555'.

    Returns:
        A :obj: The JSON object containing the results of the bulk check.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account_location,
        scopes=['https://www.googleapis.com/auth/rcsbusinessmessaging'])

    http_auth = credentials.authorize(Http())
    endpoint_url = (RBM_BASE_ENDPOINT + 'users:batchGet')

    body = {
        'users': msisdns
    }

    body_string = json.dumps(body)

    resp, content = http_auth.request(
        endpoint_url,
        method='POST',
        body=body_string,
        headers={'Content-Type': 'application/json'}
    )

    return json.loads(content)
