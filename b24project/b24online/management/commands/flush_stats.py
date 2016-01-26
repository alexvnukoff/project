# -*- encoding: utf-8 -*-

from django.core.management.base import NoArgsCommand

from b24online.stats.utils import get_redis_connection


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        """
        Flush all keys in Stats Redis DB.
        """
        rconn = get_redis_connection()
        if rconn:
            rconn.flushall()
