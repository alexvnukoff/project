from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Wall.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Wall.views.get_wall_list, name='main'),





)