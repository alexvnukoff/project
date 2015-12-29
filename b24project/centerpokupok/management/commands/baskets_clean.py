# -*- coding: utf-8 -*-
from django.utils.timezone import now, timedelta
from django.core.management.base import BaseCommand
from centerpokupok.models import UserBasket

class Command(BaseCommand):
    help = 'Delete empty baskets'

    def handle(self, *args, **options):
        UserBasket.objects.filter(created__lt=now() - timedelta(days=2)).delete()


