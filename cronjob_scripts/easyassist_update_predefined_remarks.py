from EasyAssistApp.models import *
import logging
import sys
import json

logger = logging.getLogger(__name__)

# Update Assigntask processor
try:
    access_token_objs = CobrowseAccessToken.objects.all()
    for access_token_obj in access_token_objs:
        access_token_obj.predefined_remarks = json.dumps([])
        access_token_obj.enable_predefined_remarks = False
        access_token_obj.enable_predefined_subremarks = False

        access_token_obj.save()

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    logger.error("Error easyassist_update_predefined_remarks %s at %s",
                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
