import os
import sys
import json
import logging
from os import path
import urllib.parse

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from LiveChatApp.utils_translation import get_translated_message_history, get_translated_text

from LiveChatApp.models import *
from LiveChatApp.utils_custom_encryption import *


# Logger
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class GetTranslatedMessageHistoryAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            session_id = data['session_id']
            selected_language = data['selected_language']
            
            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)

            response["message_history"] = get_translated_message_history(customer_obj, selected_language, LiveChatMISDashboard, LiveChatTranslationCache)
            response["status"] = 200
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetTranslatedMessageHistoryAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetTranslatedMessageHistory = GetTranslatedMessageHistoryAPI.as_view()


class GetTranslatedMessageAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            text_message = data['text_message']
            selected_language = data['selected_language']

            response["translated_message"] = get_translated_text(text_message, selected_language, LiveChatTranslationCache)
            response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetTranslatedMessageAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetTranslatedMessage = GetTranslatedMessageAPI.as_view()
