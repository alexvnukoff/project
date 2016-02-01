from django.conf.urls import url

from b24online.Analytic.views import (main, get_analytic, 
    RegisteredEventStatsDetailView, RegisteredEventStatsView,
    RegisteredEventStatsDiagView)

urlpatterns = [
     ## url(r'^$', main, name='main'),
     url(r'^$', RegisteredEventStatsView.as_view(), name='main'),
     url(r'^get/$', get_analytic, name='get_analytic'),
     url(r'^stats/(?P<event_type_id>\d+?)/(?P<content_type_id>\d+?)/'
         r'(?P<instance_id>\d+?)/(?P<cnt_type>\w+?)/$',
         RegisteredEventStatsDetailView.as_view(), name='event_stats_detail'),
     url(r'^stats/(?P<event_type_id>\d+?)/(?P<content_type_id>\d+?)/'
         r'(?P<cnt_type>\w+?)/$',
         RegisteredEventStatsDetailView.as_view(), name='event_stats_ct_detail'),
     url(r'^stats/(?P<event_type_id>\d+?)/(?P<content_type_id>\d+?)/'
         r'(?P<instance_id>\d+?)/(?P<cnt_type>\w+?)/distrib/$',
         RegisteredEventStatsDiagView.as_view(), 
         name='event_stats_detail_distrib'),
     url(r'^stats/(?P<event_type_id>\d+?)/(?P<content_type_id>\d+?)/'
         r'(?P<cnt_type>\w+?)/distrib/$',
         RegisteredEventStatsDiagView.as_view(), 
         name='event_stats_ct_detail_distrib'),
     url(r'^stats/$', RegisteredEventStatsView.as_view(), name='event_stats'),
]