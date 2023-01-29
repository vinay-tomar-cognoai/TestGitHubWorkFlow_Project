import sys
import uuid
import logging
from django.conf import settings
from django.utils import timezone

from oauth2client.service_account import ServiceAccountCredentials
from businessmessages import businessmessages_v1_client as bm_client
from businessmessages.businessmessages_v1_messages import (
    BusinessmessagesConversationsSurveysCreateRequest,
    BusinessMessagesSurvey)
from EasyChatApp.models import GMBDetails, Bot, MISDashboard, Profile, Channel, GBMSurveyDetails

import pytz
tz = pytz.timezone(settings.TIME_ZONE)
logger = logging.getLogger(__name__)


def send_survey_to_customer(user, bot_obj):
    try:
        logger.info("Into send_survey_to_customer For Google My Buisness...", extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': "None", 'channel': 'None', 'bot_id': str(bot_obj.pk)})
        conversation_id = user.user_id
        gmb_obj = GMBDetails.objects.filter(bot=bot_obj).first()

        service_account_location = gmb_obj.gmb_credentials_file_path
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            service_account_location,
            scopes=['https://www.googleapis.com/auth/businessmessages'])

        client = bm_client.BusinessmessagesV1(credentials=credentials)
        survey_id = str(uuid.uuid4().int)
        # Create the survey request
        survey_request = BusinessmessagesConversationsSurveysCreateRequest(surveyId=survey_id,
                                                                           parent='conversations/' + conversation_id, businessMessagesSurvey=BusinessMessagesSurvey())

        # Send the survey
        bm_client.BusinessmessagesV1.ConversationsSurveysService(
            client=client).Create(request=survey_request)

        # on succesfull survey sent update its details
        if GBMSurveyDetails.objects.filter(user_profile=user):
            survey_detail_obj = GBMSurveyDetails.objects.filter(
                user_profile=user).first()
            survey_detail_obj.survery_id = survey_id
            survey_detail_obj.survey_sent_on = timezone.now()
            survey_detail_obj.save()
        else:
            GBMSurveyDetails.objects.create(
                user_profile=user, survey_id=survey_id)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_survey_to_customer %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def check_survey_status_and_send(user, bot_obj):
    try:
        if GBMSurveyDetails.objects.filter(user_profile=user):
            survey_detail_obj = GBMSurveyDetails.objects.filter(
                user_profile=user).first()
            survey_sent_on = survey_detail_obj.survey_sent_on
            survey_sent_on = survey_sent_on.astimezone(
                tz)
            current_time = timezone.now().astimezone(tz)
            available_time = (
                current_time - survey_sent_on).total_seconds()
            last_message_time = user.last_message_date.astimezone(tz)
            # if survey was sent in last 24 hours or before last message was sent then no need to send survey
            if available_time < 24 * 60 * 60 or last_message_time < survey_sent_on:
                return
        send_survey_to_customer(user, bot_obj)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_survey_to_customer %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def check_and_send_gbm_survey():
    try:
        GbmChannel = Channel.objects.get(name="GoogleBusinessMessages")
        user_objs = Profile.objects.filter(channel=GbmChannel)
        for user in user_objs:
            last_updated_time = user.last_message_date.astimezone(
                tz)
            current_time = timezone.now().astimezone(tz)
            available_time = (
                current_time - last_updated_time).total_seconds()
            if available_time > 5 * 60:
                last_message_obj = MISDashboard.objects.filter(
                    user_id=user.user_id).order_by("-pk").first()
                bot_obj = last_message_obj.bot
                check_survey_status_and_send(user, bot_obj)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error gbm survey cronjob %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
