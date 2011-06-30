from django.db import models

# Create your models here.

class Category(models.Model):
    position = models.FloatField(default=0.0)
    title = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.title
    class Admin:
        list_display = ('title', 'position', 'created_at')
        search_fields = ['title']
    class Meta:
        ordering = ['position']

class Question(models.Model):
    position = models.FloatField(default=0.0)
    title = models.CharField(max_length=1024)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category)
    def __unicode__(self):
        return self.title
    class Admin:
        list_display = ('title', 'position', 'created_at')
        search_fields = ['title', 'answer']
        list_filter = ('category',)
    class Meta:
        ordering = ['position']