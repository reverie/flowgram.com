DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'fg_beta'             # Or path to database file if using sqlite3.
DATABASE_USER = 'fg_dev'             # Not used with sqlite3.
DATABASE_PASSWORD = 'qwe[poi'         # Not used with sqlite3.
DATABASE_HOST = 'dev3.flowgram.com'             # NEW INTERNAL IP
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
DATABASE_HOST_BLOG = 'dev3.flowgram.com'

MASTER_DOMAIN_NAME = 'www.flowgram.com'

# Avatars will go in the "avatars" subdirectory of this:"
MEDIA_ROOT = '/var/apps/website/mfs1.sat/uploads/'

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
SECRET_KEY = '1ietHiAQoufrIeV13broatHLespIAxiexIejlafLuTrOa6RLuMiahlujLusLedIa'

my_BASE_DIR = '/var/apps/website/mfs1.sat/current/django/'
my_UPLOADS_DIR = '/var/apps/website/mfs1.sat/uploads/'
my_SOURCE_BASE_DIR = '/var/apps/website/mfs1.sat/current/django_source/'
FMS_STREAM_DIR = "/usa/sat/mfs1/streams/_definst_/" + MASTER_DOMAIN_NAME

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
my_DEV_STATIC_FLEX_MEDIA = '/var/apps/flexclient2/mfs1.sat/current/public/'

my_WOWKASTDIR = my_UPLOADS_DIR + 'fgrams/'
PROCESSED_AUDIO_DIR = my_UPLOADS_DIR + "processed_audio/"

fg_LOG_DIR = '/var/apps/website/mfs1.sat/shared/log/'
my_UPLOAD_LOG = my_BASE_DIR + 'upload_log.txt'
my_DEV_ERRORLOGDIR = my_BASE_DIR + 'errors/'

fg_DOWN_FOR_MAINTENANCE = False

CACHE_MIDDLEWARE_KEY_PREFIX = 'b'
CACHE_BACKEND = "memcached://127.0.0.1:11211/"

EMAIL_HOST = 'relayi.sat.flowgram.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

FACEBOOK_API_KEY = "64d1aca0625814a88524b670cfe77af7"
FACEBOOK_API_SECRET = "b1c7a9f82fb5302005eb464f928abdc6"

FLICKR_API_KEY = "0b7888e81663a529958bbe8fae371f33"
FLICKR_API_SECRET = "d64dad47a679cc44"

AWS_ACCESS_KEY = '0VBD182JB5E9N26RJ9G2'
AWS_SECRET_ACCESS_KEY = 'rUJIqcTliXQHLwPDIOevGpAIIt9OEtvG3lVuKGsB'

S3_BUCKET_CSS = "css"
S3_BUCKET_STATIC = "static"
S3_BUCKET_AUDIO = "audio"
S3_BUCKET_UPLOAD = "upload"
S3_BUCKET_THUMB = "thumb"
S3_BUCKET_TUTORIAL = "tutorial"

S3_BUCKETS = {
    "avatar" : "avatar.flowgram.com",
    S3_BUCKET_THUMB : "thumb.flowgram.com",
    S3_BUCKET_STATIC : "static.flowgram.com",
    S3_BUCKET_UPLOAD : "upload.flowgram.com",
    S3_BUCKET_AUDIO : "audio.flowgram.com",
    S3_BUCKET_CSS : "css.flowgram.com",
    S3_BUCKET_TUTORIAL : "tutorial.flowgram.com",
}

S3_BACKUP_DIR = "/usa/sat/mfs1/s3backup"

POWERPOINT_SERVER = "ppt.flowgram.com"
POWERPOINT_DIR = ""

HYPER_ESTRAIER_DB_PATH = "/var/apps/website/mfs1.sat/shared/casket"

VIDEO = {
    'default_font_file': '/var/apps/website/mfs1.sat/current/django/flowgram/core/exporters/video/Arial.ttf',
    'ffmpeg_path': '/usr/bin/ffmpeg',
    'delete_temp_files': True,
}

FEATURE = {
    'use_regcode': False,
    'required_login_browse': False,
    'use_HEsearch' : True,
    'subscriptions_fw': True,
    'notify_fw': True,  
    'send_to_details': True,  
}

fg_INTERNAL_IPS = ['127.0.0.1',
                   '72.51.34.36', # dev3
                   '66.135.44.133', # mfs1.sat
                   '66.135.44.134', # mfs2.sat
                   '66.135.44.135', # mfs3.sat
                   '66.135.44.137', # beta.sat
                   '66.135.44.138', # winmfs1.sat
                   '66.135.44.139', # winmfs2.dev.sat
                   '67.207.118.34', # wiline
                   '75.101.132.3', # ec2 instance ip 1
                   '75.101.141.238', # ec2 instance ip 2
                   '75.101.162.12', # ec2 instance ip 3
                   '75.101.167.137', # ec2 instance ip 4
                   ]
