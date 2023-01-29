# this cronjob will run 3 times a day
# 10 AM
# 2 PM
# 5 PM
# If unanswered is not loading, just run this script once.
from EasyChatApp.models import UserSessionHealth
from EasyChatApp.utils_analytics import return_mis_objects_excluding_blocked_sessions
from cronjob_scripts.EasyChatAppCronjobUtilityFunctions.utils_cronjob import *


def unanswered_queries_cronjob():
    from datetime import datetime, timedelta
    from EasyChatApp.models import Bot, MISDashboard, Channel, UnAnsweredQueries, BotChannel
    from EasyChatApp.utils import logger, get_word_count_from_mis
    from EasyChatApp.utils_bot import get_supported_languages
    from django.conf import settings
    import json
    import sys
    import os
    cronjob_id = "easychat_unanswered_preodic_cron"
    cronjob_is_running, cronjob_objs = check_if_cronjob_is_running(cronjob_id)
    if cronjob_is_running:
        return
    try:
        today = datetime.now()
        for bot in Bot.objects.filter(is_deleted=False):
            supported_languages = get_supported_languages(bot, BotChannel)
            for channel in Channel.objects.filter(is_easychat_channel=True):
                for language in supported_languages:

                    mis_objs = MISDashboard.objects.filter(
                        channel_name=channel.name, bot=bot, status="2", is_intiuitive_query=False, intent_name=None, selected_language=language)
                    mis_objs = return_mis_objects_excluding_blocked_sessions(mis_objs, UserSessionHealth)

                    details_of_unanswered_messages = {}
                    for mis_obj in mis_objs.iterator():
                        mis_obj.status = "1"
                        mis_obj.save()
                        msg_rcvd = mis_obj.get_message_received()
                        if details_of_unanswered_messages.get(msg_rcvd.lower()):
                            details_of_unanswered_messages[msg_rcvd.lower(
                            )] += 1
                        else:
                            details_of_unanswered_messages[msg_rcvd.lower(
                            )] = 1
                    for key, value in details_of_unanswered_messages.items():
                        unanswered_query = UnAnsweredQueries.objects.filter(
                            unanswered_message=key, channel=channel, bot=bot, date=today.date(), selected_language=language)
                        try:
                            unanswered_query = unanswered_query.order_by(
                                '-count')
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("unanswered queries cronjob ! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                        if unanswered_query:
                            unanswered_query[0].count = unanswered_query[
                                0].count + value
                            unanswered_query[0].save()
                        else:
                            UnAnsweredQueries.objects.create(
                                unanswered_message=key, count=value, channel=channel, bot=bot, date=today.date(), selected_language=language)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Unanswered Queries! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    complete_cronjob_execution(cronjob_objs)


unanswered_queries_cronjob()
