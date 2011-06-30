from django.conf import settings
from django.db import models
from flowgram.core.models import Flowgram
from django.contrib.auth.models import User
from flowgram.localsettings import my_URL_BASE as URL_BASE

VIEW_METHOD_CHOICES = [('', ''),
                        ('IET', 'Internet Explorer Toolbar'), 
                        ('F0D', 'Flex Zero-Download Player'),]

# Create your models here.
class ShareLink(models.Model):
    name=models.CharField(max_length=8, unique=True)
    flowgram=models.ForeignKey(Flowgram)
    sender=models.ForeignKey(User, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    recipient = models.EmailField()
    clicks = models.IntegerField(default=0)
    def url(self):
        return URL_BASE + ("fgshare/%s/" % self.name)
    class Admin:
        list_display = ('name', 'flowgram', 'sender', 'created_at', 'recipient', 'clicks')
    class Meta:
        app_label = 'core'
        db_table = 'logging_sharelink'

class View(models.Model):
    flowgram_id = models.CharField(max_length=settings.ID_FIELD_LENGTH)
    user_id = models.CharField(max_length=settings.ID_FIELD_LENGTH, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=3, choices=VIEW_METHOD_CHOICES)
    
    class Admin:
        pass
    
    def __unicode__(self):
        return "%s views %s at %s" % (self.user, self.flowgram, self.time)
    
    class Meta:
        app_label = 'core'
        db_table = 'logging_view'

class Feedback(models.Model):
    url = models.TextField()
    email = models.TextField()
    sys_info = models.TextField()
    comments = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    class Admin:
        pass
    def __unicode__(self):
        return "Feedback from %s at %s" % (self.email, self.sent_at)
    class Meta:
        app_label = 'core'
        db_table = 'logging_feedback'
