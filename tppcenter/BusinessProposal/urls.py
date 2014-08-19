from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.BusinessProposal.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.BusinessProposal.views.get_proposal_list.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.BusinessProposal.views.get_proposal_list.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.BusinessProposal.views.get_proposal_list.as_view(my=True) , name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/', tppcenter.BusinessProposal.views.get_proposal_list.as_view(my=True), name="my_main_paginator"),
     url(r'^add/$', tppcenter.BusinessProposal.views.proposalForm,{'action': "add"}, name="add"),
     url(r'^update/(?P<item_id>[0-9]+)/$', tppcenter.BusinessProposal.views.proposalForm,{'action': "update"}, name="update"),
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.BusinessProposal.views.proposalForm,{'action': "delete"}, name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+-(?P<item_id>[0-9]+))\.html$', tppcenter.BusinessProposal.views.get_proposal_detail.as_view(), name="detail"),






)