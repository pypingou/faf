# -*- coding: utf-8 -*-
import os
from pyfaf.config import config
from pyfaf.utils.parse import str2bool
from sqlalchemy.engine.url import _parse_rfc1738_args

# Definition of PROJECT_DIR, just for convenience:
# you can use it instead of specifying the full path
PROJECT_DIR = os.path.dirname(__file__)

DEBUG = str2bool(config["hub.debug"])
TEMPLATE_DEBUG = DEBUG

ADMINS = map(lambda x: ('', x.strip()), config["hub.admins"].split(','))

MANAGERS = ADMINS

ALLOWED_HOSTS = ["*"]

dburl = _parse_rfc1738_args(config["storage.connectstring"])
# try hard to use psycopg2
if dburl.drivername.lower() in ["postgres", "postgresql"]:
    dburl.drivername = "postgresql_psycopg2"

if dburl.drivername.lower() == 'sqlite':
    dburl.drivername += '3'

DATABASES = {
    'default': {
        # 'django.db.backends.' + {'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'}
        'ENGINE': "django.db.backends.{0}".format(dburl.drivername),
        # Or path to database file if using sqlite3.
        'NAME': dburl.database,
        # Not used with sqlite3.
        'USER': dburl.username,
        # Not used with sqlite3.
        'PASSWORD': dburl.password,
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': dburl.host,
        # Set to empty string for default. Not used with sqlite3.
        'PORT': dburl.port,
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Prague'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to task logs and other files
FILES_PATH = config["hub.dir"]

# Root directory for uploaded files
UPLOAD_DIR = os.path.join(FILES_PATH, 'upload')

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, "media/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '{0}/media/'.format(config["hub.urlprefix"])

# NOTE: this setting is not compatible with  Django 1.4 and is replaced by
# more generic STATIC_URL variable (Django will now expect to find the admin
# static files under the URL <STATIC_URL>/admin/.)
ADMIN_MEDIA_PREFIX = '{0}/admin/media/'.format(config["hub.urlprefix"])

STATIC_URL = '{0}/static/'.format(config["hub.urlprefix"])

if DEBUG:
    STATICFILES_DIRS = (
        os.path.join(PROJECT_DIR, '../external/'),
        os.path.join(PROJECT_DIR, 'static/')
    )

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@RANDOM_STRING@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        'django.template.loaders.eggs.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'webfaf.menu.MenuMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'dajaxice.finders.DajaxiceFinder',
)

ROOT_URLCONF = 'webfaf.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'webfaf.menu.menu_context_processor',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    # Django AJAX libs
    'dajaxice',
    'dajax',
    # openid
    'django_openid_auth',
    # enable hub custom filters
    'webfaf',
    # hub apps
    'webfaf.summary',
    'webfaf.status',
    'webfaf.reports',
    'webfaf.problems',
    'webfaf.services',
    'webfaf.stats',
)

AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)


# required to work around
# Exception Value: <openid.yadis.manager.YadisServiceManager object at
# 0x7fd2f43b2250> is not JSON serializable
# https://bugs.launchpad.net/django-openid-auth/+bug/1252826
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

OPENID_CREATE_USERS = True
OPENID_UPDATE_DETAILS_FROM_SREG = True
OPENID_ENABLED = str2bool(config.get("openid.enabled", ""))

LOGIN_URL = '/openid/login/'
LOGIN_REDIRECT_URL = '/'

DAJAXICE_MEDIA_PREFIX = 'faf/dajaxice'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'dajaxice': {
            'handlers': ['console'],
            'level': 'ERROR'
        }
    }
}

try:
    execfile(os.path.join(PROJECT_DIR, 'settings_local.py'))
except:
    pass
