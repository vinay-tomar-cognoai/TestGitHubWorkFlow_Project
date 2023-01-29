from EasyChatApp.utils import login_activity
from django.conf import settings
import sys
import logging

logger = logging.getLogger(__name__)


def cronjob():
    try:
        if settings.ENABLE_AUTO_LOGOUT_SESSION == True:
            login_activity()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
