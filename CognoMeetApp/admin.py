from django.contrib import admin
from CognoMeetApp.models import *


class CognoMeetAgentAdmin(admin.ModelAdmin):
    ordering = ('-agent_creation_datetime', )


admin.site.register(CognoMeetAgent, CognoMeetAgentAdmin)
admin.site.register(CognoMeetAccessToken)
admin.site.register(CognoMeetConfig)


class CognoMeetIOAdmin(admin.ModelAdmin):
    ordering = ('-meeting_request_creation_datetime',)


admin.site.register(CognoMeetIO, CognoMeetIOAdmin)
admin.site.register(CognoMeetRecording)
admin.site.register(CognoMeetAuditTrail)


class CognoMeetChatHistoryAdmin(admin.ModelAdmin):
    ordering = ('-datetime',)


admin.site.register(CognoMeetChatHistory, CognoMeetChatHistoryAdmin)
admin.site.register(CognoMeetFileAccessManagement)
admin.site.register(AuthTokenDetail)
admin.site.register(CognoMeetInvitedAgentsDetails)
admin.site.register(CognoMeetTimers)
admin.site.register(CognoMeetCronjobTracker)
admin.site.register(MeetingActualStartEndTime)
admin.site.register(CognoMeetExportDataRequest)
