from EasyChatApp.models import Profile, NPS, WhatsAppWebhook
from datetime import date, datetime, timedelta


def cronjob():
    try:
        # Getting all the NPS Objects
        nps_objs = NPS.objects.filter(channel__name="WhatsApp")

        for nps_obj in nps_objs:
            # Bot
            bot = nps_obj.bot
            # Whatsapp NPS Time
            nps_time = nps_obj.whatsapp_nps_time
            today_date = date.today()
            profile_objs = Profile.objects.filter(
                channel__name="WhatsApp",
                last_message_date__date=today_date,
                is_nps_message_send=False)
            current_time = (datetime.now() -
                            timedelta(minutes=nps_time)).time()
            profile_objs = profile_objs.filter(
                last_message_date__time__gte=current_time)

            # Getting all the user ids
            user_ids = profile_objs.values_list(
                'user_id', flat=True).distinct()
            # Getting WhatsApp Webhook
            whatsapp_webhook_obj = WhatsAppWebhook.objects.filter(bot=bot)

            # Pushing the NPS message to all the users
            for user_id in user_ids:
                profile_obj = Profile.objects.filter(
                    user_id=user_id, is_nps_message_send=False)
                if profile_obj:
                    profile_obj[0].is_nps_message_send = True
                    profile_obj[0].save()
                dict_obj = {}
                exec(str(whatsapp_webhook_obj[0].extra_function), dict_obj)
                # response = dict_obj['whatsapp_push_notification'](user_id)
    except Exception:
        pass
