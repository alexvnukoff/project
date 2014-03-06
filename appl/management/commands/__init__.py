from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        '''
            Reload companies' data from prepared CSV file named companies_legacy.csv
            into buffer DB table LEGACY_DATA_L_COMPANY
        '''
        time1 = datetime.datetime.now()
        #Upload from CSV file into buffer table
        print('Load company data from CSV file into buffer table...')
        with open('c:\\data\\companies_legacy.csv', 'r') as f:
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
            short_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
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

            tpp_name = bytearray(data[i][8]).decode(encoding='utf-8')
            moderator = bytearray(data[i][9]).decode(encoding='utf-8')
            if len(data[i][10]):
                full_name = bytearray(data[i][10]).decode(encoding='utf-8').replace("&quot;", '"').\
                                    replace("quot;", '"').replace("&amp;", '').strip()
            else:
                full_name = short_name
            ur_address = bytearray(data[i][11]).decode(encoding='utf-8')
            fact_address = bytearray(data[i][12]).decode(encoding='utf-8')
            tel = bytearray(data[i][13]).decode(encoding='utf-8')
            fax = bytearray(data[i][14]).decode(encoding='utf-8')
            email = bytearray(data[i][15]).decode(encoding='utf-8')
            INN = bytearray(data[i][16]).decode(encoding='utf-8')
            KPP = bytearray(data[i][17]).decode(encoding='utf-8')
            OKVED = bytearray(data[i][27]).decode(encoding='utf-8')
            OKATO = bytearray(data[i][28]).decode(encoding='utf-8')
            OKPO = bytearray(data[i][29]).decode(encoding='utf-8')
            bank_account = bytearray(data[i][18]).decode(encoding='utf-8')
            bank_name = bytearray(data[i][19]).decode(encoding='utf-8')
            director_name = bytearray(data[i][20]).decode(encoding='utf-8')
            bux_name = bytearray(data[i][21]).decode(encoding='utf-8')
            slogan = bytearray(data[i][22]).decode(encoding='utf-8')

            if (data[i][23] == 'Y'):
                is_active = True
            else:
                is_active = False

            branch = bytearray(data[i][24]).decode(encoding='utf-8')
            experts = bytearray(data[i][25]).decode(encoding='utf-8')
            map_id = bytearray(data[i][26]).decode(encoding='utf-8')
            site = bytearray(data[i][30]).decode(encoding='utf-8')
            country_name = bytearray(data[i][31]).decode(encoding='utf-8')

            if (data[i][32] == 'Y'):
                is_deleted = True
            else:
                is_deleted = False

            keywords = bytearray(data[i][33]).decode(encoding='utf-8').replace("&quot;", '"').replace("quot;", '"').\
                                                replace("&amp;", '').strip()

            try:
                L_Company.objects.create(
                                                btx_id = btx_id,\
                                                short_name = short_name,\
                                                detail_page_url = detail_page_url,\
                                                preview_picture = preview_picture,\
                                                preview_text = preview_text,\
                                                detail_picture = detail_picture,\
                                                detail_text = detail_text,\
                                                create_date = create_date,\
                                                tpp_name = tpp_name,\
                                                moderator = moderator,\
                                                full_name = full_name,\
                                                ur_address = ur_address,\
                                                fact_address = fact_address,\
                                                tel = tel,\
                                                fax = fax,\
                                                email = email,\
                                                INN = INN,\
                                                KPP = KPP,\
                                                OKVED = OKVED,\
                                                OKATO = OKATO,\
                                                OKPO = OKPO,\
                                                bank_account = bank_account,\
                                                bank_name = bank_name,\
                                                director_name = director_name,\
                                                bux_name = bux_name,\
                                                slogan = slogan,\
                                                is_active = is_active,\
                                                branch = branch,\
                                                experts = experts,\
                                                map_id = map_id,\
                                                site = site,\
                                                country_name = country_name,\
                                                is_deleted = is_deleted,\
                                                keywords = keywords)
                count += 1
            except:
                #print('Milestone: ', i+1)
                print(btx_id, '##', short_name, '##', ' Count: ', i+1)
                continue

            #print('Milestone: ', i+1)

        print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)