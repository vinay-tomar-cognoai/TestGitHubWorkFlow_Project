from DeveloperConsoleApp.models import DeveloperConsoleConfig
from DeveloperConsoleApp.utils import logger


def create_developer_console_config_object():
    try:
        total_config_objs = DeveloperConsoleConfig.objects.all().count()
        if total_config_objs == 0:
            DeveloperConsoleConfig.objects.create()

    except Exception as e:
        logger.error("Error in create_developer_console_config_object: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

create_developer_console_config_object()
