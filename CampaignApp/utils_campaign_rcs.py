from CampaignApp.utils import *
from CampaignApp.models import *
import re


def save_rcs_campaign_template(bot_obj, template_data, template_name):
    try:
        template_obj = CampaignRCSTemplate.objects.filter(
            bot=bot_obj, template_name=template_name, is_deleted=False)

        if template_obj.exists():
            template_obj = template_obj.first()
            template_obj.template_metadata = json.dumps(template_data)
            template_obj.save()
        else:
            CampaignRCSTemplate.objects.create(
                bot=bot_obj,
                template_name=template_name,
                message_type=template_data['message_type'],
                template_metadata=json.dumps(template_data),
            )

        return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_rcs_campaign_template: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return False


def save_rcs_campaign_template_external(bot_obj, template_data, template_name):
    try:
        template_obj = CampaignRCSTemplate.objects.filter(
            bot=bot_obj, template_name=template_name, is_deleted=False)

        if not template_obj.exists():
        
            campaign_template_obj_rcs = CampaignRCSTemplate.objects.create(
                bot=bot_obj,
                template_name=template_name,
                message_type=template_data['message_type'],
                template_metadata=json.dumps(template_data),
            )

        return campaign_template_obj_rcs

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_rcs_campaign_template_external: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return None


"""
function: validate_rich_and_carousel_cards
input params:
    template_data: All the details of the Rich Card/Carousel Cards RCS Template
    validation_obj: Object of EasyChatInputValidation Class to perform validations on user input

It validates card title, media url and description,
And then calls validate_suggested_reply to validates all the suggested replies.
Returns None if no error is present, else returns the error message.
"""


def validate_rich_and_carousel_cards(template_data, validation_obj):
    try:
        error_message = None
        card_title = template_data["card_title"]
        card_title = str(template_data["card_title"]).strip()
        card_title = validation_obj.remo_complete_html_and_special_tags(card_title)
        if card_title == "":
            error_message = "Card title cannot be empty!"
        if len(card_title) > 50:
            error_message = "Card title cannot exceed 50 characters!"

        card_media_url = template_data["card_media_url"]
        if not validation_obj.is_valid_url(card_media_url):
            error_message = "Please enter a valid media URL!"

        card_description = template_data["card_description"]
        card_description = str(template_data["card_description"]).strip()
        if card_description == "":
            error_message = "Card description cannot be empty!"
        if len(card_description) > 1000:
            error_message = "Card description cannot exceed 1000 characters!"

        if error_message is not None:
            return error_message

        error_message = validate_suggested_reply(
            template_data["card_reply"], validation_obj)

        return error_message

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("validate_rich_and_carousel_cards: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return "Error in saving template!"


"""
function: validate_suggested_reply
input params:
    suggested_reply: Suggested Replies of the card (Rich card/Carousel) or the template
    validation_obj: Object of EasyChatInputValidation Class to perform validations on user input

It validates each and every suggested reply depending on the type of the reply.
Returns None if no error is present, else returns the error message.
"""


def validate_suggested_reply(suggested_reply, validation_obj):
    try:
        error_message = None
        if len(suggested_reply) >= 11:
            return "Maximum 11 replies are supported!"
        for reply in suggested_reply:

            if reply['type'] not in ["simple_reply", "open_url", "dial_action", "share_location"]:
                error_message = 'Reply types can only be \'simple_reply\', \'open_url\', \'dial_action\' or \'share_location\'.'
                return error_message

            card_suggested_text = str(reply['card_suggested_text']).strip()
            card_suggested_postback = str(
                reply['card_suggested_postback']).strip()

            if card_suggested_text == '':
                error_message = 'Suggested Text cannot be empty!'
                return error_message

            if len(card_suggested_text) > 25:
                error_message = 'The size of the reply text exceeds the maximum limit of 25 characters!'
                return error_message

            if card_suggested_postback == '':
                error_message = 'Suggested Postback cannot be empty!'
                return error_message

            if len(card_suggested_postback) > 25:
                error_message = 'The size of the reply postback text exceeds the maximum limit of 25 characters!'
                return error_message

            if reply['type'] == 'open_url':
                if not validation_obj.is_valid_url(reply['url_to_open']):
                    error_message = 'Please enter a valid URL to open!'
                    return error_message

            if reply['type'] == 'dial_action':
                regex = '\+[0-9]{1,3}[0-9]{4,14}'
                if not re.match(regex, reply['dial_action_number']):
                    error_message = 'Please enter a valid Dial Action number!'
                    return error_message
                else:
                    if not reply['dial_action_number'][1:].isdecimal():
                        error_message = 'Please enter a valid Dial Action number!'
                        return error_message

            if reply['type'] == 'share_location':
                if not validation_obj.is_valid_latitude(reply['location_latitude']):
                    error_message = 'Please enter a valid latitude!'
                    return error_message

                if not validation_obj.is_valid_longitude(reply['location_longitude']):
                    error_message = 'Please enter a valid longitude!'
                    return error_message

                location_label = str(reply['location_label']).strip()
                if location_label == '':
                    error_message = 'Please enter a valid location label!'
                    return error_message

                reply['location_label'] = location_label

            reply['card_suggested_text'] = card_suggested_text
            reply['card_suggested_postback'] = card_suggested_postback

            if error_message is not None:
                return error_message

        return error_message

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("validate_suggested_reply: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return "Error in saving template!"


def parse_text_message_type(metadata): 
    try:
        template_text = metadata["text_message"]
        suggested_reply = metadata["suggested_reply"]
        return template_text, suggested_reply

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_text_message_type %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CampaignApp', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return "", []


def parse_media_message_type(metadata): 
    try:
        media_url = metadata["media_url"]
        suggested_reply = metadata["suggested_reply"]
        return media_url, suggested_reply

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_text_message_type %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CampaignApp', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return "", []


def parse_card_message_type(metadata): 
    try:
        suggested_reply = []
        card_content = {}
        card_content["card_title"] = metadata["card_title"]
        card_content["card_media_url"] = metadata["card_media_url"]
        card_content["card_description"] = metadata["card_description"]
        card_content["card_reply"] = metadata["card_reply"]
        if "suggested_reply" in metadata:
            suggested_reply = metadata["suggested_reply"]
            
        return card_content, suggested_reply

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_text_message_type %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CampaignApp', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return {}, []


def parse_carousel_message_type(metadata): 
    try:
        carousel_cards = metadata["carousel_cards"]
        suggested_reply = metadata["suggested_reply"]
        return carousel_cards, suggested_reply

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_text_message_type %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CampaignApp', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return [], []


def append_suggestion_chip_to_cluster(cluster, suggestion_chip_list, messages): 
    try:
        suggestion_list = []
        for suggestion in suggestion_chip_list:
            if suggestion["type"] == "simple_reply":
                message = messages.SuggestedReply(suggestion["card_suggested_text"], suggestion["card_suggested_postback"])
                if cluster != None:
                    cluster.append_suggestion_chip(message)
                else:
                    suggestion_list.append(message)
            if suggestion["type"] == "open_url":
                message = messages.OpenUrlAction(suggestion["card_suggested_text"], suggestion["card_suggested_postback"], suggestion["url_to_open"])
                if cluster != None:
                    cluster.append_suggestion_chip(message)
                else:
                    suggestion_list.append(message)
            if suggestion["type"] == "dial_action":
                message = messages.DialAction(suggestion["card_suggested_text"], suggestion["card_suggested_postback"], suggestion["dial_action_number"])
                if cluster != None:
                    cluster.append_suggestion_chip(message)
                else:
                    suggestion_list.append(message)
            
            if suggestion["type"] == "share_location":
                message = messages.ViewLocationAction(suggestion["card_suggested_text"], suggestion["card_suggested_postback"], suggestion["location_latitude"], suggestion["location_longitude"], suggestion["location_label"])
                if cluster != None:
                    cluster.append_suggestion_chip(message)
                else:
                    suggestion_list.append(message)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_text_message_type %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CampaignApp', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    
    if cluster != None:
        return cluster
    else:
        return suggestion_list


def update_rcs_detailed_analytics(status, message_data, current_time):
    try:
        audience_log_obj = CampaignAudienceLog.objects.filter(
            recepient_id=message_data["messageId"]).first()
        campaign = None
        analytics_obj = None
        if audience_log_obj:
            campaign = audience_log_obj.campaign

            analytics_objs = CampaignRCSDetailedAnalytics.objects.filter(
                campaign=campaign)
            if analytics_objs.count() > 0:
                analytics_obj = analytics_objs.first()
            if status == "DELIVERED" and audience_log_obj.is_delivered == False:
                if audience_log_obj.is_sent == False:
                    audience_log_obj.is_sent = True
                    audience_log_obj.sent_datetime = current_time
                    audience_log_obj.sent_date = current_time.date()

                audience_log_obj.is_delivered = True
                audience_log_obj.delivered_datetime = current_time
                audience_log_obj.delivered_date = current_time.date()

            if status == "READ" and audience_log_obj.is_read == False:
                if audience_log_obj.is_sent == False:
                    audience_log_obj.is_sent = True
                    audience_log_obj.sent_datetime = current_time
                    audience_log_obj.sent_date = current_time.date()

                if audience_log_obj.is_delivered == False:
                    audience_log_obj.is_delivered = True
                    audience_log_obj.delivered_datetime = current_time
                    audience_log_obj.delivered_date = current_time.date()

                audience_log_obj.is_read = True
                audience_log_obj.read_datetime = current_time
                audience_log_obj.read_date = current_time.date()

            audience_log_obj.save()
            analytics_obj.sent = CampaignAudienceLog.objects.filter(
                campaign=campaign, is_sent=True).count()
            analytics_obj.read = CampaignAudienceLog.objects.filter(
                campaign=campaign, is_read=True).count()
            analytics_obj.delivered = CampaignAudienceLog.objects.filter(
                campaign=campaign, is_delivered=True).count()              
            
            analytics_obj.save()                        
            if campaign.status != CAMPAIGN_IN_PROGRESS and campaign.status != CAMPAIGN_DRAFT:
                if analytics_obj.delivered == 0 or analytics_obj.sent == 0:
                    campaign.status = CAMPAIGN_FAILED
                    campaign.save()
                else:
                    if analytics_obj.delivered == campaign.batch.total_audience_opted:
                        campaign.status = CAMPAIGN_COMPLETED
                    else:
                        campaign.status = CAMPAIGN_PARTIALLY_COMPLETED
                    campaign.save()
                analytics_obj.failed = campaign.batch.total_audience_opted - analytics_obj.delivered
                if analytics_obj.failed < 0:
                    analytics_obj.failed = 0
                analytics_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_rcs_detailed_analytics %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CampaignApp', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
