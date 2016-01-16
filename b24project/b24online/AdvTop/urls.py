from django.conf.urls import url

import b24online.AdvTop.views

urlpatterns = [
    url(r'^add/([0-9]+)/$', b24online.AdvTop.views.CreateContextAdvertisement.as_view(), name='top_form'),
    url(r'^filter/$', b24online.AdvTop.views.adv_json_filter, name='filter'),
    url(r'^order/(?P<pk>[0-9]+)/$', b24online.AdvTop.views.OrderDetail.as_view(), name='order'),
]
