from django.core.management.base import NoArgsCommand
from appl.models import Product
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Update site attribute for products
        '''
        print('Updating B2C products...')
        time1 = datetime.datetime.now()
        qty = L_Site2Prod.objects.filter(completed=True).count()
        print('Before already were processed: ', qty)
        prod_lst = L_Site2Prod.objects.filter(completed=False).all()

        b2c_site = 0
        b2b_site = 0

        i = 0
        count = 0

        for itm in prod_lst:
            try:
                leg_prod = L_Product.objects.get(btx_id=itm.btx_id)
            except:
                print('Product does not exist in buffer DB! Product btx_id:', itm.btx_id)
                i += 1
                continue

            try:
                prod = Product.objects.get(pk=leg_prod.tpp_id)
            except:
                print('Product does not exist in TPP DB! Product btx_id:', itm.btx_id)
                i += 1
                continue

            prod.sites.add(b2c_site)
            itm.completed = True
            itm.save()
            count += 1
            i += 1
            print('Milestone: ', i)

        print('Updating B2B products...')
        start = 0
        block_size = 1000
        flag = True
        j = 0
        while flag:
            prod_lst = Product.objects.exclude(sites=b2c_site).all()[start:start+block_size]
            if len(prod_lst) < block_size:
                flag = False
            else:
                start += block_size

            for prod in prod_lst:
                prod.sites.add(b2b_site)
                j += 1
                count += 1
                print('Milestone: ', j)

        print('Done. Quantity of processed items:', i+j, 'Were updated:', count)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Production sites were updated!')
