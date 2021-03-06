import threading
import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseBadRequest

logger = logging.getLogger(__name__)

def get_current_site():
    return DynamicSiteMiddleware.get_site()


class DynamicSiteMiddleware(object):
    __sites = {}

    def process_request(self, request):
        host = request.get_host()
        site = self._get_site_from_host(host)

        if isinstance(site, HttpResponse):
            return site

        if site is None:
            return HttpResponseBadRequest()

        self.__class__.set_site(site)

    def process_response(self, request, response):
        self.__class__.del_site()

        return response

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

    @classmethod
    def get_site(cls):
        return cls.__sites.get(threading.current_thread())

    @classmethod
    def set_site(cls, site):
        cls.__sites[threading.current_thread()] = site
        if hasattr(site, 'pk') and not getattr(settings, 'SITE_ID', None):
            settings.SITE_ID = site.pk

    @classmethod
    def del_site(cls):
        _site_id = getattr(settings, 'SITE_ID', None)
        _current_thread = threading.current_thread()
        if _site_id and cls.__sites.get(_current_thread) == _site_id:
            settings.SITE_ID = None
        cls.__sites.pop(_current_thread, None)
