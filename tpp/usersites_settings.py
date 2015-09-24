from tpp.settings import *
import os

SITE_ID = None
ALLOWED_HOSTS = ['*']

WSGI_APPLICATION = 'usersites.wsgi.application'
ROOT_URLCONF = 'usersites.urls'
TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'tpp', 'usersites', 'templates')]