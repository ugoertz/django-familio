"""
This is an example settings/test.py file.
Use this settings file when running tests.
These settings overrides what's in settings/base.py
"""

from __future__ import absolute_import
import os

from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'djfdbtest',
        'USER': 'djftest',
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': '',
        'PORT': '',
    },
}

INSTALLED_APPS += ('django_nose', )

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Tell nose to measure coverage on the 'foo' and 'bar' apps
NOSE_ARGS = [
        '--with-coverage',
        '--cover-package=partialdate,comments,accounts,base,genealogio,notaro,books,tags,maps,pdfexport',
        ]

# Recipients of traceback emails and other notifications.
ADMINS = (
    ('admin', 'root@localhost'),
)
MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEBUG = True

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = True

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost', ]

# Log settings
# LOGGING_CONFIG = None

ADMIN_USERNAME = 'admin'

DOCUMENTATION_URL =\
        os.path.join(PROJECT_ROOT, '/docs/_build/html/')

MEDIA_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, '../test_media/'))
