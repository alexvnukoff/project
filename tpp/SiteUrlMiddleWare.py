from threading import current_thread
import os
import sys

from django.contrib.sites.models import Site

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.utils import translation
from django.views.debug import technical_500_response
from django.conf import settings
from django.core.cache import cache


class UserBasedExceptionMiddleware(object):
    '''
        Show django stack trace when it's our IP
    '''

    def process_exception(self, request, exception):
        if request.user.is_superuser or request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return technical_500_response(request, *sys.exc_info())


class SiteUrlMiddleWare:

    '''
        Set requested site ( we have 3: UserSites, B2B and B2C) by domain
    '''

    def process_request(self, request):

        current_domain = request.get_host()
        languages = [lan[0] for lan in settings.LANGUAGES]

        if not current_domain:
            return HttpResponseBadRequest()

        current_domain = current_domain.split('.')

        if current_domain[0] == 'www':
            current_domain.pop(0)

        lang = current_domain[0]

        if lang in languages: #remove lang sub domain
            current_domain.pop(0)

        current_domain = '.'.join(current_domain)

        cache_name = 'site_domain_%s' % current_domain

        cached = cache.get(cache_name)

        if not cached:

            try:
                site = Site.objects.get(domain=current_domain)
            except Site.DoesNotExist:
                return HttpResponseBadRequest()

            cached = {
                'pk': site.pk,
                'name': str(site.name)
            }

            cache.set(cache_name, cached)

        settings.SITE_ID = cached.get('pk', None)
        settings.ROOT_URLCONF = cached.get('name', 'tppcenter') + ".urls"
        request.urlconf = cached.get('name', 'tppcenter') + ".urls"

        settings.TEMPLATE_DIRS = (
            #os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),
            os.path.join(os.path.dirname(__file__), '..', cached.get('name', 'tppcenter'), 'templates').replace('\\', '/')
        )

        SITE_THREAD_LOCAL = local()
        SITE_THREAD_LOCAL.ROOT_URLCONF = "%s.urls" % str(site.name)
        SITE_THREAD_LOCAL.SITE_ID = site.pk

        Site.objects.clear_cache()

class SiteLangRedirect:

    '''
        Redirect to lang sub domain
    '''

    def process_request(self, request):
        lang = request.get_host().split('.')[0]
        languages = [lan[0] for lan in settings.LANGUAGES]
        userLang = getattr(request, 'LANGUAGE_CODE', None)

        if lang not in languages and userLang and userLang in languages and settings.SITE_ID:

            cache_name = 'site_pk_%s' % settings.SITE_ID

            domain = cache.get(cache_name)

            if not domain:
                site = Site.objects.get(pk=settings.SITE_ID)
                domain = site.domain
                cache.set(cache_name, domain)
            protocol = 'http' if not request.is_secure() else 'https'
            
            return HttpResponseRedirect(protocol + '://' + request.LANGUAGE_CODE + '.' + domain + request.get_full_path())


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
            settings.LANGUAGE_CODE = lang

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

