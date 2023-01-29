from CampaignApp.models import *


def add_rcs_bot_channel_in_campaign():
    try:
        rcs_channel = CampaignChannel.objects.filter(name="RCS")

        if not rcs_channel:
            CampaignChannel.objects.create(
                name="RCS",
                description="Start engaging with your customers by using the most popular upgraded version of SMS with rich media texts.",
                logo="files/Campaign/google_rcs.svg",
                value="rcs",
                order=2,
            )

    except Exception as e:
        logger.error("Error in add_rcs_bot_channel_in_campaign: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running add_rcs_bot_channel_in_campaign...\n")

add_rcs_bot_channel_in_campaign()


def add_ameyo_whatsapp_bsp():
    try:
        ameyo_campaign_bsp = CampaignWhatsAppServiceProvider.objects.filter(name=1).first()

        if not ameyo_campaign_bsp:
            CampaignWhatsAppServiceProvider.objects.create(name="1", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_ameyo_webhook.py")

    except Exception as e:
        logger.error("Error in add_ameyo_whatsapp_bsp: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running add_ameyo_whatsapp_bsp...\n")

add_ameyo_whatsapp_bsp()
