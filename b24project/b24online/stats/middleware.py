# -*- encoding: utf-8 -*-

"""
The middleware class for events stats processing.
"""

import os
import logging
import uuid
import random

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from b24online.stats.helpers import GeoIPHelper
from b24online.tasks import process_events_queue

logger = logging.getLogger(__name__)


class RegisteredEventMiddleware(object):
    """
    Set the unique key for the every request and process events queue in the
    end.
    """
    def process_request(self, request):
        """
        Set the unique key for request.
        """
        setattr(request, '_uuid', str(uuid.uuid4()))

    def process_response(self, request, response):
        """
        Process the events queue and return HTTPResponse.
        """
        # Async processing of events 
        # FIXME: (andrey_k) maybe necessary use smth like USE_CELERY?
        
        # For debug
        ips = ['111.171.130.29', '51 159.8.161.4', '51 95.110.96.67',
               '95.110.96.67']
        request_uuid = getattr(request, '_uuid', None)
        if request_uuid:
            
            _ip = GeoIPHelper.get_random_ip() \
                    if getattr(settings, 'DEBUG_RANDOM_IPS', False) \
                        else GeoIPHelper.get_request_ip(request)
            ### _ip = random.choice(ips)
            if _ip:
                event_data = {}
                event_data['ip_address'] = _ip
                event_site = get_current_site(request)
                event_data['site_id'] = event_site.pk if event_site else None
                event_data['url'] = request.path
                event_data['username'] = request.META.get('REMOTE_USER')
                event_data['user_agent'] = _ua = request.META.get('HTTP_USER_AGENT') 
                geo_data = GeoIPHelper.get_geoip_data(_ip) 
                event_data.update(dict((k, str(v)) for k, v in geo_data.items()))
                process_events_queue.delay(request_uuid, event_data)
        return response
