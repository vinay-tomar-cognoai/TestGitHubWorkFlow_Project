from EasyChatApp.utils import *
from EasyChatApp.models import *
import datetime
import logging
from django.db.models import Q
logger = logging.getLogger(__name__)


def cronjob():
    try:
        start_date = (datetime.datetime.now() -
                      datetime.timedelta(minutes=60)).date()
        user_objects = Profile.objects.filter(
            last_message_date__lte=start_date)
        Data.objects.filter(user__in=user_objects, is_cache=False).delete()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside Data Model Deletion: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
