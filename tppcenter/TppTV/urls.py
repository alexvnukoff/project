from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.TppTV.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.TppTV.views.get_news_list, name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.TppTV.views.get_news_list, name="paginator"),
     url(r'^add/$', tppcenter.TppTV.views.addNews, name="add"),
     url(r'^update/([0-9]+)/$', tppcenter.TppTV.views.updateNew, name="update"),
     url(r'^[a-zA-z-]+-(?P<id>[0-9]+).html$', tppcenter.TppTV.views.get_news_list, name="detail"),





)