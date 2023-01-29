#!/bin/bash

#NAME="EasyChat-App-daphne"                                  # Name of the application
DJANGODIR=/Cognoai/EasyChat/                                     # Django project directory
#SOCKFILE=/Cognoai/EasyChat/gunicorn.sock         # we will communicate using this unix socket
#USER=root                                                 # the user to run as
#GROUP=root                                             # the group to run as
#NUM_WORKERS=4                   # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=EasyChat.settings        # which settings file should Django use
DJANGO_ASGI_MODULE=EasyChat.asgi                     # WSGI module name


export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)

exec daphne -b 0.0.0.0 \
  -p 8010 \
  ${DJANGO_ASGI_MODULE}:application
