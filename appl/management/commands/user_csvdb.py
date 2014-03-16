from django.core.management.base import NoArgsCommand
import csv
import os
import datetime
import base64
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Reload user's data from prepared CSV file named users_legacy.csv
            into buffer DB table LEGACY_DATA_L_USER
        '''
        time1 = datetime.datetime.now()
        #Upload from CSV file into buffer table
        print('Load user data from CSV file into buffer table...')
        with open(os.path.join('c:', 'data', 'user_legacy.csv'), 'r') as f:
            reader = csv.reader(f, delimiter=';')
            data = [row for row in reader]

        for i in range(0, len(data), 1):
            sz1 = len(data[i])
            for k in range(0, sz1, 1):
                data[i][k] = base64.standard_b64decode(data[i][k])

            username = bytearray(data[i][0]).decode(encoding='utf-8')
            if (bytearray(data[i][1]).decode(encoding='utf-8') == 'Y'):
                is_active = True
            else:
                is_active = False

            if not len(bytearray(data[i][2]).decode(encoding='utf-8')):
                update_date = None
            else:
                update_date = datetime.datetime.strptime(bytearray(data[i][2]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

            first_name = bytearray(data[i][3]).decode(encoding='utf-8')

            if bytearray(data[i][4]).decode(encoding='utf-8') == '':
                buf = bytearray(data[i][3]).decode(encoding='utf-8').split(' ')
                last_name = buf[0]
                first_name = ''
                for index in range(1, len(buf), 1):
                    if index == len(buf):
                        first_name += buf[index]
                    else:
                        first_name += buf[index]+' '
            else:
                last_name = bytearray(data[i][4]).decode(encoding='utf-8')

            email = bytearray(data[i][5]).decode(encoding='utf-8')

            if not len(bytearray(data[i][6]).decode(encoding='utf-8')):
                last_visit_date = None
            else:
                last_visit_date = datetime.datetime.strptime(bytearray(data[i][6]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

            btx_id = bytearray(data[i][7]).decode(encoding='utf-8')

            if not len(bytearray(data[i][8]).decode(encoding='utf-8')):
                reg_date = None
            else:
                reg_date = datetime.datetime.strptime(bytearray(data[i][8]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

            profession = bytearray(data[i][9]).decode(encoding='utf-8')
            personal_www = bytearray(data[i][10]).decode(encoding='utf-8')
            icq = bytearray(data[i][11]).decode(encoding='utf-8')
            gender = bytearray(data[i][12]).decode(encoding='utf-8')
            birth_date = None #datetime.datetime.strptime(bytearray(data[i][13]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")
            photo = bytearray(data[i][14]).decode(encoding='utf-8')
            phone = bytearray(data[i][15]).decode(encoding='utf-8')
            fax = bytearray(data[i][16]).decode(encoding='utf-8')
            cellular = bytearray(data[i][17]).decode(encoding='utf-8')
            addr_street = bytearray(data[i][18]).decode(encoding='utf-8')
            addr_city = bytearray(data[i][19]).decode(encoding='utf-8')
            addr_state = bytearray(data[i][20]).decode(encoding='utf-8')
            addr_zip = bytearray(data[i][21]).decode(encoding='utf-8')
            addr_country = bytearray(data[i][22]).decode(encoding='utf-8')
            company = bytearray(data[i][23]).decode(encoding='utf-8')
            department = bytearray(data[i][24]).decode(encoding='utf-8')
            position = bytearray(data[i][25]).decode(encoding='utf-8')
            mid_name = bytearray(data[i][26]).decode(encoding='utf-8')
            skp = bytearray(data[i][27]).decode(encoding='utf-8')

            try:
                leg_usr, created = L_User.objects.get_or_create(username = username,\
                                        is_active = is_active,\
                                        first_name = first_name,\
                                        middle_name = mid_name,\
                                        last_name = last_name,\
                                        email = email,\
                                        btx_id = btx_id,\
                                        update_date = update_date,\
                                        last_visit_date = last_visit_date,\
                                        reg_date = reg_date,\
                                        profession = profession,\
                                        personal_www = personal_www,\
                                        icq = icq,\
                                        gender = gender,\
                                        birth_date = birth_date,\
                                        photo = photo,\
                                        phone = phone,\
                                        fax = fax,\
                                        cellular = cellular,\
                                        skype = skp,\
                                        addr_street = addr_street,\
                                        addr_city = addr_city,\
                                        addr_state = addr_state,\
                                        addr_zip = addr_zip,\
                                        addr_country = addr_country,\
                                        company = company,\
                                        department = department,\
                                        position = position)

                if not created:
                    leg_usr.middle_name = mid_name
                    leg_usr.skype = skp
                    leg_usr.save()

            except:
                print('Migration process from CSV file into buffer DB was interrupted!\
                                    Possible reason is duplicated data.')

            if not i%200:
                print('Milestone: ', i)

        print('Done. Quantity of processed strings:', i)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Users were migrated from CSV into DB!')
