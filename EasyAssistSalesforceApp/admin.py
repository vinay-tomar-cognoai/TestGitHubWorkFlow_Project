from django.contrib import admin

from EasyAssistSalesforceApp.models import *
# Register your models here.


class SalesforceAgentAdmin(admin.ModelAdmin):

    list_display = ('email', 'user_id', 'web_tab_name')

admin.site.register(SalesforceAgent, SalesforceAgentAdmin)


class SalesforceNotificationManagerAdmin(admin.ModelAdmin):

    list_display = ('username', 'access_token')

admin.site.register(SalesforceNotificationManager, SalesforceNotificationManagerAdmin)
