from EasyChatApp.models import Profile, Bot, NPS, Channel, Intent, ViberDetails
from datetime import timedelta
from django.utils import timezone
from EasyChatApp.utils import logger
import sys
from django.conf import settings
import pytz
from EasyChatApp.utils_viber import viber_api_configuration, processing_text_and_attachments
from cronjob_scripts.EasyChatAppCronjobUtilityFunctions.utils_cronjob import *
import json


def cronjob():
    cronjob_id = "easychat_csat_viber_cron"
    cronjob_is_running, cronjob_objs = check_if_cronjob_is_running(cronjob_id)
    if cronjob_is_running:
        return
    try:
        logger.info("::::::::::::::::::::::: RUNINNG VIBER CSAT CRONJOB ::::::::::::::::::", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        # CSAT CONSTANTS
        tz = pytz.timezone(settings.TIME_ZONE)
        current_time = timezone.now()
        current_time = current_time.astimezone(tz)
        start_time_diff = 70  # in minutes

        # CSAT VARIABLES
        viber_csat_bots = []

        viber_channel = Channel.objects.get(name="Viber")
        nps_objs = NPS.objects.filter(channel__in=[viber_channel])

        for nps_obj in nps_objs.iterator():
            if nps_obj.bot.is_nps_required:
                viber_csat_bots.append(nps_obj.bot)
        logger.info("Viber CSAT enabled bots ::: %s", str(viber_csat_bots), extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                   'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        for bot in viber_csat_bots:
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
            end_time_diff = nps_obj.viber_nps_time  # in minutes
            bot_csat_flow_name = Intent.objects.filter(
                bots__in=[bot], is_whatsapp_csat=True)
            if bot_csat_flow_name.count() > 0:
                bot_csat_flow_name = bot_csat_flow_name.first().name
                start_time = current_time - timedelta(minutes=start_time_diff)
                end_time = current_time - timedelta(minutes=end_time_diff)
                logger.info(
                    f"CSAT Selecting {bot} users Started {start_time} --- {end_time}", extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                              'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                last_hour_profiles_user_id = Profile.objects.filter(
                    channel=viber_channel,
                    bot=bot,
                    last_message_date__gte=start_time,
                    last_message_date__lte=end_time,
                    is_csat_triggers=False).values_list('user_id', flat=True)

                selected_all_users = last_hour_profiles_user_id

                logger.info(f"CSAT All Selected User {selected_all_users}", extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                   'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                viber_obj = ViberDetails.objects.filter(
                    bot=bot).first()
                if viber_obj:
                    viber_api_token = viber_obj.viber_api_token

                    viber_sender_avatar = None

                    viber_sender_avatar_raw = json.loads(viber_obj.viber_bot_logo)

                    if 'sender_logo' in viber_sender_avatar_raw and len(viber_sender_avatar_raw['sender_logo']) > 0:
                        viber_sender_avatar = viber_sender_avatar_raw['sender_logo'][0]

                    viber_connector = viber_api_configuration(
                        viber_api_token, bot.name, viber_sender_avatar)

                    for user_id in selected_all_users:

                        profile_objs = Profile.objects.filter(
                            user_id=user_id, bot=bot, channel=viber_channel, is_csat_triggers=False, livechat_connected=False)
                        logger.info("CSAT Cronjob mobile: %s", str(profile_objs.count()), extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                                    'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        if profile_objs:

                            try:
                                message = {'type': 'text',
                                            'text': bot_csat_flow_name}
                                profile_objs[0].is_csat_triggers = True
                                profile_objs[0].tree = None
                                profile_objs[0].last_csat_triggered_date = timezone.now(
                                )
                                profile_objs[0].save()
                                processing_text_and_attachments(
                                    viber_connector, message, user_id, viber_api_token, bot, viber_sender_avatar)
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logger.info("In csat_whatsapp cronjob: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                                                        'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In csat_viber cronjob: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                              'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    complete_cronjob_execution(cronjob_objs)

cronjob()
