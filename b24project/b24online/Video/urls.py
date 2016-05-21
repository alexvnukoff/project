from django.conf.urls import url

from b24online.Video.views import VideoCreate, VideoUpdate, DeleteVideo, VideoDetail, VideoList

urlpatterns = [
    url(r'^$', VideoList.as_view(), name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', VideoList.as_view(), name="paginator"),
    url(r'^my/$', VideoList.as_view(my=True), name='my_main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', VideoList.as_view(my=True), name="my_main_paginator"),
    url(r'^add/$', VideoCreate.as_view(), name="add"),
    url(r'^update/(?P<pk>[0-9]+)/$', VideoUpdate.as_view(), {'action': 'update'}, name="update"),
    url(r'^delete/(?P<pk>[0-9]+)/$', DeleteVideo.as_view(), name="delete"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', VideoDetail.as_view(), name="detail"),
]
