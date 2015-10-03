from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.Wall.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', b24online.Wall.views.get_wall_list, name='main'),
)