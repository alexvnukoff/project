__author__ = 'user'
from django.conf.urls import patterns, url
import tppcenter.AdvBanner.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.AdvBanner.views.gatPositions, name='main'),
     url(r'^add/([0-9]+)/$', tppcenter.AdvBanner.views.addBanner, name='banner_form'),
     url(r'^filter/$', tppcenter.AdvBanner.views.advJsonFilter),

)