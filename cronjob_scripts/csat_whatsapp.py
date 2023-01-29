from datetime import date, time
from EasyChatApp.constants import WHATSAPP_CSAT_FEEDBACK_ID
from EasyChatApp.models import Profile, WhatsAppWebhook, Q, Bot, MISDashboard, NPS, Channel, Intent, EasyChatCronjobTracker
from cronjob_scripts.EasyChatAppCronjobUtilityFunctions.utils_cronjob import *
from datetime import timedelta
from django.utils import timezone
from EasyChatApp.utils import logger
import math
import random
import datetime as dt
import sys
from django.conf import settings
import pytz
import requests


def cronjob():
    cronjob_id = "easychat_csat_whatsapp_cron"
    cronjob_is_running, cronjob_objs = check_if_cronjob_is_running(cronjob_id)
    if cronjob_is_running:
        return
    try:
        logger.info("::::::::::::::::::::::: RUNINNG CSAT CRONJOB ::::::::::::::::::", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        # CSAT CONSTANTS
        tz = pytz.timezone(settings.TIME_ZONE)
        current_time = timezone.now()
        current_time = current_time.astimezone(tz)
        start_time_diff = 70  # in minutes

        # CSAT VARIABLES
        whatsapp_csat_bots = []

        whatsapp_channel = Channel.objects.get(name="WhatsApp")
        nps_objs = NPS.objects.filter(channel__in=[whatsapp_channel])

        for nps_obj in nps_objs.iterator():
            if nps_obj.bot.is_nps_required:
                whatsapp_csat_bots.append(nps_obj.bot)
        logger.info("Whatsapp CSAT enabled bots ::: %s", str(whatsapp_csat_bots), extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                         'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        for bot in whatsapp_csat_bots:
            nps_obj = NPS.objects.get(bot=bot)
            # clear profiles csat status to default
            logger.info("CSAT reset data to default started", extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                     'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            csat_reset_duration = nps_obj.csat_reset_duration  # in days
            csat_reset_time = current_time.date() - timedelta(days=csat_reset_duration)
            csat_reset_profile = Profile.objects.filter(
                is_csat_triggers=True, last_csat_triggered_date__date__lte=csat_reset_time)
            csat_reset_profile.update(
                is_csat_triggers=False, is_csat_submited=False, last_csat_triggered_date=current_time)
            logger.info("CSAT reset data to default Ended", extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                   'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            # get new csat profiles
            end_time_diff = nps_obj.whatsapp_nps_time  # in minutes
            bot_csat_flow = Intent.objects.filter(
                bots__in=[bot], is_whatsapp_csat=True).first()
            if bot_csat_flow:
                start_time = current_time - timedelta(minutes=start_time_diff)
                end_time = current_time - timedelta(minutes=end_time_diff)
                logger.info(
                    f"CSAT Selecting {bot} users Started {start_time} --- {end_time}", extra={'AppName': 'EasyChat'})
                last_hour_profiles_user_id = Profile.objects.filter(
                    channel=whatsapp_channel,
                    bot=bot,
                    last_message_date__gte=start_time,
                    last_message_date__lte=end_time,
                    is_csat_triggers=False).values_list('user_id', flat=True)

                selected_all_users = last_hour_profiles_user_id

                logger.info(f"CSAT All Selected User {selected_all_users}", extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                   'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                selected_final_users = selected_all_users

                default_bot_id = bot.pk
                whatsapp_webhook_obj = WhatsAppWebhook.objects.filter(
                    bot=Bot.objects.get(pk=default_bot_id))

                logger.info("CSAT Total selected users : %s", str(selected_final_users), extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                                'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                for user_id in selected_final_users:

                    profile_objs = Profile.objects.filter(
                        user_id=user_id, bot=bot, channel=whatsapp_channel, is_csat_triggers=False, livechat_connected=False)
                    logger.info("CSAT Cronjob mobile: %s", str(profile_objs.count()), extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                             'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    if profile_objs:

                        try:
                            dict_obj = {}
                            exec(
                                str(whatsapp_webhook_obj[0].function), dict_obj)
                            profile_objs[0].is_csat_triggers = True
                            profile_objs[0].tree = None
                            profile_objs[0].last_csat_triggered_date = timezone.now(
                            )
                            profile_objs[0].save()
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.info("In csat_whatsapp cronjob: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'EasyChat'})

                        request_packet = {'contacts': [{'profile': {'name': ''}, 'wa_id': user_id}], 'messages': [{'from': user_id, 'id': WHATSAPP_CSAT_FEEDBACK_ID, 'text': {
                            'body': str(bot_csat_flow.pk)}, 'timestamp': '0000000000', 'type': 'csat'}], 'brand_msisdn': '000000000000', 'request_id': WHATSAPP_CSAT_FEEDBACK_ID, 'bot_id': bot.pk}
                        # request_packet = {'mobile': user_id, 'type': 'text', 'text': bot_csat_flow_name,
                        #                   'timestamp': '0000000000000', 'waNumber': '912271872500', 'name': 'Allincall'}
                        response = dict_obj['whatsapp_webhook'](request_packet)

                        logger.info("response: %s", str(response), extra={
                            'AppName': 'Campaign'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In csat_whatsapp cronjob: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat'})

    complete_cronjob_execution(cronjob_objs)


cronjob()
