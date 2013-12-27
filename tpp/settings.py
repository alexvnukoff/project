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
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'modeltranslation',
    #'south',
    'core',
    'appl',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tpp.SiteUrlMiddleWare.SiteUrlMiddleWare'
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
        'HOST': 'djangodbinststage.c7szux21nkeg.us-west-2.rds.amazonaws.com',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '1521',                      # Set to empty string for default.
    }
#    'default': {
#        'ENGINE': 'django.db.backends.oracle',
#        'NAME': 'ORCL',
#        'USER': 'tpp',
#        'PASSWORD': 'migirov',
#        'HOST': 'djangodbinststage.c7szux21nkeg.us-west-2.rds.amazonaws.com',
#        'PORT': '1521',
#    }

}

#Section for Oracle
OPTIONS = {
    'threaded': True,
    'use_returning_into': False,
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'



TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'))


#Were added by Expert Center -----------------------------------------------------

#AUTH_PROFILE_MODULE = 'core.Client'
AUTH_USER_MODEL = 'core.User'
MEDIA_ROOT = '/home/media'
AUTHENTICATION_BACKENDS = (
    ('django.contrib.auth.backends.ModelBackend'),
)

gettext = lambda s: s
LANGUAGES = (
    ('ru', gettext('Russia')),
    ('am', gettext('Armenia')),
    ('az', gettext('Azerbaijan')),
    ('by', gettext('Belarus')),
    ('en', gettext('England')),
    ('et', gettext('Estonia')),
    ('ge', gettext('Georgia')),
    ('kz', gettext('Kazakhstan')),
    ('kg', gettext('Kyrgyzstan')),
    ('lt', gettext('Lithuania')),
    ('lv', gettext('Latvia')),
    ('md', gettext('Moldova')),
    ('tj', gettext('Tajikistan')),
    ('tm', gettext('Turkmenistan')),
    ('uk', gettext('Ukrainian')),
    ('uz', gettext('Uzbekistan')),
)
MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('ru', 'en'),
    'am': ('ru',),
    'az': ('ru',),
    'by': ('ru',),
    'et': ('ru',),
    'ge': ('ru',),
    'kz': ('ru',),
    'kg': ('ru',),
    'lt': ('ru',),
    'lv': ('ru',),
    'md': ('ru',),
    'tj': ('ru',),
    'tm': ('ru',),
    'uk': ('ru',),
    'uz': ('ru',),
}
try:
    from local_settings import *
