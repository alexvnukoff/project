from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.News.views
import tppcenter.views


admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.News.views.NewsList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.News.views.NewsList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.News.views.NewsList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', tppcenter.News.views.NewsList.as_view(my=True), name="my_main_paginator"),
     url(r'^add/$', tppcenter.News.views.NewsCreate.as_view(), name="add"),
     url(r'^category/(?P<category>[0-9]+)/$', tppcenter.News.views.NewsList.as_view(),  name='news_categories'),
     url(r'^category/(?P<category>[0-9]+)/page(?P<page>[0-9]+)?/$', tppcenter.News.views.NewsList.as_view(), name="news_categories_paginator"),
     url(r'^update/(?P<pk>[0-9]+)/$', tppcenter.News.views.NewsUpdate.as_view(),{'action': 'update'}, name="update"),
     # TODO
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.News.views.delete_news, name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.News.views.NewsDetail.as_view(), name="detail"),

)