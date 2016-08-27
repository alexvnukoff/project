from b24online.utils import get_current_organization
from tpp.DynamicSiteMiddleware import get_current_site


def site_processor(request):
    return {'site': get_current_site()}


def current_organization_processor(request):
    return {
        'current_organization': get_current_organization(request)
    }
