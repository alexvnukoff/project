from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from legacy_data.models import L_User
import datetime
import csv

def usersUpload(request):
    err = 0
    qty = 0
    time1 = datetime.datetime.now()

    #Upload from CSV file into buffer table
    with open('c:\\data\\users_legacy.csv', 'r') as f:
    #with open('c:\\data\\test.csv', 'r') as f:
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
        last_name = data[i][4]
        email = data[i][5]
        btx_id = data[i][7]

        if not len(data[i][6]):
            update_date = None
        else:
            last_visit_date = datetime.datetime.strptime(data[i][6], "%d.%m.%Y %H:%M")

        if not len(data[i][8]):
            update_date = None
        else:
            reg_date = datetime.datetime.strptime(data[i][8], "%d.%m.%Y %H:%M")

        L_User.objects.get_or_create(username = username,\
                                    is_active = is_active,\
                                    first_name = first_name,\
                                    last_name = last_name,\
                                    email = email,\
                                    btx_id = btx_id,\
                                    update_date = update_date,\
                                    last_visit_date = last_visit_date,\
                                    reg_date = reg_date)

        if not i%200:
            print(i)
    #print(data)
    #print(len(data))
    #L_User.objects.create()
    usr = L_User.objects.all()
    print('Количество пользователей:', usr.count())
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Время обработки:', time)
    return HttpResponse('Users were migrated!')
    #render_to_response('legacy_data/legacy_data_main.html', {'total_qty': 100, 'errors': err, 'elapsed_time': time})