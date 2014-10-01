from tpp.settings import *

SITE_ID = None
ALLOWED_HOSTS = ['*']

WSGI_APPLICATION = 'tpp.users_wsgi.application'
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'usersites','templates').replace('\\', '/'))
ROOT_URLCONF = 'usersites.urls'
