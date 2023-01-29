# from django.urls import path, re_path
from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin

from CampaignApp import views
from CampaignApp import views_lambda

urlpatterns = [
    url(r'^logout/$', views.LogoutAPI, name="logout-api"),

    url(r'unauthorised/$', views.UnauthorisedPage),

    url(r'voice-bot/review/$', views.VoiceBotReviewPage),
    url(r'voice-bot/send/$', views.SendVoiceBotCampaign),

    url(r'dashboard/$', views.CampaignHomePage, name="campaign-home-page"),
    url(r'get-active-campaign/$', views.GetActiveCampaigns),
    url(r'delete-campaigns/$', views.DeleteCampaigns),
    url(r'create-campaign/$', views.CreateCampaignPage),
    url(r'create-clone-campaign/$', views.CreateNewCloneCampaign),
    url(r'create/$', views.CreateNewCampaign),
    url(r'review/$', views.CampaignReviewPage),
    url(r'save-attachment-details/', views.SaveAttachmentDetails),
    url(r'schedule/$', views.CampaignSchedulePage),
    url(r'edit/$', views.EditCampaignPage),
    url(r'export-campaign-report/$', views.ExportCampaignReport),
    url(r'send-campaign/$', views.SendCampaign),
    url(r'send-test-campaign/', views.SendTestCampaign),
    url(r'send-rcs-campaign/$', views.SendRCSCampaign),
    url(r'check-schedule-exists/$', views.CheckScheduleExists),  
    url(r'voice-bot-campaign-details/$', views.VoiceCampaignDetailsPage),
    url(r'get-voice-campaign-details/$', views.GetVoiceCampaignDetails),
    url(r'save-export-voice-campaign-history-request/$', views.SaveExportVoiceCampaignHistoryRequest),

    # Campaign Template
    url(r'create-template/$', views.CampaignTemplatePage),
    url(r'get-campaign-templates/$', views.GetCampaignTemplates),
    url(r'get-campaign-template-details/$', views.GetCampaignTemplateDetails),
    url(r'add-template-to-campaign/$', views.AddTemplateToCampaign),
    url(r'upload-template/$', views.UploadNewTemplate),
    url(r'delete-campaign-template/$', views.DeleteCampaignTemplate),
    url(r'delete-template-file/$', views.DeleteUploadedTemplateFile),
    url(r'save-template/$', views.SaveCampaignTemplate),
    url(r'download-sample-campaign-template/$',
        views.DownloadSampleCampaignTemplate),
    url(r'download-campaign-template/$', views.DownloadCampaignTemplate),
    url(r'whatsapp-campaign-details/$', views.WhatsappCampaignDetailsPage),
    url(r'get-whatsapp-audience-campaign-details/$', views.GetWhatsappAudienceCampaignDetailsPage),
    url(r'save-export-whatsapp-campaign-history-request/$', views.SaveExportWhatsappCampaignHistoryRequest),

    # RCS Campaign Template
    url(r'save-template-rcs/$', views.SaveCampaignTemplateRCS),

    # Tag Audience
    url(r'tag-audience/$', views.TagAudiencePage),
    url(r'get-campaign-batches/$', views.GetCampaignBatches),
    url(r'download-batch-template/$', views.DownloadCampaignBatchTemplate),
    url(r'download-batch-file/$', views.DownloadCampaignBatchFile),
    url(r'^download-file/(?P<file_key>[a-zA-Z0-9-_]+)/(?P<file_name>[\Wa-zA-Z0-9-_. ()]+)/$', views.FileAccess),
    url(r'upload-batch/$', views.UploadNewBatch),
    url(r'save-batch/$', views.SaveCampaignBatch),
    url(r'delete-batch/$', views.DeleteBatch),
    url(r'delete-batch-file/$', views.DeleteUploadedBatchFile),
    url(r'add-batch-to-campaign/$', views.AddBatchToCampaign),
    url(r'test-audience-data/$', views.GetTestAudienceData),

    # API Integration
    url(r'^send-otp/', views.SendOTP),
    url(r'^verify-user/', views.VerifyUser),
    url(r'^get-selected-bot-wsp-code/', views.GetSelectedBotWSPCode),
    url(r'^api-editor/$', views.APIEditorPage),
    url(r'^save-api-code/', views.SaveCampaignAPICode),
    url(r'^mark-api-integration-completed/', views.MarkAPIIntegrationCompleted),
    url(r'^run-api/', views.CampaignAPIRun),
    url(r'^extend-session/', views.ExtendCampaignAPIUserSession),

    # Analytics
    url(r'^campaign-analytics/$', views.CampaignAnalyticsPage),
    url(r'^get-campaign-basic-analytics/$', views.GetCampaignBasicAnalytics),
    url(r'^get-campaign-detailed-analytics/$', views.GetCampaignDetailedAnalytics),
    url(r'^get-campaign-success-ratio-analytics/$', views.GetCampaignSuccessRatioAnalytics),
    url(r'^get-channel-campaign-stats-analytics/$', views.GetChannelCampaignStatsAnalytics),

    # External Exposed APIs
    url(r'^lambda/push-message/$', views_lambda.LambdaPushMessage),
    url(r'^lambda/push-delivery-packets/$', views_lambda.LambdaPushDeliveryPackets),
    url(r'^external/get-auth-token/', views.GetAuthToken),
    url(r'^external/create-campaign-external/', views.CreateExternalNewCampaign),
    url(r'^external/send-campaign-message-external/', views.SendCampaignMessageExternal),
    url(r'^external/get-campaign-reports-external/', views.GetCampaignReportsExternal),
    url(r'^external/send-event-based-triggered-whatsapp-campaign/', views.SendEventBasedTriggeredWhatsappCampaign),
    url(r'^external/create-event-based-whatsapp-campaign/', views.CreateEventBasedWhatsappCampaign),
    url(r'^external/get-event-based-whatsapp-campaign-reports/', views.GetEventBasedTriggeredCampaignReports),

    # Schedule Campaign
    url(r'create-schedule-campaign/$', views.AddCampaignSchedule),
    url(r'get-upcoming-schedules/$', views.GetUpcomingSchedule),
    url(r'get-single-schedule-data/$', views.GetSingleScheduleData),
    url(r'edit-schedule-campaign/$', views.EditScheduleCampaign),
    url(r'delete-schedule-campaign/$', views.DeleteScheduleCampaign),

    # Voice Bot
    url(r'voice-bot/settings/$', views.TriggerSettingsPage),
    url(r'voice-bot/settings/save/$', views.SaveTriggerSettings),

    url(r'campaign-end-call-back/$', views.CampaignEndCallBack),
    url(r'call-end-call-back/$', views.CallEndCallBack),

    # Track Event Progress
    url(r'^track-event-progress/', views.TrackEventProgress),

    # Campaign API documentation
    url(r'^campaign-api-documentation/$', views.CampaignAPIDocumentation),

]
