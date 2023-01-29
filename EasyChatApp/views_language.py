from EasyChatApp.utils_validation import EasyChatInputValidation
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_bot import *
from EasyChatApp.constants import MAX_INTENT_PER_PAGE

from DeveloperConsoleApp.utils import get_developer_console_settings

from EasyChatApp.utils_bot import get_translated_text

from datetime import datetime


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class UpdateSelectedLanguageAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            selected_language = validation_obj.remo_html_from_string(
                data["selected_language"])
            bot_pk = int(data["bot_pk"])

            selected_bot_obj = Bot.objects.get(
                pk=bot_pk, is_deleted=False)

            intent_objs = Intent.objects.filter(
                bots__in=[selected_bot_obj], is_deleted=False, is_hidden=False)[:MAX_INTENT_PER_PAGE]

            selected_language_obj = Language.objects.get(
                lang=selected_language)
            for intent_obj in intent_objs:
                check_and_update_tunning_object(intent_obj, selected_language_obj, LanguageTuningIntentTable, LanguageTuningTreeTable,
                                                LanguageTuningBotResponseTable, LanguageTuningChoicesTable, EasyChatTranslationCache)

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateSelectedLanguageAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateSelectedLanguage = UpdateSelectedLanguageAPI.as_view()


class UpdateSelectedLanguageIntentAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            selected_language = validation_obj.remo_html_from_string(
                data["selected_language"])
            intent_pk = int(data["intent_pk"])

            intent_obj = Intent.objects.get(
                pk=intent_pk, is_deleted=False, is_hidden=False)

            selected_language_obj = Language.objects.get(
                lang=selected_language)

            check_and_update_tunning_object(intent_obj, selected_language_obj, LanguageTuningIntentTable, LanguageTuningTreeTable,
                                            LanguageTuningBotResponseTable, LanguageTuningChoicesTable, EasyChatTranslationCache)

            response["status"] = 200
            response["language_direction"] = selected_language_obj.language_script_type
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateSelectedLanguageIntentAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateSelectedLanguageIntent = UpdateSelectedLanguageIntentAPI.as_view()


class CheckSelectedLanguageIsSupportedAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["default_language"] = "en"
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            selected_language = validation_obj.remo_html_from_string(
                data["selected_language"])
            bot_pk = int(data["bot_pk"])

            selected_bot_obj = Bot.objects.get(
                pk=bot_pk, is_deleted=False)
            supported_languages = get_supported_languages(
                selected_bot_obj, BotChannel)

            selected_language_obj = Language.objects.get(
                lang=selected_language)

            response["status"] = 200

            if selected_language_obj not in supported_languages:
                response["status"] = 301
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CheckSelectedLanguageIsSupportedAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CheckSelectedLanguageIsSupported = CheckSelectedLanguageIsSupportedAPI.as_view()


class IgnoreBotResponseChangesInNonPrimaryLanguageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            tree_pk = data["tree_pk"]
            tree_pk = validation_obj.remo_html_from_string(tree_pk)
            tree_pk = validation_obj.remo_unwanted_characters(tree_pk)

            tree_obj = Tree.objects.filter(pk=tree_pk).first()

            bot_response_obj = None
            if tree_obj:
                bot_response_obj = tree_obj.response

            if bot_response_obj != None:
                activity_update = {
                    "is_text_response_updated": "false",
                    "is_speech_response_updated": "false",
                    "is_text_reprompt_response_updated": "false",
                    "is_table_updated": "false",
                    "are_cards_updated": "false",
                }
                activity_update = json.dumps(activity_update)
                bot_response_obj.activity_update = activity_update
                bot_response_obj.save()

                response["status"] = 200
            response["message"] = "Something went wrong in ignoring the changes Please refresh the page and try again."
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("IgnoreChangesInNonPrimaryLanguageAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


IgnoreBotResponseChangesInNonPrimaryLanguage = IgnoreBotResponseChangesInNonPrimaryLanguageAPI.as_view()


class AutoFixBotResponseChangesInNonPrimaryLanguageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            tree_pk = data["tree_pk"]
            tree_pk = validation_obj.remo_html_from_string(tree_pk)
            tree_pk = validation_obj.remo_unwanted_characters(tree_pk)

            tree_obj = Tree.objects.filter(pk=tree_pk).first()

            bot_response_obj = None
            if tree_obj:
                bot_response_obj = tree_obj.response

            if bot_response_obj != None:

                tree_obj = Tree.objects.filter(response=bot_response_obj).first()
                intent_obj = get_intent_obj_from_tree_obj(tree_obj)

                bot_info_obj = None
                if intent_obj:
                    bot_info_obj = BotInfo.objects.filter(bot=intent_obj.bots.all().first()).first()

                activity_update = json.loads(bot_response_obj.activity_update)
                auto_fix_language_tuned_bot_response_objects(
                    bot_response_obj, activity_update, LanguageTuningBotResponseTable, EasyChatTranslationCache, bot_info_obj)

                auto_fix_language_tuned_tree_objs(tree_obj, activity_update, LanguageTuningTreeTable, EasyChatTranslationCache)

                auto_fix_language_tuned_intent_objs(tree_obj, activity_update, Intent, LanguageTuningIntentTable, EasyChatTranslationCache)

                activity_update = {
                    "is_text_response_updated": "false",
                    "is_speech_response_updated": "false",
                    "is_text_reprompt_response_updated": "false",
                    "is_table_updated": "false",
                    "are_cards_updated": "false",
                }
                activity_update = json.dumps(activity_update)
                bot_response_obj.activity_update = activity_update
                bot_response_obj.save()

                response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AutoFixChangesInNonPrimaryLanguageAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AutoFixBotResponseChangesInNonPrimaryLanguage = AutoFixBotResponseChangesInNonPrimaryLanguageAPI.as_view()


class IgnoreBotConfigurationChangesInNonPrimaryLanguageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Something went wrong in ignoring the changes Please refresh the page and try again."
        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(data["bot_id"])
            bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

            bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()

            activity_update = {
                "is_bot_inactivity_response_updated": "false",
                "is_bot_response_delay_message_updated": "false",
                "is_flow_termination_bot_response_updated": "false",
                "is_flow_termination_confirmation_display_message_updated": "false",
                "is_emoji_angry_response_text_updated": "false",
                "is_emoji_happy_response_text_updated": "false",
                "is_emoji_neutral_response_text_updated": "false",
                "is_emoji_sad_response_text_updated": "false",
                "is_profanity_response_text_updated": "false"
            }

            activity_update = json.dumps(activity_update)
            bot_info_obj.activity_update = activity_update
            bot_info_obj.save()

            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("IgnoreChangesInNonPrimaryLanguageAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


IgnoreBotConfigurationChangesInNonPrimaryLanguage = IgnoreBotConfigurationChangesInNonPrimaryLanguageAPI.as_view()


class AutoFixBotConfigurationChangesInNonPrimaryLanguageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(data["bot_id"])
            bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

            bot_info_obj = BotInfo.objects.filter(bot=bot_obj)

            if bot_info_obj:
                bot_info_obj = bot_info_obj.first()
                activity_update = json.loads(bot_info_obj.activity_update)
                auto_fix_bot_configurations_objects(
                    bot_obj, activity_update, LanguageTunedBot, EasyChatTranslationCache)

                activity_update = {
                    "is_bot_inactivity_response_updated": "false",
                    "is_bot_response_delay_message_updated": "false",
                    "is_flow_termination_bot_response_updated": "false",
                    "is_flow_termination_confirmation_display_message_updated": "false",
                }
                activity_update = json.dumps(activity_update)
                bot_info_obj.activity_update = activity_update
                bot_info_obj.save()

                response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AutoFixChangesInNonPrimaryLanguageAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AutoFixBotConfigurationChangesInNonPrimaryLanguage = AutoFixBotConfigurationChangesInNonPrimaryLanguageAPI.as_view()


class GetLanguageConstantKeywordsAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            selected_language = data["selected_language"]
            selected_language = validation_obj.remo_html_from_string(
                selected_language)

            bot_obj = Bot.objects.get(pk=int(bot_id))

            language_obj = Language.objects.filter(
                lang=selected_language).first()

            eng_lang_obj = check_and_create_default_language_object(
                bot_obj, Language, RequiredBotTemplate)

            language_template_obj = check_and_create_required_bot_language_template_for_selected_language(
                bot_obj, language_obj, eng_lang_obj, RequiredBotTemplate, EasyChatTranslationCache)

            if language_template_obj == None:
                response["status"] = 102
                response["message"] = str(get_developer_console_settings().google_translation_api_failure_message)
            else:
                response["constant_keywords_dict"] = get_language_constant_dict(
                    language_template_obj)
                response["status"] = 200
                response["message"] = "Success"
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLanguageConstantKeywordsAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLanguageConstantKeywords = GetLanguageConstantKeywordsAPI.as_view()


class UpdateLanguageConstantKeywordsAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            selected_language = data["selected_language"]
            selected_language = validation_obj.remo_html_from_string(
                selected_language)

            if selected_language == "en":
                response["status"] = 400
                response["message"] = "can not edit default language"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            constant_keywords_dict = data["constant_keywords_dict"]

            bot_obj = Bot.objects.get(pk=int(bot_id))
            bot_channel_obj = BotChannel.objects.filter(bot=bot_obj)
            # email_id = data["email_id"]
            # email_id = validation_obj.remo_html_from_string(email_id)

            # entered_otp = data["entered_otp"]
            # entered_otp = validation_obj.remo_html_from_string(entered_otp)

            # is_otp_verified = verify_otp_for_language_configuration(
            #     email_id, request.user, bot_obj, entered_otp, EasyChatOTPDetails)

            # if not is_otp_verified:
            #     response["status"] = 400
            #     response["message"] = "Invalid OTP"
            #     custom_encrypt_obj = CustomEncrypt()
            #     response = custom_encrypt_obj.encrypt(json.dumps(response))
            #     return Response(data=response)

            language_obj = Language.objects.filter(
                lang=selected_language).first()

            bot_template_obj = RequiredBotTemplate.objects.filter(
                bot=bot_obj, language=language_obj)
            bot_template_obj = bot_template_obj.first()

            is_language_updated = update_language_template_object(
                bot_template_obj, constant_keywords_dict, validation_obj)

            if is_language_updated:
                bot_obj.languages_supported.add(language_obj)
                # Marking trained as False for all intents of this bot so that new training questions
                # based on newly added languages could be generated on build bot.
                Intent.objects.filter(
                    bots__in=[bot_obj], is_deleted=False, is_hidden=False).update(trained=False)
                bot_obj.need_to_build = True
                bot_obj.save()
                for channel in bot_channel_obj:
                    channel.languages_supported.add(language_obj)
                response["status"] = 200
            else:
                response["status"] = 400
                response["message"] = "Language not updated successfully"

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateLanguageConstantKeywordsAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateLanguageConstantKeywords = UpdateLanguageConstantKeywordsAPI.as_view()


class DeleteLanguageFromSupportedLanguagesAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            selected_language = data["selected_language"]
            selected_language = validation_obj.remo_html_from_string(
                selected_language)

            if selected_language == "en":
                response["status"] = 400
                response["message"] = "can not delete default language"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_obj = Bot.objects.get(pk=int(bot_id))

            # email_id = data["email_id"]
            # email_id = validation_obj.remo_html_from_string(email_id)

            # entered_otp = data["entered_otp"]
            # entered_otp = validation_obj.remo_html_from_string(entered_otp)

            # is_otp_verified = verify_otp_for_language_configuration(
            #     email_id, request.user, bot_obj, entered_otp, EasyChatOTPDetails)

            # if not is_otp_verified:
            #     response["status"] = 400
            #     response["message"] = "Invalid Otp"
            #     custom_encrypt_obj = CustomEncrypt()
            #     response = custom_encrypt_obj.encrypt(json.dumps(response))
            #     return Response(data=response)

            language_obj = Language.objects.filter(
                lang=selected_language).first()

            remove_supported_langauges_from_bot(
                bot_obj, language_obj, BotChannel, RequiredBotTemplate)

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteLanguageFromSupportedLanguagesAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteLanguageFromSupportedLanguages = DeleteLanguageFromSupportedLanguagesAPI.as_view()


# class SendOtpForLanguageConfigurationAPI(APIView):

#     authentication_classes = (
#         CsrfExemptSessionAuthentication, BasicAuthentication)

#     def post(self, request, *args, **kwargs):
#         response = {}
#         response["status"] = 500
#         try:
#             data = request.data
#             json_string = DecryptVariable(data["json_string"])
#             data = json.loads(json_string)

#             validation_obj = EasyChatInputValidation()

#             bot_id = data["bot_id"]
#             bot_id = validation_obj.remo_html_from_string(bot_id)
#             email_id = validation_obj.remo_html_from_string(data["email_id"])

#             selected_language = data["selected_language"]
#             selected_language = validation_obj.remo_html_from_string(
#                 selected_language)

#             if not validation_obj.is_valid_email(email_id):
#                 response["status"] = 400
#                 response["status_message"] = "Please enter valid Email ID."
#                 custom_encrypt_obj = CustomEncrypt()
#                 response = custom_encrypt_obj.encrypt(json.dumps(response))
#                 return Response(data=response)

#             email_ends_with = email_id.split("@")[-1]

#             if email_ends_with != "getcogno.ai":
#                 response["status"] = 400
#                 response["status_message"] = "Email ID ending with getcogno.ai only is valid for Updating Language Configuration"
#                 custom_encrypt_obj = CustomEncrypt()
#                 response = custom_encrypt_obj.encrypt(json.dumps(response))
#                 return Response(data=response)

#             language_obj = Language.objects.filter(
#                 lang=selected_language).first()
                
#             action_performed = validation_obj.remo_html_from_string(
#                 data["action_performed"])
#             bot_obj = Bot.objects.get(pk=int(bot_id))

#             user = request.user
#             otp_details_objs = EasyChatOTPDetails.objects.filter(
#                 user=user, bot=bot_obj, email_id=email_id)

#             if otp_details_objs.exists():
#                 otp_details_obj = otp_details_objs.first()
#             else:
#                 logger.info("Creating new OTP Details Object: %s: %s", extra={'AppName': 'EasyChat', 'user_id': str(
#                     request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
#                 otp_details_obj = EasyChatOTPDetails.objects.create(
#                     user=user, bot=bot_obj, email_id=email_id)

#             otp = random.randrange(10**5, 10**6)

#             otp_details_obj.otp = otp
#             otp_details_obj.is_expired = False
#             otp_details_obj.otp_sent_on = datetime.now()
#             otp_details_obj.save()

#             subject, content = get_subject_and_content_based_on_action_performed(
#                 action_performed, user, bot_obj, otp, language_obj)
#             email_ids = [email_id]

#             send_otp_mail(email_ids, subject, content)

#             response["status"] = 200
#         except Exception as e:  # noqa: F841
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("SendOtpForLanguageConfigurationAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
#                 'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

#         custom_encrypt_obj = CustomEncrypt()
#         response = custom_encrypt_obj.encrypt(json.dumps(response))
#         return Response(data=response)


# SendOtpForLanguageConfiguration = SendOtpForLanguageConfigurationAPI.as_view()
