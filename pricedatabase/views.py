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
    try:
        entitieslist = pickle.loads(redis_instance.get('pd_entitieslist'))
    except:
        entitieslist = []
    if entitieslist.__len__() == 0:
        lotsqset = Lot.objects.all().order_by('-soldpriceUSD')
        lotctr = 0
        for lotobj in lotsqset[:5000]: # Need a restriction on the number of objects, otherwise it might crash the system.
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
    context['entities'] = entitieslist
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




