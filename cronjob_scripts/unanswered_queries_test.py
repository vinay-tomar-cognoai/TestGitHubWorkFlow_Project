from EasyChatApp.models import *
from cronjob_scripts.analytics_cronjob import *

for items in MISDashboard.objects.all():
    items.status = "2"
    items.save()


unanswered_queries_cronjob()
