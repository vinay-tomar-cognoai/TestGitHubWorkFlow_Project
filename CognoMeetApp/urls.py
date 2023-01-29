from django.conf.urls import url
from CognoMeetApp import views
from CognoMeetApp import views_analytics as va


urlpatterns = [
    url(r'^create-access-token/$', views.CreateAccessToken),
    url(r'^update-access-token-config/$', views.UpdateAccessTokenConfig),

    # Session related APIs
    url(r'^generate-meeting/$', views.GenerateCognoMeetMeeting),
    url(r'^meeting/(?P<session_id>[a-zA-Z0-9-_]+)$', views.ScheduleMeet),
    url(r'^meeting/client/(?P<session_id>[a-zA-Z0-9-_]+)$',
        views.ScheduleMeetClient),
    url(r'^authenticate-meeting-password/$',
        views.CognoMeetAuthenticatePassword),
    url(r'^add-participant/$', views.CognoMeetCreateParticipant),
    url(r'^upload-meeting-file-attachment/$',
        views.UploadCognoMeetFileAttachment),
    url(r'^download-file/(?P<file_key>[a-zA-Z0-9-_]+)/$', views.FileAccess),
    url(r'^save-meeting-notes/$', views.CognoMeetMeetingNotes),
    url(r'^save-meeting-screenshot/$', views.SaveCognoMeetAppScreenshot),
    url(r'^save-meeting-chats/$', views.SaveCognoMeetChat),
    url(r'^get-chat-for-session/$', views.CognoMeetGetChatForSession),
    url(r'^meeting-end/$', views.MeetingEnd),
    url(r'^update-feedback/$', views.UpdateFeedback),
    url(r'^check-participant-limit/$', views.CheckParticipantLimit),
    url(r'^update-agent-status/$', views.UpdateAgentSessionStatus),
    url(r'^update-customer-status/$', views.UpdateCustomerSessionStatus),
    url(r'^download-meeting-recording/$', views.DownloadSessionRecording),

    # CognoMeet Analytics APIs
    url(r'^get-basic-analytics/$', va.GetBasicAnalytics),
    url(r'^get-timeline-based-analytics/$', va.GetTimelineBasedAnalytics),
    url(r'^get-daily-call-time-trend-analytics/$', va.GetDailyCallTimeTrend),
    url(r'^get-agent-wise-analytics/$', va.GetAgentWiseAnalytics),
    url(r'^export-meeting-analytics/$', va.ExportMeetingAnalytics),

    # url(r'^request-agent-meeting/$', views.RequestJoinMeeting),
    # request-agent-meeting/

    url(r'^get-audit-trail-data/$', views.CognoMeetAuditTrailStats),
    url(r'^map-script/$', views.LoadMapScript),
    url(r'^save-client-location-details/$', views.SaveClientLocationDetails),
    url(r'^close-meeting/$', views.EndCognoMeetMeeting),
    url(r'^stats/export-meeting-support-history/$',
        views.ExportMeetingSupportHistory),
    url(r'^get-meeting-view-data/$', views.CognoMeetMeetingViewData),
    url(r'^update-cogno-meet/$', views.UpdateCognoMeet),
    url(r'^assign-cogno-meet-agent/$', views.AssignCognoMeetAgent),
    url(r'^invite-over-email/$', views.InviteCognoMeetOverEmail),
    url(r'^set-invited-agent/$', views.SetInvitedAgentForMeeting),
    url(r'^support-agent-joined/$', views.CognoMeetSupportAgentJoined),
    url(r'^check-meeting-ended-or-not/', views.CheckMeetingEndedOrNot),
    url(r'^create-or-update-cognomeet-agent', views.CreateOrUpdateCognoMeetAgent),
    

    # url(r'^get-all-support-request/$', views.GetAllCognoMeetSupportRequest),
]
