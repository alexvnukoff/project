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
                    'ACCOUNT_NUMBER': 'Chr',
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
                    'RELEASE_DATE': 'Dat',
                    'SEX': {'type': 'Chr', 'slots': ['Male', 'Female']},
                    'SITE_NAME': 'Chr',
                    'SMALL_IMAGE': 'Img',
                    'SKYPE': 'Chr',
                    'SKU': 'Chr',
                    'SLOGAN': 'Chr',
                    'SLUG': 'Chr',
                    'START_EVENT_DATE': 'Dat',
                    'TARGET_AUDIENCE': 'Chr',
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
    countries = {'Azerbaydjan': {'NAME': {'title': 'Azerbaydjan', 'title_ru': 'Азербайджан'}, 'COUNTRY_FLAG': "sprite-flag_azerbaijan"},
                 'Armenia': {'NAME': {'title': 'Armenia', 'title_ru': 'Армения'}, 'COUNTRY_FLAG': "sprite-flag_armenia"},
                 'Belarus': {'NAME': {'title': 'Belarus', 'title_ru': 'Беларусь'}, 'COUNTRY_FLAG': "sprite-flag_belarus"},
                 'Georgia': {'NAME': {'title': 'Georgia', 'title_ru': 'Грузия'}, 'COUNTRY_FLAG': "sprite-flag_georgia"},
                 'Israel': {'NAME': {'title': 'Israel', 'title_ru': 'Израиль'}, 'COUNTRY_FLAG': "sprite-flag_israel"},
                 'Kazakhstan': {'NAME': {'title': 'Kazakhstan', 'title_ru': 'Казахстан'}, 'COUNTRY_FLAG': "sprite-flag_kazakhstan"},
                 'Kyrgyzstan': {'NAME': {'title': 'Kyrgyzstan', 'title_ru': 'Киргизия'}, 'COUNTRY_FLAG': "sprite-flag_kyrgyzstan"},
                 'Latvia': {'NAME': {'title': 'Latvia', 'title_ru': 'Латвия'}, 'COUNTRY_FLAG': "sprite-flag_lithuania"},
                 'Lithuania': {'NAME': {'title': 'Lithuania', 'title_ru': 'Литва'}, 'COUNTRY_FLAG': "sprite-flag_lithuania"},
                 'Moldova': {'NAME': {'title': 'Moldova', 'title_ru': 'Молдова'}, 'COUNTRY_FLAG': "sprite-flag_moldova"},
                 'Russia': {'NAME': {'title': 'Russia', 'title_ru': 'Россия'}, 'COUNTRY_FLAG': "sprite-flag_russia"},
                 'Tajikistan': {'NAME': {'title': 'Tajikistan', 'title_ru': 'Таджикистан'}, 'COUNTRY_FLAG': "sprite-flag_tajikistan"},
                 'Turkmenistan': {'NAME': {'title': 'Turkmenistan', 'title_ru': 'Туркмения'}, 'COUNTRY_FLAG': "sprite-flag_turkmenistan"},
                 'Uzbekistan': {'NAME': {'title': 'Uzbekistan', 'title_ru': 'Узбекистан'}, 'COUNTRY_FLAG': "sprite-flag_uzbekistan"},
                 'Ukraine': {'NAME': {'title': 'Ukraine', 'title_ru': 'Украина'}, 'COUNTRY_FLAG': "sprite-flag_ukraine"},
                 'Estonia': {'NAME': {'title': 'Estonia', 'title_ru': 'Эстония'}, 'COUNTRY_FLAG': "sprite-flag_estonia"},
                 'Afghanistan': {'NAME': {'title': 'Afghanistan', 'title_ru': 'Афганистан'}, 'COUNTRY_FLAG': "sprite-flag_afghanistan"},
                 'Albania': {'NAME': {'title': 'Albania', 'title_ru': 'Албания'}, 'COUNTRY_FLAG': "sprite-flag_albania"},
                 'Algeria': {'NAME': {'title': 'Algeria', 'title_ru': 'Алжир'}, 'COUNTRY_FLAG': "sprite-flag_algeria"},
                 'Andorra': {'NAME': {'title': 'Andorra', 'title_ru': 'Андорра'}, 'COUNTRY_FLAG': "sprite-flag_andorra"},
                 'Angola': {'NAME': {'title': 'Angola', 'title_ru': 'Ангола'}, 'COUNTRY_FLAG': "sprite-flag_angola"},
                 'Antigua and Barbuda': {'NAME': {'title': 'Antigua and Barbuda', 'title_ru': 'Антигуа и Барбуда'}, 'COUNTRY_FLAG': "sprite-flag_antigua_and_barbuda"},
                 'Argentina': {'NAME': {'title': 'Argentina', 'title_ru': 'Аргентина'}, 'COUNTRY_FLAG': "sprite-flag_argentina"},
                 'Australia': {'NAME': {'title': 'Australia', 'title_ru': 'Австралия'}, 'COUNTRY_FLAG': "sprite-flag_australia"},
                 'Austria': {'NAME': {'title': 'Austria', 'title_ru': 'Австрия'}, 'COUNTRY_FLAG': "sprite-flag_austria"},
                 'Bahamas': {'NAME': {'title': 'Bahamas', 'title_ru': 'Багамские острова'}, 'COUNTRY_FLAG': "sprite-flag_bahamas"},
                 'Bahrain': {'NAME': {'title': 'Bahrain', 'title_ru': 'Бахрейн'}, 'COUNTRY_FLAG': "sprite-flag_bahrain"},
                 'Bangladesh': {'NAME': {'title': 'Bangladesh', 'title_ru': 'Бангладеш'}, 'COUNTRY_FLAG': "sprite-flag_bangladesh"},
                 'Barbados': {'NAME': {'title': 'Barbados', 'title_ru': 'Барбадос'}, 'COUNTRY_FLAG': "sprite-flag_barbados"},
                 'Belgium': {'NAME': {'title': 'Belgium', 'title_ru': 'Бельгия'}, 'COUNTRY_FLAG': "sprite-flag_belgium"},
                 'Belize': {'NAME': {'title': 'Belize', 'title_ru': 'Белиз'}, 'COUNTRY_FLAG': "sprite-flag_belize"},
                 'Benin': {'NAME': {'title': 'Benin', 'title_ru': 'Бенин'}, 'COUNTRY_FLAG': "sprite-flag_benin"},
                 'Bhutan': {'NAME': {'title': 'Bhutan', 'title_ru': 'Бутан'}, 'COUNTRY_FLAG': "sprite-flag_bhutan"},
                 'Bolivia': {'NAME': {'title': 'Bolivia', 'title_ru': 'Боливия'}, 'COUNTRY_FLAG': "sprite-flag_bolivia"},
                 'Bosnia and Herzegovina': {'NAME': {'title': 'Bosnia and Herzegovina', 'title_ru': 'Босния и Герцеговина'}, 'COUNTRY_FLAG': "sprite-flag_bosnia_and_herzegovina"},
                 'Botswana': {'NAME': {'title': 'Botswana', 'title_ru': 'Ботсвана'}, 'COUNTRY_FLAG': "sprite-flag_botswana"},
                 'Brazil': {'NAME': {'title': 'Brazil', 'title_ru': 'Бразилия'}, 'COUNTRY_FLAG': "sprite-flag_brazil"},
                 'Brunei': {'NAME': {'title': 'Brunei', 'title_ru': 'Бруней'}, 'COUNTRY_FLAG': "sprite-flag_brunei"},
                 'Bulgaria': {'NAME': {'title': 'Bulgaria', 'title_ru': 'Болгария'}, 'COUNTRY_FLAG': "sprite-flag_bulgaria"},
                 'Burkina Faso': {'NAME': {'title': 'Burkina Faso', 'title_ru': 'Буркина-Фасо'}, 'COUNTRY_FLAG': "sprite-flag_burkina_faso"},
                 'Burundi': {'NAME': {'title': 'Burundi', 'title_ru': 'Бурунди'}, 'COUNTRY_FLAG': "sprite-flag_burundi"},
                 'Cambodia': {'NAME': {'title': 'Cambodia', 'title_ru': 'Камбоджа'}, 'COUNTRY_FLAG': "sprite-flag_cambodia"},
                 'Cameroon': {'NAME': {'title': 'Cameroon', 'title_ru': 'Камерун'}, 'COUNTRY_FLAG': "sprite-flag_cameroon"},
                 'Canada': {'NAME': {'title': 'Canada', 'title_ru': 'Канада'}, 'COUNTRY_FLAG': "sprite-flag_canada"},
                 'Cape Verde': {'NAME': {'title': 'Cape Verde', 'title_ru': 'Кабо-Верде'}, 'COUNTRY_FLAG': "sprite-flag_cape_verde"},
                 'Central African Republic': {'NAME': {'title': 'Central African Republic', 'title_ru': 'Центрально-Африканская Республика'}, 'COUNTRY_FLAG': "sprite-flag_central_african_republic"},
                 'Chad': {'NAME': {'title': 'Chad', 'title_ru': 'Чад'}, 'COUNTRY_FLAG': "sprite-flag_chad"},
                 'Chile': {'NAME': {'title': 'Chile', 'title_ru': 'Чили'}, 'COUNTRY_FLAG': "sprite-flag_chile"},
                 'China': {'NAME': {'title': 'China', 'title_ru': 'Китай'}, 'COUNTRY_FLAG': "sprite-flag_china"},
                 'Columbia': {'NAME': {'title': 'Columbia', 'title_ru': 'Колумбия'}, 'COUNTRY_FLAG': "sprite-flag_colombia"},
                 'Comoros': {'NAME': {'title': 'Comoros', 'title_ru': 'Коморские острова'}, 'COUNTRY_FLAG': "sprite-flag_comoros"},
                 'Democratic Republic of Congo': {'NAME': {'title': 'Democratic Republic of Congo', 'title_ru': 'Демократическая Республика Конго'}, 'COUNTRY_FLAG': "sprite-flag_congo_democratic_republic"},
                 'Congo Republic': {'NAME': {'title': 'Congo Republic', 'title_ru': 'Республика Конго'}, 'COUNTRY_FLAG': "sprite-flag_congo_republic"},
                 'Cook Island': {'NAME': {'title': 'Cook Island', 'title_ru': 'острова Кука'}, 'COUNTRY_FLAG': "sprite-flag_cook_islands"},
                 'Costa Rica': {'NAME': {'title': 'Costa Rica', 'title_ru': 'Коста-Рика'}, 'COUNTRY_FLAG': "sprite-flag_costa_rica"},
                 "Cote D'ivoire": {'NAME': {'title': "Cote D'ivoire", 'title_ru': 'Берег Слоновой Кости'}, 'COUNTRY_FLAG': "sprite-flag_cote_divoire"},
                 'Croatia': {'NAME': {'title': 'Croatia', 'title_ru': 'Хорватия'}, 'COUNTRY_FLAG': "sprite-flag_croatia"},
                 'Cuba': {'NAME': {'title': 'Cuba', 'title_ru': 'Куба'}, 'COUNTRY_FLAG': "sprite-flag_cuba"},
                 'Cyprus': {'NAME': {'title': 'Cyprus', 'title_ru': 'Кипр'}, 'COUNTRY_FLAG': "sprite-flag_cyprus"},
                 'Czech Republic': {'NAME': {'title': 'Czech Republic', 'title_ru': 'Чешская республика'}, 'COUNTRY_FLAG': "sprite-flag_czech_republic"},
                 'Denmark': {'NAME': {'title': 'Denmark', 'title_ru': 'Дания'}, 'COUNTRY_FLAG': "sprite-flag_denmark"},
                 'Djibouti': {'NAME': {'title': 'Djibouti', 'title_ru': 'Джибути'}, 'COUNTRY_FLAG': "sprite-flag_djibouti"},
                 'Dominica': {'NAME': {'title': 'Dominica', 'title_ru': 'Доминика'}, 'COUNTRY_FLAG': "sprite-flag_dominica"},
                 'Dominican Republic': {'NAME': {'title': 'Dominican Republic', 'title_ru': 'Доминиканская Республика'}, 'COUNTRY_FLAG': "sprite-flag_dominican_republic"},
                 'East Timor': {'NAME': {'title': 'East Timor', 'title_ru': 'Восточный Тимор'}, 'COUNTRY_FLAG': "sprite-flag_east_timor"},
                 'Egypt': {'NAME': {'title': 'Egypt', 'title_ru': 'Египет'}, 'COUNTRY_FLAG': "sprite-flag_egypt"},
                 'El Salvador': {'NAME': {'title': 'El Salvador', 'title_ru': 'Сальвадор'}, 'COUNTRY_FLAG': "sprite-flag_el_salvador"},
                 'Ecuador': {'NAME': {'title': 'Ecuador', 'title_ru': 'Эквадор'}, 'COUNTRY_FLAG': "sprite-flag_equador"},
                 'Equatorial Guinea': {'NAME': {'title': 'Equatorial Guinea', 'title_ru': 'Экваториальная Гвинея'}, 'COUNTRY_FLAG': "sprite-flag_equatorial_guinea"},
                 'Eritrea': {'NAME': {'title': 'Eritrea', 'title_ru': 'Эритрея'}, 'COUNTRY_FLAG': "sprite-flag_eritrea"},
                 'Ethiopia': {'NAME': {'title': 'Ethiopia', 'title_ru': 'Эфиопия'}, 'COUNTRY_FLAG': "sprite-flag_ethiopia"},
                 'Federated State of Micronesia': {'NAME': {'title': 'Federated State of Micronesia', 'title_ru': 'Федеративные Штаты Микронезии'}, 'COUNTRY_FLAG': "sprite-flag_federated_states_of_micronesia"},
                 'Fiji': {'NAME': {'title': 'Fiji', 'title_ru': 'Фиджи'}, 'COUNTRY_FLAG': "sprite-flag_fiji"},
                 'Finland': {'NAME': {'title': 'Finland', 'title_ru': 'Финляндия'}, 'COUNTRY_FLAG': "sprite-flag_finland"},
                 'France': {'NAME': {'title': 'France', 'title_ru': 'Франция'}, 'COUNTRY_FLAG': "sprite-flag_france"},
                 'Gabon': {'NAME': {'title': 'Gabon', 'title_ru': 'Габон'}, 'COUNTRY_FLAG': "sprite-flag_gabon"},
                 'Gambia': {'NAME': {'title': 'Gambia', 'title_ru': 'Гамбия'}, 'COUNTRY_FLAG': "sprite-flag_gambia"},
                 'Germany': {'NAME': {'title': 'Germany', 'title_ru': 'Германия'}, 'COUNTRY_FLAG': "sprite-flag_germany"},
                 'Ghana': {'NAME': {'title': 'Ghana', 'title_ru': 'Гана'}, 'COUNTRY_FLAG': "sprite-flag_ghana"},
                 'Greece': {'NAME': {'title': 'Greece', 'title_ru': 'Греция'}, 'COUNTRY_FLAG': "sprite-flag_greece"},
                 'Grenada': {'NAME': {'title': 'Grenada', 'title_ru': 'Гренада'}, 'COUNTRY_FLAG': "sprite-flag_grenada"},
                 'Guatemala': {'NAME': {'title': 'Guatemala', 'title_ru': 'Гватемала'}, 'COUNTRY_FLAG': "sprite-flag_guatemala"},
                 'Guinea': {'NAME': {'title': 'Guinea', 'title_ru': 'Гвинея'}, 'COUNTRY_FLAG': "sprite-flag_guinea"},
                 'Guinea Bissau': {'NAME': {'title': 'Guinea Bissau', 'title_ru': 'Гвинея-Бисау'}, 'COUNTRY_FLAG': "sprite-flag_guinea_bissau"},
                 'Guyana': {'NAME': {'title': 'Guyana', 'title_ru': 'Гайана'}, 'COUNTRY_FLAG': "sprite-flag_guyana"},
                 'Haiti': {'NAME': {'title': 'Haiti', 'title_ru': 'Гаити'}, 'COUNTRY_FLAG': "sprite-flag_haiti"},
                 'Honduras': {'NAME': {'title': 'Honduras', 'title_ru': 'Гондурас'}, 'COUNTRY_FLAG': "sprite-flag_honduras"},
                 'Hungary': {'NAME': {'title': 'Hungary', 'title_ru': 'Венгрия'}, 'COUNTRY_FLAG': "sprite-flag_hungary"},
                 'Iceland': {'NAME': {'title': 'Iceland', 'title_ru': 'Исландия'}, 'COUNTRY_FLAG': "sprite-flag_iceland"},
                 'India': {'NAME': {'title': 'India', 'title_ru': 'Индия'}, 'COUNTRY_FLAG': "sprite-flag_india"},
                 'Indonesia': {'NAME': {'title': 'Indonesia', 'title_ru': 'Индонезия'}, 'COUNTRY_FLAG': "sprite-flag_indonesia"},
                 'Iran': {'NAME': {'title': 'Iran', 'title_ru': 'Иран'}, 'COUNTRY_FLAG': "sprite-flag_iran"},
                 'Iraq': {'NAME': {'title': 'Iraq', 'title_ru': 'Ирак'}, 'COUNTRY_FLAG': "sprite-flag_iraq"},
                 'Ireland': {'NAME': {'title': 'Ireland', 'title_ru': 'Ирландия'}, 'COUNTRY_FLAG': "sprite-flag_ireland"},
                 'Italy': {'NAME': {'title': 'Italy', 'title_ru': 'Италия'}, 'COUNTRY_FLAG': "sprite-flag_italy"},
                 'Jamaica': {'NAME': {'title': 'Jamaica', 'title_ru': 'Ямайка'}, 'COUNTRY_FLAG': "sprite-flag_jamaica"},
                 'Japan': {'NAME': {'title': 'Japan', 'title_ru': 'Япония'}, 'COUNTRY_FLAG': "sprite-flag_japan"},
                 'Jordan': {'NAME': {'title': 'Jordan', 'title_ru': 'Иордания'}, 'COUNTRY_FLAG': "sprite-flag_jordan"},
                 'Kenya': {'NAME': {'title': 'Kenya', 'title_ru': 'Кения'}, 'COUNTRY_FLAG': "sprite-flag_kenya"},
                 'Kiribati': {'NAME': {'title': 'Kiribati', 'title_ru': 'Кирибати'}, 'COUNTRY_FLAG': "sprite-flag_kiribati"},
                 'Kuwait': {'NAME': {'title': 'Kuwait', 'title_ru': 'Кувейт'}, 'COUNTRY_FLAG': "sprite-flag_kuwait"},
                 'Laos': {'NAME': {'title': 'Laos', 'title_ru': 'Лаос'}, 'COUNTRY_FLAG': "sprite-flag_laos"},
                 'Lebanon': {'NAME': {'title': 'Lebanon', 'title_ru': 'Ливан'}, 'COUNTRY_FLAG': "sprite-flag_lebanon"},
                 'Lesotho': {'NAME': {'title': 'Lesotho', 'title_ru': 'Лесото'}, 'COUNTRY_FLAG': "sprite-flag_lesotho"},
                 'Liberia': {'NAME': {'title': 'Liberia', 'title_ru': 'Либерия'}, 'COUNTRY_FLAG': "sprite-flag_liberia"},
                 'Libya': {'NAME': {'title': 'Libya', 'title_ru': 'Ливия'}, 'COUNTRY_FLAG': "sprite-flag_libya"},
                 'Liechtenstein': {'NAME': {'title': 'Liechtenstein', 'title_ru': 'Лихтенштейн'}, 'COUNTRY_FLAG': "sprite-flag_liechtenstein"},
                 'Luxembourg': {'NAME': {'title': 'Luxembourg', 'title_ru': 'Люксембург'}, 'COUNTRY_FLAG': "sprite-flag_luxembourg"},
                 'Macedonia': {'NAME': {'title': 'Macedonia', 'title_ru': 'Македония'}, 'COUNTRY_FLAG': "sprite-flag_macedonia"},
                 'Madagascar': {'NAME': {'title': 'Madagascar', 'title_ru': 'Мадагаскар'}, 'COUNTRY_FLAG': "sprite-flag_madagascar"},
                 'Malawi': {'NAME': {'title': 'Malawi', 'title_ru': 'Малави'}, 'COUNTRY_FLAG': "sprite-flag_malawi"},
                 'Malaysia': {'NAME': {'title': 'Malaysia', 'title_ru': 'Малайзия'}, 'COUNTRY_FLAG': "sprite-flag_malaysia"},
                 'Maldives': {'NAME': {'title': 'Maldives', 'title_ru': 'Мальдивы'}, 'COUNTRY_FLAG': "sprite-flag_maledives"},
                 'Mali': {'NAME': {'title': 'Mali', 'title_ru': 'Мали'}, 'COUNTRY_FLAG': "sprite-flag_mali"},
                 'Malta': {'NAME': {'title': 'Malta', 'title_ru': 'Мальта'}, 'COUNTRY_FLAG': "sprite-flag_malta"},
                 'Marshall Islands': {'NAME': {'title': 'Marshall Islands', 'title_ru': 'Маршалловы острова'}, 'COUNTRY_FLAG': "sprite-flag_marshall_islands"},
                 'Mauretania': {'NAME': {'title': 'Mauretania', 'title_ru': 'Мавритания'}, 'COUNTRY_FLAG': "sprite-flag_mauretania"},
                 'Mauritius': {'NAME': {'title': 'Mauritius', 'title_ru': 'Маврикий'}, 'COUNTRY_FLAG': "sprite-flag_mauritius"},
                 'Mexico': {'NAME': {'title': 'Mexico', 'title_ru': 'Мексика'}, 'COUNTRY_FLAG': "sprite-flag_mexico"},
                 'Monaco': {'NAME': {'title': 'Monaco', 'title_ru': 'Монако'}, 'COUNTRY_FLAG': "sprite-flag_monaco"},
                 'Mongolia': {'NAME': {'title': 'Mongolia', 'title_ru': 'Монголия'}, 'COUNTRY_FLAG': "sprite-flag_mongolia"},
                 'Montenegro': {'NAME': {'title': 'Montenegro', 'title_ru': 'Черногория'}, 'COUNTRY_FLAG': "sprite-flag_montenegro"},
                 'Morocco': {'NAME': {'title': 'Morocco', 'title_ru': 'Марокко'}, 'COUNTRY_FLAG': "sprite-flag_morocco"},
                 'Mozambique': {'NAME': {'title': 'Mozambique', 'title_ru': 'Мозамбик'}, 'COUNTRY_FLAG': "sprite-flag_mozambique"},
                 'Myanmar': {'NAME': {'title': 'Myanmar', 'title_ru': 'Мьянма'}, 'COUNTRY_FLAG': "sprite-flag_myanmar"},
                 'Namibia': {'NAME': {'title': 'Namibia', 'title_ru': 'Намибия'}, 'COUNTRY_FLAG': "sprite-flag_namibia"},
                 'Nauru': {'NAME': {'title': 'Nauru', 'title_ru': 'Науру'}, 'COUNTRY_FLAG': "sprite-flag_nauru"},
                 'Nepal': {'NAME': {'title': 'Nepal', 'title_ru': 'Непал'}, 'COUNTRY_FLAG': "sprite-flag_nepal"},
                 'Netherlands': {'NAME': {'title': 'Netherlands', 'title_ru': 'Нидерланды'}, 'COUNTRY_FLAG': "sprite-flag_netherlands"},
                 'New Zealand': {'NAME': {'title': 'New Zealand', 'title_ru': 'Новая Зеландия'}, 'COUNTRY_FLAG': "sprite-flag_new_zealand"},
                 'Nicaragua': {'NAME': {'title': 'Nicaragua', 'title_ru': 'Никарагуа'}, 'COUNTRY_FLAG': "sprite-flag_nicaragua"},
                 'Niger': {'NAME': {'title': 'Niger', 'title_ru': 'Нигер'}, 'COUNTRY_FLAG': "sprite-flag_niger"},
                 'Nigeria': {'NAME': {'title': 'Nigeria', 'title_ru': 'Нигерия'}, 'COUNTRY_FLAG': "sprite-flag_nigeria"},
                 'Niue': {'NAME': {'title': 'Niue', 'title_ru': 'Ниуэ'}, 'COUNTRY_FLAG': "sprite-flag_niue"},
                 'North Korea': {'NAME': {'title': 'North Korea', 'title_ru': 'Северная Корея'}, 'COUNTRY_FLAG': "sprite-flag_north_korea"},
                 'Norway': {'NAME': {'title': 'Norway', 'title_ru': 'Норвегия'}, 'COUNTRY_FLAG': "sprite-flag_norway"},
                 'Oman': {'NAME': {'title': 'Oman', 'title_ru': 'Оман'}, 'COUNTRY_FLAG': "sprite-flag_oman"},
                 'Pakistan': {'NAME': {'title': 'Pakistan', 'title_ru': 'Пакистан'}, 'COUNTRY_FLAG': "sprite-flag_pakistan"},
                 'Palau': {'NAME': {'title': 'Palau', 'title_ru': 'Палау'}, 'COUNTRY_FLAG': "sprite-flag_palau"},
                 'Palestine': {'NAME': {'title': 'Palestine', 'title_ru': 'Палестина'}, 'COUNTRY_FLAG': "sprite-flag_palestine"},
                 'Panama': {'NAME': {'title': 'Panama', 'title_ru': 'Панама'}, 'COUNTRY_FLAG': "sprite-flag_panama"},
                 'Papua New Guinea': {'NAME': {'title': 'Papua New Guinea', 'title_ru': 'Папуа-Новая Гвинея'}, 'COUNTRY_FLAG': "sprite-flag_papua_new_guinea"},
                 'Paraguay': {'NAME': {'title': 'Paraguay', 'title_ru': 'Парагвай'}, 'COUNTRY_FLAG': "sprite-flag_paraquay"},
                 'Peru': {'NAME': {'title': 'Peru', 'title_ru': 'Перу'}, 'COUNTRY_FLAG': "sprite-flag_peru"},
                 'Philippines': {'NAME': {'title': 'Philippines', 'title_ru': 'Филиппины'}, 'COUNTRY_FLAG': "sprite-flag_philippines"},
                 'Poland': {'NAME': {'title': 'Poland', 'title_ru': 'Польша'}, 'COUNTRY_FLAG': "sprite-flag_poland"},
                 'Portugal': {'NAME': {'title': 'Portugal', 'title_ru': 'Португалия'}, 'COUNTRY_FLAG': "sprite-flag_portugal"},
                 'Qatar': {'NAME': {'title': 'Qatar', 'title_ru': 'Катар'}, 'COUNTRY_FLAG': "sprite-flag_qatar"},
                 'Romania': {'NAME': {'title': 'Romania', 'title_ru': 'Румыния'}, 'COUNTRY_FLAG': "sprite-flag_romania"},
                 'Rwanda': {'NAME': {'title': 'Rwanda', 'title_ru': 'Руанда'}, 'COUNTRY_FLAG': "sprite-flag_rwanda"},
                 'Saint Kitts and Nevis': {'NAME': {'title': 'Saint Kitts and Nevis', 'title_ru': 'Сент-Китс и Невис'}, 'COUNTRY_FLAG': "sprite-flag_saint_kitts_and_nevis"},
                 'Saint Lucia': {'NAME': {'title': 'Saint Lucia', 'title_ru': 'Сент-Люсия'}, 'COUNTRY_FLAG': "sprite-flag_saint_lucia"},
                 'Saint Vincent and the Grenadines': {'NAME': {'title': 'Saint Vincent and the Grenadines', 'title_ru': 'Сент-Винсент и Гренадины'}, 'COUNTRY_FLAG': "sprite-flag_saint_vincent_and_the_grenadines"},
                 'Samoa': {'NAME': {'title': 'Samoa', 'title_ru': 'Самоа'}, 'COUNTRY_FLAG': "sprite-flag_samoa"},
                 'San Marino': {'NAME': {'title': 'San Marino', 'title_ru': 'Сан - Марино'}, 'COUNTRY_FLAG': "sprite-flag_san_marino"},
                 'Sao Tome and Principe': {'NAME': {'title': 'Sao Tome and Principe', 'title_ru': 'Сан-Томе и Принсипи'}, 'COUNTRY_FLAG': "sprite-flag_sao_tome_and_principe"},
                 'Saudi Arabia': {'NAME': {'title': 'Saudi Arabia', 'title_ru': 'Саудовская Аравия'}, 'COUNTRY_FLAG': "sprite-flag_saudi_arabia"},
                 'Senegal': {'NAME': {'title': 'Senegal', 'title_ru': 'Сенегал'}, 'COUNTRY_FLAG': "sprite-flag_senegal"},
                 'Serbia': {'NAME': {'title': 'Serbia', 'title_ru': 'Сербия'}, 'COUNTRY_FLAG': "sprite-flag_serbia"},
                 'Seychelles': {'NAME': {'title': 'Seychelles', 'title_ru': 'Сейшельские острова'}, 'COUNTRY_FLAG': "sprite-flag_seychelles"},
                 'Sierra Leone': {'NAME': {'title': 'Sierra Leone', 'title_ru': 'Сьерра-Леоне'}, 'COUNTRY_FLAG': "sprite-flag_sierra_leone"},
                 'Singapore': {'NAME': {'title': 'Singapore', 'title_ru': 'Сингапур'}, 'COUNTRY_FLAG': "sprite-flag_singapore"},
                 'Slovakia': {'NAME': {'title': 'Slovakia', 'title_ru': 'Словакия'}, 'COUNTRY_FLAG': "sprite-flag_slovakia"},
                 'Slovenia': {'NAME': {'title': 'Slovenia', 'title_ru': 'Словения'}, 'COUNTRY_FLAG': "sprite-flag_slovenia"},
                 'Solomon Islands': {'NAME': {'title': 'Solomon Islands', 'title_ru': 'Соломоновы Острова'}, 'COUNTRY_FLAG': "sprite-flag_solomon_islands"},
                 'Somalia': {'NAME': {'title': 'Somalia', 'title_ru': 'Сомали'}, 'COUNTRY_FLAG': "sprite-flag_somalia"},
                 'South Africa': {'NAME': {'title': 'South Africa', 'title_ru': 'ЮАР'}, 'COUNTRY_FLAG': "sprite-flag_south_africa"},
                 'South Korea': {'NAME': {'title': 'South Korea', 'title_ru': 'Южная Корея'}, 'COUNTRY_FLAG': "sprite-flag_south_korea"},
                 'South Sudan': {'NAME': {'title': 'South Sudan', 'title_ru': 'Южный Судан'}, 'COUNTRY_FLAG': "sprite-flag_south_sudan"},
                 'Spain': {'NAME': {'title': 'Spain', 'title_ru': 'Испания'}, 'COUNTRY_FLAG': "sprite-flag_spain"},
                 'Sri Lanka': {'NAME': {'title': 'Sri Lanka', 'title_ru': 'Шри Ланка'}, 'COUNTRY_FLAG': "sprite-flag_sri_lanka"},
                 'Sudan': {'NAME': {'title': 'Sudan', 'title_ru': 'Судан'}, 'COUNTRY_FLAG': "sprite-flag_sudan"},
                 'Suriname': {'NAME': {'title': 'Suriname', 'title_ru': 'Суринам'}, 'COUNTRY_FLAG': "sprite-flag_suriname"},
                 'Swaziland': {'NAME': {'title': 'Swaziland', 'title_ru': 'Свазиленд'}, 'COUNTRY_FLAG': "sprite-flag_swaziland"},
                 'Sweden': {'NAME': {'title': 'Sweden', 'title_ru': 'Швеция'}, 'COUNTRY_FLAG': "sprite-flag_sweden"},
                 'Switzerland': {'NAME': {'title': 'Switzerland', 'title_ru': 'Швейцария'}, 'COUNTRY_FLAG': "sprite-flag_switzerland"},
                 'Syria': {'NAME': {'title': 'Syria', 'title_ru': 'Сирия'}, 'COUNTRY_FLAG': "sprite-flag_syria"},
                 'Tanzania': {'NAME': {'title': 'Tanzania', 'title_ru': 'Танзания'}, 'COUNTRY_FLAG': "sprite-flag_tanzania"},
                 'Thailand': {'NAME': {'title': 'Thailand', 'title_ru': 'Таиланд'}, 'COUNTRY_FLAG': "sprite-flag_thailand"},
                 'Togo': {'NAME': {'title': 'Togo', 'title_ru': 'Того'}, 'COUNTRY_FLAG': "sprite-flag_togo"},
                 'Tonga': {'NAME': {'title': 'Tonga', 'title_ru': 'Тонга'}, 'COUNTRY_FLAG': "sprite-flag_tonga"},
                 'Trinidad and Tobago': {'NAME': {'title': 'Trinidad and Tobago', 'title_ru': 'Тринидад и Тобаго'}, 'COUNTRY_FLAG': "sprite-flag_trinidad_and_tobago"},
                 'Tunisia': {'NAME': {'title': 'Tunisia', 'title_ru': 'Тунис'}, 'COUNTRY_FLAG': "sprite-flag_tunisia"},
                 'Turkey': {'NAME': {'title': 'Turkey', 'title_ru': 'Турция'}, 'COUNTRY_FLAG': "sprite-flag_turkey"},
                 'Tuvalu': {'NAME': {'title': 'Tuvalu', 'title_ru': 'Тувалу'}, 'COUNTRY_FLAG': "sprite-flag_tuvalu"},
                 'Uganda': {'NAME': {'title': 'Uganda', 'title_ru': 'Уганда'}, 'COUNTRY_FLAG': "sprite-flag_uganda"},
                 'United Arab Emirates': {'NAME': {'title': 'United Arab Emirates', 'title_ru': 'Объединенные Арабские Эмираты'}, 'COUNTRY_FLAG': "sprite-flag_united_arab_emirates"},
                 'United Kingdom': {'NAME': {'title': 'United Kingdom', 'title_ru': 'Великобритания'}, 'COUNTRY_FLAG': "sprite-flag_united_kingdom"},
                 'Uruguay': {'NAME': {'title': 'Uruguay', 'title_ru': 'Уругвай'}, 'COUNTRY_FLAG': "sprite-flag_uruquay"},
                 'USA': {'NAME': {'title': 'USA', 'title_ru': 'США'}, 'COUNTRY_FLAG': "sprite-flag_usa"},
                 'Vanuatu': {'NAME': {'title': 'Vanuatu', 'title_ru': 'Вануату'}, 'COUNTRY_FLAG': "sprite-flag_vanuatu"},
                 'Vatican City': {'NAME': {'title': 'Vatican City', 'title_ru': 'Ватикан'}, 'COUNTRY_FLAG': "sprite-flag_vatican_city"},
                 'Venezuela': {'NAME': {'title': 'Venezuela', 'title_ru': 'Венесуэла'}, 'COUNTRY_FLAG': "sprite-flag_venezuela"},
                 'Vietnam': {'NAME': {'title': 'Vietnam', 'title_ru': 'Вьетнам'}, 'COUNTRY_FLAG': "sprite-flag_vietnam"},
                 'Yemen': {'NAME': {'title': 'Yemen', 'title_ru': 'Йемен'}, 'COUNTRY_FLAG': "sprite-flag_yemen"},
                 'Zambia': {'NAME': {'title': 'Zambia', 'title_ru': 'Замбия'}, 'COUNTRY_FLAG': "sprite-flag_zambia"},
                 'Zimbabwe': {'NAME': {'title': 'Zimbabwe', 'title_ru': 'Зимбабве'}, 'COUNTRY_FLAG': "sprite-flag_zimbabwe"},

    }

    for title, attr in countries.items():
        cntr, res = Country.objects.get_or_create(title=title, create_user=crt_usr)
        if res:
            cntr.setAttributeValue(attr['NAME'], crt_usr)
        cntr.setAttributeValue(attr['COUNTRY_FLAG'], crt_usr)









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

                    'Country': {'NAME': True, 'FLAG': False},

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