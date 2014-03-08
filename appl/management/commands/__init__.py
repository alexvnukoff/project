from django.core.management.base import NoArgsCommand
from django.http import HttpResponse, Http404
from legacy_data.models import L_User, L_Company, L_Product, L_TPP
from core.models import User, Relationship, Dictionary
from core.amazonMethods import add
from appl.models import Company, Tpp, Product, Country, Cabinet
from random import randint
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import Group
from django.conf import settings
import datetime
import csv
from tpp.SiteUrlMiddleWare import get_request
import base64
from django.utils.translation import trans_real

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        '''
            Reload products' data from buffer DB table LEGACY_DATA_L_PRODUCT into TPP DB
        '''
        img_root = 'c:' #additional path to images
        time1 = datetime.datetime.now()
        # Move products from buffer table into original tables
        print('Reload products from buffer DB into TPP DB...')
        qty = L_Product.objects.filter(completed=True).count()
        print('Before already were processed: ', qty)
        prod_lst = L_Product.objects.filter(completed=False).all()
        #comp_lst = L_Company.objects.exclude(preview_picture='')[:2]
        #comp_lst = L_Company.objects.filter(pk=545208)
        i = 0
        count = 0;
        create_usr = User.objects.get(pk=1)
        for leg_prod in prod_lst:
            try:
                new_prod = Product.objects.create(title='PRODUCT_LEG_ID:'+leg_prod.btx_id,
                                                  create_user=create_usr)
                count += 1
            except:
                print(leg_prod.btx_id, '##', leg_prod.prod_name, '##', ' Count: ', i)
                i += 1
                continue
            '''
            if len(leg_prod.preview_picture):
                img_small_path = add(img_root + leg_prod.preview_picture)
            else:
                img_small_path = ''
            if len(leg_prod.detail_picture):
                img_detail_path = add(img_root + leg_prod.detail_picture)
            else:
                img_detail_path = ''
            '''
            img_small_path = ''
            img_detail_path = ''
            attr = {
                    'NAME': leg_prod.prod_name,
                    'IMAGE_SMALL': img_small_path,
                    'ANONS': leg_prod.preview_text,
                    'IMAGE': img_detail_path,
                    'DETAIL_TEXT': leg_prod.detail_text,
                    'DISCOUNT': leg_prod.discount,
                }
            trans_real.activate('ru')
            res = new_prod.setAttributeValue(attr, create_usr)
            trans_real.deactivate()
            if res:
                leg_prod.tpp_id = new_prod.pk
                leg_prod.completed = True
                leg_prod.save()
            else:
                print('Problems with Attributes adding!')
                i += 1
                continue

            # create relationship type=Dependence with Company
            try:
                cmp = L_Company.objects.get(btx_id=leg_prod.company_id)
                prnt = Company.objects.get(pk=cmp.tpp_id)
                Relationship.objects.create(parent=prnt, type='dependence', child=new_prod, create_user=create_usr)
            except:
                print('Product was deleted! Product btx_id:', leg_prod.btx_id)
                Product.objects.filter(pk=new_prod.pk)
                count -= 1
                print('Milestone: ', qty + i)
                i += 1
                continue

            print('Relationship between Product and Company was created! Prod_id:', new_prod.pk)

            i += 1
            print('Milestone: ', qty + i)

        print('Done. Quantity of processed strings:', qty + i, 'Were added into DB:', count)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)