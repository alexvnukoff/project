# -*- encoding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseBadRequest
from b24online.stats.helpers import GeoIPHelper

logger = logging.getLogger(__name__)
geo = GeoIPHelper()


def get_main_c(obj):
    country = settings.GEO_COUNTRY_DB

    # Conditions for countries
    # http://dev.maxmind.com/geoip/legacy/codes/iso3166/
    if obj == 'il':
        return country['Israel']
    elif obj == 'ru' or 'kz':
        return country['Russia']
    else:
        return None


class GeolocationMiddleware(object):
    def process_request(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if geo.is_valid_ip(ip):
            request.session['geo_ip'] = ip

            try:
                geo_info = geo.get_geoip_data('62.90.75.68')
            except KeyError:
                geo_info = False
                request.session['geo_country'] = None

            if geo_info:
                request.session['geo_country'] = get_main_c(geo_info['country_code'].lower())
            else:
                request.session['geo_country'] = None

        request.session.modified = True
        return None

