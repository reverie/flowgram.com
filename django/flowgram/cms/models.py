from django.db import models

# Create your models here.

class CmsPage(models.Model):
    urlpath = models.CharField(max_length=100)
    titletag = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    class Admin:
        pass
    def __unicode__(self):
        return self.urlpath