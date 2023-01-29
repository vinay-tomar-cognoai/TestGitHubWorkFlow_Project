from EasyChatApp.models import Channel, MISDashboard, EasyChatMailerAnalyticsProfile, UserSessionHealth
from EasyChatApp.utils_analytics import return_mis_objects_excluding_blocked_sessions
from EasyChatApp.utils_email_configuration import (get_accuracy_html,
                                                   generate_mail_for_bot_accuracy)
import sys
import json
import datetime
from django.conf import settings
from EasyChatApp.utils import logger


def cronjob():
    try:
        email_configurations = EasyChatMailerAnalyticsProfile.objects.filter(
            is_deleted=False).iterator()
        start_date = (datetime.datetime.now() - datetime.timedelta(1)).date()
        end_date = (datetime.datetime.now() - datetime.timedelta(0)).date()

        for email_config in email_configurations:
            try:
                bot_obj = email_config.bot

                if bot_obj.is_deleted:
                    continue

                email_frequency = json.loads(email_config.email_frequency)

                if 'Daily' not in email_frequency:
                    continue

                if bot_obj.is_email_notifiication_enabled:

                    bot_accuracy_threshold = email_config.bot_accuracy_threshold

                    if bot_accuracy_threshold == None or bot_accuracy_threshold == '':
                        continue
                    else:
                        bot_accuracy_threshold = int(bot_accuracy_threshold)

                    for channel in Channel.objects.filter(is_easychat_channel=True):
                        mis_objs = MISDashboard.objects.filter(
                            creation_date__gte=start_date, creation_date__lt=end_date, bot=bot_obj, channel_name=channel.name)

                        mis_objs = return_mis_objects_excluding_blocked_sessions(mis_objs, UserSessionHealth)

                        total_queries = mis_objs.count()

                        if total_queries > 0:
                            total_unanswered_queries = mis_objs.filter(
                                intent_name=None).count()

                            bot_accuracy = round(
                                (100 * (total_queries - total_unanswered_queries)) / total_queries, 2)

                            if bot_accuracy < float(bot_accuracy_threshold):
                                email_subject = "ACCURACY DROP ALERT for " + \
                                    channel.name + " channel - " + bot_obj.name
                                accuracy_string = get_accuracy_html(
                                    total_queries, total_unanswered_queries, bot_accuracy)

                                email = settings.EMAIL_CSM
                                try:
                                    generate_mail_for_bot_accuracy(bot_obj.name,
                                                                   end_date,
                                                                   accuracy_string,
                                                                   email,
                                                                   email_subject,
                                                                   channel.name)
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    logger.error("Cronjob easychat_bot_accuracy_daily! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                                    continue

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Cronjob easychat_bot_accuracy_daily! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                continue
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob easychat_bot_accuracy_daily! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        pass
