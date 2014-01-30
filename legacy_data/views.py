from django.http import HttpResponse, Http404
from legacy_data.models import L_User
from core.models import User
from random import randint
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
import datetime
import csv

def users_reload_CSV_DB(request):
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Load user data from CSV file into buffer table...')
    #with open('c:\\data\\users_legacy.csv', 'r') as f:
    with open('c:\\data\\test.csv', 'r') as f:
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
            update_date = datetime.datetime.strptime(data[i][2], "%d.%m.%Y %H:%M")

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
            usr = L_User.objects.get_or_create(username = username,\
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
    time1 = datetime.datetime.now()
    # Move users from buffer table into original tables
    print('Reload users from buffer DB into TPP DB...')
    qty = L_User.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    user_lst = L_User.objects.filter(completed=False).all()
    i=1
    for usr in user_lst:
        try:
            new_user = User.objects.create_user(username=usr.username, email=usr.email, password=str(randint(1000000, 9999999)))
        except:
            return HttpResponse('Migration process from buffer DB into TPP DB was interrupted!\
                                Possible reason is duplicated data (e-mail field).')
        new_user.first_name=usr.first_name
        new_user.last_name=usr.last_name
        new_user.is_active = True
        new_user.save()
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