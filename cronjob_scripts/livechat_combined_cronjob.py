

def cronjob():
    from LiveChatApp.utils import (logger, get_livechat_cronjob_tracker_obj, create_livechat_cronjob_tracker_obj,
                                    delete_livechat_cronjob_tracker_obj)
    
    from LiveChatApp.constants import LIVECHAT_COMBINED_CRONJOB_CONSTANT

    from LiveChatApp.models import LiveChatCronjobTracker

    cronjob_tracker_obj = get_livechat_cronjob_tracker_obj(LIVECHAT_COMBINED_CRONJOB_CONSTANT, LiveChatCronjobTracker)
    
    if cronjob_tracker_obj:
        logger.info("combined cronjob is already running!",
                    extra={'AppName': 'LiveChat'})
        return
    else:
        create_livechat_cronjob_tracker_obj(LIVECHAT_COMBINED_CRONJOB_CONSTANT, LiveChatCronjobTracker)
    
    from cronjob_scripts.livechat_agent_performance_report_dump import cronjob
    logger.info("STARTING LIVECHAT AGENT NOT READY DUMP",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT AGENT NOT READY DUMP",
                extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_agent_not_ready_report_dump import cronjob
    logger.info("STARTING LIVECHAT AGENT NOT READY DUMP",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT AGENT NOT READY DUMP",
                extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_analytics_data_dump import cronjob
    logger.info("STARTING LIVECHAT ANALYTICS DUMP",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT ANALYTICS DUMP",
                extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_chat_history_dump import cronjob
    logger.info("STARTING LIVECHAT CHAT HISTORY DUMP",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT CHAT HISTORY DUMP",
                extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_daily_interaction_report_dump import cronjob
    logger.info("STARTING LIVECHAT DAILY INTERACTION",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT DAILY INTERACTION",
                extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_hourly_interaction_report_dump import cronjob
    logger.info("STARTING LIVECHAT HOURLY INTERACTION REPORT",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT HOURLY INTERACTION REPORT",
                extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_login_logout_report_dump import cronjob
    logger.info("STARTING LIVECHAT LOGIN LOGOUT",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT LOGIN LOGOUT", extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_missed_chats_report_dump import cronjob
    logger.info("STARTING LIVECHAT MISSED CHATS",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT MISSED CHATS",
                extra={'AppName': 'LiveChat'})
    from cronjob_scripts.livechat_offline_chats_report_dump import cronjob
    logger.info("STARTING LIVECHAT OFFLINE CHATS",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT OFFLINE CHATS",
                extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_abandoned_chats_report_dump import cronjob
    logger.info("STARTING LIVECHAT ABANDONED CHATS",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT ABANDONED CHATS",
                extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_voip_history_dump import cronjob
    logger.info("STARTING LIVECHAT VOIP HISTORY CRONJOB",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT TOTAL VOIP HISTORY",
                extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_conversations_dump import cronjob
    logger.info("STARTING LIVECHAT CONVERSATIONS CRONJOB",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT CONVERSATIONS CRONJOB",
                extra={'AppName': 'LiveChat'})

    from cronjob_scripts.livechat_vc_history_dump import cronjob
    logger.info("STARTING LIVECHAT VC HISTORY CRONJOB",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT TOTAL VC HISTORY",
                extra={'AppName': 'LiveChat'})
    
    from cronjob_scripts.livechat_cobrowsing_history_dump import cronjob
    logger.info("STARTING LIVECHAT CB HISTORY CRONJOB",
                extra={'AppName': 'LiveChat'})
    cronjob()
    logger.info("ENDING LIVECHAT TOTAL CB HISTORY",
                extra={'AppName': 'LiveChat'})

    delete_livechat_cronjob_tracker_obj(LIVECHAT_COMBINED_CRONJOB_CONSTANT, LiveChatCronjobTracker)
