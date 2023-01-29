#!/bin/bash

python /Cognoai/manage.py shell < /Cognoai/scripts/reset_database.py
python /Cognoai/manage.py makemigrations --noinput
python /Cognoai/manage.py migrate --noinput
cd /Cognoai/LiveChatApp/ && npm install && npm run build
python /Cognoai/manage.py collectstatic --noinput

NAME="EasyChat-App"                                  # Name of the application
DJANGODIR=/Cognoai/                                     # Django project directory
#SOCKFILE=/Cognoai/EasyChat/gunicorn.sock         # we will communicate using this unix socket
USER=root                                                 # the user to run as
GROUP=root                                             # the group to run as
NUM_WORKERS=4                   # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=EasyChat.settings        # which settings file should Django use
DJANGO_WSGI_MODULE=EasyChat.wsgi                     # WSGI module name

DJANGO_ASGI_MODULE=EasyChat.asgi

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)

exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=0.0.0.0:8002 \
  --log-level=debug \
  --log-file=- 

