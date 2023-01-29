from EasyAssistApp.models import *


def update_archive_on_unassigned_time_threshold():
    try:
        for access_token in CobrowseAccessToken.objects.all():
            access_token.archive_on_unassigned_time_threshold = 10
            access_token.save()

    except Exception as e:
        logger.error("Error in update_archive_on_unassigned_time_threshold: %s", str(e), extra={'AppName': 'EasyAssist'})


print("Running update_archive_on_unassigned_time_threshold...\n")

update_archive_on_unassigned_time_threshold()
