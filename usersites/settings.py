from tpp.settings import *

SITE_ID = None
ALLOWED_HOSTS = ['*']

WSGI_APPLICATION = 'usersites.wsgi.application'
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
ROOT_URLCONF = 'usersites.urls'
