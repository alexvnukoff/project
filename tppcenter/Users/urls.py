from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.Users.views
import tppcenter.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Users.views.UserList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.Users.views.UserList.as_view(), name="paginator"),







)