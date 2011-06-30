ADMINS = (('django.log', 'django.log@flowgram.com'),)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.gzip.GZipMiddleware',

    'django.middleware.common.CommonMiddleware',

    #'django.contrib.csrf.middleware.CsrfMiddleware',
    'flowgram.middleware.CustomCsrfMiddleware',

    #'django.contrib.sessions.middleware.SessionMiddleware',
    'flowgram.middleware.DualSessionMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    #'django.middleware.doc.XViewMiddleware',
    'flowgram.analytics.middleware.AnalyticsMiddleware',
)

from localsettings import DEBUG
if DEBUG:
    MIDDLEWARE_CLASSES += ('flowgram.middleware.ProfileMiddleware',)

from localsettings import fg_DOWN_FOR_MAINTENANCE
if fg_DOWN_FOR_MAINTENANCE:
    MIDDLEWARE_CLASSES += ('flowgram.middleware.DownForMaintenanceMiddleware',)

ROOT_URLCONF = 'flowgram.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'flowgram.core',
    'flowgram.faq',
    'flowgram.cms',
    'flowgram.analytics',
    'flowgram.tutorials',
)

AUTH_PROFILE_MODULE = 'core.UserProfile'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
PERSISTENT_SESSION_KEY = 'sessionpersistent'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
#    "django.core.context_processors.debug",
#    "django.core.context_processors.i18n",
#    "django.core.context_processors.media",
    "django.core.context_processors.request",
#    'django.contrib.sessions.context_processors.visitor_messages',
    'django.core.context_processors.messages',
    "flowgram.core.contexts.login_form",
    "flowgram.core.contexts.active_tab",
    "flowgram.core.contexts.csrf_token",
    #"flowgram.core.contexts.newsfeed",
    #"flowgram.core.contexts.on_beta",
)

SERVER_EMAIL = DEFAULT_FROM_EMAIL = 'website@flowgram.com'
CACHE_BACKEND = 'dummy:///'

DEFAULT_DURATION = 10000
HL_DURATION_NAME = "-1"

DEFAULT_PHOTO_WIDTH = 693
DEFAULT_PHOTO_HEIGHT = 520

GOOGLEBOT_UA = "googlebot"

ID_FIELD_LENGTH = 19
ID_ACTUAL_LENGTH = 14

THUMB_DIMENSIONS = ((800, 600),
                    (480, 360),
                    (400, 300),
                    (320, 240),
                    (200, 150),
                    (150, 100),
                    (120, 80))

BADGE_VIEW_LEVELS = [10000, 5000, 1000, 500, 100]

from localsettings import *
