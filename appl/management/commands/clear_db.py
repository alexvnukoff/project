from django.core.management.base import NoArgsCommand
from core.models import User
from appl.models import Department, Cabinet
from django.contrib.auth.models import Group

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Clear all generated data in DB for ORG community migration process debugging
        '''
        print('Starting DB cleaning...')
        dep_lst = Department.objects.exclude(pk__in=(233, 243))
        for dep in dep_lst:
            dep.delete()

        cab_lst = Cabinet.objects.exclude(pk__in=(1, 256, 257, 426, 427, 428))
        for cab in cab_lst:
            cab.delete()

        g = Group.objects.get(name='ORG-1000000000')
        g.user_set.add(User.objects.get(pk=26))
        g.user_set.add(User.objects.get(pk=27))

        g = Group.objects.get(name='ORG-0100000000')
        g.user_set.add(User.objects.get(pk=21))
        g.user_set.add(User.objects.get(pk=22))
        g.user_set.add(User.objects.get(pk=23))

        g = Group.objects.get(name='ORG-2000000000')
        g.user_set.add(User.objects.get(pk=24))
        g.user_set.add(User.objects.get(pk=25))
        g.user_set.add(User.objects.get(pk=26))

        print('DB is cleaned!')
