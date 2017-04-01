import os

DATABASES = {
    'default': {
         'ENGINE': 'django.db.backends.postgresql_psycopg2',
         'NAME': 'tpp',
         'USER': 'taxi',
         'PASSWORD': 'taxipassword',
         'HOST': '10.0.0.3',
         'PORT': '5432'
    }
}

CELERY_BROKER_URL = 'redis://10.0.0.3'
ORDERS_REDIS_HOST = '10.0.0.3'
DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'templates').replace('\\', '/')],
        'OPTIONS': {
            'debug': True,
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
                "tpp.context_processors.current_organization_processor"
            )
        }
    },
]

# DEBUG_
# OOLBAR_CONFIG = {
#     'SHOW_TOOLBAR_CALLBACK': lambda x: True
# }

ELASTIC_SEARCH_HOSTS = ['10.0.0.3']

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://10.0.0.3:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'

LOGGING = {}

BUCKET = 'tppuploads'
MEDIA_URL = 'https://s3-eu-west-1.amazonaws.com/tppuploads/'
USER_SITES_DOMAIN = 'tpp.dev'

SITE_ID = None
ALLOWED_HOSTS = ['*']

#ROOT_URLCONF = 'centerpokupok.urls'
#WSGI_APPLICATION = 'usersites.wsgi.application'
#ROOT_URLCONF = 'usersites.urls'

PARTIALS_URL = '/partials/'
PARTIALS_PATH = os.path.join(BASE_DIR, 'templates', 'usersites_angular', 'partials').replace('\\', '/')


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
    'captcha',
    'paypal.standard.ipn',
    'rest_framework',
    'compressor',
    'django_celery_results',
    'djcelery_email',
    'corsheaders',
)

CORS_ORIGIN_ALLOW_ALL = True

# the order is important!
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + EXTERNAL_APPS
EVENT_STORE_REDIS_URL = 'redis://10.0.0.3/1'
ANALYTIC = False