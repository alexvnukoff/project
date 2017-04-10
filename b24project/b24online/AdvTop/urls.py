from django.conf.urls import url

from b24online.AdvTop.views import CreateContextAdvertisement, adv_json_filter, OrderDetail

urlpatterns = [
    url(r'^add/(?P<class_name>\w+)/(?P<pk>[0-9]+)/$', CreateContextAdvertisement.as_view(), name='top_form'),
    url(r'^filter/$', adv_json_filter, name='filter'),
    url(r'^order/(?P<pk>[0-9]+)/$', OrderDetail.as_view(), name='order'),
]
