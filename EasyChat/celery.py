from __future__ import absolute_import, unicode_literals

import os

# from celery import Celery
# from kombu import Exchange, Queue

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyChat.settings')

# app = Celery('EasyChat')
# celeryconfig = {}
# celeryconfig['BROKER_URL'] = 'amqp://localhost'
# # celeryconfig['CELERY_RESULT_BACKEND'] = 'redis://localhost'
# celeryconfig['CELERY_ACCEPT_CONTENT'] = ['pickle']
# celeryconfig['CELERY_TASK_SERIALIZER'] = 'pickle'
# celeryconfig['CELERY_RESULT_SERIALIZER'] = 'pickle'
# celeryconfig['CELERY_QUEUES'] = (
#     Queue('tasks', Exchange('tasks'), routing_key='tasks',
#           queue_arguments={'x-max-priority': 5}),
# )
# celeryconfig['CELERY_ACKS_LATE'] = True
# celeryconfig['CELERYD_PREFETCH_MULTIPLIER'] = 1

# app.config_from_object(celeryconfig)

# app.autodiscover_tasks()
