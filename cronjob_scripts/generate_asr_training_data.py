from EasyChatApp.models import Bot, Intent
from EasyChatApp.utils_voicebot import save_asr_training_data_into_file, get_asr_training_data

bot_id = 1

bot_obj = Bot.objects.get(pk=int(bot_id))

print("asr_training_data_exported into : {0}".format(
    save_asr_training_data_into_file(bot_obj, Intent)))

print(get_asr_training_data(bot_obj))
