from django.core.management.base import NoArgsCommand
from core.models import User, Relationship
from appl.models import Country, Tpp
from django.utils.translation import trans_real
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload TPPs' data from buffer DB table LEGACY_DATA_L_TPP into TPP DB
        '''
        time1 = datetime.datetime.now()
        print('Loading TPPs from buffer DB into TPP DB...')
        qty = L_TPP.objects.filter(completed=True).count()
        print('Before already were processed: ', qty)
        i = 0
        tpp_lst = L_TPP.objects.filter(completed=False).all()
        for leg_tpp in tpp_lst:
            #set create_user (owner) for the TPP
            if leg_tpp.moderator:
                try:
                    l_user = L_User.objects.get(btx_id=leg_tpp.moderator)
                    create_usr = User.objects.get(pk=l_user.tpp_id)
                except:
                    create_usr = User.objects.get(pk=1)
            else:
                create_usr = User.objects.get(pk=1)

            try:
                new_tpp = Tpp.objects.create(title='TPP_LEG_ID:'+leg_tpp.btx_id,
                                                      create_user=create_usr)
            except:
                print(leg_tpp.btx_id, '##', leg_tpp.tpp_name, '##', ' Count: ', i)
                i += 1
                continue

            img_small_path = ''
            img_detail_path = ''
            head_pic_path = ''

            attr = {'NAME': leg_tpp.tpp_name,
                    'IMAGE_SMALL': img_small_path,
                    'ANONS': leg_tpp.preview_text,
                    'IMAGE': img_detail_path,
                    'DETAIL_TEXT': leg_tpp.detail_text,
                    'HEAD_PIC': head_pic_path,
                    'SITE_NAME': leg_tpp.domain,
                    'ADDRESS': leg_tpp.address,
                    'EMAIL': leg_tpp.email,
                    'FAX': leg_tpp.fax,
                    'MAP_POSITION': leg_tpp.map,
                    'TELEPHONE_NUMBER': leg_tpp.phone,
                }

            trans_real.activate('ru') #activate russian locale
            res = new_tpp.setAttributeValue(attr, create_usr)
            trans_real.deactivate() #deactivate russian locale
            if res:
                leg_tpp.tpp_id = new_tpp.pk
                leg_tpp.completed = True
                leg_tpp.save()
            else:
                print('Problems with Attributes adding!')
                i += 1
                continue

            # create relationship type=Dependence with country
            try: #if there isn't country in Company take it from TPP
                prnt = Country.objects.get(item2value__attr__title="NAME", item2value__title_ru=leg_tpp.country)

                Relationship.objects.create(parent=prnt, type='dependence', child=new_tpp, create_user=create_usr)
            except:
                trans_real.activate('ru')
                print('Next TPP has not country:', new_tpp.getName())
                trans_real.deactivate()

            i += 1
            print('Milestone: ', qty + i)

        #set up mother TPP
        tpp_lst = L_TPP.objects.exclude(tpp_parent='').all()
        for tpp in tpp_lst:
            try:
                parent_tpp = Tpp.objects.get(pk=L_TPP.objects.get(btx_id=tpp.tpp_parent).tpp_id)
                child_tpp = Tpp.objects.get(pk=tpp.tpp_id)
                Relationship.objects.create(parent=parent_tpp, type='hierarchy', child=child_tpp, create_user=create_usr)
                print('Relationship for parent TPPs was created!')
            except:
                continue

        print('Done. Quantity of processed strings:', qty + i)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('TPPs were migrated from buffer DB into TPP DB!')
