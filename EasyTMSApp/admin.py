from django.contrib import admin

from EasyTMSApp.models import *
from EasyTMSApp.forms import *

admin.site.register(WorkingCalendar)
admin.site.register(LeaveCalendar)
admin.site.register(TicketCategory)
admin.site.register(Agent)
admin.site.register(Ticket)
admin.site.register(TicketAuditTrail)
admin.site.register(TicketStatus)
admin.site.register(TicketPriority)
admin.site.register(TMSAccessToken)
admin.site.register(UserNotification)
admin.site.register(AgentQuery)
admin.site.register(ExportRequest)
admin.site.register(FileAccessManagement)


class WhatsappApiProcessorAdmin(admin.ModelAdmin):

    form = WhatsappApiProcessorForm

admin.site.register(WhatsappApiProcessor, WhatsappApiProcessorAdmin)
admin.site.register(WhatsappApiProcessorLogger)


class CRMIntegrationModelAdmin(admin.ModelAdmin):
    list_filter = ('is_expired', 'access_token')
    readonly_fields = ('auth_token',)
    list_display = ('access_token', 'auth_token', 'is_expired')

admin.site.register(CRMIntegrationModel, CRMIntegrationModelAdmin)
