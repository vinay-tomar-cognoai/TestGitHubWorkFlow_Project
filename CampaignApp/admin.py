from django.contrib import admin

# Register your models here.
from CampaignApp.models import *
from CampaignApp.forms import *


admin.site.register(CampaignAnalytics)

admin.site.register(CampaignChannel)

admin.site.register(CampaignCronjobTracker)

admin.site.register(CampaignVoiceUser)

admin.site.register(VoiceCampaignHistoryExportRequest)


class QuickReplyAdmin(admin.ModelAdmin):

    raw_id_fields = ('audience_log',)


admin.site.register(QuickReply, QuickReplyAdmin)

admin.site.register(CampaignHistoryExportRequest)


class CampaignAdmin(admin.ModelAdmin):

    exclude = ('last_saved_state',)

    list_per_page = 100
    list_display = ('name', 'status', 'channel',
                    'bot', 'is_deleted',)
    list_filter = ('status', 'channel', )
    ordering = ('-create_datetime', )


admin.site.register(Campaign, CampaignAdmin)


class CampaignAudienceLogAdmin(admin.ModelAdmin):

    raw_id_fields = ('audience', 'campaign')


admin.site.register(CampaignAudienceLog, CampaignAudienceLogAdmin)

admin.site.register(CampaignAudience)

admin.site.register(CampaignBatch)

admin.site.register(CampaignTemplateLanguage)

admin.site.register(CampaignTemplateCategory)

admin.site.register(CampaignTemplateStatus)

admin.site.register(CampaignTemplateType)

admin.site.register(CampaignTemplate)


class CampaignAPIAdmin(admin.ModelAdmin):

    form = CampaignAPIForm


admin.site.register(CampaignAPI, CampaignAPIAdmin)

admin.site.register(CampaignAuthUser)

admin.site.register(CampaignAPILogger)

admin.site.register(CampaignFileAccessManagement)

admin.site.register(CampaignConfig)

admin.site.register(CampaignExportRequest)

admin.site.register(CampaignTemplateVariable)

admin.site.register(CampaignWhatsAppServiceProvider)

admin.site.register(CampaignBotWSPConfig)

admin.site.register(CampaignAuthToken)

admin.site.register(CampaignSchedule)

admin.site.register(CampaignScheduleObject)

admin.site.register(CampaignVoiceBotSetting)

admin.site.register(VoiceBotRetrySetting)


class CampaignVoiceBotAPIAdmin(admin.ModelAdmin):

    form = CampaignVoiceBotAPIForm


admin.site.register(CampaignVoiceBotAPI, CampaignVoiceBotAPIAdmin)

admin.site.register(VoiceBotCallerID)

admin.site.register(CampaignVoiceBotAnalytics)

admin.site.register(CampaignVoiceBotDetailedAnalytics)

admin.site.register(CampaignRCSDetailedAnalytics)

admin.site.register(CampaignRCSTemplate)

admin.site.register(CampaignEventProgress)
