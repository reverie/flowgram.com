DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'django_db'             # Or path to database file if using sqlite3.
DATABASE_USER = 'db_user'             # Not used with sqlite3.
DATABASE_PASSWORD = 'db_pass'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
DATABASE_HOST_BLOG = 'db.flowgram.com' # for localhost dev leave this, otherwise it should be the local IP address of the machine on dev 192.168.100.36

MASTER_DOMAIN_NAME = 'localhost:8000'

# Avatars will go in the "avatars" subdirectory of this:
MEDIA_ROOT = '/var/apps/website/dev/uploads/'

# setting this up for internal media
INTERNAL_MEDIA_ROOT = MEDIA_ROOT + 'internal/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://' + MASTER_DOMAIN_NAME + '/media/'

# setting this up for internal media
INTERNAL_MEDIA_URL = 'http://' + MASTER_DOMAIN_NAME + '/intmedia/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'blah'

my_BASE_DIR = '/var/apps/website/dev/current/django/'
my_UPLOADS_DIR = '/var/apps/website/dev/uploads/'
my_SOURCE_BASE_DIR = '/var/apps/website/dev/current/django_source/'
FMS_STREAM_DIR = "C:/Program Files/Adobe/Flash Media Server 3/applications/flowgram/streams/_definst_/localhost"

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    my_BASE_DIR + 'templates/'
)

my_URL_BASE = 'http://' + MASTER_DOMAIN_NAME + '/'
fg_DEFAULT_AVATAR_URL = MEDIA_URL + '/images/default_avatar.gif'

my_DEV_STATIC_MEDIA = my_BASE_DIR + 'static/'
my_DEV_STATIC_ADMIN_MEDIA = my_SOURCE_BASE_DIR + 'django/contrib/admin/media/'
my_DEV_STATIC_FLEX_MEDIA = my_DEV_STATIC_MEDIA + "flex/"

my_WOWKASTDIR = my_UPLOADS_DIR + 'fgrams/'
PROCESSED_AUDIO_DIR = my_UPLOADS_DIR + "processed_audio/"

fg_LOG_DIR = my_BASE_DIR + 'logfiles/'
my_UPLOAD_LOG = my_BASE_DIR + 'upload_log.txt'
my_DEV_ERRORLOGDIR = my_BASE_DIR + 'errors/'

fg_DOWN_FOR_MAINTENANCE = False

#CACHE_MIDDLEWARE_KEY_PREFIX = 'd'
#CACHE_BACKEND = "memcached://127.0.0.1:11211/"

EMAIL_HOST = ''
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

FACEBOOK_API_KEY = ""
FACEBOOK_API_SECRET = ""

FLICKR_API_KEY = ""
FLICKR_API_SECRET = ""

AWS_ACCESS_KEY = '0VBD182JB5E9N26RJ9G2'
AWS_SECRET_ACCESS_KEY = 'rUJIqcTliXQHLwPDIOevGpAIIt9OEtvG3lVuKGsB'

S3_BUCKET_CSS = "css"
S3_BUCKET_STATIC = "static"
S3_BUCKET_AUDIO = "audio"
S3_BUCKET_UPLOAD = "upload"
S3_BUCKET_THUMB = "thumb"
S3_BUCKET_TUTORIAL = "tutorial"

S3_BUCKETS = {
    "avatar" : "avatar.localhost.flowgram.com",
    S3_BUCKET_THUMB : "thumb.localhost.flowgram.com",
    S3_BUCKET_STATIC : "static.localhost.flowgram.com",
    S3_BUCKET_UPLOAD : "upload.localhost.flowgram.com",
    S3_BUCKET_AUDIO : "audio.localhost.flowgram.com",
    S3_BUCKET_CSS : "css.localhost.flowgram.com",
    S3_BUCKET_TUTORIAL : "tutorial.localhost.flowgram.com",
}

S3_BACKUP_DIR = ""

POWERPOINT_SERVER = "localhost:8000/powerpoint"
POWERPOINT_DIR = ""

HYPER_ESTRAIER_DB_PATH = ""

VIDEO = {
    'default_font_file': '',
    'ffmpeg_path': '',
    'delete_temp_files': True,
}

FEATURE = {
    'use_regcode': False,
    'required_login_browse': False,
    'use_HEsearch' : False,
    'subscriptions_fw': True,
    'notify_fw': True,
    'send_to_details': True,
}

fg_INTERNAL_IPS = ['127.0.0.1']
