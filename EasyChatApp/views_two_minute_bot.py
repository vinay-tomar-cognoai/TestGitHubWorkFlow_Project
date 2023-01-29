from EasyChatApp.utils_validation import EasyChatInputValidation
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_bot import *
from EasyChatApp.utils_build_bot import update_word_dictionary
from EasyChatApp.utils_processor_validator import create_default_processor_validators


class ValidateBotNameAPI(APIView):
    
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()
            bot_name = validation_obj.remo_html_from_string(
                data["bot_name"])
            bot_name = validation_obj.remo_unwanted_characters(bot_name)
            bot_id = validation_obj.remo_html_from_string(
                data["bot_id"])

            if not validation_obj.is_valid_bot_name(bot_name) or len(bot_name) > 18:
                response['status'] = 302
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_exist = Bot.objects.filter(slug=slugify(bot_name), users__in=[
                user_obj], is_deleted=False)
            if bot_id:
                bot_exist = bot_exist.exclude(pk=int(bot_id))
            
            if(bot_exist.exists()):
                response['status'] = 400
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ValidateBotName: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

ValidateBotName = ValidateBotNameAPI.as_view()


class CreateBotWithNameImageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            logger.info("Into CreateBotWithNameImageAPI...", extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            data = request.data
            username = request.user.username
            user_obj = request.user
            latest_theme = EasyChatTheme.objects.filter(name="theme_2")[0]
            try:
                if user_obj.is_guest == True:
                    if Bot.objects.filter(created_by=user_obj, is_deleted=False):
                        response['status'] = 401
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Permission to create single bot: %s %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            no_of_bots_allowed = Config.objects.all()[0].no_of_bots_allowed
            current_number_of_bots = len(
                Bot.objects.filter(is_uat=True, is_deleted=False))
            if current_number_of_bots < no_of_bots_allowed:
                validation_obj = EasyChatInputValidation()

                bot_name = validation_obj.remo_html_from_string(
                    data["bot_name"])
                bot_name = validation_obj.remo_unwanted_characters(bot_name)
                bot_image = validation_obj.remo_html_from_string(
                    data["bot_image"]
                )
                bot_id = validation_obj.remo_html_from_string(
                    data["bot_id"])

                if not validation_obj.is_valid_bot_name(bot_name) or len(bot_name) > 18:
                    response['status'] = 302
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                if not bot_image:
                    response['status'] = 303
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                if bot_id:
                    existing_bot = Bot.objects.filter(pk=int(bot_id)).first()
                    existing_bot.name = bot_name
                    existing_bot.bot_image = bot_image
                    existing_bot.save()

                    response['status'] = 200
                    response["bot_id"] = int(bot_id)
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                if(len(Bot.objects.filter(slug=slugify(bot_name), users__in=[
                                          user_obj], is_deleted=False))):
                    response['status'] = 400
                else:
                    bot_obj = Bot.objects.create(name=bot_name)
                    bot_obj.users.add(user_obj)
                    bot_obj.created_by = user_obj
                    bot_obj.default_theme = latest_theme
                    bot_obj.bot_image = bot_image

                    # Adding defalut language English
                    language_en = Language.objects.get(lang="en")
                    bot_obj.languages_supported.add(language_en)
                    bot_channel_objs = BotChannel.objects.filter(bot=bot_obj)
                    for bot_channel in bot_channel_objs:
                        bot_channel.languages_supported.add(language_en)
                        bot_channel.save()
                    bot_obj.save()

                    # Adding default language template
                    check_and_create_bot_language_template_obj(
                        bot_obj, ["en"], RequiredBotTemplate, Language)

                    audit_trail_data = json.dumps({
                        "bot_pk": bot_obj.pk
                    })

                    if bot_obj.is_custom_js_required:
                        create_custom_js_file(bot_obj.pk)

                    if bot_obj.is_custom_css_required:
                        create_custom_css_file(
                            bot_obj.pk, bot_obj.default_theme.name)

                    save_audit_trail(
                        user_obj, CREATE_BOT_ACTION, audit_trail_data)
                    access_type_obj = AccessType.objects.get(
                        name="Full Access")

                    try:
                        access_mng_obj = AccessManagement.objects.get(
                            user=user_obj, bot=bot_obj)
                    except Exception:
                        access_mng_obj = AccessManagement.objects.create(
                            user=user_obj, bot=bot_obj)
                    access_mng_obj.access_type.clear()
                    access_mng_obj.access_type.add(access_type_obj)
                    access_mng_obj.save()

                    create_default_intents(bot_obj.pk)

                    update_word_dictionary(bot_obj)

                    create_default_processor_validators(
                        bot_obj, Processor, ProcessorValidator)

                    create_default_tms_flow(bot_obj.pk)
                    # create_whatsapp_tms_flow(bot_obj.pk)

                    sso_pre_login_check({"EmailID": [user_obj.username]})

                    CommonUtilsFile.objects.create(bot=bot_obj)

                    try:
                        bot_tester = Tester.objects.get(
                            user__username=username)

                        BotQATesting.objects.create(bot_id=bot_obj.pk,
                                                    bot_name=bot_obj.name,
                                                    bot_domain=settings.EASYCHAT_HOST_URL,
                                                    created_by=bot_tester)
                    except Exception:
                        pass

                    build_suggestions_and_word_mapper_thread = threading.Thread(
                        target=build_suggestions_and_word_mapper, args=(bot_obj.pk, Bot, WordMapper, Channel, Intent, ChunksOfSuggestions))
                    build_suggestions_and_word_mapper_thread.daemon = True
                    build_suggestions_and_word_mapper_thread.start()
                    description = "Bot created with name" + \
                        " (" + bot_name + " and bot_id " + str(bot_obj.pk) + ")"
                    add_audit_trail(
                        "EASYCHATAPP",
                        user_obj,
                        "Add-Bot",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )
                    response['status'] = 200
                    response["bot_id"] = bot_obj.pk
            else:
                response['status'] = 300

            logger.info("Exit from CreateBotWithNameImageAPI..", extra={'AppName': 'EasyChat', 'user_id': str(
                username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateBotWithNameImageAPI: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

CreateBotWithNameImage = CreateBotWithNameImageAPI.as_view()


class TwoMinuteBotConfigAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data
            json_string = DecryptVariable(data["data"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
            username = request.user.username
            if request.user not in bot_obj.users.all():
                response["status"] = 402
                response["msg"] = 'You are not authorised to perform this Operation.'
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            user_obj = request.user
            welcome_message = validation_obj.clean_html(data["welcome_message"])
            selected_languages = data["selected_languages"]
            is_nps_required = data["is_nps_required"]
            is_enable_live_chat = data["is_enable_live_chat"]
            is_enable_co_browse = data["is_enable_co_browse"]
            is_enable_ticket_management = data["is_enable_ticket_management"]
            is_enable_pdf_searcher = data["is_enable_pdf_searcher"]
            is_enable_easy_search = data["is_enable_easy_search"]
            is_enable_lead_generation = data["is_enable_lead_generation"]

            response["status"], response["msg"], welcome_message = check_two_minute_bot_welcome_message(welcome_message)

            if response["status"] == 400:
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if not bot_obj:
                response["status"] = 400
                response["msg"] = "Bot object doesn't exists."
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            welcome_message = validation_obj.remo_html_from_string(
                welcome_message)

            if len(welcome_message.strip()) > CHARACTER_LIMIT_LARGE_TEXT:
                response["status"] = 400
                response["msg"] = "Welcome Message is too long."
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            all_channels = Channel.objects.filter(is_easychat_channel=True).all()
            for channel in all_channels:
                bot_channel = BotChannel.objects.filter(bot=bot_obj, channel=channel).first()
                bot_channel.welcome_message = welcome_message
                bot_channel.save()

            if len(selected_languages) > 5:
                response["status"] = 400
                response["msg"] = "Maximum 5 languages can be selected from the list"
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_obj.is_nps_required = is_nps_required

            if is_nps_required:
                nps_obj = NPS.objects.filter(bot=bot_obj)
                if not nps_obj:
                    nps_obj = NPS.objects.create(bot=bot_obj)
                    bot_obj.scale_rating_5 = True
                    for channel_name in ["Web", "WhatsApp", "Android", "Viber", "iOS"]:
                        channel_obj = Channel.objects.filter(
                            name=channel_name).first()
                        nps_obj.channel.add(channel_obj)
                        nps_obj.save()
                    create_default_csat_flow(bot_id)

            eng_lang_obj = check_and_create_default_language_object(
                bot_obj, Language, RequiredBotTemplate)
            supported_languages = bot_obj.languages_supported.all()
            supported_languages = list(supported_languages.values('lang'))

            for selected_language in selected_languages:
                for supported_lang in supported_languages:
                    if supported_lang["lang"] == selected_language:
                        continue
                selected_language = validation_obj.remo_html_from_string(
                    selected_language)
                language_obj = Language.objects.filter(
                    lang=selected_language).first()
                language_template_obj = check_and_create_required_bot_language_template_for_selected_language(
                    bot_obj, language_obj, eng_lang_obj, RequiredBotTemplate, EasyChatTranslationCache)
                if language_template_obj == None:
                    response["status"] = 102
                    response["msg"] = str(get_developer_console_settings().google_translation_api_failure_message)
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                bot_obj.languages_supported.add(language_obj)

            bot_obj.is_easy_assist_allowed = is_enable_co_browse
            bot_obj.is_tms_allowed = is_enable_ticket_management
            bot_obj.is_easy_search_allowed = is_enable_easy_search
            bot_obj.is_pdf_search_allowed = is_enable_pdf_searcher
            bot_obj.is_lead_generation_enabled = is_enable_lead_generation

            try:
                logger.info("Updating livechat bot configuration", extra={'AppName': 'EasyChat', 'user_id': str(
                    username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                if user_obj.pk == bot_obj.created_by.pk and LiveChatUser.objects.filter(user=user_obj).count():
                    manage_default_livechat_intent(
                        is_enable_live_chat, bot_obj)
                    manage_bot_to_admin_account(
                        user_obj, is_enable_live_chat, bot_obj)
                    check_and_create_default_livechat_category(
                        bot_obj, user_obj)
                    bot_obj.is_livechat_enabled = is_enable_live_chat
                    logger.info("Successfully Updated livechat bot configuration", extra={'AppName': 'EasyChat', 'user_id': str(
                        request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("LiveChat bot configuration: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                pass

            set_easyassist_intent(bot_obj, is_enable_co_browse)
            set_easytms_intent(bot_obj, is_enable_ticket_management)
            if is_enable_ticket_management:
                set_tms_bot_admin(user_obj, Agent, bot_obj, TicketCategory)

            bot_obj.save()

            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TwoMinuteBotConfigAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

TwoMinuteBotConfig = TwoMinuteBotConfigAPI.as_view()


class UpdatingChannelLanguageAPI(APIView):

    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)
            
            validation_obj = EasyChatInputValidation()
            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            channels_added = data["channels_added"]
            selected_languages = data["selected_languages"]
            selected_bot_obj = Bot.objects.get(
                pk=int(bot_id), is_deleted=False, is_uat=True)

            if request.user not in selected_bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)
            
            all_channels = Channel.objects.filter(is_easychat_channel=True).all()
            if 'en' in selected_languages:
                selected_languages.remove('en')
            for channel in all_channels:
                channel_id = channel.pk
                bot_channel_obj = BotChannel.objects.filter(
                    bot=selected_bot_obj, channel=channel_id).first()
                if bot_channel_obj:
                    if len(bot_channel_obj.languages_supported.all()) > 1:
                        bot_channel_obj.languages_supported.clear()
                        language_obj = Language.objects.get(lang='en')
                        bot_channel_obj.languages_supported.add(language_obj)
                    if str(channel_id) in channels_added:
                        for language in selected_languages:
                            language_obj = Language.objects.get(lang=language)
                            bot_channel_obj.languages_supported.add(language_obj)
            
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdatingChannelLanguageAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdatingChannelLanguage = UpdatingChannelLanguageAPI.as_view()
