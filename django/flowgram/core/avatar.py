import Image, time, datetime, cStringIO

from django.http import Http404
from django.conf import settings

from flowgram.localsettings import my_URL_BASE
from flowgram.core import log, s3

BUILTIN_AVATARS = ['anne', 'apple', 'badr', 'balloon', 'ben', 'buildingrainbow', 
                   'bulb', 'candy', 'cyap', 'gobaudd', 'jets', 'snowmtn', 'sunglasses', 'sunkiss', 
                   'trail', 'vegas', 'waterblueblack', 'waterfall', 'waterhill', 'waterrainbow', 
                   'willow']
SIZES = (25, 32, 100, 200)

EXTENSION = 'jpg'

def now():
    return int(time.mktime(datetime.datetime.now().timetuple()))

def builtin_avatar_url(name, size):
    #print "builtin_avatar_url called"
    if size not in SIZES: raise Http404
    return '/media/images/avatars/%s-%d.%s' % (name, size, EXTENSION)    

def get_url(profile, size):
    if size not in SIZES: raise Http404
    
    if profile.avatar_builtin:
        return builtin_avatar_url(profile.avatar, size)
    
    base = profile.avatar.replace('\\', '/')
    filename = "%s_%s.%s" % (base.split('/')[-1], size, EXTENSION)
    url = s3.get_url_from_bucket("avatar", filename)
    
    return url

def middle_square(size):
    width, height = size
    length = min(size)
    offset = int((max(size)-length)/2.0)
    if width >= height:
        return (offset, 0, offset+length, length)
    return (0, offset, length, offset+length)  

def make_upload_thumbnails(filename, data):
    dataIO = cStringIO.StringIO(data)
    
    orig = Image.open(dataIO)
    orig = orig.crop(middle_square(orig.size))
    
    for size in SIZES:
        thumb = orig.resize((size, size), Image.ANTIALIAS)
        if thumb.mode != "RGB":
            thumb = thumb.convert("RGB")
            
        new_filename = "%s_%d.%s" % (filename, size, EXTENSION)
        new_file = cStringIO.StringIO()
        thumb.save(new_file, "jpeg", quality=95)
        new_file.seek(0)
        
        s3.save_string_to_bucket("avatar", new_filename, new_file.read())
        
        new_file.close()
    
    dataIO.close()
        
def save_uploaded_avatar(profile, avatar_form):
    avatar_upload = avatar_form.cleaned_data["avatar"]
    
    filename = "%d_%d" % (profile.user.id , now())
    s3.save_string_to_bucket("avatar", filename, avatar_upload.content)
    
    make_upload_thumbnails(filename, avatar_upload.content)
    
    profile.avatar = filename
    profile.avatar_filetype = EXTENSION
    profile.avatar_builtin = False
    profile.save()
    
def make_builtin_thumbnails(name):
    from localsettings import my_DEV_STATIC_MEDIA
    base_dir = my_DEV_STATIC_MEDIA + '/images/avatars/'
    path = base_dir + name + '.' + EXTENSION
    orig = Image.open(path)
    for size in SIZES:
        thumb = orig.resize((size, size), Image.ANTIALIAS)
        new_filename = "%s-%d.%s" % (name, size, EXTENSION)
        new_location = base_dir + new_filename
        thumb.save(new_location, "jpeg", quality=95)
    
def save_builtin_avatar(profile, name):
    if not name in BUILTIN_AVATARS:
        log.critical("Tried to save unknown avatar %s to %'s profile" % (name, profile.user))
        return
    profile.avatar = name
    profile.avatar_builtin = True
    profile.save()
    