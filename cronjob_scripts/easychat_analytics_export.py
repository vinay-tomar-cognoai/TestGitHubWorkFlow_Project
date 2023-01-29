from EasyChatApp.models import AnalyticsExportRequest, Language

import re
import sys
import json
import pytz
import time as _time
from django.conf import settings
from datetime import datetime, time

import logging
from EasyChatApp.utils import export_easychat_analytics_file

from EasyChatApp.utils_analytics import get_supported_languages_list
logger = logging.getLogger(__name__)


def cronjob():
    try:
        is_large_date_range_data = is_large_data_processing_required()
        export_request_objs = AnalyticsExportRequest.objects.filter(
            is_processing=False, is_completed=False, bot__is_deleted=False).exclude(analytics_type="combined_global_export")

        if is_large_date_range_data:
            export_request_objs = export_request_objs.filter(
                is_large_date_range_data=True)
        else:
            export_request_objs = export_request_objs.filter(
                is_large_date_range_data=False)
        space_removing_pattern = re.compile(r'\s+')
        for export_request_obj in export_request_objs.iterator():
            try:
                # Adding this check here as well to avoid processing of objects which were marked as processing
                # after above queryset was retrieved. This could happen when 2 cronjobs are running simultaneously.
                if export_request_obj.is_processing:
                    continue
                export_request_obj.is_processing = True
                export_request_obj.save(update_fields=['is_processing'])
                start_time = _time.time()
                request_data = json.loads(export_request_obj.request_datadump)
                bot_pk = request_data["bot_pk"]
                start_date = request_data["start_date"]
                end_date = request_data["end_date"]
                type_of_analytics = export_request_obj.analytics_type
                channel_value = request_data.get("channel_value", "All")
                selected_language = request_data["selected_language"]
                dropdown_language = request_data.get("dropdown_language", "en")
                supported_languages = get_supported_languages_list(
                    selected_language, Language)
                filter_type_particular = request_data.get("filter_type_particular", "1")
                category_name = request_data.get("category_name", "All")
                email_id = re.sub(space_removing_pattern, '', export_request_obj.email_id)
                datetime_start = start_date.split("-")
                start_date = datetime(int(datetime_start[0]), int(
                    datetime_start[1]), int(datetime_start[2]))
                datetime_end = end_date.split("-")
                end_date = datetime(int(datetime_end[0]), int(
                    datetime_end[1]), int(datetime_end[2]))
                export_easychat_analytics_file(
                    request_data, export_request_obj.user, type_of_analytics, start_date, end_date, channel_value, bot_pk, filter_type_particular,
                    category_name, selected_language, supported_languages, dropdown_language, True, email_id, export_request_obj)
                export_request_obj.is_processing = False
                export_request_obj.time_taken = _time.time() - start_time
                export_request_obj.save(
                    update_fields=['time_taken', 'is_processing'])
            except Exception as e:
                export_request_obj.is_processing = False
                export_request_obj.save(update_fields=['is_processing'])
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Inside loop of easychat_analytics_export cronjob! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("easychat_analytics_export cronjob! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def is_large_data_processing_required():
    try:
        time_zone = pytz.timezone(settings.TIME_ZONE)
        current_time = datetime.now().astimezone(time_zone).time()
        allowed_start_time = time(0, 0)
        allowed_end_time = time(6, 0)
        if allowed_start_time <= current_time <= allowed_end_time:
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_large_data_processing_required %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return False
