from django.db import models
from django.core.exceptions import ValidationError

class Auction(models.Model):
    auctionname = models.TextField()
    auctionid = models.CharField(max_length=100, blank=True, default='')
    auctionhouse = models.CharField(max_length=200, blank=True, default='')
    auctionlocation = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField()
    auctionurl = models.TextField()
    lotslistingurl = models.TextField()
    coverimage = models.TextField()
    auctiontype = models.CharField(max_length=255, blank=True, default='') # Classifies the auctions as "Online", "Location Bound" etc.
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Auctions Information Table"
        db_table = 'auctions'
        ordering = ('priority',)

    def __unicode__(self):
        return "%s"%(self.auctionname)


class Lot(models.Model):
    lotid = models.CharField(max_length=100, blank=True, default='')
    lottitle = models.TextField()
    lotdescription = models.TextField()
    artistname = models.TextField()
    artistbirth = models.CharField(max_length=50, blank=True, default='')
    artistdeath = models.CharField(max_length=50, blank=True, default='')
    artistnationality = models.CharField(max_length=100, blank=True, default='')
    medium = models.CharField(max_length=200, blank=True, default='')
    size = models.CharField(max_length=200, blank=True, default='')
    loturl = models.TextField()
    category = models.CharField(max_length=200, blank=True, default='') # Could be 'Painting', 'Etching', 'Sculpture', etc.
    auction = models.ForeignKey(Auction, blank=False, null=False, on_delete=models.CASCADE)
    estimate = models.CharField(max_length=100, blank=True, default='')
    soldprice = models.CharField(max_length=100, blank=True, default='')
    currency = models.CharField(max_length=10, blank=True, default='')
    provenance = models.TextField()
    literature = models.TextField()
    exhibited = models.TextField()
    lotimage1 = models.TextField()
    lotimage2 = models.TextField()
    lotimage3 = models.TextField()
    lotimage4 = models.TextField()
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    

    class Meta:
        verbose_name = "Lots (Artworks) Information Table"
        db_table = 'lots'
        ordering = ('priority',)

    def __unicode__(self):
        return "%s"%(self.lottitle)




