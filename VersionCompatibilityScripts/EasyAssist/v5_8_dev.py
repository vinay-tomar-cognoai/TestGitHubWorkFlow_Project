from EasyAssistApp.models import *


def update_no_agent_connect_timer():
    try:
        for access_token in CobrowseAccessToken.objects.all():
            access_token.no_agent_connects_toast_threshold = 1
            access_token.save()

    except Exception as e:
        logger.error("Error in update_no_agent_connect_timer: %s", str(e), extra={'AppName': 'EasyAssist'})


print("Running update_no_agent_connect_timer...\n")

update_no_agent_connect_timer()
