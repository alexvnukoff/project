from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.AdvTop.views

admin.autodiscover()


urlpatterns = patterns('',
     url(r'^add/([0-9]+)/$', b24online.AdvTop.views.CreateContextAdvertisement.as_view(), name='top_form'),
     url(r'^filter/$', b24online.AdvTop.views.adv_json_filter, name='filter'),
     url(r'^order/(?P<pk>[0-9]+)/$', b24online.AdvTop.views.OrderDetail.as_view(), name='order'),
)