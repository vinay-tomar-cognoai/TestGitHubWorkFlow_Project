import logging
import sys
import pytz
import math

from LiveChatApp.utils import *


logger = logging.getLogger(__name__)


def build_default_calendar(user_obj, LiveChatCalender):
    try:
        start_time = "00:00"
        end_time = "23:59"
        month = datetime.now().month
        year = datetime.now().year
        month = str(month)
        no_days = get_number_of_day(year, month)
        if not LiveChatCalender.objects.filter(event_date__month=int(month), event_date__year=int(year), created_by=user_obj):
            LiveChatCalender.objects.filter(
                event_date__month=int(month), event_date__year=int(year), created_by=user_obj).delete()
            for day in range(1, no_days + 1):
                today_date = datetime(int(year), int(month), int(day))
                LiveChatCalender.objects.create(
                    event_type="1", event_date=today_date, created_by=user_obj, start_time=start_time, end_time=end_time)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("build_default_calendar: %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def convert_to_calender(calender_objs):
    try:
        calender_list = []

        tz = pytz.timezone(settings.TIME_ZONE)

        first_row_cards = 0
        
        day_of_1st_date_of_month = calender_objs.first().event_date.astimezone(tz).strftime("%a")
        date_of_last_date_of_month = calender_objs.last().event_date.astimezone(tz).strftime("%d")

        current_month_year = calender_objs.first().event_date.astimezone(tz).strftime("%-m-%Y").split('-')
        current_month = current_month_year[0]
        current_year = current_month_year[1]

        prev_month, target_year1 = get_prev_month(current_month, current_year)
        next_month, target_year2 = get_next_month(current_month, current_year)

        prev_month_days = get_number_of_day(target_year1, prev_month)
        # next_month_days = get_number_of_day(target_year2, next_month)

        first_row_cards_dict = {'Sun': '7', 'Mon': '6', 'Tue': '5', 'Wed': '4', 'Thu': '3', 'Fri': '2', 'Sat': '1'}

        first_row_cards = int(first_row_cards_dict[day_of_1st_date_of_month])

        calender_objects_converted = 0
        first_row = []
        for card in range(DAYS_IN_WEEK - first_row_cards):
            first_row.append(prev_month_days - card)

        first_row.reverse()

        for card in range(first_row_cards):
            first_row.append(calender_objs[card])
            calender_objects_converted += 1

        calender_list.append(first_row)
        
        next_row_start = first_row_cards
        next_months_dates = 1

        no_of_rows_required_more = math.ceil((calender_objs.count() - first_row_cards) / DAYS_IN_WEEK)
            
        for row in range(no_of_rows_required_more):
            next_row_list = []
            for column in range(DAYS_IN_WEEK):
                if next_row_start < int(date_of_last_date_of_month):
                    next_row_list.append(calender_objs[next_row_start])
                    next_row_start += 1
                    calender_objects_converted += 1

            calender_list.append(next_row_list)    

        length_calender_list = len(calender_list)

        if len(calender_list[length_calender_list - 1]) < 7:
            while len(calender_list[length_calender_list - 1]) < 7:
                calender_list[length_calender_list - 1].append(next_months_dates)
                next_months_dates += 1
        
        return calender_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("convert_to_calender: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        calender_list = []
        return calender_list


def get_prev_month(month, year):
    try:
        month = int(month)
        year = int(year)

        if month - 1 < 1:
            month = 12
            year = year - 1
        else:
            month = month - 1
        return str(month), str(year) 
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_prev_month: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return str(month), str(year)   


def get_next_month(month, year):
    try:
        month = int(month)
        year = int(year)

        if month + 1 > 12:
            month = (month + 1) % 12
            year = year + 1
        else:
            month = month + 1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_next_month: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})     
    return str(month), str(year)
