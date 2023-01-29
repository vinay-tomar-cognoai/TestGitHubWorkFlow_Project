import json
import sys
import pytz
from datetime import datetime

from django.utils import timezone
from django.conf import settings

# Logger
import logging

logger = logging.getLogger(__name__)


def parse_sandbox_user_obj(sandbox_user_obj):
    sandbox_user_data = dict()
    try:
        sandbox_user_id = sandbox_user_obj.pk
        email_id = sandbox_user_obj.user.email

        enable_cobrowsing = sandbox_user_obj.enable_cobrowsing
        enable_inbound = sandbox_user_obj.enable_inbound
        enable_outbound = sandbox_user_obj.enable_outbound
        enable_reverse_cobrowsing = sandbox_user_obj.enable_reverse_cobrowsing
        enable_video_meeting = sandbox_user_obj.enable_video_meeting

        est = pytz.timezone(settings.TIME_ZONE)

        created_datetime = None
        if sandbox_user_obj.create_datetime:
            created_datetime = sandbox_user_obj.create_datetime.astimezone(
                est).strftime("%d %b %Y %I:%M %p")

        expire_date = None
        is_expiry_time_passed = False
        if sandbox_user_obj.expire_date:
            expire_date = sandbox_user_obj.expire_date.strftime("%d %b %Y")

            todays_date = timezone.now().date()
            if todays_date > sandbox_user_obj.expire_date:
                is_expiry_time_passed = True

        sandbox_user_data = {
            "sandbox_user_id": sandbox_user_id,
            "email_id": email_id,
            "enable_cobrowsing": enable_cobrowsing,
            "enable_inbound": enable_inbound,
            "enable_outbound": enable_outbound,
            "enable_reverse_cobrowsing": enable_reverse_cobrowsing,
            "enable_video_meeting": enable_video_meeting,
            "create_datetime": created_datetime,
            "expire_date": expire_date,
            "is_expiry_time_passed": is_expiry_time_passed,
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_sandbox_user_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return sandbox_user_data
