from django.conf.urls import patterns, url, include
from django.contrib import admin

import usersites.Contact.views
import usersites.views
import tppcenter.urls


admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', usersites.Contact.views.get_news_list, name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', usersites.Contact.views.get_news_list, name="paginator"),


)