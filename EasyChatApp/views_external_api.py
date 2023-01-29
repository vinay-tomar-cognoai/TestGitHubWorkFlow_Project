# Django REST framework
from rest_framework.response import Response
# from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect

"""For user authentication"""
from django.contrib.auth import authenticate
from EasyChatApp.models import *
from EasyChatApp.utils_validation import EasyChatInputValidation

import json
from django.conf import settings
from django.utils import timezone

from os import path

import pytz
import sys
from datetime import datetime, date, timedelta

from EasyChatApp.utils_external_apis import *

# Logger
import logging
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class GetAuthTokenAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = "Internal Server Error"
        external_api_audit_obj = None
        try:
            data = request.data
            tz = pytz.timezone(settings.TIME_ZONE)

            external_api_audit_obj = get_external_api_audit_obj(request, '1')

            response['request_id'] = str(external_api_audit_obj.request_id)
            response['timestamp'] = str(timezone.now().astimezone(tz))

            if 'username' not in data:
                response = get_external_api_response(
                    400, 'Invalid Username!', response, external_api_audit_obj)
                return Response(data=response, status=400)

            if 'password' not in data:
                response = get_external_api_response(
                    400, 'Invalid Password!', response, external_api_audit_obj)
                return Response(data=response, status=400)

            validation_obj = EasyChatInputValidation()
            username = validation_obj.remo_html_from_string(data['username'])
            password = data['password']
            user = authenticate(username=username, password=password)
            if user is None:
                response = get_external_api_response(
                    401, 'Invalid Username or Password!', response, external_api_audit_obj)
                return Response(data=response, status=401)

            existing_token_objs = EasyChatAuthToken.objects.filter(user=user)
            current_time = datetime.now() - timedelta(minutes=1)

            past_minute_objs = existing_token_objs.filter(
                user=user, created_datetime__gte=current_time)

            if past_minute_objs.count() >= EXTERNAL_API_TOKEN_CREATION_LIMIT_PER_MINUTE:
                response = get_external_api_response(
                    429, 'Rate Limit Exceeded!', response, external_api_audit_obj)
                return Response(data=response, status=429)

            existing_token_objs.update(is_expired=True)

            auth_token_obj = EasyChatAuthToken.objects.create(user=user)
            external_api_audit_obj.token = auth_token_obj

            response['auth_token'] = str(auth_token_obj.token)
            response['message'] = "Success"
            response['status'] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetAuthTokenAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        if external_api_audit_obj:
            external_api_audit_obj.response_data = json.dumps(response)
            external_api_audit_obj.status_code = response['status']
            external_api_audit_obj.save()
        return Response(data=response, status=response['status'])


GetAuthToken = GetAuthTokenAPI.as_view()


class GetAnalyticsExternalAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = "Internal Server Error"
        external_api_audit_obj = None
        try:
            try:
                data = request.data
            except:
                response['status'] = 400
                response['status_message'] = "Malformed request body."
                return Response(data=response, status=response['status'])
            tz = pytz.timezone(settings.TIME_ZONE)

            external_api_audit_obj = get_external_api_audit_obj(request, '2')

            response['request_id'] = str(external_api_audit_obj.request_id)
            response['timestamp'] = str(timezone.now().astimezone(tz))

            bot_obj, status_code, response_message = check_easychat_external_data_is_valid(
                data, external_api_audit_obj)

            if status_code != 200:
                response = get_external_api_response(
                    status_code, response_message, response, external_api_audit_obj)
                return Response(data=response, status=status_code)

            response["bot_id"] = bot_obj.pk

            analytics_types_map = {
                'basic_analytics': get_basic_analytics_external,
                'csat_analytics': get_csat_analytics_external,
                'message_analytics': get_message_analytics_external,
                'user_analytics': get_user_analytics_external,
                'session_analytics': get_session_analytics_external,
                'channel_analytics': get_channel_analytics_external,
                'frequent_intents': get_frequent_intents_external,
                'unanswered_questions': get_unanswered_queries_external,
                'form_assist_analytics': get_form_assist_intent_data_external,
                'intuitive_questions': get_intuitive_questions_data_external,
                'frequent_questions_category_wise': get_most_frequent_questions_category_wise_external,
                'word_cloud': get_word_cloud_data_external,
                'user_nudge': get_user_nudge_analytics_external,
                'livechat_analytics': get_livechat_conversion_analytics_external,
                'intent_analytics': get_conversion_intent_analytics_external,
                'traffic_analytics': get_bot_hit_list_data_external,
                'welcomebanner_clicks': get_welcome_banner_clicks_data_external,
                'customer_dropoff': get_conversion_drop_off_data_external,
                'flow_analytics': get_conversion_flow_analytics_data_external,
                'node_analytics': get_conversion_node_analytics_data_external,
                'device_specific_analytics': get_device_specific_analytics_external,
                'hour_wise_analytics': get_hour_wise_analytics_external,
                'catalogue_conversion_analytics': get_whatsapp_catalogue_analytics_external,
                'catalogue_combined_analytics': get_combined_catalogue_analytics_list_external,
                'whatsapp_block_spam_analytics': get_whatsapp_block_analytics_external,
            }

            if 'analytics_type' not in data or data['analytics_type'].strip().lower() not in analytics_types_map:
                response = get_external_api_response(
                    400, 'Invalid Analytics type!', response, external_api_audit_obj)
                return Response(data=response, status=400)

            analytics_type = data['analytics_type'].strip().lower()
            response['analytics_type'] = analytics_type

            filter_params = {}
            if 'filter_params' in data:
                filter_params = data['filter_params']
                if not isinstance(filter_params, dict):
                    filter_params = json.loads(filter_params)

            response = get_analytics_data_external(
                response, analytics_types_map, analytics_type, bot_obj, filter_params)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetAnalyticsExternalAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        if external_api_audit_obj:
            external_api_audit_obj.response_data = json.dumps(response)
            external_api_audit_obj.status_code = response['status']
            external_api_audit_obj.save()

        return Response(data=response, status=response['status'])


GetAnalyticsExternal = GetAnalyticsExternalAPI.as_view()


def EasyChatAPIDocumentation(request):
    try:
        selected_bot_obj = None
        if "bot_id" in request.GET:
            selected_bot_id = request.GET["bot_id"]
            selected_bot_obj = Bot.objects.filter(id=int(selected_bot_id), is_deleted=False).first()
        else:
            selected_bot_obj = Bot.objects.filter(users__in=[request.user], is_deleted=False).first()
        
        if not selected_bot_obj:
            return render(request, 'EasyChatApp/unauthorized.html')
        
        return render(request, 'EasyChatApp/easychat_api_documentation.html', {
            "selected_bot_obj": selected_bot_obj,
        })
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EasyChatAPIDocumentation ! %s %s",
                     str(e), str(exc_tb.tb_lineno))
        return HttpResponseRedirect("/chat/login/")
