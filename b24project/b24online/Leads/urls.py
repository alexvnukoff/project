from django.conf.urls import url

from b24online.Leads.views import IndexLeadsList, GoLeadDelete

urlpatterns = [
    url(r'^$', IndexLeadsList.as_view(my=True), name='main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', IndexLeadsList.as_view(my=True), name="main_paginator"),
    #url(r'^update/(?P<pk>[0-9]+)/$', GoLeadUpdate.as_view(), name="update"),
    url(r'^delete/(?P<pk>[0-9]+)/$', GoLeadDelete.as_view(), name="delete"),
]
