import os

DATABASES = {
    'default': {
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'tppdb',
         'USER': 'taxi',
         'PASSWORD': 'taxipassword',
         'HOST': 'localhost',
         'PORT': '5432'
    }
}

CELERY_REDIS = 'localhost'
ORDERS_REDIS_HOST = 'localhost'
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
                'tpp.context_processors.site_processor'
            )
        }
    },
]

HAYSTACK_CONNECTIONS = {
    'default':{
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'localhost:9200',
        'INDEX_NAME': 'lang-test',
    },
}
# DEBUG_
# OOLBAR_CONFIG = {
#     'SHOW_TOOLBAR_CALLBACK': lambda x: True
# }
ELASTIC_SEARCH_HOSTS = ['127.0.0.1']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
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
    'rest_framework'
)

# the order is important!
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + EXTERNAL_APPS
EVENT_STORE_REDIS_URL = 'redis://localhost/1'
ANALYTIC = False