from django.conf.urls import url

from b24online.Vacancy.views import RequirementList, RequirementCreate, RequirementUpdate, RequirementDelete, \
    send_resume, RequirementDetail, get_staffgroup_options

urlpatterns = [
    url(r'^$', RequirementList.as_view(), name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', RequirementList.as_view(), name="paginator"),
    url(r'^my/$', RequirementList.as_view(my=True), name='my_main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', RequirementList.as_view(my=True), {'my': True}, name="my_main_paginator"),
    url(r'^add/$', RequirementCreate.as_view(), name="add"),
    url(r'^update/(?P<pk>[0-9]+)/$', RequirementUpdate.as_view(), name="update"),
    url(r'^delete/(?P<pk>[0-9]+)/$', RequirementDelete.as_view(), name="delete"),
    url(r'^send/$', send_resume, name="send"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', RequirementDetail.as_view(), name="detail"),
    url(r'^staffgroup/options/$', get_staffgroup_options, name='staffgroups'),
]