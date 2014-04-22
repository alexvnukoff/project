from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.adminTpp.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', tppcenter.adminTpp.views.dashboard, name='main'),
    url(r'^users/$', tppcenter.adminTpp.views.users, name='users'),
)