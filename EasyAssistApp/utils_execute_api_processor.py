import logging
import sys
import func_timeout

from EasyAssistApp.utils import *

logger = logging.getLogger(__name__)


def open_file(file_dir, method):
    try:
        file_dir = settings.SECURE_MEDIA_ROOT + file_dir

        if '..' in file_dir:
            logger.info("User is trying to access this file: %s", str(file_dir), extra={'AppName': 'EasyAssist'})
            return

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("open_file: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    return open(file_dir, method)


def execute_processor_python_code(code_to_execute, parameter):
    json_data = None
    result_dict = {'open': open_file}
    exec(str(code_to_execute), result_dict)
    json_data = result_dict['foo'](parameter)
    return json_data


def execute_code_with_time_limit(code_to_execute, parameter):
    json_data = {}
    try:
        json_data = func_timeout.func_timeout(
            EASYASSIST_MAX_API_RUNTIME_LIMIT, execute_code, args=[code_to_execute, parameter])

    except func_timeout.FunctionTimedOut:
        logger.error("Error execute_code_with_time_limit ", extra={'AppName': 'EasyAssist'})

    return json_data


def execute_code(code_to_execute, parameter):
    json_data = None
    try:
        result_dict = {'open': open_file}
        exec(str(code_to_execute), result_dict)
        json_data = result_dict['foo'](parameter)
        return json_data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In execute_code: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})
        return json_data
