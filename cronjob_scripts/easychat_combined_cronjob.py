from cronjob_scripts.EasyChatAppCronjobUtilityFunctions.utils_cronjob import *


def cronjob():

    cronjob_id = "easychat_easychat_combined_cronjob_cron"
    cronjob_is_running, cronjob_objs = check_if_cronjob_is_running(cronjob_id)
    if cronjob_is_running:
        return

    from EasyChatApp.utils import logger

    from cronjob_scripts.message_history_dump import cronjob
    logger.info("STARTING SEND MAIL MONTHLY", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    cronjob()
    logger.info("ENDING SEND MAIL MONTHLY", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    from cronjob_scripts.datamodel_deletion_script import cronjob
    cronjob()
    from cronjob_scripts.flowdropoff_analytics import cronjob
    logger.info("STARTING flowdropoff analytics", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    cronjob()
    logger.info("ENDING flowdropoff analytics", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    from cronjob_scripts.flow_analytics_daily_sum import cronjob
    cronjob()

    logger.info("STARTING ANALYTICS CRONJOB", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    from cronjob_scripts.analytics_cronjob import cronjob
    cronjob()
    logger.info("ENDING ANALYTICS CRONJOB", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    logger.info("STARTING REVISED ANALYTICS CRONJOB", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    from cronjob_scripts.revised_analytics_cronjob import cronjob
    cronjob()

    logger.info("ENDING REVISED ANALYTICS CRONJOB", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    logger.info("STARTING NPS DATADUMP CRONJOB", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    from cronjob_scripts.nps_datadump import cronjob
    cronjob()

    logger.info("ENDING NPS DATADUMP CRONJOB", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    logger.info("STARTING EASYCHAT BOT ACCURACY", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    from cronjob_scripts.easychat_bot_accuracy_daily import cronjob
    cronjob()

    logger.info("ENDING EASYCHAT BOT ACCURACY CRONJOB", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    complete_cronjob_execution(cronjob_objs)
