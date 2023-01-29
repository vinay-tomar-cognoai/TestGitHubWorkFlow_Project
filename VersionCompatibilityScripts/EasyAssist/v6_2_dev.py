from EasyAssistApp.models import *
from CognoMeetApp.models import *


def update_auto_assign_unattended_lead_toggle():
    access_token_objs = CobrowseAccessToken.objects.all()
    for access_token_obj in access_token_objs:
        access_token_obj.enable_auto_assign_unattended_lead = False
        access_token_obj.enable_request_in_queue = True
        access_token_obj.save()


def create_cognomeet_access_token():
    access_token_objs = CobrowseAccessToken.objects.filter(cogno_meet_access_token="")
    for access_token_obj in access_token_objs:
        admin_agent_user_obj = access_token_obj.agent.user
        cognomeet_admin_agent = CognoMeetAgent.objects.filter(user=admin_agent_user_obj).first()
        if not cognomeet_admin_agent:
            cognomeet_admin_agent = CognoMeetAgent.objects.create(user=admin_agent_user_obj, role="admin")
        cognomeet_access_token_obj = CognoMeetAccessToken.objects.filter(agent=cognomeet_admin_agent).first()
        if not cognomeet_access_token_obj:
            cognomeet_access_token_obj = CognoMeetAccessToken.objects.create(agent=cognomeet_admin_agent)
        cognomeet_admin_agent.access_token = cognomeet_access_token_obj
        cognomeet_admin_agent.save()
        access_token_obj.cogno_meet_access_token = str(cognomeet_access_token_obj.key)
        access_token_obj.save()

print("Running update_auto_assign_unattended_lead_toggle...\n")

update_auto_assign_unattended_lead_toggle()

print("Running create_cognomeet_access_token...\n")

create_cognomeet_access_token()
