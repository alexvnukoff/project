from tpp.settings import *

SITE_ID = None
ALLOWED_HOSTS = ['*']

PARTIALS_URL = '/partialw/'
PARTIALS_PATH = os.path.join(BASE_DIR, '..', 'templates', 'usersites_angular', 'partials').replace('\\', '/')

WSGI_APPLICATION = 'usersites.wsgi.application'
ROOT_URLCONF = 'usersites.urls'