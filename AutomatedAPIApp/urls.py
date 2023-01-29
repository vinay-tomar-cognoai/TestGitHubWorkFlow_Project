from django.contrib import admin
from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^build-old/$', views.AutomatedAPIIntegrationConsoleOld),
    url(r'^build/$', views.AutomatedAPIIntegrationConsole),
    url(r'^tag-api-tree/$', views.TagAPIWithTree),
    url(r'^generate-automated-code/$', views.GenerateAutomatedAPICode),
    url(r'^save-code-into-api-tree/$', views.SaveCodeIntoApiTree),
    url(r'^test/execute-api/$', views.AutomatedAPITest),
    url(r'^test/fetch-parent-tree-variables/$',
        views.GetParentTreePostProcessorVariableNames),
    url(r'^test/get-account-balance/$', views.TestGetAccountBalance),
]
