import os

from django import template
from django.conf import settings
from django.contrib.sites.models import get_current_site
from haystack.query import SearchQuerySet
from django.core.cache import cache
from django.utils.translation import get_language

from appl.models import BusinessProposal, InnovationProject, Tender, Exhibition, Requirement, Resume, Category
from b24online.models import Chamber, B2BProduct, Organization
from centerpokupok.views import _sortMenu
from appl import func
from appl.models import Cabinet, News, NewsCategories, UserSites, AdditionalPages, staticPages, Gallery, \
    Company, Tpp
from core.models import Item

register = template.Library()


@register.inclusion_tag('AdvTop/tops.html', takes_context=True)
def userSitegetTopOnPage(context):
    request = context.get('request')
    SITE_ID = get_current_site(request).pk
    MEDIA_URL = context.get('MEDIA_URL', '')

    organization = UserSites.objects.get(sites__id=SITE_ID).organization.pk

    cache_name = "%s_adv_top_cache_site_%d" % (get_language(), SITE_ID)

    cached = cache.get(cache_name)

    if not cached:
        tops, models = func.get_tops([organization])

        cache.set(cache_name, (tops, models), 60 * 10)
    else:
        tops, models = cache.get(cache_name)

    return {'MEDIA_URL': MEDIA_URL, 'modelTop': tops, 'models': models}


@register.inclusion_tag('AdvTop/tops.html', takes_context=True)
def getTopOnPage(context, item_id=None):
    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    if item_id:
        filterAdv = func.get_detail_adv_filter(item_id)
    else:
        filterAdv = func.get_list_adv_filter(request)

    cached = None
    cache_name = "%s_adv_top_cache" % get_language()

    if filterAdv is None:
        cached = cache.get(cache_name)

    if cached is None:
        models = func.get_tops(filterAdv)

        if filterAdv is None:
            cache.set(cache_name,  models, 60 * 10)
    else:
        models = cache.get(cache_name)

    return {'MEDIA_URL': MEDIA_URL, 'models': models}


@register.inclusion_tag('AdvBanner/banners.html', takes_context=True)
def get_banner(context, block, item_id=None):
    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    if item_id:
        advertisement_filter = func.get_detail_adv_filter(item_id)
    else:
        advertisement_filter = func.get_list_adv_filter(request)

    cached = False
    cache_name = "banner:%s:%s" % (block, settings.SITE_ID)

    if advertisement_filter is None:
        cached = cache.get(cache_name)

    if not cached:
        banner = func.get_banner(block, settings.SITE_ID, advertisement_filter)

        if advertisement_filter is None:
            cache.set(cache_name, banner, 60 * 10)
    else:
        banner = cache.get(cache_name)

    return {'MEDIA_URL': MEDIA_URL, 'banner': banner}


@register.inclusion_tag('main/currentCompany.html', takes_context=True)
def getMyCompaniesList(context):
    request = context.get('request')

    if not request.user or request.user.is_anonymous() or not request.user.is_authenticated():
        return { 'current_company': None }

    current_company = request.session.get('current_company', None)

    if current_company:
        item = Organization.objects.get(pk=current_company)

        if not item.has_perm(request.user):
            request.session['current_company'] = None
            current_company = None

    if current_company is None:
        if request.user.profile:
            current_company = request.user.profile
        else:
            current_company = request.user.email

    return {
        'current_company': current_company
    }


@register.inclusion_tag('main/contextMenu.html', takes_context=True)
def setContextMenu(context, obj, **kwargs):
    current_path = context.get('current_path')
    model_name = context.get('model', None)
    request = context.get('request')
    update_url = None

    url_namespace = None
    set_current = False
    delete = True

    if model_name == BusinessProposal.__name__:
        url_namespace = "proposal"
    elif model_name == B2BProduct.__name__:
        url_namespace = "products"
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
        url_namespace = "news"
    elif model_name == Company.__name__:
        set_current = True
        url_namespace = "companies"
    elif model_name == Chamber.__name__:
        set_current = True
        url_namespace = "tpp"
        delete = False

    vars = {
        'obj': obj,
        'url_namespace': url_namespace,
        'current_path': current_path,
        'set_current': set_current,
        'update_url': update_url,
        'delete': delete
    }

    has_perm = getattr(obj, 'has_perm', None)

    if has_perm is None or url_namespace is None:
        vars['has_perm'] = None
    else:
        vars['has_perm'] = has_perm(request.user)

    vars.update(kwargs)

    return vars


@register.inclusion_tag('main/user_profile.html', takes_context=True)
def userProfile(context):
    request = context.get('request')
    cabinetValues = func.getB2BcabinetValues(request)
    MEDIA_URL = context.get('MEDIA_URL', '')

    return {
        'MEDIA_URL': MEDIA_URL,
        'cabinetValues': cabinetValues
    }


@register.inclusion_tag('News/last.html', takes_context=True)
def getLastNews(context):
    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    news = list(
        News.active.get_active().filter(c2p__parent__in=NewsCategories.objects.all()).order_by('-pk').values_list('pk',
                                                                                                                  flat=True)[
        :3])
    newsValues = Item.getItemsAttributesValues(('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG'), news)

    return {'MEDIA_URL': MEDIA_URL, 'newsValues': newsValues}


@register.inclusion_tag('slider.html', takes_context=True)
def getUserSiteSlider(context):
    request = context.get('request')

    import glob

    user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
    photos = Gallery.objects.filter(c2p__parent=user_site)
    if not photos.exists():
        user_site_slider = user_site.getAttributeValues("TEMPLATE")
        file_count = 0
        if len(user_site_slider) > 0:
            user_site_slider = user_site_slider[0]

            slider_dir = 'tppcenter/img/templates/' + user_site_slider

            dir = os.path.join(settings.MEDIA_ROOT, slider_dir).replace('\\', '/')

            file_count = len(glob.glob(dir + "/*.jpg"))

        return {'file_count': file_count, 'user_site_slider': user_site_slider, 'custom_slider': False}

    else:
        media_url = settings.MEDIA_URL
        return {'photos': photos, 'media_url': media_url, 'custom_slider': True}


@register.inclusion_tag('header.html', takes_context=True)
def getUserSitTopMenu(context):
    path = context['request'].path.split('/')
    languages = [lan[0] for lan in settings.LANGUAGES]
    url_parameter = []

    additionalPages_url = 'additionalPage'
    about_us_url = 'about_us'
    if len(path) > 0:
        if path[1] in languages:
            url_parameter = path[1]

            additionalPages_url = 'additionalPage_lang'
            about_us_url = 'about_us_lang'

    midea_url = settings.MEDIA_URL

    user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
    organization = user_site.organization.pk

    additionalPages = AdditionalPages.objects.filter(c2p__parent=organization).values_list('pk', flat=True)
    addPagesValues = Item.getItemsAttributesValues(('NAME',), additionalPages)

    return {'addPagesValues': addPagesValues, 'midea_url': midea_url, 'url_parameter': url_parameter,
            'additionalPages_url': additionalPages_url, 'about_us_url': about_us_url}


@register.inclusion_tag('site_sidebar.html', takes_context=True)
def getUserSiteMenu(context):
    path = context['request'].path.split('/')
    languages = [lan[0] for lan in settings.LANGUAGES]
    url_parameter = []
    news_url = 'news:main'
    main_url = 'main'
    proposal_url = 'proposal:main'
    products_url = 'products:main'
    contact_url = 'contact:main'
    structure_url = 'structure:main'

    if len(path) > 0:
        if path[1] in languages:
            url_parameter = path[1]
            news_url = "news_lang:main"
            main_url = 'main_lang'
            proposal_url = 'proposal_lang:main'
            products_url = 'products_lang:main'
            contact_url = 'contact_lang:main'
            structure_url = 'structure_lang:main'

    midea_url = settings.MEDIA_URL

    return {'midea_url': midea_url, 'url_parameter': url_parameter,
            "news_url": news_url, 'main_url': main_url, 'proposal_url': proposal_url, 'products_url': products_url,
            "contact_url": contact_url, 'structure_url': structure_url}


@register.inclusion_tag('main/staticPages.html')
def showStaticPages():
    cache_name = "%s_static_pages_all_bottom" % get_language()

    cached = cache.get(cache_name)

    if not cached:

        pages = [page.pk for page in staticPages.objects.all()]

        pageWithAttr = Item.getItemsAttributesValues(('SLUG', 'NAME'), pages)

        pages = {}

        for page in staticPages.objects.all():

            name = pageWithAttr[page.pk].get('NAME', [""])[0]
            slug = pageWithAttr[page.pk].get('SLUG', [""])[0]

            if page.pageType not in pages:
                pages[page.pageType] = []

            pages[page.pageType].append((slug, name))

            cache.set(cache_name, pages, 60 * 60 * 24 * 7)
    else:
        pages = cache.get(cache_name)

    return {'pagesDict': pages}


@register.inclusion_tag('main/topStaticPages.html')
def showTopStaticPages():
    cache_name = "%s_static_pages_all_top" % get_language()
    cached = cache.get(cache_name)

    if not cached:

        pages = [page.pk for page in staticPages.objects.filter(onTop=True)]

        pageWithAttr = Item.getItemsAttributesValues(('SLUG', 'NAME'), pages)
        cache.set(cache_name, pageWithAttr, 60 * 60 * 24 * 7)

    else:
        pageWithAttr = cache.get(cache_name)

    return {'pagesDict': pageWithAttr}


@register.inclusion_tag('main/socialShare.html', takes_context=True)
def b2bSocialButtons(context, image, title, text):
    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    return {'MEDIA_URL': MEDIA_URL, 'image': image, 'title': title, 'text': text}


@register.inclusion_tag("main/main_menu.html", takes_context=True)
def mainMenuB2C(context):
    lang = settings.LANGUAGE_CODE
    cache_name = "b2c_menu_%s" % lang

    sortedHierarchyStructure = cache.get(cache_name)

    if not sortedHierarchyStructure:

        # ----MAIN MENU AND CATEGORIES IN HEADER ------#
        hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
        categories_id = [cat['ID'] for cat in hierarchyStructure]
        categories = Item.getItemsAttributesValues(("NAME",), categories_id)

        sortedHierarchyStructure = _sortMenu(hierarchyStructure) if len(hierarchyStructure) > 0 else {}
        level = 0

        for node in sortedHierarchyStructure:
            node['pre_level'] = level
            node['item'] = categories[node['ID']]
            node['parent_item'] = categories[node['PARENT_ID']] if node['PARENT_ID'] is not None else ""
            level = node['LEVEL']

        cache.set(cache_name, sortedHierarchyStructure, 60 * 60 * 24 * 7)

    return {'sortedHierarchyStructure': sortedHierarchyStructure}


@register.inclusion_tag("Company/header.html", takes_context=True)
def companyMenuB2C(context, company, menu):
    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    return {
        'company': SearchQuerySet().models(Company).filter(django_id=company)[0],
        'menu': menu,
        'MEDIA_URL': MEDIA_URL,
        'user': request.user
    }
