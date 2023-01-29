from EasyAssistApp.models import *
from CognoMeetApp.models import *


def create_cognomeet_access_token():
    access_token_objs = CobrowseAccessToken.objects.filter(cogno_meet_access_token="")
    for access_token_obj in access_token_objs:
        admin_agent_user_obj = access_token_obj.agent.user
        cognomeet_admin_agent = CognoMeetAgent.objects.filter(user=admin_agent_user_obj).first()
        if not cognomeet_admin_agent:
            print("Admin agent not found. Creating...")
            cognomeet_admin_agent = CognoMeetAgent.objects.create(user=admin_agent_user_obj, role="admin")
        elif cognomeet_admin_agent.role != "admin":
            print("Admin agent found but role not of admin. Changing the role...")
            cognomeet_admin_agent.role = "admin"
        cognomeet_access_token_obj = CognoMeetAccessToken.objects.filter(agent=cognomeet_admin_agent).first()
        if not cognomeet_access_token_obj:
            cognomeet_access_token_obj = CognoMeetAccessToken.objects.create(agent=cognomeet_admin_agent)
        cognomeet_admin_agent.access_token = cognomeet_access_token_obj
        cognomeet_admin_agent.save()
        access_token_obj.cogno_meet_access_token = str(cognomeet_access_token_obj.key)
        access_token_obj.save()

print("Running create_cognomeet_access_token...\n")

create_cognomeet_access_token()
