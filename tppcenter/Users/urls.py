from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Users.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Users.views.get_users_list, name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Users.views.get_users_list, name="paginator"),







)