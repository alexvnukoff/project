from django.contrib.sites.shortcuts import get_current_site
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from b24online.models import BusinessProposal, B2BProduct, News, Company
from centerpokupok.models import B2CProduct


def wall(request):
    organization = get_current_site(request).user_site.organization
    proposals = BusinessProposal.get_active_objects().filter(organization=organization)[:3]
    news = News.get_active_objects().filter(organization=organization)[:3]

    if isinstance(organization, Company):
        b2c_products = B2CProduct.get_active_objects().filter(company=organization)[:4]
        b2b_products = B2BProduct.get_active_objects().filter(company=organization)[:4]
    else:
        b2b_products = None
        b2c_products = None

    current_section = ''
    title = _("Wall")

    template_params = {
        'current_section': current_section,
        'title': title,
        'proposals': proposals,
        'news': news,
        'b2c_products': b2c_products,
        'b2b_products': b2b_products
    }

    return render_to_response("contentPage.html", template_params, context_instance=RequestContext(request))