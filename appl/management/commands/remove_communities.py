from django.core.management.base import NoArgsCommand
from core.models import Item, Relationship
from appl.models import Tpp, Company, Department, Cabinet, Vacancy
from django.contrib.auth.models import Group
from django.utils.translation import trans_real
import datetime

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Remove all community groups ('ORG-') and sets Item.community = null
        '''
        print('Start Communities removing...')
        g_list = Group.objects.filter(name__icontains='ORG-')
        for g in g_list:
            #g.delete()
            a = 1

        item_list = Item.objects.filter(organization__isnull=False)

        print('All Communities were removed!')