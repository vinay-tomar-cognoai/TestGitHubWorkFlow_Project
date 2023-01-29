import json
from EasyChatApp.models import Intent, Bot

from xlwt import Workbook
automated_testing_wb = Workbook()
sheet1 = automated_testing_wb.add_sheet("Learning Bot")

sheet1.write(0, 0, "Question")
sheet1.write(0, 1, "Variation")
sheet1.write(0, 2, "Answer")
sheet1.write(0, 3, "Images")
sheet1.write(0, 4, "Videos")

index = 0
for intent in Intent.objects.filter(bots__in=[Bot.objects.get(pk=4)]):
    intent_name = intent.name
    intent_training_data = json.loads(intent.training_data)

    training_data_list = []
    for key in intent_training_data:
        training_data_list.append(intent_training_data[key])

    training_data_str = ", ".join(training_data_list)
    response = json.loads(intent.tree.response.sentence)["items"]
    text_response = response[0]["text_response"]

    image, video = "", ""

    try:
        image = json.loads(intent.tree.response.images)["items"][0]
    except Exception:  # noqa: F841
        pass

    try:
        video = json.loads(intent.tree.response.videos)["items"][0]
    except Exception:  # noqa: F841
        pass

    sheet1.write(index + 1, 0, intent_name)
    sheet1.write(index + 1, 1, training_data_str)
    sheet1.write(index + 1, 2, text_response)
    sheet1.write(index + 1, 3, image)
    sheet1.write(index + 1, 4, video)
    index += 1

filename = "HRBot.xls"
automated_testing_wb.save(filename)
