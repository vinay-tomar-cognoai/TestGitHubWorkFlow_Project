#!/bin/bash

python /Cognoai/manage.py crontab remove && python /Cognoai/manage.py crontab add
cron
