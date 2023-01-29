from django.contrib import admin
from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^home/$', views.AutomationHome),
    url(r'^logout/$', views.AutomationLogout),
    # url(r'^login/$', views.AutomationLogin),
    url(r'^automation-api/$', views.AutomationAPI),
    url(r'^test/automation-api/$', views.TestAutomationQuery),
    url(r'^create-new/$', views.CreateNewAutomationBot),
    url(r'^edit-bot-details/(?P<pk>\d+)/$', views.EditAutomationBot),
    url(r'^test/(?P<pk>\d+)/$', views.TestingBotConsole),
    url(r'^testcase/(?P<pk>\d+)/$', views.TestCasePreview),
    url(r'^testcase/results/(?P<pk>\d+)/$', views.TestCaseResults),
    url(r'^testcase/delete/(?P<pk>\d+)/$', views.DeleteTestCase),
    url(r'^testcase/reset/(?P<pk>\d+)/$', views.ResetTestCase),
    url(r'^testcase/reset-all/(?P<pk>\d+)/$', views.ResetAllTestCase),
    url(r'^get-testcase-flow-output/$', views.GetTestCaseFlowOutput),
    url(r'^delete-bot-details/(?P<pk>\d+)/$', views.DeleteAutomationBot),
    url(r'^upload-qa-testcase-excel/$', views.UploadQATestcaseExcel),
    url(r'^validate-qa-testcase-excel/$', views.ValidateQATestcaseExcel),
]
