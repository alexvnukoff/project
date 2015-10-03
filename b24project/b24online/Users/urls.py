from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.Users.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', b24online.Users.views.UserList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', b24online.Users.views.UserList.as_view(), name="paginator"),







)