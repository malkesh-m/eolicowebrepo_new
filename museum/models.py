from django.db import models
from django.core.exceptions import ValidationError

class Museum(models.Model):
    museumname = models.TextField()
    location = models.TextField()
    description = models.TextField()
    museumurl = models.TextField()
    coverimage = models.TextField()
    museumtype = models.CharField(max_length=255, blank=True, default='') # Classifies the museums as "Non-profit Organizations", "Artist Estates/Foundations" etc.
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Museums Information Table"
        db_table = 'museums'
        ordering = ('-priority',)

    def __unicode__(self):
        return "%s"%(self.museumname)



class MuseumEvent(models.Model):
    eventname = models.TextField()
    eventinfo = models.TextField()
    eventurl = models.TextField()
    museum = models.ForeignKey(Museum, blank=False, null=False, on_delete=models.CASCADE)
    eventperiod = models.CharField(max_length=255, blank=True, default='')
    eventstartdate = models.DateTimeField()
    eventenddate = models.DateTimeField()
    coverimage = models.TextField()
    eventstatus = models.CharField(max_length=20, blank=True, default='')
    eventtype = models.CharField(max_length=255, blank=True, default='') # Classifies the event as "Outdoor Art", "Non-western Art" etc.
    presenter = models.CharField(max_length=255, blank=True, default='')
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Museum Events Information Table"
        db_table = 'museumevents'
        ordering = ('-priority',)

    def __unicode__(self):
        return "%s"%(self.eventname)


class MuseumPieces(models.Model):
    piecename = models.TextField()
    creationdate = models.CharField(max_length=10, blank=True, default='')
    museum = models.ForeignKey(Museum, blank=False, null=False, on_delete=models.CASCADE)
    event = models.ForeignKey(MuseumEvent, blank=False, null=False, on_delete=models.CASCADE)
    artistname = models.CharField(max_length=255, blank=True, default='')
    artistbirthyear = models.CharField(max_length=4, blank=True, default='')
    artistdeathyear = models.CharField(max_length=4, blank=True, default='')
    artistnationality = models.CharField(max_length=200, blank=True, default='')
    medium = models.TextField()
    size = models.CharField(max_length=255, blank=True, default='')
    edition = models.CharField(max_length=255, blank=True, default='')
    signature = models.TextField()
    description = models.TextField()
    detailurl = models.TextField()
    provenance = models.TextField()
    literature = models.TextField()
    exhibited = models.TextField()
    status = models.CharField(max_length=40, blank=True, default='')
    image1 = models.TextField()
    image2 = models.TextField()
    image3 = models.TextField()
    image4 = models.TextField()
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Museum Pieces (artworks) Information Table"
        db_table = 'museumpieces'
        ordering = ('-priority',)

    def __unicode__(self):
        return "%s"%(self.piecename)


class MuseumArticles(models.Model):
    articlename = models.TextField()
    museum = models.ForeignKey(Museum, blank=False, null=False, on_delete=models.CASCADE)
    writername = models.CharField(max_length=255, blank=True, default='')
    articletype = models.CharField(max_length=255, blank=True, default='')
    detailurl = models.TextField()
    published = models.TextField()
    thumbimage = models.TextField()
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Museum Articles Information Table"
        db_table = 'museumarticles'
        ordering = ('-priority',)

    def __unicode__(self):
        return "%s"%(self.piecename)





