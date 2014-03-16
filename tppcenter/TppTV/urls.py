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
     url(r'^add/$', tppcenter.TppTV.views.tvForm,{'action': 'add'}, name="add"),
     url(r'^update/(?P<item_id>[0-9]+)/$', tppcenter.TppTV.views.tvForm,{'action': 'update'}, name="update"),
     url(r'^(?P<slug>[0-9a-zA-z-]+-(?P<item_id>[0-9]+))\.html$', tppcenter.TppTV.views.get_news_list, name="detail"),
)
