__author__ = 'Root'

from django.db.models.signals import post_syncdb
from django.contrib.auth.models import Group, Permission
import appl.models
from appl.models import SystemMessages, Country
from core.models import State, Attribute, Value, Slot, Dictionary, User

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

    attributes = {  'ADDRESS': 'Chr',
                    'ADDRESS_YURID': 'Chr',
                    'ADDRESS_FACT': 'Chr',
                    'ADDRESS_COUNTRY': 'Chr',
                    'ADDRESS_CITY': 'Chr',
                    'ADDRESS_ZIP': 'Chr',
                    'AUTHOR_NAME': 'Chr',
                    'ANONS': 'Str',
                    'BANK_ACCOUNT': 'Chr',
                    'BANK_NAME': 'Chr',
                    'COST': 'Flo',
                    'COUPON_DISCOUNT': 'Flo',
                    'CURRENCY': {'type': 'Chr', 'slots': ['USD', 'EUR', 'RUB']},
                    'DETAIL_TEXT': 'Str',
                    'DISCOUNT': 'Flo',
                    'DOCUMENT_1': 'Ffl',
                    'DOCUMENT_2': 'Ffl',
                    'DOCUMENT_3': 'Ffl',
                    'EMAIL': 'Chr',
                    'FAX': 'Chr',
                    'FILE': 'Ffl',
                    'FLAG': 'Img',
                    'IMAGE': 'Img',
                    'IMAGE_SMALL': 'Img',
                    'INN': 'Chr',
                    'KEYWORD': 'Str',
                    'KPP': 'Chr',
                    'MEASUREMENT_UNIT': {'type': 'Chr', 'slots': ['kg', 'piece']},
                    'MAP_POSITION': 'Chr',
                    'NAME': 'Chr',
                    'NAME_FULL': 'Chr',
                    'NAME_DIRECTOR': 'Chr',
                    'NAME_BUX': 'Chr',
                    'OKATO': 'Chr',
                    'OKVED': 'Chr',
                    'OKPO': 'Chr',
                    'ORDER_DAYS': 'Str',
                    'ORDER_HISTORY': 'Str',
                    'POSITION': 'Chr',
                    'SITE_NAME': 'Chr',
                    'SKU': 'Chr',
                    'SLOGAN': 'Chr',
                    'SLUG': 'Chr',
                    'TELEPHONE_NUMBER': 'Chr',
                    'TPP': 'Chr',
                    'YOUTUBE_CODE': 'Chr'}

    for attribute, type in attributes.items():
        if isinstance(type, dict):
            dictr, created = Dictionary.objects.get_or_create(title=attribute)
            Attribute.objects.get_or_create(title=attribute, type=type['type'], dict=dictr)
            for slot in type['slots']:
                Slot.objects.get_or_create(title=slot, dict=dictr)
        else:
            Attribute.objects.get_or_create(title=attribute, type=type)

    #Create dictionary of countries
    crt_usr = User.objects.get(pk=1)
    cntr, res = Country.objects.get_or_create(title='Azerbaydjan', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Азербайджан'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Armeniya', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Армения'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Belarus', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Беларусь'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Jordjiya', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Грузия'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Israel', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Израиль'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Kazakhstan', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Казахстан'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Kyrgiziya', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Киргизия'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Latviya', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Латвия'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Litva', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Литва'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Moldova', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Молдова'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Russia', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Россия'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Tadjikistan', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Таджикистан'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Turkmeniya', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Туркмения'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Uzbekistan', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Узбекистан'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Ukraine', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Украина'}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Estoniya', create_user = crt_usr)
    if res:
        attr = {'NAME': 'Эстония'}
        cntr.setAttributeValue(attr, crt_usr)

post_syncdb.connect(databaseInitialization, sender=appl.models)