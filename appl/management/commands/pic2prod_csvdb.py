from django.core.management.base import NoArgsCommand
import csv
import os
import datetime
import base64
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload products' pictures from prepared CSV file named pic2prod_legacy.csv
            into buffer DB table LEGACY_DATA_L_PIC2PROD
        '''
        time1 = datetime.datetime.now()
        #Upload from CSV file into buffer table
        print('Load data from CSV file into buffer table...')
        csv.field_size_limit(4000000)
        with open(os.path.join('c:', 'data', 'pic2prod_legacy.csv'), 'r') as f:
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
            preview_picture = bytearray(data[i][2]).decode(encoding='utf-8')
            detail_picture = bytearray(data[i][3]).decode(encoding='utf-8')
            gallery = bytearray(data[i][4]).decode(encoding='utf-8')

            try:
                L_Pic2Prod.objects.create(  btx_id = btx_id,\
                                            prod_name = prod_name,\
                                            preview_picture = preview_picture,\
                                            detail_picture = detail_picture,\
                                            gallery = gallery)
                count += 1
            except Exception as e:
                #print('Milestone: ', i+1)
                i += 1
                print(btx_id, '##', prod_name, '##', ' Count: ', i+1)
                continue

            print('Milestone: ', i+1)

        print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Pictures for Products were migrated from CSV into DB!')
