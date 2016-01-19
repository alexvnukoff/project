# -*- encoding: utf-8 -*-

"""
Celery task for 'b24online' application.
"""

import logging

from celery import task
from celery.schedules import crontab, crontab_parser
from celery.decorators import periodic_task

from b24online.stats.utils import get_redis_connection, glue
from b24online.stats.helpers import RegisteredEventHelper


logger = logging.getLogger('b24online.tasks')

@task(name='b24online.process_events_queue')
def process_events_queue(request_uuid, extra_data):
    """
    Process registered events queue for HTTPRequest.
    """
    site_id = extra_data.get('site_id')
    rconn = get_redis_connection()
    if site_id and rconn:
        queue_key = RegisteredEventHelper\
            .get_request_key(request_uuid, 'queue')
        geo_data_key = RegisteredEventHelper.geo_data_key
        ready_to_process_key = RegisteredEventHelper.ready_to_process
        
        while True:
            event_key_b = rconn.lpop(queue_key)
            if not event_key_b:
                break
            event_key = event_key_b.decode()
            event_unique_key = glue(
                event_key, 
                RegisteredEventHelper.get_unique_key(extra_data))
            if event_unique_key:
                rconn.incr(event_unique_key)
                geo_value = RegisteredEventHelper\
                    .get_geoip_info_key(extra_data)
                rconn.hset(geo_data_key, event_unique_key, geo_value)
                rconn.sadd(ready_to_process_key, event_unique_key)
