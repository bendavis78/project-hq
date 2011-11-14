from defaults import *
import os

ENVIRONMENT = 'production'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'farstar_hq_production',
        'USER': 'farstar_hq',
        'PASSWORD': 'lywroysAuv9',
        'HOST': 'localhost',
        'PORT': '',
    }
}

X_SENDFILE_HEADER = True

PREPEND_WWW = False

DEFAULT_FROM_EMAIL = 'Farstar HQ <hq@wedontplayfair.com>'
SERVER_EMAIL = 'errors@web1.farstarserver.com'

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

MEDIA_ROOT = os.path.join(SITE_ROOT, '..', 'media')
STATIC_ROOT = os.path.join(SITE_ROOT, '..', 'static')

