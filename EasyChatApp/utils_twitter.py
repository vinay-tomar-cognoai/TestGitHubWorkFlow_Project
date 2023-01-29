import sys
import json
import requests
import logging
import re
import time
import magic
import mimetypes
import base64
import hashlib
import hmac
import urllib.parse

from EasyChatApp.utils_validation import *
from requests.structures import CaseInsensitiveDict
from django.shortcuts import HttpResponse
from requests_oauthlib import OAuth1
from django.conf import settings
from datetime import datetime
from hashlib import sha1
from uuid import uuid4
import threading

logger = logging.getLogger(__name__)
file_validation_obj = EasyChatFileValidation()


def remove_tags(text):
    text = text.replace("<br>", "")
    text = text.replace("<b>", "")
    text = text.replace("</b>", "")
    text = text.replace("<i>", "")
    text = text.replace("</i>", "")
    text = text.replace("  ", " ")
    text = text.replace("*", "")
    return text


def verify_webhook(crc_token, consumer_secret):
    try:
        consumer_secret_byte = bytes(consumer_secret, 'utf-8')
        crc_token_byte = bytes(crc_token, 'utf-8')
        sha256_hash_digest = hmac.new(
            consumer_secret_byte, msg=crc_token_byte, digestmod=hashlib.sha256).digest()

        # construct response data with base64 encoded hash
        response = {
            'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest).decode("utf-8")
        }

        # returns properly formatted json response
        # return json.dumps(response)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "Verify API : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})


def get_twitter_webhook_url(bot_id):
    return settings.EASYCHAT_HOST_URL + "/chat/webhook/twitter/?bot_id={bot_id}".format(bot_id=bot_id)


def register_twitter_webhook(twitter_channel_detail_obj):
    '''
    API Reference:
            https://developer.twitter.com/en/docs/twitter-api/premium/account-activity-api/api-reference/aaa-premium#post-account-activity-all-env-name-subscriptions
    '''

    logger.info("\nIN register_twitter_webhook", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    REGISTER_URL = "https://api.twitter.com/1.1/account_activity/all/{twitter_dev_env_label}/webhooks.json?url={twitter_webhook_url}"
    response_message = "Webhook Register Failed"

    try:
        response = webhook_request_oauth(
            REGISTER_URL, twitter_channel_detail_obj, "POST", {})

        response_json = response.json()

        if response.status_code == 200:
            twitter_webhook_id = response_json["id"]
            twitter_channel_detail_obj.twitter_webhook_id = twitter_webhook_id
            twitter_channel_detail_obj.save()
            response_message = "Webhook Register Success"

            subscribe_twitter_webhook(twitter_channel_detail_obj)
        else:
            response_message = response_json["errors"][0]["message"]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "register_twitter_webhook : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    return response_message


def subscribe_twitter_webhook(twitter_channel_detail_obj):
    logger.info("\nIN subscribe_twitter_webhook", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    SUBSCRIBE_URL = "https://api.twitter.com/1.1/account_activity/all/{twitter_dev_env_label}/subscriptions.json"

    try:
        webhook_request_oauth(
            SUBSCRIBE_URL, twitter_channel_detail_obj, "POST", {})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "subscribe_twitter_webhook : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})


def delete_twitter_webhook(twitter_channel_detail_obj):
    logger.info("\nIN delete_twitter_webhook", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    DELETE_URL = "https://api.twitter.com/1.1/account_activity/all/{twitter_dev_env_label}/webhooks/{twitter_webhook_id}.json"
    response_message = "Webhook Delete Failed"

    try:
        response = webhook_request_oauth(
            DELETE_URL, twitter_channel_detail_obj, "DELETE", {})

        if response.status_code == 204:
            twitter_channel_detail_obj.twitter_webhook_id = ""
            twitter_channel_detail_obj.save()
            response_message = "Webhook Delete Success"
        else:
            response_json = response.json()
            response_message = response_json["errors"][0]["message"]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "delete_twitter_webhook : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    return response_message


def twitter_webhook_all_info(twitter_channel_detail_obj):
    logger.info("\nIN twitter_webhook_all_info", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    WEBHOOK_INFO_URL = "https://api.twitter.com/1.1/account_activity/all/webhooks.json"

    try:
        response = webhook_request_bearer_auth(
            WEBHOOK_INFO_URL, twitter_channel_detail_obj)

        response_json = response.json()

        if response.status_code == 200:
            twitter_webhook_id = response_json[0]["id"]
            twitter_channel_detail_obj.twitter_webhook_id = twitter_webhook_id
            twitter_channel_detail_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "twitter_webhook_all_info : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})


def twitter_webhook_configs(twitter_channel_detail_obj):
    logger.info("\nIN twitter_webhook_configs", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    WEBHOOK_CONFIG_URL = "https://api.twitter.com/1.1/account_activity/all/{twitter_dev_env_label}/webhooks.json"

    try:
        response = webhook_request_bearer_auth(
            WEBHOOK_CONFIG_URL, twitter_channel_detail_obj)

        response_json = response.json()

        if response.status_code == 200:
            twitter_webhook_id = response_json[0]["id"]
            twitter_channel_detail_obj.twitter_webhook_id = twitter_webhook_id
            twitter_channel_detail_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "twitter_webhook_configs : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})


def count_subscription(twitter_channel_detail_obj):
    logger.info("\nIN count_subscription", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    COUND_SUBSCRIPTION_URL = "https://api.twitter.com/1.1/account_activity/all/subscriptions/count.json"

    try:
        webhook_request_bearer_auth(
            COUND_SUBSCRIPTION_URL, twitter_channel_detail_obj)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "count_subscription : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})


def send_twitter_message(twitter_channel_detail_obj, recipient_id, message_data, recommendation_options=None, buttons=None, media_id=None):
    '''
    API Reference:
            https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/new-event
    '''

    logger.info("\nIN send_twitter_message", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    SEND_MESSAGE_URL = "https://api.twitter.com/1.1/direct_messages/events/new.json"

    try:
        data = {
            "event": {
                "type": "message_create",
                "message_create": {
                    "target": {
                        "recipient_id": recipient_id
                    },
                    "message_data": {
                        "text": message_data,
                    }
                }
            }
        }

        if recommendation_options and isinstance(recommendation_options, list) and len(recommendation_options) > 0:
            recommendation_options = recommendation_options[:20]
            data["event"]["message_create"]["message_data"]["quick_reply"] = {
                "type": "options", "options": recommendation_options}

        if buttons and isinstance(buttons, list) and len(buttons) > 0:
            buttons = buttons[:3]
            data["event"]["message_create"]["message_data"]["ctas"] = buttons

        if media_id:
            data["event"]["message_create"]["message_data"]["attachment"] = {
                "media": {
                    "id": media_id
                },
                "type": "media"
            }

        webhook_request_oauth(
            SEND_MESSAGE_URL, twitter_channel_detail_obj, "POST", data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "send_twitter_message : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})


class DMAttachment(object):

    MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'

    def upload_init(self):
        '''
        Initializes Upload
        '''

        logger.info("\nINIT", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        request_data = {
            'command': 'INIT',
            'media_type': self.mime_type,
            'total_bytes': self.total_bytes,
            'media_category': 'dm_image'
        }

        req = requests.post(url=DMAttachment.MEDIA_ENDPOINT_URL,
                            data=request_data, auth=self.oauth)
        media_id = req.json()['media_id']

        self.media_id = media_id

        logger.info("\nMedia ID: {media_id}".format(
            media_id=str(media_id)
        ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    def upload_append(self):
        '''
        Uploads media in chunks and appends to chunks uploaded
        '''
        segment_id = 0
        bytes_sent = 0
        CHUNK_SIZE = 4 * 1024 * 1024

        while bytes_sent < self.total_bytes:
            chunk = self.decoded_image_data[CHUNK_SIZE *
                                            segment_id:CHUNK_SIZE * (segment_id + 1)]

            logger.info("\nAPPEND", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

            request_data = {
                'command': 'APPEND',
                'media_id': self.media_id,
                'segment_index': segment_id
            }

            files = {
                'media': chunk
            }

            req = requests.post(url=DMAttachment.MEDIA_ENDPOINT_URL,
                                data=request_data, files=files, auth=self.oauth)

            if req.status_code < 200 or req.status_code > 299:

                logger.info("req.status_code {status_code}".format(
                    status_code=req.status_code
                ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

                logger.info("req.text {req_text}".format(
                    req_text=req.text
                ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

                sys.exit(0)

            segment_id = segment_id + 1
            bytes_sent = min(CHUNK_SIZE * segment_id, len(chunk))

            logger.info("\n{bytes_sent} of {total_bytes} bytes uploaded".format(
                bytes_sent=str(bytes_sent), total_bytes=str(self.total_bytes)
            ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        logger.info("\nUpload chunks complete.", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    def upload_finalize(self):
        '''
        Finalizes uploads and starts video processing
        '''

        logger.info("\nFINALIZE", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        request_data = {
            'command': 'FINALIZE',
            'media_id': self.media_id
        }

        req = requests.post(url=DMAttachment.MEDIA_ENDPOINT_URL,
                            data=request_data, auth=self.oauth)

        logger.info("upload_finalize req.status_code {status_code}".format(
            status_code=req.status_code
        ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        logger.info("upload_finalize req_json: {req_json}".format(
            req_json=json.dumps(req.json(), indent=4)
        ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        self.processing_info = req.json().get('processing_info', None)
        self.media_id = req.json().get('media_id', None)

        self.check_status()

    def check_status(self):
        '''
        Checks video processing status
        '''
        if self.processing_info is None:
            return

        state = self.processing_info['state']

        logger.info("Media processing status is {state}".format(
            state=state
        ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        if state == u'succeeded':
            return

        if state == u'failed':
            sys.exit(0)

        check_after_secs = self.processing_info['check_after_secs']

        logger.info("Checking after {check_after_secs} seconds".format(
            check_after_secs=check_after_secs
        ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        time.sleep(check_after_secs)

        logger.info("\nSTATUS", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        request_params = {
            'command': 'STATUS',
            'media_id': self.media_id
        }

        req = requests.get(url=DMAttachment.MEDIA_ENDPOINT_URL,
                           params=request_params, auth=self.oauth)

        self.processing_info = req.json().get('processing_info', None)
        self.check_status()

    def send_attachment(self, twitter_channel_detail_obj, recipient_id, media_file_path):

        logger.info("\nIN send_attachment", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        self.media_file_path = media_file_path

        media_download_response = requests.get(
            media_file_path, allow_redirects=True)

        decoded_image_data = media_download_response.content

        mime_type = magic.from_buffer(decoded_image_data, mime=True)

        self.decoded_image_data = decoded_image_data
        self.total_bytes = len(decoded_image_data)
        self.media_id = None
        self.mime_type = mime_type
        self.processing_info = None

        logger.info("\n\nMime Type {mime_type}\n\n".format(
            mime_type=self.mime_type
        ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        twitter_api_key = twitter_channel_detail_obj.twitter_api_key
        twitter_key_api_secret = twitter_channel_detail_obj.twitter_key_api_secret
        twitter_access_token = twitter_channel_detail_obj.twitter_access_token
        twitter_access_token_secret = twitter_channel_detail_obj.twitter_access_token_secret

        self.oauth = OAuth1(twitter_api_key,
                            client_secret=twitter_key_api_secret,
                            resource_owner_key=twitter_access_token,
                            resource_owner_secret=twitter_access_token_secret)

        self.upload_init()
        self.upload_append()
        self.upload_finalize()

        send_twitter_message(twitter_channel_detail_obj,
                             recipient_id, "", media_id=self.media_id)


def retrieving_twitter_media(twitter_channel_detail_obj, url):
    logger.info("\nIN retrieving_twitter_media", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    try:
        response = webhook_request_oauth(
            url, twitter_channel_detail_obj, "GET", {})
        response_content = response.content

        logger.info("\nresponse_content {response_content}\n".format(response_content=response_content), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})
        return response_content
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            "retrieving_twitter_media : " + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})


def save_and_get_twitter_file_src(twitter_channel_detail_obj, url):
    logger.info("\nIN save_and_get_twitter_file_src", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    try:
        file_content = retrieving_twitter_media(
            twitter_channel_detail_obj, url)

        file_name = str(uuid4().hex)
        file_directory = "files/twitter-attachment/"

        file_ext = file_validation_obj.get_file_extension_from_content(
            file_content)
        file_ext = file_ext.split(".")[-1]

        file_name = file_name + "." + file_ext

        allowed_file_extensions = ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "BMP", "GIF", "TIFF", "EXIF", "JFIF", "WEBM", "MPG", "MP2",
                                   "MPEG", "MPE", "MPV", "OGG", "MP4", "M4P", "M4V", "AVI", "WMV", "MOV", "QT", "FLV", "SWF", "AVCHD", "PDF", "DOCS", "DOCX", "DOC"]

        logger.info("\nfile_ext {file_ext}".format(
            file_ext=file_ext
        ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        if file_ext.upper() not in allowed_file_extensions:
            return "FORMAT_NOT_SUPPORTED"

        full_path = file_directory + file_name

        local_file = open(full_path, 'wb')

        local_file.write(file_content)
        local_file.close()

        full_path = "/files/twitter-attachment/" + file_name

        return full_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_and_get_twitter_file_src %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})
        return ""


def save_and_get_twitter_gif_src(twitter_channel_detail_obj, url):
    logger.info("\nIN save_and_get_twitter_gif_src", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    try:
        response = requests.get(url)

        file_content = response.content

        file_name = str(uuid4().hex)
        file_directory = "files/twitter-attachment/"

        file_ext = file_validation_obj.get_file_extension_from_content(
            file_content)
        file_ext = file_ext.split(".")[-1]

        file_name = file_name + "." + file_ext

        logger.info("\nfile_ext {file_ext}".format(
            file_ext=file_ext
        ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        full_path = file_directory + file_name

        local_file = open(full_path, 'wb')

        local_file.write(file_content)
        local_file.close()

        full_path = "/files/twitter-attachment/" + file_name

        logger.info("\nfull_path {full_path}".format(
            full_path=full_path
        ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        return full_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_and_get_twitter_gif_src %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})
        return ""


def replace_url_vars(url, twitter_channel_detail_obj):

    twitter_api_key = twitter_channel_detail_obj.twitter_api_key
    twitter_key_api_secret = twitter_channel_detail_obj.twitter_key_api_secret
    twitter_access_token = twitter_channel_detail_obj.twitter_access_token
    twitter_access_token_secret = twitter_channel_detail_obj.twitter_access_token_secret
    twitter_dev_env_label = twitter_channel_detail_obj.twitter_dev_env_label
    twitter_webhook_id = twitter_channel_detail_obj.twitter_webhook_id

    bot_obj = twitter_channel_detail_obj.bot
    twitter_webhook_url = get_twitter_webhook_url(bot_obj.pk)
    twitter_webhook_url = urllib.parse.quote_plus(twitter_webhook_url)

    url = url.format(
        twitter_api_key=twitter_api_key,
        twitter_key_api_secret=twitter_key_api_secret,
        twitter_access_token=twitter_access_token,
        twitter_access_token_secret=twitter_access_token_secret,
        twitter_dev_env_label=twitter_dev_env_label,
        twitter_webhook_id=twitter_webhook_id,
        twitter_webhook_url=twitter_webhook_url,
    )

    return url


def webhook_request_bearer_auth(url, twitter_channel_detail_obj):
    logger.info("\nIN webhook_request_bearer_auth", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    twitter_bearer_token = twitter_channel_detail_obj.twitter_bearer_token

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer {twitter_bearer_token}".format(
        twitter_bearer_token=twitter_bearer_token
    )

    url = replace_url_vars(url, twitter_channel_detail_obj)

    logger.info("\nurl: {url}".format(
        url=url
    ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    response = requests.get(url, headers=headers)

    logger.info("\nresponse_status_code: {response_status_code}".format(
        response_status_code=response.status_code
    ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    logger.info("\n\nresponse_text: {response_text}".format(
        response_text=response.text
    ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    return response


def webhook_request_oauth(url, twitter_channel_detail_obj, request_type, data):
    logger.info("\nIN webhook_request_oauth", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    url = replace_url_vars(url, twitter_channel_detail_obj)

    logger.info("\n\nurl: {url}\n".format(
        url=url
    ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    logger.info("\n\ndata: {data}\n".format(
        data=json.dumps(data, indent=4)
    ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    twitter_api_key = twitter_channel_detail_obj.twitter_api_key
    twitter_key_api_secret = twitter_channel_detail_obj.twitter_key_api_secret
    twitter_access_token = twitter_channel_detail_obj.twitter_access_token
    twitter_access_token_secret = twitter_channel_detail_obj.twitter_access_token_secret

    auth = OAuth1(twitter_api_key, twitter_key_api_secret,
                  twitter_access_token, twitter_access_token_secret)

    if request_type == "POST":
        response = requests.post(url, auth=auth, data=json.dumps(data))
    elif request_type == "DELETE":
        response = requests.delete(url, auth=auth, data=json.dumps(data))
    elif request_type == "GET":
        response = requests.get(url, auth=auth, data=json.dumps(data))

    logger.info("\n\nresponse_status_code: {response_status_code}\n".format(
        response_status_code=response.status_code
    ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    logger.info("\n\nresponse_headers: {response_headers}\n".format(
        response_headers=str(response.headers)
    ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    try:
        logger.info("\n\nresponse_json: {response_json}\n".format(
            response_json=json.dumps(response.json(), indent=4)
        ), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})
    except Exception:
        pass

    return response


def create_recommendation_option_object(label, metadata):

    label = remove_tags(str(label)).replace(
        "SBI", "").replace("Plan", "").strip()
    metadata = remove_tags(str(metadata))

    return {
        "label": label,
        "metadata": metadata
    }


def process_recommendations_for_quick_reply(recommendations):
    logger.info("\nIN process_recommendations_for_quick_reply", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    try:
        processed_list = []

        for recommendation in recommendations:

            if isinstance(recommendation, str) or isinstance(recommendation, int):

                label = str(recommendation)
                metadata = str(recommendation)

            elif isinstance(recommendation, dict) and "name" in recommendation:

                label = str(recommendation["name"])
                metadata = str(recommendation["name"])

            elif isinstance(recommendation, dict):

                label = recommendation["display"]
                metadata = recommendation["value"]

            processed_list.append(
                create_recommendation_option_object(label, metadata))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error process_recommendations_for_quick_reply %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        processed_list = []

    logger.info("\nIN processed_list {processed_list}".format(processed_list=str(processed_list)), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    return processed_list


def create_button_object(label, url):

    return {
        "type": "web_url",
        "label": label,
        "url": url
    }


def process_card_for_twitter_button(cards):
    logger.info("\nIN process_card_for_twitter_button", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    try:
        processed_list = []

        for card in cards:
            title = card["title"]
            # content = card["content"]
            link = card["link"]
            if not link:
                continue
            # img_url = card["img_url"]

            processed_list.append(create_button_object(title, link))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error process_card_for_twitter_button %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

        processed_list = []

    logger.info("\nIN processed_list {processed_list}".format(processed_list=str(processed_list)), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'Twitter', 'bot_id': 'None'})

    return processed_list


def send_twitter_livechat_agent_response(message, customer_obj, session_id, attached_file_src, data, twitter_channel_detail_obj, Profile):
    try:

        user_obj = Profile.objects.get(livechat_session_id=session_id)

        if user_obj.livechat_connected == True:

            recipient_id = str(user_obj.user_id).replace("twitter_user_", "")

            if attached_file_src != "":

                if "channel_file_url" in data:

                    attached_file_src = data["channel_file_url"]

                    try:
                        attached_file_src = settings.EASYCHAT_HOST_URL + attached_file_src

                        file_name = attached_file_src.split("/")[-1]

                        file_type = get_file_type(file_name)

                        if file_type == "invalid file format":
                            pass
                        elif file_type == "image":
                            dm_attachment = DMAttachment()
                            dm_attachment.send_attachment(
                                twitter_channel_detail_obj, recipient_id, attached_file_src)
                        else:
                            send_twitter_message(
                                twitter_channel_detail_obj, recipient_id, attached_file_src)

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("send_twitter_livechat_agent_response: %s at %s",
                                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            if message != "":
                send_twitter_message(
                    twitter_channel_detail_obj, recipient_id, message)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_twitter_livechat_agent_response: %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def get_file_type(file_name):
    try:
        file_ext = file_name.split(".")[-1]

        if file_ext.lower() in ["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]:
            return "image"

        elif file_ext.upper() in ["WEBM", "MPG", "MP2", "MPEG", "MPE", "MPV", "OGG", "MP4", "M4P", "M4V", "AVI", "WMV", "MOV", "QT", "FLV", "SWF", "AVCHD"]:
            return "video"

        elif file_ext.lower() in ["pdf", "docs", "docx", "doc", "PDF", "txt", "TXT"]:
            return "file"
        else:
            return "invalid file format"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return "invalid file format"
