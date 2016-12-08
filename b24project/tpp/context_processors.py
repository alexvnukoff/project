from b24online.utils import get_current_organization
from tpp.DynamicSiteMiddleware import get_current_site
from django.conf import settings


def site_processor(request):
    return {'site': get_current_site()}


def current_organization_processor(request):
    return {
        'current_organization': get_current_organization(request)
    }


def site_languages_processor(request):
    LANGUAGES = settings.LANGUAGES

    try:
        site_languages = get_current_site().user_site.languages
    except:
        site_languages = None

    if site_languages:
        obj = []
        for code, lang in LANGUAGES:
            if code in site_languages:
                obj.append((code, lang))
    else:
        obj =  LANGUAGES

    return {
        'get_site_languages': obj
    }
