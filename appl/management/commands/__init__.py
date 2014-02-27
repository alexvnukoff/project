__author__ = 'user'

from django.core.management.base import NoArgsCommand
from legacy_data.models import L_User, L_Company, L_Product, L_TPP
from core.models import User
from appl.models import Company, Tpp, Product
from random import randint
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
import datetime
import csv
from tpp.SiteUrlMiddleWare import get_request
import base64
from django.http import HttpResponse, Http404
from legacy_data.models import L_User, L_Company, L_Product, L_TPP
from core.models import User, Relationship
from core.amazonMethods import add
from appl.models import Company, Tpp, Product, Country
from random import randint
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
import datetime
import csv
from tpp.SiteUrlMiddleWare import get_request
import base64

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        '''
            Reload companies' data from buffer DB table LEGACY_DATA_L_COMPANY into TPP DB
        '''
        img_root = 'c:' #additional path to images
        time1 = datetime.datetime.now()
        # Move users from buffer table into original tables
        print('Reload companies from buffer DB into TPP DB...')
        qty = L_Company.objects.filter(completed=True).count()
        print('Before already were processed: ', qty)
        comp_lst = L_Company.objects.filter(completed=False).all()
        #comp_lst = L_Company.objects.exclude(preview_picture='')[:2]
        #comp_lst = L_Company.objects.filter(pk=545208)
        i = 0
        for leg_cmp in comp_lst:
            #set create_user (owner) for the Company
            if leg_cmp.moderator:
                try:
                    l_user = L_User.objects.get(btx_id=leg_cmp.moderator)
                    create_usr = User.objects.get(pk=l_user.tpp_id)
                except:
                    create_usr = User.objects.get(pk=1)
            else:
                create_usr = User.objects.get(pk=1)

            try:
                new_comp = Company.objects.create(title='COMPANY_LEG_ID:'+leg_cmp.btx_id,
                                                  create_user=create_usr)
            except:
                print(leg_cmp.btx_id, '##', leg_cmp.short_name, '##', ' Count: ', i)
                i += 1
                continue
            '''
            if len(leg_cmp.preview_picture):
                img_small_path = add(img_root + leg_cmp.preview_picture)
            else:
                img_small_path = ''
            if len(leg_cmp.detail_picture):
                img_detail_path = add(img_root + leg_cmp.detail_picture)
            else:
                img_detail_path = ''
            '''
            img_detail_path = ''
            img_small_path = ''
            attr = {'NAME': leg_cmp.short_name,
                    'IMAGE_SMALL': img_small_path,
                    'ANONS': leg_cmp.preview_text,
                    'IMAGE': img_detail_path,
                    'DETAIL_TEXT': leg_cmp.detail_text,
                    'NAME_FULL': leg_cmp.full_name,
                    'ADDRESS_YURID': leg_cmp.ur_address,
                    'ADDRESS_FACT': leg_cmp.fact_address,
                    'TELEPHONE_NUMBER': leg_cmp.tel,
                    'FAX': leg_cmp.fax,
                    'EMAIL': leg_cmp.email,
                    'INN': leg_cmp.INN,
                    'KPP': leg_cmp.KPP,
                    'OKVED': leg_cmp.OKVED,
                    'OKATO': leg_cmp.OKATO,
                    'OKPO': leg_cmp.OKPO,
                    'BANK_ACCOUNT': leg_cmp.bank_account,
                    'BANK_NAME': leg_cmp.bank_name,
                    'NAME_DIRECTOR': leg_cmp.director_name,
                    'NAME_BUX': leg_cmp.bux_name,
                    'SLOGAN': leg_cmp.slogan,
                    'MAP_POSITION': leg_cmp.map_id,
                }

            try: #this try for problem with bulk create for fields about 3000 symbols.
                res = new_comp.setAttributeValue(attr, create_usr)
                if res:
                    leg_cmp.tpp_id = new_comp.pk
                    leg_cmp.completed = True
                    leg_cmp.save()
                else:
                    print('Problems with Attributes adding!')
                    i += 1
                    continue
            except:
                attr = {
                        'NAME': leg_cmp.short_name[:2000],
                        'IMAGE_SMALL': img_small_path,
                        'ANONS': leg_cmp.preview_text[:2000],
                        'IMAGE': img_detail_path,
                        'DETAIL_TEXT': leg_cmp.detail_text[:2000],
                        'NAME_FULL': leg_cmp.full_name[:2000],
                        'ADDRESS_YURID': leg_cmp.ur_address[:2000],
                        'ADDRESS_FACT': leg_cmp.fact_address[:2000],
                        'TELEPHONE_NUMBER': leg_cmp.tel[:2000],
                        'FAX': leg_cmp.fax[:2000],
                        'EMAIL': leg_cmp.email[:2000],
                        'INN': leg_cmp.INN[:2000],
                        'KPP': leg_cmp.KPP[:2000],
                        'OKVED': leg_cmp.OKVED[:2000],
                        'OKATO': leg_cmp.OKATO[:2000],
                        'OKPO': leg_cmp.OKPO[:2000],
                        'BANK_ACCOUNT': leg_cmp.bank_account[:2000],
                        'BANK_NAME': leg_cmp.bank_name[:2000],
                        'NAME_DIRECTOR': leg_cmp.director_name[:2000],
                        'NAME_BUX': leg_cmp.bux_name[:2000],
                        'SLOGAN': leg_cmp.slogan[:2000],
                        'MAP_POSITION': leg_cmp.map_id[:2000],
                }
                res = new_comp.setAttributeValue(attr, create_usr)
                if res:
                    leg_cmp.tpp_id = new_comp.pk
                    leg_cmp.completed = True
                    leg_cmp.save()
                else:
                    print('Problems with Attributes adding!')
                    i += 1
                    continue

            # create relationship type=Dependence with country
            Relationship.objects.get_or_create(parent=Country.objects.get(item2value__attr__title="NAME",
                        item2value__title=leg_cmp.country_name), type='dependence', child=new_comp, create_user=create_usr)

            i += 1
            print('Milestone: ', qty + i)

        print('Done. Quantity of processed strings:', qty + i)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
