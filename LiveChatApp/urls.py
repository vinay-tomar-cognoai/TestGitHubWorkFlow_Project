from django.contrib import admin
from django.conf.urls import url, include

from . import views
from . import views_livechat_vc as livechat_vc
from EasyChatApp import views_android

urlpatterns = [
    url(r'^$', views.HomePage),
    # url(r'^login/$', views.LiveChatLoginPage),

    # Manager side activity

    url(r'^manage-agents/$', views.ManageAgent),
    url(r'^manage-agents-continuous/$', views.ManageAgentsContinuous),
    url(r'^system-settings/$', views.SystemSettings),
    url(r'^interaction-settings/$', views.InteractionSettings),
    url(r'^update-customer-list/$', views.UpdateCustomerList),
    url(r'^check-customers-are-assigned/$', views.CheckCustomersAreAssigned),
    url(r'^create-customer/$', views.CreateCustomerRoom),
    url(r'^save-customer-chat/$', views.SaveCustomerChat),
    url(r'^save-agent-chat/$', views.SaveAgentChat),
    url(r'^save-supervisor-chat/$', views.SaveSupervisorChat),
    url(r'^mark-customer-offline/$', views.MarkCustomerOffline),
    url(r'^get-archived-customer-chat/$', views.GetArchivedCustomerChat),
    url(r'^save-system-settings/$', views.SaveSystemSettings),
    url(r'^save-interaction-settings/$', views.SaveInteractionSettings),
    url(r'^chat-history/$', views.AuditTrail),
    url(r'^get-previous-session-message/$', views.PreviousSessionMessages),
    url(r'^create-new-canned-response/$', views.CreateNewCannedResponse),
    url(r'^create-new-canned-response-excel/$',
        views.CreateCannedResponseWithExcel),
    url(r'^get-canned-response/$', views.GetCannedResponse),
    url(r'^edit-canned-response/$', views.EditCannedResponse),
    url(r'^delete-canned-response/$', views.DeleteCannedResponse),
    url(r'^save-livechat-feedback/$', views.SaveLiveChatFeedback),
    url(r'^category/$', views.GetCategoryList),
    url(r'^edit-livechat-category/$', views.EditLiveChatCategory),
    url(r'^create-new-category/$', views.CreateNewCategory),
    url(r'^delete-livechat-category/$', views.DeleteLiveChatCategory),
    url(r'^get-livechat-category/$', views.GetLiveChatCategoryList),
    url(r'^switch-agent-manager/$', views.SwitchAgentManager),
    url(r'^edit-agent-info/$', views.EditAgentInfo),
    url(r'^get-bots-under-user/$', views.GetBotUnderUser),
    url(r'^data-mask-toggle/$', views.DataMaskToggle),
    url(r'^check-data-toggle-otp/$', views.CheckDataToggleOtp),
    url(r'^create-new-agent/$', views.CreateNewAgent),
    url(r'^delete-agent/$', views.DeleteAgent),
    url(r'^submit-agents-excel/$', views.CreateAgentWithExcel),
    url(r'^download-create-agent-template/$', views.DownloadAgentExcelTemplate),
    url(r'^upload-excel/$', views.LiveChatUploadExcel),
    url(r'^get-livechat-history/', views.GetLiveChatHistory),
    url(r'^get-livechat-message-history/', views.GetLiveChatMessageHistory),
    url(r'^get-livechat-message-details/', views.GetLiveChatMessageDetails),
    url(r'^export-livechat-users/', views.ExportLiveChatUsers),

    # LiveChat Only admin

    url(r'^manage-only-admin/$', views.ManageOnlyAdmin),
    url(r'^create-livechat-only-admin/$', views.CreateNewLiveChatOnlyAdmin),
    url(r'^edit-livechat-only-admin/$', views.EditLiveChatOnlyAdminInfo),
    url(r'^delete-livechat-only-admin/$', views.DeleteLiveChatOnlyAdmin),
    url(r'^download-create-livechat-only-admin-template/$',
        views.DownloadLiveChatOnlyAdminExcelTemplate),
    url(r'^submit-livechat-only-admin-excel/$',
        views.CreateLiveChatOnlyAdminWithExcel),

    # Blacklisted keyword

    url(r'^blacklisted-keyword/$', views.BlackListKeyword),
    url(r'^add-blacklisted-keyword/$', views.AddBlacklistedKeyword),
    url(r'^edit-blacklisted-keyword/$', views.EditBlacklistedKeyword),
    url(r'^delete-blacklisted-keyword/$', views.DeleteBlackListedKeyword),
    url(r'^create-blacklisted-keyword-excel/$', views.CreateBlacklistedKeywordWithExcel),

    # LiveChat calender

    url(r'^calender/$', views.LiveChatCalenderPage),
    url(r'^add-holiday-calender/$', views.AddHolidayCalender),
    url(r'^delete-calender-event/$', views.DeleteCalenderEvent),
    url(r'^edit-calender-event/$', views.EditCalenderEvent),
    url(r'^create-working-hours/$', views.CreateWorkingHours),


    # Agent side activity

    url(r'^agent-bot/$', views.AgentIframe),
    url(r'^end-chat-session/$', views.EndChatSession),
    url(r'^agent-profile/$', views.AgentProfile),
    url(r'^agent-settings/$', views.AgentSettings),
    url(r'^assign-agent/$', views.AssignAgent),
    url(r'^canned-response/$', views.CannedResponseURL),
    url(r'^transfer-chat/$', views.TransferChat),
    url(r'^get-livechat-agents/$', views.GetLiveChatAgents),
    url(r'^get-customer-details/$', views.GetCustomerDetails),
    url(r'^save-agent-general-settings/$', views.SaveAgentGeneralSettings),
    url(r'^switch-agent-status/$', views.SwitchAgentStatus),
    url(r'^update-message-history/$', views.UpdateMessageHistory),
    url(r'^invite-guest-agent/$', views.InviteGuestAgent),
    url(r'^guest-agent-accept/$', views.GuestAgentAccept),
    url(r'^guest-agent-reject/$', views.GuestAgentReject),
    url(r'^guest-agent-exit/$', views.GuestAgentExit),
    url(r'^guest-agent-no-response/$', views.GuestAgentNoResponse),
    url(r'^get-agents-group-chat/$', views.GetAgentsGroupChat),
    url(r'^update-guest-agent-status/$', views.UpdateGuestAgentStatus),
    url(r'^check-reply-message-sender/$', views.CheckReplyMessageSender),
    url(r'^update-customer-details/$', views.UpdateCustomerDetails),
    url(r'^enable-livechat-transcript/$', views.EnableLiveChatTranscript),
    url(r'^livechat-transcript/$', views.LiveChatTranscript),
    url(r'^get-livechat-special-character-toggle/$', views.GetLiveChatSpecialCharacterToggle),
    url(r'^get-whatsapp-webhook-status/$', views.GetWhatsAppWebhookStatus),
    
    # LiveChat file upload by agent
    url(r'^upload-attachment/', views.LiveChatUploadAttachment),
    # Previous chat history customer side
    url(r'^get-livechat-previous-messages/$', views.GetMessageHistory),
    url(r'^get-livechat-session-expire/$', views_android.CheckLiveChatSession),

    url(r'^update-unread-message-count/', views.UpdateUnreadMessageCount),

    # Update user last seen
    url(r'^update-last-seen/$', views.UpdateLastSeen),

    # LiveChat Analytics and Reports
    url(r'^analytics/$', views.LiveChatAnalytics),
    url(r'^get-chart-report-analytics/', views.GetLiveChatChatReportsAnalytics),
    url(r'^get-avg-nps-analytics/', views.GetAverageNPSAnalytics),
    url(r'^get-avg-handle-time-analytics/',
        views.GetAverageHandleTimeAnalytics),
    url(r'^get-avg-queue-time-analytics/',
        views.GetAverageQueueTimeAnalytics),
    url(r'^get-interactions-per-chat-analytics/',
        views.GetInteractionsPerChatAnalytics),
    url(r'^download-chat-transcript/$', views.DownloadChatTranscript),
    url(r'^exportdata/$', views.ExportData),
    url(r'^offline-chats-report/$', views.OfflineChatsReport),
    url(r'^offline-chats-exportdata/$', views.OfflineChatsExportData),
    url(r'^abandoned-chats-exportdata/$',
        views.AbandonedChatsExportData),
    url(r'^abandoned-chats-report/$', views.AbandonedChatsReport),
    url(r'^missed-chats-report/$', views.MissedChatsReport),
    url(r'^missed-chats-exportdata/$', views.MissedChatsExportData),
    url(r'^login-logout-report/$', views.LoginLogoutReport),
    url(r'^login-logout-report-exportdata/$',
        views.LoginLogoutReportExportData),
    url(r'^agent-not-ready-report/$', views.AgentNotReadyReport),
    url(r'^agent-not-ready-report-exportdata/$',
        views.AgentNotReadyReportExportData),
    url(r'^daily-interaction-count/$', views.DailyInteractionCount),
    url(r'^dailey-interaction-count-exportdata/$',
        views.DailyInteractionCountExportData),
    url(r'^hourly-interaction-count/$', views.HourlyInteractionCountPage),
    url(r'^hourly-interaction-count-by-date/$', views.HourlyInteractionCountByDate),
    url(r'^hourly-interaction-cumulative-count-by-date-range/$', views.HourlyInteractionCumulativeCountByDateRange),
    url(r'^hourly-interaction-count-exportdata/$',
        views.HourlyInteractionCountExportData),
    url(r'^analytics-exportdata/$',
        views.LiveChatAnalyticsExportData),
    url(r'^agent-performance-report/$', views.AgentPerformanceReport),
    url(r'^agent-performance-report-exportdata/$',
        views.AgentPerformanceReportExportData),
    url(r'^analytics-continous/$', views.LiveChatAnalyticsContinous),
    url(r'^get-categories-from-supervisors/$', views.GetCategoriesFromSupervisors),
    url(r'^get-agents-from-supervisors/$', views.GetAgentsFromSupervisors),
    url(r'^get-supervisors-from-categories/$', views.GetSupervisorsFromCategories),
    url(r'^agent-analytics/$', views.AgentAnalytics),
    url(r'^get-agent-analytics/$', views.GetAgentAnalytics),


    ####################### Secured Files Access #####################
    url(r'^download-file/(?P<file_key>[a-zA-Z0-9-_]+)/(?P<file_name>[a-zA-Z0-9-_.: ()]+)/$', views.FileAccess),
    url(r'^logout/$', views.LiveChatLogoutPage),

    url(r'^mark-chat-abandoned/$', views.LiveChatMarkChatAbandoned),

    ####################### Developer Options #####################
    url(r'^developer-settings/$', views.DeveloperSettings),
    url(r'^developer-editors/$', views.DeveloperEditor),
    url(r'^save-livechat-processor/$', views.SaveLiveChatProcessorContent),
    url(r'^livechat-processor-run/$', views.LiveChatProcessorRun),

    ######################### Internal Chat #############
    url(r'^internal-chat/$', views.InternalChatPage),
    url(r'^create-chat-group/', views.CreateChatGroup),
    url(r'^upload-internal-chat-attachment/',
        views.LiveChatUploadInternalChatAttachment),
    url(r'^update-internal-chat-history/', views.UpdateInternalChatHistory),
    url(r'^update-group-chat-list/', views.UpdateChatGroupList),
    url(r'^save-internal-chat/$', views.SaveInternalChat),
    url(r'^edit-group-details/', views.EditChatGroupDetails),
    url(r'^get-livechat-user-details/$', views.GetLiveChatUserDetails),
    url(r'^get-group-chat-history/', views.GetInternalChatGroupHistory),
    url(r'^get-livechat-user-details/', views.GetLiveChatUserDetails),
    url(r'^check-image-file/', views.CheckImageFile),
    url(r'^add-user-to-user-group/', views.AddUsertoUserGroup),
    url(r'^get-user-group-chat-history/', views.GetInternalUserGroupHistory),
    url(r'^update-last-seen-on-chats/', views.UpdateLastSeenOnChats),
    url(r'^leave-group/(?P<group_id>[a-zA-Z0-9-_]+)$', views.LeaveGroup),
    url(r'^set-chat-started/', views.SetChatStarted),

    ######################### Email Profile #############
    url(r'^email-settings/$', views.EmailSettings),
    url(r'^enable-disable-email-notification/$', views.EnableDisableEmailNotif),
    url(r'^save-email-profile/$', views.SaveEmailProfile),
    url(r'^delete-email-profile/$', views.DeleteEmailProfile),
    url(r'^send-sample-mail/$', views.SendSampleMail),

    ######################## Dispose Chat Form #############

    url(r'^livechat-form-builder/$', views.FormBuilderPage),
    url(r'^save-dispose-chat-form/$', views.SaveDisposeChatForm),
    url(r'^get-dispose-chat-form-data/$', views.GetDisposeChatFormData),

    ######################## VoIP ##########################

    url(r'^agent-voice-meeting/', views.LiveChatVoiceMeeting),
    url(r'^agent-meeting-end/', views.LiveChatVoIPMeetingEnded),
    url(r'^manage-voip-request/', views.ManageVoIPRequest),
    url(r'^save-client-recorded-data/', views.SaveClientRecordedData),
    url(r'^save-meeting-duration/', views.SaveVoipMeetingDuration),
    url(r'^check-meeting-status/', views.CheckMeetingStatus),
    url(r'^voip-history/$', views.VOIPHistory),
    url(r'^get-livechat-call-history/', views.GetLiveChatCallHistory),
    url(r'^export-voip-data/$', views.ExportVOIPData),
    url(r'^check-chat-report-status/$', views.CheckChatReportStatus),

    ######################## VC #################################

    url(r'^meeting/(?P<meeting_id>[a-zA-Z0-9-_]+)$', livechat_vc.LiveChatVCMeeting),
    url(r'^generate-video-meeting/$', livechat_vc.GenerateLiveChatVCMeet),
    url(r'^agent-vc-meeting-end/', livechat_vc.LiveChatVCMeetingEnded),
    url(r'^vc-history/$', views.VCHistory),
    url(r'^export-vc-data/$', views.ExportVCData),
    url(r'^save-screen-recorded-data/', livechat_vc.SaveScreenRecordedData),
    url(r'^save-call-feedback/', livechat_vc.SaveCallFeedback),

    ######################## Self Assign Chats #################################
    
    url(r'^requests-in-queue/$', views.RequestsInQueue),
    url(r'^get-livechat-queue-requests/$', views.GetLiveChatQueueRequests),
    url(r'^livechat-self-assign-request/$', views.LiveChatSelfAssignRequest),
    url(r'^check-chat-requests-queue/$', views.CheckChatRequestsQueue),

    ######################## LiveChat Exposed APIs #############################

    url(r'^external/create-customer/$', views.CreateExternalCustomerRoom),
    url(r'^external/save-chat/', views.SaveExternalCustomerChat),
    url(r'^external/end-chat/', views.EndExternalChat),
    url(r'^external/save-feedback/', views.SaveExternalChatFeedback),
    url(r'^external/update-livechat-event/', views.UpdateLiveChatEvents),

    url(r'^send-livechat-event/', views.SendLiveChatEvent),
    url(r'^api-docs/$', views.APIDocsPage),
    url(r'^download-livechat-document/(?P<document_type>[a-zA-Z0-9-_]+)$',
        views.DownloadLiveChatDocuments),

    ##### WhatsApp Webhook Integration
    url(r'^whatsapp-webhook-console/', views.WhatsAppWebhookConsole),
    url(r'^get-livechat-webhook-default-code/$', views.GetLiveChatWebhookDefaultCode),
    url(r'^save-livechat-webhook-content/$', views.SaveLiveChatWebhookContent),

    ######################## LiveChat Integrations #############################

    url(r'^integrations/$', views.LiveChatIntegrationsPage),
    url(r'^integrations/ms-dynamics/', views.MSDynamicsIntegrationPage),
    url(r'^integrations/save/', views.SaveLiveChatIntegrations),
    url(r'^download-ms-integration-doc/$', views.DownloadMSIntegrationDoc),

    ######################## LiveChat Translation #############################

    url(r'^get-translated-message-history/$', views.GetTranslatedMessageHistory),
    url(r'^get-translated-message/$', views.GetTranslatedMessage),

    ######################## LiveChat Agent Raise a Ticket #############################

    url(r'^raise-ticket-form-builder/$', views.RaiseTicketFormBuilder),
    url(r'^save-raise-ticket-form/$', views.SaveRaiseTicketForm),
    url(r'^livechat-raise-ticket/$', views.LiveChatRaiseTicket),
    url(r'^livechat-search-ticket/$', views.LiveChatSearchTicket),
    url(r'^livechat-get-previous-tickets/$', views.LiveChatGetPreviousTickets),

    ####################### LiveChat Cobrowsing #############################

    url(r'^manage-cobrowsing-request/', views.ManageCobrowsingRequest),
    url(r'^cobrowsing-end/', views.LiveChatCobrowsingEnd),
    url(r'^cobrowsing-history/$', views.CobrowsingHistory),
    url(r'^get-cobrowsing-history/', views.GetLiveChatCobrowsingHistory),
    url(r'^export-cobrowsing-data/$', views.ExportCobrowsingData),
    url(r'^save-cobrowsing-nps/$', views.SaveCobrowsingNps),
    url(r'^end-cobrowsing-session/$', views.EndCobrowsingSession),
    
    ######################## LiveChat Followup Leads #############################

    url(r'^followup-leads/$', views.FollowupLeads),
    url(r'^get-livechat-followup-leads/$', views.GetLiveChatFollowupLeads),
    url(r'^get-livechat-followup-lead-messages/$', views.GetLiveChatFollowupLeadMessages),
    url(r'^get-livechat-followup-lead-agents/$', views.GetLiveChatFollowupLeadAgents),
    url(r'^transfer-livechat-followup-lead/$', views.TransferLiveChatFollowupLead),
    url(r'^complete-livechat-followup-lead/$', views.CompleteLiveChatFollowupLead),

    ######################## LiveChat Chat Escalation Matrix #############################

    url(r'^chat-escalation/$', views.ChatEscalation),
    url(r'^save-chat-escalation-data/$', views.SaveChatEscalationData),
    url(r'^chat-escalation-warn-user/$', views.ChatEscalationWarnUser),
    url(r'^chat-escalation-report-user/$', views.ChatEscalationReportUser),
    url(r'^reported-users/$', views.ReportedUsers),
    url(r'^get-livechat-reported-users/$', views.GetLiveChatReportedUsers),
    url(r'^chat-escalation-block-user/$', views.ChatEscalationBlockUser),
    url(r'^chat-escalation-mark-complete/$', views.ChatEscalationMarkComplete),
    url(r'^blocked-users/$', views.BlockedUsers),
    url(r'^get-livechat-blocked-users/$', views.GetLiveChatBlockedUsers),
    url(r'^chat-escalation-ignore-notification/$', views.ChatEscalationIgnoreNotification),

    ######################## LiveChat Email #############################

    url(r'^email-config-authentication/$', views.LiveChatEmailConfigAuthentication),
    url(r'^handle-email-config-status/$', views.HandleEmailConfigStatus),
    url(r'^save-livechat-email-configuration/$', views.SaveLiveChatEmailConfiguration),
    url(r'^save-agent-email-chat/$', views.SaveAgentEmailChat),
    url(r'^transfer-followup-lead-to-email-conversations/$', views.TransferFollowupLeadToEmailConversation),
    url(r'^send-livechat-email-to-customer/$', views.SendLiveChatEmailToCustomer),

    ######################## LiveChat WhatsApp Conversation Reinitiation #############################

    url(r'^reinitiate-whatsapp-conversation/$', views.ReinitiateWhatsAppConversation),

    ######################## Change Agent's Supervisor ##########################

    url(r'^get-supervisor-category/$', views.GetLiveChatSupervisorCategory),

    ######################## LiveChat Exposed APIs #############################

    url(r'^external/get-auth-token/$', views.GetAuthToken),
    url(r'^external/get-analytics-external/$', views.GetAnalyticsExternal),

    ####################### LiveChat NewCustomerJoin API ########################

    url(r'^check-newchat-for-agent/$', views.CheckNewChatForAgent),

    ####################### Ameyo Fusion APIs ########################

    url(r'^fusion/create-customer/$', views.FusionCreateCustomer),
    url(r'^fusion/save-customer-chat/$', views.SaveFusionCustomerChat),
    url(r'^agent-send-message/$', views.PullMessageFromAmeyoAgent),
    url(r'^assign-agent-request/$', views.AssignAgentRequest),

]
