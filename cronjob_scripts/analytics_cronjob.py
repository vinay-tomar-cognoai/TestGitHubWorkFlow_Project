from EasyChatApp.models import BotChannel, UserSessionHealth
from EasyChatApp.utils_analytics import return_mis_objects_excluding_blocked_sessions
from EasyChatApp.utils_bot import get_supported_languages


def message_analytics_daily_cronjob():
    from datetime import datetime, timedelta
    from EasyChatApp.models import Bot, MISDashboard, Channel, MessageAnalyticsDaily, Category
    from EasyChatApp.utils import logger
    from EasyChatApp.utils_validation import EasyChatInputValidation
    from django.conf import settings
    import sys
    import os
    try:
        if MessageAnalyticsDaily.objects.all().count() != 0:
            last_date = MessageAnalyticsDaily.objects.latest(
                'date_message_analytics').date_message_analytics
        else:
            last_date = MISDashboard.objects.last().creation_date

        today = datetime.now()
        while(last_date < today.date()):
            for bot in Bot.objects.filter(is_deleted=False):
                supported_languages = get_supported_languages(bot, BotChannel)
                # Some messages are assigned under None category
                category_list = [None]
                category_list += [
                    bot_category for bot_category in Category.objects.filter(bot=bot)]
                for channel in Channel.objects.filter(is_easychat_channel=True):
                    for category in category_list:
                        for language in supported_languages:
                            date_filtered_mis_objects = MISDashboard.objects.filter(
                                creation_date=last_date, channel_name=channel.name, bot=bot, category=category, selected_language=language)
                            
                            date_filtered_mis_objects = return_mis_objects_excluding_blocked_sessions(date_filtered_mis_objects, UserSessionHealth)
                            
                            # Total Messages
                            total_messages = date_filtered_mis_objects.count()
                            if total_messages == 0:
                                continue
                            total_messages_mobile = date_filtered_mis_objects.filter(is_mobile=True).count()
                            
                            # Unanswered messages
                            total_unanswered_messages = date_filtered_mis_objects.filter(
                                intent_name=None, is_unidentified_query=True, is_intiuitive_query=False).exclude(message_received="")
                            total_unanswered_messages_count = total_unanswered_messages.count()
                            total_unanswered_messages_mobile_count = total_unanswered_messages.filter(is_mobile=True).count()
                            # intuitive messages
                            total_intuitive_messages = date_filtered_mis_objects.filter(
                                intent_name=None, is_intiuitive_query=True)
                            total_intuitive_messages_count = total_intuitive_messages.count()
                            total_intuitive_messages_mobile_count = total_intuitive_messages.filter(is_mobile=True).count()
                            
                            # Answered Messages
                            total_answered_messages = total_messages - (total_unanswered_messages_count + total_intuitive_messages_count)
                            total_answered_messages_mobile_count = total_messages_mobile - (total_unanswered_messages_mobile_count + total_intuitive_messages_mobile_count)
                            if MessageAnalyticsDaily.objects.filter(date_message_analytics=last_date, channel_message=channel, bot=bot, category=category, selected_language=language):
                                pass
                            else:
                                MessageAnalyticsDaily.objects.create(total_messages_count=total_messages, answered_query_count=total_answered_messages,
                                                                     unanswered_query_count=total_unanswered_messages_count, 
                                                                     intuitive_query_count=total_intuitive_messages_count, 
                                                                     channel_message=channel, date_message_analytics=last_date,
                                                                      bot=bot, category=category, selected_language=language,
                                                                      total_message_count_mobile=total_messages_mobile,
                                                                      intuitive_query_count_mobile=total_intuitive_messages_mobile_count,
                                                                      answered_query_count_mobile=total_answered_messages_mobile_count,
                                                                      unanswered_query_count_mobile=total_unanswered_messages_mobile_count)
            last_date = last_date + timedelta(days=1)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("MessageAnalyticsDaily! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def wordcloud_daily_cronjob():
    from datetime import datetime, timedelta
    from EasyChatApp.models import Bot, MISDashboard, Channel, MessageAnalyticsDaily, WordCloudAnalyticsDaily, Category
    from EasyChatApp.utils import logger, get_word_count_from_mis
    from django.conf import settings
    import json
    import sys
    import os
    try:
        if WordCloudAnalyticsDaily.objects.all().count() != 0:
            last_date = WordCloudAnalyticsDaily.objects.latest(
                'date').date
        else:
            last_date = MISDashboard.objects.last().creation_date

        today = datetime.now()

        while(last_date < today.date()):
            for bot in Bot.objects.filter(is_deleted=False):
                supported_languages = get_supported_languages(bot, BotChannel)
                for channel in Channel.objects.filter(is_easychat_channel=True):
                    for category in Category.objects.filter(bot=bot):
                        for language in supported_languages:
                            word_dictionary = get_word_count_from_mis(
                                [bot], MISDashboard, UserSessionHealth, last_date, last_date, category.name, channel.name, language)
                            if isinstance(word_dictionary, list) and len(word_dictionary) == 0:
                                continue
                            if WordCloudAnalyticsDaily.objects.filter(date=last_date, channel=channel, bot=bot, category=category, selected_language=language):
                                pass
                            else:
                                WordCloudAnalyticsDaily.objects.create(
                                    word_cloud_dictionary=word_dictionary, date=last_date, channel=channel, bot=bot, category=category, selected_language=language)
            last_date = last_date + timedelta(days=1)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Wordcloud Daily! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def unanswered_queries_cronjob():
    from datetime import datetime, timedelta
    from EasyChatApp.models import Bot, MISDashboard, Channel, MessageAnalyticsDaily, UnAnsweredQueries
    from EasyChatApp.utils import logger, get_word_count_from_mis
    from django.conf import settings
    import json
    import sys
    import os
    try:
        if UnAnsweredQueries.objects.all().count() != 0:
            last_date = UnAnsweredQueries.objects.latest('date').date
        else:
            last_date = MISDashboard.objects.all().order_by(
                'creation_date').first().creation_date

        today = datetime.now()
        while(last_date < today.date()):
            for bot in Bot.objects.filter(is_deleted=False):
                supported_languages = get_supported_languages(bot, BotChannel)
                for channel in Channel.objects.filter(is_easychat_channel=True):
                    for language in supported_languages:
                        mis_objs = MISDashboard.objects.filter(
                            channel_name=channel.name, bot=bot, status="2", is_intiuitive_query=False, intent_name=None, creation_date=last_date, selected_language=language)
                        mis_objs = return_mis_objects_excluding_blocked_sessions(mis_objs, UserSessionHealth)
                        if mis_objs.count() == 0:
                            continue
                        details_of_unanswered_messages = {}
                        for mis_obj in mis_objs.iterator():
                            mis_obj.status = "1"
                            mis_obj.save(update_fields=['status'])
                            msg_rcvd = mis_obj.get_message_received()
                            if details_of_unanswered_messages.get(msg_rcvd.lower()):
                                details_of_unanswered_messages[
                                    msg_rcvd.lower()] += 1
                            else:
                                details_of_unanswered_messages[
                                    msg_rcvd.lower()] = 1
                        for key, value in details_of_unanswered_messages.items():
                            unanswered_query = UnAnsweredQueries.objects.filter(
                                unanswered_message=key, channel=channel, bot=bot, date=last_date, selected_language=language)
                            try:
                                unanswered_query = unanswered_query.order_by(
                                    '-count')
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logger.error("unanswered queries cronjob ! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                                pass
                            if unanswered_query:
                                unanswered_query[0].count = unanswered_query[
                                    0].count + value
                                unanswered_query[0].save()
                            else:
                                UnAnsweredQueries.objects.create(
                                    unanswered_message=key, count=value, channel=channel, bot=bot, date=last_date, selected_language=language)
            last_date = last_date + timedelta(days=1)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Unanswered Queries! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def user_analytics_daily_cronjob():
    from datetime import datetime, timedelta
    from EasyChatApp.models import Bot, MISDashboard, Channel, UniqueUsers
    from EasyChatApp.utils import logger
    from django.conf import settings
    import sys
    import os
    try:
        if UniqueUsers.objects.all().count() != 0:
            last_date = UniqueUsers.objects.latest(
                'date').date
        else:
            last_date = MISDashboard.objects.last().creation_date
        today = datetime.now()
        while(last_date < today.date()):
            for bot in Bot.objects.filter(is_deleted=False):
                supported_languages = get_supported_languages(bot, BotChannel)
                for channel in Channel.objects.filter(is_easychat_channel=True):
                    for language in supported_languages:
                        date_filtered_mis_objects = MISDashboard.objects.filter(
                            creation_date=last_date, channel_name=channel.name, bot=bot, selected_language=language)

                        date_filtered_mis_objects = return_mis_objects_excluding_blocked_sessions(date_filtered_mis_objects, UserSessionHealth)

                        unique_users = date_filtered_mis_objects.values("user_id")
                        count_of_unique_users = unique_users.distinct().count()
                        count_of_unique_users_mobile = unique_users.filter(is_mobile=True).distinct().count()

                        unique_session_mis = date_filtered_mis_objects.values(
                            "session_id").distinct()

                        count_of_unique_sessions = unique_session_mis.count()

                        count_of_business_initiated_sesions = unique_session_mis.filter(
                            is_business_initiated_session=True).count()

                        if count_of_unique_users == 0 and count_of_unique_sessions == 0:
                            continue
                        if UniqueUsers.objects.filter(date=last_date, channel=channel, bot=bot, selected_language=language):
                            pass
                        else:
                            UniqueUsers.objects.create(count=count_of_unique_users, users_count_mobile=count_of_unique_users_mobile, session_count=count_of_unique_sessions,
                                                       business_initiated_session_count=count_of_business_initiated_sesions, date=last_date, channel=channel, bot=bot, selected_language=language)

            last_date = last_date + timedelta(days=1)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("User Analytics Daily! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def cronjob():
    message_analytics_daily_cronjob()
    unanswered_queries_cronjob()
    user_analytics_daily_cronjob()
    wordcloud_daily_cronjob()
