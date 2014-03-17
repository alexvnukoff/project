from django.core.management.base import NoArgsCommand
import csv
import os
import datetime
import base64
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload products' data from prepared CSV file named product_legacy.csv
            into buffer DB table LEGACY_DATA_L_PRODUCT
        '''
        time1 = datetime.datetime.now()
        #Upload from CSV file into buffer table
        print('Load product data from CSV file into buffer table...')
        csv.field_size_limit(4000000)
        with open(os.path.join('c:', 'data', 'product_legacy.csv'), 'r') as f:
            reader = csv.reader(f, delimiter=';')
            data = [row for row in reader]

        count = 0
        bad_count = 0
        sz = len(data)
        for i in range(0, sz, 1):
            sz1 = len(data[i])
            for k in range(0, sz1, 1):
                data[i][k] = base64.standard_b64decode(data[i][k])

            if sz1 == 0:
                print('The row# ', i+1, ' is wrong!')
                bad_count += 1
                continue

            btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
            prod_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                    replace("quot;", '"').replace("&amp;", "&").strip()
            detail_page_url = bytearray(data[i][2]).decode(encoding='utf-8')
            preview_picture = bytearray(data[i][3]).decode(encoding='utf-8')
            preview_text = bytearray(data[i][4]).decode(encoding='utf-8').replace("&quot;", '"').replace("quot;", '"').\
                                                replace("&amp;", '').strip()
            detail_picture = bytearray(data[i][5]).decode(encoding='utf-8')
            detail_text = bytearray(data[i][6]).decode(encoding='utf-8').replace("&quot;", '"').replace("quot;", '"').\
                                                replace("&amp;", '').strip()

            if not len(data[i][7]):
                create_date = None
            else:
                create_date = datetime.datetime.strptime(bytearray(data[i][7]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

            company_id = bytearray(data[i][8]).decode(encoding='utf-8')
            photos1 = bytearray(data[i][9]).decode(encoding='utf-8')
            discount = bytearray(data[i][10]).decode(encoding='utf-8')
            add_pages = bytearray(data[i][11]).decode(encoding='utf-8')
            tpp = bytearray(data[i][12]).decode(encoding='utf-8')
            direction = bytearray(data[i][13]).decode(encoding='utf-8')
            if (data[i][14] == 'Y'):
                is_deleted = True
            else:
                is_deleted = False
            photos2 = bytearray(data[i][15]).decode(encoding='utf-8')
            file = bytearray(data[i][16]).decode(encoding='utf-8')
            keywords = bytearray(data[i][17]).decode(encoding='utf-8').replace("&quot;", '"').replace("quot;", '"').\
                                                replace("&amp;", '').strip()

            try:
                L_Product.objects.create(
                                                btx_id = btx_id,\
                                                prod_name = prod_name,\
                                                detail_page_url = detail_page_url,\
                                                preview_picture = preview_picture,\
                                                preview_text = preview_text,\
                                                detail_picture = detail_picture,\
                                                detail_text = detail_text,\
                                                create_date = create_date,\
                                                company_id = company_id,\
                                                photos1 = photos1,\
                                                discount = discount,\
                                                add_pages = add_pages,\
                                                tpp = tpp,\
                                                direction = direction,\
                                                is_deleted = is_deleted,\
                                                photos2 = photos2,\
                                                file = file,\
                                                keywords = keywords)
                count += 1
            except:
                #print('Milestone: ', i+1)
                print(btx_id, '##', prod_name, '##', ' Count: ', i+1)
                continue

            print('Milestone: ', i+1)

        print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Products were migrated from CSV into DB!')
