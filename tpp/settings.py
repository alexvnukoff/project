"""
Django settings for tpp project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os



BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEFAULT_FROM_EMAIL = 'noreply@tppcenter.com'
SERVER_EMAIL  = 'noreply@tppcenter.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'noreply@tppcenter.com'
EMAIL_HOST_PASSWORD = 'qazZAQ123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

CELERY_SEND_TASK_ERROR_EMAILS = True

ADMINS = (
    ('Artur', 'artur@tppcenter.com'),
    ('Jenya', 'jenyapri@tppcenter.com'),
    ('Iliya', 'afend@tppcenter.com'),
)

ANONYMOUS_USER_ID = -1

MANAGERS = ADMINS

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%(eobc-xo+rmyen-ni0cv6+q@&dgbdsos+*3fzz8fopl=ga!%i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

INTERNAL_IPS = ['80.179.7.34']

#ALLOWED_HOSTS = [
#    '.b24online.com', # Also allow FQDN and subdomains
#    '.tppcenter.com', # Also allow FQDN and subdomains
#]

ALLOWED_HOSTS = ['*']

USER_SITES_DOMAIN = "b24online.com"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': False,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': False,
            'context_processors': (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                'tpp.context_processors.site_processor'
            )
        }
    },
]



# Application definition

INSTALLED_APPS = (
    'core',
    'appl',
    'b24online',
    'legacy_data',
    'djcelery',
    'loginas',
    'tppcenter',
    'jobs',
    'centerpokupok',
    'usersites',
    'registration',
    'django.contrib.auth',
    'django.contrib.postgres',
    'polymorphic_tree',
    'polymorphic',
    'mptt',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'haystack',
    #'django.contrib.sitemaps',
    'modeltranslation',
    #'paypal.standard.ipn'
    'debug_toolbar',
    'guardian',
    'captcha',
    'django.contrib.admin',
)

# For installations on which you want to use the sandbox,
# set PAYPAL_TEST to True.  Ensure PAYPAL_RECEIVER_EMAIL is set to
# your sandbox account email too.
PAYPAL_TEST = True
PAYPAL_RECEIVER_EMAIL = 'migirov@gmail.com'

CAN_LOGIN_AS = lambda request, target_user: request.user.is_admin or request.user.is_commando


ACCOUNT_ACTIVATION_DAYS = 7 #One week user's account activation period
REGISTRATION_OPEN = True    #Registration now is open
REGISTRATION_AUTO_LOGIN = True
LOGIN_REDIRECT_URL = 'profile:main'

MIDDLEWARE_CLASSES = (
    'tpp.ChangeCsrfCookieDomainMiddleware.ChangeCsrfCookieDomainMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'tpp.DynamicSiteMiddleware.DynamicSiteMiddleware',
    'tpp.SiteUrlMiddleWare.SiteLangRedirect',
    'tpp.SiteUrlMiddleWare.SubdomainLanguageMiddleware',
    'tpp.SiteUrlMiddleWare.GlobalRequest',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'tpp.SetCurCompanyMiddleware.SetCurCompany'
)

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'appl.func.show_toolbar'
}

WSGI_APPLICATION = 'tpp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases



# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

#SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
#SESSION_COOKIE_DOMAIN=".stackoverflow.com"

DATABASES = {
    'default': {
        #'ENGINE': 'oraclepool',
        'ENGINE': 'django.db.backends.oracle',

        'NAME': 'TPPDB',
        'USER': 'DDeath',
        'PASSWORD': '123321',
        'HOST': 'tpp-production-db.cueshukzldr1.eu-west-1.rds.amazonaws.com',
        'PORT': '1521',
        #Section for Oracle
        'OPTIONS': {
            'threaded': True,
            'use_returning_into': False,
        },
    },
    'new': {
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'b24online_db',
         'USER': 'b24online',
         'PASSWORD': 'b24online**',
         'HOST': 'b24online-db.cueshukzldr1.eu-west-1.rds.amazonaws.com',
         'PORT': '5432'
    }
}

SOUTH_DATABASE_ADAPTERS = {'default': "south.db.oracle"}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
USE_X_FORWARDED_HOST = True



TIME_ZONE = 'UTC'


USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    (os.path.join(BASE_DIR, 'locale').replace('\\', '/')),
    "locale"
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440

FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.MemoryFileUploadHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler",)

STATIC_URL = '/static/'
ROOT_URLCONF = 'tppcenter.urls'
#SITE_ID = 143


#Were added by Expert Center -----------------------------------------------------
#Free of charge period in days
FREE_PERIOD = 60
#User notification starts before till the end_date (in days)
NOTIFICATION_BEFORE_END_DATE = 60

#AUTH_PROFILE_MODULE = 'core.Client'
AUTH_USER_MODEL = 'core.User'

MEDIA_URL = 'http://static.tppcenter.com/'
MEDIA_ROOT = (os.path.join(BASE_DIR, 'appl', 'Static', 'upload').replace('\\', '/'))

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend'
)



gettext = lambda s: s
LANGUAGES = (
    ('ru', gettext('Russia')),
    ('am', gettext('Armenia')),
    #('az', gettext('Azerbaijan')),
    #('be', gettext('Belarus')),
    ('en', gettext('England')),
    #('et', gettext('Estonia')),
    #('ka', gettext('Georgia')),
    #('kk', gettext('Kazakhstan')),
    #('kg', gettext('Kyrgyzstan')),
    #('lt', gettext('Lithuania')),
    #('lv', gettext('Latvia')),
    #('mo', gettext('Moldova')),
    #('tg', gettext('Tajikistan')),
    #('tm', gettext('Turkmenistan')),
    ('uk', gettext('Ukrainian')),
    #('uz', gettext('Uzbekistan')),
    ('he', gettext('Israel')),
    ('ar', gettext('Arabic')),
    ('zh', gettext('Chinese')),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_ENABLE_FALLBACKS = True

MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('en', 'ru'),
    'en': ('ru',),
    'ru': ('en',),
    'he': ('en',),
    'am': ('ru',),
    'ar': ('en',),
    'zh': ('en',),
    #'az': ('ru',),
    #'be': ('ru',),
    #'et': ('ru',),
    #'ka': ('ru',),
    #'kk': ('ru',),
    #'kg': ('ru',),
    #'lt': ('ru',),
    #'lv': ('ru',),
    #'mo': ('ru',),
    #'tg': ('ru',),
    #'tm': ('ru',),
    'uk': ('ru',),
    #'uz': ('ru',),
}


MODELTRANSLATION_AUTO_POPULATE = 'required'

ELASTIC_SEARCH_HOSTS = ['ec2-54-171-67-193.eu-west-1.compute.amazonaws.com']

######################## Haystack settings ###############################

HAYSTACK_CONNECTIONS = {
    'default':{
        'ENGINE': 'tpp.backend.MultilingualElasticEngine',
        'URL': 'ec2-54-171-67-193.eu-west-1.compute.amazonaws.com:9200',
        'INDEX_NAME': 'lang-en',
    },
}

for lang in LANGUAGES:

    if lang[0] is 'en':
        continue

    HAYSTACK_CONNECTIONS['default' + '_' + lang[0]] = {
        'ENGINE': HAYSTACK_CONNECTIONS['default']['ENGINE'],
        'URL': HAYSTACK_CONNECTIONS['default']['URL'],
        'INDEX_NAME': 'lang-' + lang[0],
    }

HAYSTACK_ROUTERS = ['tpp.backend.DefaultRouter']
#HAYSTACK_SIGNAL_PROCESSOR = 'core.signals.ItemIndexSignal'
HAYSTACK_ID_FIELD = 'id'

############################# AWS settings ################################

AWS_SID = 'AKIAI5PE5AH2TNVDXCQQ'
AWS_SECRET = '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'
BUCKET = 'uploadstg'
BUCKET_REGION = 'eu-west-1'

##################### Celery settings ####################################
CELERY_RESULT_BACKEND ='djcelery.backends.database:DatabaseBackend'
CELERY_REDIS = 'celeryredis.wlj5jm.0001.euw1.cache.amazonaws.com'


CELERY_TASK_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

import djcelery
djcelery.setup_loader()

##################### Tornado settings ####################################
ORDERS_REDIS_HOST = 'tornado-redis.wlj5jm.0001.euw1.cache.amazonaws.com'


###################### Custom settings ###################################
try:
    from local_settings import *
except ImportError:
    pass

