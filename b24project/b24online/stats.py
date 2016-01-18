# -*- encoding: utf-8 -*-

"""
The helpers and utilities for events stats processing.
"""

import os
import socket
import random
import struct
import datetime
import logging
import uuid

from urllib.parse import unquote, urlparse
            
import redis
import GeoIP

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site

from b24online.models import (RegisteredEventType, RegisteredEvent)

logger = logging.getLogger(__name__)


class InvalidParameterError(Exception):
    """
    The common exception for the case of function (method) invalid parameters. 
    """



def get_connection(connection_url=None): 
    """ 
    Return the Redis connection by the connection URL.  
    """ 
    url = connection_url if connection_url else \
        getattr(settings, 'EVENT_STORE_REDIS_URL', None) 
    if not url:
        raise InvalidParameterError('Store connection URL is not defined')
    url_info = urlparse(url)
    assert url_info.scheme == 'redis', 'It\'s not Redis scheme'

    conn_params = {}
    if url_info.hostname:
        conn_params.update({'host': url_info.hostname})
    if url_info.port:
        conn_params.update({'port': url_info.port})

    path = url_info.path or ''
    path = path[1:] if path and path[0] == '/' else path
    if path:
        try:
            db_num = int(path)
        except ValueError:
            pass
        else:
            conn_params.update({'db': db_num})
    return redis.Redis(**conn_params)


class GeoIPHelper(object):
    """
    GeoIP actions wrapper.
    """
    IP_KEYS_ORDER = (
        'HTTP_X_FORWARDED_FOR',
        'HTTP_CLIENT_IP',
        'HTTP_X_REAL_IP',
        'HTTP_X_FORWARDED',
        'HTTP_X_CLUSTER_CLIENT_IP',
        'HTTP_FORWARDED_FOR',
        'HTTP_FORWARDED',
        'HTTP_VIA',
        'X_FORWARDED_FOR',
        'REMOTE_ADDR',
    )

    @staticmethod
    def is_valid_ip(ip_str):
        """
        Check the validity of an IPv4 address
        """
        try:
            socket.inet_pton(socket.AF_INET, ip_str)
        except AttributeError:
            try:
                socket.inet_aton(ip_str)
            except (AttributeError, socket.error):
                return False
            return ip_str.count('.') == 3
        except socket.error:
            return False
        return True

    @classmethod
    def get_request_ip(cls, request):
        """
        Return the real IP fetched from request META headers.
        """
        for key in cls.IP_KEYS_ORDER:
            value = request.META.get(key, '').strip()
            if value:
                ips = [ip.strip().lower() for ip in value.split(',')]
                for ip_str in ips:
                    if ip_str and cls.is_valid_ip(ip_str):
                        return ip_str
        return None
    
    @classmethod
    def get_geoip_data(cls, ip):
        """
        Return the info from GeoIP database for IP address.
        """
        geoip_data = {}
        gi_db_path = getattr(settings, 'GEOIP_DB_PATH', None)
        if gi_db_path:
            try:
                gi_city_h = GeoIP.open(
                    os.path.join(gi_db_path, 'GeoLiteCity.dat'),
                    GeoIP.GEOIP_STANDARD)
            except GeoIP.error:
                pass
            else:
                geoip_data = gi_city_h.record_by_addr(ip) or {}
                if not geoip_data:
                    try:
                        gi_country_h = GeoIP.open(
                            os.path.join(gi_db_path, 'GeoIP.dat'),
                            GeoIP.GEOIP_STANDARD)
                    except GeoIP.error:
                        pass
                    else:
                        country_code = gi_country_h.country_code_by_addr(ip)
                        if country_code:
                            geoip_data['country_code'] = country_code
        return geoip_data

    @staticmethod
    def random_ip():
        """
        Return random generated IP address.
        
        For debugging.
        """
        import random
        import socket
        import struct
        return socket.inet_ntoa(
            struct.pack('>I', random.randint(1, 0xffffffff)))


class RegisteredEventHelper(object):
    """
    Wrapper for RegisteredEvent.
    """

    def __init__(self, event, *args, **kwargs):
        assert isinstance(event, RegisteredEvent), 'Invalid parameter'
        self._event = event
        self.is_stored = bool(self._event.pk)

    @classmethod
    def get_event_smth_key(cls, request, query_type):
        """
        Return events query key for the HTTPRequest instance
        """
        request_uuid = getattr(request, '_uuid', None)
        return 'registered:events:{0}:{1}:{2}' . format(
            query_type,
            request__uuid, 
            datetime.date.today().strftime('%Y-%m-%d')) if request_uuid else None
            
    @classmethod
    def get_event_data_key(cls, request):
        """
        Return events query key for the HTTPRequest instance
        """
        return cls.get_event_smth_key(request, 'data')
            
    @classmethod
    def get_event_unique_key(cls, request):
        """
        Return events query key for the HTTPRequest instance
        """
        return cls.get_event_smth_key(request, 'unique')
        
    def register(self, request):
        cls = type(self)
        self._event.site = get_current_site(request)
        self._event.url = request.path
        self._event.username = request.META.get('REMOTE_USER')
        if getattr(settings, 'DEBUG_RANDOM_IPS', False):
            self._event.ip_address = GeoIPHelper._random_ip()
        else:
            self._event.ip_address = GeoIPHelper.get_request_ip(request)
        self._event.user_agent = request.META.get('HTTP_USER_AGENT') 
        self._event.event_hash = self._event.unique_key
        data = GeoIPHelper.get_geoip_data(self._event.ip_address) 
        self._event.event_data = dict((k, str(v)) for k, v in data.items())
        self._event.is_unique = self._event.check_is_unique()
        self.store_event()

    def store_event(self):
        self._event.save()


def process_stats_data(data, date_range):
    """
    Process comlex data from query about stats.
    """
    data_grid = []
    for event_type_id, data_1 in data.items():
        try:
            event_type = RegisteredEventType.objects.get(id=event_type_id)
        except RegisteredEventType.DoesNotExist:
            continue
        else:
            content_types = []
            add_1 = [event_type_id, event_type, content_types]
            data_grid.append(add_1)
            for content_type_id, data_2 in data_1.items():
                try:
                    content_type = ContentType.objects.get(pk=content_type_id)
                except ContentType.DoesNotExist:
                    continue
                else:
                    items = []
                    model_class = content_type.model_class()
                    model_name = model_class._meta.verbose_name \
                        or model_class.__name__
                    add_2 = [content_type_id, model_name, items]
                    content_types.append(add_2)
                    for item_id, data_3 in data_2.items():
                        try:
                            item = model_class.objects.get(pk=item_id)
                        except model_class.DoesNotExist:
                            continue
                        else:
                            idates = []
                            add_3 = [item_id, str(item), idates]
                            items.append(add_3)
                            for xdate, _ in date_range:
                                idates.append({'date': xdate, 
                                    'unique': data_3.get(xdate, {})\
                                        .get('unique', 0),
                                    'total': data_3.get(xdate, {})\
                                        .get('total', 0)})
    return data_grid


class RegisteredEventMiddleware(object):
    """
    Set the unique key for the every request
    """
    def process_request(self, request):
        setattr(request, '_uuid', str(uuid.uuid4())
