from django.conf.urls import patterns, url
from django.contrib import admin
from usersites.Proposals.views import BusinessProposalList, BusinessProposalDetail

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', BusinessProposalList.as_view(), name='main'),
                       url(r'^page(?P<page>[0-9]+)?/$', BusinessProposalList.as_view(), name="paginator"),
                       url(r'^(?P<slug>[0-9a-zA-z-]+)-(?P<pk>[0-9]+)\.html$', BusinessProposalDetail.as_view(),
                           name='detail'),
                       )
