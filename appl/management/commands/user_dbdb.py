from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import Group
from appl.models import Cabinet
from tpp.SiteUrlMiddleWare import get_request
from core.models import User
from django.utils.translation import trans_real
from random import randint
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
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
        photo_root = 'C:'
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
                i += 1
                continue

            new_user.first_name = usr.first_name
            new_user.last_name = usr.last_name
            new_user.is_active = True
            '''
            if len(usr.photo):
                photo_path = add(photo_root + usr.photo)
            else:
                photo_path = ''
            new_user.avatar = photo_path
            '''
            new_user.save()

            #create Cabinet for user

            try:
                user_cab = Cabinet.objects.get_or_create(title='CABINET_USER_ID_' + str(new_user.pk), user = new_user, create_user = new_user)

            except:
                User.objects.filter(pk = new_user.pk).delete()
                continue

            address = usr.addr_zip + ',' + usr.addr_country + ',' + usr.addr_state + ',' + usr.addr_city + usr.addr_street
            address.strip()

            attr = {
                    'ADDRESS': address,
                    'BIRTHDAY': usr.birth_date,
                    'ICQ': usr.icq,
                    #'IMAGE': photo_path,
                    'MOBILE_NUMBER': usr.cellular,
                    'PERSONAL_FAX': usr.fax,
                    'POSITION': usr.position,
                    'PROFESSION': usr.profession,
                    #'SEX': usr.gender,
                    'SITE_NAME': usr.personal_www,
                    'SKYPE': usr.skype,
                    'TELEPHONE_NUMBER': usr.phone,
                    'USER_FIRST_NAME': usr.first_name,
                    'USER_MIDDLE_NAME': usr.middle_name,
                    'USER_LAST_NAME': usr.last_name,
                }

            trans_real.activate('ru') #activate russian locale
            res = user_cab.setAttributeValue(attr, new_user)
            trans_real.deactivate() #deactivate russian locale
            if res:
                usr.tpp_id = new_user.pk
                usr.completed = True
                usr.save()

            #Add user to Company Creator Group
            g = Group.objects.get(name='Company Creator')
            g.user_set.add(new_user)

            if not i%200:
                print('Milestone: ', qty + i)
            i += 1

        print('Done. Quantity of processed strings:', qty + i)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)

        print('Users were migrated from buffer DB into TPP DB!')
