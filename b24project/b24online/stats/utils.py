# -*- encoding: utf-8 -*-

"""
The utitlities for :mod:`b24online.stats`.
"""

import datetime
import re
import redis

from urllib.parse import unquote, urlparse

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from b24online.models import RegisteredEventType
from b24online.stats import InvalidParameterError


KEY_COMPONENTS_SEPARATOR = ':'
DATE_RE = re.compile('^(\d{2,4})-(\d{1,2})-(\d{1,2}).*?$')


def flatten(x):
    """
    Return the flattened complex list.
    """
    return [y for l in x for y in flatten(l)] if type(x) is list else [x]
                    
                           
def glue(*components):
    """
    Return the key builded from components.
    """
    # Cast to 'list' type
    components = list(components) 
    return KEY_COMPONENTS_SEPARATOR . join(
        map(lambda x: str(x).strip(), flatten(components)))


def get_redis_connection(connection_url=None): 
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


def convert_date(date_str):
    """
    Return 'datetime.date' instance from the string 'YYYY-MM-DD'.
    """
    assert isinstance(date_str, str), 'Invalid parameter'
    _match = DATE_RE.match(date_str)
    if _match:
        _year, _month, _day = map(int, _match.groups())
        return datetime.date(_year, _month, _day)
    else:
        return None
