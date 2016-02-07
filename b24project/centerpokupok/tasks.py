# -*- coding: utf-8 -*-
from celery.schedules import crontab
from celery.decorators import periodic_task
from django.utils.timezone import now, timedelta
from centerpokupok.models import UserBasket


@periodic_task(name='centerpokupok.basket_clean',
    # UTC+03:00 Moscow 4:30 a.m.
    run_every=crontab(hour=1, minute=30)
    )
def basket_clean():
        UserBasket.objects.filter(
            created__lt=now() - timedelta(days=2)
            ).delete()


