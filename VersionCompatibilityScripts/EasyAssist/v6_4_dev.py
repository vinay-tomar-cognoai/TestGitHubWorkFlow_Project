import uuid
from EasyAssistApp.models import CobrowseAgent, LiveChatCannedResponse, AgentFrequentLiveChatCannedResponses, \
    CobrowseAccessToken, CobrowseDropLink, CobrowseDateWiseOutboundDroplinkAnalytics, AssignTaskProcessor
from EasyAssistApp.utils import get_list_agents_under_admin
from datetime import datetime, timedelta
from EasyAssistApp.constants import ASSIGN_TAKS_PROCESSOR_CODE


def update_agent_virtual_codes():
    cobrowse_agents = CobrowseAgent.objects.all()
    for cobrowse_agent in cobrowse_agents:
        uuid_str = str(uuid.uuid4())
        new_virtual_agent_code = uuid_str[-7:]
        if new_virtual_agent_code.find("-") != -1:
            new_virtual_agent_code = new_virtual_agent_code.replace("-", "a")
        cobrowse_agent.virtual_agent_code = new_virtual_agent_code
        cobrowse_agent.save(update_fields=["virtual_agent_code"])


def update_canned_responsese():
    canned_responsed_objs = LiveChatCannedResponse.objects.all()
    for canned_response_obj in canned_responsed_objs:
        if not canned_response_obj.access_token:
            canned_response_obj.access_token = canned_response_obj.agent.get_access_token_obj()
            canned_response_obj.save(update_fields=["access_token"])


def update_frequent_used_canned_response():
    common_canned_responsed_objs = AgentFrequentLiveChatCannedResponses.objects.all()
    for common_canned_response_obj in common_canned_responsed_objs:
        if not common_canned_response_obj.access_token:
            common_canned_response_obj.access_token = common_canned_response_obj.agent.get_access_token_obj()
            common_canned_response_obj.save(update_fields=["access_token"])


def remove_frequent_used_canned_response():
    AgentFrequentLiveChatCannedResponses.objects.all().delete()


def update_droplink_previous_data():
    for access_token_obj in CobrowseAccessToken.objects.all().iterator():
        go_live_date = access_token_obj.go_live_date
        today_date = datetime.now().date()
        delta = today_date - go_live_date
        agent_objs = get_list_agents_under_admin(
            access_token_obj.agent, None, None)
        for i in range(delta.days):
            date = go_live_date + timedelta(days=i)
            drop_link_objs = CobrowseDropLink.objects.filter(agent__in=agent_objs, generate_datetime__date=date, proxy_cobrowse_io=None)
            for agent in agent_objs:
                total_links_generated = drop_link_objs.filter(
                    agent=agent).count()

                cobrowse_analytics_obj = CobrowseDateWiseOutboundDroplinkAnalytics.objects.filter(
                    date=date, agent=agent).first()

                if cobrowse_analytics_obj == None:
                    CobrowseDateWiseOutboundDroplinkAnalytics.objects.create(
                        agent=agent,
                        date=date,
                        total_droplinks_generated=total_links_generated)
                else:
                    cobrowse_analytics_obj.total_droplinks_generated = total_links_generated
                    cobrowse_analytics_obj.save(
                        update_fields=["total_droplinks_generated"])


def update_assign_task_processor_function():
    for assign_task_obj in AssignTaskProcessor.objects.all().iterator():
        assign_task_obj.function = ASSIGN_TAKS_PROCESSOR_CODE
        assign_task_obj.save(update_fields=["function"])    


print("Running update_agent_virtual_codes...\n")

update_agent_virtual_codes()

print("Running update_canned_responsese...\n")

update_canned_responsese()

print("Running update_frequent_used_canned_response...\n")

update_frequent_used_canned_response()

print("Running remove_frequent_used_canned_response...\n")

remove_frequent_used_canned_response()

print("Running update_droplink_previous_data...\n")

update_droplink_previous_data()

print("Running update_assign_task_processor_function...\n")

update_assign_task_processor_function()
