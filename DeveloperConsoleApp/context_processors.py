from django.conf import settings
from DeveloperConsoleApp.utils import get_developer_console_livechat_settings, get_developer_console_easychat_settings, get_developer_console_settings, \
    get_developer_console_cognodesk_settings, get_developer_console_cobrowsing_settings, get_developer_console_cognomeet_settings


def get_livechat_config_obj(request):

    return {"livechat_config_obj": get_developer_console_livechat_settings()}


def get_easychat_config_obj(request):

    return {"easychat_config_obj": get_developer_console_easychat_settings()}


def get_developer_console_config_obj(request):

    return {"developer_config_obj": get_developer_console_settings()}


def get_cognodesk_console_config_obj(request):

    return {"cognodesk_config_obj": get_developer_console_cognodesk_settings()}


def get_cobrowse_console_config_obj(request):

    return {"cobrowse_config_obj": get_developer_console_cobrowsing_settings()}


def get_cognomeet_console_config_obj(request):

    return {"cognomeet_config_obj": get_developer_console_cognomeet_settings()}
