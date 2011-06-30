from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class PageView(models.Model):
    view = models.CharField(max_length=40)
    url = models.CharField(max_length=300)
    referer = models.CharField(max_length=300, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True)
    ip = models.IPAddressField(null=True, blank=True)
    class Admin:
        list_display = ('url', 'user', 'time', 'referer', 'ip')
        list_filter = ['view']
        search_fields = ['url']
    def __unicode__(self):
        user = self.user if self.user else self.ip
        return "%s views %s" % (user, self.url)

class StatRecord(models.Model):
    type = models.CharField(max_length=32)
    referrer = models.CharField(max_length=1024)
    ip = models.IPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True)
    num_parameter = models.IntegerField(default=0)
    string_parameter = models.CharField(max_length=1024)
    class Admin:
        list_display = ('type',
                        'referrer',
                        'ip',
                        'timestamp',
                        'user',
                        'num_parameter',
                        'string_parameter')
