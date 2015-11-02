from tpp.settings import *

SITE_ID = 121

WSGI_APPLICATION = 'tpp.centerpokupok_wsgi.application'

ALLOWED_HOSTS = [
    '.centerpokupok.ru', # Also allow FQDN and subdomains
    '.centerpokupok.com'
]

ROOT_URLCONF = 'centerpokupok.urls'