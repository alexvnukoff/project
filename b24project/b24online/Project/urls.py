__author__ = 'user'

from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

import b24online.Project.views

urlpatterns = patterns('',
    # Examples:
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', b24online.Project.views.show_page, name="detail"),
     url(r'^about/$', b24online.Project.views.project, {'template': "about.html", 'section': _('About')}, name='about'),
     url(r'^adv/$', b24online.Project.views.project, {'template': "adv.html", 'section': _('Advertise with us')}, name='adv'),
     url(r'^payment/$', b24online.Project.views.project, {'template': "payment.html", 'section': _('Payment System')}, name='pay'),
     url(r'^terms/$', b24online.Project.views.project, {'template': "terms.html", 'section': _('Terms of use')}, name='terms'),
     url(r'^partner/$', b24online.Project.views.project, {'template': "partner.html", 'section': _('Find a Business Partner')}, name='partner'),
     url(r'^offer/$', b24online.Project.views.project, {'template': "offer.html", 'section': _('Public offer')}, name='offer'),
     url(r'^shop/$', b24online.Project.views.project, {'template': "shop.html", 'section': _('Create online shop')}, name='shop'),
     url(r'^event/$', b24online.Project.views.project, {'template': "event.html", 'section': _('Post announcement event')}, name='event'),
     url(r'^proposal/$', b24online.Project.views.project, {'template': "proposal.html", 'section': _('Add a business proposal')}, name='proposal'),
     url(r'^contact/$', b24online.Project.views.project, {'template': "contact.html", 'section': _('Contact us')}, name='contact'),
     url(r'^faq/$', b24online.Project.views.project, {'template': "faq.html", 'section': _('FAQ')}, name='faq'),
     url(r'^site/$', b24online.Project.views.project, {'template': "site.html", 'section': _('Your own site')}, name='site'),
)