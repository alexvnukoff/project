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
    if obj == 'az':
        return country['Azerbaydjan']
    elif obj == 'am':
        return country['Armenia']
    elif obj == 'by':
        return country['Belarus']
    elif obj == 'ge':
        return country['Georgia']
    elif obj == 'il':
        return country['Israel']
    elif obj == 'kz':
        return country['Kazakhstan']
    elif obj == 'kg':
        return country['Kyrgyzstan']
    elif obj == 'lv':
        return country['Latvia']
    elif obj == 'lt':
        return country['Lithuania']
    elif obj == 'md':
        return country['Moldova']
    elif obj == 'ru':
        return country['Russia']
    elif obj == 'us':
        return country['USA']
    elif obj == 'ua':
        return country['Ukraine']
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
                geo_info = geo.get_geoip_data(ip)
            except KeyError:
                geo_info = None
                request.session['geo_country'] = None

            if geo_info:
                request.session['geo_country'] = get_main_c(geo_info.country.iso_code.lower())
            else:
                request.session['geo_country'] = None

        request.session.modified = True
        return None

