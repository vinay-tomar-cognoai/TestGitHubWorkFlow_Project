from CampaignApp.models import CampaignExportRequest


# Making all the phone number masking false of already created objects
def make_all_campaign_export_masking_false():
    CampaignExportRequest.objects.all().update(masking_enabled=False)


print('Running make_all_campaign_export_masking_false... \n')

make_all_campaign_export_masking_false()
