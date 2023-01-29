from django.contrib import admin

# Register your models here.
from EasyAssistApp.models import *
from EasyAssistApp.forms import *


class CobrowseIOAdmin(admin.ModelAdmin):

    list_per_page = 100
    list_display = ('session_id', 'is_lead', 'mobile_number',
                    'title', 'active_url', 'cobrowsing_start_datetime', )
    list_filter = ('is_lead', 'allow_agent_cobrowse', 'agent', )
    ordering = ('-request_datetime', )

admin.site.register(CobrowseIO, CobrowseIOAdmin)

admin.site.register(CobrowseAgent)

admin.site.register(CobrowsingSessionMetaData)


class CobrowseAccessTokenAdmin(admin.ModelAdmin):

    exclude = ('advanced_setting_static_file_action', 'enable_masking_pii_data',)

admin.site.register(CobrowseAccessToken, CobrowseAccessTokenAdmin)

admin.site.register(CobrowsingMiddlewareAccessToken)

admin.site.register(SecuredLogin)

admin.site.register(CobrowsingAuditTrail)


class CobrowseLeadHTMLFieldAdmin(admin.ModelAdmin):

    list_display = ('tag', 'tag_name', 'tag_id', 'tag_label',
                    'tag_type', 'tag_key', 'tag_value', 'is_deleted')

admin.site.register(CobrowseLeadHTMLField, CobrowseLeadHTMLFieldAdmin)

admin.site.register(CobrowseBlacklistedTag)

admin.site.register(CobrowseObfuscatedField)


class CobrowseAutoFetchFieldAdmin(admin.ModelAdmin):

    list_display = ('fetch_field_key', 'fetch_field_value',
                    'modal_field_key', 'modal_field_value', )

admin.site.register(CobrowseAutoFetchField, CobrowseAutoFetchFieldAdmin)

admin.site.register(CobrowseDisableField)


class CobrowseAgentCommentAdmin(admin.ModelAdmin):

    list_filter = ('agent', )

admin.site.register(CobrowseAgentComment, CobrowseAgentCommentAdmin)


class SystemAuditTrailAdmin(admin.ModelAdmin):

    list_filter = ('category', 'cobrowse_access_token', )

    list_display = ('category', 'description',
                    'cobrowse_io', 'cobrowse_access_token', )


admin.site.register(SystemAuditTrail, SystemAuditTrailAdmin)

admin.site.register(CobrowseChatHistory)


class CobrowsingFileAccessManagementAdmin(admin.ModelAdmin):
    ordering = ('-created_datetime', )
    list_display = ('key', 'is_public', 'access_token',
                    'created_datetime', 'file_path', )
    list_filter = ('is_public', )


admin.site.register(CobrowsingFileAccessManagement,
                    CobrowsingFileAccessManagementAdmin)

admin.site.register(SupportDocument)


class EasyAssistCustomerAdmin(admin.ModelAdmin):

    list_per_page = 100
    list_display = ('customer_id', 'full_name',
                    'mobile_number', 'title', 'active_url', 'cobrowse_io')
    list_filter = ('request_datetime', 'title', 'active_url')

admin.site.register(EasyAssistCustomer, EasyAssistCustomerAdmin)


class NotificationManagementAdmin(admin.ModelAdmin):

    list_per_page = 100
    list_display = ('cobrowse_io', 'agent', 'notification_message')
    list_filter = ('cobrowse_io', 'agent')

admin.site.register(NotificationManagement, NotificationManagementAdmin)


class LanguageSupportAdmin(admin.ModelAdmin):

    list_per_page = 100
    list_display = ['title']

admin.site.register(LanguageSupport, LanguageSupportAdmin)


class ProductCategoryAdmin(admin.ModelAdmin):

    list_per_page = 100
    list_display = ['title']

admin.site.register(ProductCategory, ProductCategoryAdmin)

admin.site.register(CobrowseVideoConferencing)

admin.site.register(CobrowseVideoAuditTrail)

admin.site.register(CobrowseVideoConferencingForm)

admin.site.register(CobrowseVideoconferencingFormCategory)

admin.site.register(CobrowseVideoConferencingFormElement)

admin.site.register(CobrowseVideoConferencingFormData)


class CobrowseAgentOnlineAuditTrailAdmin(admin.ModelAdmin):

    list_per_page = 100
    list_display = ('agent', 'last_online_start_datetime',
                    'last_online_end_datetime', )
    list_filter = ('agent', )

admin.site.register(CobrowseAgentOnlineAuditTrail,
                    CobrowseAgentOnlineAuditTrailAdmin)


class CobrowseAgentWorkAuditTrailAdmin(admin.ModelAdmin):

    list_per_page = 100
    list_display = ('agent', 'session_start_datetime',
                    'session_end_datetime', )
    list_filter = ('agent', )

admin.site.register(CobrowseAgentWorkAuditTrail,
                    CobrowseAgentWorkAuditTrailAdmin)


class EasyAssistVisitorAdmin(admin.ModelAdmin):

    list_per_page = 100
    list_display = ['visiting_date', 'visitor_count', 'get_username']

    def get_username(self, obj):
        try:
            return obj.access_token.agent.user.username
        except Exception:
            return "None"

admin.site.register(EasyAssistVisitor, EasyAssistVisitorAdmin)


class CobrowseScreenRecordingAuditTrailAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = ['cobrowse_io', 'recording_started', 'is_recording_ended']

admin.site.register(CobrowseScreenRecordingAuditTrail,
                    CobrowseScreenRecordingAuditTrailAdmin)

admin.site.register(CobrowseCapturedLeadData)


class CobrowseDropLinkAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = ('key', 'agent', 'client_page_link',
                    'customer_name', 'generate_datetime')
    list_filter = ('agent', )

admin.site.register(CobrowseDropLink, CobrowseDropLinkAdmin)


class EasyAssistExportDataRequestAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = ['agent', 'export_request_datetime', 'is_completed']

admin.site.register(EasyAssistExportDataRequest, EasyAssistExportDataRequestAdmin)

admin.site.register(CobrowsePageVisitCount)

admin.site.register(CobrowseCustomSelectRemoveField)


class AssignTaskProcessorAdmin(admin.ModelAdmin):

    form = AssignTaskProcessorForm


admin.site.register(AssignTaskProcessor, AssignTaskProcessorAdmin)

admin.site.register(StaticFileChangeLogger)


class CRMIntegrationModelAdmin(admin.ModelAdmin):
    list_filter = ('is_expired', 'access_token')
    readonly_fields = ('auth_token',)
    list_display = ('access_token', 'auth_token', 'is_expired')

admin.site.register(CRMIntegrationModel, CRMIntegrationModelAdmin)

admin.site.register(CRMCobrowseLoginToken)

admin.site.register(ChromeExtensionDetails)

admin.site.register(EasyAssistBugReport)

admin.site.register(CobrowseDateWiseInboundAnalytics)

admin.site.register(CobrowseDateWiseOutboundAnalytics)

admin.site.register(CobrowseDateWiseReverseAnalytics)

admin.site.register(AppCobrowseMaskedFields)

admin.site.register(CobrowseMailerAnalyticsProfile)

admin.site.register(CobrowseMailerAnalyticsGraph)

admin.site.register(CobrowseMailerAnalyticsTable)

admin.site.register(CobrowseMailerAnalyticsAttachment)

admin.site.register(CobrowseMailerAnalyticsCalendar)

admin.site.register(CobrowseDateWiseOutboundDroplinkAnalytics)

admin.site.register(CobrowseMailerProfileStaticEmailAuditTrail)

admin.site.register(CobrowseMailerAnalyticsAuditTrail)


class CobrowseSandboxUserAdmin(admin.ModelAdmin):

    exclude = ('password',)
    list_display = ('user', 'is_expired',)

admin.site.register(CobrowseSandboxUser, CobrowseSandboxUserAdmin)

admin.site.register(CobrowseIOInvitedAgentsDetails)

admin.site.register(CobrowseIOTransferredAgentsLogs)


class CobrowseCalendarAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_date', 'description', 'auto_response',
                    'created_by', 'modified_by', 'modified_date')

admin.site.register(CobrowseCalendar, CobrowseCalendarAdmin)

admin.site.register(EasyAssistAPIIntegrationManager)

admin.site.register(AgentDetailsAPIProcessor)

admin.site.register(UnattendedLeadTransferAuditTrail)

admin.site.register(ProxyCobrowseIO)

admin.site.register(EasyAssistCronjobTracker)


class EasyAssistPopupConfigurationsAdmin(admin.ModelAdmin):

    list_display = ('access_token', )


admin.site.register(EasyAssistPopupConfigurations,
                    EasyAssistPopupConfigurationsAdmin)

admin.site.register(LiveChatCannedResponse)

admin.site.register(AgentFrequentLiveChatCannedResponses)

admin.site.register(ProxyCobrowseConfig)

admin.site.register(CobrowseDateWiseOutboundProxyAnalytics)
