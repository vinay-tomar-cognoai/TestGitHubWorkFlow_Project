from TestingApp.models import BotQATestCaseFlow
from TestingApp.utils import execute_testcase_flow, logger, APP_NAME

import time

for qa_testcase_flow_obj in BotQATestCaseFlow.objects.filter(is_flow_tested=False):
    logger.info("Task execution started", extra={'AppName': APP_NAME})
    exe_start_time = time.time()
    execute_testcase_flow(qa_testcase_flow_obj)
    exe_end_time = time.time()
    total_execution_time = str(exe_end_time - exe_start_time)
    qa_testcase_flow_obj.total_execution_time = total_execution_time
    qa_testcase_flow_obj.save()
    logger.info("Task execution ended %s secs",
                total_execution_time, extra={'AppName': APP_NAME})
    break
