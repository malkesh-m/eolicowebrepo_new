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

#from gallery.models import Gallery, Event
from login.models import User, Session #, WebConfig, Carousel
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
                filterpdb.append(auctionhouseobj.housename)
                uniquefilter[auctionhouseobj.housename] = 1
        lotsqset = Lot.objects.order_by('-soldpriceUSD')[fstartctr:fendctr] # Need a restriction on the number of objects, otherwise it might crash the system.
        lotctr = 0
        for lotobj in lotsqset:
            lotimage = lotobj.lotimage1
            saledate = lotobj.saledate
            saledt = datetime.datetime.combine(saledate, datetime.time(0, 0))
            if saledt < date2weeksago:
                continue
            artworkobj = None
            try:
                artworkobj = Artwork.objects.get(id=lotobj.artwork_id)
                if lotimage == "": # If there is no lot image, go for the artwork image, if any.
                    lotimage = artworkobj.image1
            except:
                continue # If we can't find the corresponding artwork for this lot, then we skip it.
            if lotimage == "": # We will not show lots with no images.
                continue
            if lotctr > chunksize:
                break
            lotctr += 1
            lottitle = artworkobj.artworkname
            if lottitle not in uniquefilter.keys():
                filterpdb.append(lottitle)
                uniquefilter[lottitle] = 1
            auctionname, aucid, auctionperiod, auctionhousename = "", "", "", ""
            try:
                auctionobj = Auction.objects.get(id=lotobj.auction_id)
                auctionname = auctionobj.auctionname
                aucid = auctionobj.id
                auctionperiod = auctionobj.auctionstartdate.strftime('%d %b, %Y')
                if auctionobj.auctionenddate.strftime('%d %b, %Y') != "01 Jan, 0001" and auctionobj.auctionenddate.strftime('%d %b, %Y') != "01 Jan, 1":
                    auctionperiod += " - " + auctionobj.auctionenddate.strftime('%d %b, %Y')
                if auctionname not in uniquefilter.keys():
                    filterpdb.append(auctionname)
                    uniquefilter[auctionname] = 1
                ahid = auctionobj.auctionhouse_id
                try:
                    auctionhouseobj = AuctionHouse.objects.get(id=ahid)
                    auctionhousename = auctionhouseobj.housename
                except:
                    pass
            except:
                pass
            artistname = ""
            try:
                artistobj = Artist.objects.get(id=artworkobj.artist_id)
                artistname = artistobj.artistname
                if artistname not in uniquefilter.keys():
                    filterpdb.append(artistname)
                    uniquefilter[artistname] = 1
            except:
                pass
            d = {'artworkname' : artworkobj.artworkname, 'saledate' : lotobj.saledate.strftime('%d %b, %Y'), 'soldprice' : lotobj.soldpriceUSD, 'size' : artworkobj.sizedetails, 'medium' : artworkobj.medium, 'description' : artworkobj.description, 'lid' : lotobj.id, 'awid' : artworkobj.id, 'lotimage' : lotobj.lotimage1, 'auctionname' : auctionname, 'aucid' : aucid, 'auctionperiod' : auctionperiod, 'aid' : artworkobj.artist_id, 'artistname' : artistname, 'soldprice' : lotobj.soldpriceUSD, 'auctionhouse' : auctionhousename}
            entitieslist.append(d)
        allartistsqset = FeaturedArtist.objects.all()[:30000] 
        # We selected 30000 records as that is the optimum number for speed and content.
        # Also, these are the best selling artists, so most searches would be based on them.
        for aobj in allartistsqset:
            artistname = aobj.artist_name
            if artistname not in uniquefilter.keys():
                filterpdb.append(artistname)
                uniquefilter[artistname] = 1
        try:
            redis_instance.set('pd_filterpdb', pickle.dumps(filterpdb))
            redis_instance.set('pd_entitieslist', pickle.dumps(entitieslist))
            redis_instance.set('pd_auctionhouses', pickle.dumps(auctionhouses))
        except:
            pass
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
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="Artcurv-production")
    cursor = dbconn.cursor()
    # Remember to close db connection at the end of the function...
    auctionhouseqset = AuctionHouse.objects.filter(housename__icontains=searchkey)
    achctr = 0
    for auctionhouseobj in auctionhouseqset:
        auctionsqset = Auction.objects.filter(auctionhouse_id=auctionhouseobj.id)
        auctionhousename = auctionhouseobj.housename
        ahid = auctionhouseobj.id
        for auctionobj in auctionsqset:
            auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
            if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                auctionperiod += " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
            d = {'auctionname' : auctionobj.auctionname, 'aucid' : auctionobj.auctionid, 'auctionhouse' : auctionhousename, 'coverimage' : auctionobj.coverimage, 'ahid' : ahid, 'auctionperiod' : auctionperiod, 'aucid' : auctionobj.id, 'lotcount' : str(auctionobj.lotcount), 'obtype' : 'auction'}
            if achctr > maxperobjectsearchresults * int(page):
                break
            achctr += 1
            allsearchresults.append(d)
    auctionsqset = Auction.objects.filter(auctionname__icontains=searchkey)[objectstartctr:objectendctr] #.order_by('priority')
    aucctr = 0
    for auctionobj in auctionsqset:
        auctionhouseid = auctionobj.auctionhouse_id
        ahobj = None
        auctionhousename, ahid = "", ""
        try:
            ahobj = AuctionHouse.objects.get(id=auctionhouseid)
            auctionhousename = ahobj.housename
            ahid = ahobj.id
        except:
            pass
        auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
        if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
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
    for artist in matchedartists:
        artistartworkqset = Artwork.objects.filter(artist_id=artist[0])
        for artwork in artistartworkqset:
            lotqset = Lot.objects.filter(artwork_id=artwork.id)
            for lot in lotqset:
                soldprice = str(lot.soldpriceUSD)
                soldprice = soldprice.replace("$", "")
                #print(artist[1] + " ########################")
                d = {'artistname' : artist[1], 'lottitle' : artwork.artworkname, 'medium' : lot.medium, 'size' : lot.sizedetails.encode('utf-8'), 'aid' : artist[0], 'birthyear' : artist[3], 'deathyear' : artist[4], 'nationality' : artist[2], 'artistimage' : artist[5], 'coverimage' : lot.lotimage1, 'awid' : artwork.id, 'createdate' : artwork.creationstartdate, 'lid' : lot.id, 'obtype' : 'lot', 'aucid' : lot.auction_id, 'soldprice' : soldprice}
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
    for artwork in matchedartworks:
        artist = None
        try:
            artist = Artist.objects.get(id=artwork[3])
        except:
            continue # Skip the artwork if we can't identify the artist.
        lotqset = Lot.objects.filter(artwork_id=artwork[0])
        for lot in lotqset:
            soldprice = str(lot.soldpriceUSD)
            soldprice = soldprice.replace("$", "")
            #print(artist.artistname + " %%%%%%%%%%%%%%%%%%")
            d = {'artistname' : artist.artistname, 'lottitle' : artwork[1], 'medium' : lot.medium, 'size' : lot.sizedetails.encode('utf-8'), 'aid' : artist.id, 'birthyear' : artist.birthyear, 'deathyear' : artist.deathyear, 'nationality' : artist.nationality, 'artistimage' : artist.artistimage, 'coverimage' : lot.lotimage1, 'awid' : artwork[0], 'createdate' : artwork[2], 'lid' : lot.id, 'obtype' : 'lot', 'aucid' : lot.auction_id, 'soldprice' : soldprice}
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
    dbconn.close() # ... done! Closed db connection.
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
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="Artcurv-production")
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



