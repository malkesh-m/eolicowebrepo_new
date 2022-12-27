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
import MySQLdb

#from gallery.models import Gallery, Event
from login.models import User, Session, Favourite #,WebConfig, Carousel, Follow
#from login.views import getcarouselinfo
#from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse
from artists.models import Artist, Artwork, LotArtist

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
    chunksize = 4
    rows = 6
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    fstartctr = int(page) * chunksize - chunksize
    fendctr = int(page) * chunksize
    context = {}
    auctionhouses = [] # Auctions in various auction houses section.
    filterauctionhouses = []
    maxauctionsperhouse = 4
    maxfeaturedauctionsperhouse = 4
    maxfeaturedshows = 8
    featuredshowscutoffdate = datetime.datetime.now() - datetime.timedelta(days=2 * 365) # date of 2 year back in time. TODO: This should be changed to 3 months later during deployment.
    featuredshows = [] # Featured shows section, will show 5 top priority auctions only.
    currentmngshows = {} # Current museum and gallery shows section - keys are auction houses, values are list of priority auctions in each house. Will need association of auctions to galleries and museums, which is to be implemented later.
    uniqueauctions = {}
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    cursor = dbconn.cursor()
    try:
        filterauctionhouses = pickle.loads(redis_instance.get('ah_filterauctionhouses'))
        auctionhouses = pickle.loads(redis_instance.get('ah_auctionhouses'))
        featuredshows = pickle.loads(redis_instance.get('ah_featuredshows'))
    except:
        filterauctionhouses = []
        auctionhouses = []
        featuredshows = []
    if auctionhouses.__len__() == 0:
        auctionhousesqset = AuctionHouse.objects.all()#.order_by('-priority')
        if auctionhousesqset.__len__() <= fstartctr:
            fstartctr = 0
        auctionhouseidslist = []
        auctionhouseidsstr = ""
        for auctionhouse in auctionhousesqset:
            auchouseid = str(auctionhouse.id)
            auctionhouseidslist.append(auchouseid)
        #print(auctionhouseidslist)
        auctionhouseidsstr = "(" + ",".join(auctionhouseidslist) + ")"
        auctionhouseauctionsdict = {}
        auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar where faac_auction_house_ID in %s order by faac_auction_start_date desc"%(auctionhouseidsstr)
        cursor.execute(auctionsql)
        auctionsqset = cursor.fetchall()
        for auction in auctionsqset:
            auctionhouseid = auction[3]
            if str(auctionhouseid) in auctionhouseauctionsdict.keys():
                auctionslist = auctionhouseauctionsdict[str(auctionhouseid)]
                if auctionslist.__len__() < maxauctionsperhouse: # We won't keep more than 'maxauctionsperhouse' records per house.
                    auctionslist.append(auction)
                    auctionhouseauctionsdict[str(auctionhouseid)] = auctionslist
                else:
                    pass
            else:
                auctionslist = [auction,]
                auctionhouseauctionsdict[str(auctionhouseid)] = auctionslist
        #print(auctionhouseauctionsdict.keys())
        for auctionhouse in auctionhousesqset[fstartctr:]:
            try:
                auctionsqset = auctionhouseauctionsdict[str(auctionhouse.id)]
            except: # We found a auction house reference in auction model that doesn't exist in auctionhouse model
                continue
            coverimage = ""
            if auctionsqset.__len__() > 0:
                coverimage = auctionsqset[0][8]
            d = {'housename' : auctionhouse.housename, 'houseurl' : auctionhouse.houseurl, 'description' : '', 'image' : coverimage, 'ahid' : auctionhouse.id, 'location' : auctionhouse.location}
            auctionslist = []
            for auction in auctionsqset:
                auctionperiod = ""
                if auction[5].strftime("%d %b, %Y") != "01 Jan, 0001" and auction[5].strftime("%d %b, %Y") != "01 Jan, 1":
                    auctionperiod = auction[5].strftime("%d %b, %Y")
                    aucenddate = auction[6]
                    if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                        auctionperiod += " - " + str(aucenddate)
                d1 = {'auctionname' : auction[1], 'coverimage' : auction[8], 'auctionurl' : '', 'location' : auctionhouse.location, 'auctionperiod' : auctionperiod, 'aucid' : auction[0], 'ahid' : auctionhouse.id}
                auctionslist.append(d1)
                uniqueauctions[str(auction[0])] = auction[1]
            d['auctionslist'] = auctionslist
            auctionhouses.append(d)
            if auctionhouse.housename not in filterauctionhouses:
                filterauctionhouses.append(auctionhouse.housename)
        context['auctionhouses'] = auctionhouses
        context['filterauctionhouses'] = filterauctionhouses
        try:
            redis_instance.set('ah_auctionhouses', pickle.dumps(auctionhouses))
            redis_instance.set('ah_filterauctionhouses', pickle.dumps(filterauctionhouses))
        except:
            pass
        for auctionhouse in auctionhousesqset:
            try:
                auctionsqset = auctionhouseauctionsdict[str(auctionhouse.id)]
            except:
                continue
            coverimage = ""
            if auctionsqset.__len__() > 0:
                coverimage = auctionsqset[0][8]
            d = {'housename' : auctionhouse.housename, 'houseurl' : auctionhouse.houseurl, 'description' : '', 'image' : coverimage, 'ahid' : auctionhouse.id, 'location' : auctionhouse.location}
            auctionslist = []
            for auction in auctionsqset:
                auctionperiod = ""
                featuredshowscutoffdate = datetime.date(featuredshowscutoffdate.year, featuredshowscutoffdate.month, featuredshowscutoffdate.day)
                if auction[5] < featuredshowscutoffdate: # We won't consider auctions that have happened before the last 1 year.
                    continue
                if auction[5].strftime("%d %b, %Y") != "01 Jan, 0001" and auction[5].strftime("%d %b, %Y") != "01 Jan, 1":
                    auctionperiod = auction[5].strftime("%d %b, %Y")
                    aucenddate = auction[6]
                    if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                        auctionperiod += " - " + str(aucenddate)
                #print(auction[2])
                d1 = {'auctionname' : auction[1], 'coverimage' : auction[8], 'auctionurl' : auction[4], 'location' : auctionhouse.location, 'auctionperiod' : auctionperiod, 'aucid' : auction[0], 'ahid' : auctionhouse.id, 'housename' : auctionhouse.housename, 'salecode' : auction[2]}
                auctionslist.append(d1)
                uniqueauctions[str(auction[0])] = auction[1]
            d['auctionslist'] = auctionslist
            featuredshows.append(d)
            if featuredshows.__len__() >= maxfeaturedshows:
                break
        context['featuredshows'] = featuredshows
        try:
            redis_instance.set('ah_featuredshows', pickle.dumps(featuredshows))
        except:
            pass
    else:
        context['auctionhouses'] = auctionhouses
        context['featuredshows'] = featuredshows
    try:
        currentmngshows = pickle.loads(redis_instance.get('ah_currentmngshows'))
    except:
        currentmngshows = {}
    if currentmngshows.keys().__len__() == 0:
        maxrecs = maxauctionsperhouse * rows * 4
        auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar order by faac_auction_start_date desc limit %s"%maxrecs
        cursor.execute(auctionsql)
        auctionsqset = cursor.fetchall()
        for auction in auctionsqset:
            if str(auction[0]) in uniqueauctions.keys():
                continue
            else:
                uniqueauctions[str(auction[0])] = auction[1]
            auctionhouse = None
            try:
                auctionhouse = AuctionHouse.objects.get(id=auction[3])
            except:
                continue
            auctionhousename = auctionhouse.housename.title()
            auctionperiod = ""
            if auction[5].strftime("%d %b, %Y") != "01 Jan, 0001" and auction[5].strftime("%d %b, %Y") != "01 Jan, 1":
                auctionperiod = auction[5].strftime("%d %b, %Y")
                aucenddate = auction[6]
                if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                    auctionperiod += " - " + str(aucenddate)
            if auctionhousename in currentmngshows.keys():
                l = currentmngshows[auctionhousename]
                if l.__len__() >= maxauctionsperhouse:
                    continue
                d = {'auctionname' : auction[1], 'coverimage' : auction[8], 'auctionurl' : auctionhouse.houseurl, 'location' : auctionhouse.location, 'auctionperiod' : auctionperiod, 'aucid' : auction[0], 'ahid' : auctionhouse.id, 'salecode' : auction[2]}
                l.append(d)
                currentmngshows[auctionhousename] = l
            else:
                l = []
                d = {'auctionname' : auction[1], 'coverimage' : auction[8], 'auctionurl' : auctionhouse.houseurl, 'location' : auctionhouse.location, 'auctionperiod' : auctionperiod, 'aucid' : auction[0], 'ahid' : auctionhouse.id, 'salecode' : auction[2]}
                l.append(d)
                currentmngshows[auctionhousename] = l
        context['currentmngshows'] = currentmngshows
        try:
            redis_instance.set('ah_currentmngshows', pickle.dumps(currentmngshows))
        except:
            pass
    else:
        context['currentmngshows'] = currentmngshows
    cursor.close()
    dbconn.close()
    #carouselentries = getcarouselinfo()
    #context['carousel'] = carouselentries
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('auctionhouses.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    aucid = None
    if request.method == 'GET':
        if 'aucid' in request.GET.keys():
            aucid = str(request.GET['aucid'])
    if not aucid:
        return HttpResponse("Invalid Request: Request is missing auction Id")
    auctionobj = None
    try:
        auctionobj = Auction.objects.get(id=aucid)
    except:
        return HttpResponse("Could not identify a auction with Id %s"%aucid)
    # Find all auctions from the same auction house as the selected auction
    auctionslist = []
    relatedartists = {}
    context = {}
    auctioninfo = {}
    chunksize = 4
    try:
        auctioninfo = pickle.loads(redis_instance.get('ah_auctioninfo_%s'%auctionobj.id))
    except:
        auctioninfo = {}
    if auctioninfo.keys().__len__() == 0:
        auctionsqset = Auction.objects.filter(auctionhouse_id__iexact=auctionobj.auctionhouse_id).order_by('-auctionstartdate')
        auctionhouse = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
        auchousename = auctionhouse.housename
        auctioninfo = {'auctionname' : auctionobj.auctionname, 'auctionhouse' : auchousename, 'auctionlocation' : auctionhouse.location, 'auctionurl' : auctionobj.auctionurl, 'coverimage' : auctionobj.coverimage, 'auctiondate' : auctionobj.auctionstartdate, 'auctionid' : auctionobj.auctionid, 'aucid' : auctionobj.id}
        try:
            redis_instance.set('ah_auctioninfo_%s'%auctionobj.id, pickle.dumps(auctioninfo))
        except:
            pass
    context['auctioninfo'] = auctioninfo
    overviewlots = []
    alllots = []
    try:
        alllots = pickle.loads(redis_instance.get('ah_alllots_%s'%auctionobj.id))
        overviewlots = pickle.loads(redis_instance.get('ah_overviewlots_%s'%auctionobj.id))
        auctionslist = pickle.loads(redis_instance.get('ah_auctionslist_%s'%auctionobj.id))
        relatedartists = pickle.loads(redis_instance.get('ah_relatedartists_%s'%auctionobj.id))
    except:
        alllots = []
        overviewlots = []
    if alllots.__len__() == 0:
        # This is going to be a very costly query. Lot (lots table) needs to be indexed on auction field. 
        lotsqset = Lot.objects.filter(auction_id=auctionobj.id)#.order_by('priority')
        lctr = 0
        for lotobj in lotsqset:
            artworkobj = Artwork.objects.get(id=lotobj.artwork_id)
            artworkname = artworkobj.artworkname
            artworkdesc = artworkobj.description
            lotartistqset = LotArtist.objects.filter(artist_id=artworkobj.artist_id)
            lotartistobj = lotartistqset[0]
            artistname = lotartistobj.artist_name
            d = {'title' : artworkname, 'description' : artworkdesc, 'artistname' : str(artistname), 'loturl' : lotobj.source, 'lotimage' : lotobj.lotimage1, 'medium' : lotobj.medium, 'size' : lotobj.sizedetails, 'estimate' : str(lotobj.lowestimateUSD) + " - " + str(lotobj.highestimateUSD), 'soldprice' : str(lotobj.soldpriceUSD), 'currency' : "USD", 'nationality' : lotartistobj.nationality, 'lid' : lotobj.id}
            if lctr < chunksize:
                overviewlots.append(d)
            else:
                alllots.append(d)
            lctr += 1
        try:
            redis_instance.set('ah_overviewlots_%s'%auctionobj.id, pickle.dumps(overviewlots))
            redis_instance.set('ah_alllots_%s'%auctionobj.id, pickle.dumps(alllots))
        except:
            pass
        for auction in auctionsqset:
            auctionhouseobj = AuctionHouse.objects.get(id=auction.auctionhouse_id)
            d = {'auctionname' : auction.auctionname, 'auctionhouse' : auctionhouseobj.housename, 'auctionlocation' : auctionhouseobj.location, 'description' : '', 'auctionurl' : '', 'lotsurl' : '', 'coverimage' : auction.coverimage, 'auctionid' : auction.auctionid, 'aucid' : auction.id, 'auctiondate' : auctionobj.auctionstartdate}
            # Get 'chunksize' number of lots for this auction
            lotsqset = Lot.objects.filter(auction_id=auction.id)#.order_by() # Ordered by priority
            lots = []
            numlots = chunksize
            if numlots > lotsqset.__len__():
                numlots = lotsqset.__len__()
            for lotobj in lotsqset[0:numlots]:
                artworkobj = Artwork.objects.get(id=lotobj.artwork_id)
                artworkname = artworkobj.artworkname
                artworkdesc = artworkobj.description
                lotartistqset = LotArtist.objects.filter(artist_id=artworkobj.artist_id)
                lotartistobj = lotartistqset[0]
                artistname = lotartistobj.artist_name
                ld = {'title' : artworkname, 'description' : artworkdesc, 'artistname' : artistname, 'loturl' : '', 'lotimage' : lotobj.lotimage1, 'medium' : lotobj.medium, 'size' : lotobj.sizedetails, 'estimate' : str(lotobj.lowestimateUSD) + " - " + str(lotobj.highestimateUSD), 'soldprice' : lotobj.soldpriceUSD, 'currency' : "USD", 'nationality' : lotartistobj.nationality, 'lid' : lotobj.id}
                lots.append(ld)
                if artistname not in relatedartists.keys():
                    artistqset = Artist.objects.filter(artistname__iexact=artistname)
                    if artistqset.__len__() > 0:
                        relatedartists[artistname] = [ artistqset[0].id, artworkname, lotobj.lotimage1 ]
            d['lots'] = lots
            auctionslist.append(d)
        try:
            redis_instance.set('ah_auctionslist_%s'%auctionobj.id, pickle.dumps(auctionslist))
            redis_instance.set('ah_relatedartists_%s'%auctionobj.id, pickle.dumps(relatedartists))
        except:
            pass
    context['overviewlots'] = overviewlots
    context['alllots'] = alllots
    context['auctionslist'] = auctionslist
    context['relatedartists'] = relatedartists
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('auctionhouse_details.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def follow(request):
    return HttpResponse("")


def search(request):
    """
    This should return a json response containing a list of dicts.
    The dict keys would be the attributes of an auctionhouse object.
    """
    if request.method != 'GET':
        return HttpResponse(json.dumps({'err' : "Invalid method of call"}))
    searchkey = None
    page = 1
    if request.method == 'GET':
        if 'q' in request.GET.keys():
            searchkey = str(request.GET['q']).strip()
    if not searchkey:
        return HttpResponse(json.dumps({'err' : "Invalid Request: Request is missing search key"}))
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    #print(searchkey)
    maxauctionsperhouse = 8
    startctr = int(page) * maxauctionsperhouse - maxauctionsperhouse
    endctr = int(page) * maxauctionsperhouse
    chunksize = 10 # This number of auction houses (rows of auctions) will be shown per page.
    ahstart = int(page) * chunksize - chunksize
    ahend = int(page) * chunksize
    context = {}
    auctionhousesqset = AuctionHouse.objects.filter(housename__icontains=searchkey)[ahstart:ahend]
    auctionhousematches = []
    for auctionhouse in auctionhousesqset:
        housename = auctionhouse.housename
        auctionsqset = Auction.objects.filter(auctionhouse_id=auctionhouse.id).order_by('-auctionstartdate')[startctr:endctr]
        d = {'housename' : housename, 'houseurl' : auctionhouse.houseurl, 'description' : '', 'ahid' : auctionhouse.id, 'location' : auctionhouse.location}
        auctionslist = []
        coverimage = ""
        if auctionsqset.__len__() == 0:
            continue
        for auction in auctionsqset:
            auctionperiod = ""
            if auction.auctionstartdate.strftime("%d %b, %Y") != "01 Jan, 0001" and auction.auctionstartdate.strftime("%d %b, %Y") != "01 Jan, 1":
                auctionperiod = auction.auctionstartdate.strftime("%d %b, %Y")
                aucenddate = auction.auctionenddate
                if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                    auctionperiod += " - " + str(aucenddate)
            if coverimage == "":
                coverimage = auction.coverimage
                d['coverimage'] = coverimage
            d1 = {'auctionname' : auction.auctionname, 'coverimage' : auction.coverimage, 'auctionurl' : '', 'location' : auctionhouse.location, 'auctionperiod' : auctionperiod, 'aucid' : auction.id, 'ahid' : auctionhouse.id}
            auctionslist.append(d1)
        d['auctionslist'] = auctionslist
        auctionhousematches.append(d)
    context['auctionhousematches'] = auctionhousematches
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
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    return HttpResponse(json.dumps(context))


# Presents information on lots available for sale at the given auction
#@cache_page(CACHE_TTL)
def auctiondetails(request):
    pass



