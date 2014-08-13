from django.contrib.sites.models import Site
from django.conf import settings
from threading import current_thread
import os
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.http.response import HttpResponseRedirectBase
from django.utils import translation

class SiteUrlMiddleWare:


    def process_request(self, request):

        domains = {'centerpokupok.com': 'centerpokupok.ru'}

        current_domain = request.get_host()

        if not current_domain:
            return HttpResponseBadRequest()

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

            lang = current_domain.split('.')[0]
            languages = [lan[0] for lan in settings.LANGUAGES]

            if lang and lang in languages:
                #TODO this string was commented for debugging of categories. Check indirect impact.
                #settings.SITE_ID = 143
                site = Site.objects.get(domain=current_domain[3:])
                settings.SITE_ID = site.pk

                request.urlconf = "tppcenter.urls"
                settings.ROOT_URLCONF = "tppcenter.urls"
                settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),
                         os.path.join(os.path.dirname(__file__), '..', 'tppcenter/templates').replace('\\', '/'), )
            elif request.LANGUAGE_CODE and request.LANGUAGE_CODE in languages:
                site = Site.objects.get(pk=143)
                return HttpResponseRedirect('http://' + request.LANGUAGE_CODE + '.' + site.domain)
            else:
                site = Site.objects.get(pk=143)
                return HttpResponseRedirect('http://' + site.domain)


class UserSitesMiddleWare:

    def process_request(self, request):

        if settings.SITE_ID is None:

            current_domain = request.META.get('HTTP_HOST', False)
            
            if current_domain is False:
                return HttpResponseBadRequest()

            if current_domain[:4] == "www.":
                current_domain = current_domain[4:]

            try:
                site = Site.objects.get(domain=current_domain)
                settings.SITE_ID = site.pk
            except Site.DoesNotExist:
                return HttpResponseNotFound()

class SubdomainLanguageMiddleware(object):
    """
    Set the language for the site based on the subdomain the request
    is being served on. For example, serving on 'fr.domain.com' would
    make the language French (fr).
    """
    LANGUAGES = [lan[0] for lan in settings.LANGUAGES]

    def process_request(self, request):
        host = request.get_host().split('.')

        if host and host[0] in self.LANGUAGES:
            lang = host[0]
            translation.activate(lang)
            request.LANGUAGE_CODE = lang

class LocaleMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context. This allows pages to be dynamically
    translated to the language the user desires (if the language
    is available, of course).
    """

    def process_request(self, request):

       settings.LANGUAGE_CODE = 'ru'
       url = request.META.get('HTTP_HOST', False)
       lang = url.split('.')[0] if url else None
       path = request.path.split('/')
       languages = [lan[0] for lan in settings.LANGUAGES]



       if lang:
            if lang in languages:
                 settings.LANGUAGE_CODE = lang
       if len(path) > 0:
            if path[1] in languages:
                settings.LANGUAGE_CODE = path[1]

       translation.activate(settings.LANGUAGE_CODE)

    def process_response(self, request, response):
        translation.deactivate()

        return response



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

