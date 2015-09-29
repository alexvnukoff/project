from django.conf import settings
from django.contrib.sites.models import SITE_CACHE, Site
from django.http import HttpResponse, HttpResponseBadRequest


class DynamicSiteMiddleware(object):
    def process_request(self, request):
        host = request.get_host()

        if host not in SITE_CACHE:
            site = self._get_site_from_host(host)

            if site is None:
                return HttpResponseBadRequest()
            else:
                SITE_CACHE[host] = site

            return site

        site = self._get_site_from_host(request)

        if isinstance(site, HttpResponse):
            return site

    @staticmethod
    def _get_site_from_host(host):
        if not host:
            return HttpResponseBadRequest()

        host = host.lower().split(':')[0]

        if not host:
            return HttpResponseBadRequest()

        languages = [lan[0] for lan in settings.LANGUAGES]

        host = host.split('.')

        if host[0] == 'www':
            host.pop(0)

        lang = host[0]

        if lang in languages:
            host.pop(0)

        host = '.'.join(host)

        try:
            site = Site.objects.get(domain__iexact=host)
        except Site.DoesNotExist:
            return None

        return site
