from LiveChatApp.models import *


def add_ameyo_livechat_whatsapp_bsp():
    try:
        ameyo_livechat_bsp = LiveChatWhatsAppServiceProvider.objects.filter(name=1).first()

        if not ameyo_livechat_bsp:
            LiveChatWhatsAppServiceProvider.objects.create(name="1", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_ameyo_webhook.py")

    except Exception as e:
        logger.error("Error in add_ameyo_livechat_whatsapp_bsp: %s", str(e), extra={'AppName': 'LiveChat'})


print("Running add_ameyo_livechat_whatsapp_bsp...\n")

add_ameyo_livechat_whatsapp_bsp()
