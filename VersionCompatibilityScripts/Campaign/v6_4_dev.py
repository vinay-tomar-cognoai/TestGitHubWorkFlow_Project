from CampaignApp.models import Campaign, CampaignAudienceLog, CampaignChannel, CampaignWhatsAppServiceProvider
from LiveChatApp.models import LiveChatWhatsAppServiceProvider
from EasyChatApp.models import WhatsAppServiceProvider
from django.db.models import Value
from django.db.models.functions import Replace


def update_scripts_path_for_whatsapp_provider():
    
    WhatsAppServiceProvider.objects.exclude(default_code_file_path__contains='cronjob_scripts').update(
        default_code_file_path=Replace('default_code_file_path', Value('scripts/'), Value('cronjob_scripts/'))
    )

    LiveChatWhatsAppServiceProvider.objects.exclude(default_code_file_path__contains='cronjob_scripts').update(
        default_code_file_path=Replace('default_code_file_path', Value('scripts/'), Value('cronjob_scripts/'))
    )

    CampaignWhatsAppServiceProvider.objects.exclude(default_code_file_path__contains='cronjob_scripts').update(
        default_code_file_path=Replace('default_code_file_path', Value('scripts/'), Value('cronjob_scripts/'))
    )


# Making all the is_deleted true of already created channel objects of rcs and voice
def disable_all_bots_rcs_voice_channel():
    CampaignChannel.objects.filter(value__in=["rcs", "voicebot"]).update(is_deleted=True)


# Adding campaign to all audiences
def add_campaign_to_all_audience():
    campaign_objs = Campaign.objects.all()
    audience_logs = CampaignAudienceLog.objects.filter(
        campaign__in=campaign_objs, audience__campaign=None)

    for aud_log in audience_logs.iterator():
        aud_log.audience.campaign = aud_log.campaign
        aud_log.audience.save(update_fields=['campaign'])


print("Running update_scripts_path_for_whatsapp_provider...\n")

update_scripts_path_for_whatsapp_provider()

print('Running disable_all_bots_rcs_voice_channel... \n')

disable_all_bots_rcs_voice_channel()

print('Running add_campaign_to_all_audience... \n')

add_campaign_to_all_audience()
