from EasyChatApp.models import Bot, Channel, BotChannel, Intent

new_channe_name, channel_obj = "ET-Source", None

if Channel.objects.filter(name=new_channe_name).count() == 0:
    channel_obj = Channel.objects.create(name=new_channe_name)
else:
    channel_obj = Channel.objects.get(name=new_channe_name)

for bot_obj in Bot.objects.all():

    if BotChannel.objects.filter(bot=bot_obj, channel=channel_obj).count() == 0:
        BotChannel.objects.create(bot=bot_obj, channel=channel_obj)

    for intent_obj in Intent.objects.filter(bots__in=[bot_obj]):
        intent_obj.channels.add(channel_obj)
        intent_obj.save()
