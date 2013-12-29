from django.contrib.sites.models import Site
from django.conf import settings
import os



class SiteUrlMiddleWare:

    def process_request(self, request):
        current_domain = request.META['HTTP_HOST']
        if current_domain[:4] == "www":
            current_domain = current_domain[4:]
        try:
            site = Site.objects.get(domain=current_domain)

            settings.SITE_ID = site.pk
            settings.ROOT_URLCONF = str(site.name)+".urls"
            settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),
                     os.path.join(os.path.dirname(__file__), '..', str(site.name)+'/templates').replace('\\', '/'), )
        except Site.DoesNotExist:
            settings.SITE_ID = 1
            settings.ROOT_URLCONF = "tppcenter.urls"
            settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),
                     os.path.join(os.path.dirname(__file__), '..','tppcenter/templates').replace('\\', '/'), )

