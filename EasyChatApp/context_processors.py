from django.conf import settings
from DeveloperConsoleApp.utils import get_developer_console_settings


def is_console_logs(request):
    config_obj = get_developer_console_settings()
    if config_obj:
        return {'SHOW_CONSOLE_LOGS': config_obj.show_console_logs}
    else:
        return {'SHOW_CONSOLE_LOGS': settings.EASYCHAT_SHOW_CONSOLE_LOGS}
