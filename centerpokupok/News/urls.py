from django.conf.urls import patterns, include, url

import centerpokupok.News.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', centerpokupok.News.views.newsList),
     url(r'^([0-9]+)/$', centerpokupok.News.views.newsDetail),
    # url(r'^blog/', include('blog.urls')),


)
