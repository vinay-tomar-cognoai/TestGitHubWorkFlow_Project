from django.contrib import admin

# Register your models here.

from TestingApp.models import *

admin.site.register(Tester)
admin.site.register(BotQATesting)
admin.site.register(BotQATestCase)
admin.site.register(BotQATestCaseFlow)
