# -*- encoding: utf-8 -*-

from django.core.management.base import NoArgsCommand

from b24online.tasks import process_events_stats


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        """
        Process Regsistered Events stats stored in Redis
        through Celery.
        """
        process_events_stats()
