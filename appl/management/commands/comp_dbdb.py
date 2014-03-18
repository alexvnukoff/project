from django.core.management.base import NoArgsCommand
from random import randint
from core.models import User, Relationship
from django.contrib.auth.models import Group
from appl.models import Company, Country
from django.utils.translation import trans_real
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload companies' data from buffer DB table LEGACY_DATA_L_COMPANY into TPP DB
        '''
        time1 = datetime.datetime.now()
        # Move users from buffer table into original tables
        print('Data validation. Please, wait...')
        qty = L_Company.objects.filter(country_name='').count()
        if qty:
            L_Company.objects.filter(country_name='').delete()
            print('Were deleted companies without countries: ', qty)
        print('Reload companies from buffer DB into TPP DB...')
        qty = L_Company.objects.filter(completed=True).count()
        print('Before already were processed: ', qty)
        flag = True
        block_size = 1000
        i = 0
        while flag:
            comp_lst = L_Company.objects.filter(completed=False).all()[:block_size]
            if len(comp_lst) < block_size: # it will last big loop
                flag = False

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

                img_small_path = ''
                img_detail_path = ''
                #if wrong VATIN then generate default
                if len(leg_cmp.INN) < 5:
                    inn = 'INN_' + str(randint(1000000000, 9999999999))
                else:
                    inn = leg_cmp.INN

                attr = {'NAME': leg_cmp.short_name,
                        'IMAGE_SMALL': img_small_path,
                        'ANONS': leg_cmp.preview_text,
                        'IMAGE': img_detail_path,
                        'DETAIL_TEXT': leg_cmp.detail_text,
                        'NAME_FULL': leg_cmp.full_name,
                        'ADDRESS_YURID': leg_cmp.ur_address,
                        'ADDRESS_FACT': leg_cmp.fact_address,
                        'ADDRESS': leg_cmp.fact_address,
                        'TELEPHONE_NUMBER': leg_cmp.tel,
                        'FAX': leg_cmp.fax,
                        'EMAIL': leg_cmp.email,
                        'INN': inn,
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

                trans_real.activate('ru') #activate russian locale
                res = new_comp.setAttributeValue(attr, create_usr)
                trans_real.deactivate() #deactivate russian locale
                if res:
                    leg_cmp.tpp_id = new_comp.pk
                    leg_cmp.completed = True
                    leg_cmp.save()
                    if not leg_cmp.tpp_name:
                        new_comp.end_date = datetime.datetime.now()
                        new_comp.save()
                else:
                    print('Problems with Attributes adding!')
                    i += 1
                    continue

                # add workers to Company's community
                lst_wrk = L_User.objects.filter(company=leg_cmp.short_name)
                for wrk in lst_wrk:
                    g = Group.objects.get(name=new_comp.community)
                    try:
                        wrk_obj = User.objects.get(pk=wrk.tpp_id)
                        g.user_set.add(wrk_obj)
                    except:
                        continue

                # create relationship type=Dependence with country
                try: #if there isn't country in Company take it from TPP
                    prnt = Country.objects.get(item2value__attr__title="NAME", item2value__title_ru=leg_cmp.country_name)
                except:
                    tpp = L_TPP.objects.filter(btx_id=leg_cmp.tpp_name)
                    try:
                        prnt = Country.objects.get(item2value__attr__title="NAME", item2value__title_ru=tpp[0].country)
                    except:
                        L_Company.objects.filter(btx_id=leg_cmp.btx_id).delete()
                        Company.objects.filter(pk=leg_cmp.tpp_id).delete()
                        i += 1
                        continue

                Relationship.objects.create(parent=prnt, type='dependence', child=new_comp, create_user=create_usr)

                i += 1
                print('Milestone: ', qty + i)

        print('Done. Quantity of processed strings:', qty + i)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Companies were migrated from buffer DB into TPP DB!')
