from django.core.management.base import NoArgsCommand
from core.models import Item
from django.contrib.auth.models import Group


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Remove all community groups ('ORG-') and sets Item.community = null
        '''
        print('Start Communities removing...')
        g_list = Group.objects.filter(name__icontains='ORG-')
        for g in g_list:
            g.delete()
            
        itm = Item.objects.all()
        itm.update(community=None)

        print('All Communities were removed!')