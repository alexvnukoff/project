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

    gr4, created = Group.objects.get_or_create(name='TPP Creator')
    if created:
        gr4.permissions.add(add_tpp, read_tpp)

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
                    'ADDITIONAL_INFORMATION': 'Str',
                    'ADDITIONAL_SKILL': 'Str',
                    'ADDITIONAL_STUDY': 'Str',
                    'ACCOUNT_NUMBER': 'Chr',
                    'BANK_ACCOUNT': 'Chr',
                    'BANK_DETAILS': 'Str',
                    'BIRTHDAY': 'Dat',
                    'BANK_NAME': 'Chr',
                    'BUSINESS_PLAN': 'Str',
                    'CELLULAR': 'Chr',
                    'COST': 'Flo',
                    'COMPUTER_SKILL': 'Chr',
                    'CITY': 'Chr',
                    'COMPANY_EXP_1' : 'Chr',
                    'COMPANY_EXP_2' : 'Chr',
                    'COMPANY_EXP_3' : 'Chr',
                    'COUPON_DISCOUNT': 'Flo',
                    'COUNTRY_FLAG': "Chr",
                    'CURRENCY': {'type': 'Chr', 'slots': ['USD', 'EUR', 'RUB']},
                    'DETAIL_TEXT': 'Str',
                    'DIRECTOR': 'Chr',
                    'DISCOUNT': 'Flo',
                    'DOCUMENT_1': 'Ffl',
                    'DOCUMENT_2': 'Ffl',
                    'DOCUMENT_3': 'Ffl',

                    'END_EVENT_DATE': 'Dat',
                    'END_DATE_EXP_1': 'Dat',
                    'END_DATE_EXP_2': 'Dat',
                    'END_DATE_EXP_3': 'Dat',

                    'EMAIL': 'Eml',
                    'FACULTY': 'Chr',
                    'FAX': 'Chr',
                    'FILE': 'Ffl',
                    'FLAG': 'Img',
                    'GALLERY_TOPIC': 'Chr',
                    'HEAD_PIC': 'Img',
                    'ICQ': 'Chr',
                    'IMAGE': 'Img',
                    'IMAGE_SMALL': 'Img',
                    'INSTITUTION': 'Chr',
                    'IS_ANONYMOUS_VACANCY': 'Chr',
                    'INN': 'Chr',
                    'KEYWORD': 'Str',
                    'KPP': 'Chr',
                    'LANGUAGE_SKILL': 'Chr',
                    'MEASUREMENT_UNIT': {'type': 'Chr', 'slots': ['kg', 'piece']},
                    'MAP_POSITION': 'Chr',
                    'MARITAL_STATUS': {'type': 'Chr', 'slots': ['Single', 'Married']},
                    'MOBILE_NUMBER': 'Chr',
                    'NAME': 'Chr',
                    'NAME_FULL': 'Chr',
                    'NAME_DIRECTOR': 'Chr',
                    'NAME_BUX': 'Chr',
                    'NATIONALITY': 'Chr',
                    'OKATO': 'Chr',
                    'OKVED': 'Chr',
                    'OKPO': 'Chr',
                    'PERSONAL_FAX': 'Chr',
                    'PERSONAL_PHONE': 'Chr',
                    'PERSONAL_STATUS': {'type': 'Chr', 'slots': ['Individual', 'Businessman']},
                    'PERSONAL_WWW': 'Chr',
                    'POSITION': 'Chr',
                    'POSITION_EXP_1': 'Chr',
                    'POSITION_EXP_2': 'Chr',
                    'POSITION_EXP_3': 'Chr',
                    'PROFESSION': 'Chr',
                    'REQUIREMENTS': 'Str',
                    'ROUTE_DESCRIPTION': 'Str',
                    'PRODUCT_NAME': 'Chr',
                    'RELEASE_DATE': 'Dat',
                    'SALARY': 'Chr',
                    'SEX': {'type': 'Chr', 'slots': ['Male', 'Female']},
                    'SITE_NAME': 'Chr',
                    'SITE_LOGO': 'Img',
                    'SITE_SLOGAN': 'Chr',
                    'SMALL_IMAGE': 'Img',
                    'SKYPE': 'Chr',
                    'SKU': 'Chr',
                    'SLOGAN': 'Chr',
                    'SLUG': 'Chr',
                    'START_EVENT_DATE': 'Dat',
                    'START_DATE_EXP_1': 'Dat',
                    'START_DATE_EXP_2': 'Dat',
                    'START_DATE_EXP_3': 'Dat',
                    'STUDY_FORM': {'type': 'Chr', 'slots': ['Full-time', 'Extramural']},
                    'STUDY_END_DATE': 'Dat',
                    'STUDY_START_DATE': 'Dat',
                    'TARGET_AUDIENCE': 'Chr',
                    'TELEPHONE_NUMBER': 'Chr',
                    'TEMPLATE_IMAGE_FOLDER': 'Chr',
                    "TEMPLATE": 'Chr',
                    'TERMS': 'Str',
                    'TPP': 'Chr',
                    'TYPE_OF_EMPLOYMENT': 'Str',
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











    content_type = {'News': {'NAME': True, 'IMAGE': True, 'DETAIL_TEXT': True, 'YOUTUBE_CODE': False, 'ANONS': False},

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

                    'Country': {'NAME': True, 'FLAG': False, 'COUNTRY_FLAG': False},

                    'Exhibition': {'NAME': True, 'CITY': True, 'START_EVENT_DATE': True, 'END_EVENT_DATE': True,
                                   'KEYWORD': False, 'DOCUMENT_1': False, 'DOCUMENT_2': False, 'DOCUMENT_3': False,
                                   'ROUTE_DESCRIPTION': False, 'POSITION': False},

                    'InnovationProject': {'NAME': True, 'PRODUCT_NAME': True, 'COST': True, 'TARGET_AUDIENCE': False,
                                          'RELEASE_DATE': True, 'SITE_NAME': False, 'KEYWORD': False,
                                          'DETAIL_TEXT': False, 'BUSINESS_PLAN': False, 'DOCUMENT_1': False,
                                          'CURRENCY': True},

                    'Product': {'NAME': True, 'IMAGE': True, 'COST': True, 'CURRENCY': True, 'DETAIL_TEXT': False,
                                'COUPON_DISCOUNT': False, 'DISCOUNT': False, 'MEASUREMENT_UNIT': True, 'ANONS': False,
                                'DOCUMENT_1': False, 'DOCUMENT_2': False, 'DOCUMENT_3': False, 'KEYWORD': False,
                                'SMALL_IMAGE': False, 'SKU': False},

                    'Tender': {'NAME': True, 'COST': True, 'CURRENCY': True, 'START_EVENT_DATE': True,
                               'END_EVENT_DATE': True, 'DETAIL_TEXT': False,  'DOCUMENT_1': False, 'DOCUMENT_2': False,
                               'DOCUMENT_3': False, 'KEYWORD': False},

                    'TppTV': {'NAME': True, 'DETAIL_TEXT': True, 'IMAGE': False, 'YOUTUBE_CODE': True},

                    'Resume': {'NAME': True, 'BIRTHDAY': True, 'MARITAL_STATUS': False, 'NATIONALITY':False,
                               'TELEPHONE_NUMBER': True, 'ADDRESS': True, 'FACULTY': False, 'PROFESSION': False,
                               'STUDY_START_DATE': False, 'STUDY_END_DATE': False, 'STUDY_FORM': False,
                               'COMPANY_EXP_1': False, 'COMPANY_EXP_2': False,'COMPANY_EXP_3': False,
                               'POSITION_EXP_1': False, 'POSITION_EXP_2': False, 'POSITION_EXP_3': False,
                               'START_DATE_EXP_1': False, 'START_DATE_EXP_2': False, 'START_DATE_EXP_3': False,
                               'END_DATE_EXP_1': False, 'END_DATE_EXP_2': False, 'END_DATE_EXP_3': False,
                               'ADDITIONAL_STUDY': False, 'LANGUAGE_SKILL': False, 'COMPUTER_SKILL': False,
                               'ADDITIONAL_SKILL': False, 'SALARY': True, 'ADDITIONAL_INFORMATION': False,
                               'INSTITUTION': False },

                    'Requirement': {'NAME': True, 'CITY': True, 'TYPE_OF_EMPLOYMENT': True, 'KEYWORD': False,
                                    'DETAIL_TEXT': True, 'REQUIREMENTS': True, 'TERMS': True,
                                    'IS_ANONYMOUS_VACANCY': False}


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