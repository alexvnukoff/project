from django.core.management.base import NoArgsCommand
from core.models import *
from appl.models import Messages

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Remove messages attribute DETAIL_TEXT values in Value table
        '''
        msg_pks = Messages.objects.all().values_list('pk', flat=True)
        text_values = Value.objects.filter(item__in=msg_pks, attr__title='DETAIL_TEXT')
        text_values.delete()

