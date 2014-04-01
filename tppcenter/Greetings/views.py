from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from core.models import Item
from appl import func
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.conf import settings

def get_greetings_list(request, page=1, item_id=None, slug=None):

    description = ""
    title = ""

    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    scripts = []

    try:
        if not item_id:
            attr = ('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG')
            greetingPage = func.setContent(request, Greeting, attr, 'greetings', 'Greetings/contentPage.html', 5, page=page)

        else:
            result = _getdetailcontent(request, item_id)
            greetingPage = result[0]
            description = result[1]
            title = result[2]

    except ObjectDoesNotExist:
        greetingPage = func.emptyCompany()

    cabinetValues = func.getB2BcabinetValues(request)

    current_section = _("Greetings")

    templateParams = {
        'current_section': current_section,
        'title': title,
        'greetingPage': greetingPage,
        'scripts': scripts,
        'styles': styles,
        'cabinetValues': cabinetValues,
        'description': description,
    }

    return render_to_response("Greetings/index.html", templateParams, context_instance=RequestContext(request))

def _getdetailcontent(request, item_id):

    cache_name = "detail_%s" % item_id
    description_cache_name = "description_%s" % item_id

    cached = cache.get(cache_name)

    if not cached:
        new = get_object_or_404(News, pk=item_id)
        greetingValues = new.getAttributeValues('NAME', 'DETAIL_TEXT', 'IMAGE')
        description = greetingValues.get('DETAIL_TEXT', False)[0] if greetingValues.get('DETAIL_TEXT', False) else ""

        description = func.cleanFromHtml(description)

        title = greetingValues.get('NAME', False)[0] if greetingValues.get('NAME', False) else ""

        template = loader.get_template('Greetings/detailContent.html')

        templateParams = {
            'greetingValues': greetingValues,
            'item_id': item_id
        }

        context = RequestContext(request, templateParams)
        rendered = template.render(context)
        cache.set(cache_name, rendered, 60*60*24*7)
        cache.set(description_cache_name, (description, title), 60*60*24*7)

    else:
        rendered = cache.get(cache_name)
        result = cache.get(description_cache_name)
        description = result[0]
        title = result[1]

    return rendered, description, title