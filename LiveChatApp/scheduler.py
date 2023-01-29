import sys
from LiveChatApp.assign_task import assign_agent_via_scheduler
from LiveChatApp.assign_followup_leads import assign_followup_leads_to_agents
from LiveChatApp.retrieve_and_assign_email_chats import retrieve_livechat_mails
from LiveChatApp.constants import LIVECHAT_ASSIGN_CHAT_SCHEDULER, LIVECHAT_ASSIGN_FOLLOWUP_LEAD_SCHEDULER, LIVECHAT_RETRIEVE_EMAIL_SCHEDULER
from LiveChatApp.utils import logger, get_livechat_cronjob_tracker_obj, create_livechat_cronjob_tracker_obj, delete_livechat_cronjob_tracker_obj
from LiveChatApp.models import LiveChatCronjobTracker


def run_assign_agent_via_scheduler():
    try:
        cronjob_tracker_obj = get_livechat_cronjob_tracker_obj(LIVECHAT_ASSIGN_CHAT_SCHEDULER, LiveChatCronjobTracker)

        if cronjob_tracker_obj:
            logger.info("assign_agent_via_scheduler is already running!",
                        extra={'AppName': 'LiveChat'})

            if cronjob_tracker_obj.is_object_expired():
                delete_livechat_cronjob_tracker_obj(LIVECHAT_ASSIGN_CHAT_SCHEDULER, LiveChatCronjobTracker)    

            return
        else:
            create_livechat_cronjob_tracker_obj(LIVECHAT_ASSIGN_CHAT_SCHEDULER, LiveChatCronjobTracker)

        assign_agent_via_scheduler()

        delete_livechat_cronjob_tracker_obj(LIVECHAT_ASSIGN_CHAT_SCHEDULER, LiveChatCronjobTracker)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error inside run_assign_agent_via_scheduler : %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        delete_livechat_cronjob_tracker_obj(LIVECHAT_ASSIGN_CHAT_SCHEDULER, LiveChatCronjobTracker)


def run_assign_followup_leads_to_agents():
    try:
        cronjob_tracker_obj = get_livechat_cronjob_tracker_obj(LIVECHAT_ASSIGN_FOLLOWUP_LEAD_SCHEDULER, LiveChatCronjobTracker)

        if cronjob_tracker_obj:
            logger.info("assign_followup_leads_to_agents scheduler is already running!",
                        extra={'AppName': 'LiveChat'})

            if cronjob_tracker_obj.is_object_expired():
                delete_livechat_cronjob_tracker_obj(LIVECHAT_ASSIGN_FOLLOWUP_LEAD_SCHEDULER, LiveChatCronjobTracker)

            return
        else:
            create_livechat_cronjob_tracker_obj(LIVECHAT_ASSIGN_FOLLOWUP_LEAD_SCHEDULER, LiveChatCronjobTracker)

        assign_followup_leads_to_agents()

        delete_livechat_cronjob_tracker_obj(LIVECHAT_ASSIGN_FOLLOWUP_LEAD_SCHEDULER, LiveChatCronjobTracker)
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error inside run_assign_followup_leads_to_agents : %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        delete_livechat_cronjob_tracker_obj(LIVECHAT_ASSIGN_FOLLOWUP_LEAD_SCHEDULER, LiveChatCronjobTracker)


def run_retrieve_livechat_mails():
    try:
        cronjob_tracker_obj = get_livechat_cronjob_tracker_obj(LIVECHAT_RETRIEVE_EMAIL_SCHEDULER, LiveChatCronjobTracker)

        if cronjob_tracker_obj:
            logger.info("retrieve_livechat_mails scheduler is already running!",
                        extra={'AppName': 'LiveChat'})

            if cronjob_tracker_obj.is_object_expired():
                delete_livechat_cronjob_tracker_obj(LIVECHAT_RETRIEVE_EMAIL_SCHEDULER, LiveChatCronjobTracker)
            
            return
        else:
            create_livechat_cronjob_tracker_obj(LIVECHAT_RETRIEVE_EMAIL_SCHEDULER, LiveChatCronjobTracker)

        retrieve_livechat_mails()

        delete_livechat_cronjob_tracker_obj(LIVECHAT_RETRIEVE_EMAIL_SCHEDULER, LiveChatCronjobTracker)
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error inside run_retrieve_livechat_mails : %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        delete_livechat_cronjob_tracker_obj(LIVECHAT_RETRIEVE_EMAIL_SCHEDULER, LiveChatCronjobTracker)

run_assign_agent_via_scheduler()
run_assign_followup_leads_to_agents()
run_retrieve_livechat_mails()
