from EasyChatApp.models import *
from EasyChatApp.constants_icon import VIBER_ICON


def update_language_tuning_intent_table_data():
    
    try:
        language_tuning_intent_objs = LanguageTuningIntentTable.objects.all().order_by("pk")

        for language_tuning_intent_obj in language_tuning_intent_objs:
            temp_objs = LanguageTuningIntentTable.objects.filter(language=language_tuning_intent_obj.language, intent=language_tuning_intent_obj.intent)
            if(temp_objs.count()):
                temp_objs.exclude(pk=temp_objs.first().pk).delete()

    except Exception as e:
        logger.error("Error in update_language_tuning_intent_table_data: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_viber_icon():
    try:
        Channel.objects.filter(name="Viber").update(icon=VIBER_ICON)
    except Exception as e:
        logger.error("Error in update_viber_icon: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running update_language_tuning_intent_table_data...\n")

update_language_tuning_intent_table_data()

print("Running update_viber_icon...\n")

update_viber_icon()
