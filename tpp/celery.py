from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tpp.settings')

ORDERS_REDIS_HOST = 'celeryredis.wlj5jm.0001.euw1.cache.amazonaws.com'
ORDERS_REDIS_PORT = str(getattr(settings, 'ORDERS_REDIS_PORT', 6379))

app = Celery('tpp',  broker='redis://' + ORDERS_REDIS_HOST + ':' + ORDERS_REDIS_PORT)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
