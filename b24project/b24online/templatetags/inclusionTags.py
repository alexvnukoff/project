# -*- encoding: utf-8 -*-

import os
import logging

from django.db import models 
from django import template
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language, gettext as _
from appl import func
from b24online.models import Chamber, B2BProduct, Organization, StaticPage, Exhibition, Tender, InnovationProject, \
    BusinessProposal, Company, News, Banner, BannerBlock
from centerpokupok.models import B2CProduct, B2CProductCategory
from jobs.models import Requirement, Resume
from tpp.DynamicSiteMiddleware import get_current_site

logger = logging.getLogger(__name__)

register = template.Library()


@register.inclusion_tag('usersites/banner.html')
def site_banner(side, block):
    site_pk = get_current_site().pk
    cache_name = "banner:usersite:%s:%s" % (block, site_pk)
    cached = cache.get(cache_name)

    if not cached:
        banner = Banner.objects.filter(site_id=site_pk, block__code=block, block__block_type='user_site').order_by('?') \
            .first()

        if banner:
            cache.set(cache_name, banner, 60 * 60)
    else:
        banner = cache.get(cache_name)

    return {'banner': banner, 'side': side}


@register.inclusion_tag('usersites/tops.html')
def site_context_adv():
    organization_id = get_current_site().user_site.organization.pk
    cache_name = "adv:context:%s:%s" % (get_language(), organization_id)
    cached = cache.get(cache_name)

    if not cached:
        models = func.get_tops({Chamber: [organization_id]})

        if models is not None:
            cache.set(cache_name, models, 60 * 10)
    else:
        models = cache.get(cache_name)

    return {'MEDIA_URL': settings.MEDIA_URL, 'models': models}


@register.inclusion_tag('b24online/AdvTop/tops.html', takes_context=True)
def get_top_on_page(context, item=None):
    request = context.get('request')

    if item:
        filter_adv = func.get_detail_adv_filter(item)
    else:
        filter_adv = func.get_list_adv_filter(request)

    cached = None
    cache_name = "%s_adv_top_cache" % get_language()

    if filter_adv is None:
        cached = cache.get(cache_name)

    if cached is None:
        models = func.get_tops(filter_adv)

        if filter_adv is None and models is not None:
            cache.set(cache_name, models, 60 * 10)
    else:
        models = cache.get(cache_name)

    return {'MEDIA_URL': settings.MEDIA_URL, 'models': models}


@register.inclusion_tag('b24online/AdvBanner/banners.html', takes_context=True)
def get_banner(context, block, item):
    request = context.get('request')

    if item:
        advertisement_filter = func.get_detail_adv_filter(item)
    else:
        advertisement_filter = func.get_list_adv_filter(request)

    cached = False
    cache_name = "banner:%s:%s" % (block, settings.SITE_ID)

    if advertisement_filter is None:
        cached = cache.get(cache_name)

    if not cached:
        banner = func.get_banner(block, None, advertisement_filter)

        if advertisement_filter is None:
            cache.set(cache_name, banner, 60 * 10)
    else:
        banner = cache.get(cache_name)

    return {'banner': banner}


@register.inclusion_tag('b24online/main/currentCompany.html', takes_context=True)
def get_my_companies_list(context):
    request = context.get('request')

    if not request.user or request.user.is_anonymous() or not request.user.is_authenticated():
        return {'current_company': None}

    current_company = request.session.get('current_company', None)

    if current_company:
        item = Organization.objects.get(pk=current_company)

        if not item.has_perm(request.user):
            del request.session['current_company']
        else:
            return {'current_company': item.name}

    if request.user.profile.full_name:
        return {'current_company': request.user.profile.full_name}

    return {'current_company': request.user.email}


@register.inclusion_tag('b24online/main/statistic.html')
def statistic(*args, **kwargs):
    model_statistic = {
        # _('Products'): B2BProduct.objects.count(),
        _('Companies'): Company.objects.count(),
        _('Partners'): Chamber.objects.count()
    }

    return {'model_statistic': model_statistic}


@register.inclusion_tag('b24online/main/contextMenu.html', 
                        name='setContextMenu', takes_context=True)
def set_context_menu(context, obj, **kwargs):
    current_path = context.get('current_path')
    model_name = context.get('model', None)
    request = context.get('request')

    url_namespace = None
    set_current = False
    delete = True
    top_perm = True

    if model_name == BusinessProposal.__name__:
        url_namespace = "proposal"
    elif model_name == B2BProduct.__name__:
        url_namespace = "products"
    elif model_name == B2CProduct.__name__:
        url_namespace = "products"
        top_perm = False
    elif model_name == InnovationProject.__name__:
        url_namespace = "innov"
    elif model_name == Tender.__name__:
        url_namespace = "tenders"
    elif model_name == Exhibition.__name__:
        url_namespace = "exhibitions"
    elif model_name == Requirement.__name__:
        url_namespace = "vacancy"
    elif model_name == Resume.__name__:
        url_namespace = "resume"
    elif model_name == News.__name__:
        url_namespace = "tv" if obj.is_tv else "news"
    elif model_name == Company.__name__:
        set_current = True
        url_namespace = "companies"
    elif model_name == Chamber.__name__:
        set_current = True
        url_namespace = "tpp"
        delete = False

    params = {
        'top_perm': top_perm,
        'top_type': model_name.lower(),
        'obj': obj,
        'url_namespace': url_namespace,
        'current_path': current_path,
        'set_current': set_current,
        'delete': delete
    }

    logger.debug(obj)
    if isinstance(obj, models.Model):
        logger.debug('Step 0')
        extra_options_meth = getattr(obj, 'get_contextmenu_options', None)
        if extra_options_meth and callable(extra_options_meth):
            logger.debug('Step 1')
            params['extra_options'] = extra_options_meth(context)

    has_perm = getattr(obj, 'has_perm', None)

    if has_perm is None or url_namespace is None:
        params['has_perm'] = None
    else:
        params['has_perm'] = has_perm(request.user)

    params.update(kwargs)

    return params


@register.inclusion_tag('usersites/slider.html')
def site_slider():
    import glob
    user_site = get_current_site().user_site
    custom_images = user_site.slider_images

    if custom_images:
        images = [obj.image.original for obj in custom_images.only('image')]
    else:
        static_url = "%susersites/templates" % settings.STATIC_URL
        dir = user_site.template.folder_name
        images = ["%s/%s/%s" % (static_url, os.path.basename(dir), os.path.basename(image))
                  for image in glob.glob(dir + "/*.jpg")]

    return {'images': images}


@register.inclusion_tag('b24online/main/staticPages.html')
def show_static_pages(site_type='b2b'):
    cache_name = "%s_static_pages_all_bottom" % get_language()

    cached = cache.get(cache_name)

    if not cached:
        pages = {}

        for page in StaticPage.objects.filter(site_type=site_type).only('page_type', 'slug', 'title'):
            pages[page.page_type] = pages.get(page.page_type, []) + [page]

        cache.set(cache_name, pages, 60 * 60 * 24 * 7)
    else:
        pages = cache.get(cache_name)

    return {'pagesDict': pages}


@register.inclusion_tag('b24online/main/topStaticPages.html')
def show_top_static_pages(site_type='b2b'):
    cache_name = "%s_static_pages_all_top" % get_language()
    cached = cache.get(cache_name)

    if not cached:
        pages = StaticPage.objects.filter(is_on_top=True, site_type=site_type).only('title')
        cache.set(cache_name, pages, 60 * 60 * 24 * 7)
    else:
        pages = cache.get(cache_name)

    return {'pages': pages}


@register.inclusion_tag('b24online/main/socialShare.html', takes_context=True)
def b2b_social_buttons(context, image, title, text):
    return {
        'image': image,
        'title': title,
        'text': text
    }


@register.inclusion_tag("centerpokupok/main/main_menu.html", takes_context=True)
def categories_menu(context):
    return {'categories': B2CProductCategory.objects.filter(level=0).order_by('name')[:8]}


@register.inclusion_tag("centerpokupok/Company/header.html", takes_context=True)
def companyMenuB2C(context, company, menu):
    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    return {
        'company': Company.objects.get(pk=company),
        'menu': menu,
        'MEDIA_URL': MEDIA_URL,
        'user': request.user
    }


@register.inclusion_tag("b24online/Products/slider.html")
def products_banner_slider():
    block = BannerBlock.objects.get(code='PRODUCT_SLIDER')
    return {
        'banners': Banner.get_active_objects().filter(block=block)
    }
