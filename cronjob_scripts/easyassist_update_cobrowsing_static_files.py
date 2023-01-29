from EasyAssistApp.models import *
import logging
import sys

logger = logging.getLogger(__name__)

# Update Assigntask processor
try:
    assign_task_processor_objs = AssignTaskProcessor.objects.all()
    for assign_task_processor in assign_task_processor_objs:
        assign_task_processor.function = ASSIGN_TAKS_PROCESSOR_CODE
        assign_task_processor.save()

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    logger.error("Error update_assign_task_processor %s at %s",
                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


# Update Cobrowsing static files
try:
    access_token_objs = CobrowseAccessToken.objects.all()
    for access_token_obj in access_token_objs:
        access_token_obj.advanced_setting_static_file_action = "reset"
        access_token_obj.save()

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    logger.error("Error update_cobrowsing_static_files %s at %s",
                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
