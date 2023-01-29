def cronjob():
    from cronjob_scripts.cognoai_cronjob_utils import create_cronjob_start_log, create_cronjob_end_log, send_cron_error_report
    from CognoMeetApp.utils import logger
    from datetime import datetime
    import sys

    curr_file_name = "cognomeet_combined_cronjob"
    log_obj_id = create_cronjob_start_log(curr_file_name)

    cron_error_list = []
    try:
        from cronjob_scripts.cognomeet_export_analytics_cronjob import cronjob
        cronjob()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])

    try:
        from cronjob_scripts.cognomeet_export_support_history_cronjob import cronjob
        cronjob()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])

    send_cron_error_report(cron_error_list, "cronjob", curr_file_name)

    create_cronjob_end_log(log_obj_id)
