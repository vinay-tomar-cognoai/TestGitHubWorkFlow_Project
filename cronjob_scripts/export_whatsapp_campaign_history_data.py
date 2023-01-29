from datetime import datetime
from CampaignApp.models import CampaignHistoryExportRequest
from CampaignApp.utils_export import get_zip_file_path
from EasyChatApp.models import Bot
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses
from CampaignApp.utils import get_whatsapp_audience_log_data, logger, get_whatsapp_audience_reports
import json
import sys

from django.conf import settings
from cronjob_scripts.utils_campaign_cronjob_validator import check_if_cronjob_is_running, complete_cronjob_execution


def get_email_body(email_id, file_path, return_data, bot_name, status_filter):
    recipient_id = 'NA'
    phone_number = 'NA'
    status_filter = status_filter[0] if status_filter else "NA"
    if return_data.get('searched_type') == 'phone_number':
        phone_number = return_data.get('searched_value')
    elif return_data.get('searched_type') == 'recipient_id':
        recipient_id = return_data.get('searched_value')

    quick_filter = return_data.get('quick_reply_filter')
    if not quick_filter:
        quick_filter = 'NA'

    campaign_names = return_data.get('campaign_names')
    if not campaign_names:
        campaign_names = 'NA'

    template_names = ', '.join(
        return_data.get('selected_template_names'))
    if not template_names:
        template_names = 'NA'

    domain = settings.EASYCHAT_HOST_URL
    return f"""
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <title>Cogno AI</title>
                <style type="text/css" media="screen">
                </style>
            </head>
            <body>

            <div style="padding:1em;border:0.1em black solid;" class="container">
                <p>
                    Dear {email_id},
                </p>
                <p>
                    We have received a request to provide you with the WhatsApp Filtered Report.<br>
                    Please click on the link to download the file.
                    <a href="{domain}/{file_path}">click here</a><br><br>
                    <b>The applied filter for this report was as follows:</b><br>
                    <b>Phone Number:</b> {phone_number}<br>
                    <b>Recipient ID:</b> {recipient_id}<br>
                    <b>Campaign Name:</b> {campaign_names}<br>
                    <b>Bot Name:</b> {bot_name}<br>
                    <b>Quick Reply:</b> {quick_filter}<br>
                    <b>Template Name:</b> {template_names}<br>
                    <b>Status:</b> {status_filter} <br>
                </p>
                <p>
                    
                </p>
                
                <p>&nbsp;</p>"""


def cronjob():
    cronjob_detector_id = "campaign_whatsapp_export_cronjob"
    is_cronjob_exists, cronjob_tracker_obj = check_if_cronjob_is_running(
        cronjob_detector_id)
    if is_cronjob_exists:
        return
    try:
        whatsapp_campaign_history_export_request_objs = CampaignHistoryExportRequest.objects.filter(
            is_completed=False, is_whatsapp=True)

        for whatsapp_campaign_history_export_request_obj in whatsapp_campaign_history_export_request_objs.iterator():
            try:
                request_data = json.loads(
                    whatsapp_campaign_history_export_request_obj.request_data)
                bot_pk = request_data['bot_pk']
                bot_obj = Bot.objects.filter(
                    pk=bot_pk, is_deleted=False).first()
                email_id = request_data['email_id']
                status_filter = request_data['status_filter']
                if not bot_obj:
                    continue
                bot_name = bot_obj.name

                audience_log_objs, return_data = get_whatsapp_audience_log_data(
                    request_data, bot_obj, True)
                campaign_name = str(audience_log_objs[0].campaign)

                file_path = get_whatsapp_audience_reports(
                    audience_log_objs, request_data)

                if not file_path:
                    logger.error("campaign_export cronjob: filepath not found for request for export_request with id %s", str(
                        whatsapp_campaign_history_export_request_obj.pk), extra={'AppName': 'Campaign'})
                    continue

                if len(file_path) == 1:
                    file_path = 'files/' + file_path[0]
                else:
                    export_zip_file_path = "files/wpm_reports/bot-" + \
                        str(bot_pk) + "/CampaignWhatsAppReport-" + \
                        campaign_name + "_" + str(datetime.now()) + ".zip"

                    file_path = get_zip_file_path(
                        file_path, export_zip_file_path)

                body = get_email_body(email_id, file_path, return_data, bot_name, status_filter)

                config = get_developer_console_settings()

                body += config.custom_report_template_signature

                body += """</div></body>"""

                send_email_to_customer_via_awsses(
                    email_id, f"WhatsApp Filtered Report for {bot_name} - {email_id}", body)

                whatsapp_campaign_history_export_request_obj.is_completed = True
                whatsapp_campaign_history_export_request_obj.save(update_fields=['is_completed'])

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("cronjob: %s at %s", str(e), str(
                    exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    complete_cronjob_execution(cronjob_tracker_obj)
