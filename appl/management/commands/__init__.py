from django.core.management.base import NoArgsCommand
from django.http import HttpResponse, Http404
from legacy_data.models import *
from core.models import User, Relationship, Dictionary
from core.amazonMethods import add
from appl.models import Company, Tpp, Product, Country, Cabinet, Gallery
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


        sizes = {
            'big': {'box': (150, 140), 'fit': False},
            'small': {'box': (70, 70), 'fit': False},
            'th': {'box':(30, 30), 'fit': True}
        }

        img_root = '/extr_vlume' #additional path to images
        time1 = datetime.datetime.now()
        # Move users from buffer table into original tables

        print('Reload companies from buffer DB into TPP DB...')
        qty = L_Company.objects.filter(completed=False).count()
        print('Before already were processed: ', qty)

        flag = True
        block_size = 1000
        i = 0

        create_usr = User.objects.get(pk=1)

        while flag:
            comp_lst = L_Company.objects.filter(completed=True, tpp_id__isnull=False).all()[:block_size]

            if len(comp_lst) < block_size: # it will last big loop
                flag = False
            #comp_lst = L_Company.objects.exclude(preview_picture='')[:2]
            #comp_lst = L_Company.objects.filter(pk=545208)

            for leg_cmp in comp_lst:
                #set create_user (owner) for the Company


                try:
                    new_comp = Company.objects.get(pk=leg_cmp.tpp_id)
                except:
                    print(leg_cmp.btx_id, '##', leg_cmp.short_name, '##', ' Count: ', i)
                    i += 1
                    continue

                if len(leg_cmp.preview_picture):
                    img_small_path = add(img_root + leg_cmp.preview_picture, sizes=sizes)
                else:
                    img_small_path = ''

                if len(leg_cmp.detail_picture):
                    img_detail_path = add(img_root + leg_cmp.detail_picture, sizes=sizes)
                else:
                    img_detail_path = ''

                #if wrong VATIN then generate default
                if len(leg_cmp.INN) < 5:
                    inn = 'INN_' + str(randint(1000000000, 9999999999))
                else:
                    inn = leg_cmp.INN

                attr = {'NAME': leg_cmp.short_name,
                        'IMAGE_SMALL': img_small_path if img_small_path else img_detail_path,
                        'IMAGE': img_detail_path if img_detail_path else img_small_path,
                    }

                trans_real.activate('ru') #activate russian locale
                res = new_comp.setAttributeValue(attr, create_usr)
                trans_real.deactivate() #deactivate russian locale
                if res:
                    leg_cmp.completed = False
                    leg_cmp.save()
                else:
                    print('Problems with Attributes adding!')
                    i += 1
                    continue

                i += 1
                print('Milestone: ', qty + i)

        print('Done. Quantity of processed strings:', qty + i)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)