from django.contrib import admin

from LiveChatApp.models import *

# Register your models here.


class LiveChatUserAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'Role', 'logging_time',
                    'last_updated_time', 'is_online')

    list_filter = ('last_updated_time', 'is_online')

    def get_username(self, obj):
        try:
            return obj.user.username
        except Exception:
            return "None"

    get_username.short_description = "Username"

    def Role(self, obj):
        try:
            if obj.status == "0":
                return "LiveChat-Only-Admin"
            elif obj.status == "1":
                return "Live-Chat Admin"
            elif obj.status == "2":
                return "Live-Chat Manager"
            else:
                return "Live-Chat Agent"
        except Exception:
            return "None"


class LiveChatCustomerAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'get_username', 'agent_id',
                    'bot', 'is_session_exp', 'is_denied')

    def get_username(self, obj):
        try:
            return obj.username
        except Exception:
            return "No Agent Assigned"


class LiveChatConfigAdmin(admin.ModelAdmin):
    list_display = ('bot', 'max_customer_count')


class CannedResponseAdmin(admin.ModelAdmin):
    list_display = ('title', 'keyword',)


class LiveChatCalenderAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_date', 'description', 'auto_response',
                    'created_by', 'modified_by', 'modified_date')


class LiveChatDataExportRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_completed')


class LiveChatAuditTrailAdmin(admin.ModelAdmin):
    list_display = ('user', 'action')


class LiveChatSessionManagementAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_id', 'session_starts_at',
                    'session_ends_at', 'session_completed')


class LiveChatAgentNotReadyAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_id',
                    'not_ready_starts_at', 'not_ready_ends_at')


class LiveChatVideoConferencingAdmin(admin.ModelAdmin):
    list_display = ('meeting_id', 'agent', 'is_expired')


class LiveChatAdminConfigAdmin(admin.ModelAdmin):
    list_display = ('get_username',)

    def get_username(self, obj):
        try:
            return str(obj.admin.user.username)
        except Exception:
            return "None"


class LiveChatCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'bot', 'is_deleted')


admin.site.register(LiveChatCategory, LiveChatCategoryAdmin)
admin.site.register(CannedResponse, CannedResponseAdmin)
admin.site.register(LiveChatConfig, LiveChatConfigAdmin)
admin.site.register(LiveChatUser, LiveChatUserAdmin)
admin.site.register(LiveChatCustomer, LiveChatCustomerAdmin)
admin.site.register(LiveChatBlackListKeyword)
admin.site.register(LiveChatCalender, LiveChatCalenderAdmin)
admin.site.register(LiveChatDataExportRequest,
                    LiveChatDataExportRequestAdmin)
admin.site.register(LiveChatAuditTrail, LiveChatAuditTrailAdmin)
admin.site.register(LiveChatSessionManagement, LiveChatSessionManagementAdmin)
admin.site.register(LiveChatAgentNotReady, LiveChatAgentNotReadyAdmin)
admin.site.register(LiveChatVideoConferencing, LiveChatVideoConferencingAdmin)
admin.site.register(LiveChatAdminConfig, LiveChatAdminConfigAdmin)
admin.site.register(LiveChatConsoleColour)
admin.site.register(LiveChatWhatsAppServiceProvider)


class LiveChatMISDashboardAdmin(admin.ModelAdmin):
    list_display = ('livechat_customer', 'sender', 'message_time')


admin.site.register(LiveChatMISDashboard, LiveChatMISDashboardAdmin)


class LiveChatTransferAuditAdmin(admin.ModelAdmin):
    list_display = ('chat_transferred_by',
                    'chat_transferred_to', 'livechat_customer')


admin.site.register(LiveChatTransferAudit, LiveChatTransferAuditAdmin)
admin.site.register(LiveChatFileAccessManagement)
admin.site.register(LiveChatDeveloperProcessor)
admin.site.register(LiveChatProcessors)
admin.site.register(LiveChatGuestAgentAudit)
admin.site.register(LiveChatInternalMISDashboard)
admin.site.register(LiveChatInternalMessageInfo)
admin.site.register(LiveChatInternalChatGroup)
admin.site.register(LiveChatInternalGroupActivity)
admin.site.register(LiveChatInternalMessageReceipt)
admin.site.register(LiveChatInternalChatGroupMembers)
admin.site.register(LiveChatEmailProfile)
admin.site.register(LiveChatEmailTableParameters)
admin.site.register(LiveChatEmailGraphParameters)
admin.site.register(LiveChatEmailAttachmentParameters)
admin.site.register(LiveChatMailerAuditTrail)
admin.site.register(LiveChatDisposeChatForm)

admin.site.register(LiveChatVoIPData)
admin.site.register(LiveChatTranslationCache)
admin.site.register(LiveChatRaiseTicketForm)
admin.site.register(LiveChatTicketAudit)
admin.site.register(LiveChatInternalUserGroup)
admin.site.register(LiveChatCobrowsingData)
admin.site.register(LiveChatFollowupCustomer)
admin.site.register(LiveChatReportedCustomer)

admin.site.register(LiveChatEmailConfig)
admin.site.register(LiveChatEmailConfigSetup)
admin.site.register(LiveChatMISEmailData)

admin.site.register(LiveChatInternalChatLastSeen)

admin.site.register(LiveChatAuthToken)
admin.site.register(LiveChatExternalAPIAuditTrail)

admin.site.register(LiveChatCronjobTracker)


class FusionAuditTrailAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'api_name', 'api_status_code')


admin.site.register(FusionAuditTrail, FusionAuditTrailAdmin)
