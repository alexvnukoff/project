from django.contrib.sites.models import Site
from django.conf import settings
from threading import current_thread
import os
from django.http import HttpResponseBadRequest

class SiteUrlMiddleWare:

    def process_request(self, request):

        domains = {'centerpokupok.com': 'centerpokupok.ru'}

        current_domain = request.META.get('HTTP_HOST', False)

        if current_domain is False:
            return HttpResponseBadRequest()
        
        if current_domain[:4] == "www":
            current_domain = current_domain[4:]
        try:
            if domains.get(current_domain, False):
                site = Site.objects.get(domain=domains.get(current_domain))
            else:
                site = Site.objects.get(domain=current_domain)

            settings.SITE_ID = site.pk
            settings.ROOT_URLCONF = str(site.name)+".urls"
            request.urlconf = str(site.name)+".urls"
            settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),
                     os.path.join(os.path.dirname(__file__), '..', str(site.name)+'/templates').replace('\\', '/'), )


        except Site.DoesNotExist:
            settings.SITE_ID = 1
            request.urlconf = "tppcenter.urls"
            settings.ROOT_URLCONF = "tppcenter.urls"
            settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),
                     os.path.join(os.path.dirname(__file__), '..', 'tppcenter/templates').replace('\\', '/'), )




class GlobalRequest(object):
    _requests = {}

    @staticmethod
    def get_request():
        try:
                return GlobalRequest._requests[current_thread()]
        except KeyError:
                return None

    def process_request(self, request):
        GlobalRequest._requests[current_thread()] = request

    def process_response(self, request, response):
        # Cleanup
        thread = current_thread()
        try:
            del GlobalRequest._requests[thread]
        except KeyError:
            pass
        return response

def get_request():
    return GlobalRequest.get_request()

