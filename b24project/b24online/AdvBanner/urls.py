from django.conf.urls import url

from b24online.AdvBanner.views import BannerBlockList, CreateBanner, OrderDetail, adv_json_filter

urlpatterns = [
    url(r'^$', BannerBlockList.as_view(), name='main'),
    url(r'^add/(?P<block_id>[0-9]+)/$', CreateBanner.as_view(), name='banner_form'),
    url(r'^order/(?P<pk>[0-9]+)/$', OrderDetail.as_view(), name='order'),
    url(r'^filter/$', adv_json_filter, name="filter")
]
