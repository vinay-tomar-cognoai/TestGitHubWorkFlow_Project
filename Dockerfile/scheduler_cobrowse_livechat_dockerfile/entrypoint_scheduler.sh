#!/bin/bash

#NAME="EasyChat-App"                                  # Name of the application
DJANGODIR=/Cognoai/EasyAssistApp/                                   # Django project directory
#SOCKFILE=/Cognoai/EasyChat/gunicorn.sock         # we will communicate using this unix socket
USER=root                                                 # the user to run as
GROUP=root                                             # the group to run as
#NUM_WORKERS=4                   # how many worker processes should Gunicorn spawn
#DJANGO_SETTINGS_MODULE=EasyChat.settings        # which settings file should Django use
#DJANGO_WSGI_MODULE=EasyChat.wsgi                     # WSGI module name


#export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export $PYTHONPATH

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)

exec python /Cognoai/EasyAssistApp/start_scheduler.py &
exec python /Cognoai/LiveChatApp/start_scheduler.py
