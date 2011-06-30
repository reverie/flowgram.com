import boto, tempfile, os, shutil

from django.http import HttpResponseRedirect

from flowgram import localsettings
from flowgram.core import helpers

def save_string_to_bucket(bucket_short_name, key_name, contents, acl='public-read', content_type='text/plain'):
    if bucket_short_name not in localsettings.S3_BUCKETS:
        raise NameError, bucket_short_name + ' is an invalid bucket.'
    
    bucket_name = localsettings.S3_BUCKETS[bucket_short_name]
    
    conn = boto.connect_s3(localsettings.AWS_ACCESS_KEY, localsettings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucket_name)
    key = bucket.new_key(key_name)
    
    key.set_contents_from_string(contents, headers={'Content-Type': content_type})
    key.set_acl(acl)
    
    backup_string(bucket_name, key_name, contents)

def save_file_to_bucket(bucket_short_name, key_name, file, acl='public-read', content_type=None):
    if not bucket_short_name in localsettings.S3_BUCKETS:
        raise NameError, bucket_short_name + ' is an invalid bucket.'
    
    bucket_name = localsettings.S3_BUCKETS[bucket_short_name]
    
    conn = boto.connect_s3(localsettings.AWS_ACCESS_KEY, localsettings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucket_name)
    key = bucket.new_key(key_name)
    
    headers_ = None
    if content_type:
        headers_ = {'Content-Type': content_type}
    
    key.set_contents_from_file(file, headers = headers_)
    key.set_acl(acl)
    
    backup_file(bucket_name, key_name, file)
    
def save_filename_to_bucket(bucket_short_name, key_name, filename, acl='public-read', content_type=None):
    if not bucket_short_name in localsettings.S3_BUCKETS:
        raise NameError, bucket_short_name + ' is an invalid bucket.'
    
    bucket_name = localsettings.S3_BUCKETS[bucket_short_name]
    
    conn = boto.connect_s3(localsettings.AWS_ACCESS_KEY, localsettings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucket_name)
    key = bucket.new_key(key_name)
    
    headers_ = None
    if content_type:
        headers_ = {'Content-Type': content_type}
    
    key.set_contents_from_filename(filename, headers = headers_)
    key.set_acl(acl)
    
    backup_filename(bucket_name, key_name, filename)
    
def get_file_from_bucket(bucket_short_name, key_name, file):
    if not bucket_short_name in localsettings.S3_BUCKETS:
        raise NameError, bucket_short_name + ' is an invalid bucket.'
    
    bucket_name = localsettings.S3_BUCKETS[bucket_short_name]
    
    conn = boto.connect_s3(localsettings.AWS_ACCESS_KEY, localsettings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucket_name)
    key = bucket.get_key(key_name)
    
    if key is None:
        raise NameError, key_name + ' is an invalid key.'
    
    key.get_contents_to_file(file)
    
def copy(src_bucket_short_name, src_key_name, dest_bucket_short_name, dest_key_name, acl='public-read'):
    temp_file = tempfile.mkstemp()
    fd = temp_file[0]
    path = temp_file[1]
    
    file = os.fdopen(fd, "w+b")
    
    get_file_from_bucket(src_bucket_short_name, src_key_name, file)
    
    file.seek(0)
    save_file_to_bucket(dest_bucket_short_name, dest_key_name, file, acl)
    
    file.close()
    
    os.remove(path)
    
def get_url_from_bucket(bucket_short_name, key_name):
    if not bucket_short_name in localsettings.S3_BUCKETS:
        raise NameError, bucket_short_name + ' is an invalid bucket.'
    
    return 'http://%s/%s' % (localsettings.S3_BUCKETS[bucket_short_name], key_name)

def redirect_to_key(bucket_short_name, key_name):
    if not bucket_short_name in localsettings.S3_BUCKETS:
        raise NameError, bucket_short_name + ' is an invalid bucket.'

    return HttpResponseRedirect(get_url_from_bucket(bucket_short_name, key_name))

def backup_string(bucket_name, key_name, contents):
    if localsettings.S3_BACKUP_DIR == "":
        return

    path = localsettings.S3_BACKUP_DIR + "/" + bucket_name + "/"
    if len(key_name) > 4:
        path += helpers.get_id_subdir_path(key_name) + "/"
        
    path += key_name
    dir = os.path.dirname(path)
    helpers._mkdir(dir)
    
    f = open(path, "wb")
    f.write(contents)
    f.close()
    
def backup_file(bucket_name, key_name, file):
    if localsettings.S3_BACKUP_DIR == "":
        return

    path = localsettings.S3_BACKUP_DIR + "/" + bucket_name + "/"
    if len(key_name) > 4:
        path += helpers.get_id_subdir_path(key_name) + "/"
        
    path += key_name
    dir = os.path.dirname(path)
    helpers._mkdir(dir)
    
    destfile = open(path, "wb")
    
    file.seek(0)
    shutil.copyfileobj(file, destfile)
    file.seek(0)
    
    destfile.close()
    
def backup_filename(bucket_name, key_name, filename):
    if localsettings.S3_BACKUP_DIR == "":
        return

    path = localsettings.S3_BACKUP_DIR + "/" + bucket_name + "/"
    if len(key_name) > 4:
        path += helpers.get_id_subdir_path(key_name) + "/"
        
    path += key_name
    dir = os.path.dirname(path)
    helpers._mkdir(dir)
    
    shutil.copyfile(filename, path)