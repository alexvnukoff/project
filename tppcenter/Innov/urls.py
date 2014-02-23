from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Innov.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Innov.views.get_innov_list, name='main'),
     url(r'^page/([0-9]+)?/$', tppcenter.Innov.views.get_innov_list, name="paginator"),






)