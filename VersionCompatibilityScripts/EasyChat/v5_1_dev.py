from EasyChatApp.models import WhatsAppServiceProvider, WhatsAppWebhook, Channel, LiveChatBotChannelWebhook
from LiveChatApp.models import LiveChatWhatsAppServiceProvider
from CampaignApp.models import CampaignWhatsAppServiceProvider, CampaignAPI, CampaignBotWSPConfig


def create_wsp_objs():
    
    # WhatsAppServiceProvider.objects.create(name="1", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_ameyo_webhook.py")
    # WhatsAppServiceProvider.objects.create(name="2", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_gupshup_webhook.py")
    WhatsAppServiceProvider.objects.create(name="3", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_rml_webhook.py")
    # WhatsAppServiceProvider.objects.create(name="4", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_acl_webhook.py")
    # WhatsAppServiceProvider.objects.create(name="5", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_netcore_webhook.py")

    # LiveChatWhatsAppServiceProvider.objects.create(name="1", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_ameyo_webhook.py")
    # LiveChatWhatsAppServiceProvider.objects.create(name="2", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_gupshup_webhook.py")
    LiveChatWhatsAppServiceProvider.objects.create(name="3", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_rml_webhook.py")
    # LiveChatWhatsAppServiceProvider.objects.create(name="4", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_acl_webhook.py")
    # LiveChatWhatsAppServiceProvider.objects.create(name="5", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_netcore_webhook.py")

    # CampaignWhatsAppServiceProvider.objects.create(name="1", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_ameyo_webhook.py")
    # CampaignWhatsAppServiceProvider.objects.create(name="2", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_gupshup_webhook.py")
    CampaignWhatsAppServiceProvider.objects.create(name="3", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_rml_webhook.py")
    # CampaignWhatsAppServiceProvider.objects.create(name="4", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_acl_webhook.py")
    # CampaignWhatsAppServiceProvider.objects.create(name="5", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_netcore_webhook.py")


def update_existing_whatsapp_webhook_objects_to_rml():

    easychat_rml_wsp_obj = WhatsAppServiceProvider.objects.get(name="3")

    webhook_objs = WhatsAppWebhook.objects.all()
    for webhook_obj in webhook_objs:
        webhook_obj.whatsapp_service_provider = easychat_rml_wsp_obj
        webhook_obj.save()

    livechat_rml_wsp_obj = LiveChatWhatsAppServiceProvider.objects.get(name="3")
    channel_obj = Channel.objects.get(name="WhatsApp")
    livechat_webhook_objs = LiveChatBotChannelWebhook.objects.filter(channel=channel_obj)

    for livechat_webhook_obj in livechat_webhook_objs:
        livechat_webhook_obj.whatsapp_service_provider = livechat_rml_wsp_obj
        livechat_rml_wsp_obj.save()


def update_existing_campaign_api_objs():

    campaign_api_objs = CampaignAPI.objects.all()

    wsp_obj = CampaignWhatsAppServiceProvider.objects.get(name="3")

    file_obj = open("cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_rml_webhook.py", "r")
    code = file_obj.read()

    for campaign_api_obj in campaign_api_objs:
        try:
            bot_wsp_obj = CampaignBotWSPConfig.objects.get(bot=campaign_api_obj.campaign.bot, whatsapp_service_provider=wsp_obj)
        except:
            bot_wsp_obj = CampaignBotWSPConfig.objects.create(bot=campaign_api_obj.campaign.bot, whatsapp_service_provider=wsp_obj, code=code)
        bot_wsp_obj.save()

        campaign_api_obj.campaign_bot_wsp_config = bot_wsp_obj
        campaign_api_obj.save()


create_wsp_objs()
update_existing_whatsapp_webhook_objects_to_rml()
update_existing_campaign_api_objs()
