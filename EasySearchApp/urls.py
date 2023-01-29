from django.contrib import admin
from django.conf.urls import url, include

from EasySearchApp import crawl_website

from . import views

urlpatterns = [
    url(r'^$', views.HomePage),
    url(r'^documents/', views.DocumentsPage),
    url(r'^search/redirect/(?P<url_pk>\d+)$', views.SearchRedirect),
    url(r'^search/api', views.EasySearchQuery),
    url(r'^start-crawling/', views.StartCrawling),
    url(r'^enable-e-search/', views.EnableElasticSearch),
    url(r'^enable-g-search/', views.EnableGoogleSearch),
]

# uncomment this line to use easysearch
# crawl_website.start_scheduler()
