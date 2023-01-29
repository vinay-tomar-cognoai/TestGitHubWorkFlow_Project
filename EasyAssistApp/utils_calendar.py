import logging
import sys

from EasyAssistApp.utils import *


logger = logging.getLogger(__name__)


def build_default_calendar(user_obj, CobrowseCalendar):
    try:
        start_time = "00:00"
        end_time = "23:59"
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        month = str(month)
        no_days = get_number_of_day(year, month)
        if not CobrowseCalendar.objects.filter(event_date__month=int(month), event_date__year=int(year), created_by=user_obj):
            CobrowseCalendar.objects.filter(
                event_date__month=int(month), event_date__year=int(year), created_by=user_obj).delete()
            for day in range(1, no_days + 1):
                today_date = datetime.datetime(int(year), int(month), int(day))
                CobrowseCalendar.objects.create(
                    event_type="1", event_date=today_date, created_by=user_obj, start_time=start_time, end_time=end_time)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("build_default_calendar: %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistApp'})
