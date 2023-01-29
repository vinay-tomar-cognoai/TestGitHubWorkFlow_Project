import re
import json
import sys
import pytz

from django.conf import settings

# Logger
import logging
logger = logging.getLogger(__name__)


def parse_pdf_details(pdf_obj, EasyPDFSearcherAnalytics):
    active_pdf = dict()
    try:
        pdf_analytics_obj = EasyPDFSearcherAnalytics.objects.filter(
            pdf_searcher=pdf_obj).first()

        if pdf_analytics_obj is None:
            click_count = 0
            search_count = 0
            open_rate = 0
        else:
            click_count = pdf_analytics_obj.click_count
            search_count = pdf_analytics_obj.search_count
            open_rate = pdf_analytics_obj.open_rate()

        created_datetime = pdf_obj.created_datetime
        est = pytz.timezone(settings.TIME_ZONE)
        created_datetime = created_datetime.astimezone(
            est).strftime("%d %b %Y %I:%M:%S %p")

        pdf_status = pdf_obj.status
        pdf_id = str(pdf_obj.key)
        pdf_name = pdf_obj.name
        important_pages = pdf_obj.important_pages
        skipped_pages = pdf_obj.skipped_pages
        file_path = pdf_obj.file_path
        active_pdf = {
            "pdf_id": pdf_id,
            "name": pdf_name,
            "status": pdf_status,
            "click_count": click_count,
            "search_count": search_count,
            "open_rate": open_rate,
            "create_datetime": created_datetime,
            "important_pages": important_pages,
            "skipped_pages": skipped_pages,
            "file_path": file_path
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_pdf_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})

    return active_pdf
