# -*- encoding: utf-8 -*-

"""
Celery task for 'b24online' application.
"""

import logging
import datetime

from django.conf import settings

from celery import task
from celery.schedules import crontab, crontab_parser
from celery.decorators import periodic_task

from b24online.models import RegisteredEventStats
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


@periodic_task(name="b24online.process_events_stats",
    run_every=crontab(**getattr(settings, 'STATS_CRONTAB', {'minute': 5})))
def process_events_stats():
    return 
    today = datetime.date.today()
    rconn = get_redis_connection()
    if rconn:
        geo_data_key = RegisteredEventHelper.geo_data_key
        ready_to_process_key = RegisteredEventHelper.ready_to_process
        while True:
            event_key_b = rconn.spop(ready_to_process_key)
            if not event_key_b:
                break
            event_key = event_key_b.decode()
            total = rconn.get(event_key)
            try:
                total = int(total)
            except TypeError:
                continue
            else:
                geo_data = rconn.hget(geo_data_key, event_key)
                geo_data = geo_data.decode()                
            try:
                event_type_id, content_type_id, object_id = \
                    map(lambda x: int(x), event_key.split(':')[2:5])
            except Typeerror:
                break

            try:
                stats = RegisteredEventStats.objects\
                    .get(event_type_id=event_type_id,
                         content_type_id=content_type_id,
                         object_id=object_id,
                         registered_at=today)
            except RegisteredEventStats.DoesNotExist:
                stats = RegisteredEventStats(
                    event_type_id=event_type_id,
                    content_type_id=content_type_id,
                    object_id=object_id,
                    registered_at=today,
                    unique_amount=0, total_amount=0)
            
            data = stats.extra_data or {}
            _add = {'unique': 1, 'total': total}
            for _type in ('unique', 'total'):
                _key = glue(geo_data, _type)
                if _key in data:
                    try:
                        _old = int(data[_key])
                    except TypeError:
                        _old = 0
                    _new = _old + _add.get(_type, 0)
                else:
                    _new = _add.get(_type, 0)
                data[_key] = str(_new)
            stats.extra_data = data
            
            unique = 0
            total = 0
            for _k, _v in stats.extra_data.items():
                try:
                    v = int(_v)
                except TypeError:
                    continue
                else:
                    d = _k.split(':')[-1]
                    if d == 'unique':
                        stats.unique_amount += v
                    elif d == 'total':
                        stats.total_amount += v
            stats.save()
