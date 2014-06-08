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
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'noreply@tppcenter.com'
EMAIL_HOST_PASSWORD = 'qazZAQ123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ADMINS = (
    ('Artur', 'artur@tppcenter.com'),
    ('Jenya', 'jenyapri@tppcenter.com'),
    ('Iliya', 'afend@tppcenter.com'),
)



MANAGERS = ADMINS

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%(eobc-xo+rmyen-ni0cv6+q@&dgbdsos+*3fzz8fopl=ga!%i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = [
    '.tppcenter.com', # Allow domain and subdomains
    '.centerpokupok.ru', # Also allow FQDN and subdomains
    '.BC-CIS.COM', # Also allow FQDN and subdomains
    '.B24ONLINE.COM', # Also allow FQDN and subdomains
    '.centerpokupok.com'
]

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



# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'haystack',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    #'django.contrib.sitemaps',
    'registration',
    'modeltranslation',
    'south',
    'core',
    'appl',
    'legacy_data',
    'djcelery',
    'loginas'
    #'paypal.standard.ipn'
    #'debug_toolbar'
)

# For installations on which you want to use the sandbox,
# set PAYPAL_TEST to True.  Ensure PAYPAL_RECEIVER_EMAIL is set to
# your sandbox account email too.
# PAYPAL_TEST = True
PAYPAL_TEST = True
PAYPAL_RECEIVER_EMAIL = 'migirov@gmail.com'

CAN_LOGIN_AS = lambda request, target_user: request.user.is_admin or request.user.is_commando


ACCOUNT_ACTIVATION_DAYS = 7 #One week user's account activation period
REGISTRATION_OPEN = True    #Registration now is open

MIDDLEWARE_CLASSES = (

    'django.contrib.sessions.middleware.SessionMiddleware',
    'tpp.SiteUrlMiddleWare.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tpp.SiteUrlMiddleWare.SiteUrlMiddleWare',
    'tpp.SiteUrlMiddleWare.GlobalRequest',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'appl.func.show_toolbar'
}


ROOT_URLCONF = 'tpp.urls'

WSGI_APPLICATION = 'tpp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases



CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'tppcache.wlj5jm.0001.euw1.cache.amazonaws.com:11211',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCY:': 2

        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

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

LOCALE_PATHS = ("/var/www/html/tpp/locale", "locale")


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440

FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.MemoryFileUploadHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler",)

STATIC_URL = '/static/'

TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'))


#Were added by Expert Center -----------------------------------------------------
#Free of charge period in days
FREE_PERIOD = 60
#User notification starts before till the end_date (in days)
NOTIFICATION_BEFORE_END_DATE = 15

#AUTH_PROFILE_MODULE = 'core.Client'
AUTH_USER_MODEL = 'core.User'

MEDIA_URL = 'http://static.tppcenter.com/'
MEDIA_ROOT = (os.path.join(os.path.dirname(__file__), '..', 'appl', 'Static').replace('\\', '/'))

AUTHENTICATION_BACKENDS = (
    ('django.contrib.auth.backends.ModelBackend'),
)

SESSION_COOKIE_DOMAIN = '.tppcenter.com'

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
    #('uk', gettext('Ukrainian')),
    #('uz', gettext('Uzbekistan')),
    ('he', gettext('Israel')),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_ENABLE_FALLBACKS = True

MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('ru', 'en'),
    'en': ('ru',),
    'ru': ('en',),
    'he': ('en',),
    'am': ('en',),
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
    #'uk': ('ru',),
    #'uz': ('ru',),
}




TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)


######################## Haystack settings ###############################

HAYSTACK_CONNECTIONS = {
    'default':{
        'ENGINE': 'tpp.backend.MultilingualElasticEngine',
        'URL': 'ec2-54-72-220-8.eu-west-1.compute.amazonaws.com:9200',
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

USE_X_FORWARDED_HOST = True

HAYSTACK_SIGNAL_PROCESSOR = 'core.signals.ItemIndexSignal'

############################# AWS settings ################################

AWS_SID = 'AKIAI5PE5AH2TNVDXCQQ'
AWS_SECRET = '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'
BUCKET = 'uploadstg'


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
