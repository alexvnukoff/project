from django.http import HttpResponse, Http404
from legacy_data.models import L_User, L_Company
from core.models import User
from random import randint
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
import datetime
import csv
from tpp.SiteUrlMiddleWare import get_request
import base64

def users_reload_CSV_DB(request):
    '''
        Reload user's data from prepared CSV file named users_legacy.csv
        into buffer DB table LEGACY_DATA_L_USER
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Load user data from CSV file into buffer table...')
    with open('c:\\data\\users_legacy.csv', 'r') as f:
    #with open('c:\\data\\test_users.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    for i in range(1, len(data), 1): # start since 1, avoid title string
        username = data[i][0]
        if (data[i][1] == 'Да'):
            is_active = True
        else:
            is_active = False

        if not len(data[i][2]):
            update_date = None
        else:
            update_date = datetime.datetime.strptime(data[i][2], "%d.%m.%Y %H:%M:%S")

        first_name = data[i][3]

        if data[i][4] == '':
            buf = data[i][3].split(' ')
            last_name = buf[0]
            first_name = ''
            for index in range(1, len(buf), 1):
                if index == len(buf):
                    first_name += buf[index]
                else:
                    first_name += buf[index]+' '
        else:
            last_name = data[i][4]

        email = data[i][5]
        btx_id = data[i][7]

        if not len(data[i][6]):
            last_visit_date = None
        else:
            last_visit_date = datetime.datetime.strptime(data[i][6], "%d.%m.%Y %H:%M")

        if not len(data[i][8]):
            reg_date = None
        else:
            reg_date = datetime.datetime.strptime(data[i][8], "%d.%m.%Y %H:%M")

        try:
            L_User.objects.get_or_create(username = username,\
                                    is_active = is_active,\
                                    first_name = first_name,\
                                    last_name = last_name,\
                                    email = email,\
                                    btx_id = btx_id,\
                                    update_date = update_date,\
                                    last_visit_date = last_visit_date,\
                                    reg_date = reg_date)
        except:
            return HttpResponse('Migration process from CSV file into buffer DB was interrupted!\
                                Possible reason is duplicated data.')

        if not i%200:
            print('Milestone: ', i)

    print('Done. Quantity of processed strings:', i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Users were migrated from CSV into DB!')

def users_reload_DB_DB(request):
    '''
        Reload user's data from buffer DB table LEGACY_DATA_L_USER
        into TPP User objects (CORE_USER table)
    '''
    time1 = datetime.datetime.now()
    # Move users from buffer table into original tables
    print('Reload users from buffer DB into TPP DB...')
    qty = L_User.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    user_lst = L_User.objects.filter(completed=False).all()
    i=1
    for usr in user_lst:
        request = get_request()
        # for data migration as batch process generate random IP address 0.rand().rand().rand() for avoiding bot checking
        request.META['REMOTE_ADDR'] = '0.'+str(randint(0, 255))+'.'+str(randint(0, 255))+'.'+str(randint(0, 255))
        try:
            new_user = User.objects.create_user(username=usr.username, email=usr.email, password=str(randint(1000000, 9999999)))
        except:
            return HttpResponse('Migration process from buffer DB into TPP DB was interrupted!\
                                Possible reason is duplicated data.')
        new_user.first_name=usr.first_name
        new_user.last_name=usr.last_name
        new_user.is_active = True
        new_user.save()

        usr.tpp_id=new_user.pk
        usr.completed = True
        usr.save()

        if not i%200:
            print('Milestone: ', qty + i)
        i += 1

    print('Done. Quantity of processed strings:', qty + i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)

    return HttpResponse('Users were migrated from buffer DB into TPP DB!')

def users_reload_email_sent(request):
    '''
        For users which were reloaded from prepared CSV file named users_legacy.csv
        send e-mail with url for password change notification.
    '''
    time1 = datetime.datetime.now()
    # Move users from buffer table into original tables
    print('Sending notifications to users about password changing.')
    qty = L_User.objects.filter(completed=True, email_sent=True).count()
    print('Already was sent: ', qty)
    user_list = L_User.objects.filter(completed=True, email_sent=False).all()
    if len(user_list):
        for usr in user_list:
            form = PasswordResetForm({'email': usr.email})
            form.is_valid()
            form.save(from_email=settings.DEFAULT_FROM_EMAIL, email_template_name='legacy_data/password_reset_email.html')
            usr.email_sent=True
            usr.save()
    else:
        return HttpResponse('Nothing to send!')

    print('Done. Notifications to users were sent!')
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)

    return HttpResponse('Migrated users were notified by e-mail!')

def company_reload_CSV_DB(request):
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
        detail_picture = bytearray(data[i][3]).decode(encoding='utf-8')

        if not len(data[i][4]):
            create_date = None
        else:
            create_date = datetime.datetime.strptime(bytearray(data[i][4]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

        tpp_name = bytearray(data[i][5]).decode(encoding='utf-8')
        moderator = bytearray(data[i][6]).decode(encoding='utf-8')
        if len(data[i][7]):
            full_name = bytearray(data[i][7]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", '').strip()
        else:
            full_name = short_name
        ur_address = bytearray(data[i][8]).decode(encoding='utf-8')
        fact_address = bytearray(data[i][9]).decode(encoding='utf-8')
        tel = bytearray(data[i][10]).decode(encoding='utf-8')
        fax = bytearray(data[i][11]).decode(encoding='utf-8')
        email = bytearray(data[i][12]).decode(encoding='utf-8')
        INN = bytearray(data[i][13]).decode(encoding='utf-8')
        KPP = bytearray(data[i][14]).decode(encoding='utf-8')
        OKVED = bytearray(data[i][24]).decode(encoding='utf-8')
        OKATO = bytearray(data[i][25]).decode(encoding='utf-8')
        OKPO = bytearray(data[i][26]).decode(encoding='utf-8')
        bank_account = bytearray(data[i][15]).decode(encoding='utf-8')
        bank_name = bytearray(data[i][16]).decode(encoding='utf-8')
        director_name = bytearray(data[i][17]).decode(encoding='utf-8')
        bux_name = bytearray(data[i][18]).decode(encoding='utf-8')
        slogan = bytearray(data[i][19]).decode(encoding='utf-8')

        if (data[i][20] == 'Да'):
            is_active = True
        else:
            is_active = False

        branch = bytearray(data[i][21]).decode(encoding='utf-8')
        experts = bytearray(data[i][22]).decode(encoding='utf-8')
        map_id = bytearray(data[i][23]).decode(encoding='utf-8')
        site = bytearray(data[i][27]).decode(encoding='utf-8')
        country_name = bytearray(data[i][28]).decode(encoding='utf-8')

        if (data[i][29] == 'Да'):
            is_deleted = True
        else:
            is_deleted = False

        keywords = bytearray(data[i][30]).decode(encoding='utf-8').replace("&quot;", '"').replace("quot;", '"').\
                                            replace("&amp;", '').strip()

        try:
            L_Company.objects.get_or_create(
                                            btx_id = btx_id,\
                                            short_name = short_name,\
                                            detail_page_url = detail_page_url,\
                                            detail_picture = detail_picture,\
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
            print('Milestone: ', i+1)
            #print(btx_id, '##', short_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Companies were migrated from CSV into DB!')
