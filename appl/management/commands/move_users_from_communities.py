from django.core.management.base import NoArgsCommand
from core.models import Relationship
from appl.models import Tpp, Company, Department, Cabinet, Vacancy
from django.contrib.auth.models import Group
from django.utils.translation import trans_real
import datetime

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        '''
            Move Users from community groups ('ORG-') and attach User's Cabinets to Vacancy
        '''
        count = 0
        time1 = datetime.datetime.now()
        print('Migrate Users from community Groups into Vacancy structure...')
        #cycle through Companies
        comp_lst = Company.objects.all()
        for comp in comp_lst:
            try:
                g = Group.objects.get(pk=comp.community)
            except:
                continue

            #get all users from current group
            usr_list = g.user_set.all()

            #cycle through Users in current Company's ORG group
            if len(usr_list):
                for usr in usr_list:
                    cab, res = Cabinet.objects.get_or_create(user=usr, create_user=usr)
                    if res:
                        try:
                            cab.setAttributeValue({'USER_FIRST_NAME': usr.first_name, 'USER_MIDDLE_NAME': '',
                                                    'USER_LAST_NAME': usr.last_name, 'EMAIL': usr.email}, usr)
                            group = Group.objects.get(name='Company Creator')
                            usr.is_manager = True
                            usr.save()
                            group.user_set.add(usr)
                        except:
                            pass

                    # create department 'Администрация' and add through signal vacancy 'Работник(ца)'
                    try:
                        dep, flag = Department.objects.get_or_create(title='DEPARTMENT_FOR_COMP_ID:' + str(comp.pk),
                                                                     create_user=usr)
                        if flag:
                            #activate russian locale
                            trans_real.activate('ru')
                            res = dep.setAttributeValue({'NAME': 'Администрация'}, usr)
                            #deactivate russian locale
                            trans_real.deactivate()
                            if not res:
                                dep.delete()
                                continue
                            try:
                                Relationship.objects.create(parent=comp, child=dep, type='hierarchy', create_user=usr)
                            except:
                                print('Can not create Relationship between Department ID' + dep.pk +
                                      ' and Company ID' + comp.pk)
                                dep.delete()
                    except Exception as e:
                        print('Can not create Department for Company ID:' + comp.pk + '. The reason is:' + str(e))
                        continue

                    try:
                        vac = Vacancy.objects.get(c2p__parent__c2p__parent=comp.pk, p2c__child=None)
                    except:
                        try:
                            vac = Vacancy.objects.create(title='VACANCY_FOR_ORGANIZATION_ID:' + str(dep.pk),
                                                         create_user=usr)
                            #activate russian locale
                            trans_real.activate('ru')
                            res = vac.setAttributeValue({'NAME': 'Работник(ца)'}, usr)
                            #deactivate russian locale
                            trans_real.deactivate()
                            if not res:
                                vac.delete()
                                continue
                            try:
                                Relationship.objects.create(parent=dep, child=vac, type='hierarchy', create_user=usr)
                                #add current user to default Vacancy
                            except Exception as e:
                                print('Can not create Relationship between Vacancy ID:' + vac.pk +
                                      'and Department ID:' + dep.pk + '. The reason is:' + str(e))
                                vac.delete()
                                continue
                        except Exception as e:
                            print('Can not create Vacancy for Department ID:' + dep.pk + '. The reason is:' + str(e))
                            continue

                    if usr.is_manager:
                        is_admin = True
                    else:
                        is_admin = False

                    try:
                        Relationship.objects.create(parent=vac, child=cab, type='hierarchy',
                                                    is_admin=is_admin, create_user=usr)
                        #g.user_set.remove(usr)
                    except:
                        vac.delete()
                        continue

            #cycle through Company Departments' community Group
            dep_list = Department.objects.filter(c2p__parent=comp.pk)
            for dep in dep_list:
                if dep.community:
                    dep_g = Group.objects.get(pk=dep.community)
                    dep_usr_list = dep_g.user_set.all()
                    for usr in dep_usr_list:
                        cab, res = Cabinet.objects.get_or_create(user=usr, create_user=usr)
                        if res:
                            try:
                                cab.setAttributeValue({'USER_FIRST_NAME': usr.first_name, 'USER_MIDDLE_NAME': '',
                                                        'USER_LAST_NAME': usr.last_name, 'EMAIL': usr.email}, usr)
                                group = Group.objects.get(name='Company Creator')
                                usr.is_manager = True
                                usr.save()
                                group.user_set.add(usr)
                            except:
                                pass

                        try:
                            vac = Vacancy.objects.get(c2p__parent=dep.pk, p2c__child=None)
                        except:
                            try:
                                vac = Vacancy.objects.create(title='VACANCY_FOR_ORGANIZATION_ID:' + str(dep.pk),
                                                             create_user=usr)
                                #activate russian locale
                                trans_real.activate('ru')
                                res = vac.setAttributeValue({'NAME': 'Работник(ца)'}, usr)
                                #deactivate russian locale
                                trans_real.deactivate()
                                if not res:
                                    vac.delete()
                                    continue

                                try:
                                    Relationship.objects.create(parent=dep, child=vac,
                                                                type='hierarchy', create_user=usr)

                                #add current user to default Vacancy
                                except Exception as e:
                                    print('Can not create Relationship between Vacancy ID:' + vac.pk +
                                          'and Department ID:' + dep.pk + '. The reason is:' + str(e))
                                    vac.delete()
                                    continue

                            except Exception as e:
                                print('Can not create Vacancy for Department ID:' + dep.pk +
                                      '. The reason is:' + str(e))
                                continue

                        if usr.is_manager:
                            is_admin = True
                        else:
                            is_admin = False

                        try:
                            Relationship.objects.create(parent=vac, child=cab, type='hierarchy',
                                                        is_admin=is_admin, create_user=usr)
                        #g.user_set.remove(usr)
                        except:
                            vac.delete()
                            continue
                # if Department hasn't community
                else:
                    continue

        print('Companies communities were Migrate. Starting migration of TPP community '
              'Groups into Vacancy structure...')

        #cycle through TPP
        tpp_lst = Tpp.objects.all()
        for tpp in tpp_lst:
            tpp.pk = 1

        print('Done. Quantity of processed users:', count)
        time2 = datetime.datetime.now()
        time = time2-time1
        print('Elapsed time:', time)
        print('Users were migrated from community Groups!')
