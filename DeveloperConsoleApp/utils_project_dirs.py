from DeveloperConsoleApp.constants import *

import sys
import json
import operator
import logging
import re
import ast
import random
import array
import datetime
import pytz
import threading
import os

logger = logging.getLogger(__name__)


def create_project_directories():
    try:
        for folder_path in DYNAMIC_FOLDER_LIST:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_project_directories %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})


create_project_directories()
