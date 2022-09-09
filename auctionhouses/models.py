from django.db import models
from django.core.exceptions import ValidationError


class AuctionHouse(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, default=None, blank=False, null=False, db_column='cah_auction_house_ID')
    housename = models.CharField(max_length=255, blank=True, default='', db_column='cah_auction_house_name')
    location = models.CharField(max_length=255, blank=True, default='', db_column='cah_auction_house_location')
    country = models.CharField(max_length=255, blank=True, default='', db_column='cah_auction_house_country')
    currency = models.CharField(max_length=4, blank=True, default='', db_column='cah_auction_house_currency_code')
    houseurl = models.TextField(db_column='cah_auction_house_website')
    #priority = models.IntegerField(default=0, db_column='cah_auction_house_priority')
    inserted = models.DateTimeField(auto_now_add=True, db_column='cah_auction_house_record_created')
    edited = models.DateTimeField(auto_now=True, db_column='cah_auction_house_record_updated')
    insertedby = models.CharField(max_length=25, blank=True, null=True, db_column='cah_auction_house_record_createdby')
    editedby = models.CharField(max_length=25, blank=True, null=True, db_column='cah_auction_house_record_updatedby')

    class Meta:
        verbose_name = "Auction House Information Table"
        db_table = 'core_auction_houses'
        #ordering = ('priority',)

    def __unicode__(self):
        return "%s"%(self.housename)


