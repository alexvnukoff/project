#from tpp.settings import *
import os
from django.conf.project_template.project_name.settings import BASE_DIR

SITE_ID = None
ALLOWED_HOSTS = ['*']

#WSGI_APPLICATION = 'usersites.wsgi.application'
TEMPLATE_DIRS = [os.path.join(BASE_DIR, '..', 'usersites', 'templates')]
ROOT_URLCONF = 'usersites.urls'
