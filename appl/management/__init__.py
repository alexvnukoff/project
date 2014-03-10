__author__ = 'Root'
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_syncdb
from django.contrib.auth.models import Group, Permission
import appl.models
from appl.models import SystemMessages, Country
from core.models import State, Attribute, Value, Slot, Dictionary, User, AttrTemplate

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
                    'ACCOUNTANT': 'Chr',
                    'BANK_ACCOUNT': 'Chr',
                    'BANK_DETAILS': 'Str',
                    'BIRTHDAY': 'Dat',
                    'BANK_NAME': 'Chr',
                    'BUSINESS_PLAN': 'Str',
                    'CELLULAR': 'Chr',
                    'COST': 'Flo',
                    'CITY': 'Chr',
                    'COUPON_DISCOUNT': 'Flo',
                    'CURRENCY': {'type': 'Chr', 'slots': ['USD', 'EUR', 'RUB']},
                    'DETAIL_TEXT': 'Str',
                    'DIRECTOR': 'Chr',
                    'DISCOUNT': 'Flo',
                    'DOCUMENT_1': 'Ffl',
                    'DOCUMENT_2': 'Ffl',
                    'DOCUMENT_3': 'Ffl',

                    'END_EVENT_DATE': 'Dat',

                    'EMAIL': 'Eml',
                    'FAX': 'Chr',
                    'FILE': 'Ffl',
                    'FLAG': 'Img',
                    'GALLERY_TOPIC': 'Chr',
                    'HEAD_PIC': 'Img',
                    'ICQ': 'Chr',
                    'IMAGE': 'Img',
                    'IMAGE_SMALL': 'Img',
                    'INN': 'Chr',
                    'KEYWORD': 'Str',
                    'KPP': 'Chr',
                    'MEASUREMENT_UNIT': {'type': 'Chr', 'slots': ['kg', 'piece']},
                    'MAP_POSITION': 'Chr',
                    'MOBILE_NUMBER': 'Chr',
                    'NAME': 'Chr',
                    'NAME_FULL': 'Chr',
                    'NAME_DIRECTOR': 'Chr',
                    'NAME_BUX': 'Chr',
                    'OKATO': 'Chr',
                    'OKVED': 'Chr',
                    'OKPO': 'Chr',
                    'PERSONAL_FAX': 'Chr',
                    'PERSONAL_PHONE': 'Chr',
                    'PERSONAL_STATUS': {'type': 'Chr', 'slots': ['Individual', 'Businessman']},
                    'PERSONAL_WWW': 'Chr',
                    'POSITION': 'Chr',
                    'PROFESSION': 'Chr',
                    'ROUTE_DESCRIPTION': 'Str',
                    'PRODUCT_NAME': 'Chr',
                    'REALESE_DATE': 'Dat',
                    'SEX': {'type': 'Chr', 'slots': ['Male', 'Female']},
                    'SITE_NAME': 'Chr',
                    'SMALL_IMAGE': 'Img',
                    'SKYPE': 'Chr',
                    'SKU': 'Chr',
                    'SLOGAN': 'Chr',
                    'SLUG': 'Chr',
                    'START_EVENT_DATE': 'Dat',

                    'TELEPHONE_NUMBER': 'Chr',
                    'TPP': 'Chr',
                    'YOUTUBE_CODE': 'Chr',
                    'USER_MIDDLE_NAME': 'Chr',
                    'USER_LAST_NAME': 'Chr',
                    'USER_FIRST_NAME': 'Chr'}

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
        attr = {'NAME': {'title': 'Azerbaydjan', 'title_ru': 'Азербайджан'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Armenia', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Armenia', 'title_ru': 'Армения'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Belarus', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Belarus', 'title_ru': 'Беларусь'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Georgia', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Georgia', 'title_ru': 'Грузия'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Israel', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Israel', 'title_ru': 'Израиль'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Kazakhstan', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Kazakhstan', 'title_ru': 'Казахстан'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Kyrgyzstan', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Kyrgyzstan', 'title_ru': 'Киргизия'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Latvia', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Latvia', 'title_ru': 'Латвия'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Lithuania', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Lithuania', 'title_ru': 'Литва'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Moldova', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Moldova', 'title_ru': 'Молдова'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Russia', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Russia', 'title_ru': 'Россия'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Tajikistan', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Tajikistan', 'title_ru': 'Таджикистан'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Turkmenistan', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Turkmenistan', 'title_ru': 'Туркмения'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Uzbekistan', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Uzbekistan', 'title_ru': 'Узбекистан'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Ukraine', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Ukraine', 'title_ru': 'Украина'}}
        cntr.setAttributeValue(attr, crt_usr)

    cntr, res = Country.objects.get_or_create(title='Estonia', create_user = crt_usr)
    if res:
        attr = {'NAME': {'title': 'Estonia', 'title_ru': 'Эстония'}}
        cntr.setAttributeValue(attr, crt_usr)

    content_type = {'News': {'NAME': True, 'IMAGE': True, 'DETAIL_TEXT': True, 'YOUTUBE_CODE': False},

                    'BusinessProposal': {'NAME': True, 'DETAIL_TEXT': True, 'KEYWORD': False, 'DOCUMENT_1': False,
                                         'DOCUMENT_2': False, 'DOCUMENT_3': False},

                    'Comment': {'DETAIL_TEXT': True},

                    'Company': {'NAME': True, 'IMAGE': False, 'ADDRESS': False, 'SITE_NAME': False,
                                'TELEPHONE_NUMBER': True, 'FAX': False, 'INN': True, 'DETAIL_TEXT': True,
                                'SLOGAN': False, 'EMAIL': True, 'KEYWORD': False, 'DIRECTOR': False, 'KPP': False,
                                'OKPO': False, 'OKATO': False, 'OKVED': False, 'ACCOUNTANT': False,
                                'ACCOUNT_NUMBER': False, 'BANK_DETAILS': False, 'ANONS': True, 'POSITION': False},

                    'Tpp': {'NAME': True, 'IMAGE': False, 'ADDRESS': False, 'SITE_NAME': False,
                            'TELEPHONE_NUMBER': True, 'FAX': False, 'INN': True, 'DETAIL_TEXT': True,
                            'FAG': False, 'EMAIL': True, 'KEYWORD': False, 'DIRECTOR': False, 'KPP': False,
                            'OKPO': False, 'OKATO': False, 'OKVED': False, 'ACCOUNTANT': False,
                            'ACCOUNT_NUMBER': False, 'BANK_DETAILS': False, 'ANONS': True, 'POSITION': False},

                    'Country': {'NAME': True, 'FLAG': False},

                    'Exhibition': {'NAME': True, 'CITY': True, 'START_EVENT_DATE': True, 'END_EVENT_DATE': True,
                                   'KEYWORD': False, 'DOCUMENT_1': False, 'DOCUMENT_2': False, 'DOCUMENT_3': False,
                                   'ROUTE_DESCRIPTION': False, 'POSITION': False},

                    'InnovationProject': {'NAME': True, 'PRODUCT_NAME': True, 'COST': True, 'TARGET_AUDIENCE': False,
                                          'REALESE_DATE': True, 'SITE_NAME': False, 'KEYWORD': False,
                                          'DETAIL_TEXT': False, 'BUSINESS_PLAN': False, 'DOCUMENT_1': False,
                                          'CURRENCY': True},

                    'Product': {'NAME': True, 'IMAGE': True, 'COST': True, 'CURRENCY': True, 'DETAIL_TEXT': False,
                                'COUPON_DISCOUNT': False, 'DISCOUNT': False, 'MEASUREMENT_UNIT': True, 'ANONS': False,
                                'DOCUMENT_1': False, 'DOCUMENT_2': False, 'DOCUMENT_3': False, 'KEYWORD': False,
                                'SMALL_IMAGE': False, 'SKU': False},

                    'Tender': {'NAME': True, 'COST': True, 'CURRENCY': True, 'START_EVENT_DATE': True,
                               'END_EVENT_DATE': True, 'DETAIL_TEXT': False,  'DOCUMENT_1': False, 'DOCUMENT_2': False,
                               'DOCUMENT_3': False, 'KEYWORD': False},

                    'TppTV': {'NAME': True, 'DETAIL_TEXT': True, 'IMAGE': False, 'YOUTUBE_CODE': True}


    }

    for type, attributes in content_type.items():
        object_id = ContentType.objects.get(model=str(type).lower())
        for name, required in attributes.items():
            try:
                attr = Attribute.objects.get(title=name)
                attribute, created = AttrTemplate.objects.get_or_create(classId=object_id, attrId=attr, required=bool(required))
            except:
                pass

post_syncdb.connect(databaseInitialization, sender=appl.models)