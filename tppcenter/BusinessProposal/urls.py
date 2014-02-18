from django.conf.urls import patterns, include, url
import appl.views
import tppcenter.BusinessProposal.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', tppcenter.BusinessProposal.views.get_proposals_list, name='main'),
     url(r'^page/([0-9]+)?/$', tppcenter.BusinessProposal.views.get_proposals_list, name="paginator"),






)