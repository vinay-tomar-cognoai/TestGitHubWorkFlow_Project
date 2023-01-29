import sys
import logging
import operator
from EasyAssistApp.models import CobrowseAgent

from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from EasyAssistApp.utils_client_server_signal import *
from datetime import datetime, timedelta
from DeveloperConsoleApp.utils import get_developer_console_cobrowsing_settings, get_developer_console_cognomeet_settings
from EasyAssistApp.utils_cronjob import get_easyassist_cronjob_tracker_obj, create_easyassist_cronjob_tracker_obj, \
    delete_easyassist_cronjob_tracker_obj, delete_and_create_cron_tracker_obj

logger = logging.getLogger(__name__)


def update_agent_active_status():
    try:
        for agent in CobrowseAgent.objects.all().iterator():
            agent.is_agent_active()
            agent.is_agent_in_meeting()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_agent_active_status %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def check_customers_waiting():
    try:
        access_token_objs = CobrowseAccessToken.objects.filter(is_active=True)
        for access_token in access_token_objs.iterator():
            if access_token.enable_waitlist == False:
                continue

            try:
                agent_objs = get_list_agents_under_admin(
                    access_token.agent, is_active=True)
                waiting_cobrowse_io_objs = CobrowseIO.objects.filter(
                    agent__in=agent_objs, is_archived=False)
                waiting_customers_count = 0
                for cobrowse_io in waiting_cobrowse_io_objs.iterator():
                    if cobrowse_io.is_active_timer() == False:
                        continue
                    waiting_customers_count += 1
    
                if waiting_customers_count >= 2 * len(agent_objs):
                    access_token.show_floating_button_on_enable_waitlist = False
                else:
                    access_token.show_floating_button_on_enable_waitlist = True
                access_token.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error check_customers_waiting %s at %s for access token %s",
                             str(e), str(exc_tb.tb_lineno), str(access_token.key), extra={'AppName': 'EasyAssist'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_customers_waiting %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def assign_task():
    try:

        easyassist_cronjob_tracker_obj = get_easyassist_cronjob_tracker_obj(EASYASSIST_SCHEDULAR_ID_CONSTANT, EasyAssistCronjobTracker)
        if easyassist_cronjob_tracker_obj:
            if easyassist_cronjob_tracker_obj.is_object_expired():
                delete_and_create_cron_tracker_obj(EASYASSIST_SCHEDULAR_ID_CONSTANT, EasyAssistCronjobTracker)
            else:
                logger.info("Cobrowsing assign_task is already running!",
                            extra={'AppName': 'EasyAssist'})
                return
        else:
            create_easyassist_cronjob_tracker_obj(EASYASSIST_SCHEDULAR_ID_CONSTANT, EasyAssistCronjobTracker)

        update_agent_active_status()

        archive_cobrowse_objects(
            CobrowseAccessToken, CobrowseIO, SystemAuditTrail)

        auto_assign_unattended_leads(
            CobrowseAccessToken, CobrowseIO, CobrowseAgent, User, UnattendedLeadTransferAuditTrail)

        assign_followup_leads_to_agents()

        cobrowse_access_token_objs = CobrowseAccessToken.objects.all()

        for cobrowse_access_token_obj in cobrowse_access_token_objs.iterator():
            try:
                if not cobrowse_access_token_obj.enable_request_in_queue:
                    temp_dictionary = {}
                    assign_task_function = str(
                        cobrowse_access_token_obj.get_assign_task_processor_obj().function)
                    exec(assign_task_function, temp_dictionary)
                    temp_dictionary['assign_cobrowse_obj_to_agent'](
                        cobrowse_access_token_obj)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("In assign_task %s at %s for accesstoken : %s of agent : %s",
                             str(e), str(exc_tb.tb_lineno), str(cobrowse_access_token_obj.key), str(cobrowse_access_token_obj.agent.user.username), extra={'AppName': 'EasyAssist'})

        check_customers_waiting()
        
        delete_easyassist_cronjob_tracker_obj(EASYASSIST_SCHEDULAR_ID_CONSTANT, EasyAssistCronjobTracker)
    except Exception as e:
        delete_easyassist_cronjob_tracker_obj(EASYASSIST_SCHEDULAR_ID_CONSTANT, EasyAssistCronjobTracker)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error assign_task %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def assign_cobrowse_obj_to_agent(cobrowse_access_token_obj):

    def check_agent_available(agent_obj, active_agents):
        for agent in active_agents:
            if agent.user.username == agent_obj.user.username:
                return True
        return False
    
    cobrowse_agent_admin = cobrowse_access_token_obj.agent
    allowed_agent_support_levels = ["L1"]

    cobrowse_io_objs = CobrowseIO.objects.filter(
        access_token=cobrowse_access_token_obj, agent=None, is_lead=False, is_archived=False).order_by('request_datetime')
    for cobrowse_io_obj in cobrowse_io_objs.iterator():

        selected_agent = None
        allow_video_meeting_only = cobrowse_io_obj.access_token.allow_video_meeting_only

        active_agents = get_list_agents_under_admin(
            cobrowse_agent_admin, is_active=True)

        active_agents = filter_free_active_agent(
            active_agents, cobrowse_io_obj, for_meeting=allow_video_meeting_only, support_levels=allowed_agent_support_levels)

        if cobrowse_access_token_obj.enable_smart_agent_assignment == True:
            client_mobile_no = cobrowse_io_obj.mobile_number
            diff_time = datetime.now() - timedelta(minutes=cobrowse_access_token_obj.smart_agent_assignment_reconnecting_window)
            filter_cobrowse_io_objs = CobrowseIO.objects.filter(
                access_token=cobrowse_access_token_obj, is_archived=True, is_lead=False,
                mobile_number=get_hashed_data(client_mobile_no), 
                client_session_end_time__gte=diff_time
            ).order_by('-client_session_end_time')
            
            for filter_cobrowse_io_obj in filter_cobrowse_io_objs.iterator():
                filter_cobrowse_io_obj_agent = filter_cobrowse_io_obj.agent
                agent_obj = CobrowseAgent.objects.get(user=filter_cobrowse_io_obj_agent)
                if check_agent_available(agent_obj, active_agents):
                    selected_agent = agent_obj
                    break
        
        if selected_agent == None:

            if len(active_agents) == 0:
                logger.info("Active Agents are not available",
                            extra={'AppName': 'EasyAssist'})
                continue

            agent_dict = {}
            for agent in active_agents:
                agent_dict[agent.user.username] = []
                agent_dict[agent.user.username].append(0)
                if agent.last_lead_assigned_datetime != None:
                    agent_dict[agent.user.username].append(
                        datetime.timestamp(agent.last_lead_assigned_datetime))
                else:
                    agent_dict[agent.user.username].append(0)

            if not agent_dict:
                logger.info("Active Agents are not available",
                            extra={'AppName': 'EasyAssist'})
                continue

            waiting_cobrowse_io_objs = CobrowseIO.objects.filter(
                agent__in=active_agents, is_archived=False)

            for cobrowse_io in waiting_cobrowse_io_objs.iterator():
                if cobrowse_io.is_active_timer() == False:
                    continue

                if cobrowse_io.agent.user.username in agent_dict:
                    agent_dict[cobrowse_io.agent.user.username][0] += 1

            agent_min_lead_entry = min(agent_dict.items(),
                                        key=lambda item: (item[1][0], item[1][1]))

            agent_username = agent_min_lead_entry[0]
            agent_active_leads_count = agent_min_lead_entry[1][0]

            logger.info("agent_dict : " + str(agent_dict),
                        extra={'AppName': 'EasyAssist'})
            logger.info("Agent with min lead: " + str(agent_username) + ":" +
                        str(agent_active_leads_count), extra={'AppName': 'EasyAssist'})

            if cobrowse_io_obj.access_token.maximum_active_leads and agent_active_leads_count >= cobrowse_io_obj.access_token.maximum_active_leads_threshold:
                logger.info("All active agents have atleast %s active leads",
                            str(cobrowse_io_obj.access_token.maximum_active_leads_threshold), extra={'AppName': 'EasyAssist'})
                continue

            user = User.objects.get(username=agent_username)
            selected_agent = CobrowseAgent.objects.get(user=user)
        if selected_agent.is_active == False:
            continue

        logger.warning("Active agent selected for next cobrowsing session %s : %s",
                        str(cobrowse_io_obj.session_id), selected_agent.user.username, extra={'AppName': 'EasyAssist'})
        selected_agent.last_lead_assigned_datetime = timezone.now()
        selected_agent.save()

        cobrowse_io_obj.agent = selected_agent
        if cobrowse_access_token_obj.enable_auto_assign_unattended_lead:
            update_unattended_lead_transfer_audit_trail(cobrowse_io_obj, 
                                                        selected_agent, UnattendedLeadTransferAuditTrail)
        cobrowse_io_obj.last_agent_assignment_datetime = timezone.now()
        if allow_video_meeting_only:
            product_name = "Cogno Meet"
            cognomeet_config_obj = get_developer_console_cognomeet_settings()
            if cognomeet_config_obj:
                product_name = cognomeet_config_obj.cognomeet_title_text

            notification_message = "Hi, " + selected_agent.user.username + \
                "! A customer has connected with you on " + product_name + "."
        else:
            product_name = "Cogno Cobrowse"
            cobrowse_config_obj = get_developer_console_cobrowsing_settings()
            if cobrowse_config_obj:
                product_name = cobrowse_config_obj.cobrowsing_title_text

            notification_message = "Hi, " + selected_agent.user.username + \
                "! A customer has connected with you on " + product_name + "."

        NotificationManagement.objects.create(agent=selected_agent,
                                                cobrowse_io=cobrowse_io_obj,
                                                notification_message=notification_message,
                                                product_name=product_name)

        if cobrowse_io_obj.access_token.show_verification_code_modal == False:
            cobrowse_io_obj.allow_agent_cobrowse = "true"
        cobrowse_io_obj.save()

        notification_objs = NotificationManagement.objects.filter(
            show_notification=True, agent=selected_agent)

        response = {}
        notification_list = []

        for notification_obj in notification_objs.iterator():
            notification_list.append({
                "notification_message": notification_obj.notification_message,
                "product_name": notification_obj.product_name
            })
            notification_obj.delete()

        response["status"] = 200
        response["message"] = "success"
        response["notification_list"] = notification_list

        send_data_from_server_to_client(
            "notification", response, selected_agent.user)

    
