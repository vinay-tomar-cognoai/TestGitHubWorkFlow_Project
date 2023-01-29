from django.conf.urls import url
from . import views
from . import views_dummy as vd
from . import views_language as views_language
from . import views_webhooks as views_webhooks
from . import views_ios as ios
from . import views_voicebot as views_voicebot
from . import views_external_api as views_external
from . import views_viber
from . import views_two_minute_bot
from . import views_catalogue

urlpatterns = [
    # General ChatBot
    url(r'^$', views.EasyChatHomePage),
    # url(r'^login/', views.Login),  # RenderLogin page
    # url(r'^sales-login/', views.SalesLogin),
    url(r'^logout/', views.Logout, name="logout-api"),  # Logout
    url(r'^set-session-time-limit/', views.SetSessionTimeLimit),
    url(r'^authentication/', views.LoginSubmit),  # Authentication
    url(r'^otp-authentication/', views.LoginOTP),  # OTP-Authentication
    url(r'^resend-multifactor-login-otp/', views.ResendLoginOTP),  # Resend-Authentication-OTP
    url(r'^get-captcha-image/', views.GetCaptchaImage),
    url(r'^check-user-exists/', views.CheckUserExists),
    url(r'^verify-reset-pass-code/', views.VerifyResetPasswordCode),
    url(r'^reset-pass/', views.SaveNewPassword),
    url(r'^get-bot-list/', views.GetBotList),
    # Render Chatbot at Web Page
    url(r'^index/$', views.EasyChatPage),
    url(r'^bot/$', views.EasyChatBotPage),
    url(r'^bot/share/(?P<bot_id>\d+)/$', views.EasyChatShareableBotLink),
    # QueryAPI
    url(r'^query/$', views.Query),
    # IVRQueryAPI
    url(r'^webhook/ivr/$', views.IVRQuery),
    url(r'^webhook/ivr/welcome-message/$', views.GetIVRChannelWelcomeMessage),
    # Google Home Webhook
    url(r'^webhook/googlehome/$', views.GoogleHomeQuery),
    # WhatsApp Webhook
    url(r'^webhook/whatsapp/$', views.WhatsAppQuery),
    # Android Webhook
    url(r'^webhook/android/$', views.AndroidQuery),
    # Alexa Webhook
    url(r'^webhook/alexa/$', views.AlexaQuery),
    # GBM Webhook
    url(r'^webhook/gbm/$', views.GBMQuery),
    # Automated Testing Flow
    url(r'^webhook/automation/query/$', views.QAAutomationTestingToolQuery),
    # Clear User Data API
    url(r'^home/', views.AppHomePage),
    url(r'^clear-user-data/$', views.ClearUserData),
    url(r'^save-easychat-feedback-msg/$', views.SaveEasyChatIntentFeedback),
    url(r'^get-config-params/', views.GetConfigParams),
    url(r'^set-config-params/', views.SetConfigParams),
    url(r'^console/', views.DeveloperConsole),
    url(r'^get-feedback/', views.GetFeedBackStatitics),
    url(r'^get-channel-details/', views.GetChannelDetails),
    url(r'^get-android-channel-details/$', views.GetAndroidChannelDetails),
    url(r'^verify-access-token/$', views.VerifyBotAccessToken),
    url(r'^easychat-drive/$', views.EasyChatDrivePage),
    # Analytics
    url(r'^mis-dashboard/', views.MIS_dashboard),
    url(r'^get-mis-dashboard/', views.GetMISDashboard),
    url(r'^analytics/', views.Analytics),
    url(r'^get-monthly-analytics/', views.GetMonthlyAnalytics),
    url(r'^get-daily-analytics/', views.GetDailyAnalytics),
    url(r'^get-top-intents/', views.GetTopIntents),
    url(r'^exportdata/', views.ExportData),
    url(r'export-nps-data/', views.ExportNPSData),
    url(r'^submit-excel/', views.CreateFAQBot),
    url(r'^get-faq-excel-result/', views.GetFAQExcelResult),
    url(r'^user-filtered/$', views.GetUserFilterDashboard),
    url(r'^nps-analytics/', views.GetNPSAnalytics),
    # Revised Analytics
    url(r'^revised-analytics/$', views.RevisedAnalytics),
    url(r'^get-basic-analytics/$', views.GetBasicAnalytics),
    url(r'^get-frequent-intent/$', views.GetFrequentIntent),
    url(r'^get-recently-unanswered-message/$',
        views.GetRecentlyUnansweredMessage),
    url(r'^get-intuitive-message/$',
        views.GetIntuitiveMessage),
    url(r'^get-category-analytics', views.GetCategoryAnalytics),
    url(r'^get-category-wise-frequent-intent/$',
        views.GetCategoryWiseFrequentIntent),
    url(r'^get-frequent-window-location/$', views.GetFrequentWindowLocation),
    url(r'^get-channel-analytics/$', views.GetChannelAnalytics),
    url(r'^get-user-analytics/$', views.GetUserAnalytics),
    url(r'^get-message-analytics/$', views.GetMessageAnalytics),
    url(r'^get-device-specific-analytics/$', views.GetDeviceSpecificAnalytics),
    url(r'^get-catalogue-combined-analytics/$', views.GetCatalogueCombinedAnalytics),
    url(r'^get-hour-wise-analytics/$', views.GetHourWiseAnalytics),
    # url(r'^export-frequent-intent/$', views.ExportFrequentIntent),
    url(r'^get-session-analytics/$', views.GetSessionAnalytics),
    url(r'^get-word-cloud/', views.GetWordCloudData),
    url(r'^get-form-assist-analytics/$', views.GetFormAssistAnalytics),
    url(r'^export-form-assist-intent/$', views.ExportFormAssistIntent),
    url(r'^export-easychat-nps-excel/$', views.ExportEasyChatNpsExcel),
    url(r'^fetch-intents-of-bot-selected/', views.FetchIntentsOfBotSelected),
    url(r'^match-message-with-intent/', views.MatchMessageWithIntent),
    url(r'^save-form-data/', views.SaveFormData),
    # Conversion Analytics
    url(r'^conversion-analytics/$', views.ConversionAnalytics),
    url(r'^get-conversion-flow-analytics/$', views.GetConversionFlowAnalytics),
    url(r'^get-conversion-intent-analytics/$',
        views.GetConversionIntentAnalytics),
    url(r'^get-conversion-livechat-analytics/$',
        views.GetConversionLivechatAnalytics),
    url(r'^get-conversion-bot-hits-analytics/$',
        views.GetConversionBotHitsAnalytics),
    url(r'^get-conversion-welcome-analytics/$',
        views.GetConversionWelcomeAnalytics),
    url(r'^export-conversion-analytics-excel',
        views.ExportConversionAnalyticsExcel),
    url(r'^get-conversion-node-analytics/', views.GetConversionNodeAnalytics),
    url(r'^get-conversion-dropoff-analytics/',
        views.GetConversionDropOffAnalytics),
    url(r'^get-whatsapp-block-analytics/$',
        views.GetWhatsappBlockAnalytics),
    url(r'^get-whatsapp-catalogue-analytics/$',
        views.GetWhatsappCatalogueAnalytics),
    # Audit Trail
    url(r'^audit-trail/$', views.AuditTrailPage),
    # Supervisor
    url(r'^supervisor/$', views.SupervisorPage),
    url(r'^supervisor/create-bot-manager/$', views.CreateBotManager),
    url(r'^supervisor/remove-bot-manager/(?P<manager_pk>\d+)$',
        views.RemoveBotManager),
    url(r'^supervisor/create-sandbox-user/$', views.CreateSandboxUser),
    url(r'^supervisor/remove-sandbox-user/(?P<user_pk>\d+)$',
        views.RemoveSandboxUser),
    url(r'^supervisor/extend-sandbox-user/$',
        views.ExtendSandboxUser),
    # url(r'^testchatbot/', views.TestChatBot),
    # url(r'^get-test-analysis/', views.GetTestAnalysis),
    # Message-history api
    url(r'^message-history/', views.MessageHistory),
    url(r'^fetch-message-history/', views.FetchMessageHistory),
    url(r'^save-bot-lead-table-metadata/$', views.SaveBotLeadTableMetadata),
    url(r'^mark-flagged-queries/$', views.MarkFlaggedQueries),

    url(r'^automated-testing/', views.AutomatedTest),
    url(r'^get-automated-testing-result/', views.GetAutomatedTestingResult),
    url(r'^get-automated-test-progress/', views.GetAutomatedTestProgress),
    url(r'^stop-automated-testing/', views.StopAutomatedTesting),
    url(r'^re-run-automation-testing-for-single-sentence/',
        views.ReRunAutomatedTesting),
    url(r'^export-automated-testing-excel/', views.ExportAutomatedTest),
    url(r'^get-cluster-details/', views.GetClusterDetails),
    url(r'^create-intent-from-clusters/', views.CreateIntentFromClusters),
    url(r'^user-details/', views.UserDetails),
    url(r'^export-faqs/', views.ExportExcelFAQs),
    url(r'^fetch-faqs/', views.FetchFAQs),
    url(r'^get-mis-user/', views.GetMISUser),

    # Intent Handling
    url(r'^intent/$', views.IntentConsole),
    url(r'^settings/', views.SettingsConsole),
    url(r'^test-chatbot/', views.AutomatedTestConsole),
    url(r'^bot-learning/', views.SelfLearning),
    url(r'^extract-faqs/$', views.ExtractFAQs),
    url(r'^create-intent-from-faqs/', views.CreateIntentFromFAQs),
    url(r'^edit-tree/', views.EditTreeConsole),
    url(r'^edit-intent/', views.EditIntentConsole),
    url(r'^create-intent/', views.CreateIntentConsole),
    url(r'^save-intent/', views.SaveIntent),
    url(r'^save-intent-bot-response', views.SaveBotResponseOfIntent),
    url(r'^save-intent-icon-response', views.SaveIntentIcon),
    url(r'^save-intent-widget-response', views.SaveWidgetResponse),
    url(r'^save-intent-channel', views.SaveIntentChannel),
    url(r'^save-intent-quick-recom', views.SaveIntentQuickRecommendation),
    url(r'^save-intent-order-response/', views.SaveIntentOrderOfResponse),
    url(r'^save-intent-conversion-flow-description/', views.SaveIntentConversionFlowDescription),
    url(r'^save-intent-advance-nlp-config/', views.SaveIntentAdvanceNlpConfig),
    url(r'^save-intent-settings/', views.SaveIntentSettings),
    url(r'^save-intent-whatsapp-menu-format/', views.SaveIntentWhatsappMenuFormat),
    url(r'^delete-intent/', views.DeleteIntent),
    url(r'^insert-files-intent/', views.InsertFileIntoIntent),
    url(r'^fetch-intent-information/', views.FetchIntentInformation),
    url(r'^fetch-all-intents/', views.FetchAllIntents),
    url(r'^fetch-intent-tree-structure/', views.FetchIntentTreeStructure),
    url(r'^rename-tree/', views.RenameTree),
    url(r'^delete-tree/', views.DeleteTree),
    url(r'^delete-tree-node/', views.DeleteTreeNode),
    url(r'^paste-tree-node/', views.PasteTreeNode),
    url(r'^create-tree/', views.CreateTree),
    url(r'^insert-tree/', views.InsertTree),
    url(r'^fetch-tree-information/', views.FetchTreeInformation),
    url(r'^fetch-choices/', views.FetchAllChoice),
    url(r'^add-new-choice/', views.AddNewChoice),
    url(r'^save-tree/', views.SaveTree),
    url(r'^save-flow/', views.SaveFlow),
    url(r'^save-tree-response/', views.SaveTreeResponse),
    url(r'^save-tree-widget/', views.SaveTreeWidget),
    url(r'^save-tree-settings/', views.SaveTreeSettings),
    url(r'^save-tree-recommendation/', views.SaveTreeQuickRecommendation),
    url(r'^save-tree-order-response/', views.SaveTreeOrderOfResponse),
    url(r'^save-tree-conversion-flow-description/', views.SaveTreeConversionFlowDescription),
    url(r'^save-tree-whatsapp-menu-format/', views.SaveTreeWhatsappMenuFormat),
    url(r'^save-whatsapp-menu-section/', views.SaveWhatsAppMenuSection),
    url(r'^delete-whatsapp-menu-section/', views.DeleteWhatsAppMenuSection),
    url(r'^create-faq/', views.Edit),
    url(r'^create-quick-bot/', views.CreateQuickBotConsole),
    # url(r'^move-bot-to-prod/$', views.MoveBotToProduction),
    url(r'^deploy-chatbot/$', views.DeployChatBot),
    url(r'^enable-small-talk/$', views.EnableSmallTalk),
    url(r'^disable-small-talk/$', views.DisableSmallTalk),
    url(r'^create-flow-excel/', views.CreateFlowExcel),
    url(r'^easychat-api-analytics/$', views.EasyChatAPIAnalytics),
    url(r'^easychat-api-statistics/$', views.EasyChatAPIStatistics),
    url(r'^download-api-analytics-data/$', views.DownloadAPIAnalyticsData),
    url(r'^nlp-benchmark/', views.NLPBenchmarkConsole),
    url(r'^get-nlp-benchmarking-result/', views.GetNLPBenchmarkingResult),
    url(r'^start-nlp-benchmarking/', views.NLPBenchmarking),
    url(r'^resave-all-intents/', views.ResaveAllIntents),
    url(r'^add-training-questions/', views.AddTrainingQuestions),
    url(r'^add-intent-icon/', views.AddIntentIcon),
    url(r'^remove-intent-icon/', views.RemoveIntentIcon),
    # Saving Feedback
    url(r'^save-feedback/', views.SaveFeedback),

    ##########################################################
    # Saving TimeSpent
    url(r'^save-time-spent/', views.SaveTimeSpent),
    url(r'^get-user-time-spent/', views.GetUserTimeSpent),
    ##########################################################
    url(r'^webhook/facebook/$', views.FacebookWebhook),
    url(r'^get-user-details/', views.GetUserDetails),
    url(r'^upload-image/', views.UploadImage),
    url(r'^duplicate-image/', views.DuplicateImage),
    url(r'^upload-file-card/', views.UploadFileCard),
    url(r'^upload-images-on-server/', views.UploadImagesOnServer),
    ###########################################
    url(r'^categories/', views.CategoryPage),
    url(r'^save-category/', views.SaveCategory),
    url(r'^delete-category/', views.DeleteCategory),
    ##################################################
    # Channels
    # url(r'^channels/$', views.ChannelsPage),
    url(r'^channels/edit/(?P<bot_pk>\d+)/$', views.EditChannels),
    url(r'^channels/web/$', views.WebChannel),
    url(r'^channels/web/edit/$', views.EditWebChannelDetails),
    url(r'^channels/web/save/$', views.SaveWebChannelDetails),
    url(r'^channels/google-assistant/$', views.GoogleAssistantChannel),
    url(r'^channels/google-assistant/edit/$', views.EditGoogleChannelDetails),
    url(r'^channels/google-assistant/save/$',
        views.SaveGoogleHomeChannelDetails),
    url(r'^add-google-alexa-project-details/$',
        views.AddGoogleAlexaProjectDetails),
    url(r'^channels/google-buisness-messages/$',
        views.GoogleBusinessMessagesChannel),
    url(r'^channels/google-buisness-messages/edit/$',
        views.EditGoogleBusinessMessagesDetails),
    url(r'^channels/google-buisness-messages/save/$',
        views.SaveGoogleBusinessMessagesChannelDetails),
    url(r'^upload-gmb-credential-file/$', views.UploadGMBCredentialFile),
    url(r'^channels/alexa/$', views.AlexaChannel),
    url(r'^channels/alexa/edit/$', views.EditAlexaChannelDetails),
    url(r'^channels/alexa/save/$', views.SaveAlexaChannelDetails),
    url(r'^channels/android/$', views.AndroidChannel),
    url(r'^channels/android/edit/$', views.EditAndroidChannelDetails),
    url(r'^channels/android/save/$', views.SaveAndroidChannelDetails),
    url(r'^channels/whatsapp/$', views.WhatsAppChannel),
    url(r'^channels/whatsapp/edit/$', views.EditWhatsAppChannelDetails),
    url(r'^channels/whatsapp/save/$', views.SaveWhatsAppChannelDetails),
    url(r'^save-whatsapp-email-config/$', views.SaveWatsAppEmailConfig),
    url(r'^send-whatsapp-test-email/$', views.SendWhatsAppTestEmail),
    url(r'^webhook/google-home/auth/(?P<bot_id>\d+)/', views.RenderGAAuthPage),
    url(r'^get-google-assistant-auth-otp/$', views.GetGoogleAssistantAuthOTP),
    url(r'^verify-google-assistant-otp/$', views.VerifyGoogleAssistantAuthOTP),
    url(r'^channels/facebook/$', views.FacebookChannel),
    url(r'^channels/facebook/edit/$', views.EditFacebookChannelDetails),
    url(r'^channels/facebook/save/$', views.SaveFacebookChannelDetails),
    url(r'^channels/microsoft-teams/$', views.MSTeamsChannel),
    url(r'^channels/microsoft-teams/save/$', views.SaveMSTeamsChannelDetails),
    url(r'^webhook/microsoft-teams/$', views.MSTeamsQuery),
    url(r'^channels/ms-teams/download-config/$', views.MSTeamsDownloadConfig),

    url(r'^channels/instagram/$', views.InstagramChannel),
    url(r'^channels/instagram/save/$', views.SaveInstagramChannelDetails),
    url(r'^webhook/instagram/$', views.InstagramQuery),

    url(r'^channels/google-rcs/$', views.RCSChannel),
    url(r'^webhook/rcs/$', views.RCSQuery),
    url(r'^channels/google_rcs/save/$', views.SaveGoogleRCSChannelDetails),
    url(r'^upload-rcs-credential-file/$', views.UploadRCSCredentialFile),


    url(r'^channels/twitter/$', views.TwitterChannel),
    url(r'^channels/twitter/save/$', views.SaveTwitterChannelDetails),
    url(r'^channels/twitter/subscribe-webhook/$', views.TwitterSubscribeWebhook),
    url(r'^channels/twitter/delete-webhook/$', views.TwitterDeleteWebhook),
    url(r'^channels/twitter/reset-config/$', views.TwitterResetConfig),
    url(r'^webhook/twitter/$', views.TwitterQuery),

    url(r'^channels/voice/$', views_voicebot.VoiceChannel),
    url(r'^channels/voice/save/$', views_voicebot.SaveVoiceChannelDetails),
    url(r'^channels/voice/add-repeat-variation/', views_voicebot.AddRepeatVariations),
    url(r'^channels/voice/delete-repeat-variation/', views_voicebot.DeleteRepeatVariations),
    url(r'^channels/voice/add-caller/', views_voicebot.SaveVoiceBotCaller),
    url(r'^channels/voice/delete-caller/', views_voicebot.DeleteVoiceBotCaller),
    
    ########################      VIBER          ############################
    url(r'^channels/viber/$', views_viber.ViberChannel),
    url(r'^channels/viber/save/$', views_viber.SaveViberChannelDetails),
    url(r'^viber/set-webhook/$', views_viber.ViberWebhookSetup),
    url(r'^webhook/viber/$', views_viber.ViberQuery),

    url(r'^image-crop/$', views.CropAndSaveImage),
    url(r'^get-image-data/$', views.GetImageData),
    url(r'^set-image-data/$', views.SetImageData),
    url(r'^channels/save-web-landing/$', views.SaveWebLanding),
    url(r'^channels/edit-web-landing/$', views.EditWebLanding),
    url(r'^channels/delete-web-landing/$', views.DeleteWebLanding),
    # url(r'^channels/android/$', views.AndroidChannel),
    # url(r'^channels/android/edit/$', views.EditAndroidChannelDetails),
    # url(r'^channels/android/save/$', views.SaveAndroidChannelDetails),
    # Applicant Details Verification
    # url(r'^verify-details/$', views.VerificationOfDetails),
    ####################################################
    url(r'^get-data/', views.GetTrainingData),
    url(r'^get-intents/', views.GetIntentNames),
    url(r'^generate-campaign-link/$', views.GenerateCampaignLink),
    ####################################################
    # export and imoort functionality
    url(r'^export-import/(?P<bot_pk>\d+)/$', views.ExportImportBot),
    url(r'^easysearch/edit/(?P<bot_pk>\d+)/$', views.EditEasySearch),
    # Two Minute Bot
    url(r'^two-minute-bot/update-config', views_two_minute_bot.TwoMinuteBotConfig),
    url(r'^two-minute-bot/create/$', views_two_minute_bot.CreateBotWithNameImage),
    url(r'^two-minute-bot/bot-name-validate', views_two_minute_bot.ValidateBotName),
    url(r'^two-minute-bot/update-language', views_two_minute_bot.UpdatingChannelLanguage),
    # Bots
    url(r'^bots/$', views.BotConsole),
    url(r'^bots-details/$', views.BotsLists),
    url(r'^bot/delete/$', views.DeleteBot),
    url(r'^bot/save/$', views.SaveBot),
    url(r'^bot/save-mulitlingual-bot/$', views.SaveMultilingualBot),
    url(r'^bot/edit/(?P<bot_pk>\d+)/$', views.EditBot),
    url(r'^bot/pdf-searcher/$', views.PDFSearcher),
    url(r'^bot/get-active-pdf/$', views.GetActivePDF),
    url(r'^bot/upload-pdf/$', views.UploadPDF),
    url(r'^bot/delete-pdf/$', views.DeletePDF),
    url(r'^bot/update-pdf/$', views.UpdatePDF),
    url(r'^bot/export-pdf-search-report/$', views.ExportPDFSearchReport),
    url(r'^bot/pdf/start-indexing/$', views.StartIndexing),
    url(r'^bot/get-general-details/$', views.GetGeneralDetails),
    url(r'^bot/share/$', views.ShareBot),
    url(r'^bot/unshare/$', views.UnShareBot),
    url(r'^bot/export/(?P<bot_pk>\d+)/$', views.ExportBot),
    url(r'^bot/export-intent/(?P<intent_pk>\d+)/$', views.ExportIntent),
    url(r'^bot/export-faq/(?P<bot_pk>\d+)/$', views.ExportFAQExcel),
    url(r'^bot/import/$', views.ImportBot),
    url(r'^bot/track-event-progress/', views.TrackEventProgress),
    url(r'^bot/import-mulitlingual-intents-from-excel/$',
        views.ImportMultilingualIntentsFromExcel),
    url(r'^bot/import-intent/$', views.ImportIntent),
    url(r'^save-bot-image/', views.SaveBotImage),
    url(r'^save-bot-message-image/', views.SaveBotMessageImage),
    url(r'^save-bot-logo/', views.SaveBotLogo),
    url(r'^bot/delete-bot-image/', views.DeleteBotImage),
    url(r'^bot/delete-message-image/(?P<bot_pk>\d+)/$', views.DeleteMessageImage),
    url(r'^bot/delete-bot-logo/(?P<bot_pk>\d+)/$', views.DeleteBotLogo),
    url(r'^get-bot-image/', views.GetBotImage),
    url(r'^get-bot-message-image/', views.GetBotMessageImage),
    url(r'^submit-bot-advance-settings/', views.SubmitBotAdvanceSettings),
    url(r'^change-bot-theme-color/', views.ChangeBotThemeColor),
    url(r'^fetch-botresponse-information/', views.FetchBotResponseInformation),
    url(r'^bot/export-as-zip/(?P<bot_pk>\d+)/$', views.ExportBotAsZip),
    url(r'^bot/export-multilingual-intents-as-excel/(?P<bot_pk>\d+)/$',
        views.ExportMultilingualIntentsAsExcel),
    url(r'^bot/export-alexa-json/(?P<bot_pk>\d+)/$', views.ExportAlexaJSON),
    url(r'^bot/export-large-bot/', views.ExportLargeBot),
    url(r'^bot/import-bot-zip/$', views.ImportBotFromZip),
    url(r'^save-email-config/$', views.SaveEmailConfiguration),
    url(r'^send-test-mail/$', views.SendTestEmailBasedConfiguration),
    url(r'^save-analytics-monitorig-setting/$',
        views.SaveAnalyticsMonitoringSetting),
    url(r'^save-api-fail-email-config/$', views.SaveAPIFailEmailConfig),
    url(r'^save-bot-fail-email-config/$', views.SaveBotFailEmailConfig),
    url(r'^send-api-fail-test-email/$', views.SendAPIFailTestEmail),
    url(r'^send-bot-break-test-email/$', views.SendBotBreakFailTestEmail),
    url(r'^bot/save-font/$', views.SaveBotFont),
    url(r'^save-stop-words/', views.SaveStopWords),
    url(r'^bot/data-mask-toggle/$', views.DataMaskToggle),
    url(r'^bot/check-data-toggle-otp/$', views.CheckDataToggleOtp),

    #############################################

    url(r'^voicebot/(?P<bot_id>\d+)/initialize$',
        views_voicebot.VoiceBotInitializeAPI),
    url(r'^voicebot/(?P<bot_id>\d+)/event/(?P<session_id>[a-zA-Z0-9- ]+)$',
        views_voicebot.VoiceBotEventAPI),
    url(r'^voicebot/(?P<bot_id>\d+)/query/(?P<session_id>[a-zA-Z0-9- ]+)$',
        views_voicebot.VoiceBotQueryAPI),

    #############
    url(r'^api/share/$', views.ShareAPI),
    #############
    # Testing Module
    url(r'^add-test-sentence/', views.AddTestSentence),
    url(r'^get-test-sentences/', views.GetTestSentence),
    url(r'^set-test-sentence-active/', views.SetTestSentenceActive),
    url(r'^delete-test-sentence/(?P<test_case_pk>\d+)/(?P<sentence>[a-zA-Z0-9_ ]+)/$',
        views.DeleteTestSentence),
    #############
    # Intent Templates
    url(r'^training-sentence-templates/', views.TrainingSentence),
    ##############
    url(r'^easychat-licence/$', views.GetEasyChatLicence),
    url(r'^upload-files-into-drive/$', views.UploadFilesIntoDrive),
    url(r'^delete-files-drive/$', views.RemoveFilesFromDrive),
    url(r'^get-intent-list-drive/$', views.GetIntentListDrive),
    # FormAssist
    url(r'^form-assist-response/$', views.FormAssistResponse),
    url(r'^form-assist/$', views.FormAssistPage),
    url(r'^save-tag/$', views.SaveFormAssistTag),
    url(r'^edit-tag/$', views.EditFormAssistTag),
    url(r'^delete-tag/$', views.DeleteFormAssistTag),
    url(r'^get-form-assist-tags/$', views.GetFormAssistTags),
    # Upload data
    # url(r'^upload-attachment/$', views.UploadAttachment),
    url(r'^trigger-intent/$', views.TriggerIntent),
    url(r'^save-image-locally/$', views.SaveImageLocally),
    # Service Request
    url(r'^save-deployment-request/$', views.SaveDeploymentRequest),
    # LeadGeneration
    url(r'^lead-generation/$', views.LeadGenerationPage),
    # DataCollect
    url(r'^bot-data-collect/$', views.EasyChatDataCollectPage),
    url(r'^save-collect-form-data/$', views.SaveEasyChatDataCollect),
    url(r'^show-data-collect/$', views.ShowEasyChatDataCollection),
    url(r'^delete-data-collect/$', views.DeleteEasyChatDataCollect),
    url(r'^download-excel-data-collect/$', views.DownloadDataCollectionAsExcel),
    url(r'^save-data-collect-form-ui-data/$',
        views.SaveEasyChatDataCollectForm),
    # Edit Static File Functionality
    url(r'^edit-static/$', views.EditStaticPage),
    url(r'^load-static-file/$', views.LoadStaticFile),
    url(r'^save-static-file/$', views.SaveStaticFile),
    url(r'^log-analytics/$', views.LogAnalytics),
    url(r'^update-log-file/$', views.UpdateLogFile),
    url(r'^download-easychat-logs/$', views.DownloadEasyChatLogs),

    ########################  API Integration in console ###################
    url(r'^edit-processor/$', views.ProcessorConsole),
    url(r'^package-installer/$', views.PackageInstaller),
    url(r'^save-processor-content/$', views.SaveProcessorContent),
    url(r'^delete-processor-content/$', views.DeleteProcessorContent),
    url(r'^submit-package-install-request/$',
        views.SubmitPackageInstallRequest),
    url(r'^take-action-package-install/$', views.TakeActionPackageInstallation),
    url(r'^easychat-processor-run/$', views.EasyChatProcessorRun),
    url(r'^processor-language-change/$', views.ProcessorLanguageChange),
    url(r'^data-model-entries/$', views.DataModelEntries),
    url(r'^decrypt-data-model-values/$', views.DecryptDataModelValues),
    url(r'^whatsapp-webhook-console/$', views.WhatsAppWebHookConsole),
    url(r'^whatsapp-webhook-function-console/$',
        views.WhatsAppWebhookFunctionConsole),
    url(r'^save-whatsapp-webhook-function-code/$',
        views.SaveWhatsAppWebhookFunction),
    url(r'^save-whatsapp-webhook-content/$', views.SaveWhatsAppWebhookContent),
    url(r'^whatsapp-history/$', views.WhatsAppWebhookHistory),
    url(r'^whatsapp-simulator/$', views.WhatsAppSimulator),
    url(r'^get-whatsapp-simulator-response/$',
        views.GetWhatsAppSimulatorResponse),
    ################## Variations Beta ############################
    url(r'^get-variations/$', views.GetVariations),
    ################## Dummy API urls ############################
    url(r'^oauth/dummy-token/$', vd.dummy_return_access_token),
    url(r'^fetch-dummy-data/$', vd.FetchDummyDataAPI.as_view()),
    url(r'^fetch-dummy-soap-data/$', vd.FetchSoapDataAPI.as_view()),
    url(r'^oauth/access-token/$', vd.AccessTokenAPI.as_view()),
    url(r'^fetch-balance/$', vd.FetchDummyBalanceAPI.as_view()),
    url(r'^fetch-valuation/$', vd.FetchValuationAPI.as_view()),
    ############### Get Previous Session Data ####################
    url(r'^get-previous-session-data/$', views.GetPreviousSessionResponse),
    ################# Common settings file #######################
    url(r'^common-utils/', views.CommonUtils),
    ################ API Integration Feature #####################
    url(r'^api-integration/', views.AccessTokenForAPI),
    url(r'^request-response-trees/$', views.RequestResponseTree),
    url(r'^save-api-code/$', views.GenerateApiCode),
    ############### SSO METADATA PAGE ############################
    url(r'^sso-metadata/', views.SsoMetaData),
    url(r'^sso-data-functionality/', views.SsoMetaFileFunctionality),
    ############### FLOW ANALYTICS FUNCTIONALITY #####################
    url(r'^flow-analytics/$', views.FlowAnalyticsView),
    url(r'^download-flow-analytics/$', views.DownloadUserAnalyticsExcel),
    url(r'^download-user-specific-dropoff-analytics/$',
        views.DownloadUserSpecificDropoff),
    url(r'^get-flow-analytics-intent/$', views.FlowAnalyticsStats),
    ############## API LIST USED #####################################
    url(r'^api-list-collection/$', views.APIList),
    url(r'^upload-attachment/$', views.UploadAttachment),
    ####################### Secured Files Access #####################
    url(r'^download-file/(?P<file_key>[a-zA-Z0-9-_]+)/(?P<file_name>[a-zA-Z0-9-_. ()]+)/$', views.FileAccess),
    url(r'^chatbot-custom-js/$', views.ChatbotCustomJs),
    url(r'^save-custom-chatbot-js/$', views.SaveChatbotCustomJs),
    url(r'^chatbot-custom-css/$', views.ChatbotCustomCss),
    url(r'^save-custom-chatbot-css/$', views.SaveChatbotCustomCss),
    url(r'^landing-page/$', views.LandingPage),
    url(r'^channels/save-web-landing-initial-messages/$',
        views.SaveWebLandingInitialMessages),
    url(r'^export-traffic-source/$', views.DownloadTrafficSources),

    ####################### Android APIs ##############################

    url(r'^get-android-training-data/$', views.GetAndroidTrainingData),
    url(r'^get-android-bot-message-image/', views.GetAndroidBotMessageImage),
    url(r'^save-android-form-data/', views.SaveAndroidFormData),
    url(r'^save-easychat-android-feedback-msg/$',
        views.SaveEasyChatAndroidIntentFeedback),
    url(r'^save-android-feedback/', views.SaveAndroidFeedback),
    url(r'^clear-android-user-data/$', views.ClearAndroidUserData),
    url(r'^save-android-time-spent/', views.SaveAndroidTimeSpent),


    ####################### Telegram Integration ##############################

    url(r'^webhook/telegram/$', views.TelegramQuery),
    url(r'^channels/telegram/$', views.TelegramChannel),
    url(r'^channels/telegram/edit/$', views.EditTelegramChannelDetails),
    url(r'^channels/telegram/save/$', views.SaveTelegramChannelDetails),
    url(r'^telegram/set-webhook/$', views.TelegramWebhookSetup),

    ####################### ET Source Integration ############################

    url(r'^channels/et-source/$', views.ETSourceChannel),
    url(r'^channels/etsource/edit/$', views.EditETSourceChannelDetails),
    url(r'^channels/etsource/save/$', views.SaveETSourceChannelDetails),
    url(r'^webhook/et-source/$', views_webhooks.ETSourceWebhookQuery),
    url(r'^webhook/et-source/welcome-message/$',
        views_webhooks.ETSourceWelcomeMessage),

    ####################### Self SignUp Integration ##########################
    url(r'^login/$', views.Login),
    url(r'^redirect-login/$', views.RedirectLogin),
    url(r'^password-setup/$', views.PasswordSetup),
    url(r'^success-login/$', views.SuccessLogin),
    url(r'^signup/$', views.Signup),
    url(r'^resend-link/$', views.Resend),
    ##################### Download Form Data #################################
    url(r'^download-form-data-excel', views.DownloadFormDataExcel),
    url(r'^form-widget-reports', views.FormWidgetData),
    url(r'^download-consolidated-form-data',
        views.DownloadParticularFormConsolidatedUsers),
    url(r'^export-analytics-in-excel-individual',
        views.ExportAnalyticsExcelIndividual),
    url(r'^exportdata-analytics', views.ExportDataAnalytics),
    url(r'^get-data-suggestions', views.GetTrainingDataSuggestions),
    url(r'^save-csat-form', views.SaveCSATFeedback),

    ################## chatbot session management ######################
    url(r'^update-last-seen-chatbot/$', views.UpdateLastSeenChatbot),
    url(r'^access-file/(?P<file_key>[a-zA-Z0-9-_]+)/$', views.BotFileAccess),

    ################# Multilingual bot section  ########################
    url(r'^get-language-template/$', views.GetLanguageTemplate),
    url(r'^get-language-updated-bot-items/$', views.GetLanguageUpdatedBotItems),
    url(r'^get-language-updated-form-assist-details/$',
        views.GetLanguageUpdatedFormAssistDetails),

    ################# Word Mapper section  ########################
    url(r'^word-mappers/', views.WordMapperConsole),
    url(r'^save-word-mappers/', views.SaveWordMapper),
    url(r'^get-word-mappers/', views.GetWordMapper),
    url(r'^delete-word-mapper/(?P<pk>\d+)/$', views.DeleteWordMapper),
    url(r'^download-word-mapper-template/',
        views.DownloadWordMapperExcelTemplate),
    url(r'^upload-word-mappers/', views.UploadWordMapperExcel),

    ##########################################################
    # Saving BotClickCount
    url(r'^save-bot-click-count/', views.SaveBotClickCount),

    ###########################################################
    # Saving Welcome Banner Click Count
    url(r'^save-welcome-banner-click-count/',
        views.SaveWelcomeBannerClickCount),

    ##########################################################
    # Build Bot
    url(r'^update-need-to-build-bot/', views.UpdateNeedToBuildBot),
    url(r'^build-bot/', views.BuildBot),

    ##################################################################
    # Language Configuration
    url(r'^get-language-constant-keywords/',
        views_language.GetLanguageConstantKeywords),
    url(r'^delete-language-from-supported-languages/',
        views_language.DeleteLanguageFromSupportedLanguages),
    url(r'^update-language-constant-keywords/',
        views_language.UpdateLanguageConstantKeywords),
    # url(r'^send-otp-for-language-configuration/', views_language.SendOtpForLanguageConfiguration),
    # Language fine tunning
    url(r'^save-channel-language-tuned-objects/',
        views.SaveChannelLanguageTunedObjects),
    url(r'^channels/edit-web-landing-for-non-primary-language/',
        views.EditWebLandingForNonPrimaryLanguage),
    url(r'^ignore-changes-in-non-primary-languages/',
        views.IgnoreChangesInNonPrimaryLanguage),
    url(r'^auto-fix-changes-in-non-primary-languages/',
        views.AutoFixChangesInNonPrimaryLanguage),
    url(r'^update-selected-language/', views_language.UpdateSelectedLanguage),
    url(r'^update-selected-language-intent/',
        views_language.UpdateSelectedLanguageIntent),
    url(r'^edit-intent-multilingual/', views.EditIntentMultilingualConsole),
    url(r'^edit-tree-multilingual/', views.EditMultilingualTreeConsole),
    url(r'^save-multilingual-intent/', views.SaveMultilingualIntent),
    url(r'^save-multilingual-tree/', views.SaveMultilingualTree),
    url(r'^check-selected-language-is-supported/',
        views_language.CheckSelectedLanguageIsSupported),
    url(r'^ignore-bot-response-changes-in-non-primary-languages/',
        views_language.IgnoreBotResponseChangesInNonPrimaryLanguage),
    url(r'^auto-fix-bot-response-changes-in-non-primary-languages/',
        views_language.AutoFixBotResponseChangesInNonPrimaryLanguage),
    url(r'^get-excel-processing-progress/', views.GetExcelProcessingProgress),
    url(r'^ignore-bot-configuration-changes-in-non-primary-languages/',
        views_language.IgnoreBotConfigurationChangesInNonPrimaryLanguage),
    url(r'^auto-fix-bot-configuration-changes-in-non-primary-languages/',
        views_language.AutoFixBotConfigurationChangesInNonPrimaryLanguage),
    ##########################################################
    # Mailer Analytics
    url(r'^save-mailer-profile/', views.SaveMailerProfile),
    url(r'^delete-mailer-profile/', views.DeleteMailerProfile),
    ##################################################
    url(r'^edit-signin-processor-console/$', views.SignInProcessorConsole),
    url(r'^save-signin-processor-content/$', views.SaveSignInProcessorContent),
    url(r'^edit-console-page/$', views.EditConsolePage),

    # Alexa
    url(r'^webhook/alexa/auth/(?P<bot_id>\d+)/$', views.RenderAlexaAuthPage),
    # User nudge analytics data
    url(r'^save-bubble-click-info/$', views.SaveBubbleClickInfo),
    url(r'^get-user-nudge-analytics/$', views.GetUserNudgeAnalytics),
    url(r'^export-user-nudge-analytics/$', views.ExportUserNudgeAnalytics),
    # Edit bot manager access
    url(r'^get-manager-access-details/$', views.GetBotManagerAccessDetails),

    # iOS
    url(r'^channels/ios/$', ios.IOSChannel),
    url(r'^channels/ios/edit/$', ios.EditIOSChannelDetails),
    url(r'^channels/ios/save/$', ios.SaveIOSChannelDetails),

    url(r'^pdf/redirect/(?P<pdf_search_key>[a-zA-Z0-9-_]+)/(?P<page_number>\d+)/$',
        views.EasySearchPDFRedirect),
    url(r'^pdf/show/(?P<pdf_search_key>[a-zA-Z0-9-_]+)/(?P<page_number>\d+)/$',
        views.EasySearchPDFRender),

    # VoIP
    url(r'^customer-voice-meeting/', views.CustomerVoiceMeeting),
    url(r'^customer-meeting-end/', views.CustomerVoIPMeetingEnded),

    # Welcome Banner
    url(r'^save-welcome-banner/$', views.SaveWelcomeBanner),
    url(r'^edit-welcome-banner/$', views.EditWelcomeBanner),
    url(r'^delete-welcome-banner/$', views.DeleteWelcomeBanner),

    # Get Intent Information
    url(r'^get-intent-information/$', views.GetIntentInformation),
    url(r'^test-external-function/$', views.TestExternalFunction),

    # Whatsapp BSP
    url(r'^get-wa-webhook-default-code/$', views.GetWhatsAppWebhookDefaultCode),

    # AMP
    url(r'^amp/$', views.GetAMP),
    url(r'^get-amp-js/$', views.GetAMPJS),
    url(r'^get-amp-bot-image/(?P<bot_id>\d+)/$', views.GetAMPBotImage),

    # Forgot password
    url(r'^forgot-password-resend-otp/$', views.ForgotPasswordResendOTP),
    url(r'^forgot-password-verify-otp/$', views.ForgotPasswordVerifyOTP),
    url(r'^save-reseted-password-for-forgot-password/$',
        views.SaveResetedForgotPassword),
    url(r'^reset-forgot-password/$', views.ResetForgotPassword),

    # Dynamic Form Widget
    url(r'^field-processor/$', views.FieldProcessorConsole),
    url(r'^update-form-widget-dependent-fields/$', views.UpdateFormWidgetDependentFields),
    url(r'form-widget-api-integration-status/$', views.FormWidgetAPIIntegrationStatus),
    url(r'reset-api-integration/$', views.ResetFormWidgetAPIIntegration),

    # External Exposed APIs
    url(r'^external/get-auth-token/', views_external.GetAuthToken),
    url(r'^external/get-analytics-external/', views_external.GetAnalyticsExternal),

    # Chatbot Api Documentaion
    url(r'^easychat-api-documentation/', views_external.EasyChatAPIDocumentation),

    # Custom intents for webpages APIs
    url(r'^channels/save-custom-intents/$', views.SaveCustomIntents),
    url(r'^channels/edit-custom-intents/$', views.EditCustomIntents),
    url(r'^channels/delete-custom-intents/$', views.DeleteCustomIntents),

    # Ameyo Fusion Processor Editor
    url(r'^fusion-editor/$', views.FusionEditor),
    url(r'^save-fusion-config/$', views.SaveFusionConfig),
    url(r'^save-fusion-processor/$', views.SaveFusionProcessor),

    # WhatsApp Catalogue APIs
    url(r'^channels/whatsapp/get-catalogue-details/$', views_catalogue.GetCatalogueDetails),
    url(r'^channels/whatsapp/get-catalogue-products/$', views_catalogue.GetCatalogueProducts),
    url(r'^channels/whatsapp/catalogue-products/$', views_catalogue.CatalogueProducts),
    url(r'^channels/whatsapp/catalogue-manager/$', views_catalogue.WhatsappCatalogueManager),
    url(r'^channels/whatsapp/delete-catalogue-products/$', views_catalogue.DeleteCatalogueProducts),
    url(r'^channels/whatsapp/update-catalogue-product/$', views_catalogue.UpdateCatalogueProduct),
    url(r'^channels/whatsapp/add-catalogue-details/$', views_catalogue.AddCatalogueDetails),
    url(r'^channels/whatsapp/upload-products-csv/$', views_catalogue.UploadProductsCSV),
    url(r'^channels/whatsapp/download-catalogue-csv-template/$', views_catalogue.DownloadCatalogueCSVTemplate)
]
