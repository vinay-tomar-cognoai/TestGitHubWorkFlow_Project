from EasyChatApp.models import *
from EasyChatApp.utils import *
from django.db.models import Sum
import datetime
from EasyChatApp.utils import logger
import sys
import os


def cronjob():
    intents_objects_list = Intent.objects.filter(is_deleted=False)

    today_date = (datetime.datetime.now()).date()
    start_date = today_date - datetime.timedelta(1)
    try:
        while start_date != today_date:
            for intent in intents_objects_list.iterator():
                for channel in Channel.objects.filter(is_easychat_channel=True).iterator():
                    flow_analytics_objects = FlowAnalytics.objects.filter(
                        intent_indentifed=intent, created_time__date=start_date, channel=channel)
                    if flow_analytics_objects:
                        total_sum = flow_analytics_objects.filter(current_tree=intent.tree).aggregate(
                            Sum('flow_analytics_variable'))['flow_analytics_variable__sum']
                        if total_sum == None:
                            total_sum = 0

                        abort_count = FlowTerminationData.objects.filter(intent=intent, tree=intent.tree, created_datetime__date=start_date, channel=channel).count()

                        DailyFlowAnalytics.objects.create(intent_indentifed=intent, previous_tree=intent.tree, current_tree=intent.tree, count=flow_analytics_objects.filter(current_tree=intent.tree).count(), total_sum=total_sum, channel=channel, abort_count=abort_count, created_time=start_date)

                        list_child_parent_pair = get_parent_child_pair(
                            intent.tree, [], [])
                        for item in list_child_parent_pair:
                            if flow_analytics_objects.filter(previous_tree=item[0], current_tree=item[1]):
                                total_transaction = flow_analytics_objects.filter(
                                    previous_tree=item[0], current_tree=item[1]).aggregate(Sum('flow_analytics_variable'))
                                if total_transaction == None:
                                    total_transaction = 0
                                count = flow_analytics_objects.filter(
                                    previous_tree=item[0], current_tree=item[1]).count()
                                total_transaction = total_transaction
                                is_last_tree_child = flow_analytics_objects.filter(
                                    previous_tree=item[0], current_tree=item[1])[0].is_last_tree_child
                                if total_transaction == None:
                                    total_sum = 0
                                else:
                                    total_sum = total_transaction[
                                        'flow_analytics_variable__sum']

                                abort_count = FlowTerminationData.objects.filter(intent=intent, tree=item[1], created_datetime__date=start_date, channel=channel).count()

                                DailyFlowAnalytics.objects.create(intent_indentifed=intent, previous_tree=item[0], current_tree=item[1], count=count, total_sum=total_sum, channel=channel, is_last_tree_child=is_last_tree_child, abort_count=abort_count, created_time=start_date)

                        flow_analytics_objects.delete()

            start_date = start_date + datetime.timedelta(1)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Flow Analytics Daily! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        pass
