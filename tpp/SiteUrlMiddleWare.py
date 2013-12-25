from django.contrib.sites.models import Site
from django.conf import settings

class SiteUrlMiddleWare:

    def process_request(self, request):
        current_domain = request.META['HTTP_HOST']
        if current_domain[:4] == "www":
            current_domain = current_domain[4:]
        try:
            site = Site.objects.get(domain=current_domain)
            settings.SITE_ID = site.pk
        except Site.DoesNotExist:
            settings.SITE_ID = 1