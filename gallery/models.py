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
        ordering = ('-priority',)

    def __unicode__(self):
        return "%s"%(self.galleryname)



class Event(models.Model):
    eventname = models.CharField(max_length=255, blank=False)
    eventurl = models.TextField()
    eventinfo = models.TextField()
    eventtype = models.CharField(max_length=20, blank=True, default='')
    eventstatus = models.CharField(max_length=15, blank=True, default='')
    eventperiod = models.CharField(max_length=255, blank=True, default='')
    artworkscount = models.IntegerField()
    gallery = models.ForeignKey(Gallery, blank=False, null=False, on_delete=models.CASCADE)
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Events Information Table"
        db_table = 'events'
        ordering = ('-priority',)

    def __unicode__(self):
        return "%s"%(self.eventname)



class Artist(models.Model):
    artistname = models.CharField(max_length=255, blank=False, null=False)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    birthdate = models.CharField(max_length=30, blank=True, null=True)
    deathdate = models.CharField(max_length=10, blank=True, null=True)
    about = models.TextField()
    profileurl = models.TextField()
    gender = models.CharField(max_length=10, blank=True, null=True)
    slug = models.CharField(max_length=255, blank=True, null=True)
    squareimage = models.TextField()
    largeimage = models.TextField()
    edges = models.TextField()
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Artists Information Table"
        db_table = 'artists'
        ordering = ('-priority',)

    def __unicode__(self):
        return "%s"%(self.artistname)


class Artwork(models.Model):
    artworkname = models.TextField()
    creationdate = models.CharField(max_length=10, blank=True, null=True)
    gallery = models.ForeignKey(Gallery, blank=False, null=False, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE)
    artistname = models.CharField(max_length=255, blank=True, null=True)
    artistbirthyear = models.CharField(max_length=4, blank=True, null=True)
    artistdeathyear = models.CharField(max_length=4, blank=True, null=True)
    artistnationality = models.CharField(max_length=4, blank=True, null=True)
    size = models.CharField(max_length=255, blank=True, null=True)
    estimate = models.CharField(max_length=100, blank=True, null=True)
    soldprice = models.CharField(max_length=40, blank=True, null=True)
    medium = models.TextField()
    signature = models.TextField()
    letterofauthenticity = models.TextField()
    description = models.TextField()
    provenance = models.TextField()
    literature = models.TextField()
    exhibitions = models.TextField()
    priority = models.IntegerField(default=0)
    image1 = models.TextField()
    image2 = models.TextField()
    image3 = models.TextField()
    image4 = models.TextField()
    workurl = models.TextField()
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Artworks Information Table"
        db_table = 'artworks'
        ordering = ('-priority',)

    def __unicode__(self):
        return "%s"%(self.artworkname)



