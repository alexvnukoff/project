from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.Tpp.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Tpp.views.get_tpp_list, name='main'),
     url(r'^page/([0-9]+)?/$', tppcenter.Tpp.views.get_tpp_list, name="paginator"),






)