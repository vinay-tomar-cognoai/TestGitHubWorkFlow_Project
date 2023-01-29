from EasyChatApp.models import *
import random
import uuid

global strTimeProp, randomDate


random_messages = ["Hi",
                   "I want to know about insurance scheme",
                   "Tell me about latest home loan schemes",
                   "I want to apply for home loan",
                   "What is my account balance",
                   "account balance"]

random_bot_resp = ["Welcome to AllinCall",
                   "We have all kinds of plans. Which plans would you like to know?",
                   "Pradhan Mantri Aawas Yojna scheme",
                   "Sure. Have a look at the following offers",
                   "Your account balance is Rs. 20035",
                   "Your account balance is Rs. 30121"]

random_intent_name = ["Welcome",
                      "Insurance",
                      "Loan",
                      "Loan",
                      "AccountBalance",
                      "AccountBalance"]

data_points = 100


MISDashboard.objects.all().delete()

for iterator in range(data_points):

    random_date = randomDate()

    user_id = uuid.uuid4()

    rand_int = random.randint(0, len(random_messages) - 1)

    if rand_int >= 5:
        print("OOPs", rand_int)

    message_received = random_messages[rand_int]

    bot_response = random_bot_resp[rand_int]

    intent_name = random_intent_name[rand_int]

    channel_name = "web"

    MISDashboard.objects.create(message_received=message_received,
                                bot_response=bot_response,
                                intent_name=intent_name,
                                user_id=user_id,
                                channel_name=channel_name,
                                date=random_date)
