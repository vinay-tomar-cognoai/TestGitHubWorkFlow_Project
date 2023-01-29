from EasyChatApp.utils import create_whatsapp_tms_flow, create_default_tms_flow
from EasyChatApp.models import Intent, Bot

tms_intents = Intent.objects.filter(is_easy_tms_allowed=True)
for tms_intent in tms_intents:
    try:
        tms_intent.delete()
    except Exception as e:
        print("ERROR : ", str(e))

bots = Bot.objects.all()
for bot_obj in bots:
    try:
        print("creating intent for bot : ", str(bot_obj))
        create_default_tms_flow(
            bot_obj.pk, is_tms_allowed=bot_obj.is_tms_allowed)
        # create_whatsapp_tms_flow(
        #     bot_obj.pk, is_whatsapp_tms_allowed=bot_obj.is_whatsapp_tms_allowed)
    except Exception as e:
        print("ERROR : ", str(e))
