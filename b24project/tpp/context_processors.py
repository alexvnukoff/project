from tpp.DynamicSiteMiddleware import get_current_site


def site_processor(request):
    return {'site': get_current_site()}
