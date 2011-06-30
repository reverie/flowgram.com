import datetime, os, re, urllib2, socket, time, sys, traceback, tempfile, shutil

from django.contrib.auth import models as auth_models
from flowgram.core import s3, helpers
from flowgram.core.api.views import get_fg_thumb_by_dims
from flowgram.core.exporters.video.flowgram2video import Flowgram2Video
from flowgram.core.models import ExportToVideoRequest, StatusCode
from flowgram.queueprocessors.queueprocessor import QueueProcessor
from flowgram.queueprocessors.sendemailrequestprocessor import add_to_mail_queue
from flowgram import localsettings
from django.template import loader, Context

MAX_ATTEMPTS = 2
RETRY_TIME = datetime.timedelta(seconds=900)

TIME_TO_SLEEP = 10

ANONYMOUS_USERNAME = 'AnonymousUser'
ANONYMOUS_USER_OBJECT = auth_models.User.objects.get_or_create(username=ANONYMOUS_USERNAME)[0]

class ExportToVideoRequestProcessor(QueueProcessor):
    def __init__(self):
        socket.setdefaulttimeout(90)
        QueueProcessor.__init__(self)

    def fetch(self):
        # If the queue size is large enough
        if self.queue.qsize() > 0:
            time.sleep(TIME_TO_SLEEP)
            return
            
        tasksUnprocessed = ExportToVideoRequest.objects.filter(status_code=StatusCode.UNPROCESSED)
        tasksProcessing = ExportToVideoRequest.objects.filter(status_code=StatusCode.PROCESSING)

        tasksTimedOut = tasksProcessing.filter(started_at__lte=datetime.datetime.now() - RETRY_TIME)

        tasks = tasksUnprocessed | tasksTimedOut
        tasks = tasks[:10]
        
        for task in tasks:
            print("queuing %s" % task.id)
            task.status_code = StatusCode.PROCESSING
            task.started_at = datetime.datetime.now()
            task.save()
            
            self.queue.put(task)
        
        if len(tasks) == 0:
            time.sleep(TIME_TO_SLEEP)
            
    def process(self, task):
        print("processing %s" % task.id)
        
        task.attempts += 1
        task.started_at = datetime.datetime.now()
        task.save()

        success = False
        title = task.flowgram.title or 'Untitled'
        
        try:
            output_dir = tempfile.mkdtemp("", "", os.path.join(tempfile.gettempdir(), "exporttovideo")) + os.sep
            print("output_dir = %s" % output_dir)
            
            if os.path.isdir(output_dir):
                shutil.rmtree(output_dir)

            helpers._mkdir(output_dir)

            # Rendering the video.
            Flowgram2Video().run(task.flowgram.id,
                                 640,
                                 480,
                                 output_dir,
                                 task.use_highlight_popups)
            copy_to_uploads_directory(task, '%svideo.wmv' % output_dir)
            save_video_file_to_s3(task, '%svideo.wmv' % output_dir)

            # Closing out, and notifying corresponding users, open requests for the same video and
            # options.
            similar_tasks = ExportToVideoRequest.objects.filter(
                flowgram=task.flowgram,
                use_highlight_popups=task.use_highlight_popups,
                status_code__in=(StatusCode.UNPROCESSED, StatusCode.PROCESSING))
            for close_task in similar_tasks:
                preview_url = 'http://%s/%s.wmv' % \
                    (localsettings.S3_BUCKETS[localsettings.S3_BUCKET_UPLOAD], task.id)
                export_url = '%sexport/youtube/%s/' % (localsettings.my_URL_BASE, task.id)
                recipient = close_task.request_user.username \
                    if close_task.request_user \
                    else ''
                subject = 'Your Flowgram Video is now ready'
                template = loader.get_template('emails/video_export.html')
                context = Context({'recipient': recipient,
                                   'recipient_url': localsettings.my_URL_BASE + recipient,
                                   'recipient_email': close_task.request_email,
                                   'title': title,
                                   'fg_url': '%sp/%s/' % (localsettings.my_URL_BASE, task.flowgram.id),
                                   'fg_owner': task.flowgram.owner,
                                   'fg_owner_url': '%s%s' % (localsettings.my_URL_BASE, task.flowgram.owner),
                                   'preview_url': preview_url,
                                   'export_url': export_url,
                                   'contact_us': localsettings.my_URL_BASE + 'about_us/contact_us/',
                                   'image_url': '%sapi/getthumbbydims/fg/%s/%d/%d/' % (localsettings.my_URL_BASE, task.flowgram.id, 150, 100)})
                print 'Notice: %sapi/getthumbbydims/fg/%s/%d/%d/' % (localsettings.my_URL_BASE, task.flowgram.id, 150, 100)
                html_content = template.render(context)
                add_to_mail_queue('mailman@flowgram.com',
                                  close_task.request_user.email \
                                      if close_task.request_user != ANONYMOUS_USER_OBJECT \
                                      else close_task.request_email,
                                  subject,
                                  '',
                                  html_content,
                                  'text/html')

                close_task.status_code = StatusCode.DONE
                close_task.save()

            success = True
        except:
            traceback.print_exc(file=sys.stdout)
            print("Failed attempt to encode video for Flowgram: %s" % task.flowgram.id)
        finally:
            if not success:
                if task.attempts >= MAX_ATTEMPTS:
                    add_to_mail_queue(
                        'mailman@flowgram.com',
                        task.request_user.email if task.request_user else task.request_user.email,
                        'Flowgram Video "%s" Processing Error' % (task.flowgram.title or 'Untitled'),
                        'The video of the Flowgram "%s" could not be processed at this time.  We have recorded this problem and will look into the cause.  Sorry for the inconvenience.' % \
                            title)

                    task.status_code = StatusCode.ERROR
                    task.save()

            if localsettings.VIDEO["delete_temp_files"]:
                shutil.rmtree(output_dir)


def copy_to_uploads_directory(task, file):
    from distutils import file_util
    file_util.copy_file(file, '%srendered_video/%s.wmv' % (localsettings.MEDIA_ROOT, task.id))


def save_video_file_to_s3(task, file):
    s3.save_file_to_bucket(localsettings.S3_BUCKET_UPLOAD,
                           '%s.wmv' % task.id,
                           open(file),
                           'public-read',
                           'video/x-ms-wmv')
    return "S3"
