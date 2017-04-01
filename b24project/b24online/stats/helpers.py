# -*- encoding: utf-8 -*-

"""
The helpers for events stats processing.
"""

import datetime
import hashlib
import logging
import os
import re

import geoip2.database
import maxminddb
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import smart_str
from django.utils.functional import cached_property
from geoip2.errors import AddressNotFoundError

from b24online.models import RegisteredEventType
from b24online.stats import InconsistentDataError
from b24online.stats.utils import glue, get_redis_connection

logger = logging.getLogger(__name__)

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

    _state = {}

    def __new__(cls, *p, **k):
        self = object.__new__(cls)
        self.__dict__ = cls._state
        return self

    @cached_property
    def city_reader(self):
        return geoip2.database.Reader(os.path.join(self.gi_db_path, 'GeoLite2-City.mmdb'))

    @cached_property
    def country_reader(self):
        return geoip2.database.Reader(os.path.join(self.gi_db_path, 'GeoLite2-Country.mmdb'))

    @cached_property
    def gi_db_path(self):
        return getattr(settings, 'GEOIP_DB_PATH', None)

    @staticmethod
    def is_valid_ip(ip_str):
        """
        Check the validity of an IPv4 address
        """
        match = re.match("^(\d{0,3})\.(\d{0,3})\.(\d{0,3})\.(\d{0,3})$", ip_str)
        if not match:
            return False
        quad = []
        for number in match.groups():
            quad.append(int(number))
        if quad[0] < 1:
            return False
        for number in quad:
            if number > 255 or number < 0:
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
        try:
            return cls().city_reader.city(ip)
        except (maxminddb.InvalidDatabaseError, AddressNotFoundError):
            return cls().country_reader.country(ip)
        except (maxminddb.InvalidDatabaseError, AddressNotFoundError):
            return None

    @staticmethod
    def get_random_ip():
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

    ready_to_process = glue('registered', 'events', 'ready')
    geo_data_key = glue('registered', 'events', 'geo_data')
    already_key = glue('registered', 'events', 'already')

    @classmethod
    def get_request_key(cls, request_uuid, affix):
        """
        Return events query key for the HTTPRequest instance
        """

        return glue('registered', 'events',
                    datetime.date.today().strftime('%Y-%m-%d'),
                    request_uuid, affix)

    @classmethod
    def get_stored_event(cls, instance, event_type_slug):
        """
        Return the key for Instance and EventType
        """
        assert isinstance(instance, models.Model), 'Invalid parameter'
        try:
            content_type = ContentType.objects.get_for_model(instance)
            event_type = RegisteredEventType.objects.get(
                slug=event_type_slug)
        except (RegisteredEventType.DoesNotExist, AttributeError) as exc:
            err_msg = 'Error: %s' % exc
            logger.error(err_msg)
            raise InconsistentDataError(err_msg)
        else:
            return [event_type.pk, content_type.pk, instance.pk]

    @classmethod
    def register(cls, event_stored_data, request):
        """
        Store the Event in Redis queue.
        """
        event_stored_key = glue('registered', 'event', event_stored_data)
        request_uuid = getattr(request, '_uuid', None)
        if request_uuid:
            events_queue_key = cls.get_request_key(request_uuid, 'queue')
            if events_queue_key:
                rconn = get_redis_connection()
                rconn.lpush(events_queue_key, event_stored_key)

    @classmethod
    def get_unique_key(cls, extra_data):
        """
        Return the unique key based on instance, IP and UA.
        """
        ip = extra_data.get('ip_address')
        ua = extra_data.get('user_agent')
        if all((ip, ua)):
            meaning_data = (ip, ua)
            key_str_raw = ':'.join(map(smart_str, meaning_data))
            key_str = key_str_raw.encode('utf-8')
            return hashlib.md5(key_str).hexdigest()
        return None

    @classmethod
    def get_geoip_info_key(cls, extra_data):
        key_data = []

        if 'country' in extra_data and extra_data['country'] != 'None':
            key_data.append(extra_data['country'].get('is_code', '').strip())
            key_data.append(extra_data['country']['names'].get('en', '').strip())
        else:
            key_data += ['undef', 'undef']

        if 'city' in extra_data and extra_data['city'] != 'None':
            key_data.append(extra_data['city']['names'].get('en', '').strip())
        else:
            key_data.append('undef')

        return glue(key_data)
