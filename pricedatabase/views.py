from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template.context_processors import csrf
from django.views.generic import View
from django.http import HttpResponseBadRequest, HttpResponse , HttpResponseRedirect, HttpRequest
from django.urls import reverse
from django.template import RequestContext
from django.db.models import Q
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int, is_safe_url
from django.template import Template, Context
from django.template.loader import get_template
from django.core.mail import send_mail
from django.contrib.sessions.backends.db import SessionStore
from django.template import loader

import os, sys, re, time, datetime
import simplejson as json
import redis
import pickle
import urllib
import MySQLdb
import unicodedata, itertools

#from gallery.models import Gallery, Event
from login.models import User, Session, Favourite #,WebConfig, Carousel, Follow
#from login.views import getcarouselinfo
#from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse
from artists.models import Artist, Artwork, FeaturedArtist

# Caching related imports and variables
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def removecontrolcharacters(s):
    all_chars = (chr(i) for i in range(sys.maxunicode))
    categories = {'Cc'}
    control_chars = ''.join(map(chr, itertools.chain(range(0x00,0x20), range(0x7f,0xa0))))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))
    return control_char_re.sub('', s)



#@cache_page(CACHE_TTL)
def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 20
    maxlotstoconsider = 2500 # These would be the 2500 top high priced lots. For this page we won't consider lots beyond the top 2500.
    rows = 6
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    fstartctr = int(page) * maxlotstoconsider - maxlotstoconsider
    fendctr = int(page) * maxlotstoconsider
    context = {}
    date2weeksago = datetime.datetime.now() - datetime.timedelta(days=settings.PDB_LATESTPERIOD)
    entitieslist = []
    filterpdb = []
    auctionhouses = {}
    uniquefilter = {}
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    cursor = dbconn.cursor()
    try:
        entitieslist = pickle.loads(redis_instance.get('pd_entitieslist'))
        filterpdb = pickle.loads(redis_instance.get('pd_filterpdb'))
        auctionhouses = pickle.loads(redis_instance.get('pd_auctionhouses'))
    except:
        entitieslist = []
        filterpdb = []
    if entitieslist.__len__() == 0:
        allauctionhousesqset = AuctionHouse.objects.all()
        for auctionhouseobj in allauctionhousesqset:
            auctionhouses[auctionhouseobj.housename] = auctionhouseobj.id
            if auctionhouseobj.housename not in uniquefilter.keys():
                autocompleteauctionhousename = auctionhouseobj.housename
                autocompleteauctionhousename = autocompleteauctionhousename.replace('"', "")
                autocompleteauctionhousename = removecontrolcharacters(autocompleteauctionhousename)
                filterpdb.append(autocompleteauctionhousename)
                uniquefilter[auctionhouseobj.housename] = 1
        lotsqset = Lot.objects.order_by('-soldpriceUSD')[fstartctr:fendctr] # Need a restriction on the number of objects, otherwise it might crash the system.
        artworkidslist = []
        auctionidslist = []
        artistidslist = []
        for lotobj in lotsqset:
            artworkidslist.append(str(lotobj.artwork_id))
            auctionidslist.append(str(lotobj.auction_id))
        artworkidsstr = "(" + ",".join(artworkidslist) + ")"
        artworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_requires_review, faa_artwork_start_year, faa_artwork_end_year, faa_artwork_start_year_identifier, faa_artwork_end_year_identifier, faa_artwork_start_year_precision, faa_artwork_end_year_precision, faa_artist_ID, faa_artist2_ID, faa_artist3_ID, faa_artist4_ID, faa_artwork_size_details, faa_artwork_height, faa_artwork_width, faa_artwork_depth, faa_arwork_measurement_unit, faa_artwork_material, faa_artwork_edition, faa_artwork_category, faa_artwork_markings, faa_artwork_description, faa_artwork_literature, faa_artwork_exhibition, faa_artwork_image1, faa_artwork_record_created, faa_artwork_record_updated from fineart_artworks where faa_artwork_ID in %s"%artworkidsstr
        cursor.execute(artworksql)
        allartworksqset = cursor.fetchall()
        artworksdict = {}
        for awrec in allartworksqset:
            awid = str(awrec[0])
            artworksdict[awid] = awrec
            artistid = str(awrec[9])
            artistidslist.append(artistid)
        artistidsstr = "(" + ",".join(artistidslist) + ")"
        auctionidsstr = "(" + ",".join(auctionidslist) + ")"
        auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar where faac_auction_ID in %s order by faac_auction_start_date desc"%auctionidsstr
        artistsql = "SELECT fa_artist_name, fa_artist_ID, fa_artist_name_prefix, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_description, fa_artist_aka, fa_artist_bio, fa_artist_genre, fa_artist_image, fa_artist_record_created from fineart_artists Where fa_artist_ID in %s"%artistidsstr
        auctionsdict = {}
        artistsdict = {}
        ahidslist = []
        cursor.execute(auctionsql)
        auctionsqset = cursor.fetchall()
        for auctionrec in auctionsqset:
            aucid = str(auctionrec[0])
            auctionsdict[aucid] = auctionrec
            ahid = auctionrec[3]
            ahidslist.append(ahid)
        cursor.execute(artistsql)
        artistsqset = cursor.fetchall()
        for artistrec in artistsqset:
            aid = str(artistrec[1])
            artistsdict[aid] = artistrec
        auctionhousesqset = AuctionHouse.objects.filter(id__in=ahidslist)
        auctionhousesdict = {}
        for auctionhouse in auctionhousesqset:
            auctionhousesdict[str(auctionhouse.id)] = auctionhouse
        lotctr = 0
        for lotobj in lotsqset:
            lotimage = lotobj.lotimage1
            saledate = lotobj.saledate
            saledt = datetime.datetime.combine(saledate, datetime.time(0, 0))
            if saledt < date2weeksago:
                continue
            artworkobj = None
            try:
                artworkobj = artworksdict[str(lotobj.artwork_id)]
                if lotimage == "": # If there is no lot image, go for the artwork image, if any.
                    lotimage = artworkobj[25]
            except:
                continue # If we can't find the corresponding artwork for this lot, then we skip it.
            if lotimage == "": # We will not show lots with no images.
                continue
            if lotctr > chunksize:
                break
            lotctr += 1
            lottitle = artworkobj[1]
            if lottitle not in uniquefilter.keys():
                autocompletelotname = lottitle
                autocompletelotname = autocompletelotname.replace('"', "")
                autocompletelotname = removecontrolcharacters(autocompletelotname)
                filterpdb.append(autocompletelotname)
                uniquefilter[lottitle] = 1
            auctionname, aucid, auctionperiod, auctionhousename = "", "", "", ""
            try:
                auctionobj = auctionsdict[str(lotobj.auction_id)]
                auctionname = auctionobj[1]
                aucid = auctionobj[0]
                auctionperiod = auctionobj[5].strftime('%d %b, %Y')
                if type(auctionobj[6]) is datetime.date and auctionobj[6].strftime('%d %b, %Y') != "01 Jan, 0001" and auctionobj[6].strftime('%d %b, %Y') != "01 Jan, 1":
                    auctionperiod += " - " + auctionobj[6].strftime('%d %b, %Y')
                if auctionname not in uniquefilter.keys():
                    autocompleteauctionname = auctionname
                    autocompleteauctionname = autocompleteauctionname.replace('"', "")
                    autocompleteauctionname = removecontrolcharacters(autocompleteauctionname)
                    filterpdb.append(autocompleteauctionname)
                    uniquefilter[auctionname] = 1
                ahid = auctionobj[3]
                try:
                    auctionhouseobj = auctionhousesdict[str(ahid)]
                    auctionhousename = auctionhouseobj.housename
                except:
                    pass
            except:
                pass
            artistname = ""
            try:
                artistobj = artistsdict[str(artworkobj[9])]
                artistname = artistobj[0]
                if artistname not in uniquefilter.keys():
                    autocompleteartistname = artistname
                    autocompleteartistname = autocompleteartistname.replace('"', "")
                    autocompleteartistname = removecontrolcharacters(autocompleteartistname)
                    filterpdb.append(autocompleteartistname)
                    uniquefilter[artistname] = 1
            except:
                pass
            d = {'artworkname' : artworkobj[1], 'saledate' : lotobj.saledate.strftime('%d %b, %Y'), 'soldprice' : lotobj.soldpriceUSD, 'size' : artworkobj[13], 'medium' : artworkobj[18], 'description' : artworkobj[22], 'lid' : lotobj.id, 'awid' : artworkobj[0], 'lotimage' : lotobj.lotimage1, 'auctionname' : auctionname, 'aucid' : aucid, 'auctionperiod' : auctionperiod, 'aid' : artworkobj[9], 'artistname' : artistname, 'soldprice' : lotobj.soldpriceUSD, 'auctionhouse' : auctionhousename}
            entitieslist.append(d)
        allartistsqset = FeaturedArtist.objects.all()[:30000] 
        # We selected 30000 records as that is the optimum number for speed and content.
        # Also, these are the best selling artists, so most searches would be based on them.
        for aobj in allartistsqset:
            artistname = aobj.artist_name
            if artistname not in uniquefilter.keys():
                autocompleteartistname = artistname
                autocompleteartistname = autocompleteartistname.replace('"', "")
                autocompleteartistname = removecontrolcharacters(autocompleteartistname)
                filterpdb.append(autocompleteartistname)
                uniquefilter[artistname] = 1
        try:
            redis_instance.set('pd_filterpdb', pickle.dumps(filterpdb))
            redis_instance.set('pd_entitieslist', pickle.dumps(entitieslist))
            redis_instance.set('pd_auctionhouses', pickle.dumps(auctionhouses))
        except:
            pass
    cursor.close()
    dbconn.close()
    context['entities'] = entitieslist
    context['filterpdb'] = filterpdb
    context['auctionhouses'] = auctionhouses
    #carouselentries = getcarouselinfo()
    #context['carousel'] = carouselentries
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('pdb.html')
    return HttpResponse(template.render(context, request))


def details(request):
    pass


def search(request):
    """
    This should return a json response containing a list of dicts.
    The dict keys would be the attributes of auction, artist or lot object.
    The object type will be specified in the object with the 'obtype' key.
    """
    if request.method != 'GET':
        return HttpResponse(json.dumps({'err' : "Invalid method of call"}))
    searchkey = None
    if request.method == 'GET':
        if 'q' in request.GET.keys():
            searchkey = str(request.GET['q']).strip()
    if not searchkey or searchkey == "":
        return HttpResponse(json.dumps({'err' : "Invalid Request: Request is missing search key"}))
    searchkey = searchkey.replace("'", "\\'").replace('"', '\\"') # Escape apostrophes and quotes.
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = request.GET['page']
    context = {}
    allsearchresults = []
    maxperobjectsearchresults = 30
    maxsearchresults = maxperobjectsearchresults * 3 # 3 types of objects are searched: auctions, artworks/lots and artists.
    startsearchctr = int(page) * maxsearchresults - maxsearchresults
    endsearchctr = int(page) * maxsearchresults + 1
    objectstartctr = maxperobjectsearchresults * int(page) - maxperobjectsearchresults
    objectendctr = maxperobjectsearchresults * int(page)
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    idpattern = re.compile("\d+")
    cursor = dbconn.cursor()
    # Remember to close db connection at the end of the function...
    auctionhouseqset = AuctionHouse.objects.filter(housename__icontains=searchkey)
    auctionhouseidslist = []
    for auctionhouseobj in auctionhouseqset:
        ah_id = str(auctionhouseobj.id)
        auctionhouseidslist.append(ah_id)
    auctionsdict = {}
    auctionhouseidsstr = "(" + ",".join(auctionhouseidslist) + ")"
    auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar where faac_auction_house_ID in %s order by faac_auction_start_date desc"%auctionhouseidsstr
    #print(auctionsql)
    if re.search(idpattern, auctionhouseidsstr):
        cursor.execute(auctionsql)
        auctionsqset = cursor.fetchall()
    else:
        auctionsqset = []
    for auctionrec in auctionsqset:
        auchouseid = str(auctionrec[3])
        if auchouseid in auctionsdict.keys():
            auctionslist = auctionsdict[auchouseid]
            auctionslist.append(auctionrec)
            auctionsdict[auchouseid] = auctionslist
        else:
            auctionsdict[auchouseid] = [auctionrec,]
    achctr = 0
    for auctionhouseobj in auctionhouseqset:
        auctionsqset = auctionsdict[str(auctionhouseobj.id)]
        auctionhousename = auctionhouseobj.housename
        ahid = auctionhouseobj.id
        for auctionobj in auctionsqset:
            auctionperiod = auctionobj[5].strftime("%d %b, %Y")
            if type(auctionobj[6]) == datetime.date and auctionobj[6].strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj[6].strftime("%d %b, %Y") != "01 Jan, 1":
                auctionperiod += " - " + auctionobj[6].strftime("%d %b, %Y")
            d = {'auctionname' : auctionobj[1], 'aucid' : auctionobj[2], 'auctionhouse' : auctionhousename, 'coverimage' : auctionobj[8], 'ahid' : ahid, 'auctionperiod' : auctionperiod, 'aucid' : auctionobj[0], 'lotcount' : str(auctionobj[7]), 'obtype' : 'auction'}
            if achctr > maxperobjectsearchresults * int(page):
                break
            achctr += 1
            allsearchresults.append(d)
    auctionsqset = Auction.objects.filter(auctionname__icontains=searchkey)[objectstartctr:objectendctr] #.order_by('priority')
    aucctr = 0
    auctionhouseidslist = []
    auctionhousedict = {}
    for auctionobj in auctionsqset:
        ah_id = str(auctionobj.auctionhouse_id)
        auctionhouseidslist.append(ah_id)
    auctionhouseidsstr = "(" + ",".join(auctionhouseidslist) + ")"
    auctionhousesql = "select cah_auction_house_ID, cah_auction_house_name from core_auction_houses where cah_auction_house_ID in %s"%auctionhouseidsstr
    if re.search(idpattern, auctionhouseidsstr):
        cursor.execute(auctionhousesql)
        ahqset = cursor.fetchall()
    else:
        ahqset = []
    for ahrec in ahqset:
        ah_id = str(ahrec[0])
        ah_name = ahrec[1]
        auctionhousedict[ah_id] = ah_name
    for auctionobj in auctionsqset:
        auctionhouseid = auctionobj.auctionhouse_id
        auctionhousename, ahid = "", ""
        try:
            auctionhousename = auctionhousedict[str(auctionhouseid)]
            ahid = auctionhouseid
        except:
            pass
        auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
        if type(auctionobj.auctionenddate) == datetime.date and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
            auctionperiod += " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
        d = {'auctionname' : auctionobj.auctionname, 'aucid' : auctionobj.auctionid, 'auctionhouse' : auctionhousename, 'coverimage' : auctionobj.coverimage, 'ahid' : ahid, 'auctionperiod' : auctionperiod, 'aucid' : auctionobj.id, 'lotcount' : str(auctionobj.lotcount), 'obtype' : 'auction'}
        if aucctr > maxperobjectsearchresults * int(page):
            break
        aucctr += 1
        allsearchresults.append(d)
    """
    Here we would be using raw SQL to speed up the searches. The following
    SQL queries use MATCH/AGAINST searches on fields that are indexed using
    FULLTEXT indexing. -Supriyo.
    """
    artctr = 0
    quotaflag = 0
    searchartistsql = "select fa_artist_ID, fa_artist_name, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_image from fineart_artists where MATCH(fa_artist_name) AGAINST ('" + searchkey + "') limit " + str(maxperobjectsearchresults) + " OFFSET " + str(objectstartctr)
    cursor.execute(searchartistsql)
    matchedartists = cursor.fetchall()
    artworkartistdict = {}
    lotartworkdict = {}
    artistidslist = []
    artworkidslist = []
    for artist in matchedartists:
        aid = str(artist[0])
        artistidslist.append(aid)
    artistidsstr = "(" + ",".join(artistidslist) + ")"
    artworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_requires_review, faa_artwork_start_year, faa_artwork_end_year, faa_artwork_start_year_identifier, faa_artwork_end_year_identifier, faa_artist_ID, faa_artwork_size_details, faa_artwork_material, faa_artwork_edition, faa_artwork_category, faa_artwork_markings, faa_artwork_description, faa_artwork_literature, faa_artwork_exhibition, faa_artwork_image1, faa_artwork_record_created from fineart_artworks where faa_artist_ID in %s"%artistidsstr
    #artworklotartistsql = "select artist_id, artist_name, artist_price_usd, prefix, nationality, birthyear, deathyear, description, aka, bio, artistimage, genre, saledate, auctionid, lotstatus, medium, sizedetails, lotcategory, lotnum, artworkid, artworkname, highestimate, lowestimate, lotimage1, lotimage2, lotid from fa_artwork_lot_artist where artist_id in %s"%artistidsstr
    if re.search(idpattern, artistidsstr):
        cursor.execute(artworksql)
        artworksqset = cursor.fetchall()
    else:
        artworksqset = []
    for awrec in artworksqset:
        artistid = str(awrec[7])
        if artistid in artworkartistdict.keys():
            awlist = artworkartistdict[artistid]
            awlist.append(awrec)
            artworkartistdict[artistid] = awlist
        else:
            artworkartistdict[artistid] = [awrec,]
        awid = str(awrec[0])
        artworkidslist.append(awid)
    awidsstr = "(" + ",".join(artworkidslist) + ")"
    lotsql = "select fal_lot_ID, fal_lot_no, fal_sub_lot_no, fal_artwork_ID, fal_auction_ID, fal_lot_sale_date, fal_lot_material, fal_lot_size_details, fal_lot_category, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_high_estimate, fal_lot_low_estimate, fal_lot_sale_price_USD, fal_lot_sale_price, fal_lot_condition, fal_lot_status, fal_lot_provenance, fal_lot_published, fal_lot_image1, fal_lot_image2 from fineart_lots where fal_artwork_ID in %s"%awidsstr
    if re.search(idpattern, awidsstr):
        cursor.execute(lotsql)
        lotsqset = cursor.fetchall()
    else:
        lotsqset = []
    for lotrec in lotsqset:
        awidstr = str(lotrec[3])
        if awidstr in lotartworkdict.keys():
            lotlist = lotartworkdict[awidstr]
            lotlist.append(lotrec)
            lotartworkdict[awidstr] = lotlist
        else:
            lotartworkdict[awidstr] = [lotrec,]
    for artist in matchedartists:
        try:
            artistartworkqset = artworkartistdict[str(artist[0])]
        except:
            artistartworkqset = []
        for artwork in artistartworkqset:
            try:
                lotqset = lotartworkdict[str(artwork[0])]
            except:
                lotqset = []
            for lot in lotqset:
                soldprice = str(lot[13])
                soldprice = soldprice.replace("$", "")
                #print(artist[1] + " ########################")
                szdet = lot[7]
                if lot[7] is None:
                    szdet = ""
                d = {'artistname' : artist[1], 'lottitle' : artwork[1], 'medium' : lot[6], 'size' : szdet.encode('utf-8'), 'aid' : artist[0], 'birthyear' : artist[3], 'deathyear' : artist[4], 'nationality' : artist[2], 'artistimage' : artist[5], 'coverimage' : lot[19], 'awid' : artwork[0], 'createdate' : artwork[3], 'lid' : lot[0], 'obtype' : 'lot', 'aucid' : lot[4], 'soldprice' : soldprice}
                allsearchresults.append(d)
                artctr += 1
                if artctr > maxperobjectsearchresults:
                    quotaflag = 1 # Quota for this object (artists) has been emptied.
                    break
            if quotaflag == 1:
                break
        if quotaflag == 1:
            break
    searchartworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_start_year, faa_artist_ID from fineart_artworks where MATCH(faa_artwork_title) AGAINST ('" + searchkey + "') limit " + str(maxperobjectsearchresults) + " OFFSET " + str(objectstartctr)
    cursor.execute(searchartworksql)
    matchedartworks = cursor.fetchall()
    #artworkqset = Artwork.objects.filter(artworkname__icontains=searchkey)[objectstartctr:objectendctr]
    #print(artworkqset.explain())
    awctr = 0
    quotaflag = 0
    artistdict = {}
    lotartworkdict = {}
    artistidslist = []
    artworkidslist = []
    for artwork in matchedartworks:
        artistid = str(artwork[3])
        artistidslist.append(artistid)
        artworkid = str(artwork[0])
        artworkidslist.append(artworkid)
    artistidsstr = "(" + ",".join(artistidslist) + ")"
    artworkidsstr = "(" + ",".join(artworkidslist) + ")"
    artistsql = "SELECT fa_artist_name, fa_artist_ID, fa_artist_name_prefix, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_description, fa_artist_aka, fa_artist_bio, fa_artist_genre, fa_artist_image, fa_artist_record_created from fineart_artists Where fa_artist_ID in %s"%artistidsstr
    lotsql = "select fal_lot_ID, fal_lot_no, fal_sub_lot_no, fal_artwork_ID, fal_auction_ID, fal_lot_sale_date, fal_lot_material, fal_lot_size_details, fal_lot_category, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_high_estimate, fal_lot_low_estimate, fal_lot_sale_price_USD, fal_lot_sale_price, fal_lot_condition, fal_lot_status, fal_lot_provenance, fal_lot_published, fal_lot_image1, fal_lot_image2 from fineart_lots where fal_artwork_ID in %s"%artworkidsstr
    if re.search(idpattern, artistidsstr):
        cursor.execute(artistsql)
        artistsqset = cursor.fetchall()
    else:
        artistsqset = []
    for artistrec in artistsqset:
        artistidstr = str(artistrec[1])
        artistdict[artistidstr] = artistrec
    if re.search(idpattern, artworkidsstr):
        cursor.execute(lotsql)
        lotsqset = cursor.fetchall()
    else:
        lotsqset = []
    for lotrec in lotsqset:
        artworkid = str(lotrec[3])
        if artworkid in lotartworkdict.keys():
            lotslist = lotartworkdict[artworkid]
            lotslist.append(lotrec)
            lotartworkdict[artworkid] = lotslist
        else:
            lotartworkdict[artworkid] = [lotrec,]
    for artwork in matchedartworks:
        artist = None
        try:
            artist = artistdict[str(artwork[3])]
        except:
            continue # Skip the artwork if we can't identify the artist.
        try:
            lotqset = lotartworkdict[str(artwork[0])]
        except:
            lotqset = []
        for lot in lotqset:
            soldprice = str(lot[13])
            soldprice = soldprice.replace("$", "")
            #print(artist.artistname + " %%%%%%%%%%%%%%%%%%")
            szdet = lot[7]
            if lot[7] is None:
                szdet = ""
            d = {'artistname' : artist[0], 'lottitle' : artwork[1], 'medium' : lot[6], 'size' : szdet.encode('utf-8'), 'aid' : artist[1], 'birthyear' : artist[4], 'deathyear' : artist[5], 'nationality' : artist[3], 'artistimage' : artist[10], 'coverimage' : lot[19], 'awid' : artwork[0], 'createdate' : artwork[2], 'lid' : lot[0], 'obtype' : 'lot', 'aucid' : lot[4], 'soldprice' : soldprice}
            allsearchresults.append(d)
            awctr += 1
            if awctr > maxperobjectsearchresults:
                quotaflag = 1 # Quota for this object (artwork) has been emptied.
                break
        if quotaflag == 1:
            break
    context['allsearchresults'] = allsearchresults
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    cursor.close()
    dbconn.close()
    prevpage = int(page) - 1
    nextpage = int(page) + 1
    displayedprevpage1 = 0
    displayedprevpage2 = 0
    if prevpage > 0:
        displayedprevpage1 = prevpage - 1
        displayedprevpage2 = prevpage - 2
    displayednextpage1 = nextpage + 1
    displayednextpage2 = nextpage + 2
    firstpage = 1
    context['pages'] = {'prevpage' : prevpage, 'nextpage' : nextpage, 'firstpage' : firstpage, 'displayedprevpage1' : displayedprevpage1, 'displayedprevpage2' : displayedprevpage2, 'displayednextpage1' : displayednextpage1, 'displayednextpage2' : displayednextpage2, 'currentpage' : int(page)}
    return HttpResponse(json.dumps(context))



def dofilter(request):
    if request.method != 'POST':
        return HttpResponse('{ "error" : "Invalid request method"}')
    artistname, lottitle, medium, auctionhouseids, sizespec, sizeunit, saleoutcomes, soldmin, soldmax, estimatemin, estimatemax = "", "", "", "", "", "", "", "", "", "", ""
    page = "1"
    requestbody = str(request.body)
    bodycomponents = requestbody.split("&")
    requestdict = {}
    for comp in bodycomponents:
        compparts = comp.split("=")
        if compparts.__len__() > 1:
            compparts[0] = compparts[0].replace("b'", "")
            requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
    endbarPattern = re.compile("\|\s*$")
    onlyspacesPattern = re.compile("^\s+$")
    if 'pageno' in requestdict.keys():
        page = requestdict['pageno'].strip()
    if 'artistname' in requestdict.keys():
        artistname = requestdict['artistname'].strip()
        artistname = artistname.replace("'", "\\'").replace('"', '\\"') # Escape apostrophes and quotes.
    if 'lottitle' in requestdict.keys():
        lottitle = requestdict['lottitle'].strip()
        lottitle = lottitle.replace("'", "\\'").replace('"', '\\"') # Escape apostrophes and quotes.
    if 'medium' in requestdict.keys():
        medium = requestdict['medium'].lower()
        medium = endbarPattern.sub("", medium)
    if 'auctionhouse' in requestdict.keys():
        auctionhouseids = requestdict['auctionhouse'].strip()
        auctionhouseids = endbarPattern.sub("", auctionhouseids)
        auctionhouseids = onlyspacesPattern.sub("", auctionhouseids)
    if 'sizeunit' in requestdict.keys():
        sizeunit = requestdict['sizeunit']
    if 'size' in requestdict.keys():
        sizespec = requestdict['size']
        sizespec = endbarPattern.sub("", sizespec)
    if 'saleoutcome' in requestdict.keys():
        saleoutcomes = requestdict['saleoutcome']
        saleoutcomes = endbarPattern.sub("", saleoutcomes)
    if 'soldmin' in requestdict.keys():
        soldmin = requestdict['soldmin'].strip()
    if 'soldmax' in requestdict.keys():
        soldmax = requestdict['soldmax'].strip()
    if 'estimatemin' in requestdict.keys():
        estimatemin = requestdict['estimatemin'].strip()
    if 'estimatemax' in requestdict.keys():
        estimatemax = requestdict['estimatemax'].strip()
    try:
        page = int(page)
    except:
        page = 1
    startctr = page * settings.PDB_MAXSEARCHRESULT - settings.PDB_MAXSEARCHRESULT
    endctr = page * settings.PDB_MAXSEARCHRESULT + 1
    artworkstartctr = page * settings.PDB_ARTWORKSLIMIT - settings.PDB_ARTWORKSLIMIT
    artworkendctr = page * settings.PDB_ARTWORKSLIMIT
    artiststartctr = page * settings.PDB_ARTISTSLIMIT - settings.PDB_ARTISTSLIMIT
    artistendctr = page * settings.PDB_ARTISTSLIMIT
    maxartworkmatches = 500 # This is the maximum number of artworks by a single artist that would be considered for searching.
    ahidlist = []
    mediumlist = []
    solist = []
    sizelist = []
    ahidlist = auctionhouseids.split("|")
    ahctr = 0
    for ah in ahidlist:
        if ah == "":
            ahidlist.pop(ahctr)
        ahctr += 1
    mediumlist = medium.split("|")
    mctr = 0
    for m in mediumlist:
        if m == "":
            mediumlist.pop(mctr)
        mctr += 1
    solist = saleoutcomes.split("|")
    sizelist = sizespec.split("|")
    entitieslist = []
    context = {}
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    cursor = dbconn.cursor()
    l_entities = []
    if lottitle != "":
        filterartworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_image1, faa_artist_ID from fineart_artworks where MATCH(faa_artwork_title) AGAINST ('" + lottitle + "') limit %s OFFSET %s"%(settings.PDB_ARTWORKSLIMIT, artworkstartctr)
        cursor.execute(filterartworksql)
        filterartworks = cursor.fetchall()
        for artwork in filterartworks:
            artworkname = artwork[1]
            #print(artworkname + " #######################")
            awid = artwork[0]
            lotqset = Lot.objects.filter(artwork_id=artwork[0])[0:1] # We need only one referenced lot.
            artistobj = None
            lartistname, aid = "", ""
            try:
                artistobj = Artist.objects.get(id=artwork[3])
                lartistname = artistobj.artistname
                aid = artistobj.id
            except:
                pass
            lmedium, lsize, lsaledate, lsoldprice, lminestimate, lmaxestimate, lcategory, lestimate, lid, lh, lw, ld, limage = "", "", "", "", "", "", "", "", "", "", "", "", ""
            auctionname, aucid, auctionperiod, auctionhousename, ahid = "", "", "", "", ""
            if lotqset.__len__() > 0:
                lmedium = lotqset[0].medium.lower()
                lsize = lotqset[0].sizedetails.encode('utf-8')
                lsaledate = lotqset[0].saledate.strftime("%d %b, %Y")
                lsoldprice = lotqset[0].soldpriceUSD
                lminestimate = lotqset[0].lowestimateUSD
                lmaxestimate = lotqset[0].highestimateUSD
                lestimate = str(lminestimate)
                if lmaxestimate and lmaxestimate > 0.00:
                    lestimate += " - " + str(lmaxestimate)
                lcategory = lotqset[0].category
                lid = lotqset[0].id
                lh = lotqset[0].height
                lw = lotqset[0].width
                ld = lotqset[0].depth
                limage = lotqset[0].lotimage1
                if limage == "":
                    limage = artwork[2]
                if limage == "": # If we still don't have an image, just skip it.
                    continue
                auctionobj = None
                try:
                    auctionobj = Auction.objects.get(id=lotqset[0].auction_id)
                    auctionname = auctionobj.auctionname
                    aucid = auctionobj.id
                    auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                    if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                        auctionperiod += " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
                    auchouseobj = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
                    auctionhousename = auchouseobj.housename
                    ahid = auchouseobj.id
                except:
                    pass
            d = {'lottitle' : artworkname, 'artistname' : lartistname, 'aid' : aid, 'awid' : awid, 'medium' : lmedium, 'size' : lsize, 'saledate' : lsaledate, 'soldprice' : lsoldprice, 'estimate' : lestimate, 'lid' : lid, 'auctionname' : auctionname, 'auctionperiod' : auctionperiod, 'aucid' : aucid, 'auctionhouse' : auctionhousename, 'ahid' : ahid, 'obtype' : 'lot', 'coverimage' : limage}
            # Now check all parameters against user's selected values to determine if this dict should be appended to 'entitieslist'.
            artistflag, titleflag, mediumflag, sizeflag, soldpriceflag, estimateflag, auctionhouseflag = -1, 1, -1, -1, -1, -1, -1
            if artistname != "" and artistname.lower() in lartistname.lower(): # Partial match is considered.
                artistflag = 1
            elif artistname != "":
                artistflag = 0
            else:
                pass
            for m in mediumlist:
                if m in lmedium: # If a single medium component matches, we set the flag to True and break out.
                    mediumflag = 1
                    break
            if mediumlist.__len__() > 0 and mediumflag == -1:
                mediumflag = 0
            ahctr = 0
            for ad in ahidlist:
                if ad == "" or ahid == "":
                    continue
                ahctr += 1
                if int(ad) == int(ahid):
                    auctionhouseflag = 1
                    break
            if ahctr > 0 and auctionhouseflag == -1:
                auctionhouseflag = 0
            if soldmin != "" and lsoldprice != "" and float(soldmin) < float(lsoldprice):
                if soldmax != "" and float(soldmax) > float(lsoldprice):
                    soldpriceflag = 1
                elif soldmax == "":
                    soldpriceflag = 1
            elif soldmin != "" and lsoldprice != "" and float(soldmin) > float(lsoldprice):
                soldpriceflag = 0
            else:
                pass
            sizeparts = [lh, lw]
            if ld != "":
                sizeparts.append(ld)
            for sz in sizelist:
                if sz == "small":
                    for sp in sizeparts:
                        try:
                            fsp = float(sp)
                            if fsp < 40: # Check if any of the dimensions is less than 40 cm.
                                sizeflag = 1
                                break
                            else:
                                sizeflag = 0
                        except:
                            pass
                elif sz == "medium":
                    for sp in sizeparts:
                        try:
                            fsp = float(sp)
                            if fsp > 40 and fsp < 100: # Check if any of the dimensions is between 40 and 100 cm.
                                sizeflag = 1
                                break
                            else:
                                sizeflag = 0
                        except:
                            pass
                elif sz == "large":
                    for sp in sizeparts:
                        try:
                            fsp = float(sp)
                            if fsp > 100: # Check if any of the dimensions is greater than 100 cm.
                                sizeflag = 1
                                break
                            else:
                                sizeflag = 0
                        except:
                            pass
                else:
                    pass
            try:
                if float(lminestimate) < float(estimatemin) and float(lmaxestimate) > float(estimatemax):
                    estimateflag = 1
                else:
                    estimateflag = 0
            except: # If user didn't specify any estimate values, then the flag remains -1.
                pass
            #print(str(estimateflag) + " ## " + str(sizeflag) + " ## " + str(soldpriceflag) + " ## " + str(auctionhouseflag) + " ## " + str(mediumflag) + " ## " + str(artistflag))
            if estimateflag != 0 and sizeflag != 0 and soldpriceflag != 0 and auctionhouseflag != 0 and mediumflag != 0 and artistflag != 0:
                l_entities.append(d)
    else: # Handle case with parameters other than artwork name.
        filterartists = []
        if artistname != "":
            filterartistsql = "select fa_artist_ID, fa_artist_name, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_image from fineart_artists where MATCH(fa_artist_name) AGAINST ('%s') limit %s offset %s"%(artistname, settings.PDB_ARTISTSLIMIT, artiststartctr)
            cursor.execute(filterartistsql)
            filterartists = cursor.fetchall()
        else:
            filterartistsql = "select fa_artist_ID, fa_artist_name, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_image from fineart_artists limit %s offset %s"%(settings.PDB_ARTISTSLIMIT, artiststartctr)
            cursor.execute(filterartistsql)
            filterartists = cursor.fetchall()
        for artist in filterartists:
            aid = artist[0]
            if aid in settings.BLACKLISTED_ARTISTS:
                continue
            artistnm = artist[1]
            for artwork in Artwork.objects.filter(artist_id=artist[0]).order_by('-edited')[:maxartworkmatches].iterator():
                if artwork.image1 == "":
                    continue
                awid = artwork.id
                artworkname = artwork.artworkname
                lotqset = Lot.objects.filter(artwork_id=artwork.id)
                lmedium, lsize, lsaledate, lsoldprice, lminestimate, lmaxestimate, lcategory, lestimate, lid = "", "", "", "", "", "", "", "", ""
                auctionname, aucid, auctionperiod, auctionhousename, ahid = "", "", "", "", ""
                if lotqset.__len__() > 0:
                    lmedium = lotqset[0].medium.lower()
                    lsize = lotqset[0].sizedetails.encode('utf-8')
                    lsaledate = lotqset[0].saledate.strftime("%d %b, %Y")
                    lsoldprice = lotqset[0].soldpriceUSD
                    lminestimate = lotqset[0].lowestimateUSD
                    lmaxestimate = lotqset[0].highestimateUSD
                    lestimate = str(lminestimate)
                    if lmaxestimate and lmaxestimate > 0.00:
                        lestimate += " - " + str(lmaxestimate)
                    lcategory = lotqset[0].category
                    lid = lotqset[0].id
                    auctionobj = None
                    try:
                        auctionobj = Auction.objects.get(id=lotqset[0].auction_id)
                        auctionname = auctionobj.auctionname
                        aucid = auctionobj.id
                        auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                        if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                            auctionperiod += " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
                        auchouseobj = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
                        auctionhousename = auchouseobj.housename
                        ahid = auchouseobj.id
                    except:
                        pass
                d = {'lottitle' : artworkname, 'artistname' : artistnm, 'aid' : aid, 'awid' : awid, 'medium' : lmedium, 'size' : lsize, 'saledate' : lsaledate, 'soldprice' : lsoldprice, 'estimate' : lestimate, 'lid' : lid, 'auctionname' : auctionname, 'auctionperiod' : auctionperiod, 'aucid' : aucid, 'auctionhouse' : auctionhousename, 'ahid' : ahid, 'obtype' : 'lot', 'coverimage' : artwork.image1}
                entitieslist.append(d)
        l_entities = []
        if entitieslist.__len__() > 0:
            for entity in entitieslist:
                mediumflag, sizeflag, soldpriceflag, estimateflag, auctionhouseflag = -1, -1, -1, -1, -1
                for m in mediumlist:
                    if m in entity['medium'].lower():
                        mediumflag = 1
                        break
                if mediumlist.__len__() > 0 and mediumflag == -1:
                    mediumflag = 0 # User specified medium, but none of them matched this entity's medium.
                for ah in ahidlist:
                    try:
                        if int(ah) == int(entity['ahid']):
                            auctionhouseflag = 1
                            break
                    except:
                        pass
                if ahidlist.__len__() > 0 and auctionhouseflag == -1:
                    auctionhouseflag = 0
                try:
                    if float(entity['soldprice']) > float(soldmin) and float(entity['soldprice']) < float(soldmax):
                        soldpriceflag = 1
                    else:
                        soldpriceflag = 0
                except:
                    print("ERROR: %s %s"%(sys.exc_info()[1].__str__(), entity['soldprice'])) # This should be logged - TODO
                estimateparts = entity['estimate'].split(" - ")
                lminestimate = estimateparts[0]
                lmaxestimate = ""
                if estimateparts.__len__() > 1:
                    lmaxestimate = estimateparts[1]
                try:
                    if float(lminestimate) < float(estimatemin) and float(lmaxestimate) > float(estimatemax):
                        estimateflag = 1
                    else:
                        estimateflag = 0
                except:
                    pass
                if mediumflag != 0 and soldpriceflag != 0 and estimateflag != 0 and auctionhouseflag != 0:
                    l_entities.append(entity)
                #print(str(estimateflag) + " ## " + str(soldpriceflag) + " ## " + str(auctionhouseflag) + " ## " + str(mediumflag))
        else: # Control should never come here.
            pass
    dbconn.close() # Closed db connection!
    r_entitieslist = []
    if l_entities.__len__() > settings.PDB_MAXSEARCHRESULT:
        for d in l_entities[startctr:endctr]:
            r_entitieslist.append(d)
    else:
        for d in l_entities:
            r_entitieslist.append(d)
    context['allsearchresults'] = r_entitieslist
    prevpage = int(page) - 1
    nextpage = int(page) + 1
    displayedprevpage1 = 0
    displayedprevpage2 = 0
    if prevpage > 0:
        displayedprevpage1 = prevpage - 1
        displayedprevpage2 = prevpage - 2
    displayednextpage1 = nextpage + 1
    displayednextpage2 = nextpage + 2
    firstpage = 1
    context['pages'] = {'prevpage' : prevpage, 'nextpage' : nextpage, 'firstpage' : firstpage, 'displayedprevpage1' : displayedprevpage1, 'displayedprevpage2' : displayedprevpage2, 'displayednextpage1' : displayednextpage1, 'displayednextpage2' : displayednextpage2, 'currentpage' : int(page)}
    return HttpResponse(json.dumps(context))



