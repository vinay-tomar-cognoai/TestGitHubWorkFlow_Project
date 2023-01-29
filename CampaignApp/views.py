from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from cronjob_scripts.campaign_export import generate_report, generate_test_report

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
from CampaignApp.permissions import *

from CampaignApp.views_api_integration import *
from CampaignApp.views_tag_audience import *
from CampaignApp.views_campaign_template import *
from CampaignApp.views_analytics import *
from CampaignApp.views_external_api import *
from CampaignApp.views_campaign_schedule import *
from CampaignApp.views_voice_bot import *
from CampaignApp.views_whatsapp_campaign_details import *

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


# Logger
import logging
logger = logging.getLogger(__name__)
validation_obj = CampaignInputValidation()


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


"""

LogoutAPI() : Logout user from the current session

"""


@authentication_classes([CsrfExemptSessionAuthentication, BasicAuthentication])
def LogoutAPI(request):
    if request.user.is_authenticated:
        user_obj = User.objects.get(username=request.user.username)
        user_obj.is_online = False
        user_obj.save()
        try:
            secured_login_obj = SecuredLogin.objects.get(user=user_obj)
            secured_login_obj.failed_attempts = 0
            secured_login_obj.is_online = False
            secured_login_obj.save()

            campaign_user_objs = CampaignAuthUser.objects.filter(user=user_obj)

            for campaign_user_obj in campaign_user_objs:
                campaign_user_obj.is_token_expired = True
                campaign_user_obj.save()
        except Exception:
            pass

        logout_all(request.user.username, UserSession, Session)
        logout(request)

    return redirect("/chat/login/")


"""

UnauthorisedPage() : Render Unauthorised page

"""


def UnauthorisedPage(request):
    try:
        message = None
        if "campaign" in request.GET:
            message = "Campaign is in progress"

        return render(request, "CampaignApp/unauthorised.html", {
            "message": message
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("UnauthorisedPage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return HttpResponse("Invalid Access")


"""

CampaignHomePage() : Render Campaign Dashboard page

"""


@login_required(login_url="/chat/login")
def CampaignHomePage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']

        try:
            access_token = request.GET['access_token']
        except Exception:
            access_token = None

        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        check_and_create_config_obj(bot_obj, CampaignConfig)

        channels = CampaignChannel.objects.filter(is_deleted=False)

        channel_names = []
        for channel in channels:
            channel_names.append(channel.name)

        show_sqs_count = False
        bot_wsp_obj = CampaignBotWSPConfig.objects.filter(
            bot=bot_obj, whatsapp_service_provider__name=CAMPAIGN_BOT_BSP_FOR_SQS).first()
        if bot_wsp_obj and bot_wsp_obj.show_sqs_message_count:
            show_sqs_count = True

        if request.user in bot_obj.users.all():
            return render(request, "CampaignApp/dashboard.html", {
                'selected_bot_obj': bot_obj,
                'access_token': access_token,
                'default_start_date': bot_obj.created_datetime.date(),
                'default_end_date': (datetime.today()).date(),
                'channels': channels,
                'channel_names': channel_names,
                'show_sqs_count': show_sqs_count
            })
        else:
            return redirect("/campaign/unauthorised/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CampaignHomePage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


"""

CreateCampaignPage() : Render Create Campaign page (Basic Info Page)

"""


@login_required(login_url="/chat/login")
def CreateCampaignPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']

        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        if request.user in bot_obj.users.all():
            campaign_channels = CampaignChannel.objects.filter(
                is_deleted=False).order_by("order")
            campaign_obj = None
            if "campaign_id" in request.GET:
                campaign_id = request.GET["campaign_id"]
                campaign_obj = Campaign.objects.filter(
                    pk=int(campaign_id), bot=bot_obj, is_deleted=False).first()

                if check_campaign_in_progress(campaign_obj):
                    return redirect("/campaign/unauthorised/?campaign=progress")

                campaign_obj.last_saved_state = CAMPAIGN_BASIC_INFO_STATE
                campaign_obj.save()

            return render(request, "CampaignApp/create_campaign.html", {
                "campaign_channels": campaign_channels,
                "selected_bot_obj": bot_obj,
                "campaign_obj": campaign_obj,
            })
        else:
            return redirect("/campaign/unauthorised/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CreateCampaignPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


"""

EditCampaignPage() : Redirect to last saved state of campaign (only for draft)

"""


@login_required(login_url="/chat/login")
def EditCampaignPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        if request.user in bot_obj.users.all():
            campaign_id = request.GET['campaign_id']
            campaign_obj = Campaign.objects.get(
                pk=int(campaign_id), bot=bot_obj, is_deleted=False)

            last_saved_state = campaign_obj.last_saved_state

            last_saved_page_url = get_last_saved_page_url(
                last_saved_state, bot_pk, campaign_id)
            return HttpResponseRedirect(last_saved_page_url)
        else:
            return redirect("/campaign/unauthorised/")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error EditCampaignPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


"""

CampaignReviewPage() : Render Campaign Review page

"""


@login_required(login_url="/chat/login")
def CampaignReviewPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        if request.user in bot_obj.users.all():
            try:
                campaign_id = request.GET['campaign_id']
                campaign_obj = Campaign.objects.get(
                    pk=int(campaign_id), bot=bot_obj, is_deleted=False)
            except Exception:
                return redirect("/campaign/create-campaign/?bot_pk=" + str(bot_pk))

            valid_data_obj = check_campaign_current_page_valid(
                CAMPIGN_REVIEW_STATE, campaign_obj)

            if valid_data_obj["is_valid"] == False:
                last_saved_page_url = get_last_saved_page_url(
                    valid_data_obj["last_saved_state"], bot_pk, campaign_id)
                return HttpResponseRedirect(last_saved_page_url)

            if check_campaign_in_progress(campaign_obj):
                return redirect("/campaign/dashboard/?bot_pk=" + str(bot_pk))

            campaign_channels = CampaignChannel.objects.filter(
                is_deleted=False)

            campaign_api_obj = CampaignAPI.objects.filter(
                campaign=campaign_obj).first()

            if campaign_obj.channel.name != 'RCS':
                template_obj = campaign_obj.campaign_template
            else:
                template_obj = campaign_obj.campaign_template_rcs

            is_api_completed = False
            if campaign_api_obj and campaign_api_obj.is_api_completed == True:
                is_api_completed = True
            campaign_batch = campaign_obj.batch
            try:
                template_variable_obj = CampaignTemplateVariable.objects.get(
                    template=template_obj, campaign=campaign_obj, batch=campaign_batch)
                variables = json.loads(template_variable_obj.variables)
                header_variables = json.loads(template_variable_obj.header_variable)
                dynamic_cta_url_variables = json.loads(template_variable_obj.dynamic_cta_url_variable)
                attachment_details = template_variable_obj.attachment_details
                if not isinstance(attachment_details, dict):
                    attachment_details = json.loads(attachment_details)
                dynamic_attactment_column = attachment_details.get('dynamic_attactment_column', 'none')
                doc_name_options = attachment_details.get('doc_name_options', 'none')
                is_static = attachment_details.get('is_static', True)
                fall_back_doc_name = attachment_details.get('fall_back_doc_name', '')
                attachment_details = attachment_details.get('custom_attachment_url')

            except Exception:
                variables = []
                header_variables = []
                dynamic_cta_url_variables = []
                attachment_details = ''
                dynamic_attactment_column = ''
                doc_name_options = ''
                fall_back_doc_name = ''
                is_static = True

            bot_wsp_objs = CampaignBotWSPConfig.objects.filter(bot=bot_obj)
            selected_bot_bsp = campaign_api_obj.campaign_bot_wsp_config

            campaign_obj.last_saved_state = CAMPIGN_REVIEW_STATE
            campaign_obj.save()
            rcs_campaign_template_details = {}
            if campaign_obj.channel.name == 'RCS':
                rcs_campaign_template_details = parse_rcs_campaign_template_details(template_obj)
            
            template_metadata = json.loads(template_obj.template_metadata)
            template_header = template_obj.template_header
            template_body = template_obj.template_body
            cta_link = template_obj.cta_link

            if template_body:
                template_body = get_unique_template_variable_body(template_body, variables)

            if template_header:
                template_header = get_unique_template_variable_body(template_header, header_variables)

            if cta_link:
                cta_link = get_unique_template_variable_body(cta_link, dynamic_cta_url_variables)
            
            batch_obj = campaign_obj.batch
            header_fields_json = json.loads(batch_obj.batch_header_meta)

            header_fields = []
            for header in header_fields_json:
                header_fields.append(header['col_name'])

            attachment_src = ''
            if attachment_details:
                attachment_src = attachment_details
            else:
                attachment_src = template_obj.attachment_src

            return render(request, "CampaignApp/campaign_review.html", {
                "campaign_channels": campaign_channels,
                "selected_bot_obj": bot_obj,
                "campaign_obj": campaign_obj,
                "template_obj": template_obj,
                "callus_number": template_metadata.get('callus_number'),
                "callus_text": template_metadata.get('callus_text'),
                "type_of_first_cta_btton": template_metadata.get('type_of_first_cta_btton'),
                "template_qr_1": template_metadata.get('template_qr_1'),
                "template_qr_2": template_metadata.get('template_qr_2'),
                "template_qr_3": template_metadata.get('template_qr_3'),
                "is_api_completed": is_api_completed,
                "variables": variables,
                "bot_wsp_objs": bot_wsp_objs,
                "is_single_vendor": bot_wsp_objs.count() == 1,
                "rcs_campaign_template_details": rcs_campaign_template_details,
                "template_header": template_header,
                "template_body": template_body,
                "cta_link": cta_link,
                "dynamic_cta_url_variable": '{{' + dynamic_cta_url_variables[0] + '}}' if dynamic_cta_url_variables else [],
                "header_fields": header_fields,
                "document_name": template_metadata.get('document_file_name', 'document'),
                "attachment_src": attachment_src,
                "campaign_batch": campaign_batch.total_audience,
                "batch_name": campaign_batch.batch_name,
                'dynamic_attactment_column': dynamic_attactment_column,
                'doc_name_options': doc_name_options,
                'selected_bot_bsp': selected_bot_bsp,
                'fall_back_doc_name': fall_back_doc_name,
                'is_static': is_static,
            })
        else:
            return redirect("/campaign/unauthorised/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CampaignReviewPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


"""

CampaignSchedulePage() : Render Campaign Schedule page

"""


@login_required(login_url="/chat/login")
def CampaignSchedulePage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_wsp_id = -1
        channel = request.GET['channel']
        if channel == "WhatsApp":
            bot_wsp_id = request.GET['bot_wsp_id']

        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        if request.user in bot_obj.users.all():
            try:
                campaign_id = request.GET['campaign_id']
                campaign_obj = Campaign.objects.get(
                    pk=int(campaign_id), bot=bot_obj, is_deleted=False)
            except Exception:
                return redirect("/campaign/create-campaign/?bot_pk=" + str(bot_pk))

            valid_data_obj = check_campaign_current_page_valid(
                CAMPIGN_REVIEW_STATE, campaign_obj)

            if valid_data_obj["is_valid"] == False:
                last_saved_page_url = get_last_saved_page_url(
                    valid_data_obj["last_saved_state"], bot_pk, campaign_id)
                return HttpResponseRedirect(last_saved_page_url)

            campaign_channels = CampaignChannel.objects.filter(
                is_deleted=False)

            campaign_api_obj = CampaignAPI.objects.filter(
                campaign=campaign_obj).first()

            template_obj = campaign_obj.campaign_template

            is_api_completed = False
            if campaign_api_obj and campaign_api_obj.is_api_completed == True:
                is_api_completed = True

            bot_wsp_obj = CampaignBotWSPConfig.objects.filter(pk=int(bot_wsp_id)).first()
            if bot_wsp_obj:
                campaign_api_obj.campaign_bot_wsp_config = bot_wsp_obj
                campaign_api_obj.save()
            batch_objs = CampaignBatch.objects.filter(bot=bot_obj)

            return render(request, "CampaignApp/campaign_schedule.html", {
                "campaign_channels": campaign_channels,
                "selected_bot_obj": bot_obj,
                "campaign_obj": campaign_obj,
                "template_obj": template_obj,
                "is_api_completed": is_api_completed,
                "campaign_name": campaign_obj.name,
                "batch_objs": batch_objs,
            })
        else:
            return redirect("/campaign/unauthorised/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CampaignSchedulePage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


"""

CampaignTemplatePage() : Render Campaign Template page

"""


@login_required(login_url="/chat/login")
def CampaignTemplatePage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        if request.user in bot_obj.users.all():
            try:
                campaign_id = request.GET['campaign_id']
                campaign_obj = Campaign.objects.get(
                    pk=int(campaign_id), bot=bot_obj, is_deleted=False)
            except Exception:
                return redirect("/campaign/create-campaign/?bot_pk=" + str(bot_pk))

            valid_data_obj = check_campaign_current_page_valid(
                CAMPAIGN_TEMPLATE_STATE, campaign_obj)

            if valid_data_obj["is_valid"] == False:
                last_saved_page_url = get_last_saved_page_url(
                    valid_data_obj["last_saved_state"], bot_pk, campaign_id)
                return HttpResponseRedirect(last_saved_page_url)

            if check_campaign_in_progress(campaign_obj):
                return redirect("/campaign/unauthorised/?campaign=progress")

            batch_obj = campaign_obj.batch
            header_fields_json = json.loads(batch_obj.batch_header_meta)

            header_fields = []
            for header in header_fields_json:
                header_fields.append(header['col_name'])

            try:
                template_variable_obj = CampaignTemplateVariable.objects.get(
                    campaign=campaign_obj, template=campaign_obj.campaign_template, batch=campaign_obj.batch)
                variables = json.loads(template_variable_obj.variables)
                cta_variables = json.loads(template_variable_obj.dynamic_cta_url_variable)
                header_variable = json.loads(template_variable_obj.header_variable)
                selected_template_pk = template_variable_obj.template.pk
            except Exception:
                variables = []
                cta_variables = []
                header_variable = []
                selected_template_pk = 0

            campaign_obj.last_saved_state = CAMPAIGN_TEMPLATE_STATE
            campaign_obj.save()

            return render(request, "CampaignApp/campaign_template.html", {
                "selected_bot_obj": bot_obj,
                "campaign_obj": campaign_obj,
                "header_fields": header_fields,
                "variables": variables,
                "cta_variables": cta_variables,
                "header_variable": header_variable,
                "channel": campaign_obj.channel.name,
                "selected_template_pk": selected_template_pk,
            })
        else:
            return redirect("/campaign/unauthorised/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CampaignTemplatePage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


"""

TagAudiencePage() : Render Campaign Tag Audience page

"""


@login_required(login_url="/chat/login")
def TagAudiencePage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        if request.user in bot_obj.users.all():
            try:
                campaign_id = request.GET['campaign_id']
                campaign_obj = Campaign.objects.get(
                    pk=int(campaign_id), bot=bot_obj, is_deleted=False)
            except Exception:
                return redirect("/campaign/create-campaign/?bot_pk=" + str(bot_pk))

            valid_data_obj = check_campaign_current_page_valid(
                CAMPAIGN_TAG_AUDIENCE_STATE, campaign_obj)

            if valid_data_obj["is_valid"] == False:
                last_saved_page_url = get_last_saved_page_url(
                    valid_data_obj["last_saved_state"], bot_pk, campaign_id)
                return HttpResponseRedirect(last_saved_page_url)

            if check_campaign_in_progress(campaign_obj):
                return redirect("/campaign/unauthorised/?campaign=progress")

            campaign_channels = CampaignChannel.objects.filter(
                is_deleted=False)

            channel_names = []
            for channel in campaign_channels:
                channel_names.append(channel.name)

            campaign_obj.last_saved_state = CAMPAIGN_TAG_AUDIENCE_STATE
            campaign_obj.save()

            return render(request, "CampaignApp/tag_audience.html", {
                "campaign_channels": campaign_channels,
                "selected_bot_obj": bot_obj,
                "campaign_id": campaign_id,
                "channel": campaign_obj.channel.name,
                "campaign_obj": campaign_obj,
                "channel_names": channel_names,
            })
        else:
            return redirect("/campaign/unauthorised/")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error TagAudiencePage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


"""

CampaignAnalyticsPage() : Renders campaign analytics page

"""


@login_required(login_url="/chat/login")
def CampaignAnalyticsPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        try:
            access_token = request.GET['access_token']
        except Exception:
            access_token = None

        if request.user in bot_obj.users.all():
            start_date = bot_obj.created_datetime.date()
            end_date = datetime.now().strftime('%Y-%m-%d')
            campaign_objs = Campaign.objects.filter(bot=bot_obj, is_deleted=False, channel__is_deleted=False).exclude(
                status__in=[CAMPAIGN_DRAFT, CAMPAIGN_SCHEDULED, CAMPAIGN_SCHEDULE_COMPLETED])
            campaign_channels = CampaignChannel.objects.filter(
                is_deleted=False)
            return render(request, "CampaignApp/campaign_analytics.html", {
                "selected_bot_obj": bot_obj,
                "campaign_objs": campaign_objs,
                "access_token": access_token,
                "start_date": start_date,
                "end_date": end_date,
                "campaign_channels": campaign_channels,
            })
        else:
            return redirect("/campaign/unauthorised/")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CampaignAnalyticsPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


"""

GetActiveCampaignsAPI() : return all active campaign objs

"""


class GetActiveCampaignsAPI(APIView):

    permission_classes = [IsAuthenticated, DisableOptionsPermission]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            page = data["page"]
            bot_pk = data["bot_pk"]
            bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)
            channels = data['channels']
            searched_campaign = data['searched_campaign']
            filter_date_type = data['filter_date_type']
            tab = data.get("tab", "all_campaigns")

            campaign_objs = Campaign.objects.filter(
                is_deleted=False, bot=bot_obj, channel__name__in=channels, channel__is_deleted=False)

            if tab == "all_campaigns":
                campaign_objs = campaign_objs.exclude(
                    status__in=[CAMPAIGN_SCHEDULED, CAMPAIGN_SCHEDULE_COMPLETED])
            elif tab == "schedules":
                status_filter_query = reduce(operator.or_, (Q(status=status) for status in [
                                             CAMPAIGN_SCHEDULED, CAMPAIGN_SCHEDULE_COMPLETED]))
                campaign_objs = campaign_objs.filter(status_filter_query)

            if filter_date_type == '4':
                campaign_objs = campaign_objs.filter(is_deleted=False)
            else:
                if filter_date_type == '1':
                    start_date = datetime.now() - timedelta(days=7)
                    end_date = datetime.now()

                elif filter_date_type == '2':
                    start_date = datetime.now() - timedelta(days=30)
                    end_date = datetime.now()

                elif filter_date_type == '3':
                    start_date = datetime.now() - timedelta(days=90)
                    end_date = datetime.now()

                elif filter_date_type == '5':
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

                campaign_objs = campaign_objs.filter(
                    create_datetime__date__gte=start_date, create_datetime__date__lte=end_date, is_deleted=False)

            if 'selected_status' in data:
                status = data['selected_status']

                campaign_objs = campaign_objs.filter(status__in=status)

            if searched_campaign:
                campaign_objs = campaign_objs.filter(
                    name__icontains=searched_campaign)

            campaign_objs = campaign_objs.order_by('-create_datetime')

            total_rows_per_pages = 100
            total_campaign_objs = campaign_objs.count()

            paginator = Paginator(
                campaign_objs, total_rows_per_pages)

            try:
                campaign_objs = paginator.page(page)
            except PageNotAnInteger:
                campaign_objs = paginator.page(1)
            except EmptyPage:
                campaign_objs = paginator.page(paginator.num_pages)

            if page != None:
                start_point = total_rows_per_pages * (int(page) - 1) + 1
                end_point = min(total_rows_per_pages *
                                int(page), total_campaign_objs)
                if start_point > end_point:
                    start_point = max(end_point - len(campaign_objs) + 1, 1)
            else:
                start_point = 1
                end_point = min(total_rows_per_pages, total_campaign_objs)

            start_point = min(start_point, end_point)

            pagination_range = campaign_objs.paginator.page_range

            has_next = campaign_objs.has_next()
            has_previous = campaign_objs.has_previous()
            next_page_number = -1
            previous_page_number = -1

            if has_next:
                next_page_number = campaign_objs.next_page_number()
            if has_previous:
                previous_page_number = campaign_objs.previous_page_number()

            pagination_metadata = {
                'total_count': total_campaign_objs,
                'start_point': start_point,
                'end_point': end_point,
                'page_range': [pagination_range.start, pagination_range.stop],
                'has_next': has_next,
                'has_previous': has_previous,
                'next_page_number': next_page_number,
                'previous_page_number': previous_page_number,
                'number': campaign_objs.number,
                'num_pages': campaign_objs.paginator.num_pages
            }

            active_campaigns = []
            for campaign_obj in campaign_objs:
                active_campaigns.append(parse_campaign_details(
                    campaign_obj, CampaignAnalytics, CampaignAPI))

            bot_wsp_obj = CampaignBotWSPConfig.objects.filter(
                bot=bot_obj, whatsapp_service_provider__name=CAMPAIGN_BOT_BSP_FOR_SQS).first()
            if bot_wsp_obj and bot_wsp_obj.show_sqs_message_count:
                response["messages_in_sqs_queue"] = get_messages_in_queue(bot_wsp_obj)
                # To get the actual count in the queue
                # attribute_names = ['ApproximateNumberOfMessages']
                # attributes = get_queue_attributes(attribute_names, bot_wsp_obj)
                # if attributes:
                #     messages_in_sqs_queue = attributes['Attributes']['ApproximateNumberOfMessages']
                #     response["messages_in_sqs_queue"] = messages_in_sqs_queue
                # else:
                #     response["messages_in_sqs_queue"] = 'NA'

            response["status"] = 200
            response["message"] = "success"
            response["active_campaigns"] = active_campaigns
            response["pagination_metadata"] = pagination_metadata
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetActiveCampaignsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetActiveCampaigns = GetActiveCampaignsAPI.as_view()


"""

DeleteCampaignsAPI() : delete campaign API

"""


class DeleteCampaignsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def delete_campaign(self, campaign_obj):
        try:
            campaign_obj.is_deleted = True
            campaign_obj.delete_datetime = timezone.now()
            campaign_obj.save()

            batch_objs = CampaignBatch.objects.filter(
                campaigns__in=[campaign_obj])
            for batch_obj in batch_objs:
                batch_obj.campaigns.remove(campaign_obj)

            CampaignSchedule.objects.filter(
                campaign=campaign_obj).delete()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("delete_campaign: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            campaign_ids = data["campaign_ids"]

            campaign_objs = Campaign.objects.filter(pk__in=campaign_ids)
            is_unauthorized = False
            for campaign_obj in campaign_objs.iterator():
                if request.user not in campaign_obj.bot.users.all():
                    is_unauthorized = True
                    break
            if is_unauthorized:
                response["status"] = "401"
                if campaign_objs.count() == 1:
                    response['status_message'] = 'You are not authorised to delete this campaign'
                else:
                    response['status_message'] = 'You are not authorised to delete some of the campaigns'
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response) 

            for campaign_obj in campaign_objs:

                if campaign_obj.channel.value == 'voicebot' and campaign_obj.status in [CAMPAIGN_IN_PROGRESS, CAMPAIGN_SCHEDULED]:
                    voice_bot_obj = CampaignVoiceBotSetting.objects.get(
                        campaign=campaign_obj)
                    api_obj = check_and_create_voice_bot_api_obj(
                        campaign_obj, CampaignVoiceBotAPI)
                    api_code = api_obj.api_code

                    processor_check_dictionary = {'open': open_file}

                    param = {
                        'campaign_sid': voice_bot_obj.campaign_sid,
                        'url': voice_bot_obj.url,
                        'bot_id': str(campaign_obj.bot.pk)
                    }

                    exec(str(api_code), processor_check_dictionary)
                    json_data = processor_check_dictionary['pause_running_campaign'](
                        json.dumps(param))

                    logger.info("pause campaign: %s", str(
                        json_data), extra={'AppName': 'Campaign'})

                    if campaign_obj.status == CAMPAIGN_SCHEDULED:
                        self.delete_campaign(campaign_obj)

                    if json_data['response']:
                        status_code = json_data['response'][0]['code']

                        if status_code == 200:
                            campaign_obj.status = CAMPAIGN_COMPLETED
                            campaign_obj.save()
                    
                else:
                    self.delete_campaign(campaign_obj)

            response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteCampaignsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteCampaigns = DeleteCampaignsAPI.as_view()


"""

CheckScheduleExistsAPI() : Check if api configured

"""


class CheckScheduleExistsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Not able to open schedule page. Please try again"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            campaign_id = data["campaign_id"]
            bot_id = data["bot_pk"]

            bot_objs = Bot.objects.filter(pk=int(bot_id), is_deleted=False)
            if bot_objs.count() > 0:
                bot_obj = bot_objs.first()
                campaign_objs = Campaign.objects.filter(
                    pk=int(campaign_id), bot=bot_obj)
                if campaign_objs.count() > 0:
                    campaign_obj = campaign_objs.first()
                    response["channel"] = campaign_obj.channel.name
                    campaign_api_objs = CampaignAPI.objects.filter(
                        campaign=campaign_obj)
                    if campaign_api_objs.count() > 0:
                        campaign_api_obj = campaign_api_objs.first()
                        if campaign_api_obj.is_api_completed:
                            response["status"] = 200
                            if campaign_obj.channel.name == "Whatsapp Business":
                                if campaign_api_obj.campaign_bot_wsp_config == None:
                                    response["status"] = 401
                                    response["status_message"] = "No schedules found"
                                else:
                                    response["bot_wsp_id"] = campaign_api_obj.campaign_bot_wsp_config.pk
                            elif campaign_obj.channel.name == "RCS":
                                if campaign_obj.campaign_template_rcs == None:
                                    response["status"] = 401
                                    response["status_message"] = "No schedules found"
                        else:
                            response["status"] = 401
                            response["status_message"] = "Api not configured for campaign."

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CheckScheduleExistsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status"] = 500
            response["status_message"] = "Not able to open schedule page. Please try again"

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckScheduleExists = CheckScheduleExistsAPI.as_view()


"""

CreateNewCampaignAPI() : create new campaign API

"""


class CreateNewCampaignAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            bot_id = data["bot_id"]
            channel_id = data["channel_id"]
            campaign_name = data["campaign_name"]
            campaign_name = strip_html_tags(campaign_name)
            campaign_name = remo_special_tag_from_string(campaign_name)

            if len(campaign_name.strip()) == 0 or validation_obj.check_for_special_characters(campaign_name):
                response["status"] = 400
                response["status_message"] = 'Please Enter Valid Campaign Name'

            channel_obj = CampaignChannel.objects.get(pk=int(channel_id))
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            if request.user not in bot_obj.users.all():
                response["status"] = 400
                response["status_message"] = 'You are not authorised to create this campaign'

            if channel_obj.name == 'RCS' and not RCSDetails.objects.filter(bot=bot_obj).exists():
                response["status"] = 402
                response["status_message"] = 'Please setup RCS Channel for the bot'

            if response["status"] == 400 or response["status"] == 402:
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            existing_campaign_obj = Campaign.objects.filter(
                name__iexact=campaign_name, bot=bot_obj, is_deleted=False).first()

            check_and_create_config_obj(bot_obj, CampaignConfig)
        
            try:
                campaign_id = data["campaign_id"]
                campaign_obj = Campaign.objects.get(pk=campaign_id)

                if existing_campaign_obj and campaign_obj.pk != existing_campaign_obj.pk:
                    response["status"] = 301

                elif campaign_obj.status == CAMPAIGN_IN_PROGRESS:
                    response["status"] = 401
                else:
                    campaign_obj.name = campaign_name
                    campaign_obj.channel = channel_obj
                    campaign_obj.bot = bot_obj
                    campaign_obj.status = CAMPAIGN_DRAFT
                    campaign_obj.last_saved_state = CAMPAIGN_BASIC_INFO_STATE
                    campaign_obj.save()

                    check_and_create_campaign_api(channel_obj, campaign_obj, CampaignAPI, CampaignVoiceBotAPI)

                    response["status"] = 200
                    response["campaign_id"] = str(campaign_obj.pk)

            except Exception:

                if existing_campaign_obj:
                    response["status"] = 301
                else:
                    campaign_obj = Campaign.objects.create(
                        name=campaign_name,
                        channel=channel_obj,
                        bot=bot_obj,
                        status=CAMPAIGN_DRAFT,
                        last_saved_state=CAMPAIGN_BASIC_INFO_STATE
                    )

                    check_and_create_campaign_api(channel_obj, campaign_obj, CampaignAPI, CampaignVoiceBotAPI)

                    response["status"] = 200
                    response["campaign_id"] = str(campaign_obj.pk)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateNewCampaignAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CreateNewCampaign = CreateNewCampaignAPI.as_view()


"""

CreateNewCloneCampaignAPI() : create new clone campaign API

"""


class CreateNewCloneCampaignAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = "The server was unable to process your request due to an internal error. Please try again after some time."
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            bot_id = data["bot_id"]
            campaign_id = data["campaign_id"]
            campaign_obj = Campaign.objects.get(pk=campaign_id)
            campaign_name = data["cloned_campaign_name"]

            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            existing_campaign_obj = Campaign.objects.filter(
                name__iexact=campaign_name, bot=bot_obj, is_deleted=False).first()

            if request.user not in bot_obj.users.all():
                response["status"] = 400
                response["status_message"] = 'You are not authorised to create this campaign'

            elif campaign_obj.channel.value in ['voicebot', 'rcs']:
                response["status"] = 402
                response["status_message"] = 'The duplicate campaign feature is only supported on the WhatsApp channel for now.'

            elif campaign_obj.status == CAMPAIGN_DRAFT or not campaign_obj.is_source_dashboard:
                response["status"] = 401
                response["status_message"] = 'You cannot duplicate a Draft campaign and any campaigns created by the External APIs.'

            elif existing_campaign_obj:
                response["status"] = 301
                response["status_message"] = 'This campaign name already exists, please provide another name.'

            if response["status"] in [301, 400, 401, 402]:
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            check_and_create_config_obj(bot_obj, CampaignConfig)
            cloned_campaign_obj = create_cloned_campaign(campaign_obj, campaign_name)

            response["status"] = 200
            response["campaign_id"] = str(cloned_campaign_obj.pk)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateNewCloneCampaignAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CreateNewCloneCampaign = CreateNewCloneCampaignAPI.as_view()


"""

ExportCampaignReportAPI() : Export campaign report API

"""


class ExportCampaignReportAPI(APIView):

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
            email_id = data["email_id"].strip()
            export_type = data['export_type']
            is_instant_download = data['is_instant_download']

            bot_obj = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            campaign_obj = Campaign.objects.filter(bot=bot_obj, is_deleted=False, channel__is_deleted=False)
            status_filter_query = reduce(operator.or_, (Q(status=status) for status in ['completed', 'partially_completed', 'failed', 'ongoing']))
            campaign_obj = campaign_obj.filter(status_filter_query)

            if request.user not in bot_obj.users.all():
                response[
                    'message'] = 'You are not authorised to perform this request.'
            elif not campaign_obj.first() and export_type != '4':
                response["status"] = 400
                response["message"] = "There is no data available to export for the selected date range."
            elif not is_instant_download and not validation_obj.is_valid_email(email_id):
                response['message'] = 'Please enter a valid Email ID.'
            else:
                if export_type == '2':
                    export_request = CampaignExportRequest.objects.create(
                        email_id=email_id,
                        export_type=export_type,
                        user=request.user,
                        bot=bot_obj)
                    request_date_type = data['request_date_type']

                    if request_date_type == '1':
                        start_date = datetime.today() - timedelta(days=1)
                        end_date = datetime.today()
                    elif request_date_type == '2':
                        start_date = datetime.today() - timedelta(days=7)
                        end_date = datetime.today()
                    elif request_date_type == '3':
                        start_date = datetime.today() - timedelta(days=30)
                        end_date = datetime.today()
                    else:
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

                    campaign_obj = campaign_obj.filter(created_date__gte=start_date, created_date__lte=end_date).first()
                    is_empty_request, response = get_audience_log_exists_for_export_of_campaign(False, campaign_obj, custom_encrypt_obj, response)
                    if is_empty_request == 400:
                        return Response(data=response)

                    export_request.start_date = start_date
                    export_request.end_date = end_date
                    export_request.save()

                elif export_type == '4':
                    campaign_id = data["campaign_id"]
                    campaign_obj = Campaign.objects.filter(
                        pk=int(campaign_id)).first()
                    file_path = generate_test_report(
                        campaign_obj, masking_enabled)
                    if file_path:
                        file_path = 'files/' + file_path[0]
                        response['file_path'] = file_path
                    else:
                        return Response(data=response)
                else:
                    campaign_id = data["campaign_id"]
                    campaign_obj = Campaign.objects.filter(pk=int(campaign_id)).first()
                    is_empty_request, response = get_audience_log_exists_for_export_of_campaign(True, campaign_obj, custom_encrypt_obj, response)
                    if is_empty_request:
                        return Response(data=response)
                    if is_instant_download:
                        file_path = generate_report(campaign_obj, masking_enabled)
                        file_path = 'files/' + file_path[0]
                        response['file_path'] = file_path
                    else:
                        CampaignExportRequest.objects.create(
                            email_id=email_id,
                            export_type=export_type,
                            user=request.user,
                            bot=bot_obj,
                            campaign=campaign_obj)

                response['status'] = 200
                response['message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportCampaignReportAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportCampaignReport = ExportCampaignReportAPI.as_view()


class SendCampaignAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_id = data['campaign_id']
            bot_pk = data['bot_pk']
            bot_wsp_id = data['bot_wsp_id']

            bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

            if request.user not in bot_obj.users.all():
                response[
                    'message'] = 'You are not authorised to send campaign for this bot.'
            else:
                campaign_obj = Campaign.objects.get(pk=int(campaign_id))
                response, campaign_wsp_config_meta, bot_wsp_obj = get_campaign_wsp_config_meta(campaign_obj, bot_wsp_id, response)
                if response['status'] == 201:
                    if campaign_wsp_config_meta["enable_queuing_system"]:
                        sqs_response = validate_aws_sqs_credentials(
                            bot_wsp_obj, campaign_wsp_config_meta)

                        if sqs_response == None:
                            response['message'] = 'Unable to connect to the queueing system due to invalid credentials. Please connect with our support team to get this resolved.'
                            response['status'] = 404
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)

                    t1 = threading.Thread(target=execute_send_campaign, args=(campaign_wsp_config_meta, campaign_id,
                                          Campaign, CampaignFileAccessManagement, CampaignAudience, CampaignAudienceLog, CampaignAnalytics, CampaignTemplateVariable))
                    t1.daemon = True
                    t1.start()

                    campaign_obj.start_datetime = datetime.now()
                    campaign_obj.show_processed_datetime = True
                    campaign_obj.status = CAMPAIGN_IN_PROGRESS
                    campaign_obj.is_source_dashboard = True  # True because campaign is being sent from GUI
                    campaign_obj.save(
                        update_fields=['start_datetime', 'status', 'is_source_dashboard', 'show_processed_datetime'])
                    response['status'] = 200
                    response['message'] = 'success'
                    response['status_message'] = 'success'

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SendCampaignAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SendCampaign = SendCampaignAPI.as_view()


class SendRCSCampaignAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_id = data['campaign_id']
            bot_pk = data['bot_pk']

            bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

            if request.user not in bot_obj.users.all():
                response[
                    'message'] = 'You are not authorised to send campaign for this bot.'
            else:
                campaign_obj = Campaign.objects.get(pk=int(campaign_id))
                campaign_api = CampaignAPI.objects.filter(
                    campaign=campaign_obj)

                if not campaign_api or not campaign_api[0].is_api_completed:
                    response[
                        'message'] = 'Send Campaign failed because API Integration is pending.'
                else:
                    campaign_api = campaign_api[0]
                    campaign_api.save()

                    t1 = threading.Thread(target=execute_send_rcs_campaign, args=(campaign_id, None,
                                          Campaign, CampaignFileAccessManagement, CampaignAudience, CampaignAudienceLog, CampaignAnalytics, CampaignTemplateVariable))
                    t1.daemon = True
                    t1.start()

                    campaign_obj.status = CAMPAIGN_IN_PROGRESS
                    campaign_obj.is_source_dashboard = True  # True because campaign is being sent from GUI
                    campaign_obj.save(update_fields=['status', 'is_source_dashboard'])
                    response['status'] = 200
                    response['message'] = 'success'

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SendRCSCampaignAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SendRCSCampaign = SendRCSCampaignAPI.as_view()


"""

TriggerSettingsPage() : Render Campaign Trigger Settings page

"""


@login_required(login_url="/chat/login")
def TriggerSettingsPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        if request.user in bot_obj.users.all():
            try:
                campaign_id = request.GET['campaign_id']
                campaign_obj = Campaign.objects.get(
                    pk=int(campaign_id), bot=bot_obj, is_deleted=False)
            except Exception:
                return redirect("/campaign/create-campaign/?bot_pk=" + str(bot_pk))

            campaign_objs = Campaign.objects.filter(
                bot=bot_obj, is_deleted=False)

            valid_data_obj = check_campaign_current_page_valid(
                CAMPAIGN_SETTINGS_STATE, campaign_obj)

            if valid_data_obj["is_valid"] == False:
                last_saved_page_url = get_last_saved_page_url(
                    valid_data_obj["last_saved_state"], bot_pk, campaign_id)
                return HttpResponseRedirect(last_saved_page_url)

            if check_campaign_in_progress(campaign_obj):
                return redirect("/campaign/unauthorised/?campaign=progress")

            campaign_channels = CampaignChannel.objects.filter(
                is_deleted=False)

            caller_id_objs = VoiceBotCallerID.objects.filter(bot=bot_obj)

            voice_bot_obj = check_and_create_trigger_setting(
                campaign_obj, CampaignVoiceBotSetting, VoiceBotRetrySetting)

            trigger_setting = parse_trigger_settings(voice_bot_obj)

            campaign_obj.last_saved_state = CAMPAIGN_SETTINGS_STATE
            campaign_obj.save()

            selected_app_id = ""
            if caller_id_objs:
                selected_app_id = caller_id_objs[0].app_id
                if caller_id_objs.filter(caller_id=trigger_setting["caller_id"]):
                    selected_app_id = caller_id_objs.filter(caller_id=trigger_setting["caller_id"])[0].app_id

            return render(request, "CampaignApp/trigger_settings.html", {
                "campaign_channels": campaign_channels,
                "selected_bot_obj": bot_obj,
                "campaign_id": campaign_id,
                "campaign_objs": campaign_objs,
                "channel": campaign_obj.channel.name,
                "campaign_obj": campaign_obj,
                "trigger_setting": trigger_setting,
                "caller_id_objs": caller_id_objs,
                "bot_pk": bot_pk,
                "selected_app_id": selected_app_id
            })
        else:
            return redirect("/campaign/unauthorised/")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error TriggerSettingsPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


"""

VoiceBotReviewPage() : Render Voice Bot Review Page

"""


@login_required(login_url="/chat/login")
def VoiceBotReviewPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        if request.user in bot_obj.users.all():
            try:
                campaign_id = request.GET['campaign_id']
                campaign_obj = Campaign.objects.get(
                    pk=int(campaign_id), bot=bot_obj, is_deleted=False)
            except Exception:
                return redirect("/campaign/create-campaign/?bot_pk=" + str(bot_pk))

            campaign_objs = Campaign.objects.filter(
                bot=bot_obj, is_deleted=False)

            valid_data_obj = check_campaign_current_page_valid(
                CAMPAIGN_VB_REVIEW_STATE, campaign_obj)

            if valid_data_obj["is_valid"] == False:
                last_saved_page_url = get_last_saved_page_url(
                    valid_data_obj["last_saved_state"], bot_pk, campaign_id)
                return HttpResponseRedirect(last_saved_page_url)

            if check_campaign_in_progress(campaign_obj):
                return redirect("/campaign/unauthorised/?campaign=progress")

            campaign_channels = CampaignChannel.objects.filter(
                is_deleted=False)

            caller_ids = VoiceBotCallerID.objects.filter(bot=bot_obj)

            voice_bot_obj = check_and_create_trigger_setting(
                campaign_obj, CampaignVoiceBotSetting, VoiceBotRetrySetting)

            trigger_setting = parse_trigger_settings(voice_bot_obj)

            user_details, _ = get_user_details_from_batch(
                campaign_obj.batch, CampaignFileAccessManagement)

            mob_numbers = []
            for user_detail in user_details:
                mob_numbers.append(user_detail[0])

            campaign_obj.last_saved_state = CAMPAIGN_VB_REVIEW_STATE
            campaign_obj.save()

            bot_channel_obj = BotChannel.objects.filter(bot=bot_obj, channel=Channel.objects.filter(name="Voice").first()).first()
            voice_bot_config_obj = VoiceBotConfiguration.objects.filter(bot_channel=bot_channel_obj).first()

            api_key = ""
            api_token = ""
            sid = ""

            if voice_bot_config_obj:
                api_key = voice_bot_config_obj.api_key
                api_token = voice_bot_config_obj.api_token
                sid = voice_bot_config_obj.api_sid

            app_id = ""
            selected_caller_obj = caller_ids.filter(caller_id=trigger_setting["caller_id"]).first()
            if selected_caller_obj:
                app_id = selected_caller_obj.app_id

            return render(request, "CampaignApp/voice_bot_review.html", {
                "campaign_channels": campaign_channels,
                "selected_bot_obj": bot_obj,
                "campaign_id": campaign_id,
                "campaign_objs": campaign_objs,
                "channel": campaign_obj.channel.name,
                "campaign_obj": campaign_obj,
                "trigger_setting": trigger_setting,
                "caller_ids": caller_ids,
                "bot_pk": bot_pk,
                "mob_numbers": mob_numbers,
                "api_key": api_key,
                "api_token": api_token,
                "sid": sid,
                "app_id": app_id,
            })
        else:
            return redirect("/campaign/unauthorised/")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error VoiceBotReviewPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


class TrackEventProgressAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["data"])
            data = json.loads(data)
            event_progress_id = data['event_progress_id']

            event_obj = CampaignEventProgress.objects.get(pk=event_progress_id)

            if event_obj:

                response['event_progress'] = event_obj.event_progress
                response['is_completed'] = event_obj.is_completed
                response['is_toast_displayed'] = event_obj.is_toast_displayed
                response['is_failed'] = event_obj.is_failed
                response['event_info'] = json.loads(event_obj.event_info)
                response['failed_message'] = event_obj.failed_message

                if event_obj.is_completed or event_obj.is_failed:
                    event_obj.is_toast_displayed = True
                    event_obj.save()

                response['status'] = 200
            else:
                response['status'] = 300

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TrackEventProgressAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


TrackEventProgress = TrackEventProgressAPI.as_view()


@login_required(login_url="/chat/login")
def CampaignAPIDocumentation(request):
    try:
        selected_bot_obj = None
        if "bot_pk" in request.GET:
            selected_bot_id = request.GET["bot_pk"]
            selected_bot_obj = Bot.objects.filter(id=int(selected_bot_id), is_deleted=False).first()
        else:
            selected_bot_obj = Bot.objects.filter(users__in=[request.user], is_deleted=False).first()
        
        if not selected_bot_obj:
            return render(request, 'CampaignApp/unauthorised.html')
        
        return render(request, 'CampaignApp/campaign_api_documentation.html', {
            "selected_bot_obj": selected_bot_obj,
        })
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CampaignAPIDocumentation ! %s %s",
                     str(e), str(exc_tb.tb_lineno))
        return HttpResponseRedirect("/chat/login/")


class SaveAttachmentDetailsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response['message'] = 'Internal Server Error'
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_obj = Campaign.objects.filter(pk=data.get('campaign_id')).first()
            if request.user not in campaign_obj.bot.users.all():
                response['message'] = 'You are not authorised to save campaign for this bot.'
            else:
                CampaignTemplateVariable.objects.filter(campaign=campaign_obj).update(attachment_details=json.dumps(data))
                response['status'] = 200
                response['message'] = 'Data saved successfully'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveAttachmentDetailsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
        
        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAttachmentDetails = SaveAttachmentDetailsAPI.as_view()


class SendTestCampaignAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response['message'] = 'Internal Server Error'
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_wsp_id = data.get('bot_wsp_id')
            campaign_id = data.get('campaign_id')
            campaign_obj = Campaign.objects.filter(pk=campaign_id)
            campaign_obj_query = campaign_obj.first()
            if request.user not in campaign_obj_query.bot.users.all():
                response['message'] = 'You are not authorised to save campaign for this bot.'
            else:
                response, campaign_wsp_config_meta, _ = get_campaign_wsp_config_meta(
                    campaign_obj_query, bot_wsp_id, response, True)
                campaign_wsp_config_meta['is_test_campaign'] = True
                campaign_obj.update(times_campaign_tested=F(
                    'times_campaign_tested') + 1)
                test_data = {}
                test_data['total_audience_to_test'] = data.get('max_row')
                execute_send_campaign(campaign_wsp_config_meta, campaign_id, Campaign, CampaignFileAccessManagement,
                                      CampaignAudience, CampaignAudienceLog, CampaignAnalytics, CampaignTemplateVariable, test_data)
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SendTestCampaignAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SendTestCampaign = SendTestCampaignAPI.as_view()
