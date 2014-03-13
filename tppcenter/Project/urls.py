__author__ = 'user'

from django.conf.urls import patterns, url
import tppcenter.Project.views
import tppcenter.views
from django.utils.translation import ugettext as _

urlpatterns = patterns('',
    # Examples:
     url(r'^about/$', tppcenter.Project.views.project, {'template': "about.html", 'section': _('About')}, name='about'),
     url(r'^how/$', tppcenter.Project.views.project, {'template': "how.html", 'section': _('How the system works')}, name='how'),
     url(r'^terms/$', tppcenter.Project.views.project, {'template': "terms.html", 'section': _('Terms of use')}, name='terms'),
     url(r'^partner/$', tppcenter.Project.views.project, {'template': "partner.html", 'section': _('Find a Business Partner')}, name='partner'),
     url(r'^privacy/$', tppcenter.Project.views.project, {'template': "privacy.html", 'section': _('Privacy')}, name='privacy'),
     url(r'^shop/$', tppcenter.Project.views.project, {'template': "shop.html", 'section': _('Create online shop')}, name='shop'),
     url(r'^event/$', tppcenter.Project.views.project, {'template': "event.html", 'section': _('Post announcement event')}, name='event'),
     url(r'^proposal/$', tppcenter.Project.views.project, {'template': "proposal.html", 'section': _('Add a business proposal')}, name='proposal'),
     url(r'^contact/$', tppcenter.Project.views.project, {'template': "contact.html", 'section': _('Contact us')}, name='contact'),
     url(r'^community/$', tppcenter.Project.views.project, {'template': "community.html", 'section': _('Ask the community')}, name='community'),
     url(r'^faq/$', tppcenter.Project.views.project, {'template': "faq.html", 'section': _('FAQ')}, name='faq'),
)