from tpp.settings import *

SITE_ID = None
ALLOWED_HOSTS = ['*']

PARTIALS_URL = '/partialw/'
PARTIALS_PATH = os.path.join(BASE_DIR, '..', 'templates', 'usersites_angular', 'partials').replace('\\', '/')

WSGI_APPLICATION = 'usersites.wsgi.application'
ROOT_URLCONF = 'usersites.urls'

SESSION_COOKIE_NAME = 'site_session_id'

if TEMPLATES:
    TEMPLATES[0]['DIRS'].insert(0,
        os.path.join(BASE_DIR, '..', 'templates/_usersites/'))

LOGIN_REDIRECT_URL = '/'

# For PayPal button
PAYPAL_IMAGE = 'https://www.sandbox.paypal.com/en_US/i/btn/btn_buynowCC_LG.gif'

