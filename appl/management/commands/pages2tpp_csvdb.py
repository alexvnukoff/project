from django.core.management.base import NoArgsCommand
import csv
import datetime
import base64
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload TPPs' Additional Pages data from prepared CSV file named pages2tpp_legacy.csv
            into buffer DB table LEGACY_DATA_L_PAGES2TPP
        '''
        time1 = datetime.datetime.now()
        #Upload from CSV file into buffer table
        print('Loading Company additional pages from CSV file into buffer table...')
        csv.field_size_limit(4000000)
        with open('c:\\data\\pages2tpp_legacy.csv', 'r') as f:
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
            page_name = bytearray(data[i][1]).decode(encoding='utf-8')
            page_text = bytearray(data[i][2]).decode(encoding='utf-8').replace("&quot;", '"').\
                                    replace("quot;", '"').replace("&amp;", "&").strip()

            try:
                L_Pages2Tpp.objects.create(btx_id = btx_id,\
                                    page_name = page_name,\
                                    page_text = page_text)
                count += 1
            except:
                print('Milestone: ', i+1)
                print(btx_id, '##', page_name, '##', ' Count: ', i+1)
                continue

            print('Milestone: ', i+1)

        print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('TPP additional pages were migrated from CSV into DB!')