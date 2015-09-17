__author__ = 'user'
from django.conf.urls import patterns, url
import tppcenter.AdvBanner.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.AdvBanner.views.BannerBlockList.as_view(), name='main'),
     url(r'^add/(?P<block_id>[0-9]+)/$', tppcenter.AdvBanner.views.CreateBanner.as_view(), name='banner_form'),
     url(r'^order/(?P<pk>[0-9]+)/$', tppcenter.AdvBanner.views.OrderDetail.as_view(), name='order'),
     url(r'^filter/$', tppcenter.AdvBanner.views.adv_json_filter, name="filter")
)