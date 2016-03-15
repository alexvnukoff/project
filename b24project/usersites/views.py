from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.shortcuts import render_to_response
from b24online.models import BusinessProposal, B2BProduct, News, Company
from b24online.utils import get_template_with_base_path
from centerpokupok.models import B2CProduct
from django.utils.timezone import now

from tpp.DynamicSiteMiddleware import get_current_site


def render_page(request, template, **kwargs):
    return render_to_response(get_template_with_base_path(template), kwargs, context_instance=RequestContext(request))


def wall(request):
    organization = get_current_site().user_site.organization
    proposals = BusinessProposal.get_active_objects().filter(organization=organization)
    news = News.get_active_objects().filter(organization=organization)

    if isinstance(organization, Company):
        b2c_products = B2CProduct.get_active_objects().filter(company=organization)
        b2c_coupons = B2CProduct.get_active_objects().filter(company=organization,
                                                             coupon_dates__contains=now().date(),
                                                             coupon_discount_percent__gt=0).order_by("-created_at")
        b2b_products = B2BProduct.get_active_objects().filter(company=organization)
    else:
        b2b_products = None
        b2c_products = None
        b2c_coupons = None

    current_section = ''

    template_params = {
        'current_section': current_section,
        'title': get_current_site().user_site.organization.name,
        'proposals': proposals,
        'news': news,
        'b2c_coupons': b2c_coupons,
        'b2c_products': b2c_products,
        'b2b_products': b2b_products
    }
    template_name = "{template_path}/contentPage.html"
    site = get_current_site()
    try:
        user_site = site.user_site
        user_site.refresh_from_db()

        if user_site.user_template is not None:
            folder_template = user_site.user_template.folder_name
            template_name = template_name.format(template_path=folder_template)
        else:
            template_name = template_name.format(template_path='usersites')
    except ObjectDoesNotExist:
        template_name = template_name.format(template_path='usersites')

    return render_to_response(template_name, template_params, context_instance=RequestContext(request))
