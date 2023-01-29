from django.contrib import admin
from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.homePage),
    url(r'^logout/$', views.logoutAPI, name="logout-api"),
    url(r'^dashboard/$', views.dashboard),
    url(r'^get-audit-trail/$', views.GetAuditTrail),
    url(r'^export-audit-trail/$', views.ExportAuditTrail),
    url(r'^download-file/(?P<file_key>[a-zA-Z0-9-_]+)/$', views.fileAccess),
    url(r'^unauthorised/$', views.unauthorisedPage),
]
