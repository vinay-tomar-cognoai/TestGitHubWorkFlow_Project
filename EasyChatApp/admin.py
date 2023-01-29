from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.urls import reverse

from EasyChatApp.models import *
from EasyChatApp.forms import *
from EasyChatApp.models import RCSDetails

admin.site.unregister(Group)

admin.site.register(CustomerCareAgent)
admin.site.register(LiveChatSession)
admin.site.register(User)
admin.site.register(SandboxUser)
admin.site.register(SecuredLogin)

admin.site.register(LanguageApiFailureLogs)

admin.site.register(EasyChatMAil)
admin.site.register(BrokenBotMail)

admin.site.register(EasyChatQueryToken)
admin.site.register(GeneralFeedBack)
admin.site.register(ExcelProcessingProgress)
admin.site.register(AutoPopUpClickInfo)
admin.site.register(WelcomeBanner)
admin.site.register(WhatsAppServiceProvider)

admin.site.register(RCSDetails)
admin.site.register(RCSMessageDetails)

admin.site.register(BuiltInIntentIcon)

admin.site.register(VoiceBotProfileDetail)
admin.site.register(VoiceBotConfiguration)
admin.site.register(ViberDetails)

admin.site.register(EasyChatCronjobTracker)
admin.site.register(WhatsAppMenuSection)
admin.site.register(DailyLiveChatAnalytics)

CONSTANT_TREE_NAME = "Tree Name"
CONSTANT_TREE_ID = "Tree ID"


class LiveChatBotChannelWebhookAadmin(admin.ModelAdmin):

    form = LiveChatBotChannelWebhookForm


admin.site.register(LiveChatBotChannelWebhook, LiveChatBotChannelWebhookAadmin)


class EasyChatAccessTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'is_expired',)


admin.site.register(EasyChatAccessToken, EasyChatAccessTokenAdmin)


def generate_display_links(objects, model_name):
    link = ""
    try:
        for index, obj in enumerate(objects):
            obj_name = obj.name
            obj_id = obj.id
            if index != 0:
                link += ", "
            url = reverse("admin:EasyChatApp_" + model_name +
                          "_change", args=[obj_id])
            link += '<a href="%s">%s</a>' % (url, obj_name)
        return mark_safe(link)
    except Exception:  # noqa: F841
        return ""


class ProfileAdmin(admin.ModelAdmin):

    list_display = ('user_id',)
    raw_id_fields = ('bot', 'tree', 'previous_tree')
    search_fields = ('user_id',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Explanation)


class FlowAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('intent_indentifed', 'previous_tree', 'current_tree')


admin.site.register(FlowAnalytics, FlowAnalyticsAdmin)


class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Channel, ChannelAdmin)


class WordMapperAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'similar_words',)


admin.site.register(WordMapper, WordMapperAdmin)


class IntentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_bot_name', 'get_bot_id', 'is_deleted',)
    list_per_page = 500
    list_filter = ("channels",)
    list_filter = ("bots",)
    search_fields = ('name',)

    def get_bot_name(self, instance):
        try:
            link = generate_display_links(instance.bots.all(), "bot")
            return mark_safe(link)
        except Exception:  # noqa: F841
            return ""
    get_bot_name.short_description = "Bot Name"

    def get_bot_id(self, instance):
        try:
            return list(instance.bots.all().values_list('id', flat=True))
        except Exception:  # noqa: F841
            return ""
    get_bot_id.short_description = "Bot ID"


admin.site.register(Intent, IntentAdmin)


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('value',)


admin.site.register(Choice, ChoiceAdmin)


class BotResponseAdmin(admin.ModelAdmin):
    list_display = ('sentence', 'get_tree_name', 'get_tree_id',)

    def get_tree_name(self, instance):
        try:
            link = generate_display_links(instance.tree_set.all(), "tree")
            return mark_safe(link)
        except Exception:  # noqa: F841
            return ""
    get_tree_name.short_description = CONSTANT_TREE_NAME

    def get_tree_id(self, instance):
        try:
            return list(instance.tree_set.all().values_list('pk', flat=True))
        except Exception:  # noqa: F841
            return ""
    get_tree_id.short_description = CONSTANT_TREE_ID

    form = BotResponseEditorForm


admin.site.register(BotResponse, BotResponseAdmin)


class ProcessorAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tree_name', 'get_tree_id',)
    search_fields = ('name',)

    def get_tree_name(self, instance):
        try:
            link = generate_display_links(instance.pre_processor.all(), "tree")
            link += generate_display_links(
                instance.post_processor.all(), "tree")
            link += generate_display_links(
                instance.pipe_processor.all(), "tree")
            return mark_safe(link)
        except Exception:  # noqa: F841
            return ""
    get_tree_name.short_description = CONSTANT_TREE_NAME

    def get_tree_id(self, instance):
        try:
            list1 = list(instance.pre_processor.all(
            ).values_list('pk', flat=True))
            list2 = list(instance.post_processor.all(
            ).values_list('pk', flat=True))
            list3 = list(instance.pipe_processor.all(
            ).values_list('pk', flat=True))
            return list1 + list2 + list3
        except Exception:  # noqa: F841
            return ""
    get_tree_id.short_description = CONSTANT_TREE_ID

    form = ProcessorEditorForm


admin.site.register(Processor, ProcessorAdmin)


class ApiTreeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tree_name', 'get_tree_id', 'apis_used')
    search_fields = ('name',)

    def get_tree_name(self, instance):
        try:
            link = generate_display_links(instance.tree_set.all(), "tree")
            return mark_safe(link)
        except Exception:  # noqa: F841
            return ""
    get_tree_name.short_description = CONSTANT_TREE_NAME

    def get_tree_id(self, instance):
        try:
            return list(instance.tree_set.all().values_list('pk', flat=True))
        except Exception:  # noqa: F841
            return ""
    get_tree_id.short_description = CONSTANT_TREE_ID

    form = ApiTreeEditorForm


admin.site.register(ApiTree, ApiTreeAdmin)


class TreeAdmin(admin.ModelAdmin):

    list_display = ('name', 'get_intent_name', 'get_intent_id',
                    'get_parent_name', 'get_children_name', 'is_deleted',)
    search_fields = ('name',)

    def get_intent_name(self, instance):
        try:
            return list(instance.intent_set.all().values_list('name',
                                                              flat=True))
        except Exception:  # noqa: F841
            return ""
    get_intent_name.short_description = "Intent Name"

    def get_intent_id(self, instance):
        try:
            return list(instance.intent_set.all().values_list('pk', flat=True))
        except Exception:  # noqa: F841
            return ""
    get_intent_id.short_description = "Intent ID"

    def get_parent_name(self, instance):
        try:
            link = generate_display_links(instance.tree_set.all(), "tree")
            return mark_safe(link)
        except Exception:  # noqa: F841
            return ""
    get_parent_name.short_description = "Parent"

    def get_children_name(self, instance):
        try:
            link = generate_display_links(instance.children.all(), "tree")
            return mark_safe(link)
        except Exception:  # noqa: F841
            return ""
    get_children_name.short_description = "Children"


admin.site.register(Tree, TreeAdmin)


class DataAdmin(admin.ModelAdmin):
    list_display = ('user', 'variable', 'value', 'is_cache')
    search_fields = ('user__user_id',)


admin.site.register(Data, DataAdmin)

admin.site.register(Config)


class MISDashboardAdmin(admin.ModelAdmin):
    list_display = ('date',
                    'user_id',
                    'message_received',
                    'bot_response',
                    'intent_name',
                    'channel_name',
                    'api_request_packet',
                    'api_response_packet',
                    'intent_recognized',
                    'is_helpful_field',
                    'feedback_comment',
                    'session_id',
                    'form_data_widget',
                    'category_name',
                    'bot',)


admin.site.register(MISDashboard, MISDashboardAdmin)


class BotAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'is_deleted',)
    list_filter = ('is_uat', )


admin.site.register(Bot, BotAdmin)


class BotChannelAdmin(admin.ModelAdmin):

    list_filter = ('bot', 'channel')
    readonly_fields = ('api_key', )


admin.site.register(BotChannel, BotChannelAdmin)


class LanguageTunedBotChannelAdmin(admin.ModelAdmin):

    list_filter = ('language', 'bot_channel')


admin.site.register(LanguageTunedBotChannel, LanguageTunedBotChannelAdmin)


class LanguageTunedBotAdmin(admin.ModelAdmin):

    list_filter = ('language', 'bot')


admin.site.register(LanguageTunedBot, LanguageTunedBotAdmin)


class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'datetime')
    list_filter = ('user', 'action')


admin.site.register(AuditTrail, AuditTrailAdmin)

admin.site.register(TagMapper)

admin.site.register(Authentication)

admin.site.register(UserAuthentication)

admin.site.register(Language)

admin.site.register(TrainingTemplateSentence)

admin.site.register(TrainingTemplate)

admin.site.register(ProcessorValidator)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user_id',
                    'get_bot_name', 'rating', 'comments')

    def get_bot_name(self, obj):
        try:
            return obj.bot
        except Exception:  # noqa: F841
            return ""

    get_bot_name.short_description = "Bot name"


admin.site.register(Feedback, FeedbackAdmin)

admin.site.register(WordDictionary)


class EasyChatDriveAdmin(admin.ModelAdmin):
    list_display = ('user', 'media_name', 'media_type', 'media_url')
    list_filter = ('user', 'media_type')


admin.site.register(EasyChatDrive, EasyChatDriveAdmin)

admin.site.register(Supervisor)


class TimeSpentByUserAdmin(admin.ModelAdmin):

    list_display = ('user_id', 'start_datetime', 'end_datetime')
    list_filter = ('user_id',)


admin.site.register(TimeSpentByUser, TimeSpentByUserAdmin)

admin.site.register(FormAssist)

admin.site.register(FormAssistAnalytics)

admin.site.register(Category)


class ServiceRequestAdmin(admin.ModelAdmin):

    list_display = ('user', 'customer_name')
    list_filter = ('user',)


admin.site.register(ServiceRequest, ServiceRequestAdmin)

admin.site.register(EasyChatDataCollect)

admin.site.register(EasyChatDataCollectForm)

admin.site.register(EasyChatTheme)


class WhatsAppWebhookAdmin(admin.ModelAdmin):

    form = WhatsAppWebhookForm


admin.site.register(WhatsAppWebhook, WhatsAppWebhookAdmin)

admin.site.register(WhatsAppHistory)


class APIElapsedTimeAdmin(admin.ModelAdmin):

    list_display = ('api_name', 'bot', 'created_at',
                    'api_status', 'api_status_code')


admin.site.register(APIElapsedTime, APIElapsedTimeAdmin)

admin.site.register(LeadGeneration)

admin.site.register(AccessType)

admin.site.register(AccessManagement)

admin.site.register(EmailConfiguration)

admin.site.register(PackageManager)

admin.site.register(AnalyticsMonitoring)

admin.site.register(AnalyticsMonitoringLogs)


class ExportMessageHistoryRequestAdmin(admin.ModelAdmin):

    list_display = ('is_completed', 'bot', 'user', )

    list_filter = ('is_completed', 'bot', 'user', )


admin.site.register(ExportMessageHistoryRequest,
                    ExportMessageHistoryRequestAdmin)

admin.site.register(NPS)

admin.site.register(ImageData)


class ApiIntegrationDetailAdmin(admin.ModelAdmin):
    list_display = ('url',)


admin.site.register(ApiIntegrationDetail, ApiIntegrationDetailAdmin)

admin.site.register(UserSession)


class DailyFlowAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('intent_indentifed', 'previous_tree',
                    'current_tree', 'count')


admin.site.register(DailyFlowAnalytics, DailyFlowAnalyticsAdmin)

admin.site.register(CommonUtilsFile)

admin.site.register(TrafficSources)

admin.site.register(WelcomeBannerClicks)

admin.site.register(EasyChatAppFileAccessManagement)

admin.site.register(SelfSignupUser)

admin.site.register(TelegramDetails)

admin.site.register(GMBDetails)

admin.site.register(AutomatedTestResult)


class MessageAnalyticsDailyAdmin(admin.ModelAdmin):
    list_display = ('date_message_analytics', 'total_messages_count',
                    'answered_query_count', 'unanswered_query_count', 'channel_message', 'bot')


admin.site.register(MessageAnalyticsDaily, MessageAnalyticsDailyAdmin)


class WordCloudAnalyticsDailyAdmin(admin.ModelAdmin):
    list_display = ('date', 'channel', 'bot')


admin.site.register(WordCloudAnalyticsDaily, WordCloudAnalyticsDailyAdmin)


class UnAnsweredQueriesAdmin(admin.ModelAdmin):
    list_display = ('unanswered_message', 'channel', 'bot')


admin.site.register(UnAnsweredQueries, UnAnsweredQueriesAdmin)


class IntuitiveQuestionsAdmin(admin.ModelAdmin):
    list_display = ('intuitive_message_query', 'channel', 'bot')


admin.site.register(IntuitiveQuestions, IntuitiveQuestionsAdmin)


class UniqueUsersAdmin(admin.ModelAdmin):
    list_display = ('date', 'channel', 'bot', 'count')


admin.site.register(UniqueUsers, UniqueUsersAdmin)
admin.site.register(FormWidgetDataCollection)
admin.site.register(AnalyticsExportRequest)


class AutomatedTestProgressAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'bot',)


admin.site.register(AutomatedTestProgress, AutomatedTestProgressAdmin)


class ChunksOfSuggestionsAdmin(admin.ModelAdmin):
    list_display = ('bot',)


admin.site.register(ChunksOfSuggestions, ChunksOfSuggestionsAdmin)


class CSATFeedBackDetailsAdmin(admin.ModelAdmin):
    list_display = ('bot_obj', 'all_feedbacks', 'number_of_feedbacks')


admin.site.register(CSATFeedBackDetails, CSATFeedBackDetailsAdmin)
admin.site.register(WhitelistedEnglishWords)
admin.site.register(EasyChatSessionIDGenerator)
admin.site.register(WhatsAppUserSessionMapper)
admin.site.register(PasswordHistory)
admin.site.register(ResetPassword)


class RequiredBotTemplateAdmin(admin.ModelAdmin):
    list_display = ('bot', 'language', 'placeholder')


admin.site.register(RequiredBotTemplate, RequiredBotTemplateAdmin)

admin.site.register(EasyChatTranslationCache)

admin.site.register(EasyChatSpellCheckerWord)

# Language fine tunning

admin.site.register(LanguageTuningIntentTable)

admin.site.register(LanguageTuningTreeTable)

admin.site.register(LanguageTuningBotResponseTable)

admin.site.register(LanguageTuningChoicesTable)

admin.site.register(GBMSurveyDetails)

admin.site.register(GBMSurveyQuestion)

admin.site.register(GBMCSATMapping)

admin.site.register(EasyChatMailerAnalyticsProfile)

admin.site.register(EasyChatMailerTableParameters)

admin.site.register(EasyChatMailerGraphParameters)

admin.site.register(EasyChatMailerAttachmentParameters)

admin.site.register(EasyChatMailerAuditTrail)

admin.site.register(EasyChatUserAuthenticationStatus)

admin.site.register(GoogleAlexaProjectDetails)

admin.site.register(TwitterChannelDetails)

admin.site.register(SignInProcessor)

admin.site.register(CustomUser)

admin.site.register(IntentTreeHash)

admin.site.register(BotInfo)

admin.site.register(FlowTerminationData)


class SuggestedQueryHashAdmin(admin.ModelAdmin):
    list_display = ("query_text", 'bot')


admin.site.register(SuggestedQueryHash, SuggestedQueryHashAdmin)

admin.site.register(SuggestedQueryInfo)

admin.site.register(FormAssistBotData)

admin.site.register(EasyChatOTPDetails)

admin.site.register(EventProgress)

admin.site.register(FormWidgetFieldProcessor)

admin.site.register(EmojiBotResponse)

admin.site.register(ProfanityBotResponse)

admin.site.register(TrainingData)

admin.site.register(EasyChatAuthToken)

admin.site.register(EasyChatExternalAPIAuditTrail)

admin.site.register(UserFlowDropOffAnalytics)

admin.site.register(CustomIntentBubblesForWebpages)

admin.site.register(BotFusionConfigurationProcessors)

admin.site.register(FusionProcessor)

admin.site.register(WhatsappCatalogueDetails)

admin.site.register(BlockConfig)

admin.site.register(WhatsappCredentialsConfig)

admin.site.register(UserSessionHealth)

admin.site.register(WhatsappCatalogueCart)

admin.site.register(WhatsappCatalogueItems)

admin.site.register(EasyChatFileCaching)

admin.site.register(WhatsAppVendorConfig)

admin.site.register(TwitterTracker)
