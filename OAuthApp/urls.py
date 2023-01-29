from django.conf.urls import url
from OAuthApp import views

urlpatterns = [
    # General ChatBot
    url(r'^v1/$', views.ClientConsoleOAuth, name="client-console-auth"),
    url(r'^authorization/$', views.oauth_validation, name="oauth-authorization"),
    url(r'^remove-access/$', views.RemoveAccess),
    url(r'^get-models-name/$', views.GetModelNamesAPI),
    url(r'^model-access/$', views.ModelAccess)
]
