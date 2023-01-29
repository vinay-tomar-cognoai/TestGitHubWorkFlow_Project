from django.conf.urls import url
from . import views

urlpatterns = [
    # General ChatBot
    url(r'^settings/$', views.DeveloperSettings),
    url(r'^whitelabel/chatbot/$', views.WhitelableChatbotPage),
    url(r'^whitelabel/general/$', views.WhitelableGeneralPage),
    url(r'^whitelabel/cobrowse/$', views.WhitelableCobrowsePage),
    url(r'^whitelabel/livechat/$', views.WhitelableLiveChatPage),
    url(r'^whitelabel/desk/$', views.WhitelableCognoDeskPage),
    url(r'^whitelabel/meet/$', views.WhitelableCognoMeetPage),
    url(r'^whitelabel/save-general-whitelabel-settings/$',
        views.SaveGeneralWhitelabelSettings),
    url(r'^whitelabel/save-easychatapp-whitelabel-settings/$', views.SaveEasyChatAppWhiteLabelSettings),
    url(r'^whitelabel/save-cognodeskapp-whitelabel-settings/$', views.SaveCognoDeskAppWhiteLabelSettings),
    url(r'^whitelabel/save-livechat-whitelabel-settings/$',
        views.SaveLiveChatWhitelabelSettings),
    url(r'^whitelabel/reset-livechat-whitelabel-settings/$',
        views.ResetLiveChatWhitelabelSettings),
    url(r'^whitelabel/save-cobrowsing-whitelabel-settings/$',
        views.SaveCobrowsingWhitelabelSettings),
    url(r'^whitelabel/reset-cobrowse-whitelabel-settings/$',
        views.ResetCobrowseWhitelabelSettings),
    url(r'^whitelabel/save-cognomeet-whitelabel-settings/$',
        views.SaveCognoMeetWhitelabelSettings),
    url(r'^whitelabel/reset-cognomeet-whitelabel-settings/$',
        views.ResetCognoMeetWhitelabelSettings),
]
