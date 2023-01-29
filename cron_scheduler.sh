#!/bin/bash

while [ 1 ]
do
	. ../venv/bin/activate && python manage.py shell < scripts/cognoai_cron_monitor.py
	sleep 60s
done
