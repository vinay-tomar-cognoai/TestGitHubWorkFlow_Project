from django.contrib import admin

# Register your models here.
from EasySearchApp.models import *

admin.site.register(WebsiteLink)
admin.site.register(SearchUser)
admin.site.register(EasySearchConfig)


class EasyPDFSearcherAdmin(admin.ModelAdmin):

    list_per_page = 50
    list_display = ('name', 'bot_obj', 'status', 'is_deleted', )
    list_filter = ('status', 'is_deleted')


admin.site.register(EasyPDFSearcher, EasyPDFSearcherAdmin)


class EasyPDFSearcherAnalyticsAdmin(admin.ModelAdmin):

    list_per_page = 50
    list_display = ('pdf_searcher', 'click_count', 'search_count')


admin.site.register(EasyPDFSearcherAnalytics, EasyPDFSearcherAnalyticsAdmin)


class PDFSearchExportRequestAdmin(admin.ModelAdmin):

    list_per_page = 50
    list_display = ('email_id', 'bot', 'is_completed')
    list_filter = ('is_completed', )


admin.site.register(PDFSearchExportRequest, PDFSearchExportRequestAdmin)


class PDFSearchIndexStatAdmin(admin.ModelAdmin):

    list_per_page = 50
    list_display = ('bot', 'is_indexing_required', 'is_indexing_in_progress')


admin.site.register(PDFSearchIndexStat, PDFSearchIndexStatAdmin)
