# -*- encoding: utf-8 -*-

"""
Celery task for 'b24online' application.
"""

import logging

from celery import task
from celery.schedules import crontab, crontab_parser
from celery.decorators import periodic_task

from b24online.stats.utils import get_redis_connection
from b24online.stats.helpers import RegisteredEventHelper


logger = logging.getLogger('b24online.tasks')

@task(name='b24online.process_events_queue')
def process_events_queue(request_uuid, data):
    """
    Process registered events queue for HTTPRequest.
    """
    rconn = get_redis_connection()
    if rconn:
        events_queue_key = RegisteredEventHelper\
            .get_request_key(request_uuid, 'queue')
        while True:
            event_key_b = rconn.lpop(events_queue_key)
            if not event_key_b:
                break
            event_key = event_key_b.decode()
            event_type_id, content_type_id, instanse_id = \
                map(lambda x: int(x), event_key.split(':')[2:])
