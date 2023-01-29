import os
import sys
import json
import pytz

import datetime
from django.conf import settings
from EasyAssistApp.models import *


def cronjob():

    try:
        logger.info("Inside easyassist_auto_archive",
                    extra={'AppName': 'EasyAssist'})

        access_token_objs = CobrowseAccessToken.objects.all()
        for access_token in access_token_objs:
            auto_archive_session_timer = access_token.auto_archive_cobrowsing_session_timer * 60

            inactivity_datetime = datetime.datetime.now().astimezone(pytz.timezone(
                settings.TIME_ZONE)) - datetime.timedelta(seconds=auto_archive_session_timer)

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_archived=False, request_datetime__lte=inactivity_datetime, access_token=access_token)
            for cobrowse_io in cobrowse_io_objs:
                cobrowse_io.is_archived = True
                cobrowse_io.save()
        logger.info("Successfully exited from easyassist_auto_archive", extra={
                    'AppName': 'EasyAssist'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In easyassist_auto_archive: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})
