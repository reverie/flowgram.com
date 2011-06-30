DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'fg_dev'             # Or path to database file if using sqlite3.
DATABASE_USER = 'fg_dev'             # Not used with sqlite3.
DATABASE_PASSWORD = 'qwe[poi'         # Not used with sqlite3.
DATABASE_HOST = 'db.flowgram.com'             # NEW INTERNAL IP
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
DATABASE_HOST_BLOG = '192.168.100.36'

MASTER_DOMAIN_NAME = 'dev.flowgram.com'

# Avatars will go in the "avatars" subdirectory of this:"
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
SECRET_KEY = '32@#5jdksl@#jds0jk3l2F@sdijkljl235@#'

my_BASE_DIR = '/var/apps/website/dev3/current/django/'
my_UPLOADS_DIR = '/var/apps/website/dev3/uploads/'
my_SOURCE_BASE_DIR = '/var/apps/website/dev3/current/django_source/'
FMS_STREAM_DIR = "/opt/macromedia/fms/applications/flowgram/streams/_definst_/" + MASTER_DOMAIN_NAME

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    my_BASE_DIR + 'templates/',
)

my_URL_BASE = 'http://' + MASTER_DOMAIN_NAME + '/'
fg_DEFAULT_AVATAR_URL = MEDIA_URL + '/images/default_avatar.gif'

my_DEV_STATIC_MEDIA = my_BASE_DIR + 'static/'
my_DEV_STATIC_ADMIN_MEDIA = my_SOURCE_BASE_DIR + 'django/contrib/admin/media/'
my_DEV_STATIC_FLEX_MEDIA = '/dev/null'

my_WOWKASTDIR = my_UPLOADS_DIR + 'fgrams/'
PROCESSED_AUDIO_DIR = my_UPLOADS_DIR + "processed_audio/"

fg_LOG_DIR = '/var/apps/website/dev3/shared/log/'
my_UPLOAD_LOG = my_BASE_DIR + 'upload_log.txt' 
my_DEV_ERRORLOGDIR = my_BASE_DIR + 'errors/'

fg_DOWN_FOR_MAINTENANCE = False

#CACHE_MIDDLEWARE_KEY_PREFIX = 'd'
#CACHE_BACKEND = "memcached://127.0.0.1:11211/"

EMAIL_HOST = 'mail.wowkast.dreamhosters.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'topadmin'
EMAIL_HOST_PASSWORD = 'VkCg6PUD'

FACEBOOK_API_KEY = "b8ba2f0b8e9141ab260b65cc6547c86c"
FACEBOOK_API_SECRET = "631b9d675a714883d95997634a18ade9"

FLICKR_API_KEY = "a88902bbaacc895430f343c2d52bc9b0"
FLICKR_API_SECRET = "c8dd2e7c00d63fb9"

AWS_ACCESS_KEY = '0VBD182JB5E9N26RJ9G2'
AWS_SECRET_ACCESS_KEY = 'rUJIqcTliXQHLwPDIOevGpAIIt9OEtvG3lVuKGsB'

S3_BUCKET_CSS = "css"
S3_BUCKET_STATIC = "static"
S3_BUCKET_AUDIO = "audio"
S3_BUCKET_UPLOAD = "upload"
S3_BUCKET_THUMB = "thumb"
S3_BUCKET_TUTORIAL = "tutorial"

S3_BUCKETS = {
    "avatar" : "avatar.dev.flowgram.com",
    S3_BUCKET_THUMB : "thumb.dev.flowgram.com",
    S3_BUCKET_STATIC : "static.dev.flowgram.com",
    S3_BUCKET_UPLOAD : "upload.dev.flowgram.com",
    S3_BUCKET_AUDIO : "audio.dev.flowgram.com",
    S3_BUCKET_CSS : "css.dev.flowgram.com",
    S3_BUCKET_TUTORIAL : "tutorial.dev.flowgram.com",
}

S3_BACKUP_DIR = "/s3backup"

POWERPOINT_SERVER = "ppt.dev.flowgram.com"
POWERPOINT_DIR = ""

HYPER_ESTRAIER_DB_PATH = ""

VIDEO = {
    'default_font_file': None,
    'ffmpeg_path': None,
    'delete_temp_files': True,
}

FEATURE = {
    'use_regcode': True,
    'required_login_browse': True,
    'use_HEsearch' : False,
    'subscriptions_fw': True,
    'notify_fw': True, 
    'send_to_details': True,   
}

fg_INTERNAL_IPS = ['127.0.0.1',
                   '72.51.34.36', # dev3
                   '74.211.197.14', # DSL speakeasy
                   '67.207.118.34', # wiline
                   '66.135.44.139' # winmfs2.dev.sat.flowgram.com
                   ]
