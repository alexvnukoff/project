__author__ = 'user'
from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.AdvBanner.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', b24online.AdvBanner.views.BannerBlockList.as_view(), name='main'),
     url(r'^add/(?P<block_id>[0-9]+)/$', b24online.AdvBanner.views.CreateBanner.as_view(), name='banner_form'),
     url(r'^order/(?P<pk>[0-9]+)/$', b24online.AdvBanner.views.OrderDetail.as_view(), name='order'),
     url(r'^filter/$', b24online.AdvBanner.views.adv_json_filter, name="filter")
)