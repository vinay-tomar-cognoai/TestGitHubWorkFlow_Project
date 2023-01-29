from os import path
from os.path import basename
from datetime import datetime, timedelta
import sys
import os
from django.conf import settings
from django.core import serializers
import json

from EasyChatApp.models import MISDashboard, UserSessionHealth
from EasyChatApp.utils_analytics import return_mis_objects_excluding_blocked_sessions

if not os.path.exists(settings.MEDIA_ROOT + 'mis_dump'):
    os.makedirs(settings.MEDIA_ROOT + 'mis_dump')

last_date = MISDashboard.objects.last().date
today = datetime.now()
mis_objects = return_mis_objects_excluding_blocked_sessions(MISDashboard.objects, UserSessionHealth)
while(last_date.date() < today.date()):
    serialized_data = serializers.serialize(
        'json', mis_objects.filter(date__date=last_date.date()))
    new_arr = []
    # comment the 3 lines below if
    # you are migrating into a completely new database.
    # where for item in json.loads(serialized_data):
    # item['pk'] = None
    # new_arr.append(item)
    for item in json.loads(serialized_data):
        item['pk'] = None
        new_arr.append(item)
    filename = settings.MEDIA_ROOT + "mis_dump/serialize_data" + \
        str(last_date.date()) + ".json"
    with open(filename, 'w') as f:
        json.dump(new_arr, f)
    last_date = last_date + timedelta(1)

print("done")
