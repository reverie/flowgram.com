import datetime, os, re, urllib2, socket, time

from flowgram.core.models import EmailDigestRecord, UserProfile
from flowgram.queueprocessors.queueprocessor import QueueProcessor
from flowgram.core import newsfeed
from flowgram import localsettings
from flowgram.queueprocessors.sendemailrequestprocessor import add_to_mail_queue

MAX_ATTEMPTS = 1

class EmailDigestProcessor(QueueProcessor):
    def __init__(self):
        socket.setdefaulttimeout(90)
        QueueProcessor.__init__(self)

    def fetch(self):
        user_profiles = UserProfile.objects.filter(notify_by_email=True).exclude(notification_freq='')
        print("got %d user profiles" % len(user_profiles))
            
        for user_profile in user_profiles:
            user = user_profile.user
            email_digest_record = None
            now = datetime.datetime.now()
            timestamp = None
            try:
                email_digest_record = EmailDigestRecord.objects.get(user=user)

                timestamp = now
                if user_profile.notification_freq == 'I':
                    timestamp -= datetime.timedelta(seconds=600)
                elif user_profile.notification_freq == 'D':
                    timestamp -= datetime.timedelta(seconds=86400)
                elif user_profile.notification_freq == 'W':
                    timestamp -= datetime.timedelta(seconds=604800)

                if email_digest_record.timestamp > timestamp:
                    continue

                timestamp = email_digest_record.timestamp

                email_digest_record.timestamp = now
                email_digest_record.save()
                
                print("user=%s has timestamp=%s" % (user.id, str(now)))
            except:
                EmailDigestRecord.objects.create(user=user, timestamp=now)
                print("user=%s had no EmailDigestRecord so made one with timetsamp=%s" % (user.id, str(now)))

            content = newsfeed.get_rendered_news_feed(user, user, 'E', timestamp)
            if content:
                print("sending email to %s" % user.id)
                
                add_to_mail_queue(
                    'mailman@flowgram.com',
                    user.email,
                    '[Flowgram] Your subscription updates',
                    '',
                    content,
                    'text/html')
        
        time.sleep(600)
            
    def process(self, task):
        pass
