__author__ = 'Root'

from django.db.models.signals import post_syncdb
from django.contrib.auth.models import Group, Permission
import appl.models
from core.models import State

def databaseInitialization(sender, **kwargs):
    '''
       Create initial database objects for TPP project.
       Only run when model got created using signal post_syncdb
    '''

    #Default Groups with Permissions
    read_item = Permission.objects.get(codename='read_item')

    read_tpp = Permission.objects.get(codename='read_tpp')
    add_tpp = Permission.objects.get(codename='add_tpp')
    change_tpp = Permission.objects.get(codename='change_tpp')
    delete_tpp = Permission.objects.get(codename='delete_tpp')

    read_company = Permission.objects.get(codename='read_company')
    add_company = Permission.objects.get(codename='add_company')
    change_company = Permission.objects.get(codename='change_company')
    delete_company = Permission.objects.get(codename='delete_company')

    read_department = Permission.objects.get(codename='read_department')
    add_department = Permission.objects.get(codename='add_department')
    change_department = Permission.objects.get(codename='change_department')
    delete_department = Permission.objects.get(codename='delete_department')

    gr1, created = Group.objects.get_or_create(name='Default TPP Permissions')
    if created:
        gr1.permissions.add(read_tpp)

    gr2, created = Group.objects.get_or_create(name='Default Company Permissions')
    if created:
        gr2.permissions.add(read_company)

    gr3, created = Group.objects.get_or_create(name='Default Department Permissions')
    if created:
        gr3.permissions.add(read_department)

    gr4, created = Group.objects.get_or_create(name='Company Creator')
    if created:
        gr4.permissions.add(add_company, read_company)

    gr5, created = Group.objects.get_or_create(name='Owner')
    if created:
        gr5.permissions.add(read_company, change_company, delete_company,
                            read_department, change_department, delete_department)

    gr6, created = Group.objects.get_or_create(name='Admin')
    if created:
        gr6.permissions.add(read_company, change_company,
                            read_department, change_department)

    gr7, created = Group.objects.get_or_create(name='Staff')
    if created:
        gr7.permissions.add(read_company, read_department)

    #Default States
    st1, created=State.objects.get_or_create(title='Default TPP State', perm=gr1)
    st2, created=State.objects.get_or_create(title='Default Company State', perm=gr2)
    st3, created=State.objects.get_or_create(title='Default Department State')

post_syncdb.connect(databaseInitialization, sender=appl.models)