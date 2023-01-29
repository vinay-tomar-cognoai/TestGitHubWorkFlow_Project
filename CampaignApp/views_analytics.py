from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect

# Django REST framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.decorators import authentication_classes

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.sessions.models import Session

"""For user authentication"""
from django.contrib.auth import logout

from CampaignApp.utils import *
from CampaignApp.models import *
from EasyChatApp.models import *
from CampaignApp.constants import *

from CampaignApp.views_api_integration import *
from CampaignApp.views_tag_audience import *
from CampaignApp.views_campaign_template import *

import json
import time
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from django.utils import timezone

from django.db.models import Q, Count, Max
import operator
from os import path


import pytz
import uuid
import sys
from datetime import datetime, date, timedelta
import threading

from django.db.models import Sum

# Logger
import logging
logger = logging.getLogger(__name__)

validation_obj = CampaignInputValidation()


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


"""

GetCampaignBasicAnalyticsAPI() : return total campaigns, average open rate and total launched campaigns

"""


class GetCampaignBasicAnalyticsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_id = data["bot_id"]
            selected_date_filter = data['selected_date_filter']
            selected_campaigns = data['selected_campaigns']
            channel_list = data.get('channel_list', [])

            bot_obj = Bot.objects.get(pk=int(bot_id))
            total_campaign_objs_count = Campaign.objects.filter(bot=bot_obj, is_deleted=False, status__in=[CAMPAIGN_COMPLETED, CAMPAIGN_IN_PROGRESS, CAMPAIGN_PARTIALLY_COMPLETED, CAMPAIGN_FAILED, CAMPAIGN_PROCESSED, CAMPAIGN_ONGOING]).count()

            if request.user not in bot_obj.users.all():
                response[
                    'message'] = 'You are not authorised to perform this request.'
            else:
                if selected_campaigns and len(selected_campaigns) < total_campaign_objs_count:
                    campaign_objs = Campaign.objects.filter(
                        pk__in=selected_campaigns)
                else:
                    if selected_date_filter == '1':
                        start_date = datetime.now() - timedelta(days=7)
                        end_date = datetime.now()

                    elif selected_date_filter == '2':
                        start_date = datetime.now() - timedelta(days=30)
                        end_date = datetime.now()

                    elif selected_date_filter == '3':
                        start_date = datetime.now() - timedelta(days=90)
                        end_date = datetime.now()

                    elif selected_date_filter == '4':
                        start_date = bot_obj.created_datetime
                        end_date = datetime.now()

                    elif selected_date_filter == '5':
                        start_date = data['start_date']
                        end_date = data['end_date']

                        start_date, end_date, error_message = validation_obj.get_start_and_end_date_time(
                            start_date, end_date)
                        if error_message:
                            response["message"] = error_message
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)

                    campaign_objs = Campaign.objects.filter(
                        bot=bot_obj, is_deleted=False, start_datetime__date__gte=start_date, start_datetime__date__lte=end_date)

                if channel_list:
                    channel_objs = CampaignChannel.objects.filter(value__in=channel_list)                      
                else:
                    channel_objs = CampaignChannel.objects.filter(is_deleted=False)

                campaign_objs = campaign_objs.filter(channel__in=channel_objs)

                campaign_objs_whatsapp = campaign_objs.filter(channel__value="whatsapp")
                campaign_objs_voicebot = campaign_objs.filter(channel__value="voicebot")
                campaign_objs_rcs = campaign_objs.filter(channel__value="rcs")

                total_campaigns = campaign_objs.exclude(
                    status__in=[CAMPAIGN_SCHEDULED, CAMPAIGN_SCHEDULE_COMPLETED]).count()

                total_launched_campaigns = campaign_objs.exclude(
                    status__in=[CAMPAIGN_DRAFT, CAMPAIGN_SCHEDULED, CAMPAIGN_SCHEDULE_COMPLETED]).count()
                total_failed_campaigns = campaign_objs.filter(
                    status=CAMPAIGN_FAILED).count()
                total_completed_campaigns = campaign_objs.filter(
                    status__in=[CAMPAIGN_COMPLETED, CAMPAIGN_PARTIALLY_COMPLETED]).count()
                # Ongoing and scheduled campaigns that have the number of messages 1 or more are also to be considered as completed

                campaign_analytics_objs = CampaignAnalytics.objects.filter(
                    campaign__in=campaign_objs_whatsapp)

                campaigns_completed_with_partial_results_whatsapp = campaign_analytics_objs.filter(
                    campaign__status__in=[CAMPAIGN_ONGOING], message_sent__gt=0).count()

                campaign_voice_analytics_objs = CampaignVoiceBotAnalytics.objects.filter(
                    campaign__in=campaign_objs_voicebot)

                campaigns_completed_with_partial_results_voicebot = campaign_voice_analytics_objs.filter(
                    campaign__status=CAMPAIGN_SCHEDULED, call_completed__gt=0).count()

                campaign_rcs_analytics_objs = CampaignRCSDetailedAnalytics.objects.filter(
                    campaign__in=campaign_objs_rcs)
                
                campaigns_completed_with_partial_results_rcs = campaign_rcs_analytics_objs.filter(
                    campaign__status=[CAMPAIGN_SCHEDULED], sent__gt=0).count()

                total_completed_campaigns += campaigns_completed_with_partial_results_whatsapp + campaigns_completed_with_partial_results_voicebot + campaigns_completed_with_partial_results_rcs

                whatsapp_analytics = get_campaign_whatsapp_analytics(campaign_analytics_objs)

                total_calls_created, total_calls_scheduled, total_calls_initiated, total_calls_in_progress, total_calls_retry, total_calls_failed, total_calls_completed = get_campaign_voice_analytics(campaign_voice_analytics_objs)

                submitted, sent, delivered, read, failed, replied = get_campaign_rcs_analytics(campaign_rcs_analytics_objs)

                average_open_rate = 0 if total_completed_campaigns == 0 else (
                    total_completed_campaigns * 100) / (total_completed_campaigns + total_failed_campaigns)

                response['status'] = 200
                response['message'] = 'success'
                response['total_campaigns'] = total_campaigns
                response['total_launched_campaigns'] = total_launched_campaigns
                response['avg_open_rate'] = average_open_rate
                response['total_messages_sent'] = whatsapp_analytics.get('total_messages_sent', 'NA')
                response['total_messages_read'] = whatsapp_analytics.get('total_messages_read', 'NA')
                response['total_messages_delivered'] = whatsapp_analytics.get('total_messages_delivered', 'NA')
                response[
                    'total_messages_unsuccessful'] = whatsapp_analytics.get('total_messages_unsuccessful', 'NA')
                response[
                    'total_messages_processed'] = whatsapp_analytics.get('total_messages_processed', 'NA')
                response['total_messages_replied'] = whatsapp_analytics.get('total_messages_replied', 'NA')
                response['test_message_sent'] = whatsapp_analytics.get('test_message_sent', 'NA')
                response['test_message_unsuccessful'] = whatsapp_analytics.get('test_message_unsuccessful', 'NA')
                response['total_calls_created'] = total_calls_created
                response['total_calls_scheduled'] = total_calls_scheduled
                response['total_calls_initiated'] = total_calls_initiated
                response['total_calls_in_progress'] = total_calls_in_progress
                response['total_calls_retry'] = total_calls_retry
                response['total_calls_failed'] = total_calls_failed
                response['total_calls_completed'] = total_calls_completed

                response["total_rcs_messages_submitted"] = submitted
                response["total_rcs_messages_sent"] = sent
                response["total_rcs_messages_delivered"] = delivered
                response["total_rcs_messages_read"] = read
                response["total_rcs_messages_failed"] = failed
                response["total_rcs_messages_replied"] = replied

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetCampaignBasicAnalyticsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCampaignBasicAnalytics = GetCampaignBasicAnalyticsAPI.as_view()


class GetCampaignDetailedAnalyticsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_id = data["bot_id"]
            selected_date_filter = data['selected_date_filter']
            selected_campaigns = data['selected_campaigns']
            channel_list = data['channel_list']

            bot_obj = Bot.objects.get(pk=int(bot_id))
            total_campaign_objs_count = Campaign.objects.filter(bot=bot_obj, is_deleted=False, status__in=[CAMPAIGN_COMPLETED, CAMPAIGN_IN_PROGRESS, CAMPAIGN_PARTIALLY_COMPLETED, CAMPAIGN_FAILED, CAMPAIGN_PROCESSED, CAMPAIGN_ONGOING]).count()

            if request.user not in bot_obj.users.all():
                response[
                    'message'] = 'You are not authorised to perform this request.'
            else:
                if selected_campaigns and len(selected_campaigns) < total_campaign_objs_count:
                    campaign_objs = Campaign.objects.filter(
                        pk__in=selected_campaigns)

                    est = pytz.timezone(settings.TIME_ZONE)
                    start_date = bot_obj.created_datetime.astimezone(est)
                    end_date = datetime.now().astimezone(est)
                else:
                    if selected_date_filter == '1':
                        start_date = datetime.now() - timedelta(days=7)
                        end_date = datetime.now()

                    elif selected_date_filter == '2':
                        start_date = datetime.now() - timedelta(days=30)
                        end_date = datetime.now()

                    elif selected_date_filter == '3':
                        start_date = datetime.now() - timedelta(days=90)
                        end_date = datetime.now()

                    elif selected_date_filter == '4':
                        est = pytz.timezone(settings.TIME_ZONE)
                        start_date = bot_obj.created_datetime.astimezone(est)
                        end_date = datetime.now().astimezone(est)

                    elif selected_date_filter == '5':
                        start_date = data['start_date']
                        end_date = data['end_date']

                        start_date, end_date, error_message = validation_obj.get_start_and_end_date_time(
                            start_date, end_date)
                        if error_message:
                            response["message"] = error_message
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)

                    campaign_objs = Campaign.objects.filter(
                        bot=bot_obj, is_deleted=False, start_datetime__date__gte=start_date, start_datetime__date__lte=end_date)

                if channel_list:
                    channel_objs = CampaignChannel.objects.filter(value__in=channel_list)
                else:
                    channel_objs = CampaignChannel.objects.filter(is_deleted=False)

                # total run campaigns
                campaign_objs = campaign_objs.filter(status__in=[CAMPAIGN_COMPLETED, CAMPAIGN_IN_PROGRESS, CAMPAIGN_PARTIALLY_COMPLETED, CAMPAIGN_FAILED, CAMPAIGN_PROCESSED, CAMPAIGN_ONGOING])

                response['labels'] = []
                response['whatsapp'] = {
                    'label': 'Whatsapp Business',
                    'data': [],
                }

                response['voicebot'] = {
                    'label': 'Voice Bot',
                    'data': [],
                }

                response['rcs'] = {
                    'label': 'Google RCS',
                    'data': [],
                }

                temp_date = start_date
                while temp_date <= end_date:
                    response['labels'].append(temp_date.strftime('%d %b %y'))

                    for channel in channel_objs:
                        launched_campaigns = campaign_objs.filter(
                            start_datetime__date=temp_date, channel=channel).count()

                        launched_campaigns = 0 if launched_campaigns == None else launched_campaigns
                        response[channel.value]['data'].append(
                            launched_campaigns)

                    temp_date = temp_date + timedelta(days=1)

                response['status'] = 200
                response['message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetCampaignDetailedAnalyticsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCampaignDetailedAnalytics = GetCampaignDetailedAnalyticsAPI.as_view()


class GetCampaignSuccessRatioAnalyticsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_id = data["bot_id"]
            selected_date_filter = data['selected_date_filter']
            selected_campaigns = data['selected_campaigns']
            channel_list = data['channel_list']

            bot_obj = Bot.objects.get(pk=int(bot_id))
            total_campaign_objs_count = Campaign.objects.filter(bot=bot_obj, is_deleted=False, status__in=[CAMPAIGN_COMPLETED, CAMPAIGN_IN_PROGRESS, CAMPAIGN_PARTIALLY_COMPLETED, CAMPAIGN_FAILED, CAMPAIGN_ONGOING, CAMPAIGN_PROCESSED]).count()

            if request.user not in bot_obj.users.all():
                response[
                    'message'] = 'You are not authorised to perform this request.'
            else:
                if selected_campaigns and len(selected_campaigns) < total_campaign_objs_count:
                    campaign_objs = Campaign.objects.filter(
                        pk__in=selected_campaigns)

                    start_date = bot_obj.created_datetime
                    end_date = datetime.now()
                else:
                    if selected_date_filter == '1':
                        start_date = datetime.now() - timedelta(days=7)
                        end_date = datetime.now()

                    elif selected_date_filter == '2':
                        start_date = datetime.now() - timedelta(days=30)
                        end_date = datetime.now()

                    elif selected_date_filter == '3':
                        start_date = datetime.now() - timedelta(days=90)
                        end_date = datetime.now()

                    elif selected_date_filter == '4':
                        start_date = bot_obj.created_datetime
                        end_date = datetime.now()

                    elif selected_date_filter == '5':
                        start_date = data['start_date']
                        end_date = data['end_date']

                        start_date, end_date, error_message = validation_obj.get_start_and_end_date_time(
                            start_date, end_date)
                        if error_message:
                            response["message"] = error_message
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)

                    campaign_objs = Campaign.objects.filter(
                        bot=bot_obj, is_deleted=False, start_datetime__date__gte=start_date, start_datetime__date__lte=end_date)

                if channel_list:
                    channel_objs = CampaignChannel.objects.filter(value__in=channel_list)
                else:
                    channel_objs = CampaignChannel.objects.filter(is_deleted=False)

                campaign_objs = campaign_objs.filter(channel__in=channel_objs)

                sent_data = 0
                failed_data = 0
                # completed_data = 0

                if 'whatsapp' in channel_list:
                    campaign_analytics_objs = CampaignAnalytics.objects.filter(
                        campaign__in=campaign_objs)
                    total_messages_sent = campaign_analytics_objs.aggregate(Sum('message_sent'))[
                        'message_sent__sum']
                    total_messages_sent = 0 if total_messages_sent == None else total_messages_sent

                    total_messages_unsuccessful = campaign_analytics_objs.aggregate(
                        Sum('message_unsuccessful'))['message_unsuccessful__sum']
                    total_messages_unsuccessful = 0 if total_messages_unsuccessful == None else total_messages_unsuccessful

                    test_message_sent = campaign_analytics_objs.aggregate(
                        Sum('test_message_sent'))['test_message_sent__sum']
                    test_message_sent = 0 if test_message_sent == None else test_message_sent

                    test_message_unsuccessful = campaign_analytics_objs.aggregate(
                        Sum('test_message_unsuccessful'))['test_message_unsuccessful__sum']
                    test_message_unsuccessful = 0 if test_message_unsuccessful == None else test_message_unsuccessful

                    sent_data += total_messages_sent + test_message_sent
                    failed_data += total_messages_unsuccessful + test_message_unsuccessful
                    # completed_data += total_messages_delivered

                if 'voicebot' in channel_list:
                    campaign_voice_analytics_objs = CampaignVoiceBotAnalytics.objects.filter(
                        campaign__in=campaign_objs)
                    
                    total_calls_scheduled = campaign_voice_analytics_objs.aggregate(Sum('call_scheduled'))[
                        'call_scheduled__sum']
                    total_calls_scheduled = 0 if total_calls_scheduled == None else total_calls_scheduled

                    total_calls_completed = campaign_voice_analytics_objs.aggregate(Sum('call_completed'))[
                        'call_completed__sum']
                    total_calls_completed = 0 if total_calls_completed == None else total_calls_completed

                    sent_data += total_calls_completed
                    failed_data += total_calls_scheduled - total_calls_completed
                    # completed_data += total_calls_completed   

                if 'rcs' in channel_list:
                    campaign_rcs_analytics_objs = CampaignRCSDetailedAnalytics.objects.filter(
                        campaign__in=campaign_objs)
                    
                    sent_rcs = campaign_rcs_analytics_objs.aggregate(Sum('sent'))[
                        'sent__sum']
                    sent_rcs = 0 if sent_rcs == None else sent_rcs

                    failed_rcs = campaign_rcs_analytics_objs.aggregate(Sum('failed'))[
                        'failed__sum']
                    failed_rcs = 0 if failed_rcs == None else failed_rcs

                    sent_data += sent_rcs
                    failed_data += failed_rcs
                    # completed_data += delivered 

                response['status'] = 200
                response['message'] = 'success'
                response['sent_data'] = sent_data
                response['failed_data'] = failed_data
                # response['completed_data'] = completed_data

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetCampaignSuccessRatioAnalyticsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCampaignSuccessRatioAnalytics = GetCampaignSuccessRatioAnalyticsAPI.as_view()


class GetChannelCampaignStatsAnalyticsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_id = data["bot_id"]
            selected_date_filter = data['selected_date_filter']
            selected_campaigns = data['selected_campaigns']
            channel_list = data['channel_list']

            bot_obj = Bot.objects.get(pk=int(bot_id))
            total_campaign_objs_count = Campaign.objects.filter(bot=bot_obj, is_deleted=False, status__in=[CAMPAIGN_COMPLETED, CAMPAIGN_IN_PROGRESS, CAMPAIGN_PARTIALLY_COMPLETED, CAMPAIGN_FAILED, CAMPAIGN_PROCESSED, CAMPAIGN_ONGOING]).count()

            if request.user not in bot_obj.users.all():
                response[
                    'message'] = 'You are not authorised to perform this request.'
            else:
                if selected_campaigns and len(selected_campaigns) < total_campaign_objs_count:
                    campaign_objs = Campaign.objects.filter(
                        pk__in=selected_campaigns)

                    start_date = bot_obj.created_datetime
                    end_date = datetime.now()
                else:
                    if selected_date_filter == '1':
                        start_date = datetime.now() - timedelta(days=7)
                        end_date = datetime.now()

                    elif selected_date_filter == '2':
                        start_date = datetime.now() - timedelta(days=30)
                        end_date = datetime.now()

                    elif selected_date_filter == '3':
                        start_date = datetime.now() - timedelta(days=90)
                        end_date = datetime.now()

                    elif selected_date_filter == '4':
                        start_date = bot_obj.created_datetime
                        end_date = datetime.now()
                        
                    elif selected_date_filter == '5':
                        start_date = data['start_date']
                        end_date = data['end_date']

                        start_date, end_date, error_message = validation_obj.get_start_and_end_date_time(
                            start_date, end_date)
                        if error_message:
                            response["message"] = error_message
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)

                    campaign_objs = Campaign.objects.filter(
                        bot=bot_obj, is_deleted=False, start_datetime__date__gte=start_date, start_datetime__date__lte=end_date)

                if channel_list:
                    channel_objs = CampaignChannel.objects.filter(value__in=channel_list)
                else:
                    channel_objs = CampaignChannel.objects.filter(is_deleted=False)

                # total run campaigns
                campaign_objs = campaign_objs.filter(status__in=[CAMPAIGN_COMPLETED, CAMPAIGN_IN_PROGRESS, CAMPAIGN_PARTIALLY_COMPLETED, CAMPAIGN_FAILED, CAMPAIGN_PROCESSED, CAMPAIGN_ONGOING])

                channel_stats_label = []
                channel_stats_data = []

                for channel in channel_objs:
                    channel_stats_label.append(channel.name)
                    channel_stats_data_objs = campaign_objs.filter(channel=channel)
                    channel_stats_data.append(channel_stats_data_objs.count())            

                response['status'] = 200
                response['message'] = 'success'
                response['channel_stats_label'] = channel_stats_label
                response['channel_stats_data'] = channel_stats_data

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetChannelCampaignStatsAnalyticssAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetChannelCampaignStatsAnalytics = GetChannelCampaignStatsAnalyticsAPI.as_view()
