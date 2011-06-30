import datetime, os, re, socket, time

from flowgram.core import s3
from flowgram.core.models import UploadToYouTubeRequest, StatusCode
from flowgram.queueprocessors.queueprocessor import QueueProcessor
from flowgram import localsettings
from flowgram.core.exporters.video import uploadtoyoutube

MAX_ATTEMPTS = 2
RETRY_TIME = datetime.timedelta(seconds=900)

TIME_TO_SLEEP = 60

class UploadToYouTubeRequestProcessor(QueueProcessor):
    def __init__(self):
        socket.setdefaulttimeout(90)
        QueueProcessor.__init__(self)

    def fetch(self):
        # If the queue size is large enough
        if self.queue.qsize() > 0:
            time.sleep(TIME_TO_SLEEP)
            return
            
        tasksUnprocessed = UploadToYouTubeRequest.objects.filter(status_code=StatusCode.UNPROCESSED)
        tasksProcessing = UploadToYouTubeRequest.objects.filter(status_code=StatusCode.PROCESSING)

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
        try:
            uploadtoyoutube.upload(task.token,
                                   '%srendered_video/%s.wmv' % (localsettings.MEDIA_ROOT,
                                                                task.export_to_video_request.id),
                                   task.flowgram,
                                   task.title,
                                   task.description,
                                   task.keywords,
                                   task.category,
                                   task.private)

            task.status_code = StatusCode.DONE
            task.save()

            success = True
        except Exception, e:
            print e
            print("Failed attempt to upload Flowgram video to YouTube: %s" % task.flowgram.id)
        finally:
            if not success:
                if task.attempts >= MAX_ATTEMPTS:
                    # TODO(westphal): Add some type of user notification here.

                    task.status_code = StatusCode.ERROR
                    task.save()
