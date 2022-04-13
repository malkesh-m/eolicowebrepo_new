from django.db import models
from django.core.exceptions import ValidationError


class AuctionHouse(models.Model):
    housename = models.CharField(max_length=255, blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField()
    houseurl = models.TextField()
    coverimage = models.TextField()
    housetype = models.CharField(max_length=255, blank=True, default='') # Classifies the auction houses as "Non-profit Organizations", "Artist Estates/Foundations" etc.
    priority = models.IntegerField(default=0)
    inserted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Auction House Information Table"
        db_table = 'auctionhouses'
        ordering = ('priority',)

    def __unicode__(self):
        return "%s"%(self.housename)


