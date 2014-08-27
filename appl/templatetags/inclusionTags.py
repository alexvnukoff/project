import os

from django import template
from django.conf import settings

from appl.models import Cabinet, Organization, News, NewsCategories, UserSites, AdditionalPages, staticPages, Gallery,\
    BusinessProposal, Product, InnovationProject, Tender, Exhibition, Requirement, Resume, Company, Tpp, TppTV
from core.models import Item

from haystack.query import SearchQuerySet
from django.db.models import Q
from django.core.cache import cache
from django.utils.translation import get_language

from appl import func
from appl.models import Cabinet, Organization, News, NewsCategories, UserSites, AdditionalPages, staticPages, Gallery, \
    Company, Tpp
from core.models import Item


register = template.Library()

@register.inclusion_tag('AdvTop/tops.html', takes_context=True)
def getTopOnPage(context, item_id=None):

    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    if item_id:
        filterAdv = func.getDeatailAdv(item_id)
    else:
        filterAdv = func.getListAdv(request)


    cached = False
    cache_name = "%s_adv_top_cache" % get_language()

    if filterAdv is None:
        cached = cache.get(cache_name)

    if not cached:
        tops, models = func.getTops(request, filterAdv)

        if filterAdv is None:
            cache.set(cache_name, (tops, models), 60 * 10)
    else:
        tops, models = cache.get(cache_name)

    return {'MEDIA_URL': MEDIA_URL,  'modelTop': tops, 'models': models}

@register.inclusion_tag('AdvBanner/banners.html', takes_context=True)
def getBanners(context, item_id=None, *places):

    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    if item_id:
        filterAdv = func.getDeatailAdv(item_id)
    else:
        filterAdv = func.getListAdv(request)

    cached = False
    cache_name = "%s_adv_banner_cache" % get_language()

    if filterAdv is None:
        cached = cache.get(cache_name)

    if not cached:
        banners = func.getBanners(places, settings.SITE_ID, filterAdv)

        if filterAdv is None:
            cache.set(cache_name, banners, 60 * 10)
    else:
        banners = cache.get(cache_name)


    return {'MEDIA_URL': MEDIA_URL, 'banners': banners}

@register.inclusion_tag('main/currentCompany.html', takes_context=True)
def getMyCompaniesList(context):

    request = context.get('request')

    current_company = request.session.get('current_company', False)

    cab = Cabinet.objects.get(user=request.user)

    if current_company is not False:
        if Organization.objects.filter(Q(create_user=request.user, department=None) |
                                        Q(p2c__child__p2c__child__p2c__child=cab.pk), pk=current_company).exists():
            current_company = SearchQuerySet().models(Tpp, Company).filter(django_id=current_company)[0].title
        else:
            current_company = False

    if current_company is False:
        cabinet = SearchQuerySet().models(Cabinet).filter(django_id=cab.pk)[0]

        if not cabinet.text:
            current_company = request.user.email
        else:
            current_company = cabinet.text

    return {
        'current_company': current_company
    }

@register.inclusion_tag('main/contextMenu.html', takes_context=True)
def setContextMenu(context, obj):

    items_perms = context.get('items_perms')
    current_path = context.get('current_path')
    model_name = context.get('model', None)


    delete_perm = "delete_" + model_name.lower()
    change_perm = "change_" + model_name.lower()
    top_perm = ""
    url_namespace = ""
    set_current = False

    if model_name == BusinessProposal.__name__:
        top_perm = "add_advtop"
        url_namespace = "proposal"
    elif model_name == Product.__name__:
        top_perm = "add_advtop"
        url_namespace = "products"
    elif model_name == InnovationProject.__name__:
        top_perm = "add_advtop"
        url_namespace = "innov"
    elif model_name == Tender.__name__:
        url_namespace = "tenders"
    elif model_name == Exhibition.__name__:
        top_perm = "add_advtop"
        url_namespace = "exhibitions"
    elif model_name == Requirement.__name__:
       top_perm = "add_advtop"
       url_namespace = "vacancy"
    elif model_name == Resume.__name__:
       url_namespace = "resume"
    elif model_name == News.__name__:
       url_namespace = "news"
       top_perm = "add_advtop"
    elif model_name == Company.__name__:
       top_perm = "add_advtop"
       set_current = True
       url_namespace = "companies"
    elif model_name == Tpp.__name__:
       top_perm = "add_advtop"
       set_current = True
       url_namespace = "tpp"
       delete_perm = False
    elif model_name == TppTV.__name__:
       url_namespace = "tv"






    vars = {
        "delete_perm": delete_perm,
        'change_perm': change_perm,
        "top_perm": top_perm,
        'obj': obj,
        'url_namespace': url_namespace,
        "items_perms": items_perms,
        'current_path':current_path,
        'set_current': set_current,
    }

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

    news = list(News.active.get_active().filter(c2p__parent__in=NewsCategories.objects.all()).order_by('-pk').values_list('pk', flat=True)[:3])
    newsValues = Item.getItemsAttributesValues(('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG'), news)



    return {'MEDIA_URL': MEDIA_URL,  'newsValues': newsValues }


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

            file_count = len(glob.glob(dir+"/*.jpg"))




        return {'file_count':file_count ,  'user_site_slider': user_site_slider, 'custom_slider': False}

    else:
         media_url = settings.MEDIA_URL
         return {'photos':photos , 'media_url': media_url, 'custom_slider': True}


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

    return {'addPagesValues': addPagesValues, 'midea_url': midea_url, 'url_parameter':  url_parameter,
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

    return { 'midea_url': midea_url, 'url_parameter':  url_parameter,
            "news_url": news_url, 'main_url': main_url, 'proposal_url': proposal_url, 'products_url': products_url,
            "contact_url": contact_url,'structure_url': structure_url}

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
