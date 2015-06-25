"""
This is an example settings/test.py file.
Use this settings file when running tests.
These settings overrides what's in settings/base.py
"""

from __future__ import absolute_import
import json
import os

from .base import *

# PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__) + "../../../")
from .base import *

secrets = json.load(file(os.path.join(PROJECT_ROOT, '../secrets_test.json')))

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'djfdbtest',
        'USER': 'djftest',
        'PASSWORD': secrets['DB_PASSWORD'],
        'HOST': '',
        'PORT': '',
        # 'OPTIONS': {
        #     'init_command': 'SET storage_engine=InnoDB',
        #     'charset' : 'utf8',
        #     'use_unicode' : True,
        # },
        # 'TEST_CHARSET': 'utf8',
        # 'TEST_COLLATION': 'utf8_general_ci',
    },
    # 'slave': {
    #     ...
    # },
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
TEMPLATE_DEBUG = True

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = True

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost', ]

# Log settings
# LOGGING_CONFIG = None

ADMIN_USERNAME = 'admin'
SITE_ID = 1

SECRET_KEY = secrets['SECRET_KEY_%d' % SITE_ID]

FILEBROWSER_VERSIONS_BASEDIR = '%d_versions/' % SITE_ID
FILEBROWSER_DIRECTORY = '%d_uploads/' % SITE_ID
STATIC_URL = '/static/'

DOCUMENTATION_URL =\
        os.path.join(PROJECT_ROOT, '/docs/_build/html/')
ALLOWABLE_VALUES = ('DOCUMENTATION_URL', )

