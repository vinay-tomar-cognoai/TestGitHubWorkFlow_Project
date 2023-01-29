import json
from EasyChatApp.models import Channel
from LiveChatApp.models import LiveChatCustomer, LiveChatBotChannelWebhook

# As per old data, for all livechat_customer_objs created from channels except Web, Android, iOS, source (in customer_details) was marked as Mobile
# As per new logic, source should be Others
# Updating old data as the per the new logic


def update_old_data_customer_details_field():
    channel_list = ["Web", "Android", "iOS"]
    livechat_customer_objs = LiveChatCustomer.objects.exclude(channel__in=Channel.objects.filter(name__in=channel_list))

    for livechat_customer_obj in livechat_customer_objs:
        try:
            customer_source_details = json.loads(livechat_customer_obj.customer_details)
            customer_source_details[0]['value'] = "Others"
            livechat_customer_obj.customer_details = json.dumps(customer_source_details)
            livechat_customer_obj.source_of_incoming_request = '3'
            livechat_customer_obj.save(update_fields=['customer_details', 'source_of_incoming_request'])
            print(f"Updated for LiveChat Username: {livechat_customer_obj.username}")
        except Exception as e:
            print(f"Failed to update for LiveChat Username: {livechat_customer_obj.username} with error: {str(e)}")


# For updating newly added field (source_of_incoming_request) from old data
# in LiveChatApp > models.py > LiveChatCustomer > source_of_incoming_request from existing field of customer_details


def update_source_of_incoming_request_field_from_old_data():
    livechat_customer_objs = LiveChatCustomer.objects.all()
    for livechat_customer_obj in livechat_customer_objs:
        try:
            if livechat_customer_obj.get_source_name_from_customer_details() == "Desktop":
                livechat_customer_obj.source_of_incoming_request = "1"
            elif livechat_customer_obj.get_source_name_from_customer_details() == "Mobile":
                livechat_customer_obj.source_of_incoming_request = "2"
            else:
                livechat_customer_obj.source_of_incoming_request = "3"       
            livechat_customer_obj.save(update_fields=['source_of_incoming_request']) 
            print(f"Updated for LiveChat Username: {livechat_customer_obj.username}")
        except Exception as e:
            print(f"Failed to update for LiveChat Username: {livechat_customer_obj.username} with error: {str(e)}")


def update_livechat_whatsapp_webhook():
    print("In update_livechat_whatsapp_webhook...")
    livechat_channel_webhooks = LiveChatBotChannelWebhook.objects.all()
    for webhook_obj in livechat_channel_webhooks:
        if webhook_obj.function.find("use_aliases=True") != -1:
            webhook_obj.function = webhook_obj.function.replace("use_aliases=True", "language='alias'")
            webhook_obj.save()


# Fuctions calls to be executed in the mentioned order

update_old_data_customer_details_field()
update_source_of_incoming_request_field_from_old_data()
update_livechat_whatsapp_webhook()
