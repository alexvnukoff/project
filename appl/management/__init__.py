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


    attributes = {
        'ADDRESS': {'type': 'Chr', 'multilingual': True},
        'ADDRESS_YURID': {'type': 'Chr', 'multilingual': True},
        'ADDRESS_FACT': {'type': 'Chr', 'multilingual': True},
        'ADDRESS_COUNTRY': {'type': 'Chr', 'multilingual': True},
        'ADDRESS_CITY': {'type': 'Chr', 'multilingual': True},
        'ADDRESS_ZIP': {'type': 'Chr', 'multilingual': True},
        'AUTHOR_NAME': {'type': 'Chr', 'multilingual': True},
        'ANONS': {'type': 'Str', 'multilingual': True},
        'ACCOUNTANT': {'type': 'Chr', 'multilingual': True},
        'ADDITIONAL_INFORMATION': {'type': 'Str', 'multilingual': True},
        'ADDITIONAL_SKILL': {'type': 'Str', 'multilingual': True},
        'ADDITIONAL_STUDY': {'type': 'Str', 'multilingual': True},
        'ACCOUNT_NUMBER': {'type': 'Chr', 'multilingual': True},
        'ATTACHMENT': {'type': 'Ffl', 'multilingual': False},
        'BANK_ACCOUNT': {'type': 'Chr', 'multilingual': True},
        'BANK_DETAILS': {'type': 'Str', 'multilingual': True},
        'BIRTHDAY': {'type': 'Dat', 'multilingual': True},
        'BANK_NAME': {'type': 'Chr', 'multilingual': True},
        'BUSINESS_PLAN': {'type': 'Str', 'multilingual': True},
        'CELLULAR': {'type': 'Chr', 'multilingual': False},
        'COST': {'type': 'Flo', 'multilingual': False},
        'COMPUTER_SKILL': {'type': 'Chr', 'multilingual': True},
        'CITY': {'type': 'Chr', 'multilingual': True},
        'COMPANY_EXP_1': {'type': 'Chr', 'multilingual': True},
        'COMPANY_EXP_2': {'type': 'Chr', 'multilingual': True},
        'COMPANY_EXP_3': {'type': 'Chr', 'multilingual': True},
        'COUPON_DISCOUNT': {'type': 'Flo', 'multilingual': False},
        'COUNTRY_FLAG': {'type': 'Chr', 'multilingual': False},
        'CURRENCY': {'type': 'Chr', 'slots': ['USD', 'EUR', 'RUB']},
        'DETAIL_TEXT': {'type': 'Str', 'multilingual': True},
        'DIRECTOR': {'type': 'Chr', 'multilingual': True},
        'DISCOUNT': {'type': 'Flo', 'multilingual': False},
        'DOCUMENT_1': {'type': 'Ffl', 'multilingual': False},
        'DOCUMENT_2': {'type': 'Ffl', 'multilingual': False},
        'DOCUMENT_3': {'type': 'Ffl', 'multilingual': False},

        'END_EVENT_DATE': {'type': 'Dat', 'multilingual': False},
        'END_DATE_EXP_1': {'type': 'Dat', 'multilingual': False},
        'END_DATE_EXP_2': {'type': 'Dat', 'multilingual': False},
        'END_DATE_EXP_3': {'type': 'Dat', 'multilingual': False},

        'EMAIL': {'type': 'Eml', 'multilingual': False},
        'FACULTY': {'type': 'Chr', 'multilingual': True},
        'FAX': {'type': 'Chr', 'multilingual': False},
        'FILE': {'type': 'Ffl', 'multilingual': False},
        'FLAG': {'type': 'Img', 'multilingual': False},
        'GALLERY_TOPIC': {'type': 'Chr', 'multilingual': False},
        'HEAD_PIC': {'type': 'Img', 'multilingual': False},
        'HEIGHT': {'type': 'Int', 'multilingual': False},
        'ICQ': {'type': 'Int', 'multilingual': False},
        'IMAGE': {'type': 'Img', 'multilingual': False},
        'IMAGE_SMALL': {'type': 'Img', 'multilingual': False},
        'INSTITUTION': {'type': 'Chr', 'multilingual': True},
        'IS_ANONYMOUS_VACANCY': {'type': 'Chr', 'multilingual': False},
        'INN': {'type': 'Chr', 'multilingual': False},
        'KEYWORD': {'type': 'Str', 'multilingual': True},
        'KPP': {'type': 'Chr', 'multilingual': False},
        'LANGUAGE_SKILL': {'type': 'Chr', 'multilingual': True},
        'MEASUREMENT_UNIT': {'type': 'Chr', 'slots': ['kg', 'piece']},
        'MAP_POSITION': {'type': 'Chr', 'multilingual': False},
        'MARITAL_STATUS': {'type': 'Chr', 'slots': ['Single', 'Married']},
        'MOBILE_NUMBER': {'type': 'Chr', 'multilingual': False},
        'NAME': {'type': 'Chr', 'multilingual': True},
        'NAME_FULL': {'type': 'Chr', 'multilingual': True},
        'NAME_DIRECTOR': {'type': 'Chr', 'multilingual': True},
        'NAME_BUX': {'type': 'Chr', 'multilingual': True},
        'NATIONALITY': {'type': 'Chr', 'multilingual': True},
        'OKATO': {'type': 'Chr', 'multilingual': False},
        'OKVED': {'type': 'Chr', 'multilingual': False},
        'OKPO': {'type': 'Chr', 'multilingual': False},
        'ORDER_DAYS': {'type': 'Int', 'multilingual': False},
        'ORDER_HISTORY': {'type': 'Str', 'multilingual': False},
        'PERSONAL_FAX': {'type': 'Chr', 'multilingual': False},
        'PERSONAL_PHONE': {'type': 'Chr', 'multilingual': False},
        'PERSONAL_STATUS': {'type': 'Chr', 'slots': ['Individual', 'Businessman']},
        'PERSONAL_WWW': {'type': 'Chr', 'multilingual': False},
        'POSITION': {'type': 'Chr', 'multilingual': False},
        'POSITION_NAME': {'type': 'Chr', 'multilingual': True},
        'POSITION_EXP_1': {'type': 'Chr', 'multilingual': True},
        'POSITION_EXP_2': {'type': 'Chr', 'multilingual': True},
        'POSITION_EXP_3': {'type': 'Chr', 'multilingual': True},
        'PROFESSION': {'type': 'Chr', 'multilingual': True},
        'REQUIREMENTS': {'type': 'Str', 'multilingual': True},
        'ROUTE_DESCRIPTION': {'type': 'Str', 'multilingual': True},
        'PRODUCT_NAME': {'type': 'Chr', 'multilingual': True},
        'RELEASE_DATE': {'type': 'Dat', 'multilingual': False},
        'SALARY': {'type': 'Chr', 'multilingual': False},
        'SEX': {'type': 'Chr', 'slots': ['Male', 'Female']},
        'SHIPPING_NAME': {'type': 'Chr', 'multilingual': True},
        'SITE_NAME': {'type': 'Str', 'multilingual': True},
        'SITE_LOGO': {'type': 'Img', 'multilingual': False},
        'SITE_SLOGAN': {'type': 'Chr', 'multilingual': True},
        'SMALL_IMAGE': {'type': 'Img', 'multilingual': False},
        'SKYPE': {'type': 'Chr', 'multilingual': False},
        'SKU': {'type': 'Chr', 'multilingual': False},
        'SLOGAN': {'type': 'Chr', 'multilingual': True},
        'SLUG': {'type': 'Chr', 'multilingual': True},
        'START_EVENT_DATE': {'type': 'Dat', 'multilingual': False},
        'START_DATE_EXP_1': {'type': 'Dat', 'multilingual': False},
        'START_DATE_EXP_2': {'type': 'Dat', 'multilingual': False},
        'START_DATE_EXP_3': {'type': 'Dat', 'multilingual': False},
        'STUDY_FORM': {'type': 'Chr', 'slots': ['Full-time', 'Extramural']},
        'STUDY_END_DATE': {'type': 'Dat', 'multilingual': False},
        'STUDY_START_DATE': {'type': 'Dat', 'multilingual': False},
        'TARGET_AUDIENCE': {'type': 'Chr', 'multilingual': True},
        'TELEPHONE_NUMBER': {'type': 'Chr', 'multilingual': False},
        'TEMPLATE_IMAGE_FOLDER': {'type': 'Chr', 'multilingual': False},
        "TEMPLATE": {'type': 'Chr', 'multilingual': False},
        'TERMS': {'type': 'Str', 'multilingual': True},
        'TPP': {'type': 'Chr', 'multilingual': True},
        'TYPE_OF_EMPLOYMENT': {'type': 'Chr', 'slots': ['Full-time', 'Partial', 'Shifts', 'For students']},
        'YOUTUBE_CODE': {'type': 'Chr', 'multilingual': False},
        'USER_MIDDLE_NAME': {'type': 'Chr', 'multilingual': True},
        'USER_LAST_NAME': {'type': 'Chr', 'multilingual': True},
        'USER_FIRST_NAME': {'type': 'Chr', 'multilingual': True},
        'WIDTH': {'type': 'Int', 'multilingual': False},
        'QUANTITY': {'type': 'Int', 'multilingual': False},
    }

    for attribute, properties in attributes.items():

        slots = properties.get('slots', False)

        if slots:
            dictr, created = Dictionary.objects.get_or_create(title=attribute)

            for slot in slots:
                Slot.objects.get_or_create(title=slot, dict=dictr)

        attrType = properties['type']
        multilingual = properties.get('multilingual', True)

        Attribute.objects.get_or_create(title=attribute, type=attrType, multilingual=multilingual)

    #Create dictionary of countries

    content_type = {
        'News': {
            'NAME': True,
            'IMAGE': True,
            'DETAIL_TEXT': True,
            'YOUTUBE_CODE': False,
            'ANONS': False
        },

        'BusinessProposal': {
            'NAME': True,
            'DETAIL_TEXT': True,
            'KEYWORD': False,
            'DOCUMENT_1': False,
            'DOCUMENT_2': False,
            'DOCUMENT_3': False
        },

        'Comment': {
            'DETAIL_TEXT': True
        },

        'Company': {
            'NAME': True,
            'IMAGE': False,
            'ADDRESS': False,
            'SITE_NAME': False,
            'TELEPHONE_NUMBER': True,
            'FAX': False,
            'INN': True,
            'DETAIL_TEXT': True,
            'SLOGAN': False,
            'EMAIL': True,
            'KEYWORD': False,
            'DIRECTOR': False,
            'KPP': False,
            'OKPO': False,
            'OKATO': False,
            'OKVED': False,
            'ACCOUNTANT': False,
            'ACCOUNT_NUMBER': False,
            'BANK_DETAILS': False,
            'ANONS': True,
            'POSITION': False
        },

        'Tpp': {
            'NAME': True,
            'IMAGE': False,
            'ADDRESS': False,
            'SITE_NAME': False,
            'TELEPHONE_NUMBER': True,
            'FAX': False,
            'INN': True,
            'DETAIL_TEXT': True,
            'FLAG': False,
            'EMAIL': True,
            'KEYWORD': False,
            'DIRECTOR': False,
            'KPP': False,
            'OKPO': False,
            'OKATO': False,
            'OKVED': False,
            'ACCOUNTANT': False,
            'ACCOUNT_NUMBER': False,
            'BANK_DETAILS': False,
            'ANONS': True,
            'POSITION': False,
            'SLOGAN': False
        },

        'Country': {
            'NAME': True,
            'FLAG': False,
            'COUNTRY_FLAG': False
        },

        'Exhibition': {
            'NAME': True,
            'CITY': True,
            'START_EVENT_DATE': True,
            'END_EVENT_DATE': True,
            'KEYWORD': False,
            'DOCUMENT_1': False,
            'DOCUMENT_2': False,
            'DOCUMENT_3': False,
            'ROUTE_DESCRIPTION': False,
            'POSITION': False,
            'DETAIL_TEXT': False
        },

        'InnovationProject': {
            'NAME': True,
            'PRODUCT_NAME': True,
            'COST': True,
            'TARGET_AUDIENCE': False,
            'RELEASE_DATE': True,
            'SITE_NAME': False,
            'KEYWORD': False,
            'DETAIL_TEXT': False,
            'BUSINESS_PLAN': False,
            'DOCUMENT_1': False,
            'CURRENCY': True
        },

        'Product': {
            'NAME': True,
            'IMAGE': True,
            'COST': True,
            'CURRENCY': True,
            'DETAIL_TEXT': False,
            'COUPON_DISCOUNT': False,
            'DISCOUNT': False,
            'MEASUREMENT_UNIT': True,
            'ANONS': False,
            'DOCUMENT_1': False,
            'DOCUMENT_2': False,
            'DOCUMENT_3': False,
            'KEYWORD': False,
            'SMALL_IMAGE': False,
            'SKU': False
        },

        'Tender': {
            'NAME': True,
            'COST': True,
            'CURRENCY': True,
            'START_EVENT_DATE': True,
            'END_EVENT_DATE': True,
            'DETAIL_TEXT': False,
            'DOCUMENT_1': False,
            'DOCUMENT_2': False,
            'DOCUMENT_3': False,
            'KEYWORD': False
        },

        'TppTV': {
            'NAME': True,
            'DETAIL_TEXT': False,
            'IMAGE': False,
            'YOUTUBE_CODE': True
        },

        'Resume': {
            'NAME': True,
            'BIRTHDAY': True,
            'MARITAL_STATUS': False,
            'NATIONALITY':False,
            'TELEPHONE_NUMBER': True,
            'ADDRESS': True,
            'FACULTY': False,
            'PROFESSION': False,
            'STUDY_START_DATE': False,
            'STUDY_END_DATE': False,
            'STUDY_FORM': False,
            'COMPANY_EXP_1': False,
            'COMPANY_EXP_2': False,
            'COMPANY_EXP_3': False,
            'POSITION_EXP_1': False,
            'POSITION_EXP_2': False,
            'POSITION_EXP_3': False,
            'START_DATE_EXP_1': False,
            'START_DATE_EXP_2': False,
            'START_DATE_EXP_3': False,
            'END_DATE_EXP_1': False,
            'END_DATE_EXP_2': False,
            'END_DATE_EXP_3': False,
            'ADDITIONAL_STUDY': False,
            'LANGUAGE_SKILL': False,
            'COMPUTER_SKILL': False,
            'ADDITIONAL_SKILL': False,
            'SALARY': True,
            'ADDITIONAL_INFORMATION': False,
            'INSTITUTION': False
        },

        'Requirement': {
            'NAME': True,
            'CITY': True,
            'TYPE_OF_EMPLOYMENT': True,
            'KEYWORD': False,
            'DETAIL_TEXT': True,
            'REQUIREMENTS': True,
            'TERMS': True,
            'IS_ANONYMOUS_VACANCY': False
        },

        'Messages': {
            'DETAIL_TEXT': True,
            'ATTACHMENT': False
        },

        'UserSites': {
            'NAME': True,
            'SITE_SLOGAN': False,
            'SITE_LOGO': True,
            'DETAIL_TEXT': True,
            'TEMPLATE': False
        },

        'staticPages': {
            'NAME': True,
            'DETAIL_TEXT': True
        },

        'AdvOrder': {
            'COST': False,
            'IMAGE': False,
            'SITE_NAME': False,
            'START_EVENT_DATE': False,
            'END_EVENT_DATE': False,
            'NAME': False,
            'ORDER_HISTORY': False,
            'ORDER_DAYS': False
        },

        'AdvTop': {
            'COST': True,
            'START_EVENT_DATE': True,
            'END_EVENT_DATE': True,

        },

        'AdvBanner': {
            'COST': True,
            'START_EVENT_DATE': True,
            'END_EVENT_DATE': True,
            'NAME': False,
            'SITE_NAME': True,
            'IMAGE': True
        },

        'AdvBannerType': {
            'NAME': True,
            'WIDTH': True,
            'HEIGHT': True
        },

        'Greeting': {
            'IMAGE': True,
            'TPP': True,
            'AUTHOR_NAME': True,
            'POSITION': True,
            'NAME': True,
            'DETAIL_TEXT': True
        }
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
