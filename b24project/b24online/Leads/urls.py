from django.conf.urls import url

from b24online.Leads.views import IndexLeadsList

urlpatterns = [
    url(r'^$', IndexLeadsList.as_view(my=True), name='main'),
    url(r'^my/page(?P<page>[0-9]+)?/$', IndexLeadsList.as_view(my=True), name="main_paginator"),
]
