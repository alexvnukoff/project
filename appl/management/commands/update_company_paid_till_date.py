from django.core.management.base import NoArgsCommand
from django.conf import settings
import datetime
from appl.models import Company


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """ Update Companies' pay_till_date. Setup now() + settings.FREE_PERIOD date """
        paid_next_date = (datetime.datetime.now() + datetime.timedelta(days=settings.FREE_PERIOD)).date()
        # Get only Companies which are not a members of TPPs
        Company.objects.exclude(c2p__parent__organization__isnull=False).update(paid_till_date=paid_next_date)
        # For TPP members set unlimited period
        Company.objects.filter(c2p__parent__organization__isnull=False).update(paid_till_date=None)
