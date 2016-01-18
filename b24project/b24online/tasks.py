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


logger = logging.getLogger(__name__)

@task(name='b24online.process_events_queue')
def process_events_queue(request_uuid, data):
    """
    Process registered events queue for HTTPRequest.
    """
    rconn = get_redis_connection()
    if rconn:
        events_queue_key = RegisteredEventHelper\
            .get_request_key(request_uuid, 'query')
        while True:
            event_key = rconn.lpop(events_queue_key)
            if not event_key:
                break
            
            event_type_id, content_type_id, instanse_id = \
                map(lambda x: int(x), event_key.split(':')[2:])
            logger.debug(event_type_id)
            logger.debug(content_type_id)
            logger.debug(object_id)
            