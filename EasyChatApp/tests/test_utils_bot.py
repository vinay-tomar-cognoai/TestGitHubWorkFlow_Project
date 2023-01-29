# -*- coding: utf-8 -*-
import sys
import logging
from django.test import TestCase
from EasyChatApp.models import BotChannel, User, RequiredBotTemplate, Language, Bot, Config, EasyChatTranslationCache, LanguageTunedBot, LanguageTunedBotChannel, Channel, Profile
from EasyChatApp.utils_bot import create_language_en_template,\
    check_and_create_bot_language_template_obj, get_translated_text, need_to_show_auto_fix_popup_for_bot_configuration, need_to_show_auto_fix_popup_for_channels, check_and_create_default_language_object, convert_to_channel_url_param, channel_name_formatter, check_and_create_required_bot_language_template_for_selected_language
from EasyChatApp.utils_channels import change_language_response_required, get_language_selected_by_user, get_languages, is_change_language_triggered
from EasyChatApp.utils_translation_module import translat_via_api
from EasyChatApp.utils_execute_query import set_user, save_data

logger = logging.getLogger(__name__)


class UtilsSmallMethodsWithModels(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        Config.objects.create()
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        channel = Channel.objects.create(name="Web")
        BotChannel.objects.create(bot=bot_obj, channel=channel)
        User.objects.create(
            role="1", status="1", username="test", password="test")

        Language.objects.create(lang="en")
        Language.objects.create(lang="hi")
        Language.objects.create(lang="vi")
        Language.objects.create(lang="ta")
        Language.objects.create(lang="te")
        Language.objects.create(lang="kn")
        Language.objects.create(lang="ml")

    def test_create_language_en_template(self):
        print("\n\nTesting create_language_en_template function")

        create_language_en_template(None, None, RequiredBotTemplate)

        self.assertEqual(RequiredBotTemplate.objects.all().count(), 0)

        bot_obj = Bot.objects.get(pk=1)
        # create_language_en_template(bot_obj, None, RequiredBotTemplate)
        check_and_create_default_language_object(bot_obj, Language, RequiredBotTemplate)
        self.assertEqual(RequiredBotTemplate.objects.all().count(), 1)

    def test_check_and_create_bot_language_template_obj(self):
        print("\n\nTesting check_and_create_bot_language_template_obj function")

        check_and_create_bot_language_template_obj(
            None, None, RequiredBotTemplate, Language)

        self.assertEqual(RequiredBotTemplate.objects.all().count(), 0)

        check_and_create_bot_language_template_obj(
            None, "None", RequiredBotTemplate, Language)

        self.assertEqual(RequiredBotTemplate.objects.all().count(), 0)

        bot_obj = Bot.objects.get(pk=1)
        check_and_create_bot_language_template_obj(
            bot_obj, ["en"], RequiredBotTemplate, Language)

        self.assertEqual(RequiredBotTemplate.objects.all().count(), 1)

        check_and_create_bot_language_template_obj(
            bot_obj, "None", RequiredBotTemplate, Language)

        self.assertEqual(RequiredBotTemplate.objects.all().count(), 1)

    # def test_translat_via_api(self):
    #     print("\n\nTesting translat_via_api function")

    #     self.assertEqual(translat_via_api("संपर्क करें", "en")[0], "Contact")

    # def test_get_translated_text(self):
    #     print("\n\nTesting get_translated_text function")

    #     self.assertEqual(get_translated_text(
    #         "hi", "hi", EasyChatTranslationCache), "नमस्ते")

    def test_need_to_show_auto_fix_popup_for_bot_configuration(self):

        print("\n\nTesting need_to_show_auto_fix_popup_for_bot_configuration")

        bot_obj = Bot.objects.get(pk=1)
        activity_update = {
            "is_bot_inactivity_response_updated": "false",
            "is_bot_response_delay_message_updated": "false",
            "is_flow_termination_bot_response_updated": "false",
            "is_flow_termination_confirmation_display_message_updated": "false",
        }

        eng_lang_obj = Language.objects.get(lang="en")
        hi_lang_obj = Language.objects.get(lang="hi")

        need_to_show = need_to_show_auto_fix_popup_for_bot_configuration(
            bot_obj, activity_update, "en", eng_lang_obj, LanguageTunedBot)

        self.assertEqual(False, need_to_show)

        activity_update = {
            "is_bot_inactivity_response_updated": "false",
            "is_bot_response_delay_message_updated": "true",
            "is_flow_termination_bot_response_updated": "false",
            "is_flow_termination_confirmation_display_message_updated": "false",
        }

        need_to_show = need_to_show_auto_fix_popup_for_bot_configuration(
            bot_obj, activity_update, "hi", eng_lang_obj, LanguageTunedBot)

        self.assertEqual(False, need_to_show)

        activity_update = {
            "is_bot_inactivity_response_updated": "false",
            "is_bot_response_delay_message_updated": "false",
            "is_flow_termination_bot_response_updated": "true",
            "is_flow_termination_confirmation_display_message_updated": "false",
        }

        LanguageTunedBot.objects.create(bot=bot_obj, language=hi_lang_obj)

        need_to_show = need_to_show_auto_fix_popup_for_bot_configuration(
            bot_obj, activity_update, "en", eng_lang_obj, LanguageTunedBot)

        self.assertEqual(True, need_to_show)

        activity_update = {
            "is_bot_inactivity_response_updated": "false",
            "is_bot_response_delay_message_updated": "false",
            "is_flow_termination_bot_response_updated": "true",
            "is_flow_termination_confirmation_display_message_updated": "true",
        }

        need_to_show = need_to_show_auto_fix_popup_for_bot_configuration(
            bot_obj, activity_update, "en", eng_lang_obj, LanguageTunedBot)

        self.assertEqual(True, need_to_show)

    def test_need_to_show_auto_fix_popup_for_channels(self):

        print("\n\nTesting need_to_show_auto_fix_popup_for_channels")

        bot_channel_obj = BotChannel.objects.get(pk=1)

        activity_update = {
            "is_welcome_message_updated": "false",
            "is_failure_message_updated": "false",
            "is_authentication_message_updated": "false",
            "is_auto_pop_up_text_updated": "false",
            "is_web_prompt_message_updated": "[]",
        }

        eng_lang_obj = Language.objects.get(lang="en")
        hi_lang_obj = Language.objects.get(lang="hi")
        bot_channel_obj.languages_supported.add(eng_lang_obj)
        bot_channel_obj.languages_supported.add(hi_lang_obj)

        bot_channel_obj.save()

        need_to_show = need_to_show_auto_fix_popup_for_channels(
            bot_channel_obj, activity_update, "en", LanguageTunedBotChannel)

        self.assertEqual(False, need_to_show)

        activity_update = {
            "is_welcome_message_updated": "false",
            "is_failure_message_updated": "false",
            "is_authentication_message_updated": "false",
            "is_auto_pop_up_text_updated": "false",
            "is_web_prompt_message_updated": "[]",
        }

        need_to_show = need_to_show_auto_fix_popup_for_channels(
            bot_channel_obj, activity_update, "hi", LanguageTunedBotChannel)

        self.assertEqual(False, need_to_show)

        activity_update = {
            "is_welcome_message_updated": "false",
            "is_failure_message_updated": "true",
            "is_authentication_message_updated": "false",
            "is_auto_pop_up_text_updated": "false",
            "is_web_prompt_message_updated": "[]",
        }

        LanguageTunedBotChannel.objects.create(
            bot_channel=bot_channel_obj, language=hi_lang_obj)

        need_to_show = need_to_show_auto_fix_popup_for_channels(
            bot_channel_obj, activity_update, "en", LanguageTunedBotChannel)

        self.assertEqual(True, need_to_show)

        activity_update = {
            "is_welcome_message_updated": "false",
            "is_failure_message_updated": "false",
            "is_authentication_message_updated": "true",
            "is_auto_pop_up_text_updated": "false",
            "is_web_prompt_message_updated": "[]",
        }

        need_to_show = need_to_show_auto_fix_popup_for_channels(
            bot_channel_obj, activity_update, "en", LanguageTunedBotChannel)

        self.assertEqual(True, need_to_show)

    def test_is_change_language_triggered(self):
        print("\n\nTesting is_change_language_triggered")
        
        user_id = "test_user"
        bot_id = 1
        bot_obj = Bot.objects.filter(pk=bot_id).first()
        set_user(user_id, "web", "src", "Web", bot_id)
        profile_obj = Profile.objects.filter(user_id=user_id, bot=bot_obj).first()
        save_data(profile_obj, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                        src="None", channel="Web", bot_id=bot_id, is_cache=True)

        is_triggered = is_change_language_triggered(user_id, bot_obj)

        self.assertTrue(is_triggered)

    def test_get_languages(self):
        print("\n\nTesting get_languages")

        selected_langs = ["en", "hi"]
        bot = Bot.objects.filter(pk=1).first()
        channel = Channel.objects.filter(name="Web").first()
        channel = BotChannel.objects.get(bot=bot, channel=channel)
        for lang in selected_langs:
            lang_obj = Language.objects.filter(lang=lang).first()
            channel.languages_supported.add(lang_obj)
        channel.save()

        language_list = get_languages(1, "Web")

        self.assertEqual(len(language_list), 2)

    def test_change_language_response_required(self):
        print("\n\nTesting change_language_response_required")

        user_id = "test_user"
        bot_id = 1
        bot_obj = Bot.objects.filter(pk=bot_id).first()
        channel = Channel.objects.filter(name="Web").first()
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel).first()
        set_user(user_id, "web", "src", "Web", bot_id)
        profile_obj = Profile.objects.filter(
            user_id=user_id, bot=bot_obj).first()
        selected_langs = ["en", "hi"]

        pre_enabled_option = change_language_response_required(user_id, bot_id, bot_obj, "Web")

        self.assertFalse(pre_enabled_option)

        bot_channel_obj.is_enable_choose_language_flow_enabled_for_welcome_response = True
        profile_obj.selected_language = None
        for lang in selected_langs:
            lang_obj = Language.objects.filter(lang=lang).first()
            bot_channel_obj.languages_supported.add(lang_obj)
        profile_obj.save()
        bot_channel_obj.save()

        post_enabled_option = change_language_response_required(user_id, bot_id, bot_obj, "Web")

        self.assertTrue(post_enabled_option)
        
    def test_get_language_selected_by_user(self):
        print("\n\nTesting get_language_selected_by_user")

        user_id = "test_user"
        bot_id = 1
        bot_obj = Bot.objects.filter(pk=bot_id).first()

        selected_lang = get_language_selected_by_user(user_id, bot_id, bot_obj, "", "Web")

        self.assertEqual(selected_lang, "en")

    def test_convert_to_channel_url_param(self):
        print("\n\nTesting convert_to_channel_url_param")

        converted_gbm = convert_to_channel_url_param("GoogleBusinessMessages")
        converted_et_source = convert_to_channel_url_param("ET-Source")
        converted_android = convert_to_channel_url_param("Android")

        self.assertEqual(converted_gbm, "google-buisness-messages")
        self.assertEqual(converted_et_source, "et-source")
        self.assertEqual(converted_android, "android")

    def test_channel_name_formatter(self):
        print("\n\nTesting channel_name_formatter")

        formatted_gbm = channel_name_formatter("GoogleBusinessMessages")
        formatted_et_source = channel_name_formatter("ET-Source")
        formatted_android = channel_name_formatter("Android")

        self.assertEqual(formatted_gbm, "Google Business Messages")
        self.assertEqual(formatted_et_source, "ET Source")
        self.assertEqual(formatted_android, "Android")
