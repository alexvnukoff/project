from django.conf.urls import url
from django.utils.translation import ugettext as _

from b24online.Project.views import show_page, project

urlpatterns = [
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', show_page, name="detail"),
    url(r'^about/$', project, {'template': "about.html", 'section': _('About')}, name='about'),
    url(r'^adv/$', project, {'template': "adv.html", 'section': _('Advertise with us')}, name='adv'),
    url(r'^payment/$', project, {'template': "payment.html", 'section': _('Payment System')}, name='pay'),
    url(r'^terms/$', project, {'template': "terms.html", 'section': _('Terms of use')}, name='terms'),
    url(r'^partner/$', project, {'template': "partner.html", 'section': _('Find a Business Partner')}, name='partner'),
    url(r'^offer/$', project, {'template': "offer.html", 'section': _('Public offer')}, name='offer'),
    url(r'^shop/$', project, {'template': "shop.html", 'section': _('Create online shop')}, name='shop'),
    url(r'^event/$', project, {'template': "event.html", 'section': _('Post announcement event')}, name='event'),
    url(r'^proposal/$', project, {'template': "proposal.html", 'section': _('Add a business proposal')},
        name='proposal'),
    url(r'^contact/$', project, {'template': "contact.html", 'section': _('Contact us')}, name='contact'),
    url(r'^faq/$', project, {'template': "faq.html", 'section': _('FAQ')}, name='faq'),
    url(r'^site/$', project, {'template': "site.html", 'section': _('Your own site')}, name='site'),
]
