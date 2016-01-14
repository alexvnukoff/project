from django.conf.urls import url

import b24online.Resume.views

urlpatterns = [
    url(r'^$', b24online.Resume.views.ResumeList.as_view(), name='main'),
    url(r'^page/(?P<page>[0-9]+)?/$', b24online.Resume.views.ResumeList.as_view(), name="paginator"),
    url(r'^my/$', b24online.Resume.views.ResumeList.as_view(my=True), name='my_main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', b24online.Resume.views.ResumeList.as_view(my=True), name="my_main_paginator"),
    url(r'^add/$', b24online.Resume.views.ResumeCreate.as_view(), name="add"),
    url(r'^update/(?P<pk>[0-9]+)/$', b24online.Resume.views.ResumeUpdate.as_view(), name="update"),
    url(r'^delete/(?P<pk>[0-9]+)/$', b24online.Resume.views.ResumeDelete.as_view(), name="delete"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', b24online.Resume.views.ResumeDetail.as_view(),
        name="detail"),
]
