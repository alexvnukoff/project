# -*- encoding: utf-8 -*-
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
                        'badip',
                        nargs='+',
                        type=str,
                        help='<ip_one> <ip_two> <ip_three> ..'
                    )

    def handle(self, *args, **options):
        for i in options['badip']:
            cache.set('oi:%(obj_ip)s:bad' % {'obj_ip': i}, 1, None)
            print("IP adress {0} added to list..".format(i))
