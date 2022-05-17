from django.db import models
from django.core.exceptions import ValidationError


yearidentifier_choices = [('exact', 'exact'),('after', 'after'),('before', 'before'),('circa', 'circa')]
yearprecision_choices = [('decade', 'decade'),('century', 'century'),('millennial', 'millennial')]

class Artist(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, default=None, blank=False, null=False, db_column='fa_artist_ID')
    artistname = models.CharField(max_length=255, blank=False, null=False, db_column='fa_artist_name')
    prefix = models.CharField(max_length=25, blank=False, null=False, db_column='fa_artist_name_prefix')
    suffix = models.CharField(max_length=25, blank=False, null=False, db_column='fa_artist_name_suffix')
    nationality = models.CharField(max_length=255, blank=True, null=True, db_column='fa_artist_nationality')
    birthyear = models.CharField(max_length=10, blank=True, null=True, db_column='fa_artist_birth_year')
    deathyear = models.CharField(max_length=10, blank=True, null=True, db_column='fa_artist_death_year')
    birthyearidentifier = models.CharField(max_length=20, blank=True, null=True, db_column='fa_artist_birth_year_identifier', choices=yearidentifier_choices)
    deathyearidentifier = models.CharField(max_length=20, blank=True, null=True, db_column='fa_artist_death_year_identifier', choices=yearidentifier_choices)
    birthyearprecision = models.CharField(max_length=20, blank=True, null=True, db_column='fa_artist_birth_year_precision', choices=yearprecision_choices)
    deathyearprecision = models.CharField(max_length=20, blank=True, null=True, db_column='fa_artist_death_year_precision', choices=yearprecision_choices)
    description = models.TextField(db_column='fa_artist_description')
    aka = models.CharField(max_length=100, blank=True, null=True, db_column='fa_artist_aka')
    bio = models.TextField(db_column='fa_artist_bio')
    genre = models.CharField(max_length=255, blank=True, null=True, db_column='fa_artist_genre')
    artistimage = models.TextField(db_column='fa_artist_image')
    priority = models.IntegerField(default=0, db_column='fa_artist_priority')
    inserted = models.DateTimeField(auto_now_add=True, db_column='fa_artist_record_created')
    edited = models.DateTimeField(auto_now=True, db_column='fa_artist_record_updated')
    insertedby = models.CharField(max_length=25, blank=True, null=True, db_column='fa_arist_record_createdby')
    editedby = models.CharField(max_length=25, blank=True, null=True, db_column='fa_artist_record_updatedby')

    class Meta:
        verbose_name = "Artists Information Table"
        db_table = 'fineart_artists'
        ordering = ('priority',)

    def __unicode__(self):
        return "%s"%(self.artistname)


class Artwork(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, default=None, blank=False, null=False, db_column='faa_artwork_ID')
    artworkname = models.TextField(db_column='faa_artwork_title')
    review = models.TextField(db_column='faa_artwork_requires_review')
    creationstartdate = models.CharField(max_length=100, blank=True, null=True, db_column='faa_artwork_start_year')
    creationenddate = models.CharField(max_length=100, blank=True, null=True, db_column='faa_artwork_end_year')
    startyearidentifier = models.CharField(max_length=100, blank=True, null=True, db_column='faa_artwork_start_year_identifier', choices=yearidentifier_choices)
    endyearidentifier = models.CharField(max_length=100, blank=True, null=True, db_column='faa_artwork_end_year_identifier', choices=yearidentifier_choices)
    startyearprecision = models.CharField(max_length=100, blank=True, null=True, db_column='faa_artwork_start_year_precision', choices=yearprecision_choices)
    endyearprecision = models.CharField(max_length=100, blank=True, null=True, db_column='faa_artwork_end_year_precision', choices=yearprecision_choices)
    artist_id = models.IntegerField(null=True, db_column='faa_artist_ID')
    artist2_id = models.IntegerField(null=True, db_column='faa_artist2_ID')
    artist3_id = models.IntegerField(null=True, db_column='faa_artist3_ID')
    artist4_id = models.IntegerField(null=True, db_column='faa_artist4_ID')
    sizedetails = models.CharField(max_length=255, blank=True, null=True, db_column='faa_artwork_size_details')
    height = models.DecimalField(max_digits=13, decimal_places=2, db_column='faa_artwork_height')
    width = models.DecimalField(max_digits=13, decimal_places=2, db_column='faa_artwork_width')
    depth = models.DecimalField(max_digits=13, decimal_places=2, db_column='faa_artwork_depth')
    measureunit = models.CharField(max_length=255, blank=True, null=True, db_column='faa_arwork_measurement_unit')
    medium = models.TextField(db_column='faa_artwork_material')
    edition = models.TextField(db_column='faa_artwork_edition')
    category = models.TextField(db_column='faa_artwork_category')
    signature = models.TextField(db_column='faa_artwork_markings')
    description = models.TextField(db_column='faa_artwork_description')
    literature = models.TextField(db_column='faa_artwork_literature')
    exhibitions = models.TextField(db_column='faa_artwork_exhibition')
    priority = models.IntegerField(default=5, db_column='faa_artwork_priority')
    image1 = models.TextField(db_column='faa_artwork_image1')
    inserted = models.DateTimeField(auto_now_add=True, db_column='faa_artwork_record_created')
    edited = models.DateTimeField(auto_now=True, db_column='faa_artwork_record_updated')
    insertedby = models.CharField(max_length=25, blank=True, null=True, db_column='faa_artwork_record_createdby')
    editedby = models.CharField(max_length=25, blank=True, null=True, db_column='faa_artwork_record_updatedby')

    class Meta:
        verbose_name = "Artworks Information Table"
        db_table = 'fineart_artworks'
        ordering = ('priority',)

    def __unicode__(self):
        return "%s"%(self.artworkname)




