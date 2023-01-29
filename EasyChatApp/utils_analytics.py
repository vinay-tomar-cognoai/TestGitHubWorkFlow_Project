from django.db.models import Q, F, Count, Avg
from django.conf import settings

import requests
import json
import csv
import re
import logging
import nltk
import sys
import copy
import xlwt
import hashlib
import os
from xlwt import Workbook

from datetime import datetime, timedelta
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

from EasyChatApp.constants import *

logger = logging.getLogger(__name__)

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

stop = stopwords.words("english")

for word in ignore_list:
    stop.remove(word)

"""
function: get_word_mapper_dictionary
input params:
    WordMapper: model
    bot_obj: active bot object
output:
    return dictionary which contains wordmappers
"""


def get_word_mapper_dictionary(WordMapper, bot_obj, src, channel, user_id, sync_all=True):  # noqa: N803
    logger.info("Into get_word_mapper_dictionary...", extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    word_mapper_dictionary = dict()

    if sync_all:
        word_mapper_objs = WordMapper.objects.filter(bots__in=[bot_obj])
    else:
        word_mapper_objs = WordMapper.objects.filter(
            bots__in=[bot_obj], synced=False)

    for word_mapper in word_mapper_objs:
        keyword = word_mapper.keyword
        similar_words = word_mapper.similar_words.split(',')
        for similar_word in similar_words:
            if similar_word.strip().lower() == "":
                continue
            word_mapper_dictionary[
                similar_word.strip().lower()] = keyword.strip().lower()
    logger.info(word_mapper_dictionary, extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    logger.info("Exit from get_word_mapper_dictionary...", extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    return word_mapper_dictionary


"""
function: run_word_mapper
input params:
    WordMapper: model
    sentence: input user message
    bot_obj: active bot object
output:
    return string after word mapping

This function helps in mapping synonym words for example
what is mf? -> what is mutual fund?
"""


def run_word_mapper(WordMapper, sentence, bot_obj, src, channel, user_id):  # noqa: N803
    logger.info("Into run_word_mapper...", extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    logger.info("before run_word_mapper: %s", str(sentence), extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    new_sentence = ''
    word_mapper_dictionary = get_word_mapper_dictionary(
        WordMapper, bot_obj, src, channel, user_id)
    for word in sentence.strip().split(" "):
        strip_word = word.strip().lower()
        if strip_word in word_mapper_dictionary:
            new_sentence += word_mapper_dictionary[strip_word]
        else:
            new_sentence += strip_word
        new_sentence += ' '
    logger.info("After run_word_mapper: %s", str(new_sentence), extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    logger.info("Exit from run_word_mapper...", extra={'AppName': 'EasyChat', 'user_id': str(
        user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    return new_sentence.strip()


"""
function: word_stemmer
input params:
    word: input token
output:
    return stemmed token

eg. sleeping -> sleep
"""


def word_stemmer(word):
    if not settings.EASYCHAT_LEMMATIZER_REQUIRED:
        return stemmer.stem(str(word).strip().lower())
    else:
        return lemmatizer.lemmatize(str(word).strip().lower())


"""
function: get_stem_words_of_sentence
input params:
    sentence: input user query or message
output:
    return list of stemmed keywords using NLP
"""


def get_stem_words_of_sentence(sentence, src, channel, user_id, bot_obj):
    stem_words = []
    bot_id = None
    try:
        if bot_obj != None and type(bot_obj) == list:
            bot_obj = bot_obj[0]

        try:
            bot_id = bot_obj.pk
        except Exception:
            pass

        if bot_obj == None:
            stopwords = stop
        else:
            try:
                stopwords = json.loads(bot_obj.stop_keywords)

                if stopwords == "" or stopwords == None or len(stopwords) == 0:
                    stopwords = stop
            except Exception:
                stopwords = stop

        stopwords = [stop.lower() for stop in stopwords]
        # logger.info("Into get_stem_words_of_sentence...")
        query_sentence = process_string_for_intent_identification(
            sentence, src, channel, user_id, bot_id)
        # Word Tokenizer
        token_list = nltk.word_tokenize(query_sentence)
        # Remove stop word from token list
        token_list = [token for token in token_list if token.lower()
                      not in stopwords]
        # Apply stemmer
        stem_words = [word_stemmer(token)
                      for token in token_list if token != ""]
        # logger.info("Exit from get_stem_words_of_sentence...")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_stem_words_of_sentence %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    return stem_words


"""
function: remove_whitespace
input params:
    sentence: string
output:
    return string after removing extra whitespace

"""


def remove_whitespace(sentence):
    return re.sub('\s+', ' ', sentence).strip()  # noqa: W605


"""
function: query_bot
input params:
    question: question which is to be tested
    channel:channel, default=web(optional)
    user_id:user id of active user  defaultis "" (optional)
output:
    return recognized intent fro given question
"""


def query_bot(question, channel="web", user_id=""):
    port = Config.objects.all()[0].app_port
    try:
        data = {
            "user_id": user_id,
            "message": str(question),
            "channel": channel
        }

        resp = requests.post('http://localhost:' + str(port) +
                             '/chat/query/', data=data)
        json_responce = json.loads(resp.text)
        recognized_intent = json_responce["intent"]

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("query_bot %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None

    return recognized_intent


"""
function: export_mis_dashboard_without_filter
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    start_date: start date from which you want to export data
    end_date: end date to which you want to export data
    username: username of active user
output:
    generates csv file containing mis dashboard data of all the intents
"""


def export_mis_dashboard_without_filter(User, Bot, MISDashboard, start_date, end_date, username,
                                        bot_name):  # noqa: N803
    # file_path = "chat/mis_dashboard"
    try:
        logger.info("Inside export_mis_dashboard_without_filter function", extra={
            'AppName': 'EasyChat', 'user_id': str(User.username), 'source': 'None', 'channel': 'None',
            'bot_id': 'None'})
        bot_objs = get_bot_objects_for_given_user(username, User, Bot)

        date_format = "%Y-%m-%d"
        # from datetime import datetime
        datetime_start = datetime.datetime.strptime(
            start_date, date_format).date()
        datetime_end = datetime.datetime.strptime(end_date, date_format).date()

        automated_testing_wb = Workbook()
        sheet1 = automated_testing_wb.add_sheet("Message History")

        sheet1.write(0, 0, "Date")
        sheet1.col(0).width = 256 * 20
        sheet1.write(0, 1, "User ID")
        sheet1.col(1).width = 256 * 40
        sheet1.write(0, 2, "User Query")
        sheet1.col(2).width = 256 * 40
        sheet1.write(0, 3, "Bot Response")
        sheet1.col(3).width = 256 * 50
        sheet1.write(0, 4, "Intent Identified")
        sheet1.col(4).width = 256 * 30
        sheet1.write(0, 5, "Intent Feedback")
        sheet1.col(5).width = 256 * 10
        sheet1.write(0, 6, "User Feedback")
        sheet1.col(6).width = 256 * 40

        mis_objs = MISDashboard.objects.filter(bot__in=bot_objs,
                                               creation_date__gte=datetime_start,
                                               creation_date__lte=datetime_end).order_by('-date')

        if bot_name != "All":
            bot = Bot.objects.filter(name=bot_name)[0]
            mis_objs = mis_objs.filter(bot=bot)

        index = 0
        for mis_obj in mis_objs:

            helpful_comment = ""
            if mis_obj.is_helpful():
                helpful_comment = "Helpful"
            elif mis_obj.is_unhelpFul():
                helpful_comment = "Unhelpful"

            intent_name = str(mis_obj.get_intent_obj())
            sheet1.write(index + 1, 0, mis_obj.get_datetime())
            sheet1.write(index + 1, 1, mis_obj.user_id)
            sheet1.write(index + 1, 2, mis_obj.get_message_received())
            sheet1.write(index + 1, 3, mis_obj.get_bot_response())
            sheet1.write(index + 1, 4, intent_name)
            sheet1.write(index + 1, 5, helpful_comment)
            sheet1.write(index + 1, 6, mis_obj.get_feedback_comments())
            index += 1

        filename = "files/filtered_data_" + \
                   str(datetime.datetime.today().date()) + \
                   "_" + str(username) + ".xls"
        automated_testing_wb.save(filename)
        logger.info("Exit from export_mis_dashboard_without_filter", extra={'AppName': 'EasyChat', 'user_id': str(
            User.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_mis_dashboard_without_filter %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(User.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return filename


"""
function: export_mis_dashboard_with_filter_based_message
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    start_date: start date from which you want to export data
    end_date: end date to which you want to export data
    username: username of active user
output:
    generates csv file containing mis dashboard data of intents whose name is none
"""


def export_mis_dashboard_with_filter_based_message(User, Bot, MISDashboard, start_date, end_date, username,
                                                   bot_name):  # noqa: N803
    # file_path = "chat/mis_dashboard"
    try:
        logger.info(
            "Inside export_mis_dashboard_with_filter_based_message function",
            extra={'AppName': 'EasyChat', 'user_id': str(User.username), 'source': 'None', 'channel': 'None',
                   'bot_id': 'None'})
        bot_objs = get_bot_objects_for_given_user(username, User, Bot)

        date_format = "%Y-%m-%d"
        # from datetime import datetime
        datetime_start = datetime.datetime.strptime(
            start_date, date_format).date()
        datetime_end = datetime.datetime.strptime(end_date, date_format).date()

        automated_testing_wb = Workbook()
        sheet1 = automated_testing_wb.add_sheet("Message History")

        sheet1.write(0, 0, "Date")
        sheet1.col(0).width = 256 * 20
        sheet1.write(0, 1, "User Id")
        sheet1.col(1).width = 256 * 40
        sheet1.write(0, 2, "User Query")
        sheet1.col(2).width = 256 * 40
        sheet1.write(0, 3, "Bot Response")
        sheet1.col(3).width = 256 * 50
        sheet1.write(0, 4, "Intent Identified")
        sheet1.col(4).width = 256 * 30
        sheet1.write(0, 5, "Intent Feedback")
        sheet1.col(5).width = 256 * 10
        sheet1.write(0, 6, "User Feedback")
        sheet1.col(6).width = 256 * 40

        mis_objs = MISDashboard.objects.filter(bot__in=bot_objs,
                                               date__date__gte=datetime_start,
                                               date__date__lte=datetime_end).filter(intent_name=None).order_by('-date')

        if bot_name != "All":
            bot = Bot.objects.filter(name=bot_name)[0]
            mis_objs = mis_objs.filter(bot=bot)

        index = 0
        for mis_obj in mis_objs:

            helpful_comment = ""
            if mis_obj.is_helpful():
                helpful_comment = "Helpful"
            elif mis_obj.is_unhelpFul():
                helpful_comment = "Unhelpful"

            intent_name = str(mis_obj.get_intent_obj())
            sheet1.write(index + 1, 0, mis_obj.get_datetime())
            sheet1.write(index + 1, 1, mis_obj.user_id)
            sheet1.write(index + 1, 2, mis_obj.get_message_received())
            sheet1.write(index + 1, 3, mis_obj.get_bot_response())
            sheet1.write(index + 1, 4, intent_name)
            sheet1.write(index + 1, 5, helpful_comment)
            sheet1.write(index + 1, 6, mis_obj.get_feedback_comments())
            index += 1

        filename = "files/filtered_data_" + \
                   str(datetime.datetime.today().date()) + \
                   "_" + str(username) + ".xls"
        automated_testing_wb.save(filename)
        logger.info("Exit from export_mis_dashboard_with_filter_based_message", extra={
            'AppName': 'EasyChat', 'user_id': str(User.username), 'source': 'None', 'channel': 'None',
            'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_mis_dashboard_with_filter_based_message %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(User.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return filename


"""
function: process_string_for_intent_identification
input params:
    sentence: string which contains all types of special character
output:
    output string which contains only a-z, A-Z, 0-9
"""


def process_string_for_intent_identification(sentence, src, channel, user_id, bot_id):
    try:
        # logger.info("Into process_string_for_intent_identification...")
        # logger.info("Input sentence: %s", sentence)
        sentence = re.sub(r"[^a-zA-Z0-9]+", ' ', sentence)
        sentence = sentence.strip()
        sentence = re.sub('(\s+)(a|an|the)(\s+)', ' ', sentence.lower())
        # logger.info("Output processed sentence: %s", sentence)
        # logger.info("Exit from process_string_for_intent_identification...")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("process_string_for_intent_identification %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

    return sentence


"""
function: keyword_exist_in_string
input params:
    keyword_list: list of keywords
    query_string: string which to be checked for keywords
output:
    returns True/False based on whether keyword is found in query string or not
"""


def keyword_exist_in_string(keyword_list, query_string):
    try:

        keyword_list = [keyword.strip().lower() for keyword in keyword_list]
        query_token_list = process_string_for_intent_identification(
            query_string.lower(), None, None, None, None).split(" ")
        intersection_list = list(set(keyword_list) & set(query_token_list))

        if len(intersection_list) > 0:
            return True
        else:
            return False

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("keyword_exist_in_string %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return False


"""
function: export_MIS_dashboard_with_filter_keywords
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    username: username of active user
    keyword_list: list of keywords
output:
    generates csv file containing mis dashboard data for which mis message does
        not contains keywords form keyword_list
"""


def export_mis_dashboard_with_filter_keywords(User, Bot, MISDashboard, keyword_list, username,
                                              bot_name):  # noqa: N803,N802
    filename = None
    try:
        bot_objs = get_bot_objects_for_given_user(username, User, Bot)

        logger.info("Inside exportMISDashboardWithFilterKeyWords function", extra={
            'AppName': 'EasyChat', 'user_id': str(User.username), 'source': 'None', 'channel': 'None',
            'bot_id': 'None'})
        mis_objects = MISDashboard.objects.filter(
            bot__in=bot_objs).filter(~Q(message_received=None))

        if bot_name != "All":
            bot = Bot.objects.filter(name=bot_name)[0]
            mis_objects = mis_objects.filter(bot=bot)

        filtered_objs = []
        for mis_object in mis_objects:
            mis_message_received = mis_object.get_message_received()
            if keyword_exist_in_string(keyword_list, mis_message_received):
                filtered_objs.append(mis_object)

        keywords_export_wb = Workbook()
        sheet1 = keywords_export_wb.add_sheet("Message History")

        sheet1.write(0, 0, "Date")
        sheet1.col(0).width = 256 * 20
        sheet1.write(0, 1, "User Id")
        sheet1.col(1).width = 256 * 40
        sheet1.write(0, 2, "User Query")
        sheet1.col(2).width = 256 * 40
        sheet1.write(0, 3, "Bot Response")
        sheet1.col(3).width = 256 * 50
        sheet1.write(0, 4, "Intent Identified")
        sheet1.col(4).width = 256 * 30
        sheet1.write(0, 5, "Intent Feedback")
        sheet1.col(5).width = 256 * 10
        sheet1.write(0, 6, "User Feedback")
        sheet1.col(6).width = 256 * 40

        index = 0
        for mis_obj in filtered_objs:

            helpful_comment = ""
            if mis_obj.is_helpful():
                helpful_comment = "Helpful"
            elif mis_obj.is_unhelpFul():
                helpful_comment = "Unhelpful"

            intent_name = str(mis_obj.get_intent_obj())
            sheet1.write(index + 1, 0, mis_obj.get_datetime())
            sheet1.write(index + 1, 1, mis_obj.user_id)
            sheet1.write(index + 1, 2, mis_obj.get_message_received())
            sheet1.write(index + 1, 3, mis_obj.get_bot_response())
            sheet1.write(index + 1, 4, intent_name)
            sheet1.write(index + 1, 5, helpful_comment)
            sheet1.write(index + 1, 6, mis_obj.get_feedback_comments())
            index += 1

        filename = "files/filtered_data_" + \
                   str(datetime.datetime.today().date()) + \
                   "_" + str(username) + ".xls"
        keywords_export_wb.save(filename)

        logger.info("Exit from exportMISDashboardWithFilterKeyWords function", extra={
            'AppName': 'EasyChat', 'user_id': str(User.username), 'source': 'None', 'channel': 'None',
            'bot_id': 'None'})

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_MIS_dashboard_with_filter_keywords %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(User.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return filename


"""
function: get_bot_objects_for_given_user
input params:
    User: user model
    Bot: Bot model
    username: username of active user
output:
    returns list of bot objects for given user
"""


def get_bot_objects_for_given_user(username, User, Bot):  # noqa: N803
    user_obj = User.objects.get(username=str(username))
    bot_slug = []
    bots = Bot.objects.filter(
        users__in=[user_obj], is_uat=True, is_deleted=False)

    for bot in bots:
        if bot.slug not in bot_slug and bot.slug != None:
            bot_slug.append(bot.slug)

    bot_objs = []
    for slug in bot_slug:
        bot_obj = Bot.objects.filter(slug=slug, is_deleted=False)
        bot_objs += bot_obj

    return bot_objs


"""
function: get_count_of_unanswered_messages
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    username: username of active user
    bot_objs: list of bot objects
    year: year for which you want data
    month: month for which you want data
    day: day for which you want data
output:
    returns number of unanswered message on that given day
"""


def get_count_of_unanswered_messages(User, Bot, MISDashboard, datetime_obj, username, bot_objs):  # noqa: N803
    # bot_objs = get_bot_objects_for_given_user(username, User, Bot)
    mis_objects = MISDashboard.objects.filter(
        creation_date=datetime_obj, bot__in=bot_objs)
    mis_objects = mis_objects.filter(intent_name=None)
    return mis_objects.count()


"""
function: get_count_of_answered_messages
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    username: username of active user
    bot_objs: list of bot objects
    year: year for which you want data
    month: month for which you want data
    day: day for which you want data
output:
    returns number of answered message on that given day
"""


def get_count_of_answered_messages(User, Bot, MISDashboard, datetime_obj, username, bot_objs):  # noqa: N803
    # bot_objs = get_bot_objects_for_given_user(username, User, Bot)
    mis_objects = MISDashboard.objects.filter(
        creation_date=datetime_obj, bot__in=bot_objs)
    mis_objects = mis_objects.filter(~Q(intent_name=None))
    return mis_objects.count()


"""
function: get_count_of_message_by_channel
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    Channel: Channel model
    username: username of active user
    bot_objs: list of bot objects
    year: year for which you want data
    month: month for which you want data
    day: day for which you want data
output:
    returns json containg details of number of total message per channel
"""


def get_count_of_message_by_channel(User, Bot, MISDashboard, Channel, datetime_obj, username, bot_objs):  # noqa: N803
    # bot_objs = get_bot_objects_for_given_user(username, User, Bot)
    mis_objects = MISDashboard.objects.filter(
        creation_date=datetime_obj, bot__in=bot_objs)
    channel_count_dict = {}
    for channel_obj in Channel.objects.filter(is_easychat_channel=True):
        channel_name = channel_obj.name
        if channel_name != "default":
            filtered_objects = mis_objects.filter(channel_name=channel_name)
            channel_count_dict[str(channel_name)] = filtered_objects.count()
    return channel_count_dict


"""
function: promoter_feedback_count
input params:
    bot_objs: list of bot objects
output:
    returns number of promoter responses for that bot
"""


def promoter_feedback_count(bot_objs, channel_obj, Feedback):  # noqa: N803
    try:
        if channel_obj:
            feedback_objects_rating_4 = Feedback.objects.filter(
                bot__in=bot_objs, channel=channel_obj, rating__gte=3, scale_rating_5=False).count()

            feedback_objects_rating_5 = Feedback.objects.filter(
                bot__in=bot_objs, channel=channel_obj, rating__gte=4, scale_rating_5=True).count()

        else:
            feedback_objects_rating_4 = Feedback.objects.filter(
                bot__in=bot_objs, rating__gte=3, scale_rating_5=False).count()

            feedback_objects_rating_5 = Feedback.objects.filter(
                bot__in=bot_objs, rating__gte=4, scale_rating_5=True).count()

        feedback_objects = feedback_objects_rating_4 + feedback_objects_rating_5

        return feedback_objects
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("promoter_feedback_count %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: demoter_feedback_count
input params:
    bot_objs: list of bot objects
output:
    returns number of demoter responses for that bot
"""


def demoter_feedback_count(bot_objs, channel_obj, Feedback):  # noqa: N803
    if channel_obj:
        feedback_objects = Feedback.objects.filter(
            bot__in=bot_objs, channel=channel_obj, rating__lte=2).count()
    else:
        feedback_objects = Feedback.objects.filter(
            bot__in=bot_objs, rating__lte=2).count()
    return feedback_objects


def get_db_objects_based_on_filter(db_objects, channel_name, category_name, selected_language, supported_languages):
    is_channel_filter_required = channel_name.lower() != 'all'
    is_category_filter_required = category_name.lower() != 'all'
    is_language_filter_required = selected_language.lower() != 'all'

    if is_channel_filter_required:
        db_objects = db_objects.filter(channel_name=channel_name)

    if is_category_filter_required:
        db_objects = db_objects.filter(category__name=category_name)

    if is_language_filter_required:
        db_objects = db_objects.filter(
            selected_language__in=supported_languages)

    return db_objects


def return_mis_objects_based_on_category_channel_language(start_date_time, end_date_time, bot_objs, channel_name,
                                                          category_name, selected_language, supported_languages,
                                                          MISDashboard, UserSessionHealth, block_check_required=True):
    if start_date_time != None and end_date_time != None:
        mis_objects = MISDashboard.objects.filter(
            creation_date__gte=start_date_time, creation_date__lte=end_date_time, bot__in=bot_objs)
    else:
        mis_objects = MISDashboard.objects.filter(bot__in=bot_objs)

    if block_check_required:
        mis_objects = return_mis_objects_excluding_blocked_sessions(mis_objects, UserSessionHealth)

    mis_objects = get_db_objects_based_on_filter(
        mis_objects, channel_name, category_name, selected_language, supported_languages)

    return mis_objects


def return_mis_objects_excluding_blocked_sessions(mis_objects, UserSessionHealth):
    try:
        return mis_objects.filter(is_session_blocked=False)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("return_mis_objects_excluding_blocked_sessions: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'}) 

    return mis_objects


def return_mis_daily_objects_based_on_filter(bot_objs, channel_name, category_name, category_obj, selected_language, supported_languages, MessageAnalyticsDaily):
    previous_mis_objects = MessageAnalyticsDaily.objects.filter(
        bot__in=bot_objs)
    is_channel_filter_required = channel_name.lower() != 'all'
    is_category_filter_required = category_name.lower() != 'all'
    is_language_filter_required = selected_language.lower() != 'all'

    if is_channel_filter_required:
        previous_mis_objects = previous_mis_objects.filter(
            channel_message__name=channel_name)

    if is_category_filter_required:
        previous_mis_objects = previous_mis_objects.filter(
            category=category_obj)

    if is_language_filter_required:
        previous_mis_objects = previous_mis_objects.filter(
            selected_language__in=supported_languages)

    return previous_mis_objects


def return_unique_users_objects_based_on_filter(bot_objs, channel_name, selected_language, supported_languages, UniqueUsers):
    previous_mis_objects = UniqueUsers.objects.filter(
        bot__in=bot_objs)
    is_channel_filter_required = channel_name.lower() != 'all'
    is_language_filter_required = selected_language.lower() != 'all'

    if is_channel_filter_required:
        previous_mis_objects = previous_mis_objects.filter(
            channel__name=channel_name)

    if is_language_filter_required:
        previous_mis_objects = previous_mis_objects.filter(
            selected_language__in=supported_languages)

    return previous_mis_objects


def return_zero_if_number_is_none(number):
    if not number:
        return 0

    return number


"""
function: get_daily_count_of_messages
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    username: username of active user
    bot_objs: list of bot objects
    year: year for which you want data
    month: month for which you want data
    day: day for which you want data
output:
    returns number of total messages for that given date
"""


def get_daily_count_of_messages(MISDashboard, UserSessionHealth, datetime_obj, bot_objs, channel_name='All', category_name='All',
                                selected_language="All", supported_languages=[]):  # noqa: N803

    mis_objects = return_mis_objects_based_on_category_channel_language(
        datetime_obj, datetime_obj, bot_objs, channel_name, category_name, selected_language, supported_languages,
        MISDashboard, UserSessionHealth, False)

    return mis_objects.count()


"""
function: get_daily_count_of_users
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    username: username of active user
    bot_objs: list of bot objects
    year: year for which you want data
    month: month for which you want data
    day: day for which you want data
output:
    returns number of total users for that given date
"""


def get_daily_count_of_users(MISDashboard, UserSessionHealth, datetime_obj, bot_objs, channel_name='All', category_name='All',
                             selected_language="All", supported_languages=[]):  # noqa: N803
    mis_objects = return_mis_objects_based_on_category_channel_language(
        datetime_obj, datetime_obj, bot_objs, channel_name, category_name, selected_language, supported_languages,
        MISDashboard, UserSessionHealth, False)
    len_mis_objects = mis_objects.values("user_id").distinct().count()
    return len_mis_objects


"""
function: get_daily_count_of_messages_categorized_by_intent
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    username: username of active user
    bot_objs: list of bot objects
    year: year for which you want data
    month: month for which you want data
    day: day for which you want data
output:
    returns list of number of total messages categorized_by_intent of that given day
"""


def get_daily_count_of_messages_categorized_by_intent(User, Bot, MISDashboard, datetime_obj, username,
                                                      bot_objs):  # noqa: N803
    # bot_objs = get_bot_objects_for_given_user(username, User, Bot)
    mis_objects = MISDashboard.objects.filter(creation_date=datetime_obj).filter(
        ~Q(intent_name="INFLOW-INTENT"), bot__in=bot_objs)

    length = mis_objects.count()
    mis_objects = mis_objects.values("intent_name").order_by(
        "intent_name").annotate(frequency=Count("intent_name"))

    for mis_object in mis_objects:
        length = length - mis_object['frequency']

    for mis_object in mis_objects:
        if (mis_object['intent_name'] == None):
            mis_object['frequency'] = length
            break

    return list(mis_objects)


"""
function: get_monthly_count_of_message
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    username: username of active user
    bot_objs: list of bot objects
    year: year for which you want data
    month: month for which you want data
output:
    returns number of total messages for that month
"""


def get_monthly_count_of_message(User, Bot, MISDashboard, year, month, username, bot_objs):  # noqa: N803
    # bot_objs = get_bot_objects_for_given_user(username, User, Bot)
    mis_objects = MISDashboard.objects.filter(creation_date__year=str(
        year), creation_date__month=str(month), bot__in=bot_objs)
    return mis_objects.count()


"""
function: get_monthly_count_of_users
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    username: username of active user
    bot_objs: list of bot objects
    year: year for which you want data
    month: month for which you want data
output:
    returns number of total users for that month
"""


def get_monthly_count_of_users(User, Bot, MISDashboard, year, month, username, bot_objs):  # noqa: N803
    # bot_objs = get_bot_objects_for_given_user(username, User, Bot)
    mis_objects = MISDashboard.objects.filter(creation_date__year=str(
        year), creation_date__month=str(month), bot__in=bot_objs)
    len_mis_objects = mis_objects.values("user_id").distinct().count()
    return len_mis_objects


"""
function: get_monthly_count_of_messages_categorized_by_intent
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    username: username of active user
    bot_objs: list of bot objects
    year: year for which you want data
    month: month for which you want data
output:
    returns list of number of total messages categorized_by_intent of that given month
"""


def get_monthly_count_of_messages_categorized_by_intent(User, Bot, MISDashboard, year, month, username,
                                                        bot_objs):  # noqa: N803

    mis_objects = MISDashboard.objects.filter(creation_date__year=str(
        year), creation_date__month=str(month)).filter(~Q(intent_name="INFLOW-INTENT"), bot__in=bot_objs)

    length = mis_objects.count()

    mis_objects = mis_objects.values("intent_name").order_by(
        "intent_name").annotate(frequency=Count("intent_name"))

    for mis_object in mis_objects:
        length = length - mis_object['frequency']

    for mis_object in mis_objects:
        if (mis_object['intent_name'] == None):
            mis_object['frequency'] = length
            break

    return list(mis_objects)


"""
function: get_list_of_unanswered_messages
input params:
    User: user model
    Bot: Bot model
    MISDashboard: Misboard model
    username: username of active user
output:
    returns list of unanswered messages
"""


def get_list_of_unanswered_messages(User, Bot, MISDashboard, username):  # noqa: N803
    bot_objs = get_bot_objects_for_given_user(username, User, Bot)
    mis_objects = MISDashboard.objects.filter(
        intent_name=None, bot__in=bot_objs)
    mis_objects = mis_objects.values("message_received")
    return list(mis_objects)


"""
function: create_intent
input params:
    intent_name: name of intent
    variation_list: training sentences
    answer: text response of bot
    bot_obj: bot object for intent to be created
    Intent: Intent model
    Channel: Channel model
    BotResponse: BotResponse model
    is_part_of_suggestion_list: Boolean whether it will be part of suggestion list or not
output:
    creates intent with given data
"""


def create_intent(intent_name, variation_list, answer, bot_obj, Intent, Channel, BotResponse,
                  is_part_of_suggestion_list):  # noqa: N803
    # this function is currently not used anywhere
    training_data = {}
    for index, variation in enumerate(variation_list):
        training_data[str(index)] = str(variation)
    stem_words = get_stem_words_of_sentence(
        intent_name, None, None, None, bot_obj)
    stem_words.sort()

    hashed_name = ' '.join(stem_words)
    hashed_name = hashlib.md5(hashed_name.encode()).hexdigest()
    intent_obj = Intent.objects.create(name=intent_name,
                                       intent_hash=hashed_name,
                                       keywords=json.dumps({}),
                                       training_data=json.dumps(training_data),
                                       threshold=1.0,
                                       is_part_of_suggestion_list=is_part_of_suggestion_list)

    for channel_obj in Channel.objects.filter(is_easychat_channel=True):
        intent_obj.channels.add(channel_obj)

    intent_obj.bots.add(bot_obj)

    tree_obj = intent_obj.tree

    sentence = {
        "items": [
            {
                "text_response": str(answer),
                "speech_response": str(answer),
                "text_reprompt_response": str(answer),
                "speech_reprompt_response": str(answer),
            }
        ]
    }

    cards = {
        "items": [
        ]
    }

    modes = {
        "is_typable": "true",
        "is_button": "true",
        "is_slidable": "false",
        "is_date": "false",
        "is_dropdown": "false"
    }

    modes_param = {
        "is_slidable": [{
            "max": "",
            "min": "",
            "step": ""
        }]
    }

    bot_response_obj = BotResponse.objects.create(
        sentence=json.dumps(sentence),
        cards=json.dumps(cards),
        modes=json.dumps(modes),
        modes_param=json.dumps(modes_param))

    tree_obj.response = bot_response_obj
    tree_obj.save()
    intent_obj.save()


"""
function: create_default_intent
input params:
    bot_obj: bot object for default intents to be created
    DefaultIntent: DefaultIntent model
    Intent: Intent model
    Channel: Channel model
    BotResponse: BotResponse model
    is_part_of_suggestion_list: Boolean whether it will be part of suggestion list or not
output:
    creates default intents for given bot
"""


def create_default_intent(bot_obj, DefaultIntent, Intent, Channel, BotResponse,
                          is_part_of_suggestion_list):  # noqa: N803
    try:
        for default_intent in DefaultIntent.objects.all():
            variation_list = [variation for variation in default_intent.variations.split(
                ",") if variation != ""]
            create_intent(intent_name=default_intent.intent_name,
                          variation_list=variation_list,
                          answer=default_intent.answer,
                          bot_obj=bot_obj,
                          Intent=Intent,
                          Channel=Channel,
                          BotResponse=BotResponse,
                          is_part_of_suggestion_list=is_part_of_suggestion_list)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_default_intent: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: build_bot_not_found_response
check if user is trying to authenticate with same credentials from two different browser.
"""


def build_continuous_session_running_error_response(user_id, src, channel, bot_id, language_template_obj):
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        response["user_id"] = ""
        response["bot_id"] = ""
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"]["recommendations"] = []

        response["response"]["tooltip_response"] = ""
        response["response"]["speech_response"][
            "text"] = language_template_obj.get_more_than_one_session_running_text()
        response["response"]["speech_response"][
            "reprompt_text"] = language_template_obj.get_more_than_one_session_running_text()
        response["response"]["text_response"][
            "text"] = language_template_obj.get_more_than_one_session_running_text()
        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        response["status_code"] = 500
        response["status_message"] = str(e)
    return response


"""
function: invalid_channel_response
builds rich json response in case of invalid channel query
"""


def invalid_channel_response(user_id, src, channel, bot_id):
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        response["user_id"] = ""
        response["bot_id"] = ""
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"]["recommendations"] = []
        response["response"]["tooltip_response"] = ""
        response["response"]["speech_response"][
            "text"] = "Looks like I don't have support for this channel."
        response["response"]["speech_response"][
            "reprompt_text"] = "Looks like I don't have support for this channel."
        response["response"]["text_response"][
            "text"] = "Looks like I don't have support for this channel."
        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        response["status_code"] = 500
        response["status_message"] = str(e)
    return response


"""
function: build_bot_not_found_response

builds rich json response in case of bot not found
"""


def build_bot_not_found_response(user_id, src, channel, bot_id):
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        response["user_id"] = ""
        response["bot_id"] = ""
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"]["recommendations"] = []

        response["response"]["tooltip_response"] = ""
        response["response"]["speech_response"][
            "text"] = "Looks like I don't have answer for selected bot query."
        response["response"]["speech_response"][
            "reprompt_text"] = "Looks like I don't have answer for selected bot query."
        response["response"]["text_response"][
            "text"] = "Looks like I don't have answer for selected bot query."
        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        response["status_code"] = 500
        response["status_message"] = str(e)
    return response


"""
function: build_internal_server_error_response

builds rich json response in case of internal server error
"""


def build_internal_server_error_response(user_id, src, channel, bot_id, language_template_obj):
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        response["user_id"] = ""
        response["bot_id"] = ""
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"]["recommendations"] = []
        response["response"]["tooltip_response"] = ""
        response["response"]["speech_response"][
            "text"] = language_template_obj.get_internal_server_error_text()
        response["response"]["speech_response"][
            "reprompt_text"] = language_template_obj.get_internal_server_error_text()
        response["response"]["text_response"][
            "text"] = language_template_obj.get_internal_server_error_text()
        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
        response["status_code"] = 500
        response["status_message"] = str(e)
    return response


"""
function: build_autocorrect_response
input params:
    user: active user object
    bot_obj: active bot object
    user_message: user actual message
    corrected_message: corrected user message
output:
    return rich bot json response
"""


def build_autocorrect_response(user, bot_obj, user_message, corrected_message, src, channel, language_template_obj):
    logger.info("Into buildAutoCorrectResponse...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        response["user_id"] = user.user_id
        response["bot_id"] = bot_obj.pk
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"]["recommendations"] = [
            corrected_message, user_message]

        response["response"]["tooltip_response"] = ""
        response["response"]["speech_response"][
            "text"] = language_template_obj.get_did_you_mean_text() + "\n" + str(autocorrect_suggestion_str)
        response["response"]["speech_response"][
            "reprompt_text"] = language_template_obj.get_did_you_mean_text() + "\n" + str(autocorrect_suggestion_str)
        response["response"]["text_response"][
            "text"] = language_template_obj.get_did_you_mean_text() + "\n" + str(autocorrect_suggestion_str)
        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
        response["status_code"] = 500
        response["status_message"] = str(e)

    logger.info("Exit from buildAutoCorrectResponse...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    return response


"""
function: build_whatsapp_spam_response
input params:
    user: active user object
    bot_obj: active bot object
    selected_language: user selected language
    query_status: query health
output:
    return rich bot json response
"""


def build_whatsapp_spam_response(user, channel_obj, bot_obj, selected_language, query_status, BlockConfig, BotChannel, Language, LanguageTunedBotChannel):
    logger.info("Into build_whatsapp_spam_response...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(selected_language), 'channel': "WhatsApp", 'bot_id': str(bot_obj.pk)})
    user.tree = None
    user.save(update_fields=["tree"])
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        block_config_obj = BlockConfig.objects.filter(bot=bot_obj).first()
        bot_response = ""
        intent_name = ""

        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel_obj).first()
        lang_obj = Language.objects.filter(lang=selected_language).first()
        language_tuned_objects = LanguageTunedBotChannel.objects.filter(
            language=lang_obj, bot_channel=bot_channel_obj).first()
        if language_tuned_objects:
            language_tuned_block_spam_data = json.loads(language_tuned_objects.block_spam_data)
        else:
            language_tuned_block_spam_data = {}

        if query_status == "query_warning":
            bot_response = block_config_obj.user_query_warning_message_text
            if language_tuned_block_spam_data != {} and selected_language != "en":
                bot_response = language_tuned_block_spam_data["query_warning_message_text"]
            intent_name = "User query warning response"
        elif query_status == "query_block":
            bot_response = block_config_obj.user_query_block_message_text
            if language_tuned_block_spam_data != {} and selected_language != "en":
                bot_response = language_tuned_block_spam_data["query_block_message_text"]
            intent_name = "User query block response"
        elif query_status == "keyword_warning":
            bot_response = block_config_obj.spam_keywords_warning_message_text
            if language_tuned_block_spam_data != {} and selected_language != "en":
                bot_response = language_tuned_block_spam_data["keywords_warning_message_text"]
            intent_name = "Keyword warning response"
        elif query_status == "keyword_block":
            bot_response = block_config_obj.spam_keywords_block_message_text
            if language_tuned_block_spam_data != {} and selected_language != "en":
                bot_response = language_tuned_block_spam_data["keywords_block_message_text"]
            intent_name = "Keyword block response"
        elif query_status == "ignore":
            bot_response = ""
            intent_name = "Spam user"
            
        response["user_id"] = user.user_id
        response["bot_id"] = bot_obj.pk
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["intent_name"] = intent_name
        response["response"]["is_response_to_be_language_processed"] = selected_language != "en"
        response["response"]["speech_response"][
            "text"] = bot_response
        response["response"]["speech_response"][
            "reprompt_text"] = bot_response
        response["response"]["text_response"][
            "text"] = bot_response

        response["response"]["easy_search_results"] = []

        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("build_whatsapp_spam_response: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(selected_language), 'channel': "WhatsApp", 'bot_id': str(bot_obj.pk)})
        response["status_code"] = 500
        response["status_message"] = str(e)
    
    logger.info("Exit from build_whatsapp_spam_response...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(selected_language), 'channel': "WhatsApp", 'bot_id': str(bot_obj.pk)})
    return response


"""
function: build_abuse_detected_response
input params:
    user: active user object
    bot_obj: active bot object
    message: user message
output:
    return rich bot json response
"""


def build_abuse_detected_response(user, bot_obj, message, channel, src, language_template_obj):
    logger.info("Into build_abuse_detected_response...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    user.tree = None
    user.save()
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        response["user_id"] = user.user_id
        response["bot_id"] = bot_obj.pk
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"]["speech_response"][
            "text"] = language_template_obj.get_upset_text()
        response["response"]["speech_response"][
            "reprompt_text"] = language_template_obj.get_upset_text()
        response["response"]["text_response"][
            "text"] = language_template_obj.get_upset_text()

        response["response"]["easy_search_results"] = []
        response["response"]["is_text_to_speech_required"] = bot_obj.is_text_to_speech_required

        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
        response["status_code"] = 500
        response["status_message"] = str(e)

    logger.info("Exit from build_abuse_detected_response...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
    return response


"""
function: build_emoji_detected_response
input params:
    user: active user object
    bot_obj: active bot object
    message: user message
output:
    return rich bot json response
"""


def build_emoji_detected_response(user, bot_obj, message, src, emoji_sentiment_detected, EmojiBotResponse,
                                  LanguageTunedBot, Language):
    logger.info("Into build_emoji_detected_response...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': '', 'bot_id': str(bot_obj.pk)})
    user.tree = None
    user.save()
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        response["user_id"] = user.user_id
        response["bot_id"] = bot_obj.pk
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        emoji_bot_response_obj = EmojiBotResponse.objects.filter(bot=bot_obj)
        if emoji_bot_response_obj.count() == 0:
            emoji_bot_response_obj = EmojiBotResponse.objects.create(
                bot=bot_obj)
        else:
            emoji_bot_response_obj = emoji_bot_response_obj.first()

        add_livechat_intent = emoji_bot_response_obj.add_livechat_intent
        if src != "en":
            lang_obj = Language.objects.get(lang=src)
            lang_bot_obj = LanguageTunedBot.objects.filter(
                bot=bot_obj, language=lang_obj)

            if lang_bot_obj.exists():
                emoji_bot_response_obj = lang_bot_obj.first()

        speech_response_text, speech_response_reprompt_text, text_response_text = build_emoji_response_based_on_sentiment(
            emoji_sentiment_detected, emoji_bot_response_obj)

        response["response"]["speech_response"][
            "text"] = speech_response_text
        response["response"]["speech_response"][
            "reprompt_text"] = speech_response_reprompt_text
        response["response"]["text_response"][
            "text"] = text_response_text
        response["response"][
            "is_text_to_speech_required"] = bot_obj.is_text_to_speech_required
        if bot_obj.is_livechat_enabled:
            add_livechat_intent = json.loads(add_livechat_intent)
            if add_livechat_intent[emoji_sentiment_detected.lower()] == "True":
                intent_obj = bot_obj.livechat_default_intent
                suggestion_list = []
                suggestion_list.append(
                    {"name": intent_obj.name, "id": intent_obj.pk})
                response["response"]["recommendations"] = suggestion_list

        response["response"]["easy_search_results"] = []

        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
        response["response"]["is_go_back_enabled"] = False

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: build_emoji_detected_response %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(user.user_id), 'source': str(src), 'channel': '', 'bot_id': str(bot_obj.pk)})
        response["status_code"] = 500
        response["status_message"] = str(e)

    logger.info("Exit from build_emoji_detected_response...", extra={'AppName': 'EasyChat', 'user_id': str(
        user.user_id), 'source': str(src), 'channel': '', 'bot_id': str(bot_obj.pk)})
    return response


def build_emoji_response_based_on_sentiment(emoji_sentiment_detected, emoji_bot_response_obj):
    try:
        speech_response_text = ""
        speech_response_reprompt_text = ""
        text_response_text = ""
        if emoji_sentiment_detected == "Angry":
            speech_response = process_speech_response_query(
                emoji_bot_response_obj.emoji_angry_response_text)
            speech_response_text = speech_response
            speech_response_reprompt_text = speech_response
            text_response_text = emoji_bot_response_obj.emoji_angry_response_text

        elif emoji_sentiment_detected == "Happy":
            speech_response = process_speech_response_query(
                emoji_bot_response_obj.emoji_happy_response_text)
            speech_response_text = speech_response
            speech_response_reprompt_text = speech_response
            text_response_text = emoji_bot_response_obj.emoji_happy_response_text

        elif emoji_sentiment_detected == "neutral":
            speech_response = process_speech_response_query(
                emoji_bot_response_obj.emoji_neutral_response_text)
            speech_response_text = speech_response
            speech_response_reprompt_text = speech_response
            text_response_text = emoji_bot_response_obj.emoji_neutral_response_text

        elif emoji_sentiment_detected == "sad":
            speech_response = process_speech_response_query(
                emoji_bot_response_obj.emoji_sad_response_text)
            speech_response_text = speech_response
            speech_response_reprompt_text = speech_response
            text_response_text = emoji_bot_response_obj.emoji_sad_response_text

        return speech_response_text, speech_response_reprompt_text, text_response_text

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: build_emoji_response_based_on_sentiment %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

    return speech_response_text, speech_response_reprompt_text, text_response_text


"""
function: build_suggestion_response
input params:
    user: active user object
    bot_obj: active bot object
    suggestion_list: suggested intent name list
output:
    return rich json response
"""


def build_suggestion_response(user, bot_obj, suggestion_list, src, channel, language_template_obj):
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        suggestion_str = ""
        response["user_id"] = user.user_id
        response["bot_id"] = bot_obj.pk
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"]["recommendations"] = suggestion_list
        did_you_mean_text = language_template_obj.get_did_you_mean_text()

        response["response"]["tooltip_response"] = ""
        response["response"]["speech_response"][
            "text"] = did_you_mean_text + "\n" + str(suggestion_str)
        response["response"]["speech_response"][
            "reprompt_text"] = did_you_mean_text + "\n" + str(suggestion_str)
        response["response"]["text_response"][
            "text"] = did_you_mean_text + "\n" + str(suggestion_str)

        response["response"]["easy_search_results"] = []
        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            user.user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
        response["status_code"] = 500
        response["status_message"] = str(e)
    return response


"""
function: build_flow_break_response
input params:
    user: active user object
    bot_obj: active bot object
    message: flow break response
output:
    return rich json response
"""


def build_flow_break_response(user, bot_obj, message, src, channel, termination_confirmed=False, is_abort_flow=False):
    response = copy.deepcopy(DEFAULT_RESPONSE)
    try:
        # If flow_termination_user_confirmation_toggle is false then clear
        # user's tree
        if termination_confirmed:
            user.tree = None
            user.save()

        suggestion_list = []
        if not termination_confirmed or is_abort_flow:
            # android changes
            # if str(channel) != "Android":
            #     suggestion_list = ["Yes", "No"]
            # else:
            #     dict_yes = {
            #         "name": "Yes",
            #         "id": "nil"
            #     }
            #     suggestion_list.append(dict_yes)
            #     dict_no = {
            #         "name": "No",
            #         "id": "nil"
            #     }
            #     suggestion_list.append(dict_no)
            suggestion_list = ["Yes", "No"]

        response["user_id"] = user.user_id
        response["bot_id"] = bot_obj.pk
        response["status_code"] = "200"
        response["status_message"] = "SUCCESS"
        response["response"][
            "is_text_to_speech_required"] = bot_obj.is_text_to_speech_required
        response["response"]["recommendations"] = suggestion_list

        response["response"]["tooltip_response"] = ""
        speech_resp = process_speech_response_query(str(message))
        response["response"]["speech_response"][
            "text"] = speech_resp
        response["response"]["speech_response"][
            "reprompt_text"] = speech_resp
        response["response"]["text_response"][
            "text"] = str(message)

        response["response"]["easy_search_results"] = []
        response["response"]["is_flow_ended"] = True
        response["response"]["is_authentication_required"] = False
        response["response"]["is_bot_switch"] = False
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: build_flow_break_response %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': str(src), 'channel': str(channel), 'bot_id': 'None'})
        response["status_code"] = 500
        response["status_message"] = str(e)
    return response


"""
function: total_time
input params:
    TimeSpentByUsers: TimeSpentByUsers model
output params:
    total time: total time spent by alll user

returns total time spent by all user. Ex. If user1 spent 3,4 second and user2 spent 1,2 second on the bot, then it will return 10seconds in total
"""


def total_time(TimeSpentByUsers):  # noqa: N803
    total_time = 0
    timespent_objs = TimeSpentByUsers.objects.all()
    for time_obj in timespent_objs:
        time_delta = (time_obj.end_datetime - time_obj.start_datetime)
        total_time = total_time + int(time_delta.total_seconds())
    return total_time


"""
function: user_count
input params:
    TimeSpentByUsers: TimeSpentByUsers model
output params:
    user_count: number of all users

returns total number of users, who have open the chat window. There may be duplicate users.
"""


def user_count(TimeSpentByUsers):  # noqa: N803

    user_count = 0
    user_count = TimeSpentByUsers.objects.all().count()
    return user_count


"""
function: total_number_of_answered_queries
input params:
    bot_objs: Bot object model
output params:
    user_count: total number of answered queries

returns total number of users in specified bot

"""


def total_number_of_answered_queries(bot_objs, MISDashboard):
    return MISDashboard.objects.filter(bot__in=bot_objs).filter(~Q(intent_name=None)).count()


"""
function: get_average_number_of_message_per_session
input params:
    bot_objs: Bot object model
output params:
    average_number_of_message: Average number of messages per session

returns total number of users in specified bot

"""


def get_bot_accuracy(mis_objects):
    from EasyChatApp.models import BotInfo
    total_queries = mis_objects.count()
    if total_queries > 0:
        total_unanswered_queries = mis_objects.filter(
            intent_name=None, is_unidentified_query=True).count()
        exclude_intuitive_query_from_bot_accuracy = BotInfo.objects.filter(
            bot=mis_objects[0].bot).values_list("exclude_intuitive_query_from_bot_accuracy", flat=True)[0]
        total_intuitive_queries = mis_objects.filter(
            is_intiuitive_query=True).count()

        bot_accuracy = round(
            (100 * (total_queries - total_unanswered_queries)) / total_queries, 2) if exclude_intuitive_query_from_bot_accuracy else round(
            (100 * (total_queries - (total_unanswered_queries + total_intuitive_queries)) / total_queries, 2))

        if bot_accuracy != None:
            return bot_accuracy
        else:
            return "No data available for this channel"
    else:
        return "No data available for this channel"


def get_average_number_of_message_per_session(mis_objects):
    session_fre = list(mis_objects.values("session_id").order_by(
        "session_id").annotate(frequency=Count("session_id")))

    if len(session_fre) == 0:
        return 0, 0

    total_sessions = len(session_fre)

    total_messages = 0
    for session_detail in session_fre:
        total_messages += session_detail["frequency"]

    # logger.info(total_messages, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return int(total_messages / float(total_sessions)), total_sessions


"""
function: get_average_session_time
input params:
    TimeSpentByUser:
    bot_objs: list of bot objects
output:
    returns average time spent by users on bots
"""


def get_time_in_standard_format(time_in_seconds):
    time = "0s"
    try:
        hour = (time_in_seconds) // 3600
        rem = (time_in_seconds) % 3600
        minute = rem // 60
        sec = rem % 60
        time = ""
        if hour != 0:
            time = str(hour) + "h "
        if minute != 0:
            time += str(minute) + "m "
        time += str(sec) + "s"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in get_total_offline_time %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
        pass

    return time


def get_average_session_time(bot_objs, TimeSpentByUser, datetime_start, datetime_end):
    from django.db.models import Sum
    time_spent_objs = TimeSpentByUser.objects.filter(
        bot__in=bot_objs, start_datetime__date__gte=datetime_start, end_datetime__date__lte=datetime_end)
    total_sessions = time_spent_objs.count()

    total_seconds = time_spent_objs.aggregate(Sum('total_time_spent'))[
        'total_time_spent__sum']
    if total_seconds == None:
        total_seconds = 0

    logger.info(total_sessions, extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    if total_sessions == 0:
        return 0

    logger.info(total_seconds, extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return int(total_seconds / float(total_sessions))


"""
function: get_intent_frequency
input params:
    MISDashboard: Misboard model
    bot_objs: list of bot objects
output:
    returns list of intents with their frequency
"""


def get_intent_frequency(bot_objs, MISDashboard, UserSessionHealth, start_date, end_date, channel_name='All', category_name='All',
                         selected_language="All", supported_languages=[]):
    mis_objects = return_mis_objects_based_on_category_channel_language(
        start_date, end_date, bot_objs, channel_name, category_name, selected_language, supported_languages,
        MISDashboard, UserSessionHealth)

    mis_objects = mis_objects.filter(small_talk_intent=False)

    intent_frequency = list(mis_objects.filter(~Q(intent_name=None)).values(
        "intent_recognized__name", "intent_recognized").order_by("intent_recognized__name").annotate(intent_name=F("intent_recognized__name"), frequency=Count("intent_recognized__name")).order_by(
        '-frequency').exclude(intent_name="INFLOW-INTENT"))

    return intent_frequency


"""
function: get_recently_unanswered_messages
input params:
    MISDashboard: Misboard model
    bot_objs: list of bot objects
output:
    returns unanswered messages
"""


def get_recently_unanswered_messages(bot_objs, MISDashboard, UserSessionHealth, UnAnsweredQueries, Channel, start_date, end_date,
                                     channel_name='All', selected_language="All", supported_languages=[], search_term=""):
    try:
        import math
        from django.db.models import Sum
        from EasyChatApp.utils_bot import get_translated_text_with_api_status
        from EasyChatApp.models import EasyChatTranslationCache
        today_date = datetime.datetime.now().date()
        if channel_name == 'All' and selected_language.lower() == "all":
            mis_objs = MISDashboard.objects.filter(
                bot__in=bot_objs, intent_name=None, status="2", is_intiuitive_query=False, creation_date=today_date).order_by("-creation_date")
        elif channel_name == 'All':
            mis_objs = MISDashboard.objects.filter(
                bot__in=bot_objs, intent_name=None, status="2", is_intiuitive_query=False,
                selected_language__in=supported_languages, creation_date=today_date).order_by("-creation_date")

        elif selected_language.lower() == "all":
            mis_objs = MISDashboard.objects.filter(
                bot__in=bot_objs, intent_name=None, channel_name=channel_name, status="2",
                is_intiuitive_query=False, creation_date=today_date).order_by("-creation_date")

        else:
            mis_objs = MISDashboard.objects.filter(
                bot__in=bot_objs, intent_name=None, channel_name=channel_name, status="2", is_intiuitive_query=False,
                selected_language__in=supported_languages, creation_date=today_date).order_by("-creation_date")

        mis_objs = return_mis_objects_excluding_blocked_sessions(mis_objs, UserSessionHealth)
        bot_obj = bot_objs[0]
        for mis_obj in mis_objs.iterator():
            msg_rcvd = mis_obj.get_message_received()
            mis_obj.status = "1"
            mis_obj.save(update_fields=['status'])
            lang_obj = mis_obj.selected_language
            mis_creation_date = mis_obj.creation_date
            channel_obj = Channel.objects.get(name=mis_obj.channel_name)
            try:
                unanswered_query = UnAnsweredQueries.objects.filter(
                    unanswered_message=msg_rcvd, channel=channel_obj, bot=bot_obj, date=mis_creation_date).order_by('-count')
            except Exception:
                logger.error('get_recently_unanswered_messages', extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                unanswered_query = UnAnsweredQueries.objects.filter(
                    unanswered_message=msg_rcvd, channel=channel_obj, bot=bot_obj, date=mis_creation_date)
                pass
            if unanswered_query:
                unanswered_query[0].count = unanswered_query[0].count + 1
                unanswered_query[0].save()
            else:
                UnAnsweredQueries.objects.create(
                    unanswered_message=msg_rcvd, count=1, channel=channel_obj, bot=bot_obj,
                    selected_language=lang_obj, date=mis_creation_date)

        if channel_name == 'All' and selected_language.lower() == "all":
            unanswered_queries = UnAnsweredQueries.objects.filter(
                bot=bot_obj, date__gte=start_date, date__lte=end_date).order_by('-count')
        elif channel_name == 'All':
            unanswered_queries = UnAnsweredQueries.objects.filter(
                bot=bot_obj, date__gte=start_date, date__lte=end_date,
                selected_language__in=supported_languages).order_by('-count')
        elif selected_language.lower() == "all":
            unanswered_queries = UnAnsweredQueries.objects.filter(
                bot=bot_obj, date__gte=start_date, date__lte=end_date,
                channel=Channel.objects.get(name=channel_name)).order_by('-count')
        else:
            unanswered_queries = UnAnsweredQueries.objects.filter(
                bot=bot_obj, date__gte=start_date, date__lte=end_date,
                channel=Channel.objects.get(name=channel_name), selected_language__in=supported_languages).order_by(
                '-count')
        
        unanswered_queries = unanswered_queries.exclude(unanswered_message="")

        if search_term:
            unanswered_queries = unanswered_queries.filter(unanswered_message__icontains=search_term)

        return unanswered_queries.values_list("unanswered_message").annotate(total=Sum("count")).order_by("-total")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("UnAnsweredQueries %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': '', 'channel': '', 'bot_id': 'None'})
        return []


def get_intuitive_messages(bot_objs, MISDashboard, IntuitiveQuestions, Channel, start_date, end_date,
                           channel_name='All', selected_language="All", supported_languages=[], page=1, dropdown_language="en", translate_api_status=True, search_term=""):
    try:
        import math
        from django.db.models import Sum
        from EasyChatApp.utils_bot import get_translated_text_with_api_status
        from EasyChatApp.models import EasyChatTranslationCache

        pagination_data = {
            "is_last_page": True
        }

        if channel_name == 'All' and selected_language.lower() == "all":
            intuitive_queries = IntuitiveQuestions.objects.filter(
                bot=bot_objs[0], date__gte=start_date, date__lte=end_date).order_by('intuitive_message_query_hash')
        elif channel_name == 'All':
            intuitive_queries = IntuitiveQuestions.objects.filter(
                bot=bot_objs[0], date__gte=start_date, date__lte=end_date,
                selected_language__in=supported_languages).order_by('intuitive_message_query_hash')

        elif selected_language.lower() == "all":
            intuitive_queries = IntuitiveQuestions.objects.filter(
                channel=channel_name, bot=bot_objs[0], date__gte=start_date, date__lte=end_date).order_by(
                'intuitive_message_query_hash')

        else:
            intuitive_queries = IntuitiveQuestions.objects.filter(
                channel=channel_name, bot=bot_objs[0], date__gte=start_date, date__lte=end_date,
                selected_language__in=supported_languages).order_by('intuitive_message_query_hash')

        count = 1
        start_count = ((int(page) - 1) * 5) + 1
        end_count = (int(page) * 5) + 1
        is_last_page = True
        
        intuitive_queries = intuitive_queries.exclude(intuitive_message_query="")
        intuitive_counts_mapping = intuitive_queries.values("intuitive_message_query_hash", "intuitive_message_query").annotate(total=Sum("count")).order_by("-total")
        intuitive_list_questions = []
        intuitive_count_list = []
        intuitive_lang_count_list = []

        for intuitive_data in intuitive_counts_mapping.iterator():
            multilingual_name, translate_api_status = get_translated_text_with_api_status(intuitive_data["intuitive_message_query"], dropdown_language, EasyChatTranslationCache, translate_api_status)
            if search_term:
                if dropdown_language != "en" and search_term.lower() not in multilingual_name.lower():
                    continue
                if dropdown_language == "en" and search_term.lower() not in intuitive_data["intuitive_message_query"].lower():
                    continue

            if count < start_count:
                count += 1
                continue
            elif count >= end_count:
                is_last_page = False
                break

            intuitive_hash_queries = intuitive_queries.filter(intuitive_message_query_hash=intuitive_data["intuitive_message_query_hash"]).order_by("date")
            suggested_intents_dict = {}

            for intuitive_query in intuitive_hash_queries.iterator():
                suggested_intents = intuitive_query.suggested_intents.all()
                suggested_intents_set = set()
                for intent in suggested_intents:
                    if str(intent.pk) not in suggested_intents_dict:
                        suggested_intents_dict[str(intent.pk)], translate_api_status = create_dict_per_intuitive_intent(intent, dropdown_language, translate_api_status)
                        suggested_intents_set.add(str(intent.pk))

                intent_difference = set(suggested_intents_dict.keys()).difference(suggested_intents_set)
                for intent_pk in intent_difference:
                    suggested_intents_dict[intent_pk]["resolved"] = "true"

            intuitive_list_questions.append(list(suggested_intents_dict.values()))
            intuitive_count_list.append((intuitive_data["intuitive_message_query"], intuitive_data["total"]))
            intuitive_lang_count_list.append((multilingual_name, intuitive_data["total"]))
            count += 1

        if translate_api_status:
            intuitive_count_list = intuitive_lang_count_list

        pagination_data["is_last_page"] = is_last_page

        return intuitive_count_list, intuitive_list_questions, translate_api_status, pagination_data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_intuitive_messages %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': '', 'channel': '', 'bot_id': 'None'})
        return [], [], translate_api_status, pagination_data


def create_dict_per_intuitive_intent(intent, selected_language="en", translate_api_status=True):
    try:
        multilingual_intent_name, translate_api_status = get_multilingual_intent_obj_name(
            intent, selected_language, translate_api_status)

        dict_intent = {
            "name": intent.name,
            "pk": str(intent.pk),
            "resolved": "false",
            "deleted": str(intent.is_deleted).lower(),
            "multilingual_intent_name": multilingual_intent_name
        }
        
        return dict_intent, translate_api_status
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_dict_per_intuitive_intent %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': '', 'channel': '', 'bot_id': 'None'})
        return {}, translate_api_status


"""
function: get_window_location_frequency
input params:
    MISDashboard: Misboard model
    bot_objs: list of bot objects
    datetime_start: start date
    datetime_end: end date
output:
    returns frequency of every hosts from where the bot gets request

Ex. [{"localhost": 5}, {"13.233.0.125": 3}]
"""


def get_window_location_frequency(bot_objs, TrafficSources, datetime_start, datetime_end, channel_name='All'):
    web_pages_name = []
    web_page_visited_count = []
    bot_clicked_count = []

    if (channel_name == 'All' or channel_name == 'Web'):
        traffic_sources_objects = TrafficSources.objects.filter(
            visiting_date__gte=datetime_start, visiting_date__lte=datetime_end, bot=bot_objs).order_by(
            '-bot_clicked_count')

        for traffic_sources_object in traffic_sources_objects:
            if traffic_sources_object.web_page in web_pages_name:
                web_page_visited_count[web_pages_name.index(traffic_sources_object.web_page)] = web_page_visited_count[web_pages_name.index(
                    traffic_sources_object.web_page)] + traffic_sources_object.web_page_visited
                bot_clicked_count[web_pages_name.index(traffic_sources_object.web_page)] = bot_clicked_count[web_pages_name.index(
                    traffic_sources_object.web_page)] + traffic_sources_object.bot_clicked_count
            else:
                regex_webpage = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                url_check = re.findall(
                    regex_webpage, traffic_sources_object.web_page)
                if (len(url_check) >= 1):
                    web_pages_name.append(traffic_sources_object.web_page)
                    web_page_visited_count.append(
                        traffic_sources_object.web_page_visited)
                    bot_clicked_count.append(
                        traffic_sources_object.bot_clicked_count)

    return web_pages_name, web_page_visited_count, bot_clicked_count


"""
function: get_word_count_from_MIS
input params:
    query_type: Query type : day, week , month, 6months
    MISDashboard: Misboard model
    bot_objs: list of bot objects
    year: year for which you want data
    month: month for which you want data
    day: day for which you want data
output:
    returns word dict containing word and its frequesncy
"""


def get_word_count_from_mis(bot_objs, MISDashboard, UserSessionHealth, datetime_start, datetime_end, category_name, channel_name='All',
                            language='All'):
    word_freq_data = []
    try:
        if channel_name == 'All' and language == 'All':
            mis_objects = MISDashboard.objects.filter(~Q(intent_name="INFLOW-INTENT"),
                                                      bot__in=bot_objs, creation_date__gte=datetime_start,
                                                      creation_date__lte=datetime_end, category__name=category_name)
        elif channel_name == 'All':
            mis_objects = MISDashboard.objects.filter(~Q(intent_name="INFLOW-INTENT"),
                                                      bot__in=bot_objs, creation_date__gte=datetime_start,
                                                      creation_date__lte=datetime_end, category__name=category_name,
                                                      selected_language=language)
        elif language == 'All':
            mis_objects = MISDashboard.objects.filter(~Q(intent_name="INFLOW-INTENT"),
                                                      bot__in=bot_objs, creation_date__gte=datetime_start,
                                                      creation_date__lte=datetime_end,
                                                      channel_name=channel_name, category__name=category_name)
        else:
            mis_objects = MISDashboard.objects.filter(~Q(intent_name="INFLOW-INTENT"),
                                                      bot__in=bot_objs, creation_date__gte=datetime_start,
                                                      creation_date__lte=datetime_end,
                                                      channel_name=channel_name, category__name=category_name,
                                                      selected_language=language)
        
        mis_objects = return_mis_objects_excluding_blocked_sessions(mis_objects, UserSessionHealth)

        sentence_list = []
        for mis_obj in mis_objects.iterator():
            if not mis_obj.is_small_talk_intent():
                sentence_list.append(
                    {'message_received': mis_obj.get_message_received()})

        sentence_list = {v['message_received']: v for v in sentence_list}.values()
        sentence_data = ""
        for elm in sentence_list:
            sentence_data += " " + str(elm["message_received"]).lower()

        sentence_data = re.sub(r'\W+', ' ', sentence_data)

        token_list = nltk.word_tokenize(sentence_data)

        token_list = [token for token in token_list if token not in stop]

        fdist1 = nltk.FreqDist(token_list).most_common(500)

        word_freq_data = []
        for (word, freq) in fdist1:
            if not word.isdigit():
                temp_dict = {
                    "word": word,
                    "freq": freq,
                }
                word_freq_data.append(temp_dict)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ERROR get_word_count_from_MIS %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return word_freq_data


def embed_url(video_url):
    try:
        regex = r"(?:https:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(.+)"
        return re.sub(regex, r"https://www.youtube.com/embed/\1", video_url)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ERROR embed_url %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return video_url


def get_max_intent_category_name(bot_objs, MISDashboard, UserSessionHealth, start_date, end_date, channel_name='All', selected_language="All", supported_languages=[]):
    mis_objects = MISDashboard.objects.filter(
        bot__in=bot_objs, creation_date__gte=start_date, creation_date__lte=end_date)

    mis_objects = return_mis_objects_excluding_blocked_sessions(mis_objects, UserSessionHealth)

    if channel_name != 'All':
        mis_objects = mis_objects.filter(channel_name=channel_name)

    if selected_language.lower() != "all":
        mis_objects = mis_objects.filter(
            selected_language__in=supported_languages)

    return mis_objects.filter(small_talk_intent=False).values("category__name").order_by("category__name").annotate(frequency=Count("category__name")).order_by('-frequency').exclude(category__name=None).distinct()


def get_category_wise_intent_frequency(bot_objs, MISDashboard, UserSessionHealth, start_date, end_date, category_name, channel_name='All',
                                       global_filter_category_name='All', selected_language="All",
                                       supported_languages=[]):
    if global_filter_category_name == 'All':
        mis_objects = MISDashboard.objects.filter(
            bot__in=bot_objs, creation_date__gte=start_date, creation_date__lte=end_date)

        mis_objects = return_mis_objects_excluding_blocked_sessions(mis_objects, UserSessionHealth)

        if channel_name != 'All':
            mis_objects = mis_objects.filter(channel_name=channel_name)

        if selected_language.lower() != "all":
            mis_objects = mis_objects.filter(
                selected_language__in=supported_languages)

        if category_name == "All":
            intent_frequency = list(mis_objects.filter(small_talk_intent=False).exclude(intent_name=None).values(
                "intent_recognized__name", "intent_recognized").order_by("intent_recognized__name").annotate(intent_name=F("intent_recognized__name"), frequency=Count("intent_recognized__name")).order_by('-frequency'))
        else:
            intent_frequency = list(mis_objects.filter(category__name=category_name, small_talk_intent=False).exclude(intent_name=None).values(
                "intent_recognized__name", "intent_recognized").order_by("intent_recognized__name").annotate(intent_name=F("intent_recognized__name"), frequency=Count("intent_recognized__name")).order_by('-frequency'))

    else:
        mis_objects = MISDashboard.objects.filter(
            bot__in=bot_objs, creation_date__gte=start_date, creation_date__lte=end_date,
            category__name=global_filter_category_name)

        mis_objects = return_mis_objects_excluding_blocked_sessions(mis_objects, UserSessionHealth)

        if channel_name != 'All':
            mis_objects = mis_objects.filter(channel_name=channel_name)

        if selected_language.lower() != "all":
            mis_objects = mis_objects.filter(
                selected_language__in=supported_languages)

        intent_frequency = list(mis_objects.filter(small_talk_intent=False).exclude(intent_name=None).values(
            "intent_recognized__name", "intent_recognized").order_by("intent_recognized__name").annotate(
            intent_name=F("intent_recognized__name"), frequency=Count("intent_recognized__name")).order_by('-frequency'))
            
    return intent_frequency


# def export_frequent_intent(Bot, MISDashboard, bot_pk, reverse, username):
#     path_to_file = None

#     try:
#         logger.info("In function export_frequent_intent", extra={
#             'AppName': 'EasyChat', 'user_id': username, 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#         uat_bot_obj = Bot.objects.get(
#             pk=int(bot_pk), is_deleted=False, is_uat=True)

#         prod_bot_obj = None

#         bot_objs = []
#         if prod_bot_obj == None:
#             bot_objs = [uat_bot_obj]
#         else:
#             bot_objs = [prod_bot_obj]

#         intent_frequency_list = get_intent_frequency(
#             bot_objs, MISDashboard)

#         if str(reverse).lower() == "false":
#             intent_frequency_list.reverse()

#         from xlwt import Workbook
#         export_intent_wb = Workbook()
#         sheet_name = "Frequent Questions"
#         sheet1 = export_intent_wb.add_sheet(sheet_name)
#         sheet1.write(0, 0, "Questions")
#         sheet1.write(0, 1, "Frequency")

#         index = 1
#         for intent_frequency in intent_frequency_list:
#             sheet1.write(index, 0, intent_frequency["intent_name"])
#             sheet1.write(index, 1, intent_frequency["frequency"])
#             index += 1
#         if str(reverse).lower() == "false":
#             filename = str(username) + "-" + \
#                 str(uat_bot_obj.slug) + "-least-frequent-questions.xls"
#         else:
#             filename = str(username) + "-" + \
#                 str(uat_bot_obj.slug) + "-most-frequent-questions.xls"
#         export_intent_wb.save(settings.MEDIA_ROOT + "private/" + filename)
#         path_to_file = '/files/private/' + str(filename)

#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("ERROR export_frequent_intent %s at %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

#     return path_to_file


def export_form_assist_intent(Bot, Intent, FormAssist, FormAssistAnalytics, bot_pk, username,
                              is_language_filter_applied, supported_languages, dropdown_language="en", email_id="", to_be_mailed=False, export_request_obj=None, start_date=None, end_date=None):
    file_url = None
    try:
        from EasyChatApp.utils import send_mail_of_analytics
        from EasyChatApp.models import EasyChatAppFileAccessManagement
        logger.info("In function export_form_assist_intent", extra={
            'AppName': 'EasyChat', 'user_id': username, 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_form_assist_enabled=True)

        intent_objs = Intent.objects.filter(
            bots=uat_bot_obj, is_form_assist_enabled=True, is_hidden=False)
        intent_frequency_list_english = []
        intent_frequency_list_multilingual = []
        translate_api_status = True
        for intent_obj in intent_objs:
            form_assist_id = FormAssist.objects.filter(
                intent=intent_obj, bot=uat_bot_obj).first()

            if form_assist_id:
                if is_language_filter_applied:
                    if (start_date == None or end_date == None):
                        form_assist_field = FormAssistAnalytics.objects.filter(
                            bot=uat_bot_obj, form_assist_field=form_assist_id, selected_language__in=supported_languages)
                    else:
                        form_assist_field = FormAssistAnalytics.objects.filter(
                            bot=uat_bot_obj, form_assist_field=form_assist_id, selected_language__in=supported_languages, lead_datetime__date__gte=start_date, lead_datetime__date__lte=end_date)
                else:
                    if (start_date == None or end_date == None):
                        form_assist_field = FormAssistAnalytics.objects.filter(
                            bot=uat_bot_obj, form_assist_field=form_assist_id)
                    else:
                        form_assist_field = FormAssistAnalytics.objects.filter(
                            bot=uat_bot_obj, form_assist_field=form_assist_id, lead_datetime__date__gte=start_date, lead_datetime__date__lte=end_date)
                length_assist_field = len(form_assist_field)

                intent_frequency_list_english.append({
                    "intent": intent_obj.name,
                    "user_assisted": length_assist_field
                })
                if translate_api_status:
                    intent_multilingual_name, translate_api_status = get_multilingual_intent_obj_name(
                        intent_obj, dropdown_language, translate_api_status)
                    intent_frequency_list_multilingual.append({
                        "intent": intent_multilingual_name,
                        "user_assisted": length_assist_field
                    })

        language_text = "-"
        if is_language_filter_applied:
            language_text = list(
                supported_languages.values_list("name_in_english"))
            language_text = [lang[0] for lang in language_text]
            language_text = ", ".join(language_text)

        from xlwt import Workbook
        export_intent_wb = Workbook()
        sheet_name = "Most Used Intents"
        sheet1 = export_intent_wb.add_sheet(sheet_name)
        sheet1.write(0, 0, "Intent")
        sheet1.write(0, 1, "Frequency")
        if is_language_filter_applied:
            sheet1.write(0, 2, "Language")

        index = 1

        if translate_api_status:
            intent_frequency_list = intent_frequency_list_multilingual
        else:
            intent_frequency_list = intent_frequency_list_english

        for intent_frequency in intent_frequency_list:
            sheet1.write(index, 0, intent_frequency["intent"])
            sheet1.write(index, 1, intent_frequency["user_assisted"])
            if is_language_filter_applied:
                sheet1.write(index, 2, language_text)
            index += 1
        filename_for_mail = 'form-assist-intent' + \
                            start_date.strftime("%d-%m-%Y") + '_to_' + \
                            end_date.strftime("%d-%m-%Y")
        filename = filename_for_mail + '.xls'
        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)
        export_intent_wb.save(secured_files_path + filename)
        path = '/secured_files/EasyChatApp/custom_analytics/' + \
            str(bot_pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            send_mail_of_analytics('Form Assist Intents',
                                        file_url, email_id)
        else:
            return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ERROR export_form_assist_intent %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return file_url


def export_easy_chat_nps_excel(Bot, Feedback, bot_pk, username):
    path_to_file = None
    try:
        logger.info("In function export_easy_chat_nps_excel", extra={
            'AppName': 'EasyChat', 'user_id': username, 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_uat=True)

        feedback_objs = Feedback.objects.filter(bot=bot_obj)

        from xlwt import Workbook
        export_nps_wb = Workbook()
        sheet_name = "NPS Sheet"
        sheet1 = export_nps_wb.add_sheet(sheet_name)
        sheet1.write(0, 0, "Bot Name")
        sheet1.write(0, 1, "NPS Score")
        sheet1.write(0, 2, "Comments")

        index = 1
        for feedback_obj in feedback_objs:
            sheet1.write(index, 0, feedback_obj.bot.name)
            sheet1.write(index, 1, feedback_obj.rating)
            sheet1.write(index, 2, feedback_obj.comments)
            index += 1

        filename = str(username) + "-" + \
            str(bot_obj.slug) + "-NPS-sheet.xls"
        export_nps_wb.save(settings.MEDIA_ROOT + "private/" + filename)
        path_to_file = '/files/private/' + str(filename)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ERROR export_easy_chat_nps_excel %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return path_to_file


def get_parent_child_pair(root_tree_obj, tree_pk_list, parent_list):
    try:
        parent_list.append(root_tree_obj)
        for iterator in root_tree_obj.children.filter(is_deleted=False):
            if iterator not in parent_list:
                get_parent_child_pair(iterator, tree_pk_list, parent_list)
                tree_pk_list.append((root_tree_obj, iterator))

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_parent_child_pair: %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return tree_pk_list


def get_parent_child_pair_intent(root_tree_obj, tree_pk_list):
    try:
        for iterator in root_tree_obj.children.filter(is_deleted=False):
            get_parent_child_pair_intent(iterator, tree_pk_list)
            if iterator.api_tree != None and iterator.api_tree.apis_used != "":
                tree_pk_list.append((iterator, "api"))
            if iterator.post_processor != None and iterator.post_processor.apis_used != "":
                tree_pk_list.append((iterator, "post"))
            if iterator.pipe_processor != None and iterator.pipe_processor.apis_used != "":
                tree_pk_list.append((iterator, "pipe"))

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_parent_child_pair: %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return tree_pk_list


def get_child_tree_objs_flow_dropoff_analytics(root_tree_pk, root_child_tree_obj, tree_pk_list, flow_analytics_objects,
                                               flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj,
                                               count_intent_was_called, parent_list, child_parent_tuple, parent_node,
                                               level, result, selected_language="en", translate_api_status=True):
    try:
        from EasyChatApp.models import Tree
        from django.db.models import Sum

        dropoff_resp, translate_api_status = get_child_tree_flow_dropoff_analytics_data(
            root_tree_pk, root_child_tree_obj, flow_analytics_objects, flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj, count_intent_was_called, parent_node, level, selected_language, translate_api_status)
        if dropoff_resp:
            result.append(dropoff_resp)

        tree_pk_list.append(root_child_tree_obj.pk)
        child_tree_objs = root_child_tree_obj.children.filter(is_deleted=False)

        parent_list.append(root_child_tree_obj)
        for child_tree_obj in child_tree_objs:
            tuple_child = (root_child_tree_obj, child_tree_obj)
            if child_tree_obj not in parent_list or tuple_child not in child_parent_tuple:
                child_parent_tuple.append(tuple_child)
                result, translate_api_status = get_child_tree_objs_flow_dropoff_analytics(root_child_tree_obj.pk, child_tree_obj, tree_pk_list, flow_analytics_objects, flow_analytics_objects_that_day,
                                                                                          flow_termination_data_objs, intent_obj, count_intent_was_called, parent_list, child_parent_tuple, False, level + 1, result, selected_language, translate_api_status)

        return result, translate_api_status

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_child_tree_objs_flow_dropoff_analytics: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_child_tree_objs_flow_analytics(root_tree_pk, root_child_tree_obj, tree_pk_list, flow_analytics_objects,
                                       flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj,
                                       count_intent_was_called, parent_list, child_parent_tuple, parent_node, level,
                                       parent_node_actions, previous_node_actions, selected_language="en",
                                       translate_api_status=True):
    try:
        from EasyChatApp.models import Tree
        from django.db.models import Sum

        max_level = 0
        json_resp = {}
        json_resp["name"] = root_child_tree_obj.name.strip()
        json_resp["tree_pk"] = root_child_tree_obj.pk
        json_resp["parent_tree_pk"] = root_tree_pk
        if parent_node:
            json_resp["multilingual_name"], translate_api_status = get_multilingual_intent_obj_name(
                intent_obj, selected_language, translate_api_status)
            json_resp["behavior"] = "Parent Node"
        else:

            json_resp["multilingual_name"], translate_api_status = get_multilingual_tree_obj_name(
                root_child_tree_obj, selected_language, translate_api_status)
            json_resp["behavior"] = "Child Node"

        json_resp["level"] = "Level " + str(level)

        json_resp, flow_count, parent_node_actions, previous_node_actions = get_child_tree_flow_analytics_data(
            json_resp, root_tree_pk, root_child_tree_obj, flow_analytics_objects, flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj, count_intent_was_called, parent_node, level, parent_node_actions, previous_node_actions)

        tree_pk_list.append(root_child_tree_obj.pk)
        child_tree_objs = root_child_tree_obj.children.filter(is_deleted=False)

        temp_json = []
        parent_list.append(root_child_tree_obj)
        for child_tree_obj in child_tree_objs:
            tuple_child = (root_child_tree_obj, child_tree_obj)
            if child_tree_obj not in parent_list or tuple_child not in child_parent_tuple:
                child_parent_tuple.append(tuple_child)
                temp_json_output, max_level, translate_api_status = get_child_tree_objs_flow_analytics(
                    root_child_tree_obj.pk, child_tree_obj, tree_pk_list, flow_analytics_objects,
                    flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj, count_intent_was_called,
                    parent_list, child_parent_tuple, False, level + 1, parent_node_actions, previous_node_actions, selected_language, translate_api_status)
                temp_json.append(temp_json_output)

        json_resp["children"] = temp_json
        return json_resp, max(level, max_level), translate_api_status

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_child_tree_objs_flow_analytics: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_all_bot_flows_intent_pk_list(start_date, end_date, bot_objs, channels, Intent, Tree, FlowAnalytics,
                                     DailyFlowAnalytics):
    try:
        from django.db.models import Sum

        trees = Tree.objects.exclude(children=None)
        intent_objs = Intent.objects.filter(
            bots__in=bot_objs, tree__in=trees, is_deleted=False)
        intent_objs_trees = intent_objs.values('tree')

        intent_objs_ids_previous = list(
            DailyFlowAnalytics.objects.filter(intent_indentifed__in=intent_objs, current_tree__in=intent_objs_trees,
                                              created_time__date__gte=start_date,
                                              created_time__date__lte=end_date, channel__in=channels).values_list(
                'intent_indentifed', flat=True).distinct())

        intent_objs_ids_that_day = []
        if end_date.date() == datetime.datetime.now().date():
            intent_objs_ids_that_day = list(FlowAnalytics.objects.filter(intent_indentifed__in=intent_objs, current_tree__in=intent_objs_trees, created_time__date=end_date.date(), channel__in=channels).values_list('intent_indentifed', flat=True).distinct())

        intent_objs_ids = set(intent_objs_ids_previous +
                              intent_objs_ids_that_day)

        return intent_objs_ids

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_conversion_flow_counts_data: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return set()


def get_conversion_flow_counts_data(start_date, end_date, bot_objs, channels, Intent, Tree, FlowAnalytics, FlowTerminationData, DailyFlowAnalytics, selected_language):
    try:
        from django.db.models import Sum
        trees = Tree.objects.exclude(children=None)
        intent_objs = Intent.objects.filter(
            bots__in=bot_objs, tree__in=trees, is_deleted=False)
        intent_objs_trees = intent_objs.values('tree')

        intent_objs_ids_previous = list(
            DailyFlowAnalytics.objects.filter(intent_indentifed__in=intent_objs, current_tree__in=intent_objs_trees,
                                              created_time__date__gte=start_date,
                                              created_time__date__lte=end_date, channel__in=channels).values_list(
                'intent_indentifed', flat=True).distinct().order_by('intent_indentifed'))

        intent_objs_ids_that_day = []
        today_date = datetime.datetime.today().date()
        if end_date.date() == today_date:
            intent_objs_ids_that_day = list(FlowAnalytics.objects.filter(intent_indentifed__in=intent_objs, current_tree__in=intent_objs_trees, created_time__date=end_date, channel__in=channels).values_list('intent_indentifed', flat=True).distinct().order_by('intent_indentifed'))

        intent_objs_ids = set(intent_objs_ids_previous +
                              intent_objs_ids_that_day)

        flow_conversion_data = []
        translate_api_status = True
        for intent_obj_id in intent_objs_ids:
            intent_obj = Intent.objects.get(pk=int(intent_obj_id))
            flow_conversion_dict = {}
            flow_conversion_dict['id'] = intent_obj.pk
            flow_conversion_dict['name'] = intent_obj.tree.name

            flow_conversion_dict['multilingual_name'], translate_api_status = get_multilingual_intent_obj_name(
                intent_obj, selected_language, translate_api_status)

            intent_hit_count = \
                DailyFlowAnalytics.objects.filter(intent_indentifed=intent_obj, current_tree=intent_obj.tree,
                                                  created_time__date__gte=start_date,
                                                  created_time__date__lte=end_date, channel__in=channels).aggregate(
                    Sum('count'))['count__sum']
            if intent_hit_count is None:
                intent_hit_count = 0

            if end_date.date() == today_date:
                intent_hit_count += FlowAnalytics.objects.filter(intent_indentifed=intent_obj, current_tree=intent_obj.tree, created_time__date=end_date, channel__in=channels).count()
            flow_conversion_dict['hit_count'] = int(intent_hit_count)

            intent_complete_count = DailyFlowAnalytics.objects.filter(
                intent_indentifed=intent_obj, is_last_tree_child=True, created_time__date__gte=start_date,
                created_time__date__lte=end_date, channel__in=channels).aggregate(Sum('count'))['count__sum']
            if intent_complete_count is None:
                intent_complete_count = 0

            if end_date.date() == today_date:
                intent_complete_count += FlowAnalytics.objects.filter(intent_indentifed=intent_obj, is_last_tree_child=True, created_time__date=end_date, channel__in=channels).count()
            flow_conversion_dict['complete_count'] = int(intent_complete_count)

            flow_conversion_dict['abort_count'] = FlowTerminationData.objects.filter(
                intent=intent_obj, created_datetime__date__gte=start_date, created_datetime__date__lte=end_date,
                channel__in=channels).count()
            if flow_conversion_dict['hit_count'] == 0:
                flow_conversion_dict['flow_percent'] = 0
            else:
                flow_conversion_dict['flow_percent'] = int(
                    (flow_conversion_dict['complete_count'] / flow_conversion_dict['hit_count']) * 100)

            flow_conversion_data.append(flow_conversion_dict)

        flow_completion_data = sorted(
            list(flow_conversion_data), key=lambda i: i['flow_percent'], reverse=True)

        return flow_completion_data, translate_api_status
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_conversion_flow_counts_data: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_abort_flow_sheet(intent_id, startdate, enddate, channel_objs, abort_flow_sheet, FlowTerminationData, Tree,
                         Intent):
    try:
        datetime_start = startdate.split("-")
        start_date = datetime.datetime(int(datetime_start[0]), int(
            datetime_start[1]), int(datetime_start[2]))
        datetime_end = enddate.split("-")
        end_date = datetime.datetime(int(datetime_end[0]), int(
            datetime_end[1]), int(datetime_end[2]))
        abort_flow_sheet.write(0, 0, "Node Name")
        abort_flow_sheet.col(0).width = 256 * 75
        abort_flow_sheet.write(0, 1, "Intent Name/Flow Termination Keyword")
        abort_flow_sheet.col(0).width = 256 * 75
        abort_flow_sheet.write(0, 2, "Count")
        abort_flow_sheet.col(0).width = 256 * 75

        intent_obj = Intent.objects.get(pk=intent_id)
        flow_termination_objs = FlowTerminationData.objects.filter(intent=intent_obj,
                                                                   created_datetime__date__gte=start_date,
                                                                   created_datetime__date__lte=end_date,
                                                                   channel__in=channel_objs).values('tree',
                                                                                                    'termination_message').annotate(
            Count('pk'))

        index = 1
        for flow_termination_obj in flow_termination_objs:
            tree_obj = Tree.objects.get(pk=int(flow_termination_obj['tree']))
            abort_flow_sheet.write(index, 0, tree_obj.name)
            abort_flow_sheet.write(
                index, 1, flow_termination_obj['termination_message'])
            abort_flow_sheet.write(index, 2, str(
                flow_termination_obj['pk__count']))
            index += 1

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error add_abort_flow_sheet: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_child_tree_flow_dropoff_analytics_data(root_tree_pk, root_child_tree_obj, flow_analytics_objects,
                                               flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj,
                                               count_intent_was_called, parent_node, level, selected_language="en", translate_api_status=True):
    try:
        from EasyChatApp.models import Tree
        from django.db.models import Sum

        response = {}

        flow_count = 0
        if level != 1:
            flow_analytics_objects_count = flow_analytics_objects.filter(previous_tree=Tree.objects.get(
                pk=root_tree_pk), current_tree=root_child_tree_obj).aggregate(Sum('count'))['count__sum']
            if flow_analytics_objects_count == None:
                flow_analytics_objects_count = 0
            flow_count = flow_analytics_objects_count + flow_analytics_objects_that_day.filter(
                previous_tree=Tree.objects.get(pk=root_tree_pk), current_tree=root_child_tree_obj).count()
        else:
            flow_count = count_intent_was_called

        flow_click = 0
        if not root_child_tree_obj.children.filter(is_deleted=False):
            return None, translate_api_status

        elif flow_count != 0 and count_intent_was_called != 0:
            previous_flow_click = flow_analytics_objects.filter(previous_tree=root_child_tree_obj).exclude(
                current_tree=root_child_tree_obj).aggregate(Sum('count'))['count__sum']
            if previous_flow_click == None:
                previous_flow_click = 0
            flow_click = previous_flow_click + flow_analytics_objects_that_day.filter(
                previous_tree=root_child_tree_obj).exclude(
                current_tree=root_child_tree_obj).exclude(current_tree=intent_obj.tree).count()

            flow_abort = flow_termination_data_objs.filter(
                tree=root_child_tree_obj).count()

            flow_drop = flow_count - (flow_click + flow_abort)

            if flow_drop <= 0:
                return None, translate_api_status

            flow_drop_percent = int(
                round((flow_drop / count_intent_was_called) * 100))

            response["child_intent_name"] = str(root_child_tree_obj.name)
            response['child_intent_id'] = root_child_tree_obj.pk
            response["dropoffs"] = flow_drop
            response["main_intent_name"] = str(intent_obj.tree.name)
            response["id"] = intent_obj.pk
            response["dropoff_percentage"] = flow_drop_percent
            response["main_intent_multilingual_name"], translate_api_status = get_multilingual_intent_obj_name(
                intent_obj, selected_language, translate_api_status)
            if root_child_tree_obj == intent_obj.tree:
                response["child_intent_multilingual_name"] = response["main_intent_multilingual_name"]
            else:
                response["child_intent_multilingual_name"], translate_api_status = get_multilingual_tree_obj_name(
                    root_child_tree_obj, selected_language, translate_api_status)

        else:
            return None, translate_api_status

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Get Child Tree Objs", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        response["child_intent_name"] = str(root_child_tree_obj.name)
        response["dropoffs"] = 0
        response["main_intent_name"] = str(intent_obj.tree.name)
        response["id"] = intent_obj.pk
        response["dropoff_percentage"] = 0

    return response, translate_api_status


def get_child_tree_flow_analytics_data(json_resp, root_tree_pk, root_child_tree_obj, flow_analytics_objects,
                                       flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj,
                                       count_intent_was_called, parent_node, level, parent_node_actions,
                                       previous_node_actions):
    try:
        from EasyChatApp.models import Tree
        from django.db.models import Sum
        from django.db.models import Q

        flow_count = 0
        if level != 1:
            flow_analytics_objects_count = flow_analytics_objects.filter(previous_tree=Tree.objects.get(
                pk=root_tree_pk), current_tree=root_child_tree_obj).aggregate(Sum('count'))['count__sum']
            if flow_analytics_objects_count == None:
                flow_analytics_objects_count = 0

            # Checking if tree object has children.
            # If YES, along with forward flow , we will fetch rows from FlowAnalytics model where flow is coming back to previous intent (Go back button) .
            # Else we will just fetch rows of forward flow only.
            if(root_child_tree_obj.children.all()):
                flow_count = flow_analytics_objects_count + flow_analytics_objects_that_day.filter(
                    Q(previous_tree=Tree.objects.get(pk=root_tree_pk)) | Q(previous_tree=Tree.objects.get(pk=root_child_tree_obj.children.all()[0].pk)), current_tree=root_child_tree_obj).count()
            else:
                flow_count = flow_analytics_objects_count + flow_analytics_objects_that_day.filter(
                    previous_tree=Tree.objects.get(pk=root_tree_pk), current_tree=root_child_tree_obj).count()
        else:
            flow_count = count_intent_was_called
        json_resp["size"] = flow_count
        json_resp["percentage_of_parent"] = 0
        json_resp["rule"] = 0
        if parent_node_actions != 0:
            json_resp["percentage_of_parent"] = int(
                (flow_count / parent_node_actions) * 100)
        if parent_node:
            parent_node_actions = flow_count
        if previous_node_actions != 0:
            json_resp["rule"] = int(
                round((flow_count / previous_node_actions) * 100))

        flow_click = 0
        if flow_count != 0:
            previous_flow_click = flow_analytics_objects.filter(previous_tree=root_child_tree_obj).exclude(
                current_tree=root_child_tree_obj).aggregate(Sum('count'))['count__sum']
            if previous_flow_click == None:
                previous_flow_click = 0
            flow_click = previous_flow_click + flow_analytics_objects_that_day.filter(
                previous_tree=root_child_tree_obj).exclude(
                current_tree=root_child_tree_obj).exclude(current_tree=intent_obj.tree).count()
            flow_click_percent = int(round((flow_click / flow_count) * 100))

            flow_abort = flow_termination_data_objs.filter(
                tree=root_child_tree_obj).count()
            flow_abort_percent = int(round((flow_abort / flow_count) * 100))

            flow_drop = flow_count - (flow_click + flow_abort)
            flow_drop_percent = int(round((flow_drop / flow_count) * 100))
        else:
            flow_click_percent = 0
            flow_abort_percent = 0
            flow_drop_percent = 0

        json_resp["click_percent"] = flow_click_percent
        json_resp["abort_percent"] = flow_abort_percent
        json_resp["drop_percent"] = flow_drop_percent

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Get Child Tree Objs", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        json_resp["size"] = 0
        json_resp["click_percent"] = 0
        json_resp["abort_percent"] = 0
        json_resp["drop_percent"] = 0

    return json_resp, flow_count, parent_node_actions, flow_click


def create_user_nudge_analytics_excel(user_obj, bot_pk, channel_name, category_name, start_date, end_date,
                                      selected_language, supported_languages, email_id, to_be_mailed, export_request_obj=None):
    try:
        from EasyChatApp.models import Channel, Intent, AutoPopUpClickInfo, BotChannel, EasyChatTranslationCache, EasyChatAppFileAccessManagement, Bot, BotInfo, CustomIntentBubblesForWebpages
        from EasyChatApp.utils_bot import get_translated_text
        from datetime import timedelta
        from EasyChatApp.utils import send_mail_of_analytics

        bot_obj = Bot.objects.get(pk=bot_pk)
        auto_popup_intent_list = []
        bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
        if(bot_info_obj.custom_intents_for == AUTO_POPUP):
            custom_intent_objs = CustomIntentBubblesForWebpages.objects.filter(
                bot=bot_obj, custom_intents_for=AUTO_POPUP)
            for custom_intents in custom_intent_objs.iterator():
                for intents in custom_intents.custom_intent_bubble.all():
                    auto_popup_intent_list.append(intents.name)

        wb = Workbook()
        sheet1 = wb.add_sheet("User Nudge Analytics")
        sheet1.write(0, 0, "Date")
        sheet1.write(0, 1, "Greeting/Intent bubble name")
        sheet1.write(0, 2, "Click Count")
        sheet1.write(0, 3, "Active/Inactive")

        if selected_language != "all":
            sheet1.write(0, 4, "Language")
            language_text = list(
                supported_languages.values_list("name_in_english"))
            language_text = [lang[0] for lang in language_text]
            language_text = ", ".join(language_text)
            sheet1.col(4).width = 25 * 256

        sheet1.col(1).width = 40 * 256
        index = 1

        auto_popup_type = bot_obj.auto_popup_type
        is_auto_popup_desktop = bot_obj.is_auto_pop_allowed_desktop
        is_auto_popup_mobile = bot_obj.is_auto_pop_allowed_mobile
        auto_popup_enabled = (is_auto_popup_desktop or is_auto_popup_mobile)
        auto_popup_initial_messages = []
        if str(auto_popup_type) == "3":
            auto_popup_initial_messages = json.loads(
                bot_obj.auto_popup_initial_messages)

        temp_date = start_date

        if channel_name in ["Web", "All"]:

            bot_channel_obj = BotChannel.objects.filter(
                bot=bot_obj, channel=Channel.objects.filter(name="Web")[0])[0]
            languages_supported = bot_channel_obj.languages_supported.all().exclude(
                lang="en").values("lang")

            if str(auto_popup_type) == "3":
                for language_supported in languages_supported:
                    auto_popup_initial_messages += get_translated_text("$$$".join(json.loads(
                        bot_obj.auto_popup_initial_messages)), language_supported["lang"], EasyChatTranslationCache).split(
                        "$$$")

            while temp_date <= end_date:

                bubble_click_count_objs = AutoPopUpClickInfo.objects.filter(
                    bot=bot_obj, date=temp_date)
                if selected_language.lower() != "all":
                    bubble_click_count_objs = bubble_click_count_objs.filter(
                        selected_language__in=supported_languages)

                distinct_bubble_click_objs = bubble_click_count_objs.exclude(
                    name="Greeting bubble").values("name").distinct()

                other_lang_to_english_dict = {}
                initial_messages = json.loads(
                    bot_obj.auto_popup_initial_messages)
                for bubble_click_obj in distinct_bubble_click_objs:
                    if bubble_click_obj["name"].strip().replace(" ", "").isalpha():
                        other_lang_to_english_dict[bubble_click_obj["name"].strip(
                        )] = bubble_click_obj["name"].strip()
                        if bubble_click_obj["name"].strip() not in initial_messages:
                            initial_messages.append(
                                bubble_click_obj["name"].strip())

                if initial_messages != []:
                    for language_supported in languages_supported:
                        translated_initial_messages = get_translated_text("$$$".join(
                            initial_messages), language_supported["lang"], EasyChatTranslationCache).split("$$$")
                        for idx, translated_initial_message in enumerate(translated_initial_messages):
                            other_lang_to_english_dict[translated_initial_message.strip(
                            )] = initial_messages[idx]

                sheet1.write(index, 0, temp_date.strftime("%d-%m-%Y"))
                sheet1.write(index, 1, "Greeting bubble")
                sheet1.write(index, 2, str(
                    bubble_click_count_objs.filter(name="Greeting bubble").count()))
                if str(auto_popup_type) in ["2", "3"]:
                    sheet1.write(index, 3, "Active")
                if selected_language != "all":
                    sheet1.write(index, 4, language_text)
                index += 1

                if auto_popup_intent_list:
                    translated_intent = ''
                    for intent in auto_popup_intent_list:
                        translated_intent += '"' + intent + '", '

                    translated_intent = "[" + translated_intent[:-2] + "]"
                    for language_supported in languages_supported:
                        auto_popup_intent_list += get_translated_text("$$$".join(json.loads(
                            translated_intent)), language_supported["lang"], EasyChatTranslationCache).split("$$$")

                distinct_bubble_click_objs_list = []
                for distinct_bubble_click_obj in distinct_bubble_click_objs:
                    distinct_bubble_click_objs_list.append(distinct_bubble_click_obj["name"])
                    try:
                        if category_name != "All":
                            Intent.objects.get(bots__in=[bot_obj],
                                               name=other_lang_to_english_dict[distinct_bubble_click_obj["name"].strip(
                                               )], category__name=category_name.strip(),
                                               channels__in=Channel.objects.filter(name="Web"))
                        if(bot_info_obj.enable_custom_intent_bubbles == False or distinct_bubble_click_obj["name"] not in auto_popup_intent_list):
                            sheet1.write(
                                index, 0, temp_date.strftime("%d-%m-%Y"))
                            sheet1.write(
                                index, 1, distinct_bubble_click_obj["name"])
                            sheet1.write(index, 2, str(bubble_click_count_objs.filter(
                                name=distinct_bubble_click_obj["name"]).count()))
                            if distinct_bubble_click_obj["name"] in auto_popup_initial_messages and auto_popup_type == "3" and auto_popup_enabled:
                                sheet1.write(index, 3, "Active")
                            if selected_language != "all":
                                sheet1.write(index, 4, language_text)
                            index += 1
                    except:
                        continue

                for default_intents in auto_popup_initial_messages:
                    try:
                        if default_intents != "" and default_intents not in distinct_bubble_click_objs_list:
                            sheet1.write(
                                index, 0, temp_date.strftime("%d-%m-%Y"))
                            sheet1.write(
                                index, 1, default_intents)
                            sheet1.write(index, 2, str(bubble_click_count_objs.filter(
                                name=default_intents).count()))
                            if auto_popup_type == "3" and auto_popup_enabled:
                                sheet1.write(index, 3, "Active")
                            if selected_language != "all":
                                sheet1.write(index, 4, language_text)
                            index += 1
                    except:
                        continue

                for intents in auto_popup_intent_list:
                    try:
                        if intents not in auto_popup_initial_messages:
                            sheet1.write(index, 0, temp_date.strftime("%d-%m-%Y"))
                            sheet1.write(
                                index, 1, intents)
                            sheet1.write(index, 2, str(bubble_click_count_objs.filter(
                                name=intents).count()))
                            if bot_info_obj.enable_custom_intent_bubbles and auto_popup_type == "3" and auto_popup_enabled:
                                sheet1.write(index, 3, "Active")
                            if selected_language != "all":
                                sheet1.write(index, 4, language_text)
                            index += 1
                    except:
                        continue

                temp_date = temp_date + timedelta(1)

        secured_files_path = settings.SECURE_MEDIA_ROOT + \
            'EasyChatApp/custom_analytics/' + str(bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        filename = str(user_obj.username) + "_user_nudge_analytics.xls"

        wb.save(secured_files_path + filename)
        path = '/secured_files/EasyChatApp/custom_analytics/' + \
            str(bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            send_mail_of_analytics('User Nudge Analytics',
                                        file_url, email_id)
        else:
            return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_user_nudge_analytics_excel: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        file_url = ""

    return file_url


def get_dict_of_channel_wise_supported_languages(bot_channel_objs):
    final_dict = {}
    list_of_languages_across_all_channels = []
    try:
        for bot_channel in bot_channel_objs:
            supported_languages = bot_channel.languages_supported.all().values_list("lang",
                                                                                    "name_in_english")
            supported_languages = list(supported_languages)
            final_dict[bot_channel.channel.name] = supported_languages
            list_of_languages_across_all_channels.extend(supported_languages)
        list_of_languages_across_all_channels = set(
            list_of_languages_across_all_channels)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_user_nudge_analytics_excel: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return final_dict, list_of_languages_across_all_channels


def get_supported_languages_stringified_channel_wise(dict_of_channel_wise_languages):
    final_str = ""

    try:
        for index, channel_name in enumerate(dict_of_channel_wise_languages):

            channel_str = channel_name + "###"
            for idx, lang in enumerate(dict_of_channel_wise_languages[channel_name]):
                if idx == len(dict_of_channel_wise_languages[channel_name]) - 1:
                    channel_str = channel_str + lang[0] + "-" + lang[1]
                else:
                    channel_str = channel_str + lang[0] + "-" + lang[1] + ","

            if index == len(dict_of_channel_wise_languages) - 1:
                final_str = final_str + channel_str
            else:
                final_str = final_str + channel_str + "$$$"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_supported_languages_stringified_channel_wise: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return final_str


def get_supported_languages_list(selected_language, Language):
    try:
        supported_languages_list = []
        if selected_language.lower() != "all":
            supported_languages_list = selected_language.split(",")
            supported_languages_list = [
                lang.strip() for lang in supported_languages_list]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_supported_languages_list: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    supported_languages = Language.objects.filter(
        lang__in=supported_languages_list)
        
    return supported_languages    
    

def get_multilingual_intent_obj_name(intent_obj, selected_language, translate_api_status):
    try:
        from EasyChatApp.models import Language, LanguageTuningIntentTable, EasyChatTranslationCache
        from EasyChatApp.utils_bot import get_translated_text_with_api_status

        selected_language_obj = Language.objects.get(
            lang=selected_language)
        if intent_obj:
            intent_tunning_object = LanguageTuningIntentTable.objects.filter(
                intent=intent_obj, language=selected_language_obj).first()
            if intent_tunning_object:
                return intent_tunning_object.multilingual_name, True

        return get_translated_text_with_api_status(intent_obj.tree.name, selected_language, EasyChatTranslationCache,
                                                   translate_api_status)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_multilingual_intent_obj_name: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return intent_obj.tree.name, False


def get_multilingual_tree_obj_name(tree_obj, selected_language, translate_api_status):
    try:
        from EasyChatApp.models import Language, LanguageTuningTreeTable, EasyChatTranslationCache
        from EasyChatApp.utils_bot import get_translated_text_with_api_status

        selected_language_obj = Language.objects.get(
            lang=selected_language)
        if tree_obj:
            tree_tunning_object = LanguageTuningTreeTable.objects.filter(
                tree=tree_obj, language=selected_language_obj).first()
            if tree_tunning_object:
                return tree_tunning_object.multilingual_name, True

        return get_translated_text_with_api_status(tree_obj.name, selected_language, EasyChatTranslationCache,
                                                   translate_api_status)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_multilingual_tree_obj_name: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return tree_obj.name, False


def update_multilingual_name(dict_obj, selected_language, translate_api_status):
    from EasyChatApp.utils_bot import get_translated_text_with_api_status
    from EasyChatApp.models import EasyChatTranslationCache
    dict_obj["multilingual_name"], translate_api_status = get_translated_text_with_api_status(
        dict_obj["name"], selected_language, EasyChatTranslationCache, translate_api_status)
    for child_num in range(len(dict_obj["children"])):
        dict_obj["children"][child_num], translate_api_status = update_multilingual_name(
            dict_obj["children"][child_num], selected_language, translate_api_status)

    return dict_obj, translate_api_status


def process_speech_response_query(text):
    try:
        regex_cleaner = re.compile('<.*?>')
        cleaned_raw_str = re.sub(regex_cleaner, ' ', str(text))
        text = cleaned_raw_str.strip()
        text = re.sub(r'[^\x00-\x7f]', r' ', text)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("process_speech_response_query: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return text


def conversion_intent_analytics_translator(intent_completion_data, selected_language, translate_api_status, search_term=""):
    from EasyChatApp.models import Intent, EasyChatTranslationCache
    from EasyChatApp.utils_bot import get_translated_text_with_api_status
    searched_intent_completion_data = []
    try:
        for data in range(len(intent_completion_data)):
            intent_obj = Intent.objects.filter(
                pk=intent_completion_data[data]['intent_recognized']).first()
            if intent_obj:
                intent_completion_data[data]["multilingual_name"], translate_api_status = get_multilingual_intent_obj_name(
                    intent_obj, selected_language, translate_api_status)
            else:
                intent_completion_data[data]["multilingual_name"], translate_api_status = get_translated_text_with_api_status(
                    intent_completion_data[data]["intent_name"], selected_language, EasyChatTranslationCache, translate_api_status)
            if search_term:
                if selected_language != "en" and search_term.lower() not in intent_completion_data[data]["multilingual_name"].lower():
                    continue
                if selected_language == "en" and search_term.lower() not in intent_completion_data[data]["intent_name"].lower():
                    continue
            searched_intent_completion_data.append(intent_completion_data[data])
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("conversion_intent_analytics_translator: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return list(searched_intent_completion_data), translate_api_status


def welcome_analytics_translator(welcome_banner_clicked_data_count, selected_language, translate_api_status):
    from EasyChatApp.models import Intent
    try:
        for data in range(len(welcome_banner_clicked_data_count)):
            if welcome_banner_clicked_data_count[data]['intent__pk']:
                intent_obj = Intent.objects.filter(
                    pk=welcome_banner_clicked_data_count[data]['intent__pk']).first()
                if intent_obj:
                    welcome_banner_clicked_data_count[data]['multilingual_name'], translate_api_status = get_multilingual_intent_obj_name(
                        intent_obj, selected_language, translate_api_status)
            else:
                welcome_banner_clicked_data_count[data]['multilingual_name'] = "-"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("welcome_analytics_translator: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return intent_obj.tree.name, False

    return list(welcome_banner_clicked_data_count), translate_api_status


def get_total_days_based_on_filter_type(filter_type, today_flag, no_days, data_list=[]):
    try:
        total_days = 0
        if filter_type == "1":
            if today_flag:
                total_days = no_days + 1
            else:
                total_days = no_days
        elif filter_type == "2":
            total_days = len(data_list) * 7
        elif filter_type == "3":
            total_days = len(data_list) * 30      

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_total_days_based_on_filter_type: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        
    return total_days


def get_start_and_end_time(data):
    from datetime import datetime
    try:
        date_format = "%Y-%m-%d"
        start_date = data["start_date"]
        end_date = data["end_date"]
        datetime_start = datetime.strptime(
            start_date, date_format).date()
        datetime_end = datetime.strptime(end_date, date_format).date()  # noqa: F841
        if datetime_start > datetime_end:
            return datetime_start, datetime_end, "Start date can not be greater than End date!"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_start_and_end_time: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        datetime_start = (datetime.today() - timedelta(7)).date()
        datetime_end = datetime.today().date()

    return datetime_start, datetime_end, None
