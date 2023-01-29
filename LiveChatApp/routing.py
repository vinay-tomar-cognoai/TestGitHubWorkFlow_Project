from django.conf.urls import url

from . import consumers
from EasyAssistApp import consumers as easyassist_consumers
from EasyTMSApp import consumers as tms_consumers

websocket_urlpatterns = [
    url(r'^ws/(?P<session_id>[a-zA-Z0-9-_]+)/(?P<sender>\w+)/$',
        consumers.ChatConsumer.as_asgi()),

    url(r'^ws/cobrowse/(?P<room_name>[a-zA-Z0-9-_]+)/(?P<sender>\w+)/$',
        easyassist_consumers.CobrowsingConsumer.as_asgi()),

    url(r'^ws/meet/(?P<room_name>[a-zA-Z0-9-_]+)/(?P<sender>\w+)/$',
        easyassist_consumers.CobrowsingMeeting.as_asgi()),

    url(r'^ws/cognoai-signal/(?P<app_token>[a-zA-Z0-9-_]+)/(?P<sender>\w+)/$',
        easyassist_consumers.CognoAIsignal.as_asgi()),

    url(r'^ws/cobrowse/sync-utils/(?P<room_name>[a-zA-Z0-9-_]+)/(?P<sender>\w+)/$',
        easyassist_consumers.SyncUtilsCobrowsingConsumer.as_asgi()),

    url(r'^ws/tms-signal/(?P<app_token>[a-zA-Z0-9-_]+)/(?P<sender>\w+)/$',
        tms_consumers.TMSSignal.as_asgi()),
]
