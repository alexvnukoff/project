# -*- coding: utf-8 -*-
from celery.schedules import crontab
from django.utils.timezone import now, timedelta
from centerpokupok.models import UserBasket
from tpp.celery import app


@app.task
def basket_clean():
        UserBasket.objects.filter(
            created__lt=now() - timedelta(days=2)
            ).delete()


app.conf.beat_schedule.update({
    'basket_clean': {
        'task': 'basket_clean',
        'schedule': crontab(hour=1, minute=30)
    }
})
