from EasyChatApp.models import TwitterTracker
import sys
import datetime
from EasyChatApp.utils import logger


def cronjob():
    try:
        TwitterTracker.objects.filter(created_on__lte=(datetime.datetime.now() - datetime.timedelta(minutes=60))).delete()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Twitter Tracker! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        pass
