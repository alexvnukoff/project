from django.http import HttpResponse, Http404
from legacy_data.models import L_User, L_Company, L_Product, L_TPP
from core.models import User, Relationship
from core.amazonMethods import add
from appl.models import Company, Tpp, Product, Country
from random import randint
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import Group
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
    with open('c:\\data\\user_legacy.csv', 'r') as f:
    #with open('c:\\data\\test_users.csv', 'r') as f:
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

        try:
            L_User.objects.get_or_create(username = username,\
                                    is_active = is_active,\
                                    first_name = first_name,\
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
                                    addr_street = addr_street,\
                                    addr_city = addr_city,\
                                    addr_state = addr_state,\
                                    addr_zip = addr_zip,\
                                    addr_country = addr_country,\
                                    company = company,\
                                    department = department,\
                                    position = position)
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
            #return HttpResponse('Migration process from buffer DB into TPP DB was interrupted!\
            #                    Possible reason is duplicated data.')
            print(usr.username, '##', usr.email, '##', ' Count: ', i)
            i +=1
            continue

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
    return HttpResponse('Companies were migrated from CSV into DB!')

def company_reload_DB_DB(request):
    '''
        Reload companies' data from buffer DB table LEGACY_DATA_L_COMPANY into TPP DB
    '''
    img_root = 'c:' #additional path to images
    time1 = datetime.datetime.now()
    # Move users from buffer table into original tables
    print('Data validation. Please, wait...')
    qty = L_Company.objects.filter(country_name='').count()
    if qty:
        L_Company.objects.filter(country_name='').delete()
        print('Were deleted companies without countries: ', qty)
    print('Reload companies from buffer DB into TPP DB...')
    qty = L_Company.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    flag = True
    block_size = 1000
    i = 0
    while flag:
        comp_lst = L_Company.objects.filter(completed=False).all()[:block_size]
        if len(comp_lst) < block_size: # it will last big loop
            flag = False
        #comp_lst = L_Company.objects.exclude(preview_picture='')[:2]
        #comp_lst = L_Company.objects.filter(pk=545208)

        for leg_cmp in comp_lst:
            #set create_user (owner) for the Company
            if leg_cmp.moderator:
                try:
                    l_user = L_User.objects.get(btx_id=leg_cmp.moderator)
                    create_usr = User.objects.get(pk=l_user.tpp_id)
                except:
                    create_usr = User.objects.get(pk=1)
            else:
                create_usr = User.objects.get(pk=1)

            try:
                new_comp = Company.objects.create(title='COMPANY_LEG_ID:'+leg_cmp.btx_id,
                                                  create_user=create_usr)
            except:
                print(leg_cmp.btx_id, '##', leg_cmp.short_name, '##', ' Count: ', i)
                i += 1
                continue
            '''
            if len(leg_cmp.preview_picture):
                img_small_path = add(img_root + leg_cmp.preview_picture)
            else:
                img_small_path = ''
            if len(leg_cmp.detail_picture):
                img_detail_path = add(img_root + leg_cmp.detail_picture)
            else:
                img_detail_path = ''
            '''
            img_small_path = ''
            img_detail_path = ''
            attr = {'NAME': leg_cmp.short_name,
                    'IMAGE_SMALL': img_small_path,
                    'ANONS': leg_cmp.preview_text,
                    'IMAGE': img_detail_path,
                    'DETAIL_TEXT': leg_cmp.detail_text,
                    'NAME_FULL': leg_cmp.full_name,
                    'ADDRESS_YURID': leg_cmp.ur_address,
                    'ADDRESS_FACT': leg_cmp.fact_address,
                    'ADDRESS': leg_cmp.fact_address,
                    'TELEPHONE_NUMBER': leg_cmp.tel,
                    'FAX': leg_cmp.fax,
                    'EMAIL': leg_cmp.email,
                    'INN': leg_cmp.INN,
                    'KPP': leg_cmp.KPP,
                    'OKVED': leg_cmp.OKVED,
                    'OKATO': leg_cmp.OKATO,
                    'OKPO': leg_cmp.OKPO,
                    'BANK_ACCOUNT': leg_cmp.bank_account,
                    'BANK_NAME': leg_cmp.bank_name,
                    'NAME_DIRECTOR': leg_cmp.director_name,
                    'NAME_BUX': leg_cmp.bux_name,
                    'SLOGAN': leg_cmp.slogan,
                    'MAP_POSITION': leg_cmp.map_id,
                }

            res = new_comp.setAttributeValue(attr, create_usr)
            if res:
                leg_cmp.tpp_id = new_comp.pk
                leg_cmp.completed = True
                leg_cmp.save()
                if not leg_cmp.tpp_name:
                    new_comp.end_date = datetime.datetime.now()
                    new_comp.save()
            else:
                print('Problems with Attributes adding!')
                i += 1
                continue

            # add workers to Company's community
            lst_wrk = L_User.objects.filter(company=leg_cmp.short_name)
            for wrk in lst_wrk:
                g = Group.objects.get(name=new_comp.community)
                try:
                    wrk_obj = User.objects.get(pk=wrk.tpp_id)
                    g.user_set.add(wrk_obj)
                except:
                    continue

            # create relationship type=Dependence with country
            try: #if there isn't country in Company take it from TPP
                prnt = Country.objects.get(item2value__attr__title="NAME", item2value__title=leg_cmp.country_name)
            except:
                tpp = L_TPP.objects.filter(btx_id=leg_cmp.tpp_name)
                try:
                    prnt = Country.objects.get(item2value__attr__title="NAME", item2value__title=tpp[0].country)
                except:
                    L_Company.objects.get(btx_id=leg_cmp.btx_id).delete()
                    Company.objects.get(pk=leg_cmp.tpp_id).delete()
                    i += 1
                    continue

            Relationship.objects.get_or_create(parent=prnt, type='dependence', child=new_comp, create_user=create_usr)

            i += 1
            print('Milestone: ', qty + i)

    print('Done. Quantity of processed strings:', qty + i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Companies were migrated from buffer DB into TPP DB!')


def product_reload_CSV_DB(request):
    '''
        Reload products' data from prepared CSV file named product_legacy.csv
        into buffer DB table LEGACY_DATA_L_PRODUCT
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Load product data from CSV file into buffer table...')
    csv.field_size_limit(4000000)
    with open('c:\\data\\product_legacy.csv', 'r') as f:
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
    return HttpResponse('Products were migrated from CSV into DB!')


def product_reload_DB_DB(request):
    '''
        Reload products' data from buffer DB table LEGACY_DATA_L_PRODUCT into TPP DB
    '''
    img_root = 'c:' #additional path to images
    time1 = datetime.datetime.now()
    # Move products from buffer table into original tables
    print('Reload products from buffer DB into TPP DB...')
    qty = L_Product.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    prod_lst = L_Product.objects.filter(completed=False).all()
    #comp_lst = L_Company.objects.exclude(preview_picture='')[:2]
    #comp_lst = L_Company.objects.filter(pk=545208)
    i = 0
    create_usr = User.objects.get(pk=1)
    for leg_prod in prod_lst:
        try:
            new_prod = Company.objects.create(title='COMPANY_LEG_ID:'+leg_prod.btx_id,
                                              create_user=create_usr)
        except:
            print(leg_prod.btx_id, '##', leg_prod.prod_name, '##', ' Count: ', i)
            i += 1
            continue
        '''
        if len(leg_prod.preview_picture):
            img_small_path = add(img_root + leg_prod.preview_picture)
        else:
            img_small_path = ''
        if len(leg_prod.detail_picture):
            img_detail_path = add(img_root + leg_prod.detail_picture)
        else:
            img_detail_path = ''
        '''
        img_small_path = ''
        img_detail_path = ''
        attr = {
                'NAME': leg_prod.prod_name,
                'IMAGE_SMALL': img_small_path,
                'ANONS': leg_prod.preview_text,
                'IMAGE': img_detail_path,
                'DETAIL_TEXT': leg_prod.detail_text,
                'DISCOUNT': leg_prod.discount,
            }

        try: #this try for problem with bulk create for fields about 3000 symbols.
            res = new_prod.setAttributeValue(attr, create_usr)
            if res:
                leg_prod.tpp_id = new_prod.pk
                leg_prod.completed = True
                leg_prod.save()
            else:
                print('Problems with Attributes adding!')
                i += 1
                continue
        except:
            attr = {
                    'NAME': leg_prod.prod_name[0:2000],
                    'IMAGE_SMALL': img_small_path[0:2000],
                    'ANONS': leg_prod.preview_text[0:2000],
                    'IMAGE': img_detail_path[0:2000],
                    'DETAIL_TEXT': leg_prod.detail_text[0:2000],
                    'DISCOUNT': leg_prod.discount[0:2000],
                }
            res = new_prod.setAttributeValue(attr, create_usr)
            if res:
                leg_prod.tpp_id = new_prod.pk
                leg_prod.completed = True
                leg_prod.save()
            else:
                print('Problems with Attributes adding!')
                i += 1
                continue

        # create relationship type=Dependence with Company
        try:
            prod_cmp = L_Company.objects.get(btx_id=leg_prod.company_id)
            prnt = Company.objects.get(pk=prod_cmp.tpp_id)
        except:
            continue

        Relationship.objects.get_or_create(parent=prnt, type='dependence', child=new_prod, create_user=create_usr)

        i += 1
        print('Milestone: ', qty + i)

    print('Done. Quantity of processed strings:', qty + i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Products were migrated from buffer DB into TPP DB!')

def tpp_reload_CSV_DB(request):
    '''
        Reload TPPs' data from prepared CSV file named product_legacy.csv
        into buffer DB table LEGACY_DATA_L_TPP
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Load product data from CSV file into buffer table...')
    with open('c:\\data\\tpp_legacy.csv', 'r') as f:
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
        tpp_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
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

        country = bytearray(data[i][8]).decode(encoding='utf-8')
        moderator = bytearray(data[i][9]).decode(encoding='utf-8')
        head_pic = bytearray(data[i][10]).decode(encoding='utf-8')
        logo = bytearray(data[i][11]).decode(encoding='utf-8')
        domain = bytearray(data[i][12]).decode(encoding='utf-8')
        header_letter = bytearray(data[i][13]).decode(encoding='utf-8')
        member_letter = bytearray(data[i][14]).decode(encoding='utf-8')
        address = bytearray(data[i][15]).decode(encoding='utf-8')
        email = bytearray(data[i][16]).decode(encoding='utf-8')
        fax = bytearray(data[i][17]).decode(encoding='utf-8')
        map = bytearray(data[i][18]).decode(encoding='utf-8')
        tpp_parent = bytearray(data[i][19]).decode(encoding='utf-8')
        phone = bytearray(data[i][20]).decode(encoding='utf-8')
        extra = bytearray(data[i][21]).decode(encoding='utf-8')

        try:
            L_TPP.objects.create(btx_id = btx_id,\
                                tpp_name = tpp_name,\
                                detail_page_url = detail_page_url,\
                                preview_picture = preview_picture,\
                                preview_text = preview_text,\
                                detail_picture = detail_picture,\
                                detail_text = detail_text,\
                                create_date = create_date,\
                                country = country,\
                                moderator = moderator,\
                                head_pic = head_pic,\
                                logo = logo,\
                                domain = domain,\
                                header_letter = header_letter,\
                                member_letter = member_letter,\
                                address = address,\
                                email = email,\
                                fax = fax,\
                                map = map,\
                                tpp_parent = tpp_parent,\
                                phone = phone,\
                                extra = extra)
            count += 1
        except:
            print('Milestone: ', i+1)
            print(btx_id, '##', tpp_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('TPPs were migrated from CSV into DB!')
