Test_var = True

try:
    from django.contrib.auth import get_user_model

    User = get_user_model()

    if User.objects.all():
        Test_var = False
except:
    pass

if Test_var:
    from EasyChatApp.models import *
    from EasyChatApp.constants_icon import *
    from EasyChatApp.constants import DEFAULT_THEME_IMAGE_DICT
    from EasySearchApp.models import *
    from EasyTMSApp.models import *
    from LiveChatApp.models import *
    from EasyAssistApp.models import *
    from CognoMeetApp.models import *
    from CampaignApp.models import *
    from DeveloperConsoleApp.models import *
    from EasyChatApp.utils_bot import get_translated_text
    from EasyChatApp.constants_language import *
    from EasyChatApp.intent_icons_constants import INTENT_ICONS

    # from django.contrib.auth.hashers import make_password

    import os

    from django.contrib.auth import get_user_model

    User = get_user_model()

    cmd = "rm db.sqlite3 EasyChatApp/migrations/00*"
    os.system(cmd)

    cmd = "rm EasySearchApp/migrations/00*"
    os.system(cmd)

    cmd = "rm EasyTMSApp/migrations/00*"
    os.system(cmd)

    cmd = "rm LiveChatApp/migrations/00*"
    os.system(cmd)

    cmd = "rm EasyAssistApp/migrations/00*"
    os.system(cmd)

    cmd = "rm CognoMeetApp/migrations/00*"
    os.system(cmd)

    cmd = "rm EasyAssistSalesforceApp/migrations/00*"
    os.system(cmd)

    cmd = "rm AutomatedAPIApp/migrations/00*"
    os.system(cmd)

    cmd = "rm TestingApp/migrations/00*"
    os.system(cmd)

    cmd = "rm CampaignApp/migrations/00*"
    os.system(cmd)

    cmd = "rm DeveloperConsoleApp/migrations/00*"
    os.system(cmd)

    cmd = "rm AuditTrailApp/migrations/00*"
    os.system(cmd)

    cmd = "python manage.py makemigrations EasyChatApp"
    os.system(cmd)

    cmd = "python manage.py makemigrations"
    os.system(cmd)

    cmd = "python manage.py migrate"
    os.system(cmd)

    user = User.objects.create(username='admin', password='adminadmin', is_bot_invocation_enabled=True,
                               is_staff=True, is_superuser=True, role=BOT_BUILDER_ROLE, status="1", is_chatbot_creation_allowed="1")

    SearchUser.objects.create(user=user)

    Agent.objects.create(user=user, role="admin")

    livechat_category = LiveChatCategory.objects.create(title="Others")

    livechat_user = LiveChatUser.objects.create(user=user, status="1")

    livechat_user.category.add(livechat_category)

    livechat_user.save()

    cobrowse_agent = CobrowseAgent.objects.create(user=user)
    cobrowse_agent.is_switch_allowed = True
    cobrowse_agent.role = "admin"
    cobrowse_agent.save()

    cognomeet_agent = CognoMeetAgent.objects.create(user=user)
    cognomeet_agent.role = "admin"
    cognomeet_agent.save()
    cognomeet_access_token_obj = CognoMeetAccessToken.objects.filter(agent=cognomeet_agent).first()
    cognomeet_agent.access_token = cognomeet_access_token_obj
    cognomeet_agent.save()

    cobrowse_access_token_obj = CobrowseAccessToken.objects.filter(agent=cobrowse_agent).first()
    if cobrowse_access_token_obj:
        cobrowse_access_token_obj.cogno_meet_access_token = str(cognomeet_access_token_obj.key)
        cobrowse_access_token_obj.save()

    Config.objects.create()

    Channel.objects.create(name='Web', icon=WEB_ICON)
    Channel.objects.create(name='GoogleHome', icon=GOOGLE_HOME_ICON)
    Channel.objects.create(name='Alexa', icon=ALEXA_ICON)
    Channel.objects.create(name='WhatsApp', icon=WHATSAPP_ICON)
    Channel.objects.create(name='Android', icon=ANDROID_ICON)
    Channel.objects.create(name='Facebook', icon=FACEBOOK_ICON)
    Channel.objects.create(name='Microsoft', icon=MICROSOFT_ICON)
    Channel.objects.create(name='Telegram', icon=TELEGRAM_ICON)
    Channel.objects.create(name='GoogleBusinessMessages',
                           icon=GOOGLE_BUSINESS_MESSAGES_ICON)
    Channel.objects.create(name='iOS', icon=IOS_ICON)
    Channel.objects.create(name='ET-Source', icon=ET_SOURCE_ICON)
    Channel.objects.create(name='Twitter', icon=TWITTER_ICON)
    Channel.objects.create(name='Instagram', icon=INSTAGRAM_ICON)
    Channel.objects.create(name='GoogleRCS', icon=GOOGLE_RCS_ICON)
    Channel.objects.create(name='Voice', icon=IVR_ICON)
    Channel.objects.create(name='Viber', icon=VIBER_ICON)

    AccessType.objects.create(name="Full Access", value="full_access")
    AccessType.objects.create(name="Intent Related",
                              value="access_intent_related")
    AccessType.objects.create(name="Bot Setting Related",
                              value="access_bot_setting")
    AccessType.objects.create(name="Lead Gen Related", value="access_lead_gen")
    AccessType.objects.create(name="Form Assist Related",
                              value="access_form_assist")
    AccessType.objects.create(name="Self Learning Related",
                              value="access_self_learning")
    AccessType.objects.create(name="Analytics Related",
                              value="access_msg_history_analytics")
    AccessType.objects.create(name="EasyDrive Related",
                              value="access_easydrive")
    AccessType.objects.create(name="Word Mapper Related",
                              value="access_word_mapper")
    AccessType.objects.create(
        name="Create Bot With Excel Related", value="access_create_bot_with_excel")
    AccessType.objects.create(name="Extract FAQ Related",
                              value="access_extract_faq")
    AccessType.objects.create(name="Message History Related",
                              value="access_only_message_history")
    AccessType.objects.create(name="API Analytics Related",
                              value="access_api_analytics")
    AccessType.objects.create(
        name="Categories", value="access_easychat_categories")
    AccessType.objects.create(name="Automated Testing",
                              value="access_automated_testing")
    AccessType.objects.create(name="PDF Searcher",
                              value="access_pdf_searcher")
    AccessType.objects.create(name="Easy Data Collection",
                              value="access_data_collection")

    LiveChatConfig.objects.create(max_customer_count=3)

    WordDictionary.objects.create()

    EasyChatTheme.objects.create(
        name="theme_1", main_page="EasyChatApp/theme1_bot.html", chat_page="EasyChatApp/theme1.html", theme_image_paths=json.dumps(DEFAULT_THEME_IMAGE_DICT["theme_1"]))

    EasyChatTheme.objects.create(
        name="theme_2", main_page="EasyChatApp/theme2_bot.html", chat_page="EasyChatApp/theme2.html", theme_image_paths=json.dumps(DEFAULT_THEME_IMAGE_DICT["theme_2"]))

    EasyChatTheme.objects.create(
        name="theme_3", main_page="EasyChatApp/theme3_bot.html", chat_page="EasyChatApp/theme3.html", theme_image_paths=json.dumps(DEFAULT_THEME_IMAGE_DICT["theme_3"]))

    EasyChatTheme.objects.create(
        name="theme_4", main_page="EasyChatApp/theme4_bot.html", chat_page="EasyChatApp/theme4.html", theme_image_paths=json.dumps(DEFAULT_THEME_IMAGE_DICT["theme_4"]))

    CampaignChannel.objects.create(
        name="Whatsapp Business",
        description="Start engaging with your customers using the most popular messaging app in the world.",
        logo="files/Campaign/whatsapp_channel.svg",
        value="whatsapp",
        order=1,
    )

    CampaignTemplateStatus.objects.create(
        title="approved"
    )

    # default gbmsurvey question
    GBMSurveyQuestion.objects.create(
        question_id="GOOGLE_DEFINED_TASK_COMPLETION", response_score_mapper='{"yes": 5, "no": 1}')

    DeveloperConsoleConfig.objects.create()

    def add_default_language_objects():
        try:
            for language in LANGUAGE_LIST:
                name_in_english = language[0]
                lang = language[1]
                if not Language.objects.filter(lang=lang).exists():
                    display = get_translated_text(
                        name_in_english, lang, EasyChatTranslationCache)

                    language_script_type = "ltr"
                    if lang in ["ar", "he", "fa", "ur", "ps", "sd", "ug", "yi"]:
                        language_script_type = "rtl"

                    Language.objects.create(name_in_english=name_in_english, lang=lang, display=display, language_script_type=language_script_type)

        except Exception as e:
            logger.error("Error in add_default_language_objects: %s", str(e), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    add_default_language_objects()

    WhatsAppServiceProvider.objects.create(
        name="1", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_ameyo_webhook.py")
    # WhatsAppServiceProvider.objects.create(name="2", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_gupshup_webhook.py")
    WhatsAppServiceProvider.objects.create(
        name="3", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_rml_webhook.py")
    # WhatsAppServiceProvider.objects.create(name="4", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_acl_webhook.py")
    # WhatsAppServiceProvider.objects.create(name="5", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_netcore_webhook.py")

    LiveChatWhatsAppServiceProvider.objects.create(
        name="1", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_ameyo_webhook.py")
    # LiveChatWhatsAppServiceProvider.objects.create(name="2", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_gupshup_webhook.py")
    LiveChatWhatsAppServiceProvider.objects.create(
        name="3", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_rml_webhook.py")
    # LiveChatWhatsAppServiceProvider.objects.create(name="4", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_acl_webhook.py")
    # LiveChatWhatsAppServiceProvider.objects.create(name="5", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_netcore_webhook.py")

    CampaignWhatsAppServiceProvider.objects.create(
        name="1", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_ameyo_webhook.py")
    # CampaignWhatsAppServiceProvider.objects.create(name="2", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_gupshup_webhook.py")
    CampaignWhatsAppServiceProvider.objects.create(
        name="3", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_rml_webhook.py")
    # CampaignWhatsAppServiceProvider.objects.create(name="4", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_acl_webhook.py")
    # CampaignWhatsAppServiceProvider.objects.create(name="5", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_netcore_webhook.py")

    for intent_icon in INTENT_ICONS:
        BuiltInIntentIcon.objects.create(
            unique_id=intent_icon[0], icon=intent_icon[1])

    CampaignChannel.objects.create(
        name="Voice Bot",
        description="Start engaging with your customers using the most popular Interactive voice response",
        logo="files/Campaign/voice_bot_channel.svg",
        value="voicebot",
        order=3,
        is_deleted=True,
    )

    CampaignChannel.objects.create(
        name="RCS",
        description="Start engaging with your customers by using the most popular upgraded version of SMS with rich media texts.",
        logo="files/Campaign/google_rcs.svg",
        value="rcs",
        order=2,
        is_deleted=True,
    )
