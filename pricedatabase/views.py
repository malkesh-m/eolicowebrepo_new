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

from gallery.models import Gallery, Event
from login.models import User, Session, WebConfig, Carousel
from login.views import getcarouselinfo
from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse
from artists.models import Artist, Artwork

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
    chunksize = 12
    rows = 6
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    fstartctr = int(page) * chunksize
    fendctr = int(page) * chunksize + chunksize
    context = {}
    date2weeksago = datetime.datetime.now() - datetime.timedelta(days=365)
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
        lotsqset = Lot.objects.all().order_by('-soldpriceUSD')
        lotctr = 0
        for lotobj in lotsqset[:5000]: # Need a restriction on the number of objects, otherwise it might crash the system.
            if lotobj.lotimage1 == "": # We will not show lots with no images.
                continue
            saledate = lotobj.saledate
            saledt = datetime.datetime.combine(saledate, datetime.time(0, 0))
            if saledt < date2weeksago:
                continue
            artworkobj = None
            try:
                artworkobj = Artwork.objects.get(id=lotobj.artwork_id)
            except:
                continue # If we can't find the corresponding artwork for this lot, then we skip it.
            if lotctr > chunksize:
                break
            lotctr += 1
            auctionname, aucid, auctionperiod = "", "", ""
            try:
                auctionobj = Auction.objects.get(id=lotobj.auction_id)
                auctionname = auctionobj.auctionname
                aucid = auctionobj.id
                auctionperiod = auctionobj.auctionstartdate.strftime('%d %b, %Y')
                if auctionobj.auctionenddate.strftime('%d %b, %Y') != "01 Jan, 0001" and auctionobj.auctionenddate.strftime('%d %b, %Y') != "01 Jan, 1":
                    auctionperiod += " - " + auctionobj.auctionenddate.strftime('%d %b, %Y')
                ahid = auctionobj.auctionhouse_id
                try:
                    auctionhouseobj = AuctionHouse.objects.get(id=ahid)
                    auctionhouses[auctionhouseobj.housename] = auctionhouseobj.id
                except:
                    pass
            except:
                pass
            artistname = ""
            try:
                artistobj = Artist.objects.get(id=artworkobj.artist_id)
                artistname = artistobj.artistname
            except:
                pass
            d = {'artworkname' : artworkobj.artworkname, 'saledate' : lotobj.saledate.strftime('%d %b, %Y'), 'soldprice' : lotobj.soldpriceUSD, 'size' : artworkobj.sizedetails, 'medium' : artworkobj.medium, 'description' : artworkobj.description, 'lid' : lotobj.id, 'awid' : artworkobj.id, 'lotimage' : lotobj.lotimage1, 'auctionname' : auctionname, 'aucid' : aucid, 'auctionperiod' : auctionperiod, 'aid' : artworkobj.artist_id, 'artistname' : artistname, 'soldprice' : lotobj.soldpriceUSD}
            entitieslist.append(d)
        for lotobj in lotsqset[:2000]:
            lottitle = ""
            artworkobj = None
            try:
                artworkobj = Artwork.objects.get(id=lotobj.artwork_id)
            except:
                continue # If we can't find the corresponding artwork for this lot, then we skip it.
            lottitle = artworkobj.artworkname
            if lottitle not in uniquefilter.keys():
                filterpdb.append(lottitle)
                uniquefilter[lottitle] = 1
            auctionname = ""
            try:
                auctionobj = Auction.objects.get(id=lotobj.auction_id)
                auctionname = auctionobj.auctionname
                if auctionname not in uniquefilter.keys():
                    filterpdb.append(auctionname)
                    uniquefilter[auctionname] = 1
                ahid = auctionobj.auctionhouse_id
                try:
                    auctionhouseobj = AuctionHouse.objects.get(id=ahid)
                    auctionhouses[auctionhouseobj.housename] = auctionhouseobj.id
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
        try:
            redis_instance.set('pd_filterpdb', pickle.dumps(filterpdb))
            redis_instance.set('pd_entitieslist', pickle.dumps(entitieslist))
            redis_instance.set('pd_auctionhouses', pickle.dumps(auctionhouses))
        except:
            pass
    context['entities'] = entitieslist
    context['filterpdb'] = filterpdb
    context['auctionhouses'] = auctionhouses
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    if request.user.is_authenticated:
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
    #print(searchkey)
    context = {}
    allsearchresults = []
    maxperobjectsearchresults = 30
    auctionsqset = Auction.objects.filter(auctionname__icontains=searchkey).order_by('priority')
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
        if aucctr > maxperobjectsearchresults:
            break
        aucctr += 1
        allsearchresults.append(d)
    artistsqset = Artist.objects.filter(artistname__icontains=searchkey).order_by('priority')
    artctr = 0
    for artist in artistsqset:
        artworkqset = Artwork.objects.filter(artist_id=artist.id)
        for artwork in artworkqset:
            lotqset = Lot.objects.filter(artwork_id=artwork.id)
            for lot in lotqset:
                soldprice = str(lot.soldpriceUSD)
                soldprice = soldprice.replace("$", "")
                d = {'artistname' : artist.artistname, 'lottitle' : artwork.artworkname, 'medium' : lot.medium, 'size' : lot.sizedetails.encode('utf-8'), 'aid' : artist.id, 'birthyear' : artist.birthyear, 'deathyear' : artist.deathyear, 'nationality' : artist.nationality, 'artistimage' : artist.artistimage, 'coverimage' : lot.lotimage1, 'awid' : artwork.id, 'createdate' : artwork.creationstartdate, 'lid' : lot.id, 'obtype' : 'lot', 'aucid' : lot.auction_id, 'soldprice' : soldprice}
                allsearchresults.append(d)
                artctr += 1
                if artctr > maxperobjectsearchresults:
                    break
    artworkqset = Artwork.objects.filter(artworkname__icontains=searchkey).order_by('priority')
    awctr = 0
    for artwork in artworkqset:
        lotqset = Lot.objects.filter(artwork_id=artwork.id)
        for lot in lotqset:
            artistobj = None
            try:
                artistobj = Artist.objects.get(id=artwork.artist_id)
            except:
                continue
            soldprice = str(lot.soldpriceUSD)
            soldprice = soldprice.replace("$", "")
            d = {'artistname' : artistobj.artistname, 'aid' : artistobj.id, 'birthyear' : artistobj.birthyear, 'deathyear' : artistobj.deathyear, 'nationality' : artistobj.nationality, 'lottitle' : artwork.artworkname, 'medium' : lot.medium, 'size' : lot.sizedetails.encode('utf-8'), 'coverimage' : lot.lotimage1, 'awid' : artwork.id, 'createdate' : artwork.creationstartdate, 'lid' : lot.id, 'obtype' : 'lot', 'aucid' : lot.auction_id, 'soldprice' : soldprice}
            awctr += 1
            if awctr > maxperobjectsearchresults:
                break
            allsearchresults.append(d)
    context['allsearchresults'] = allsearchresults
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    return HttpResponse(json.dumps(context))



def dofilter(request):
    if request.method != 'POST':
        return HttpResponse('{ "error" : "Invalid request method"}')
    artistname, lottitle, medium, auctionhouseids, sizespec, sizeunit, saleoutcomes, soldmin, soldmax, estimatemin, estimatemax = "", "", "", "", "", "", "", "", "", "", ""
    requestbody = str(request.body)
    bodycomponents = requestbody.split("&")
    requestdict = {}
    for comp in bodycomponents:
        compparts = comp.split("=")
        if compparts.__len__() > 1:
            compparts[0] = compparts[0].replace("b'", "")
            requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
    endbarPattern = re.compile("\|\s*$")
    if 'artistname' in requestdict.keys():
        artistname = requestdict['artistname'].strip()
    if 'lottitle' in requestdict.keys():
        lottitle = requestdict['lottitle'].strip()
    if 'medium' in requestdict.keys():
        medium = requestdict['medium'].lower()
        medium = endbarPattern.sub("", medium)
    if 'auctionhouse' in requestdict.keys():
        auctionhouseids = requestdict['auctionhouse']
        auctionhouseids = endbarPattern.sub("", auctionhouseids)
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
    ahidlist = []
    mediumlist = []
    solist = []
    sizelist = []
    ahidlist = auctionhouseids.split("|")
    mediumlist = medium.split("|")
    solist = saleoutcomes.split("|")
    sizelist = sizespec.split("|")
    entitieslist = []
    context = {}
    if lottitle != "":
        artworksqset = Artwork.objects.filter(artworkname__icontains=lottitle).order_by('-edited') # Latest first
        for artwork in artworksqset[:settings.PDB_ARTWORKSLIMIT]: # We restrict our search to the latest 10000 entries. 
            artworkname = artwork.artworkname
            awid = artwork.id
            lotqset = Lot.objects.filter(artwork_id=artwork.id)
            artistobj = None
            lartistname, aid = "", ""
            try:
                artistobj = Artist.objects.get(id=artwork.artist_id)
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
                    limage = artwork.image1
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
            d = {'lottitle' : artworkname, 'artistname' : artistname, 'aid' : aid, 'awid' : awid, 'medium' : lmedium, 'size' : lsize, 'saledate' : lsaledate, 'soldprice' : lsoldprice, 'estimate' : lestimate, 'lid' : lid, 'auctionname' : auctionname, 'auctionperiod' : auctionperiod, 'aucid' : aucid, 'auctionhouse' : auctionhousename, 'ahid' : ahid, 'obtype' : 'lot', 'coverimage' : limage}
            # Now check all parameters against user's selected values to determine if this dict should be appended to 'entitieslist'.
            artistflag, titleflag, mediumflag, sizeflag, soldpriceflag, estimateflag, auctionhouseflag = -1, 1, -1, -1, -1, -1, -1
            if artistname != "" and artistname.lower() in lartistname.lower(): # Partial match is considered.
                artistflag = 1
            elif artistname != "":
                artistflag = 0
            else:
                pass
            #if lottitle != "" and lottitle.lower() in artworkname.lower(): # This need not execute. We selected artworks based on title.
            #    titleflag = True
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
            if estimateflag != 0 and sizeflag != 0 and soldpriceflag != 0 and auctionhouseflag != 0 and mediumflag != 0 and artistflag != 0:
                entitieslist.append(d)
    else: # Handle case with parameters other than artwork name.
        artistqset = []
        if artistname != "":
            artistqset = Artist.objects.filter(artistname__icontains=artistname)
        else:
            artistqset = Artist.objects.all().order_by('-edited') # Latest first
        artistqset2 = []
        if artistqset.__len__() > settings.PDB_ARTISTSLIMIT: # Consider only first 5000 records. This is the only way we can execute in a timely manner.
            for artist in artistqset[:settings.PDB_ARTISTSLIMIT]:
                artistqset2.append(artist)
        else:
            for artist in artistqset:
                artistqset2.append(artist)
        for artist in artistqset2:
            artworkqset = Artwork.objects.filter(artist_id=artist.id)
            aid = artist.id
            artistnm = artist.artistname
            for artwork in artworkqset:
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
        mediumflag, sizeflag, soldpriceflag, estimateflag, auctionhouseflag = -1, -1, -1, -1, -1
        if entitieslist.__len__() > 0:
            ectr = 0
            for entity in entitieslist:
                for m in mediumlist:
                    if m in entity['medium'].lower():
                        mediumflag = 1
                        break
                if mediumlist.__len__() > 0 and mediumflag == -1:
                    mediumflag = 0 # User specified medium, but none of them matched this entity's medium.
                for ah in ahidlist:
                    if ah == entity['ahid']:
                        auctionhouseflag = 1
                        break
                if ahidlist.__len__() > 0 and auctionhouseflag == -1:
                    auctionhouseflag = 0
                try:
                    if float(entity['soldprice']) > float(soldmin) and float(entity['soldprice']) < float(soldmax):
                        soldpriceflag = 1
                    else:
                        soldpriceflag = 0
                except:
                    pass
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
                    pass
                else: # Delete this entity from entitieslist
                    entitieslist.pop(ectr)
                    continue
                ectr += 1
        else: # Control should never come here.
            pass
    r_entitieslist = []
    if entitieslist.__len__() > settings.PDB_MAXSEARCHRESULT:
        for d in entitieslist[:settings.PDB_MAXSEARCHRESULT]:
            r_entitieslist.append(d)
    context['allsearchresults'] = r_entitieslist
    return HttpResponse(json.dumps(context))



