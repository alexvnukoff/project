from django.core.management.base import NoArgsCommand
import csv
import os
import datetime
import base64
from legacy_data.models import *
from dateutil import parser

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload Innovative Projects data from prepared CSV file named innov_prj_legacy.csv
            into buffer DB table LEGACY_DATA_L_INNPRJ
        '''
        time1 = datetime.datetime.now()
        #Upload from CSV file into buffer table
        print('Loading Innovative Projects from CSV file into buffer table...')
        with open(os.path.join("c:", "data", "innov_prj_legacy.csv"), 'r') as f:
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
            prj_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                    replace("quot;", '"').replace("&amp;", "&").strip()
            detail_page_url = bytearray(data[i][2]).decode(encoding='utf-8')
            preview_picture = bytearray(data[i][3]).decode(encoding='utf-8')
            preview_text = bytearray(data[i][4]).decode(encoding='utf-8')
            detail_picture = bytearray(data[i][5]).decode(encoding='utf-8')
            detail_text = bytearray(data[i][6]).decode(encoding='utf-8')

            if not len(data[i][7]):
                create_date = None
            else:
                create_date = datetime.datetime.strptime(bytearray(data[i][7]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

            author = bytearray(data[i][8]).decode(encoding='utf-8')
            industry = bytearray(data[i][9]).decode(encoding='utf-8')
            company = bytearray(data[i][10]).decode(encoding='utf-8')
            tpp = bytearray(data[i][11]).decode(encoding='utf-8')
            prj_title = bytearray(data[i][12]).decode(encoding='utf-8')
            fax = bytearray(data[i][13]).decode(encoding='utf-8')
            phone = bytearray(data[i][14]).decode(encoding='utf-8')
            email = bytearray(data[i][15]).decode(encoding='utf-8')
            tech_info = bytearray(data[i][16]).decode(encoding='utf-8')
            deleted = bytearray(data[i][17]).decode(encoding='utf-8')
            keywords = bytearray(data[i][18]).decode(encoding='utf-8')
            private_name = bytearray(data[i][19]).decode(encoding='utf-8')
            private_resume = bytearray(data[i][20]).decode(encoding='utf-8')
            country = bytearray(data[i][21]).decode(encoding='utf-8')
            site = bytearray(data[i][22]).decode(encoding='utf-8')
            project_name = bytearray(data[i][23]).decode(encoding='utf-8')
            project_point = bytearray(data[i][24]).decode(encoding='utf-8')
            target_community = bytearray(data[i][25]).decode(encoding='utf-8')
            prj_sum = bytearray(data[i][26]).decode(encoding='utf-8')

            if not len(data[i][27]):
                estim_date = None
            else:
                #estim_date = datetime.datetime.strptime(bytearray(data[i][27]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")
                estim_date = parser.parse(bytearray(data[i][27]).decode(encoding='utf-8'))

            bp_decrip = bytearray(data[i][28]).decode(encoding='utf-8')
            bp_file = bytearray(data[i][29]).decode(encoding='utf-8')
            photos = bytearray(data[i][30]).decode(encoding='utf-8')


            try:
                L_InnPrj.objects.create(btx_id = btx_id,\
                                    prj_name = prj_name,\
                                    detail_page_url = detail_page_url,\
                                    preview_picture = preview_picture,\
                                    preview_text = preview_text,\
                                    detail_picture = detail_picture,\
                                    detail_text = detail_text,\
                                    create_date = create_date,\
                                    author = author,\
                                    industry = industry,\
                                    company = company,\
                                    tpp = tpp,\
                                    prj_title = prj_title,\
                                    fax = fax,\
                                    phone = phone,\
                                    email = email,\
                                    tech_info = tech_info,\
                                    deleted = deleted,\
                                    keywords = keywords,\
                                    private_name = private_name,\
                                    private_resume = private_resume,\
                                    country = country,\
                                    site = site,\
                                    project_name = project_name,\
                                    project_point = project_point,\
                                    target_community = target_community,\
                                    prj_sum = prj_sum,\
                                    estim_date = estim_date,\
                                    bp_decrip = bp_decrip,\
                                    bp_file = bp_file,\
                                    photos = photos)
                count += 1
            except:
                print('Milestone: ', i+1)
                print(btx_id, '##', prj_name, '##', ' Count: ', i+1)
                continue

            print('Milestone: ', i+1)

        print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Innovative Projects were migrated from CSV into DB!')
