from django.conf.urls import patterns, url
from django.contrib import admin

import tppcenter.BusinessProposal.views
import tppcenter.views

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.BusinessProposal.views.BusinessProposalList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', tppcenter.BusinessProposal.views.BusinessProposalList.as_view(), name="paginator"),
     url(r'^my/$', tppcenter.BusinessProposal.views.BusinessProposalList.as_view(my=True) , name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/', tppcenter.BusinessProposal.views.BusinessProposalList.as_view(my=True), name="my_main_paginator"),
     url(r'^add/$', tppcenter.BusinessProposal.views.BusinessProposalCreate.as_view(), name="add"),
     url(r'^update/(?P<pk>[0-9]+)/$', tppcenter.BusinessProposal.views.BusinessProposalUpdate.as_view(), name="update"),
     url(r'^delete/(?P<item_id>[0-9]+)/$', tppcenter.BusinessProposal.views.proposalForm,{'action': "delete"}, name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', tppcenter.BusinessProposal.views.BusinessProposalDetail.as_view(), name="detail"),
     url(r'^bp-category-list$', tppcenter.BusinessProposal.views.bp_categories_list,  name="BusinessProposalCategoryList"),
)
