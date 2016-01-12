__author__ = 'user'
from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.Analytic.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', b24online.Analytic.views.main, name='main'),
     url(r'^get/$', b24online.Analytic.views.get_analytic, 
         name='get_analytic'),
     url(r'^stats/(?P<event_type_id>\d+?)/(?P<content_type_id>\d+?)/'
         r'(?P<instance_id>\d+?)/(?P<cnt_type>\w+?)/$', 
         b24online.Analytic.views.RegisteredEventStatsDetail.as_view(),
         name='event_stats_detail'),
     url(r'^stats/$', 
         b24online.Analytic.views.RegisteredEventStats.as_view(),
         name='event_stats'),
)