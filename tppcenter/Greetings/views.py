from appl import func
from appl.models import Greeting
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _, get_language, trans_real
from django.template import RequestContext, loader

def get_greetings_list(request, page=1, item_id=None, slug=None):

    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    scripts = []

    try:
        if not item_id:
            greetingPage = _getContent(request, page)

        else:
            greetingPage, meta = _getdetailcontent(request, item_id)

    except ObjectDoesNotExist:
        greetingPage = func.emptyCompany()

    current_section = _("Greetings")

    templateParams = {
        'current_section': current_section,
        'greetingPage': greetingPage,
        'scripts': scripts,
        'styles': styles
    }

    if item_id:
        templateParams['meta'] = meta

    return render_to_response("Greetings/index.html", templateParams, context_instance=RequestContext(request))

def _getdetailcontent(request, item_id):

    cache_name = "%s_detail_%s" % (get_language(), item_id)
    cached = cache.get(cache_name)

    if not cached:
        greeting = get_object_or_404(Greeting, pk=item_id)
        greetingValues = greeting.getAttributeValues('NAME', 'DETAIL_TEXT', 'IMAGE', 'POSITION', 'TPP')

        template = loader.get_template('Greetings/detailContent.html')

        templateParams = {
            'greetingValues': greetingValues,
            'item_id': item_id
        }

        context = RequestContext(request, templateParams)
        rendered = template.render(context)
        meta = func.getItemMeta(request, greetingValues)

        cache.set(cache_name, [rendered, meta], 60*60*24*7)
    else:
        rendered, meta = cache.get(cache_name)

    return rendered, meta

def _getContent(request, page):

    cached = False
    cache_name = "%s_greeting_list_result_page_%s" % (get_language(), page)

    if not request.user.is_authenticated():
        cached = cache.get(cache_name)

    if not cached:
        greetings = Greeting.objects.all()
        url_paginator = "greetings:paginator"
        attr = ('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG', 'POSITION', 'TPP')

        result = func.setPaginationForItemsWithValues(greetings, *attr, page_num=7, page=page)
        greetingList = result[0]

        page = result[1]
        paginator_range = func.getPaginatorRange(page)

        template = loader.get_template('Greetings/contentPage.html')

        templateParams = {
            'greetingList': greetingList,
            'page': page,
            'paginator_range': paginator_range,
            'url_paginator': url_paginator
        }

        context = RequestContext(request, templateParams)
        rendered = template.render(context)

        if not request.user.is_authenticated():
            cache.set(cache_name, rendered, 60 * 5)

    else:
        rendered = cache.get(cache_name)

    return rendered
