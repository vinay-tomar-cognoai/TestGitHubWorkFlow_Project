from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect

# Django REST framework
from rest_framework.response import Response
# from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.contrib.sessions.models import Session

"""For user authentication"""
from django.contrib.auth import authenticate

from CampaignApp.utils import *
from CampaignApp.utils_external_api import *
from CampaignApp.models import *
from EasyChatApp.models import *
from CampaignApp.constants import *

from CampaignApp.views_api_integration import *
from CampaignApp.views_tag_audience import *
from CampaignApp.utils_validation import *

import sys
import func_timeout
from datetime import datetime, date, timedelta
import re

# Logger
import logging
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


"""

GetAuthToken() : Logout user from the current session

"""


class GetAuthTokenAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            try:
                data = request.data
            except:
                response['status'] = 400
                response['message'] = "Malformed request body."
                return Response(data=response, status=response['status'])

            username = ""
            if 'username' in data:
                username = data['username']

            password = ""
            if 'password' in data:
                password = data['password']

            bot_id = ""
            if 'bot_id' in data:
                bot_id = data['bot_id']
            
            if username == "":
                response['status'] = 400
                response['message'] = "Invalid username!"
                return Response(data=response, status=400)

            if password == "":
                response['status'] = 400
                response['message'] = "Invalid password!"
                return Response(data=response, status=400)

            if bot_id == "":
                response['status'] = 400
                response['message'] = 'Invalid bot id!'
                return Response(data=response, status=400)

            try:
                user = authenticate(username=username, password=password)
                if user == None or user.is_chatbot_creation_allowed != "1":
                    response['status'] = 401
                    response['message'] = 'Invalid username or password!'
                    return Response(data=response, status=401)

                user_obj = User.objects.get(username=username)
                
                try:
                    malformed_bot_id = False
                    bot_id = int(bot_id)
                    if bot_id < 1:
                        malformed_bot_id = True
                except:
                    malformed_bot_id = True
                
                if malformed_bot_id:
                    response['status'] = 422
                    response['message'] = 'Invalid bot id (Bot id should be a number greater than 0)!'
                    return Response(data=response, status=422)

                bot_objs = Bot.objects.filter(pk=bot_id, users__in=[user_obj], is_uat=True, is_deleted=False)
                if bot_objs.exists():
                    bot_obj = bot_objs.first()
                    auth_token_obj = CampaignAuthToken.objects.create(bot=bot_obj, user=user_obj)
                    response['auth_token'] = auth_token_obj.token
                    response['message'] = "Success"
                    response['status'] = 200
                else:
                    response['status'] = 404
                    response['message'] = 'Bot not found!'
                    
                return Response(data=response, status=response['status'])
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("GetAuthTokenAPI check user: %s at %s", e, str(
                    exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetAuthTokenAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return Response(data=response, status=response['status'])


GetAuthToken = GetAuthTokenAPI.as_view()


"""

CreateExternalNewCampaignAPI() : create new campaign and template API

"""


class CreateExternalNewCampaignAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
     
        try:
            try:
                data = request.data
            except:
                response['status'] = 400
                response['status_message'] = "Malformed request body."
                return Response(data=response, status=response['status'])

            auth_token = ""
            if "authorization" in data:
                auth_token = data["authorization"]
            
            response, auth_token_obj = validate_external_auth_token(auth_token, response)

            if not auth_token_obj:
                return Response(data=response, status=401)

            bot_id = auth_token_obj.bot.pk
            try:
                campaign_name = data["campaign_name"]
                campaign_name = strip_html_tags(campaign_name)
                campaign_name = remo_special_tag_from_string(campaign_name)
                if bool(re.match('^[\W_ ]+$', campaign_name)):
                    response['status'] = 400
                    response['status_message'] = 'Campaign name can\'t only contain special characters!'
                    return Response(data=response, status=400)

                if campaign_name == "":
                    response['status'] = 400
                    response['status_message'] = 'Invalid Campaign Name!'
                    return Response(data=response, status=400)
            except:
                response['status'] = 400
                response['status_message'] = 'Invalid Campaign Name!'
                return Response(data=response, status=400)
            
            response["campaign_name"] = campaign_name
            try:
                channel_id = data["channel_id"]
                channel_obj = CampaignChannel.objects.get(pk=int(channel_id))
            except:
                response['status'] = 400
                response['status_message'] = 'Invalid channel Id!'
                return Response(data=response, status=400)

            bot_obj = Bot.objects.get(pk=int(bot_id))

            existing_campaign_obj = Campaign.objects.filter(
                name__iexact=campaign_name, bot=bot_obj, is_deleted=False).first()

            response["status"] = 200
            if existing_campaign_obj:
                response['status'] = 409
                response['status_message'] = 'Campaign with the same name already exists with campaign id ' + str(existing_campaign_obj.pk)
            else:
                if channel_obj.value == "whatsapp":
                    status, message, template_obj = add_template_external_api(data, bot_obj)
                elif channel_obj.value == "voicebot":
                    status, message, campaign_obj = add_template_external_api_voicebot(data, bot_obj, campaign_name, channel_obj)
                elif channel_obj.value == "rcs":
                    status, message, template_obj = add_template_external_api_rcs(data, bot_obj)
            
                response["status"] = status
                response["status_message"] = message

                if channel_obj.value != "voicebot":
                    if template_obj == None:
                        response['status'] = 400
                        response['status_message'] = message
                        return Response(data=response, status=response["status"])

                    response["status_message"] = "Campaign created successfully"
                    if status == 202:
                        response["status"] = 200
                        response["status_message"] = message

                    if channel_obj.value == "whatsapp":
                        campaign_obj = Campaign.objects.create(
                            name=campaign_name,
                            channel=channel_obj,
                            bot=bot_obj,
                            campaign_template=template_obj,
                            status=CAMPAIGN_DRAFT
                        )
                    elif channel_obj.value == "rcs":
                        campaign_obj = Campaign.objects.create(
                            name=campaign_name,
                            channel=channel_obj,
                            bot=bot_obj,
                            campaign_template_rcs=template_obj,
                            status=CAMPAIGN_DRAFT
                        )

                if CampaignAPI.objects.filter(campaign=campaign_obj).count() == 0:
                    CampaignAPI.objects.create(campaign=campaign_obj)
                
                if campaign_obj:
                    response["campaign_id"] = str(campaign_obj.pk)
                else:
                    response["campaign_id"] = "-"

            return Response(data=response, status=response["status"])
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateNewCampaignAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status"] = "500"
            response["status_message"] = "Internal server Error"

        return Response(data=response, status=response["status"])


CreateExternalNewCampaign = CreateExternalNewCampaignAPI.as_view()


"""

SendCampaignMessageExternalAPI() : Creates batch and send message to the clients.

"""


class SendCampaignMessageExternalAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
     
        try:
            try:
                data = request.data
            except:
                response['status'] = 400
                response['status_message'] = "Malformed request body."
                return Response(data=response, status=response['status'])

            auth_token = ""
            if "authorization" in data:
                auth_token = data["authorization"]
            
            response, auth_token_obj = validate_external_auth_token(auth_token, response)

            if not auth_token_obj:
                return Response(data=response, status=401)

            bot_id = auth_token_obj.bot.pk
            bot_obj = Bot.objects.get(pk=int(bot_id))
            campaign_id = ""
            if "campaign_id" in data:
                campaign_id = data["campaign_id"]

            try:
                campaign_obj = Campaign.objects.get(pk=int(campaign_id), is_deleted=False)
                if campaign_obj.bot != bot_obj:
                    response['status'] = 400
                    response['status_message'] = 'Token does not matches with campaign id!'
                    return Response(data=response, status=400) 

                status_to_check = ['complete', 'progress', 'schedule', 'fail']
                if any(status in campaign_obj.status for status in status_to_check):
                    response['status'] = 409
                    response['status_message'] = 'This campaign is already ' + campaign_obj.status + '.'
                    return Response(data=response, status=409)

            except:
                response['status'] = 400
                response['status_message'] = 'Invalid Campaign Id!'
                return Response(data=response, status=400) 

            username = auth_token_obj.user

            clients_data = data.get("client_data")
            if clients_data and isinstance(clients_data, list):
                if len(clients_data) > EXTERNAL_CAMPAIGN_MAXIMUM_AUDIENCE_BATCH_LIMIT:
                    response['status'] = 400
                    response['status_message'] = 'Client\'s data is too large. A maximum of 40,000 entries can be sent at a time.'
                    return Response(data=response, status=400) 
            else:
                response['status'] = 400
                response['status_message'] = 'Please enter valid client data.'
                return Response(data=response, status=400) 

            if campaign_obj.channel.value == "whatsapp":
                campaign_template_obj = campaign_obj.campaign_template

            elif campaign_obj.channel.value == "voicebot":
                campaign_template_obj = CampaignVoiceBotSetting.objects.filter(campaign=campaign_obj)
                if campaign_template_obj.exists():
                    campaign_template_obj = campaign_template_obj.first()

            elif campaign_obj.channel.value == "rcs":       
                campaign_template_obj = campaign_obj.campaign_template_rcs

            try:
                status, message, rcs_enabled_user_list = func_timeout.func_timeout(
                    EXTERNAL_CAMPAIGN_APP_MAX_TIMEOUT_LIMIT, add_batch_external_api_and_send_message, args=[data, bot_obj, username, campaign_obj])

            except func_timeout.FunctionTimedOut:
                response['status'] = 408
                response['status_message'] = 'Request took longer than expected. Please try again later.'
                return Response(data=response, status=408) 

            response["status"] = status
            response["status_message"] = message
            if len(rcs_enabled_user_list) > 0:
                response["rcs_enabled_user_list"] = rcs_enabled_user_list

            return Response(data=response, status=response["status"])       

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateNewCampaignAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status"] = 500
            response["status_message"] = "Internal server Error"

        return Response(data=response, status=response["status"])


SendCampaignMessageExternal = SendCampaignMessageExternalAPI.as_view()


"""

GetCampaignReportsExternalAPI() : Fetches report in relation to specific campaign

"""


class GetCampaignReportsExternalAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
     
        try:
            try:
                data = request.data
            except:
                response['status'] = 400
                response['status_message'] = "Malformed request body."
                return Response(data=response, status=response['status'])

            auth_token = ""
            if "authorization" in data:
                auth_token = data["authorization"]

            response, auth_token_obj = validate_external_auth_token(auth_token, response)

            if not auth_token_obj:
                return Response(data=response, status=401)
                
            bot_id = auth_token_obj.bot.pk
            user = auth_token_obj.user
            bot_obj = Bot.objects.get(pk=int(bot_id))
            campaign_id = ""
            if "campaign_id" in data:
                campaign_id = data["campaign_id"]

            try:
                campaign_obj = Campaign.objects.get(pk=int(campaign_id), is_deleted=False)
                if campaign_obj.bot != bot_obj:
                    response['status'] = 400
                    response['status_message'] = 'Token does not matches with campaign id!'
                    return Response(data=response, status=400) 

            except:
                response['status'] = 400
                response['status_message'] = 'Invalid Campaign Id!'
                return Response(data=response, status=400) 
            phone_number = data.get('phone_number', '').strip()
            phone_number = validation_obj.removing_phone_non_digit_element(phone_number)
            phone_number = remo_html_from_string(str(phone_number))
            phone_number = remo_special_tag_from_string(phone_number)
            email_id = data.get('email_id')
            if email_id and not validation_obj.is_valid_email(email_id):
                response['status'] = 400
                response['status_message'] = "Please enter a valid email id."
                return Response(data=response, status=400) 
            users_parameter_data = {
                'audience_unique_id': data.get('unique_id', ''),
                'phone_number': phone_number,
                'email_id': email_id,
                'user': user
            }
            if campaign_obj.channel.value == "whatsapp":
                status, message, json_obj = add_campaign_details_in_reports_external(campaign_obj, users_parameter_data)
            elif campaign_obj.channel.value == "voicebot":
                status, message, json_obj = add_campaign_details_in_reports_external_voicebot(campaign_obj, users_parameter_data)
            elif campaign_obj.channel.value == "rcs":
                status, message, json_obj = add_campaign_details_in_reports_external_rcs(campaign_obj, users_parameter_data)

            response["reports"] = json_obj
            response["status"] = status
            response["status_message"] = message

            return Response(data=response, status=response["status"])       

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetCampaignReportsExternalAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status"] = "500"
            response["status_message"] = "Internal server Error"

        return Response(data=response, status=response["status"])


GetCampaignReportsExternal = GetCampaignReportsExternalAPI.as_view()


"""

CreateEventBasedWhatsappCampaignAPI() : create new campaignm, template and batch API

"""


class CreateEventBasedWhatsappCampaignAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Unable to Create Campaign. This is an internal error." 
        try:
            try:
                data = request.data
            except:
                response['status'] = 400
                response['status_message'] = "Malformed request body."
                return Response(data=response, status=response['status'])

            auth_token = data.get("authorization", "")
            response, auth_token_obj = validate_external_auth_token(auth_token, response)
            if not auth_token_obj:
                return Response(data=response, status=401)

            campaign_name = data.get("campaign_name", "")
            status, campaign_name = is_valid_campign_batch_template_name(campaign_name)
            if status == 400:
                response["status"] = 400
                response["status_message"] = "Invalid Campaign Name!"
                return Response(data=response, status=response["status"])

            batch_name = data.get("batch_name", "")
            status, batch_name = is_valid_campign_batch_template_name(batch_name)
            if status == 400:
                response["status"] = 400
                response["status_message"] = "Invalid Batch Name!"
                return Response(data=response, status=response["status"])

            bot_obj = auth_token_obj.bot
            existing_campaign_obj = Campaign.objects.filter(
                name__iexact=campaign_name, bot=bot_obj, is_deleted=False).first()

            if existing_campaign_obj:
                response['status'] = 409
                response['status_message'] = 'Campaign with the same name already exists with campaign id ' + str(existing_campaign_obj.pk)
            else:
                status, message, template_obj = add_template_external_api(data, bot_obj)
                response["status"] = status
                response["status_message"] = message
                
                if template_obj == None:
                    response['status'] = 400
                    response['status_message'] = message
                    return Response(data=response, status=response["status"])

                response["status_message"] = "Campaign created successfully"
                if status == 202:
                    response["status"] = 200
                    response["status_message"] = "Campaign created successfully but template with same name already existed."

                channel_obj = CampaignChannel.objects.filter(value="whatsapp").first()
                status, message, campaign_batch_obj = save_batch_data(0, 0, auth_token_obj.user, bot_obj, batch_name, channel_obj)
                if campaign_batch_obj == None:
                    response["status"] = status
                    response["status_message"] = message
                    return Response(data=response, status=response["status"])
                
                campaign_obj = Campaign.objects.create(name=campaign_name, channel=channel_obj, bot=bot_obj, campaign_template=template_obj, status=CAMPAIGN_DRAFT,
                                                       batch=campaign_batch_obj)
                campaign_batch_obj.campaigns.add(campaign_obj)
                campaign_batch_obj.save()

                if not CampaignAPI.objects.filter(campaign=campaign_obj).exists():
                    CampaignAPI.objects.create(campaign=campaign_obj)

                response["campaign_id"] = str(campaign_obj.pk)

            return Response(data=response, status=response["status"])
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateEventBasedWhatsappCampaignAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return Response(data=response, status=response["status"])


CreateEventBasedWhatsappCampaign = CreateEventBasedWhatsappCampaignAPI.as_view()


"""

SendEventBasedTriggeredCampaignAPI() : This is a single event based trigger api to send campaign to 1 user max based
on an event.

"""


class SendEventBasedTriggeredWhatsappCampaignAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
     
        try:
            try:
                data = request.data
            except:
                response['status'] = 400
                response['status_message'] = "Malformed request body."
                return Response(data=response, status=response['status'])

            auth_token = ""
            if "authorization" in data:
                auth_token = data["authorization"]

            response, auth_token_obj = validate_external_auth_token(auth_token, response)

            if not auth_token_obj:
                return Response(data=response, status=401)

            bot_obj = auth_token_obj.bot

            if bot_obj.is_deleted:
                response['status'] = 404
                response['status_message'] = 'Bot not found!'
                return Response(data=response, status=400)
            
            # send single event based campaign
            campaign_id = data.get("campaign_id", "")
            try:
                campaign_obj = Campaign.objects.filter(pk=int(campaign_id), is_deleted=False).first()
                if campaign_obj.bot != bot_obj:
                    response['status'] = 400
                    response['status_message'] = 'Token does not matches with campaign id!'
                    return Response(data=response, status=400)
            except:
                response['status'] = 400
                response['status_message'] = 'Invalid Campaign Id!'
                return Response(data=response, status=400)   

            status, response = add_single_batch_and_send_message_api(data, campaign_obj)
            response = response
            response["status"] = status

            return Response(data=response, status=response["status"])   

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SendEventBasedTriggeredWhatsappCampaignAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status"] = "500"
            response["status_message"] = "Internal server Error"

        return Response(data=response, status=response["status"])


SendEventBasedTriggeredWhatsappCampaign = SendEventBasedTriggeredWhatsappCampaignAPI.as_view()


"""

GetEventBasedTriggeredCampaignReportsAPI() : Fetches report in relation to the given params

"""


class GetEventBasedTriggeredCampaignReportsAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
     
        try:
            try:
                data = request.data
            except:
                response['status'] = 400
                response['status_message'] = "Malformed request body."
                return Response(data=response, status=response['status'])

            validation_obj = CampaignInputValidation()
            auth_token = ""
            if "authorization" in data:
                auth_token = data["authorization"]

            response, auth_token_obj = validate_external_auth_token(auth_token, response)

            if not auth_token_obj:
                return Response(data=response, status=401)   

            start_date = data.get("start_date", "")
            end_date = data.get("end_date", "")
            date_filter_required = True
            if start_date == "" and end_date == "":
                date_filter_required = False

            start_date_time, end_date_time, error_message_date = validation_obj.get_start_and_end_date_time(start_date, end_date)

            bot_obj = auth_token_obj.bot
            user = auth_token_obj.user
            campaign_id = data.get("campaign_id", "")
            if campaign_id == "":
                response['status'] = 400
                response['status_message'] = 'Please enter a valid campaign id!'
                return Response(data=response, status=400) 
            
            json_obj = {}
            try:
                campaign_obj = Campaign.objects.get(pk=int(campaign_id), is_deleted=False)
                if campaign_obj.bot != bot_obj:
                    response['status'] = 400
                    response['status_message'] = 'Token does not matches with campaign id!'
                    return Response(data=response, status=400) 

            except:
                response['status'] = 400
                response['status_message'] = 'Invalid Campaign Id!'
                return Response(data=response, status=400) 
                
            if date_filter_required:
                if error_message_date:
                    response["status"] = 400
                    response["status_message"] = error_message_date
                    return Response(data=response, status=400)
            
            try:
                status, message, json_obj = func_timeout.func_timeout(
                    EXTERNAL_CAMPAIGN_APP_MAX_TIMEOUT_LIMIT, add_single_api_campaign_details_in_reports, args=[data, campaign_obj, date_filter_required, start_date_time, end_date_time, user]) 
            except func_timeout.FunctionTimedOut:
                response['status'] = 408
                response['status_message'] = 'Request timed out!'
                return Response(data=response, status=400) 
                
            response["reports"] = json_obj
            response["status"] = status
            response["status_message"] = message

            return Response(data=response, status=response["status"])       

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetCampaignReportsExternalAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status"] = "500"
            response["status_message"] = "Internal server Error"

        return Response(data=response, status=response["status"])


GetEventBasedTriggeredCampaignReports = GetEventBasedTriggeredCampaignReportsAPI.as_view()
