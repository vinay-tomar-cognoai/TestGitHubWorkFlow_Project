from EasyChatApp.models import *

for intent_obj in Intent.objects.filter(is_deleted=False):
    bot_obj = Bot.objects.filter(is_deleted=False)[0]
    intent_obj.bots.add(bot_obj)
    intent_obj.save()
    print(len(intent_obj.bots.all()))
