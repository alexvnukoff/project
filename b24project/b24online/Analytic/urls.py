__author__ = 'user'
from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.Analytic.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', b24online.Analytic.views.main, name='main'),
     url(r'^get/$', b24online.Analytic.views.get_analytic, name='get_analytic'),

)