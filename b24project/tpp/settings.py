# -*- encoding: utf-8 -*-
import os, logging
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEFAULT_FROM_EMAIL = 'noreply@b24online.com'
SERVER_EMAIL = 'noreply@b24online.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'noreply@b24online.com'
EMAIL_HOST_PASSWORD = 'qazZAQ123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
CELERY_SEND_TASK_ERROR_EMAILS = True

SOCIAL_AUTH_RAISE_EXCEPTIONS = True
RAISE_EXCEPTIONS = True

ADMINS = (
    ('Artur', 'artur@tppcenter.com'),
    ('Jenya', 'jenyapri@tppcenter.com'),
    ('Iliya', 'afend@tppcenter.com'),
)

ANONYMOUS_USER_ID = -1

MANAGERS = ADMINS
SECRET_KEY = '%(eobc-xo+rmyen-ni0cv6+q@&dgbdsos+*3fzz8fopl=ga!%i'
DEBUG = False

INTERNAL_IPS = ['80.179.7.34']
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
        'DIRS': [os.path.join(BASE_DIR, '..', 'templates').replace('\\', '/')],
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
                "tpp.context_processors.site_processor",
                "tpp.context_processors.current_organization_processor",
                "social.apps.django_app.context_processors.backends",
                "social.apps.django_app.context_processors.login_redirect"
            )
        }
    },
]

# django
DJANGO_APPS = (
    'django.contrib.postgres',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
)

LOCAL_APPS = (
    'social.apps.django_app.default',
    'raven.contrib.django.raven_compat',
    'b24online',
    'jobs',
    'centerpokupok',
    'usersites',
)

EXTERNAL_APPS = (
    'debug_toolbar',
    'djcelery',
    'loginas',
    'registration',
    'polymorphic_tree',
    'polymorphic',
    'mptt',
    'modeltranslation',
    'django.contrib.admin',
    'guardian',
    'captcha',
    'paypal.standard.ipn',
    'rest_framework',
    'compressor'
)

# the order is important!
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + EXTERNAL_APPS

# For installations on which you want to use the sandbox,
# set PAYPAL_TEST to True.  Ensure PAYPAL_RECEIVER_EMAIL is set to
# your sandbox account email too.
PAYPAL_TEST = False
PAYPAL_RECEIVER_EMAIL = 'migirov@gmail.com'

LOGOUT_URL = reverse_lazy('loginas-logout')
CAN_LOGIN_AS = lambda request, target_user: request.user.is_admin or request.user.is_commando

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}

ACCOUNT_ACTIVATION_DAYS = 7  # One week user's account activation period
REGISTRATION_OPEN = True  # Registration now is open
REGISTRATION_AUTO_LOGIN = True
LOGIN_REDIRECT_URL = 'profile:main'

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'tpp.DynamicSiteMiddleware.DynamicSiteMiddleware',
    'tpp.SiteUrlMiddleWare.SiteLangRedirect',
    'tpp.SiteUrlMiddleWare.SubDomainLanguageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'tpp.ChangeCsrfCookieDomainMiddleware.ChangeCsrfCookieDomainMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tpp.SiteUrlMiddleWare.GlobalRequest',
    'tpp.SetCurCompanyMiddleware.SetCurCompany',
    'centerpokupok.BasketMiddleware.Basket',
    'b24online.stats.middleware.RegisteredEventMiddleware',
    'tpp.GeolocationFilterByRegion.GeolocationMiddleware',
)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.cssmin.CSSCompressorFilter'
]

COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter'
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False
# DEBUG_TOOLBAR_CONFIG = {
#     'SHOW_TOOLBAR_CALLBACK': 'appl.func.show_toolbar'
# }

WSGI_APPLICATION = 'tpp.wsgi.application'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://tornado-redis.wlj5jm.0001.euw1.cache.amazonaws.com:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake',
#     }
# }

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_SAVE_EVERY_REQUEST = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'b24online_db',
        'USER': 'b24online',
        'PASSWORD': 'b24online**',
        'HOST': 'b24online-db.cueshukzldr1.eu-west-1.rds.amazonaws.com',
        'PORT': '5432',
        'CONN_MAX_AGE': 60
    }
}

USE_X_FORWARDED_HOST = True
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = False
USE_TZ = True

LOCALE_PATHS = (
    (os.path.join(BASE_DIR, '..', 'locale').replace('\\', '/')),
)

FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440

FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.MemoryFileUploadHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler",)

STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static').replace('\\', '/')
STATICFILES_DIRS = (os.path.join(BASE_DIR, '..', 'static-assets').replace('\\', '/'),)

STATIC_URL = '/static/'
ROOT_URLCONF = 'b24online.urls'
SITE_ID = 143

AUTH_USER_MODEL = 'b24online.User'

MEDIA_URL = '//static.b24online.com/'
MEDIA_ROOT = (os.path.join(BASE_DIR, '..', 'uploads').replace('\\', '/'))

# FACEBOOK
SOCIAL_AUTH_FACEBOOK_KEY = '1701658433380177'
SOCIAL_AUTH_FACEBOOK_SECRET = '72a75fd39cc67a7682e23c4939b48d1e'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'fields': 'id,name,email', }

# GOOGLE
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '941800294954-4vsfrb8u7ctc6bjvvfree9m9ja54d6bp.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'KPftndibEQQ5fvqYQyRqebR9'
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email']

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', ]

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.open_id.OpenIdAuth',
    'social.backends.google.GoogleOpenId',
    'social.backends.google.GoogleOAuth2',
    'social.backends.google.GoogleOAuth',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend'
)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.user.create_user',
    'b24online.models.user_extended_profile',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

LANGUAGE_CODE = 'ru'

LANGUAGES = [
    ('en', _('English')),
    ('ru', _('Russian')),
    ('am', _('Armenian')),
    ('bg', _('Bulgarian')),
    # ('az', _('Azerbaijan')),
    # ('be', _('Belarus')),
    # ('et', _('Estonia')),
    # ('ka', _('Georgia')),
    # ('kk', _('Kazakhstan')),
    # ('kg', _('Kyrgyzstan')),
    # ('lt', _('Lithuania')),
    # ('lv', _('Latvia')),
    # ('mo', _('Moldova')),
    # ('tg', _('Tajikistan')),
    # ('tm', _('Turkmenistan')),
    ('uk', _('Ukrainian')),
    # ('uz', _('Uzbekistan')),
    ('he', _('Hebrew')),
    ('ar', _('Arabic')),
    ('zh', _('Chinese')),
    ('es', _('Spanish')),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_ENABLE_FALLBACKS = True

MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('en', 'ru', 'he')
}

MODELTRANSLATION_AUTO_POPULATE = 'required'

ELASTIC_SEARCH_HOSTS = ['ec2-54-72-220-8.eu-west-1.compute.amazonaws.com']

############################# LXML settings ################################
ALLOWED_IFRAME_HOSTS = ['www.youtube.com']

############################# AWS settings ################################

AWS_SID = 'AKIAI5PE5AH2TNVDXCQQ'
AWS_SECRET = '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'
BUCKET = 'uploadstg'
BUCKET_REGION = 'eu-west-1'

##################### Celery settings ####################################
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_REDIS = 'redis://celeryredis.wlj5jm.0001.euw1.cache.amazonaws.com:6379'

CELERY_TASK_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

import djcelery

djcelery.setup_loader()

######################## DJANGO GUARDIAN SETTINGS #########################
GUARDIAN_GET_CONTENT_TYPE = 'polymorphic.contrib.guardian.get_polymorphic_base_content_type'

##################### Tornado settings ####################################
ORDERS_REDIS_HOST = 'tornado-redis.wlj5jm.0001.euw1.cache.amazonaws.com'

###################### Custom settings ###################################

RAVEN_CONFIG = {
    'dsn': 'https://c01d9a4420f94559be74d1b30f18e7e8:9d976cb46171495cbeb33892ae0ad102@sentry.ssilaev.com/3',
}

###################### Statistics settings ###################################
# Set the path to GeoIP database
GEOIP_DB_PATH = '/usr/share/GeoIP/'

# The Redis DB url for stats
EVENT_STORE_REDIS_URL = 'redis://celeryredis.wlj5jm.0001.euw1.cache.amazonaws.com/2'
ANALYTIC = True

try:
    from local_settings import *
except ImportError as e:
    logging.info(e)

# The text template for notification about ordered product
ORDER_NOTIFICATION_TEMPLATE = 'b24online/Products/notification.txt'
ORDER_NOTIFICATION_DISABLE = False
ORDER_NOTIFICATION_FROM = 'noreply@tppcenter.com'
ORDER_NOTIFICATION_TO = 'orders@b24online.com'

# Countries ID's form our database
GEO_COUNTRY_DB = {
    'Azerbaydjan': '1',
    'Armenia': '2',
    'Belarus': '3',
    'Georgia': '4',
    'Israel': '5',
    'Kazakhstan': '6',
    'Kyrgyzstan': '7',
    'Latvia': '8',
    'Lithuania': '9',
    'Moldova': '10',
    'Russia': '11',
    'USA': '142479',
}

