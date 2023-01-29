from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from EasyAssistSalesforceApp.assign_task import assign_task


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(assign_task, 'interval', seconds=5)
    scheduler.start()
