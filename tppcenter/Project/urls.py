__author__ = 'user'

from django.conf.urls import patterns, url
import tppcenter.Project.views
import tppcenter.views


urlpatterns = patterns('',
    # Examples:
     url(r'^about/$', tppcenter.Project.views.about, name='about'),
     url(r'^how/$', tppcenter.Project.views.how, name='how'),
     url(r'^terms/$', tppcenter.Project.views.terms, name='terms'),
     url(r'^partner/$', tppcenter.Project.views.partner, name='partner'),
     url(r'^privacy/$', tppcenter.Project.views.privacy, name='privacy'),
     url(r'^shop/$', tppcenter.Project.views.shop, name='shop'),
     url(r'^event/$', tppcenter.Project.views.event, name='event'),
     url(r'^proposal/$', tppcenter.Project.views.proposal, name='proposal'),
     url(r'^contact/$', tppcenter.Project.views.contact, name='contact'),
     url(r'^community/$', tppcenter.Project.views.community, name='community'),
     url(r'^faq/$', tppcenter.Project.views.faq, name='faq'),
)