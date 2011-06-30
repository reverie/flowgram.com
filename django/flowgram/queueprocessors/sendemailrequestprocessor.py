import datetime, os, time
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage, SMTPConnection
from flowgram.core.models import SendEmailRequest, StatusCode
from flowgram.queueprocessors.queueprocessor import QueueProcessor

MAX_ATTEMPTS = 2
RETRY_TIME = datetime.timedelta(seconds=300)

TIME_TO_SLEEP = 30

# TODO(westphal): Handle circular references.
class SendEmailRequestProcessor(QueueProcessor):
    def fetch(self):
        # If the queue size is large enough
        if self.queue.qsize() > 0:
            time.sleep(TIME_TO_SLEEP)
            return

        tasksUnprocessed = SendEmailRequest.objects.filter(status_code=StatusCode.UNPROCESSED)
        tasksProcessing = SendEmailRequest.objects.filter(status_code=StatusCode.PROCESSING)

        tasksTimedOut = tasksProcessing.filter(started_at__lte=datetime.datetime.now() - RETRY_TIME)
        
        tasks = tasksUnprocessed | tasksTimedOut
        tasks = tasks[:60]
        
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
            if not task.altContent:
                connection = SMTPConnection(username=None, password=None, fail_silently=False)
                EmailMessage(task.subject,
                             task.content,
                             '"%s" <noreply@notify.flowgram.com>' % (task.fromAddress),
                             [task.toAddress],
                             connection=connection,
                             headers={
                                'Reply-To': task.fromAddress
                             }).send()
                #send_mail(task.subject, task.content, task.fromAddress, [task.toAddress])
            else:
                email = EmailMultiAlternatives(task.subject,
                                               task.content,
                                               '"%s" <noreply@notify.flowgram.com>' % (task.fromAddress),
                                               [task.toAddress],
                                               headers={
                                                   'Reply-To': task.fromAddress
                                               })
                email.attach_alternative(task.altContent, task.altContentType or 'text/html')
                email.send()

            task.status_code = StatusCode.DONE
            task.save()

            success = True
        except:
            print("Failed attempt to send email to: %s" % task.toAddress)
        finally:
            if not success:
                if task.attempts >= MAX_ATTEMPTS:
                    task.status_code = StatusCode.ERROR
                    task.save()

def add_to_mail_queue(fromAddress, toAddress, subject, content, altContent='', altContentType=''):
    SendEmailRequest.objects.create(fromAddress=fromAddress,
                                    toAddress=toAddress,
                                    subject=subject,
                                    content=content,
                                    altContent=altContent,
                                    altContentType=altContentType)
