import pandas as pd
import demoji
import os
from django.conf import settings


def predict_emoji_label(emoji):
    if os.path.exists(settings.STATIC_ROOT + "EasyChatApp/emoji_csv/happy_sad_angry_neutral_emoji.csv"):
        df = pd.read_csv(settings.STATIC_ROOT + "EasyChatApp/emoji_csv/happy_sad_angry_neutral_emoji.csv")

    classes = (df.label.unique()).tolist()
    happy_label = classes[0]
    angry_label = classes[1]
    sad_label = classes[2]
    neutral_label = classes[3]

    happy_list = []
    angry_list = []
    sad_list = []
    neutral_list = []

    happy_emoji_list = (df.emoji[df.label == "Happy"]).tolist()
    angry_emoji_list = (df.emoji[df.label == "Angry"]).tolist()
    sad_emoji_list = (df.emoji[df.label == "sad"]).tolist()
    neutral_emoji_list = (df.emoji[df.label == "neutral"]).tolist()

    for row in range(len(happy_emoji_list)):
        for col in range(len(emoji)):
            if emoji[col] == happy_emoji_list[row]:
                happy_list.append(emoji[col])

    for row in range(len(angry_emoji_list)):
        for col in range(len(emoji)):
            if emoji[col] == angry_emoji_list[row]:
                angry_list.append(emoji[col])

    for row in range(len(sad_emoji_list)):
        for col in range(len(emoji)):
            if emoji[col] == sad_emoji_list[row]:
                sad_list.append(emoji[col])

    for row in range(len(neutral_emoji_list)):
        for col in range(len(emoji)):
            if emoji[col] == neutral_emoji_list[row]:
                neutral_list.append(emoji[col])

    if ((len(happy_list) > 0) and (len(angry_list) > 0) and (len(sad_list) > 0) and (len(neutral_list) > 0)):
        return neutral_label

    elif ((len(happy_list) > 0) and (len(angry_list) > 0) and (len(sad_list) > 0)):
        return neutral_label

    elif ((len(happy_list) > 0) and (len(angry_list) > 0) and (len(neutral_list) > 0)):
        return neutral_label

    elif ((len(happy_list) > 0) and (len(sad_list) > 0) and (len(neutral_list) > 0)):
        return neutral_label

    elif ((len(angry_list) > 0) and (len(sad_list) > 0) and (len(neutral_list) > 0)):
        return neutral_label

    elif ((len(angry_list) > 0) and (len(happy_list) > 0)):
        return neutral_label

    elif ((len(sad_list) > 0) and (len(happy_list) > 0)):
        return neutral_label

    elif ((len(neutral_list) > 0) and (len(happy_list) > 0)):
        return neutral_label

    elif ((len(angry_list) > 0) and (len(sad_list) > 0)):
        return neutral_label

    elif ((len(angry_list) > 0) and (len(neutral_list) > 0)):
        return neutral_label

    elif ((len(sad_list) > 0) and (len(neutral_list) > 0)):
        return neutral_label

    elif (len(happy_list) > 0):
        return happy_label

    elif (len(angry_list) > 0):
        return angry_label

    elif (len(sad_list) > 0):
        return sad_label

    elif (len(neutral_list) > 0):
        return neutral_label


def run_emoji_detection(emoji_input):
    emoji = demoji.findall(emoji_input)
    emoji = list(emoji.keys())
    result = predict_emoji_label(emoji)
    return result
