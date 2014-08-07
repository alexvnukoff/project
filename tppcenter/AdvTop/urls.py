__author__ = 'user'
from django.conf.urls import patterns, url
import tppcenter.AdvTop.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^add/([0-9]+)/$', tppcenter.AdvTop.views.addTop, name='top_form'),
     url(r'^filter/$', tppcenter.AdvTop.views.advJsonFilter, name='filter'),
     url(r'^order/([0-9]+)/$', tppcenter.AdvTop.views.resultOrder, name='resultOrder'),
)