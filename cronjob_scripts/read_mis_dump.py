from os import path
from os.path import basename
from datetime import datetime, timedelta
import sys
import os
from django.conf import settings
from django.core import serializers
import json
import pathlib

from EasyChatApp.models import MISDashboard

for path in pathlib.Path(settings.MEDIA_ROOT + "mis_dump").iterdir():
    current_file = open(path, "r")
    for deserialized_object in serializers.deserialize("json", current_file.read()):
        deserialized_object.save()
