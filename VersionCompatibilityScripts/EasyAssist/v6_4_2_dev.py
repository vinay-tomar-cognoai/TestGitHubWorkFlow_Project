from EasyAssistApp.models import CobrowseAccessToken, logger


def map_access_token_to_agents():
    try:
        access_token_objs = CobrowseAccessToken.objects.all()
        for access_token_obj in access_token_objs.iterator():
            admin_agent = access_token_obj.agent
            # saving access token in admin agent
            admin_agent.access_token = access_token_obj
            admin_agent.save(update_fields=["access_token"])

            admin_allies_list = []
            supervisors_list = []
            agents_list = []

            # getting admin allies under admin
            admin_allies_list += admin_agent.agents.filter(role="admin_ally")
            # getting supervisors under admin
            supervisors_list += admin_agent.agents.filter(role="supervisor")
            # getting agents under admin
            agents_list += admin_agent.agents.filter(role="agent")

            # getting supervisors and agents under admin allies
            for admin_ally in admin_allies_list:
                supervisors_list += admin_ally.agents.filter(role="supervisor")
                agents_list += admin_ally.agents.filter(role="agent")
                admin_ally.access_token = access_token_obj
                admin_ally.save(update_fields=["access_token"])

            supervisors_list = list(set(supervisors_list))
            # getting agents under supervisors
            for supervisor in supervisors_list:
                agents_list += supervisor.agents.filter(role="agent")
                supervisor.access_token = access_token_obj
                supervisor.save(update_fields=["access_token"])

            agents_list = list(set(agents_list))
            for agent in agents_list:
                agent.access_token = access_token_obj
                agent.save(update_fields=["access_token"])

    except Exception as e:
        logger.error("Error in map_access_token_to_agents: %s", str(
            e), extra={'AppName': 'EasyAssist'})


def disable_proxy_cobrowsing():
    access_token_objs = CobrowseAccessToken.objects.all()
    for access_token_obj in access_token_objs.iterator():
        proxy_config_obj = access_token_obj.get_proxy_config_obj()
        proxy_config_obj.enable_proxy_cobrowsing = False
        proxy_config_obj.save(update_fields=["enable_proxy_cobrowsing"])


print("Running map_access_token_to_agents...\n")

map_access_token_to_agents()

print("Running disable_proxy_cobrowsing...\n")

disable_proxy_cobrowsing()
