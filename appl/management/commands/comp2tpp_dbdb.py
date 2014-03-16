from django.core.management.base import NoArgsCommand
from core.models import User, Relationship
from appl.models import Company, Tpp
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Create relationships between companies and their TPP
        '''
        print('Create relationships between Companies and their TPP...')
        time1 = datetime.datetime.now()

        count = 0;
        create_usr = User.objects.get(pk=1)
        flag = True
        start = 0
        block_size = 1000
        i = 0
        while flag:
            comp_lst = L_Company.objects.exclude(tpp_name='').all()[start:start+block_size]
            if len(comp_lst) < block_size: # it will last big loop
                flag = False
            else:
                start += block_size

            for cmp in comp_lst:
                try:
                    company = Company.objects.get(pk=cmp.tpp_id)
                except:
                    print('Company does not exist in DB! Company btx_id:', cmp.btx_id)
                    i += 1
                    continue

                try:
                    leg_tpp = L_TPP.objects.get(btx_id=cmp.tpp_name)
                except:
                    print('Legacy TPP does not exist in DB! TPP btx_id:', cmp.tpp_name)
                    i += 1
                    continue

                try:
                    tpp = Tpp.objects.get(pk=leg_tpp.tpp_id)
                except:
                    print('TPP does not exist in DB! TPP btx_id:', cmp.tpp_name)
                    i += 1
                    continue

                # create relationship
                try:
                    Relationship.objects.create(parent=tpp, type='relation', child=company, create_user=create_usr)
                    count += 1
                except:
                    print('Can not establish relationship! Company ID:', company.pk, ' TPP ID:', tpp.pk)
                    i += 1
                    continue

                i += 1
                print('Milestone: ', i)

        print('Done. Quantity of processed strings:', i, 'Were added into DB:', count)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Relationships between Companies and their TPP were created!')