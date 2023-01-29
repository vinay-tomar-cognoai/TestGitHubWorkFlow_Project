# Django REST framework
from rest_framework.response import Response
# from rest_framework import status
from rest_framework.views import APIView

from CampaignApp.utils import get_unique_template_variable_body, get_value_from_cache, open_file, set_value_to_cache
from CampaignApp.constants import *
from CampaignApp.models import Campaign, CampaignAudienceLog, CampaignAudience, CampaignBotWSPConfig

import sys
import json
import logging

from CampaignApp.utils_lambda import *
from EasyChatApp.models import Bot, Channel, Language, MISDashboard, Profile

logger = logging.getLogger(__name__)

log_param = {'AppName': 'Campaign', 'user_id': 'None',
             'source': 'None', 'channel': 'WhatsApp', 'bot_id': 'None'}


class LambdaPushMessageAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            if data['event_name'] == "INITIAL_PUSH_TRIGGER_EVENT":
                response["status"] = 200
                response["message"] = "Initial push trigger event verified successfully"
                return Response(data=response)

            campaign_id = data['campaign_id']
            bot_wsp_id = data['bot_wsp_id']
            campaign_obj = Campaign.objects.get(pk=int(campaign_id))
            
            parameter = data['parameter']
            audience_id = data['audience_id']
            audience_obj = CampaignAudience.objects.get(
                pk=int(audience_id))
            campaign_aud_log = CampaignAudienceLog.objects.filter(
                campaign=campaign_obj, audience=audience_obj)
            if campaign_aud_log.exists():
                response["status"] = 200
                response["message"] = "Message processed successfully"
                return Response(data=response)
                    
            audience_log_obj = CampaignAudienceLog.objects.create(
                audience=audience_obj, campaign=campaign_obj)
                
            code = get_value_from_cache(CACHE_KEY_CAMPAIGN_BOT_WSP_CONFIG, bot_wsp_id)

            if not code:
                code = CampaignBotWSPConfig.objects.get(pk=bot_wsp_id).code
                set_value_to_cache(CACHE_KEY_CAMPAIGN_BOT_WSP_CONFIG, bot_wsp_id, code)

            processor_check_dictionary = {'open': open_file}

            exec(str(code), processor_check_dictionary)
            code_response = processor_check_dictionary['f'](
                json.dumps(parameter))

            if code_response.get('response') and 'request_id' in code_response['response']:
                audience_log_obj.recepient_id = code_response['response']['request_id']
            else:
                audience_log_obj.is_failed = True

            if code_response.get('request') and code_response.get('response'):
                audience_log_obj.request = json.dumps(code_response['request'])
                audience_log_obj.response = json.dumps(
                    code_response['response'])

            audience_log_obj.is_processed = True
            audience_log_obj.save(
                update_fields=["recepient_id", "request", "response", "is_failed", "is_processed"])
            response["status"] = 200
            response["message"] = "Message processed successfully."

        except Exception as e:  # noqa: F841
            response["message"] = str(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LambdaPushMessageAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        logger.info("LambdaPushMessageAPI: %s", response,
                    extra={'AppName': 'Campaign'})
        return Response(data=response)

LambdaPushMessage = LambdaPushMessageAPI.as_view()


class LambdaPushDeliveryPacketsAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            request_packet = data['request_packet']
            delivery_status_updated = data['delivery_status_updated']
            
            if delivery_status_updated:
                logger.error("INCOMING_DELIVERY_PACKET WA WEBHOOK: %s",
                             str(request_packet), extra=log_param)
                # extra = ""
                # if "extra" in request_packet["statuses"][0]:
                #     extra = request_packet["statuses"][0]["extra"]
                    
                try:
                    mobile_number = request_packet["statuses"][0]["recipient_id"]
                    request_id = request_packet["statuses"][0]["id"]
                    status = request_packet["statuses"][0]["status"]
                    timestamp = request_packet["statuses"][0]["timestamp"]

                    BOT_ID = request_packet["bot_id"]

                    if status == "delivered" or status == "read":
                        check_and_create_session_if_required(mobile_number, BOT_ID)

                    # if extra != "Allincall" and extra != "":
                    #     try:
                    #         campaign = Campaign.objects.get(
                    #             name=extra, partner=extra)
                    #     except Exception as e:
                    #         campaign = Campaign.objects.create(
                    #             name=extra, status="in_progress", partner=extra)
                    #         logger.info("Creating campaign: %s",
                    #                     str(e), extra=log_param)
                    #     try:
                    #         audience = CampaignAudience.objects.get(
                    #             audience_id=mobile_number)
                    #     except Exception as e:
                    #         audience = CampaignAudience.objects.create(
                    #             audience_id=mobile_number)
                    #         logger.info("Creating audience: %s",
                    #                     str(e), extra=log_param)
                    #     try:
                    #         audience_log_obj = CampaignAudienceLog.objects.get(
                    #             recepient_id=request_id)
                    #     except Exception as e:
                    #         audience_log_obj = CampaignAudienceLog.objects.create(
                    #             recepient_id=request_id, campaign=campaign, audience=audience)
                    #         logger.info("Creating audience_log_obj: %s",
                    #                     str(e), extra=log_param)

                    normal_timestamp = convert_timestamp_to_normal(int(timestamp))

                    audience_log_obj = CampaignAudienceLog.objects.get(
                        recepient_id=request_id)
                    campaign = audience_log_obj.campaign

                    if status == "sent" and audience_log_obj.is_sent == False:
                        audience_log_obj.is_sent = True
                        audience_log_obj.sent_datetime = normal_timestamp
                        audience_log_obj.save(update_fields=['is_sent', 'sent_datetime'])

                    if status == "delivered" and audience_log_obj.is_delivered == False:
                        update_sent = False
                        if audience_log_obj.is_sent == False:
                            audience_log_obj.is_sent = True
                            audience_log_obj.sent_datetime = normal_timestamp
                            update_sent = True

                        audience_log_obj.is_delivered = True
                        audience_log_obj.delivered_datetime = normal_timestamp
                        mobile = str(request_packet["statuses"][0]["recipient_id"])
                        bot_obj = Bot.objects.get(pk=int(BOT_ID), is_deleted=False)
                        session_id, _, is_business_initiated_session = get_session_id_based_on_user_session(
                            mobile, BOT_ID, True)

                        user_profile_obj = Profile.objects.filter(
                            user_id=str(mobile), bot=bot_obj).first()
                        if user_profile_obj and user_profile_obj.selected_language:
                            user_selected_language = user_profile_obj.selected_language
                        else:
                            try:
                                lang_src = get_language_from_campaign_template_string(campaign.campaign_template.language.title)
                                user_selected_language = Language.objects.filter(lang=lang_src)
                                if user_selected_language.exists() and is_this_language_supported_by_bot(bot_obj, lang_src, Channel.objects.get(name="WhatsApp")):
                                    user_selected_language = user_selected_language.first()
                                else:
                                    user_selected_language = Language.objects.filter(lang="en").first()
                            except:
                                logger.info("get_language_from_campaign_template_string failed: using default en", extra=log_param)
                                user_selected_language = Language.objects.filter(lang="en").first()

                        if not user_profile_obj:
                            Profile.objects.create(user_id=mobile, bot=bot_obj, selected_language=user_selected_language)
                        try:
                            campaign_request_packet = json.loads(
                                audience_log_obj.request)
                            if not isinstance(campaign_request_packet, dict):
                                campaign_request_packet = json.loads(
                                    campaign_request_packet)
                            response_json = {'response': {}}
                            response_json['response']['is_campaign'] = True
                            campaign_template_obj = campaign.campaign_template
                            campaign_message_body = str(
                                campaign_template_obj.template_body)
                            if '{{' in campaign_message_body:
                                template_variables = []
                                if campaign_request_packet['template']['components'][0]['type'] == 'body':
                                    template_variables = campaign_request_packet[
                                        'template']['components'][0]['parameters']
                                elif campaign_request_packet['template']['components'][1]['type'] == 'body':
                                    template_variables = campaign_request_packet[
                                        'template']['components'][1]['parameters']
                                temp_var = []
                                for variables in template_variables:
                                    temp_var.append(variables.get('text'))
                                template_variables = temp_var
                                campaign_message_body = get_unique_template_variable_body(
                                    campaign_message_body, template_variables)
                                campaign_message_body = campaign_message_body.replace(
                                    "{{", '').replace("}}", '')
                            response_json = campaign_json_response_creator(campaign_template_obj, campaign_message_body, campaign_request_packet, response_json)            
                            response_json = json.dumps(response_json)
                            MISDashboard.objects.create(bot=bot_obj,
                                                        message_received="",
                                                        bot_response=campaign_message_body,
                                                        user_id=mobile,
                                                        response_json=response_json,
                                                        session_id=session_id,
                                                        channel_name="WhatsApp",
                                                        is_business_initiated_session=is_business_initiated_session,
                                                        selected_language=user_selected_language)
                        except Exception as E:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Error in creating Campaign MIS: %s at %s", str(
                                E), str(exc_tb.tb_lineno), extra=log_param)
                        
                        if update_sent:
                            audience_log_obj.save(update_fields=['is_sent', 'sent_datetime', 'is_delivered', 'delivered_datetime'])
                        else:
                            audience_log_obj.save(update_fields=['is_delivered', 'delivered_datetime'])

                    if status == "read" and audience_log_obj.is_read == False:

                        if audience_log_obj.is_sent == False:
                            audience_log_obj.is_sent = True
                            audience_log_obj.sent_datetime = normal_timestamp

                        if audience_log_obj.is_delivered == False:
                            audience_log_obj.is_delivered = True
                            audience_log_obj.delivered_datetime = normal_timestamp

                        audience_log_obj.is_read = True
                        audience_log_obj.read_datetime = normal_timestamp
                        audience_log_obj.save(update_fields=['is_sent', 'sent_datetime', 'is_delivered', 'delivered_datetime', 'is_read', 'read_datetime'])

                    if status == "failed":
                        audience_log_obj.is_sent = False
                        audience_log_obj.is_delivered = False
                        audience_log_obj.is_failed = True
                        
                        error_details = request_packet.get("statuses")[0].get('errors', [{"title": "Whatsapp Internal error."}])[0].get('title', "Whatsapp Internal error.")
                        failure_response = {"errors": [{"code": 500, "title": error_details, "details": "Whatsapp Internal error."}]}
                        audience_log_obj.response = json.dumps(failure_response)
                        audience_log_obj.save(update_fields=['is_sent', 'is_delivered', 'is_failed', 'response'])

                    response["mobile_number"] = request_packet["statuses"][0]["recipient_id"]
                except Exception:
                    pass
                response["status"] = 200
                response["message"] = "Request processed successfully."
                logger.info("AmeyoDeliveryCheck: %s",
                            str(response), extra=log_param)

                return Response(data=response)
            
        except Exception as e:  # noqa: F841
            response["message"] = str(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LambdaPushDeliveryPacketsAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        logger.info("LambdaPushDeliveryPacketsAPI: %s", response,
                    extra={'AppName': 'Campaign'})
        return Response(data=response)

LambdaPushDeliveryPackets = LambdaPushDeliveryPacketsAPI.as_view()
