from django.core.management.base import NoArgsCommand
from core.amazonMethods import add
from core.models import User, Relationship
from appl.models import Company, Gallery, Tpp
from django.utils.translation import trans_real
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload products' pictures from buffer DB table LEGACY_DATA_L_PIC2ORG into TPP DB
        '''
        img_root = 'c:' #additional path to images
        time1 = datetime.datetime.now()
        # Move products' pictures from buffer table into original tables
        print('Reload products from buffer DB into TPP DB...')
        qty = L_Pic2Org.objects.filter(completed=True).count()
        print('Before already were processed: ', qty)
        pic_lst = L_Pic2Org.objects.filter(completed=False).all()

        i = 0
        count = 0;
        prev_btx_id = 0;
        create_usr = User.objects.get(pk=1)
        for rec in pic_lst:
            if prev_btx_id != rec.btx_id:
                try:
                    leg_org = L_Company.objects.get(btx_id=rec.btx_id)
                except:
                    try:
                        leg_org = L_TPP.objects.get(btx_id=rec.btx_id)
                    except:
                        print('ATTENTION! Legacy Organization not found! Org ID:', rec.btx_id)
                        rec.completed = True
                        rec.save()
                        i += 1
                        continue
                try:
                    org = Company.objects.get(pk=leg_org.tpp_id)
                except:
                    try:
                        org = Tpp.objects.get(pk=leg_org.tpp_id)
                    except:
                        print('ATTENTION! Organization not found! Org ID:', leg_org.tpp_id)
                        i += 1
                        continue

                prev_btx_id = rec.btx_id

                if len(leg_org.preview_picture):
                    img_small_path = add(img_root + leg_org.preview_picture)
                else:
                    img_small_path = ''
                if len(leg_org.detail_picture):
                    img_detail_path = add(img_root + leg_org.detail_picture)
                else:
                    img_detail_path = ''

                attr = {
                        'IMAGE_SMALL': img_small_path,
                        'IMAGE': img_detail_path,
                    }
                trans_real.activate('ru')
                res = org.setAttributeValue(attr, create_usr)
                trans_real.deactivate()
                if not res:
                    print('Problems with Attributes adding!')
                    i += 1
                    continue

            if len(rec.gallery): #create relationship with Gallery
                try:
                    gal = Gallery.objects.create(title='GALLERY_FOR_ORG_ID:'+rec.btx_id,\
                                                 photo=add(img_root + rec.gallery), create_user=create_usr)
                    attr = {
                        'GALLERY_TOPIC': rec.gallery_topic,
                        'NAME': rec.pic_title,
                    }
                    trans_real.activate('ru')
                    res = org.setAttributeValue(attr, create_usr)
                    trans_real.deactivate()
                    if not res:
                        print('Problems with Attributes adding!')
                        i += 1
                        continue
                except:
                    print('Can not create Gallery! Organization ID: ', org.pk)
                    i += 1
                    continue

                # create relationship
                try:
                    Relationship.objects.create(parent=org, type='relation', child=gal, create_user=create_usr)
                    rec.tpp_id = org.pk
                    rec.save()
                    leg_org.pic_completed = True
                    leg_org.save()
                    print('Relationship between Organization and Gallery was created! Org_id:', org.pk)
                    count += 1
                except:
                    print('Can not establish gallery relationship! Organization btx_id:', leg_org.btx_id)
                    gal.delete()
                    count -= 1
                    i += 1
                    continue

            i += 1
            print('Milestone: ', qty + i)

        print('Done. Quantity of processed strings:', qty + i, 'Were added into DB:', count)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Organization pictures were migrated from buffer DB into TPP DB!')
