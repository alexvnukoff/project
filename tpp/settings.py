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


EMAIL_BACKEND ='django.core.mail.backends.console.EmailBackend'
EMAIL_PORT = 1025
DEFAULT_FROM_EMAIL = 'admin@tppcenter.com'




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%(eobc-xo+rmyen-ni0cv6+q@&dgbdsos+*3fzz8fopl=ga!%i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


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
    'registration',
    'modeltranslation',
    'south',
    'core',
    'appl',
    'legacy_data',
)

ACCOUNT_ACTIVATION_DAYS = 7 #One week user's account activation period
REGISTRATION_OPEN = True    #Registration now is open

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tpp.SiteUrlMiddleWare.SiteUrlMiddleWare',
    'tpp.SiteUrlMiddleWare.GlobalRequest',
)


ROOT_URLCONF = 'tpp.urls'

WSGI_APPLICATION = 'tpp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases





DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'ORCL',
        'USER': 'tpp',
        'PASSWORD': 'migirov',
        'HOST': 'djangodbinststage.c7szux21nkeg.us-west-2.rds.amazonaws.com',
        'PORT': '1521',
        #Section for Oracle
        'OPTIONS': {
            'threaded': True,
            'use_returning_into': False,
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = ("locale",)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'



TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'))


#Were added by Expert Center -----------------------------------------------------

#AUTH_PROFILE_MODULE = 'core.Client'
AUTH_USER_MODEL = 'core.User'
MEDIA_ROOT = (os.path.join(os.path.dirname(__file__), '..', 'appl/Static').replace('\\', '/'))
AUTHENTICATION_BACKENDS = (
    ('django.contrib.auth.backends.ModelBackend'),
)
#Email backend for production
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# Email backend for debugging


gettext = lambda s: s
LANGUAGES = (
    ('ru', gettext('Russia')),
    ('am', gettext('Armenia')),
    ('az', gettext('Azerbaijan')),
    ('be', gettext('Belarus')),
    ('en', gettext('England')),
    ('et', gettext('Estonia')),
    ('ka', gettext('Georgia')),
    ('kk', gettext('Kazakhstan')),
    ('kg', gettext('Kyrgyzstan')),
    ('lt', gettext('Lithuania')),
    ('lv', gettext('Latvia')),
    ('mo', gettext('Moldova')),
    ('tg', gettext('Tajikistan')),
    ('tm', gettext('Turkmenistan')),
    ('uk', gettext('Ukrainian')),
    ('uz', gettext('Uzbekistan')),
    ('he', gettext('Israel')),
)
MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('ru', 'en'),
    'am': ('ru',),
    'az': ('ru',),
    'be': ('ru',),
    'et': ('ru',),
    'ka': ('ru',),
    'kk': ('ru',),
    'kg': ('ru',),
    'lt': ('ru',),
    'lv': ('ru',),
    'mo': ('ru',),
    'tg': ('ru',),
    'tm': ('ru',),
    'uk': ('ru',),
    'uz': ('ru',),
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

'''
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}
'''

HAYSTACK_CONNECTIONS = {
    'default':{
        'ENGINE': 'tpp.backend.MultilingualElasticEngine',
        'URL': 'http://ec2-50-112-162-13.us-west-2.compute.amazonaws.com:9200',
        'INDEX_NAME': 'lang-en',
    },
}

for lang in LANGUAGES:
    HAYSTACK_CONNECTIONS['default' + '_' + lang] = {
        'ENGINE': HAYSTACK_CONNECTIONS['default']['ENGINE'],
        'URL': HAYSTACK_CONNECTIONS['default']['URL'],
        'INDEX_NAME': 'lang-' + lang,
    }

HAYSTACK_SIGNAL_PROCESSOR = 'core.signals.ItemIndexSignal'

try:
    from local_settings import *
except ImportError:
    pass
