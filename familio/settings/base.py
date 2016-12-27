"""
This is the project's main settings file that can be committed to your
repo. If you need to override a setting locally, use local.py
"""

import os
import logging

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.contrib.messages import constants as messages


# Your project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__) + "../../../")

SITE_ID = int(os.environ['SITE_ID'])
SECRET_KEY = os.environ['SECRET_KEY']
SETTINGS_PATH = os.environ['DJANGO_SETTINGS_MODULE']


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': '',
    },
}

SUPPORTED_NONLOCALES = ['media', 'admin', 'static']

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de'
LANGUAGES = [(b'de', b'German'), ]  # used by pybbm

# Defines the views served for root URLs.
ROOT_URLCONF = 'familio.urls'

# Application definition
INSTALLED_APPS = (
    # place grappelli and filebrowser first because they need to override admin
    # templates; grappelli.dashboard needs to come after contenttypes, but
    # before grappelli.
    'django.contrib.contenttypes',
    'grappelli.dashboard',
    'grappelli',
    'filebrowser',

    # Django contrib apps
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.sites',

    # Third-party apps, patches, fixes
    'reversion',
    'compressor',
    'django_extensions',
    'braces',
    'taggit',
    'dajaxice',
    'crispy_forms',
    'django_markup',
    'typogrify',
    'watson',
    'leaflet',
    'djgeojson',
    'userena',
    'userena.contrib.umessages',
    'easy_thumbnails',
    'pybb',

    # Application base, containing global templates.
    'base',
    'accounts',
    'comments',
    'tags',

    # Local apps, referenced via appname
    'maps',
    'books',
    'genealogio',
    'notaro',
    'partialdate',
)

# Place bcrypt first in the list, so it will be the default password hashing
# mechanism
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

# Sessions
#
# By default, be at least somewhat secure with our session cookies.
SESSION_COOKIE_HTTPONLY = True

# Set this to true if you are using https
SESSION_COOKIE_SECURE = True

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'  # override in local settings files if required

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'dajaxice.finders.DajaxiceFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'base.middleware.CheckUserSiteMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'pybb.middleware.PybbMiddleware',
    'watson.middleware.SearchContextMiddleware',
    'notaro.middleware.NotaroMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.static',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'pybb.context_processors.processor',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
            ]
        },
    },
]


TEST_RUNNER = 'django.test.runner.DiscoverRunner'



AUTHENTICATION_BACKENDS = {
    'base.auth_backend.SiteBackend',
    #  'django.contrib.auth.backends.ModelBackend',
}

FILE_UPLOAD_PERMISSIONS = 0o0664

# The WSGI Application to use for runserver
WSGI_APPLICATION = 'familio.wsgi.application'


# Recipients of traceback emails and other notifications.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

# SECURITY WARNING: don't run with debug turned on in production!
# Debugging displays nice error messages, but leaks memory. Set this to False
# on all server instances and True only for development.
DEBUG = TEMPLATE_DEBUG = False

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = False


# Enable this option for memcached
# CACHE_BACKEND= "memcached://127.0.0.1:11211/"


LOG_LEVEL = logging.INFO
HAS_SYSLOG = True
SYSLOG_TAG = "http_app_familio"  # Make this unique to your project.

# LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        # Include the default Django email handler for errors
        # This is what you'd get without configuring logging at all.
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            'include_html': False,
        },
        # Log to a text file that can be rotated by logrotate
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/django/djf.log'
        },
    },
    'loggers': {
        # Again, default Django configuration to email unhandled exceptions
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # Might as well log any errors anywhere else in Django
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Your own app - this assumes all your logger names start with "myapp."
        # 'myapp': {
        #     'handlers': ['logfile'],
        #     'level': 'WARNING',  # Or maybe INFO or DEBUG
        #     'propagate': False
        # },
    },
}


DAJAXICE_XMLHTTPREQUEST_JS_IMPORT = False


ANONYMOUS_USER_ID = -1
AUTH_PROFILE_MODULE = 'accounts.UserProfile'
USERENA_SIGNIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'
USERENA_DEFAULT_PRIVACY = 'closed'
USERENA_DISABLE_PROFILE_LIST = True
USERENA_DISABLE_SIGNUP = True
USERENA_USE_MESSAGES = False
USERENA_REGISTER_PROFILE = False
USERENA_ACTIVATION_DAYS = 150
USERENA_USE_HTTPS = True

GRAPPELLI_ADMIN_TITLE = '<a href="/">Unsere Familiengeschichte</a>'
GRAPPELLI_AUTOCOMPLETE_LIMIT = 100
GRAPPELLI_AUTOCOMPLETE_SEARCH_FIELDS = {
        "sites": {
            "site": ("domain__icontains", "name__icontains",)
            }
        }

GRAPPELLI_INDEX_DASHBOARD = 'familio.dashboard.CustomIndexDashboard'
GRAPPELLI_SWITCH_USER = True

FILEBROWSER_MAX_UPLOAD_SIZE = 100000000  # 100MB
FILEBROWSER_OVERWRITE_EXISTING = False
FILEBROWSER_VERSIONS_BASEDIR = '%d_versions/' % SITE_ID
FILEBROWSER_DIRECTORY = '%d_uploads/' % SITE_ID
PDF_DIRECTORY = '%d_pdfs' % SITE_ID

# sequence of settings variables accessible via template tag
ALLOWABLE_VALUES = ('DOCUMENTATION_URL', )


MARKUP_SETTINGS = {
    'restructuredtext': {
        'settings_overrides': {
            'initial_header_level': 2,
            'doctitle_xform': False,
            'table_style': 'booktabs',
            'footnote_references': 'superscript',
            'trim_footnote_reference_space': True,
            'default_reference_context': 'view',
            'link_base': ''
        }
    },
    'genrestructuredtext': {
        'settings_overrides': {
            'initial_header_level': 2,
            'doctitle_xform': False,
            'table_style': 'booktabs',
            'footnote_references': 'superscript',
            'trim_footnote_reference_space': True,
            'default_reference_context': 'view',
            'link_base': ''
        }
    }
}


LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (51.5, 7.5),
    'DEFAULT_ZOOM': 7,
}

PYBB_MARKUP = 'markdown'
PYBB_PROFILE_RELATED_NAME = 'userprofile'
PYBB_TEMPLATE = '_layouts/base.html'
PYBB_SMILES = {}
PYBB_DISABLE_SUBSCRIPTIONS = False
PYBB_DISABLE_NOTIFICATIONS = True
PYBB_DEFAULT_TIMEZONE = 1
PYBB_ATTACHMENT_ENABLE = True
PYBB_PERMISSION_HANDLER = 'accounts.permissions.CustomPermissionHandler'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

NOTARO_SETTINGS = {
    'autocomplete_helper': ('js/genrst-hint.js', ),
}

MESSAGE_TAGS = {
    messages.INFO: 'bg-info',
    messages.SUCCESS: 'bg-success',
    messages.DEBUG: 'bg-info',
    messages.WARNING: 'bg-warning',
    messages.ERROR: 'bg-danger',
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, '..', 'media'))

TRANSFER_SERVER = 'nginx'
TRANSFER_MAPPINGS = {
    MEDIA_ROOT: '/transfer',
}

