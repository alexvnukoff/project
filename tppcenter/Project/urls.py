__author__ = 'user'

from django.conf.urls import patterns, url
import tppcenter.Project.views
import tppcenter.views
from django.utils.translation import ugettext as _

urlpatterns = patterns('',
    # Examples:
     url(r'^(?P<slug>[a-zA-z0-9-]+-(?P<item_id>[0-9]+))\.html$', tppcenter.Project.views.showPage, name="detail"),
     url(r'^about/$', tppcenter.Project.views.project, {'template': "about.html", 'section': _('About')}, name='about'),
     url(r'^adv/$', tppcenter.Project.views.project, {'template': "adv.html", 'section': _('Advertise with us')}, name='adv'),
     url(r'^payment/$', tppcenter.Project.views.project, {'template': "payment.html", 'section': _('Payment System')}, name='pay'),
     url(r'^terms/$', tppcenter.Project.views.project, {'template': "terms.html", 'section': _('Terms of use')}, name='terms'),
     url(r'^partner/$', tppcenter.Project.views.project, {'template': "partner.html", 'section': _('Find a Business Partner')}, name='partner'),
     url(r'^offer/$', tppcenter.Project.views.project, {'template': "offer.html", 'section': _('Public offer')}, name='offer'),
     url(r'^shop/$', tppcenter.Project.views.project, {'template': "shop.html", 'section': _('Create online shop')}, name='shop'),
     url(r'^event/$', tppcenter.Project.views.project, {'template': "event.html", 'section': _('Post announcement event')}, name='event'),
     url(r'^proposal/$', tppcenter.Project.views.project, {'template': "proposal.html", 'section': _('Add a business proposal')}, name='proposal'),
     url(r'^contact/$', tppcenter.Project.views.project, {'template': "contact.html", 'section': _('Contact us')}, name='contact'),
     url(r'^faq/$', tppcenter.Project.views.project, {'template': "faq.html", 'section': _('FAQ')}, name='faq'),
     url(r'^site/$', tppcenter.Project.views.project, {'template': "site.html", 'section': _('Your own site')}, name='site'),
)