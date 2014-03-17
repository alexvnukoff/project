from django.core.management.base import NoArgsCommand
from core.models import User, Relationship
from appl.models import Gallery, Product
from core.amazonMethods import add
from django.utils.translation import trans_real
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload products' pictures from buffer DB table LEGACY_DATA_L_PIC2PROD into TPP DB
        '''
        img_root = 'c:' #additional path to images
        time1 = datetime.datetime.now()
        # Move products' pictures from buffer table into original tables
        print('Reload products from buffer DB into TPP DB...')
        qty = L_Pic2Prod.objects.filter(completed=True).count()
        print('Before already were processed: ', qty)
        pic_lst = L_Pic2Prod.objects.filter(completed=False).all()

        i = 0
        count = 0;
        prev_btx_id = 0;
        create_usr = User.objects.get(pk=1)
        for rec in pic_lst:
            if prev_btx_id != rec.btx_id:
                try:
                    leg_prod = L_Product.objects.get(btx_id=rec.btx_id)
                except:
                    i += 1
                    continue
                try:
                    prod = Product.objects.get(pk=leg_prod.tpp_id)
                except:
                    i += 1
                    continue

                prev_btx_id = rec.btx_id

                if len(rec.preview_picture):
                    img_small_path = add(img_root + rec.preview_picture)
                else:
                    img_small_path = ''
                if len(rec.detail_picture):
                    img_detail_path = add(img_root + rec.detail_picture)
                else:
                    img_detail_path = ''

                attr = {
                        'IMAGE_SMALL': img_small_path,
                        'IMAGE': img_detail_path,
                    }
                trans_real.activate('ru')
                res = prod.setAttributeValue(attr, create_usr)
                trans_real.deactivate()
                if not res:
                    print('Problems with Attributes adding!')
                    i += 1
                    continue

            rec.tpp_id = prod.pk
            rec.completed = True
            rec.save()

            if len(rec.gallery): #create relationship with Gallery
                try:
                    gal = Gallery.objects.create(title='GALLERY_FOR_PROD_ID:'+rec.btx_id, create_user=create_usr)
                except:
                    i += 1
                    continue

                gal.photo = add(img_root + rec.gallery)
                # create relationship
                try:
                    Relationship.objects.create(parent=prod, type='relation', child=gal, create_user=create_usr)
                    print('Relationship between Product and Gallery was created! Prod_id:', prod.pk)
                    count += 1
                except:
                    print('Product was deleted! Product btx_id:', leg_prod.btx_id)
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
        print('Product pictures were migrated from buffer DB into TPP DB!')
