from EasyChatApp.models import *
import datetime
import csv
import pathlib
import pandas as pd
import pytz
import os
from EasyChatApp.utils import logger


def create_directory():
    try:
        if not os.path.isdir(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/"):
            os.mkdir(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("User Dropoff directory creation create_directory! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def create_csv_file(filename, filepath):
    try:
        if not os.path.isdir(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" + filepath):
            os.mkdir(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" + filepath)

        file = pathlib.Path(settings.SECURE_MEDIA_ROOT +
                            "EasyChatApp/Botwise-flow-dropoff/" + filepath + filename)

        if not file.exists():
            headings = ["Date & Time", "User-ID", "Channel", "Parent Intent",
                        "Child Intent", "Drop-off type", "Intent Name/Flow Termination Keyword"]
            f = open(file, "w")
            csv.writer(f).writerow(headings)
            f.close()

        logger.info("User dropoff file created with name: " + str(filename), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("User Dropoff CSV creation create_csv_file! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_single_userdropoff_message_to_csv(filename, filepath, date_time, user_id, channel, parent_intent, current_intent, drop_off_type, intent_name):
    try:
        est = pytz.timezone(settings.TIME_ZONE)
        append_data = [str(date_time.astimezone(est).strftime(
            "%Y-%m-%d %H:%M:%S")), user_id, channel, parent_intent, current_intent, drop_off_type]

        if intent_name == "" or intent_name == None:
            append_data.append("-")
        else:
            append_data.append(intent_name)

        csv_file = open(settings.SECURE_MEDIA_ROOT +
                        "EasyChatApp/Botwise-flow-dropoff/" + filepath + filename, 'a')

        writer_obj = csv.writer(csv_file)

        writer_obj.writerow(append_data)

        csv_file.close()

        logger.info("User dropoff file updated with name: " + str(filename), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        pass
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("User Dropoff CSV file updation create_single_messgae_history_csv_file! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def cronjob():
    try:
        create_directory()
        yesterday_date = datetime.datetime.now().date() - datetime.timedelta(days=1)
        flow_analytics_objs = FlowAnalytics.objects.filter(
            created_time__date=yesterday_date).order_by("user__bot", "user", "pk")
        flow_termination_objs = FlowTerminationData.objects.filter(
            created_datetime__date=yesterday_date)
        flow_dropoff_objs = UserFlowDropOffAnalytics.objects.filter(
            created_datetime__date=yesterday_date)
        is_flow_completed = True

        filename = "User_dropoff_analytics_of_" + \
                str(yesterday_date) + ".csv"

        dropoff_type = ["Terminate", "Timeout", "Miscellaneous"]

        if flow_analytics_objs.exists():
            filepath = str(flow_analytics_objs.first().user.bot.name) + \
                "_" + str(flow_analytics_objs.first().user.bot.pk) + "/"
            create_csv_file(filename, filepath)

        # adding iterator in loop only because flow_analytics_objs is used in some if conditions where its count is bieng fetched which wont work if 
        # we use iterator in flow_analytics_objs during initialization hence using it while looping through the objects only
        for flow_analytics_obj in flow_analytics_objs.iterator():
            if not is_flow_completed and flow_analytics_obj.user.bot != prev_flow_obj.user.bot:
                if not prev_flow_obj.is_flow_aborted and prev_flow_obj.current_tree.children.all().count():
                    parent_tree_list = prev_flow_obj.current_tree.tree_set.all()
                    if parent_tree_list.count() == 0:
                        parent_tree = prev_flow_obj.current_tree
                    else:
                        parent_tree = parent_tree_list[0]
                    drop_off_type = "Timeout"
                    if prev_flow_obj.channel.name in ["Web", "Android", "iOS"]:
                        drop_off_type = "Miscellaneous"
                        UserFlowDropOffAnalytics.objects.create(created_datetime=prev_flow_obj.created_time, user=prev_flow_obj.user, previous_tree=parent_tree,
                                                                current_tree=prev_flow_obj.current_tree, intent_indentifed=prev_flow_obj.intent_indentifed, dropoff_type=3, channel=prev_flow_obj.channel, intent_name="-")
                    else:
                        UserFlowDropOffAnalytics.objects.create(created_datetime=prev_flow_obj.created_time, user=prev_flow_obj.user, previous_tree=parent_tree,
                                                                current_tree=prev_flow_obj.current_tree, intent_indentifed=prev_flow_obj.intent_indentifed, dropoff_type=2, channel=prev_flow_obj.channel, intent_name="-")

                    add_single_userdropoff_message_to_csv(filename, filepath, prev_flow_obj.created_time, prev_flow_obj.user.user_id,
                                                          prev_flow_obj.channel, parent_tree.name, prev_flow_obj.current_tree.name, drop_off_type, "-")

                prev_flow_obj = flow_analytics_obj
                filepath = str(prev_flow_obj.user.bot.name) + \
                    "_" + str(prev_flow_obj.user.bot.pk) + "/"
                create_csv_file(filename, filepath)
                continue

            if not is_flow_completed and flow_analytics_obj.user != prev_flow_obj.user:
                if not prev_flow_obj.is_flow_aborted and prev_flow_obj.current_tree.children.all().count():
                    parent_tree_list = prev_flow_obj.current_tree.tree_set.all()
                    if parent_tree_list.count() == 0:
                        parent_tree = prev_flow_obj.current_tree
                    else:
                        parent_tree = parent_tree_list[0]
                    drop_off_type = "Timeout"
                    if prev_flow_obj.channel.name in ["Web", "Android", "iOS"]:
                        drop_off_type = "Miscellaneous"
                        UserFlowDropOffAnalytics.objects.create(created_datetime=prev_flow_obj.created_time, user=prev_flow_obj.user, previous_tree=parent_tree,
                                                                current_tree=prev_flow_obj.current_tree, intent_indentifed=prev_flow_obj.intent_indentifed, dropoff_type=3, channel=prev_flow_obj.channel, intent_name="-")
                    else:
                        UserFlowDropOffAnalytics.objects.create(created_datetime=prev_flow_obj.created_time, user=prev_flow_obj.user, previous_tree=parent_tree,
                                                                current_tree=prev_flow_obj.current_tree, intent_indentifed=prev_flow_obj.intent_indentifed, dropoff_type=2, channel=prev_flow_obj.channel, intent_name="-")

                    add_single_userdropoff_message_to_csv(filename, filepath, prev_flow_obj.created_time, prev_flow_obj.user.user_id,
                                                          prev_flow_obj.channel, parent_tree.name, prev_flow_obj.current_tree.name, drop_off_type, "-")
                prev_flow_obj = flow_analytics_obj
                continue

            if not is_flow_completed and not prev_flow_obj.current_tree.children.all().count():
                is_flow_completed = True

            if not is_flow_completed and (prev_flow_obj.intent_indentifed != flow_analytics_obj.intent_indentifed and prev_flow_obj.current_tree != flow_analytics_obj.current_tree):
                if not prev_flow_obj.is_flow_aborted:
                    parent_tree_list = prev_flow_obj.current_tree.tree_set.all()
                    if parent_tree_list.count() == 0:
                        parent_tree = prev_flow_obj.current_tree
                    else:
                        parent_tree = parent_tree_list[0]
                    drop_off_type = "Timeout"
                    if prev_flow_obj.channel.name in ["Web", "Android", "iOS"]:
                        drop_off_type = "Miscellaneous"
                        UserFlowDropOffAnalytics.objects.create(created_datetime=prev_flow_obj.created_time, user=prev_flow_obj.user, previous_tree=parent_tree, current_tree=prev_flow_obj.current_tree,
                                                                intent_indentifed=prev_flow_obj.intent_indentifed, dropoff_type=3, channel=prev_flow_obj.channel, intent_name="-")
                    else:
                        UserFlowDropOffAnalytics.objects.create(created_datetime=prev_flow_obj.created_time, user=prev_flow_obj.user, previous_tree=parent_tree, current_tree=prev_flow_obj.current_tree,
                                                                intent_indentifed=prev_flow_obj.intent_indentifed, dropoff_type=2, channel=prev_flow_obj.channel, intent_name="-")
                    add_single_userdropoff_message_to_csv(filename, filepath, prev_flow_obj.created_time, prev_flow_obj.user.user_id,
                                                          prev_flow_obj.channel, parent_tree.name, prev_flow_obj.current_tree.name, drop_off_type, "-")

            if is_flow_completed:
                is_flow_completed = False

            prev_flow_obj = flow_analytics_obj

        if flow_analytics_objs.count() and flow_analytics_objs.last().current_tree.children.all().count():
            last_flow_analytics_obj = flow_analytics_objs.last()
            if not last_flow_analytics_obj.is_flow_aborted:
                parent_tree_list = last_flow_analytics_obj.current_tree.tree_set.all()
                if parent_tree_list.count() == 0:
                    parent_tree = last_flow_analytics_obj.current_tree
                else:
                    parent_tree = parent_tree_list[0]

                drop_off_type = "Timeout"
                if last_flow_analytics_obj.channel.name in ["Web", "Android", "iOS"]:
                    drop_off_type = "Miscellaneous"
                    UserFlowDropOffAnalytics.objects.create(created_datetime=last_flow_analytics_obj.created_time, user=last_flow_analytics_obj.user, previous_tree=parent_tree,
                                                            current_tree=last_flow_analytics_obj.current_tree, intent_indentifed=last_flow_analytics_obj.intent_indentifed, dropoff_type=3, channel=last_flow_analytics_obj.channel, intent_name="-")
                else:
                    UserFlowDropOffAnalytics.objects.create(created_datetime=last_flow_analytics_obj.created_time, user=last_flow_analytics_obj.user, previous_tree=parent_tree,
                                                            current_tree=last_flow_analytics_obj.current_tree, intent_indentifed=last_flow_analytics_obj.intent_indentifed, dropoff_type=2, channel=last_flow_analytics_obj.channel, intent_name="-")

                add_single_userdropoff_message_to_csv(filename, filepath, last_flow_analytics_obj.created_time, last_flow_analytics_obj.user.user_id,
                                                      last_flow_analytics_obj.channel, parent_tree.name, last_flow_analytics_obj.current_tree.name, drop_off_type, "-")

        for flow_dropoff_obj in flow_dropoff_objs.iterator():
            filepath = str(flow_dropoff_obj.user.bot.name) + "_" + str(flow_dropoff_obj.user.bot.pk) + "/"
            add_single_userdropoff_message_to_csv(filename, filepath, flow_dropoff_obj.created_datetime, flow_dropoff_obj.user.user_id, flow_dropoff_obj.channel.name, flow_dropoff_obj.previous_tree.name, flow_dropoff_obj.current_tree.name, dropoff_type[int(flow_dropoff_obj.dropoff_type) - 1], str(flow_dropoff_obj.intent_name))

        for flow_termination_obj in flow_termination_objs.iterator():
            parent_tree_list = flow_termination_obj.tree.tree_set.all()
            if parent_tree_list.count() == 0:
                parent_tree = flow_termination_obj.tree
            else:
                parent_tree = parent_tree_list[0]
            if flow_termination_obj.user != None:
                filepath = str(flow_termination_obj.user.bot.name) + \
                    "_" + str(flow_termination_obj.user.bot.pk) + "/"
                add_single_userdropoff_message_to_csv(filename, filepath, flow_termination_obj.created_datetime, flow_termination_obj.user.user_id,
                                                      flow_termination_obj.channel, parent_tree.name, flow_termination_obj.tree.name, "Terminate", flow_termination_obj.termination_message)
        if filename in vars() and filepath in vars(): 
            df = pd.read_csv(settings.SECURE_MEDIA_ROOT +
                                "EasyChatApp/Botwise-flow-dropoff/" + filepath + filename)
            df.sort_values([df.columns[1], df.columns[0]],
                            axis=0,
                            ascending=[True, True],
                            inplace=True)
            df.to_csv(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" +
                        filepath + filename, index=False)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("User Specific Dropoff analytics CSV cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
