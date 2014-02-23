from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Exhibitions.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Exhibitions.views.get_exhibitions_list, name='main'),
     url(r'^page/([0-9]+)?/$', tppcenter.Exhibitions.views.get_exhibitions_list, name="paginator"),






)