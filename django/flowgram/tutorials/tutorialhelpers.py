import time, datetime, os
from django.http import Http404
from django.conf import settings
from flowgram import localsettings
from flowgram.core import log, s3

def now():
    return int(time.mktime(datetime.datetime.now().timetuple()))

def save_uploaded_video(request, tutorial, form):
    
    if not request.FILES:
        return
        
    file = request.FILES['video']
    video = file['content']
    content_type = file['content-type']
    prefix = 'tutorial'
    if form.cleaned_data["filename_prefix"]:
        prefix = prefix + '_' + form.cleaned_data["filename_prefix"]
    filename = "%s_%s.flv" % (prefix, str(now()))
    f = open(localsettings.INTERNAL_MEDIA_ROOT + filename, 'wb')
    f.write(video)
    f.close()
    
    s3.save_file_to_bucket(localsettings.S3_BUCKET_STATIC,
                           filename,
                           open(localsettings.INTERNAL_MEDIA_ROOT + filename),
                           'public-read',
                           content_type)
    
    os.remove(localsettings.INTERNAL_MEDIA_ROOT + filename)

    tutorial.video_path = filename
    tutorial.save()

def get_tutorial_video_path(tutorial):
    
    video_path = 'http://' + localsettings.S3_BUCKETS[localsettings.S3_BUCKET_STATIC] + '/' + tutorial.video_path
    
    return video_path
    
    