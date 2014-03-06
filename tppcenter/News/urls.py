from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.News.views
import tppcenter.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.News.views.get_news_list, name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.News.views.get_news_list, name="paginator"),
     url(r'^my/$', tppcenter.News.views.get_news_list,{'my':True}, name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.News.views.get_news_list,{'my':True}, name="my_main_paginator"),
     url(r'^add/$', tppcenter.News.views.addNews, name="add"),
     url(r'^update/([0-9]+)/$', tppcenter.News.views.updateNew, name="update"),
     url(r'^[0-9a-zA-z-]+-(?P<item_id>[0-9]+).html$', tppcenter.News.views.detail, name="detail"),
)