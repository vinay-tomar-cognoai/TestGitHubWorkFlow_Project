from django.contrib import admin

from DeveloperConsoleApp.models import *

admin.site.register(DeveloperConsoleConfig)

admin.site.register(LiveChatAppConfig)


class CentralisedFileAccessManagementAdmin(admin.ModelAdmin):

    list_per_page = 100
    list_display = ('key', 'file_path', )

admin.site.register(CentralisedFileAccessManagement, CentralisedFileAccessManagementAdmin)
admin.site.register(EasyChatAppConfig)
admin.site.register(CognoDeskAppConfig)

admin.site.register(CobrowsingAppConfig)
admin.site.register(CognoMeetAppConfig)
