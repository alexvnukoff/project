# -*- encoding: utf-8 -*-

"""
Celery task for 'b24online' application.
"""

import datetime
import logging

from celery.schedules import crontab

from tpp.celery import app

from b24online.models import RegisteredEventStats
from b24online.stats.helpers import RegisteredEventHelper
from b24online.stats.utils import get_redis_connection, glue

logger = logging.getLogger('b24online.tasks')


# @app.task
# def process_events_queue(request_uuid, extra_data):
#     """
#     Process registered events queue for HTTPRequest.
#     """
#     site_id = extra_data.get('site_id')
#     rconn = get_redis_connection()
#     if site_id and rconn:
#         queue_key = RegisteredEventHelper \
#             .get_request_key(request_uuid, 'queue')
#         geo_data_key = RegisteredEventHelper.geo_data_key
#         ready_to_process_key = RegisteredEventHelper.ready_to_process

#         while True:
#             event_key_b = rconn.lpop(queue_key)
#             if not event_key_b:
#                 break
#             event_key = event_key_b.decode()
#             event_unique_key = glue(
#                 event_key,
#                 RegisteredEventHelper.get_unique_key(extra_data))
#             if event_unique_key:
#                 rconn.incr(event_unique_key)
#                 geo_value = RegisteredEventHelper \
#                     .get_geoip_info_key(extra_data)
#                 rconn.hset(geo_data_key, event_unique_key, geo_value)
#                 rconn.sadd(ready_to_process_key, event_unique_key)


# @app.task
# def process_events_stats():
#     today = datetime.date.today()
#     rconn = get_redis_connection()
#     if rconn:
#         geo_data_key = RegisteredEventHelper.geo_data_key
#         ready_to_process_key = RegisteredEventHelper.ready_to_process
#         already_key = RegisteredEventHelper.already_key
#         stats_ids = []
#         while True:
#             event_key_b = rconn.spop(ready_to_process_key)
#             if not event_key_b:
#                 break

#             already = False
#             event_key = event_key_b.decode()
#             total = rconn.get(event_key) or 0
#             try:
#                 total = int(total)
#             except TypeError:
#                 continue
#             else:
#                 rconn.set(event_key, 0)
#                 if rconn.hget(already_key, event_key):
#                     already = True
#                 else:
#                     rconn.hset(already_key, event_key, True)

#                 geo_data = rconn.hget(geo_data_key, event_key)
#                 geo_data = geo_data.decode()
#             try:
#                 event_type_id, content_type_id, object_id = \
#                     map(lambda x: int(x), event_key.split(':')[2:5])
#             except Typeerror:
#                 break

#             try:
#                 stats = RegisteredEventStats.objects \
#                     .get(event_type_id=event_type_id,
#                          content_type_id=content_type_id,
#                          object_id=object_id,
#                          registered_at=today)
#             except RegisteredEventStats.DoesNotExist:
#                 stats = RegisteredEventStats(
#                     event_type_id=event_type_id,
#                     content_type_id=content_type_id,
#                     object_id=object_id,
#                     registered_at=today,
#                     unique_amount=0, total_amount=0)

#             data = stats.extra_data or {}
#             _add = {'unique': 1 if not already else 0, 'total': total}
#             for _type in ('unique', 'total'):
#                 _key = glue(geo_data, _type)
#                 if _key in data:
#                     try:
#                         _old = int(data[_key])
#                     except TypeError:
#                         _old = 0
#                     _new = _old + _add.get(_type, 0)
#                 else:
#                     _new = _add.get(_type, 0)
#                 data[_key] = str(_new)

#             stats.extra_data = data
#             stats.unique_amount += _add['unique']
#             stats.total_amount += _add['total']
#             stats.save()


@app.task
def flush_events_stats():
    """
    Flush the events entries in Redis.
    """
    rconn = get_redis_connection()
    if rconn:
        for item_key in rconn.keys('registered*'):
            rconn.delete(item_key)


app.conf.beat_schedule.update({
    'flush_events_stats': {
        'task': 'b24online.tasks.flush_events_stats',
        'schedule': crontab(hour=4)
    },
    'process_events_stats': {
        'task': 'b24online.tasks.process_events_stats',
        'schedule': crontab(hour='*/6')
    },
})
