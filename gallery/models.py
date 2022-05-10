from django.db import models
from django.core.exceptions import ValidationError




class Gallery(models.Model):
    galleryname = models.TextField()
    location = models.TextField()
    description = models.TextField()
    galleryurl = models.TextField()
    website = models.TextField()
    coverimage = models.TextField()
    gallerytype = models.CharField(max_length=255, null=False, blank=False)
    slug = models.CharField(max_length=255, blank=True, default='')
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Galleries Information Table"
        db_table = 'galleries'
        ordering = ('priority',)

    def __unicode__(self):
        return "%s"%(self.galleryname)



class Event(models.Model):
    eventname = models.CharField(max_length=255, blank=False)
    eventurl = models.TextField()
    eventinfo = models.TextField()
    eventtype = models.CharField(max_length=20, blank=True, default='')
    eventstatus = models.CharField(max_length=15, blank=True, default='')
    eventperiod = models.CharField(max_length=255, blank=True, default='')
    eventstartdate = models.DateTimeField()
    eventenddate = models.DateTimeField()
    artworkscount = models.IntegerField()
    gallery = models.ForeignKey(Gallery, blank=False, null=False, on_delete=models.CASCADE)
    eventimage = models.TextField()
    eventlocation = models.CharField(max_length=200, blank=True, default='')
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Events Information Table"
        db_table = 'events'
        ordering = ('priority',)

    def __unicode__(self):
        return "%s"%(self.eventname)







