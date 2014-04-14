from django.core.management.base import NoArgsCommand
from core.models import Relationship
from appl.models import Cabinet

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Move Users from community groups ('ORG-') and attach User's Cabinets to Vacancy
        '''
        print('Update Relationship type between Vacancies and Cabinets...')
        cab_list = Cabinet.objects.all()
        for cab in cab_list:
            rel = Relationship.objects.filter(child=cab, type='hierarchy')
            for r in rel:
                r.type='relation'
                r.save()