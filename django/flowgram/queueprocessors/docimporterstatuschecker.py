import os, re, urllib2, socket, time

from datetime import datetime, timedelta

from flowgram import localsettings
from flowgram.core import models
from flowgram.queueprocessors.queueprocessor import QueueProcessor
from flowgram.queueprocessors.sendemailrequestprocessor import add_to_mail_queue

# This is the retry time from pptprocessor.py.
RETRY_TIME = datetime.timedelta(seconds=900)

class DocImporterStatusChecker(QueueProcessor):
    def __init__(self):
        self.last_time = None
        self.last_count = 0

        socket.setdefaulttimeout(90)
        QueueProcessor.__init__(self)


    def fetch(self):
        tasksUnprocessed = models.PptImportRequest.objects.filter(status_code=models.StatusCode.UNPROCESSED).filter(uploaded_to_s3=True)
        tasksProcessing = models.PptImportRequest.objects.filter(status_code=models.StatusCode.PROCESSING)

        tasksTimedOut = tasksProcessing.filter(started_at__lte=datetime.now() - RETRY_TIME)
        
        tasks = tasksUnprocessed | tasksTimedOut

        if self.last_time:
            tasks = tasks.exclude(timestamp__gte=self.last_time)

        count = tasks.count()

        if self.last_time:
            if self.last_count <= count:
                add_to_mail_queue(
                    'mailman@flowgram.com',
                    'django.log@flowgram.com',
                    '[STATUS UPDATE] Doc Import Service - Slow/Not Working',
                    'Doc Import Service - Slow/Not Working\n\nSincerely,\n- Flowgram')
                
        self.last_time = datetime.now()
        self.last_count = count
        
        time.sleep(300)
            

    def process(self, task):
        pass
