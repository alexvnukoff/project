from django.conf.urls import url

from b24online.Resume.views import ResumeList, ResumeCreate, ResumeUpdate, ResumeDelete, ResumeDetail

urlpatterns = [
    url(r'^$', ResumeList.as_view(), name='main'),
    url(r'^page/(?P<page>[0-9]+)?/$', ResumeList.as_view(), name="paginator"),
    url(r'^my/$', ResumeList.as_view(my=True), name='my_main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', ResumeList.as_view(my=True), name="my_main_paginator"),
    url(r'^add/$', ResumeCreate.as_view(), name="add"),
    url(r'^update/(?P<pk>[0-9]+)/$', ResumeUpdate.as_view(), name="update"),
    url(r'^delete/(?P<pk>[0-9]+)/$', ResumeDelete.as_view(), name="delete"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', ResumeDetail.as_view(), name="detail"),
]
