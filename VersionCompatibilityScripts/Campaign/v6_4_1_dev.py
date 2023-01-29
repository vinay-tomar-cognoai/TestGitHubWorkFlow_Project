from CampaignApp.models import CampaignAudienceLog, QuickReply, CampaignAudience
from CampaignApp.utils_validation import CampaignInputValidation
import logging
logger = logging.getLogger(__name__)
validation_obj = CampaignInputValidation()


def update_quick_replies():
    try:
        campaign_audience_log_objs = CampaignAudienceLog.objects.filter(campaign__bot__is_deleted=False)
        for campaign_audience_log_obj in campaign_audience_log_objs.iterator():
            old_quick_reply = campaign_audience_log_obj.quick_reply
            if old_quick_reply:
                for quick_reply in old_quick_reply.split(', '):
                    bot_obj = campaign_audience_log_obj.campaign.bot
                    quick_reply_obj = QuickReply.objects.filter(name=quick_reply, bot=bot_obj).first()
                    if not quick_reply_obj:
                        quick_reply_obj = QuickReply.objects.create(name=quick_reply, bot=bot_obj)
                    quick_reply_obj.audience_log.add(campaign_audience_log_obj)
                    campaign_audience_log_obj.quick_replies.add(quick_reply_obj)
    except Exception as e:
        logger.error("Error in update_quick_replies: %s", str(e), extra={'AppName': 'Campaign', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print('Running update_quick_replies()...\n')

update_quick_replies()


def update_invalid_phone_numbers():
    try:
        campaign_auidence_objs = CampaignAudience.objects.all().iterator()
        for campaign_auidence_obj in campaign_auidence_objs:
            mobile_number = campaign_auidence_obj.audience_id.replace('.0', '')
            mobile_number = validation_obj.removing_phone_non_digit_element(mobile_number)
            campaign_auidence_obj.audience_id = mobile_number
            campaign_auidence_obj.save(update_fields=['audience_id'])
    except Exception as e:
        logger.error("Error in update_invalid_phone_numbers: %s", str(e), extra={'AppName': 'Campaign', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print('Running update_invalid_phone_numbers()...\n')

update_invalid_phone_numbers()
