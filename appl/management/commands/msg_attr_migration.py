from django.core.management.base import NoArgsCommand
from core.models import Item
from appl.models import Messages

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload messages attribute DETAIL_TEXT into class field 'text'
        '''
        msg_lst = Messages.objects.all()
        msg_pks = msg_lst.values_list('pk', flat=True)
        msg_lst_wa = Item.getItemsAttributesValues('DETAIL_TEXT', msg_pks)
        for msg in msg_lst:
            for m_id, m_attr in msg_lst_wa.items():
                if msg.id == m_id:
                    msg.text = m_attr['DETAIL_TEXT'][0]
                    msg.save()

