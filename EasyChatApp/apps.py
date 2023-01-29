# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
import sys


class EasychatappConfig(AppConfig):
    name = 'EasyChatApp'

    def ready(self):
        # This function is called when whole app is loaded.
        # Below file is imported inline because apps.py file is loaded before loading of app and other files.
        from EasyChatApp.environment_ready import load_spell_checker, load_advanced_nlp_dependencies

        command_called = sys.argv[-1]
            
        if command_called.strip().lower() == "runserver" or command_called.strip().lower() == "easychat.wsgi:application":

            load_spell_checker()
            load_advanced_nlp_dependencies()
