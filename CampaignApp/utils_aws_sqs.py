import sys
import logging
from CampaignApp.constants import CACHE_KEY_CAMPAIGN_BOT_WSP_CONFIG_OBJ
from django.core.cache import cache
import boto3
from django.conf import settings
import json

logger = logging.getLogger(__name__)


def send_message_into_campaign_sqs(str_message_body, sqs_client, aws_sqs_url, delay_seconds=10):
    try:
        queue_url = aws_sqs_url
        # Send message to SQS queue
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            DelaySeconds=delay_seconds,
            MessageBody=str_message_body
        )
        return response
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_message_into_campaign_sqs ERROR: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
        return None


def send_delivery_packet_to_sqs(request_packet, bot_obj, CampaignWhatsAppServiceProvider, CampaignBotWSPConfig):
    try:
        delivery_status_updated = "statuses" in request_packet.keys() or "delivery_status" in request_packet.keys()
        if delivery_status_updated:
            # for ameyo
            bsp_name = "1"
            dynamic_prefix = str(bot_obj.pk) + '_' + bsp_name

            bot_wsp_config = cache.get(
                CACHE_KEY_CAMPAIGN_BOT_WSP_CONFIG_OBJ + dynamic_prefix)

            if not bot_wsp_config:
                bot_wsp_config = CampaignBotWSPConfig.objects.filter(
                    bot=bot_obj, whatsapp_service_provider__name=bsp_name).first()
                cache.set(CACHE_KEY_CAMPAIGN_BOT_WSP_CONFIG_OBJ +
                          dynamic_prefix, bot_wsp_config, settings.CACHE_TIME)

            if bot_wsp_config.enable_delivery_queuing_system:
                
                aws_key_id, aws_secret_access_key, aws_sqs = bot_wsp_config.aws_key_id, bot_wsp_config.aws_secret_access_key, bot_wsp_config.aws_sqs_delivery_packets
                sqs_client = boto3.client(
                    'sqs', 'ap-south-1', aws_access_key_id=aws_key_id, aws_secret_access_key=aws_secret_access_key)

                sqs_domain = f'{settings.EASYCHAT_HOST_URL}/campaign/lambda/push-delivery-packets/'
                sqs_packet = {
                    "url": sqs_domain,
                    "request_packet": request_packet,
                    "delivery_status_updated": delivery_status_updated,
                    "event_name": "SEND_DELIVERY_PACKET"
                }
                send_message_into_campaign_sqs(
                    json.dumps(sqs_packet), sqs_client, aws_sqs)

                return True

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_message_into_campaign_sqs ERROR: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return False
