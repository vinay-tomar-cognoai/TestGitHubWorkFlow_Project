from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from EasyChatApp.views import BotConsole
from EasyChatApp.views import EasyChatHomePage
from EasyAssistApp.views_agent import service_worker
from LiveChatApp.views_agent import service_worker_livechat

import django_saml2_auth.views

urlpatterns = [
    url(r'^sso/login/$', django_saml2_auth.views.signin),
    url(r'^sso_auth/', include('django_saml2_auth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^logs/', include('logtailer.urls')),
    url(r'^chat/', include('EasyChatApp.urls')),
    url(r'^campaign/', include("CampaignApp.urls")),
    url(r'^developer-console/', include("DeveloperConsoleApp.urls")),
    url(r'^livechat/', include('LiveChatApp.urls')),
    url(r'^ameyo/', include('LiveChatApp.urls')),
    url(r'^easy-assist/', include("EasyAssistApp.urls")),
    url(r'^easy-assist-salesforce/', include("EasyAssistSalesforceApp.urls")),
    url(r'^search/', include('EasySearchApp.urls')),
    url(r'^tms/', include('EasyTMSApp.urls')),
    url(r'^automated-api/', include('AutomatedAPIApp.urls')),
    url(r'^automation/', include('TestingApp.urls')),
    url(r'^audit-trail/', include('AuditTrailApp.urls')),
    url(r'^oauth/', include('OAuthApp.urls')),
    url(r'^', include('EasyChatApp.urls')),
    url(r'^service-worker-cobrowse.js', service_worker),
    url(r'^service-worker-livechat.js', service_worker_livechat),
    url(r'^cogno-meet/', include("CognoMeetApp.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'EasyChatApp.views.PageNotFoundView'
