# -*- encoding: utf-8 -*-

"""
The helpers for events stats processing.
"""

import os
import socket
import random
import struct
import datetime
import logging
import uuid
import GeoIP

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from b24online.models import RegisteredEventType
from b24online.stats import InconsistentDataError
from b24online.stats.utils import glue, get_redis_connection


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
            err_msg = 'Error: %s' % esc
            logger.error(err_msg)
            raise InconsistentDataError(err_msg)
        else:
            return glue('registered', 'event', 
                event_type.pk, content_type.pk, instance.pk)

    @classmethod
    def register(cls, event_stored_key, request):
        """
        Store the Event in Redis queue.
        """
        request_uuid = getattr(request, '_uuid', None)
        if request_uuid:
            events_queue_key = cls.get_request_key(request_uuid, 'queue')
            if events_queue_key:
                rconn = get_redis_connection()
                rconn.lpush(events_queue_key, event_stored_key)
