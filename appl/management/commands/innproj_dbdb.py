from django.core.management.base import NoArgsCommand
from core.models import User, Relationship
from appl.models import Gallery, InnovationProject, Cabinet, Company, Tpp
from core.amazonMethods import add, addFile
from django.utils.translation import trans_real
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload Innovative Projects from buffer DB table LEGACY_DATA_L_INNPRJ into TPP DB
        '''
        img_root = "c:"
        time1 = datetime.datetime.now()
        print('Loading Innovative Projects from buffer DB into TPP DB...')
        qty = L_InnPrj.objects.filter(completed=True).count()
        print('Before already were processed: ', qty)
        i = 0
        prj_lst = L_InnPrj.objects.filter(completed=False).all()
        for leg_prj in prj_lst:
            #set create_user (owner) for the Innovative Project
            if leg_prj.author:
                try:
                    l_user = L_User.objects.get(btx_id=leg_prj.author)
                    create_usr = User.objects.get(pk=l_user.tpp_id)
                except:
                    create_usr = User.objects.get(pk=1)
            else:
                create_usr = User.objects.get(pk=1)

            try:
                prj = InnovationProject.objects.create(title='INN_PROJECT_LEG_ID:'+leg_prj.btx_id,
                                                      create_user=create_usr)
            except:
                print(leg_prj.btx_id, '##', leg_prj.prj_name, '##', ' Count: ', i)
                i += 1
                continue

            file_path = addFile(leg_prj.bp_file)

            attr = {
                    'NAME': leg_prj.prj_name,
                    'PRODUCT_NAME': leg_prj.prj_title,
                    'COST': 0,
                    #'CURRENCY': '',
                    'TARGET_AUDIENCE': leg_prj.target_community,
                    'RELEASE_DATE': leg_prj.estim_date,
                    'SITE_NAME': leg_prj.site,
                    'KEYWORD': leg_prj.keywords,
                    'DETAIL_TEXT': leg_prj.detail_text,
                    'BUSINESS_PLAN': leg_prj.bp_decrip,
                    'DOCUMENT_1': file_path,
                    }

            trans_real.activate('ru') #activate russian locale
            res = prj.setAttributeValue(attr, create_usr)
            trans_real.deactivate() #deactivate russian locale
            if res:
                leg_prj.tpp_id = prj.pk
                leg_prj.completed = True
                leg_prj.save()
            else:
                print('Problems with Attributes adding!')
                i += 1
                continue

            # create relationship type=Dependence with business entity
            try:
                leg_ent = L_Company.objects.get(btx_id=leg_prj.company)
                b_entity = Company.objects.get(pk=leg_ent.tpp_id)
                Relationship.objects.create(parent=b_entity, type='dependence', child=prj, create_user=create_usr)
            except:
                try:
                    leg_ent = L_TPP.objects.get(btx_id=leg_prj.tpp)
                    b_entity = Tpp.objects.get(pk=leg_ent.tpp_id)
                    Relationship.objects.create(parent=b_entity, type='dependence', child=prj, create_user=create_usr)
                except:
                    try:
                        leg_ent = L_User.objects.get(btx_id=leg_prj.author)
                        usr = User.objects.get(pk=leg_ent.tpp_id)
                        b_entity = Cabinet.objects.get(user=usr.pk)
                        Relationship.objects.create(parent=b_entity, type='dependence', child=prj, create_user=create_usr)
                    except:
                        i += 1
                        continue

            #attache gallery to Innovative Project

            if len(leg_prj.photos): #create relationship with Gallery
                pic_lst = leg_prj.photos.split('#')
                for pic in pic_lst:
                    try:
                        gal = Gallery.objects.create(title='GALLERY_FOR_INN_PROJECT_ID:'+leg_prj.btx_id, create_user=create_usr)
                    except:
                        continue

                    gal.photo = add(img_root + pic)
                    # create relationship
                    try:
                        Relationship.objects.create(parent=prj, type='dependence', child=gal, create_user=create_usr)
                        print('Relationship between Innovative Project and Gallery was created! Project ID:', prj.pk)
                    except:
                        print('Can not create relationship! Project ID:', prj.pk)
                        continue

            i += 1
            print('Milestone: ', qty + i)

        print('Done. Quantity of processed strings:', qty + i)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Innovative Projects were migrated from buffer DB into TPP DB!')
