import re
import json
import sys
import pytz

from datetime import datetime, timedelta
from django.conf import settings

from CampaignApp.constants import CAMPAIGN_DRAFT, CAMPAIGN_IN_PROGRESS, CAMPAIGN_PROCESSED, CAMPAIGN_SCHEDULED, TIME_FORMAT, DATE_FORMAT_b_d_y

# Logger
import logging

from CampaignApp.models import CampaignVoiceBotAnalytics, CampaignVoiceBotSetting, CampaignRCSDetailedAnalytics

logger = logging.getLogger(__name__)


def get_campaign_status(campaign_obj, CampaignVoiceBotSetting):
    try:
        if campaign_obj.channel.name != 'Voice Bot':
            return campaign_obj.status

        voice_bot_obj = CampaignVoiceBotSetting.objects.filter(
            campaign=campaign_obj)

        if voice_bot_obj and campaign_obj.status == CAMPAIGN_SCHEDULED:
            voice_bot_obj = voice_bot_obj.first()

            start_date = voice_bot_obj.start_date
            start_time = voice_bot_obj.start_time

            today_date = datetime.now().date()
            today_time = datetime.now().time()

            if today_date > start_date or (today_date == start_date and today_time >= start_time):
                campaign_obj.status = CAMPAIGN_IN_PROGRESS
                campaign_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_campaign_status: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

    return campaign_obj.status


def parse_campaign_details(campaign_obj, CampaignAnalytics, CampaignAPI):
    active_campaign = dict()
    try:
        start_datetime = 'NA'
        processed_datetime = 'NA'
        campaign_status = campaign_obj.status 
        system_timezone = pytz.timezone(settings.TIME_ZONE)
        if campaign_status not in [CAMPAIGN_DRAFT, CAMPAIGN_SCHEDULED]:
            start_datetime = campaign_obj.start_datetime
            start_datetime = start_datetime.astimezone(
                system_timezone).strftime("%d %b %Y %I:%M %p")
            
            if campaign_obj.show_processed_datetime and campaign_status != CAMPAIGN_IN_PROGRESS:
                processed_datetime = campaign_obj.processed_datetime
                processed_datetime = processed_datetime.astimezone(
                    system_timezone).strftime("%d %b %Y %I:%M %p")            
        
        create_datetime = campaign_obj.create_datetime
        create_datetime = create_datetime.astimezone(
            system_timezone).strftime("%d %b %Y %I:%M:%S %p")
        active_campaign = {
            "campaign_id": str(campaign_obj.id),
            "name": campaign_obj.name,
            "channel": campaign_obj.channel.name,
            "status": campaign_status,
            "start_datetime": start_datetime,
            "create_datetime": create_datetime,
            "processed_datetime": processed_datetime,
            "channel_value": campaign_obj.channel.value,
            "times_campaign_tested": campaign_obj.times_campaign_tested,
            "is_source_dashboard": campaign_obj.is_source_dashboard
        }

        channel_related_info = {}
        if campaign_obj.channel.name == "Whatsapp Business":
            channel_related_info = get_whatsapp_channel_info(
                campaign_obj, CampaignAPI, CampaignAnalytics)
        elif campaign_obj.channel.name == "Voice Bot":
            channel_related_info = get_voice_bot_channel_info(campaign_obj)
        elif campaign_obj.channel.name == "RCS":
            channel_related_info = get_rcs_campaign_info(campaign_obj)

        active_campaign.update(channel_related_info)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_campaign_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return active_campaign


def get_whatsapp_channel_info(campaign_obj, CampaignAPI, CampaignAnalytics):
    channel_related_info = {}
    try:
        campaign_analytics_obj = CampaignAnalytics.objects.filter(
            campaign=campaign_obj).first()

        if campaign_analytics_obj is None:
            message_sent = 0
            message_delivered = 0
            message_read = 0
            message_unsuccessful = 0
            message_replied = 0
            message_processed = 0
            total_audience = campaign_obj.batch.total_audience if campaign_obj.batch else 0
            open_rate = 0
            test_sent = 0
            test_failed = 0
            
        else:
            message_sent = campaign_analytics_obj.message_sent
            message_delivered = campaign_analytics_obj.message_delivered
            message_read = campaign_analytics_obj.message_read
            message_unsuccessful = campaign_analytics_obj.message_unsuccessful
            message_replied = campaign_analytics_obj.message_replied
            message_processed = campaign_analytics_obj.message_processed
            total_audience = campaign_analytics_obj.total_audience
            open_rate = campaign_analytics_obj.open_rate()
            test_sent = campaign_analytics_obj.test_message_sent
            test_failed = campaign_analytics_obj.test_message_unsuccessful
            
        batch_name = campaign_obj.batch.batch_name if campaign_obj.batch else "-"
        template_name = campaign_obj.campaign_template.template_name if campaign_obj.campaign_template else "-"
            
        bot_wsp_obj = CampaignAPI.objects.get(
            campaign=campaign_obj).campaign_bot_wsp_config

        whatsapp_bsp_name = "-"
        if bot_wsp_obj:
            whatsapp_bsp_name = bot_wsp_obj.whatsapp_service_provider.get_name_display()

        channel_related_info = {
            'message_sent': message_sent,
            'message_delivered': message_delivered,
            'message_read': message_read,
            'message_replied': message_replied,
            'message_unsuccessful': message_unsuccessful,
            'message_processed': message_processed,
            'total_audience': total_audience,
            'open_rate': open_rate,
            'whatsapp_bsp_name': whatsapp_bsp_name,
            'batch_name': batch_name,
            'template_name': template_name,
            'test_sent': test_sent,
            'test_failed': test_failed
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_whatsapp_channel_info %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return channel_related_info


def get_voice_bot_channel_info(campaign_obj):
    channel_related_info = {}
    try:
        campaign_analytics_obj = CampaignVoiceBotAnalytics.objects.filter(
            campaign=campaign_obj).first()

        if campaign_analytics_obj is None:
            call_scheduled = 0
            call_initiated = 0
            call_completed = 0
            call_failed = 0
            call_in_progress = 0
            call_invalid = 0
        else:
            call_scheduled = campaign_analytics_obj.call_scheduled
            call_initiated = campaign_analytics_obj.call_initiated
            call_completed = campaign_analytics_obj.call_completed
            call_failed = campaign_analytics_obj.call_failed
            call_in_progress = campaign_analytics_obj.call_in_progress
            call_invalid = campaign_analytics_obj.call_invalid

        campaign_info = get_voice_bot_campaign_info(campaign_obj)

        channel_related_info = {
            'call_scheduled': call_scheduled,
            'call_initiated': call_initiated,
            'call_completed': call_completed,
            'call_failed': call_failed,
            'call_in_progress': call_in_progress,
            'call_invalid': call_invalid,
            'total_audience': campaign_obj.total_audience,
        }

        channel_related_info.update(campaign_info)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_voice_bot_channel_info %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return channel_related_info


def get_voice_bot_campaign_info(campaign_obj):
    campaign_info = {}
    try:
        voice_bot_obj = CampaignVoiceBotSetting.objects.filter(
            campaign=campaign_obj)

        if not voice_bot_obj:
            return campaign_info

        voice_bot_obj = voice_bot_obj.first()
        retry_setting = voice_bot_obj.retry_setting

        if voice_bot_obj.is_saved:
            start_date = voice_bot_obj.start_date.strftime('%b, %d, %Y')
            start_time = voice_bot_obj.start_time.strftime(TIME_FORMAT)
            end_date = voice_bot_obj.end_date.strftime('%b, %d, %Y')
            end_time = voice_bot_obj.end_time.strftime(TIME_FORMAT)
        else:
            start_date = '-'
            start_time = ''
            end_date = '-'
            end_time = ''

        on_status = []
        if retry_setting.is_busy_enabled:
            on_status.append('Busy')
        
        if retry_setting.is_no_answer_enabled:
            on_status.append('No Answer')
        
        if retry_setting.is_failed_enabled:
            on_status.append('Failed')

        campaign_info = {
            'caller_id': voice_bot_obj.caller_id,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
            'retry_mechanism': retry_setting.mechanism,
            'no_of_retries': retry_setting.no_of_retries,
            'retry_interval': retry_setting.retry_interval,
            'is_busy_enabled': retry_setting.is_busy_enabled,
            'is_no_answer_enabled': retry_setting.is_no_answer_enabled,
            'is_failed_enabled': retry_setting.is_failed_enabled,
            'on_status': on_status,
            'url': voice_bot_obj.url,
            'app_id': voice_bot_obj.app_id,
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_voice_bot_campaign_info %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return campaign_info


def get_rcs_campaign_info(campaign_obj):
    campaign_related_info = {}
    tz = pytz.timezone(settings.TIME_ZONE)

    try:
        campaign_analytics_obj = CampaignRCSDetailedAnalytics.objects.filter(
            campaign=campaign_obj).first()
        if campaign_analytics_obj is None:
            submitted = 0
            sent = 0
            delivered = 0
            read = 0
            failed = 0
            replied = 0
            if campaign_obj.campaign_template_rcs != None:
                template_name = campaign_obj.campaign_template_rcs.template_name
                template_type = campaign_obj.campaign_template_rcs.get_message_type_display()
            else:
                template_name = "NA"
                template_type = "NA"
            start_date_time = "NA"
            end_date_time = "NA"
        else:
            submitted = campaign_analytics_obj.submitted
            sent = campaign_analytics_obj.sent
            delivered = campaign_analytics_obj.delivered
            read = campaign_analytics_obj.read
            failed = campaign_analytics_obj.failed
            replied = campaign_analytics_obj.replied
            template_name = campaign_obj.campaign_template_rcs.template_name
            template_type = campaign_obj.campaign_template_rcs.get_message_type_display()
            start_date_time = campaign_analytics_obj.start_time.astimezone(tz).strftime(DATE_FORMAT_b_d_y)
            end_date_time = campaign_analytics_obj.end_time.astimezone(tz).strftime(DATE_FORMAT_b_d_y)

        campaign_related_info = {
            'total_audience': campaign_obj.total_audience,
            'submitted': submitted,
            'sent': sent,
            'delivered': delivered,
            'read': read,
            'failed': failed,
            'replied': replied,
            'template_name': template_name,
            'template_type': template_type,
            'start_date_time': start_date_time,
            'end_date_time': end_date_time
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_rcs_campaign_info %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return campaign_related_info


def parse_campaign_batch_details(batch_obj):
    active_batch = dict()
    try:
        create_datetime = batch_obj.created_datetime
        est = pytz.timezone(settings.TIME_ZONE)
        create_datetime = create_datetime.astimezone(
            est).strftime("%d %b %Y %I:%M:%S %p")

        active_campaigns = []
        active_campaign_objs = batch_obj.campaigns.all()
        for active_campaign in active_campaign_objs:
            active_campaigns.append(active_campaign.name)

        active_batch = {
            "batch_id": str(batch_obj.pk),
            "batch_name": batch_obj.batch_name,
            "created_on": create_datetime,
            "total_contacts": batch_obj.total_audience,
            "opted_in": batch_obj.total_audience_opted,
            "active_campaigns": active_campaigns,
            "batch_header_meta": json.loads(batch_obj.batch_header_meta),
            "sample_data": json.loads(batch_obj.sample_data),
            "file_path": batch_obj.file_path,
            "file_name": batch_obj.file_name,
            "rcs_enabled": batch_obj.total_audience_opted,
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_campaign_batch_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return active_batch


def parse_campaign_template_details(template_obj):
    active_template = dict()
    try:
        created_datetime = template_obj.created_datetime
        est = pytz.timezone(settings.TIME_ZONE)
        created_datetime = created_datetime.astimezone(
            est).strftime("%d %b %Y %I:%M:%S %p")

        language_obj = template_obj.language
        language = None
        if language_obj is not None:
            language = language_obj.title

        category_obj = template_obj.category
        category = None
        if category_obj is not None:
            category = category_obj.title

        status_obj = template_obj.status
        status = None
        if status_obj is not None:
            status = status_obj.title

        template_type_obj = template_obj.template_type
        template_type = None
        if template_type_obj is not None:
            template_type = template_type_obj.title

        template_variables = re.findall(
            r'\{\{(.*?)\}\}', template_obj.template_body)

        dynamic_cta_url_variable = re.findall(
            r'\{\{(.*?)\}\}', str(template_obj.cta_link))
        
        header_variable = re.findall(
            r'\{\{(.*?)\}\}', str(template_obj.template_header))
        
        template_metadata = json.loads(template_obj.template_metadata)
        
        button_type = template_metadata.get('button_type')
        callus_text = template_metadata.get('callus_text')
        callus_number = template_metadata.get('callus_number')
        template_qr_1 = template_metadata.get('template_qr_1')
        template_qr_2 = template_metadata.get('template_qr_2')
        template_qr_3 = template_metadata.get('template_qr_3')
        document_file_name = template_metadata.get('document_file_name', '-')

        active_template = {
            "template_pk": str(template_obj.pk),
            "template_name": template_obj.template_name,
            "type": template_type,
            "language": language,
            "category": category,
            "status": status,
            "created_datetime": created_datetime,
            "template_header": template_obj.template_header,
            "template_body": template_obj.template_body,
            "template_footer": template_obj.template_footer,
            "template_button_type": button_type,
            "cta_text": template_obj.cta_text,
            "cta_link": template_obj.cta_link,
            "template_callus_text": callus_text,
            "template_callus_number": callus_number,
            "template_qr_1": template_qr_1,
            "template_qr_2": template_qr_2,
            "template_qr_3": template_qr_3,
            "attachment_src": template_obj.attachment_src,
            "template_variables": template_variables,
            "dynamic_cta_url_variable": dynamic_cta_url_variable,
            "header_variable": header_variable,
            "document_file_name": document_file_name
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_campaign_template_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return active_template


def parse_rcs_campaign_template_details(template_obj):
    active_template = dict()
    try:
        created_datetime = template_obj.created_datetime
        est = pytz.timezone(settings.TIME_ZONE)
        created_datetime = created_datetime.astimezone(
            est).strftime("%d %b %Y %I:%M:%S %p")

        message_type = '-'
        if template_obj.message_type == '1':
            message_type = 'Text'
        elif template_obj.message_type == '2':
            message_type = 'Media'
        elif template_obj.message_type == '3':
            message_type = 'Rich Card'
        elif template_obj.message_type == '4':
            message_type = 'Carousel'

        suggested_reply_types = []
        template_metadata = json.loads(template_obj.template_metadata)
        suggested_reply = template_metadata['suggested_reply']
        for reply in suggested_reply:
            if len(suggested_reply_types) == 4:  # Since there are maximum 4 types of suggested reply
                break
            if reply['type'] == 'simple_reply':
                reply_type = 'Simple Reply'
            elif reply['type'] == 'open_url':
                reply_type = 'Open URL'
            elif reply['type'] == 'dial_action':
                reply_type = 'Dial Action'
            elif reply['type'] == 'share_location':
                reply_type = 'Share Location'
            if reply_type not in suggested_reply_types:
                suggested_reply_types.append(reply_type)

        if len(suggested_reply_types):
            suggested_reply_types = ', '.join(suggested_reply_types)
        else:
            suggested_reply_types = '-'
        
        active_template = {
            "template_pk": str(template_obj.pk),
            "template_name": template_obj.template_name,
            "message_type": message_type,
            "created_datetime": created_datetime,
            "suggested_reply_type": suggested_reply_types,
            "template_metadata": template_metadata,
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_rcs_campaign_template_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return active_template
