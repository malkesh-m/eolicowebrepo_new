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
    try:
        entitieslist = pickle.loads(redis_instance.get('pd_entitieslist'))
        filterpdb = pickle.loads(redis_instance.get('pd_filterpdb'))
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
            filterpdb.append(lottitle)
            auctionname = ""
            try:
                auctionobj = Auction.objects.get(id=lotobj.auction_id)
                auctionname = auctionobj.auctionname
                filterpdb.append(auctionname)
            except:
                pass
            artistname = ""
            try:
                artistobj = Artist.objects.get(id=artworkobj.artist_id)
                artistname = artistobj.artistname
                filterpdb.append(artistname)
            except:
                pass
        try:
            redis_instance.set('pd_filterpdb', pickle.dumps(filterpdb))
            redis_instance.set('pd_entitieslist', pickle.dumps(entitieslist))
        except:
            pass
    context['entities'] = entitieslist
    context['filterpdb'] = filterpdb
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
                d = {'artistname' : artist.artistname, 'lottitle' : artwork.artworkname, 'medium' : lot.medium, 'size' : lot.sizedetails, 'aid' : artist.id, 'birthyear' : artist.birthyear, 'deathyear' : artist.deathyear, 'nationality' : artist.nationality, 'artistimage' : artist.artistimage, 'coverimage' : lot.lotimage1, 'awid' : artwork.id, 'createdate' : artwork.creationstartdate, 'lid' : lot.id, 'obtype' : 'lot', 'aucid' : lot.auction_id}
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
            d = {'artistname' : artistobj.artistname, 'aid' : artistobj.id, 'birthyear' : artistobj.birthyear, 'deathyear' : artistobj.deathyear, 'nationality' : artistobj.nationality, 'lottitle' : artwork.artworkname, 'medium' : lot.medium, 'size' : lot.sizedetails, 'coverimage' : lot.lotimage1, 'awid' : artwork.id, 'createdate' : artwork.creationstartdate, 'lid' : lot.id, 'obtype' : 'lot', 'aucid' : lot.auction_id}
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





