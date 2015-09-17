from django.conf.urls import patterns, url
import tppcenter.AdvTop.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
     url(r'^add/([0-9]+)/$', tppcenter.AdvTop.views.CreateContextAdvertisement.as_view(), name='top_form'),
     url(r'^filter/$', tppcenter.AdvTop.views.adv_json_filter, name='filter'),
     url(r'^order/(?P<pk>[0-9]+)/$', tppcenter.AdvTop.views.OrderDetail.as_view(), name='order'),
)