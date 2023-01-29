import sys
import logging
import operator

from EasyAssistSalesforceApp.models import *
from EasyAssistSalesforceApp.utils import *
from EasyAssistSalesforceApp.utils_client_server_signal import *
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def update_agent_active_status():
    try:
        for agent in CobrowseAgent.objects.all():
            agent.is_agent_active()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_agent_active_status %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def check_customers_waiting():
    try:
        access_token_objs = CobrowseAccessToken.objects.filter(is_active=True)
        for access_token in access_token_objs:
            if access_token.enable_waitlist == False:
                continue

            try:
                agent_objs = get_list_agents_under_admin(
                    access_token.agent, is_active=True)
                waiting_cobrowse_io_objs = CobrowseIO.objects.filter(
                    agent__in=agent_objs, is_archived=False)
                waiting_customers_count = 0
                for cobrowse_io in waiting_cobrowse_io_objs:
                    if cobrowse_io.is_active_timer() == False:
                        continue
                    waiting_customers_count += 1
                logger.info("Access token: " + str(access_token),
                            extra={'AppName': 'EasyAssistSalesforce'})
                logger.info("total agents: " + str(len(agent_objs)),
                            extra={'AppName': 'EasyAssistSalesforce'})
                logger.info("customers waiting: " + str(waiting_customers_count),
                            extra={'AppName': 'EasyAssistSalesforce'})
                if waiting_customers_count >= 2 * len(agent_objs):
                    access_token.show_floating_button_on_enable_waitlist = False
                else:
                    access_token.show_floating_button_on_enable_waitlist = True
                access_token.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error check_customers_waiting %s at %s for access token %s",
                             str(e), str(exc_tb.tb_lineno), str(access_token.key), extra={'AppName': 'EasyAssistSalesforce'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_customers_waiting %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def assign_task():
    try:

        update_agent_active_status()

        cobrowse_io_objs = CobrowseIO.objects.filter(agent=None, is_lead=False).filter(
            ~Q(access_token=None)).order_by('request_datetime')

        # if cobrowse_io_objs.count() == 0:
        #     return

        for cobrowse_io_obj in cobrowse_io_objs:
            try:
                cobrowse_agent_admin = cobrowse_io_obj.access_token.agent

                active_agents = get_list_agents_under_admin(
                    cobrowse_agent_admin, is_active=True)

                active_agents = filter_free_active_agent(active_agents, cobrowse_io_obj)

                if len(active_agents) == 0:
                    logger.info("Active Agents are not available",
                                extra={'AppName': 'EasyAssistSalesforce'})
                    continue

                agent_dict = {}
                for agent in active_agents:
                    if not agent.is_cobrowsing_active:
                        agent_dict[agent.user.username] = 0

                if not agent_dict:
                    logger.info("Active Agents are not available",
                                extra={'AppName': 'EasyAssistSalesforce'})
                    continue

                time_threshold = timezone.now() - timedelta(hours=1)
                cobrowseio_obj_list = CobrowseIO.objects.filter(request_datetime__gte=time_threshold, agent__in=active_agents).values(
                    'agent__user__username').annotate(total=Count('agent')).order_by("total")

                for cobrowseio_obj in cobrowseio_obj_list:
                    if cobrowseio_obj["agent__user__username"] in agent_dict:
                        agent_dict[cobrowseio_obj["agent__user__username"]
                                   ] = cobrowseio_obj["total"]

                agent_username = min(agent_dict.items(),
                                     key=operator.itemgetter(1))[0]
                user = User.objects.get(username=agent_username)
                agent_obj = CobrowseAgent.objects.get(user=user)

                logger.info("Active agent selected for next job: %s",
                            agent_username, extra={'AppName': 'EasyAssistSalesforce'})

                notification_message = "Hi, " + agent.user.username + "! A customer has connected with you on Cogno Cobrowse."
                NotificationManagement.objects.create(
                    agent=agent_obj, 
                    cobrowse_io=cobrowse_io_obj,
                    notification_message=notification_message)
                cobrowse_io_obj.agent = agent_obj
                cobrowse_io_obj.save()

                notification_objs = NotificationManagement.objects.filter(
                    show_notification=True, agent=agent_obj)

                response = {}
                notification_list = []

                for notification_obj in notification_objs:
                    notification_list.append(notification_obj.notification_message)
                    notification_obj.delete()

                response["status"] = 200
                response["message"] = "success"
                response["notification_list"] = notification_list

                send_data_from_server_to_client("notification", response, agent_obj.user)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("In assign_task %s at %s for cobrowseio session id : %s",
                             str(e), str(exc_tb.tb_lineno), str(cobrowse_io_obj.session_id), extra={'AppName': 'EasyAssistSalesforce'})
        check_customers_waiting()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error assign_task %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
