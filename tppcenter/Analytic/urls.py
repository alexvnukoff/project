__author__ = 'user'
from django.conf.urls import patterns, url
import tppcenter.Analytic.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.Analytic.views.main, name='main'),

)