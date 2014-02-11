from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.News.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.News.views.get_news_list, name='main'),
     url(r'^page/([0-9]+)?/$', tppcenter.News.views.get_news_list, name="paginator"),
     url(r'^add/$', tppcenter.News.views.addNews, name="add"),
     url(r'^update/([0-9]+)/$', tppcenter.News.views.updateNew, name="update"),





)