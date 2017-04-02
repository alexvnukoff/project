# -*- encoding: utf-8 -*-
import os
import logging
import redis
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEFAULT_FROM_EMAIL = os.getenv('SETTING_DEFAULT_FROM_EMAIL', 'noreply@b24online.com')
SERVER_EMAIL = os.getenv('SETTING_SERVER_EMAIL', 'noreply@b24online.com')
EMAIL_HOST = os.getenv('SETTING_EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_USER = os.getenv('SETTING_EMAIL_HOST_USER', 'noreply@b24online.com')
EMAIL_HOST_PASSWORD = os.getenv('SETTING_EMAIL_HOST_PASSWORD', 'qazZAQ123')
EMAIL_PORT = os.getenv('SETTING_EMAIL_PORT', 587)
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

CELERY_SEND_TASK_ERROR_EMAILS = True

SOCIAL_AUTH_RAISE_EXCEPTIONS = True
RAISE_EXCEPTIONS = True

ADMINS = (
    ('Artur', 'artur@tppcenter.com'),
)

ANONYMOUS_USER_ID = -1

MANAGERS = ADMINS
SECRET_KEY = '%(eobc-xo+rmyen-ni0cv6+q@&dgbdsos+*3fzz8fopl=ga!%i'
DEBUG = False

INTERNAL_IPS = []
ALLOWED_HOSTS = ['*']
USER_SITES_DOMAIN = "b24online.com"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR', # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/src/log/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
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
                "tpp.context_processors.site_languages_processor",
                "tpp.context_processors.current_organization_processor",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect"
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
    'raven.contrib.django.raven_compat',
    'captcha',
    'b24online',
    'jobs',
    'centerpokupok',
    'usersites',
)

EXTERNAL_APPS = (
    #'debug_toolbar',
    'social_django',
    'loginas',
    'registration',
    'polymorphic_tree',
    'polymorphic',
    'mptt',
    'modeltranslation',
    'django.contrib.admin',
    'guardian',
    'paypal.standard.ipn',
    'rest_framework',
    'compressor',
    'django_celery_results',
    'djcelery_email'
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
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

ACCOUNT_ACTIVATION_DAYS = 7  # One week user's account activation period
REGISTRATION_OPEN = True  # Registration now is open
REGISTRATION_AUTO_LOGIN = True
LOGIN_REDIRECT_URL = 'profile:main'

MIDDLEWARE_CLASSES = (
    # 'django.middleware.gzip.GZipMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv('SETTING_REDIS_CACHE_LOCATION', "redis://redis:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_SAVE_EVERY_REQUEST = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('SETTING_DB_NAME', 'b24online_db'),
        'USER': os.getenv('SETTING_DB_USER', 'b24online'),
        'PASSWORD': os.getenv('SETTING_DB_PASSWORD', 'b24online**'),
        'HOST': os.getenv('SETTING_DB_HOST', 'b24online-db.cueshukzldr1.eu-west-1.rds.amazonaws.com'),
        'PORT': os.getenv('SETTING_DB_PORT', '5432'),
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

MEDIA_URL = os.getenv('SETTING_MEDIA_URL', '//static.b24online.com/')
MEDIA_ROOT = (os.path.join(BASE_DIR, '..', 'uploads').replace('\\', '/'))

# FACEBOOK
SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('SETTING_SOCIAL_AUTH_FACEBOOK_KEY', '1701658433380177')
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('SETTING_SOCIAL_AUTH_FACEBOOK_SECRET', '72a75fd39cc67a7682e23c4939b48d1e')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'fields': 'id,name,email', }

# GOOGLE
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SETTING_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '941800294954-4vsfrb8u7ctc6bjvvfree9m9ja54d6bp.apps.googleusercontent.com')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SETTING_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', 'KPftndibEQQ5fvqYQyRqebR9')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email']

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', ]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.google.GoogleOAuth',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend'
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.mail.mail_validation',
    'social_core.pipeline.user.create_user',
    'b24online.models.user_extended_profile',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details'
)

LANGUAGE_CODE = 'en'

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

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_ENABLE_FALLBACKS = True

MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('en', 'ru', 'he')
}

MODELTRANSLATION_AUTO_POPULATE = 'required'

ELASTIC_SEARCH_HOSTS = [os.getenv('SETTING_ELASTIC_SEARCH_HOST', 'elasticsearch')]

############################# LXML settings ################################
ALLOWED_IFRAME_HOSTS = ['www.youtube.com']

############################# AWS settings ################################

AWS_SID = os.getenv('SETTING_AWS_SID', 'AKIAI5PE5AH2TNVDXCQQ')
AWS_SECRET = os.getenv('SETTING_AWS_SECRET', '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')
BUCKET = os.getenv('SETTING_BUCKET', 'uploadstg')
BUCKET_REGION = os.getenv('SETTING_BUCKET_REGION', 'eu-west-1')

##################### Celery settings ####################################
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_URL = os.getenv('SETTING_CELERY_REDIS_BROKER_URL', 'redis://redis:6379/4')

CELERY_TASK_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

######################## DJANGO GUARDIAN SETTINGS #########################
GUARDIAN_GET_CONTENT_TYPE = 'polymorphic.contrib.guardian.get_polymorphic_base_content_type'

##################### Tornado settings ####################################
ORDERS_REDIS_HOST = os.getenv('SETTING_ORDERS_REDIS_HOST', 'redis://redis:6379/5')

###################### Custom settings ###################################

RAVEN_CONFIG = {
    'dsn': 'https://f694fe38d6a74dbd8f1f6b15ce840756:0345d977c5cb4c0185d12619141fbe3c@sentry.msk.tech/3',
}

###################### Statistics settings ###################################
# Set the path to GeoIP database
GEOIP_DB_PATH = '/usr/share/GeoIP/'

# The Redis DB url for stats
EVENT_STORE_REDIS_URL = os.getenv('SETTING_EVENT_STORE_REDIS_URL', 'redis://redis/2')
ANALYTIC = True


# The text template for notification about ordered product
ORDER_NOTIFICATION_TEMPLATE = 'b24online/Products/notification.txt'
ORDER_NOTIFICATION_DISABLE = False
ORDER_NOTIFICATION_FROM = os.getenv('SETTING_ORDER_NOTIFICATION_FROM', 'noreply@b24online.com')
ORDER_NOTIFICATION_TO = os.getenv('SETTING_ORDER_NOTIFICATION_TO', 'orders@b24online.com')

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
    'Ukraine': '15',
}

REDIS_USERSITE = redis.Redis(
        host=os.getenv('SETTING_REDIS_USERSITE_HOST', 'redis'),
        port=os.getenv('SETTING_REDIS_USERSITE_PORT', 6379),
        db=os.getenv('SETTING_REDIS_USERSITE_DB', 3),
    )

TYPEOF_TEMPLATE = (
    (0, 'Simple'),
    (1, 'Extend'),
)

# CAPTCHA SETTINGS
CAPTCHA_FONT_SIZE = 26
CAPTCHA_IMAGE_SIZE = (120, 50)
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)
CAPTCHA_BACKGROUND_COLOR = '#f1f1f1'
CAPTCHA_FOREGROUND_COLOR = '#666666'


try:
    from local_settings import *
except ImportError as e:
    logging.info(e)

