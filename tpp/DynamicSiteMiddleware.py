# coding:utf-8

"""
    Dynamic SITE ID
    ~~~~~~~~~~~~~~~

    Set the SITE_ID dynamic by the current Domain Name.

    More info: read .../django_tools/dynamic_site/README.creole

    :copyleft: 2011-2015 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from django.http import HttpResponseBadRequest, HttpResponse
import os
import sys
import warnings

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django.conf import settings
from django.contrib.sites import models as sites_models
from django.core.exceptions import MiddlewareNotUsed, ImproperlyConfigured
from django.utils import log

from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache


USE_DYNAMIC_SITE_MIDDLEWARE = getattr(settings, "USE_DYNAMIC_SITE_MIDDLEWARE", True)

logger = log.getLogger("django_tools.DynamicSite")


Site = sites_models.Site  # Shortcut


class DynamicSiteId(object):
    def __getattribute__(self, name):
        return getattr(SITE_THREAD_LOCAL.SITE_ID, name)
    def __int__(self):
        return SITE_THREAD_LOCAL.SITE_ID
    def __hash__(self):
        return hash(SITE_THREAD_LOCAL.SITE_ID)
    def __repr__(self):
        return repr(SITE_THREAD_LOCAL.SITE_ID)
    def __str__(self):
        return str(SITE_THREAD_LOCAL.SITE_ID)
    def __unicode__(self):
        return str(SITE_THREAD_LOCAL.SITE_ID)


def _clear_cache(self):
    logger.debug("Clear SITE_CACHE (The django-tools LocalSyncCache() dict)")
    SITE_CACHE.clear()


# Use the same SITE_CACHE for getting site object by host [1] and get current site by SITE_ID [2]
# [1] here in DynamicSiteMiddleware._get_site_id_from_host()
# [2] in django.contrib.sites.models.SiteManager.get_current()
SITE_CACHE = LocalSyncCache(id="DynamicSiteMiddlewareCache")
sites_models.SITE_CACHE = SITE_CACHE

SITE_THREAD_LOCAL = local()

# Use Fallback ID if host not exist in Site table. We use int() here, because
# os environment variables are always strings.
FALLBACK_SITE_ID = 1#int(getattr(os.environ, "SITE_ID", settings.SITE_ID))
logger.debug("Fallback SITE_ID: %r" % FALLBACK_SITE_ID)

# Use Fallback ID at startup before process_request(), e.g. in unittests
SITE_THREAD_LOCAL.SITE_ID = FALLBACK_SITE_ID

try:
    FALLBACK_SITE = Site.objects.fiter(name='tppcenter').first()
except Site.DoesNotExist as e:
    all_sites = Site.objects.all()
    msg = "Fallback SITE_ID %i doesn't exist: %s (Existing sites: %s)" % (
        FALLBACK_SITE_ID, e, repr(all_sites.values_list("id", "domain").order_by('id'))
    )
    logger.critical(msg)
    raise ImproperlyConfigured(msg)
#        site = Site(id=FALLBACK_SITE_ID, domain="example.tld", name="Auto Created!")
#        site.save()

settings.SITE_ID = DynamicSiteId()

# Use the same cache for Site.objects.get_current():
sites_models.SITE_CACHE = SITE_CACHE

# monkey patch for django.contrib.sites.models.SiteManager.clear_cache
sites_models.SiteManager.clear_cache = _clear_cache


class DynamicSiteMiddleware(object):
    """ Set settings.SITE_ID based on request's domain. """

    def __init__(self):
        # User must add "USE_DYNAMIC_SITE_MIDDLEWARE = True" in his local_settings.py
        # to activate this middleware
        if USE_DYNAMIC_SITE_MIDDLEWARE != True:
            logger.info("DynamicSiteMiddleware is deactivated.")
            raise MiddlewareNotUsed()
        else:
            logger.info("DynamicSiteMiddleware is active.")

    def process_request(self, request):
        # Get django.contrib.sites.models.Site instance by the current domain name:
        site = self._get_site_id_from_host(request)

        if isinstance(site, HttpResponse):
            return site

        # Save the current site
        SITE_THREAD_LOCAL.SITE_ID = site.pk
        # settings.ROOT_URLCONF = "%s.urls" % str(site.name)
        # request.urlconf = "%s.urls" % str(site.name)
        #
        # settings.TEMPLATE_DIRS = [
        #     os.path.join(settings.BASE_DIR, '..', str(site.name), 'templates').replace('\\', '/')
        # ]
        # SITE_THREAD_LOCAL.TEMPLATE_DIRS = settings.TEMPLATE_DIRS
        # SITE_THREAD_LOCAL.ROOT_URLCONF = "%s.urls" % str(site.name)


        # Put site in cache for django.contrib.sites.models.SiteManager.get_current():
        SITE_CACHE[SITE_THREAD_LOCAL.SITE_ID] = site

#        def test():
#            from django.contrib.sites.models import Site, SITE_CACHE
#            from django.conf import settings
#            print id(SITE_CACHE), SITE_CACHE
#            print "-"*79
#            for k, v in SITE_CACHE.items():
#                print k, type(k), id(k), hash(k), v
#            print "-"*79
#            print id(settings.SITE_ID), settings.SITE_ID
#            print "TEST:", Site.objects.get_current()
#        test()

    def _get_site_id_from_host(self, request):
        host = request.get_host().lower().split(':')[0]
        languages = [lan[0] for lan in settings.LANGUAGES]

        if not host:
            return HttpResponseBadRequest()

        host = host.split('.')

        if host[0] == 'www':
            host.pop(0)

        lang = host[0]

        if lang in languages: #remove lang sub domain
            host.pop(0)

        host = '.'.join(host)

        try:
            return SITE_CACHE[host]
        except KeyError:
            site = self._get_site_from_host(host)
            if site is None:
                # Fallback:
                logger.critical("Use FALLBACK_SITE !")
                site = FALLBACK_SITE
            else:
                logger.debug("Set site to %r for %r" % (site, host))
                SITE_CACHE[host] = site
            return site

    def _get_site_from_host(self, host):
        try:
            site = Site.objects.get(domain__iexact=host)
        except Site.DoesNotExist:
            return None

        return site
