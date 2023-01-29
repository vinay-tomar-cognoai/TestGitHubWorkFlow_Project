from django.contrib import admin
from django.conf.urls import url, include

from . import views
from . import views_analytics as va

urlpatterns = [
    url(r'^$', views.homePage),
    url(r'^logout/$', views.logoutAPI, name="logout-api"),
    # Dashboard
    url(r'^dashboard/$', views.dashboard),
    url(r'^get-active-tickets/$', views.GetActiveTickets),
    url(r'^get-ticket-details/$', views.GetTicketDetails),
    url(r'^get-mapped-agents/$', views.GetMappedAgents),
    url(r'^active-agent-metadata/$', views.ActiveAgentMetaData),
    url(r'^save-agent-lead-table-metadata/$', views.SaveAgentLeadTableMetadata),
    url(r'^update-ticket-priority/$', views.UpdateTicketPriority),
    url(r'^update-ticket-category/$', views.UpdateTicketCategory),
    url(r'^assign-agent/$', views.AssignAgent),
    url(r'^get-agent-comments/$', views.GetAgentComments),
    url(r'^get-ticket-audit-trail/$', views.GetTicketAuditTrail),
    url(r'^save-agent-comments/$', views.SaveAgentComments),

    # Analytics
    url(r'^analytics/$', views.Analytics),
    url(r'^card-analytics/$', va.CardAnalytics),
    url(r'^service-request-analytics/$', va.ServiceRequestAnalytics),
    url(r'^export-analytics/$', va.ExportAnalytics),

    # Access Management
    url(r'^access-management/$', views.AccessManagement),
    url(r'^add-new-agent/$', views.AddNewAgentDetails),
    url(r'^update-agent-details/$', views.UpdateAgentDetails),
    url(r'^delete-tms-agent/$', views.DeleteTMSAgent),
    url(r'^change-agent-activate-status/$', views.ChangeAgentActivateStatus),
    url(r'^change-agent-absent-status/$', views.ChangeAgentAbsentStatus),
    url(r'^resend-account-password/$', views.ResendAccountPassword),
    url(r'^upload-user-details/$', views.UploadUserDetails),
    url(r'^download-user-details-excel-template/$', views.DownloadUserDetailsTemplate),
    url(r'^export-user-details/$', views.ExportUserDetails),
    url(r'^export-supervisor-details/$', views.ExportSupervisorDetails),

    # Settings
    url(r'^settings/', views.ConsoleSettings),
    url(r'^agent/save-details/$', views.SaveAgentDetails),
    url(r'^agent/save-tms-meta-details/general/$', views.SaveTMSMetaDetailsGeneral),
    url(r'^upload-tms-logo/$',
        views.UploadTMSLogo, name="upload-tms-logo"),
    url(r'^delete-tms-logo/$',
        views.DeleteTMSLogo, name="delete-tms-logo"),

    # Notifications
    url(r'^notifications/', views.Notifications),

    # Common API
    url(r'^fetch-user-notification-count/$', views.FetchUserNotificationCount),
    url(r'^fetch-user-notification/$', views.FetchUserNotification),
    url(r'^clear-user-notification/$', views.ClearUserNotification),
    url(r'^download-file/(?P<file_key>[a-zA-Z0-9-_]+)/$', views.fileAccess),

    # CRM Integration
    url(r'^download-crm-document/(?P<document_type>[a-zA-Z0-9-_]+)$', views.DownloadCRMDocuments),
    url(r'^crm/auth-token/$', views.CRMGenerateAuthToken),
    url(r'^crm/generate-ticket/$', views.CRMGenerateTicket),
    url(r'^crm/ticket-info/$', views.CRMGetTicketInfo),
    url(r'^crm/ticket-activity/$', views.CRMGetTicketActivity),

    # Developer Settings
    url(r'^developer-settings/api-integration/$', views.DeveloperSettingsApiIntegration),
    url(r'^save-whatsapp-api-processor-code/$', views.SaveWhatsappApiProcessorCode),
]
