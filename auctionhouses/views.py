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

from gallery.models import Gallery, Event, Artist, Artwork
from login.models import User, Session, WebConfig, Carousel
from login.views import getcarouselinfo
from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse

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
    fstartctr = int(page) * chunksize
    fendctr = int(page) * chunksize + chunksize
    context = {}
    auctionhouses = [] # Auctions in various auction houses section.
    filterauctionhouses = []
    featuredshows = [] # Featured shows section, will show 5 top priority auctions only.
    currentmngshows = {} # Current museum and gallery shows section - keys are auction houses, values are list of priority auctions in each house. Will need association of auctions to galleries and museums, which is to be implemented later.
    try:
        filterauctionhouses = redis_instance.get('ah_filterauctionhouses')
        auctionhouses = redis_instance.get('ah_auctionhouses')
        featuredshows = redis_instance.get('ah_featuredshows')
    except:
        filterauctionhouses = []
        auctionhouses = []
        featuredshows = []
    if auctionhouses.__len__() == 0:
        auctionhousesqset = AuctionHouse.objects.all().order_by('priority', '-edited')
        if auctionhousesqset.__len__() <= fstartctr:
            fstartctr = 0
        for auctionhouse in auctionhousesqset[fstartctr:]:
            d = {'housename' : auctionhouse.housename, 'houseurl' : auctionhouse.houseurl, 'description' : auctionhouse.description, 'image' : auctionhouse.coverimage, 'ahid' : auctionhouse.id, 'location' : auctionhouse.location}
            auctionsqset = Auction.objects.filter(auctionhouse__iexact=auctionhouse.housename)
            auctionslist = []
            for auction in auctionsqset:
                d1 = {'auctionname' : auction.auctionname, 'coverimage' : auction.coverimage, 'auctionurl' : auction.auctionurl, 'location' : auction.auctionlocation, 'description' : auction.description, 'aucid' : auction.id}
                auctionslist.append(d1)
            d['auctionslist'] = auctionslist
            auctionhouses.append(d)
            filterauctionhouses.append(auctionhouse.housename)
        context['auctionhouses'] = auctionhouses
        context['filterauctionhouses'] = filterauctionhouses
        try:
            redis_instance.set('ah_auctionhouses', auctionhouses)
            redis_instance.set('ah_filterauctionhouses', filterauctionhouses)
        except:
            pass
        for auctionhouse in auctionhousesqset[:fstartctr]:
            d = {'housename' : auctionhouse.housename, 'houseurl' : auctionhouse.houseurl, 'description' : auctionhouse.description, 'image' : auctionhouse.coverimage, 'ahid' : auctionhouse.id, 'location' : auctionhouse.location}
            auctionsqset = Auction.objects.filter(auctionhouse__iexact=auctionhouse.housename)
            auctionslist = []
            for auction in auctionsqset:
                d1 = {'auctionname' : auction.auctionname, 'coverimage' : auction.coverimage, 'auctionurl' : auction.auctionurl, 'location' : auction.auctionlocation, 'description' : auction.description, 'aucid' : auction.id, 'auctiondate' : str(auction.auctiondate)}
                auctionslist.append(d1)
            d['auctionslist'] = auctionslist
            featuredshows.append(d)
        context['featuredshows'] = featuredshows
        try:
            redis_instance.set('ah_featuredshows', featuredshows)
        except:
            pass
    else:
        context['auctionhouses'] = auctionhouses
        context['filterauctionhouses'] = filterauctionhouses
        context['featuredshows'] = featuredshows
    try:
        currentmngshows = redis_instance.get('ah_currentmngshows')
    except:
        currentmngshows = {}
    if currentmngshows.keys().__len__() == 0:
        auctionsqset = Auction.objects.all().order_by('priority', '-edited')
        for auction in auctionsqset:
            auctionhouse = auction.auctionhouse.title()
            if auctionhouse in currentmngshows.keys():
                l = currentmngshows[auctionhouse]
                d = {'auctionname' : auction.auctionname, 'coverimage' : auction.coverimage, 'auctionurl' : auction.auctionurl, 'location' : auction.auctionlocation, 'description' : auction.description, 'aucid' : auction.id, 'auctiondate' : str(auction.auctiondate)}
                l.append(d)
                currentmngshows[auctionhouse] = l
            else:
                l = []
                d = {'auctionname' : auction.auctionname, 'coverimage' : auction.coverimage, 'auctionurl' : auction.auctionurl, 'location' : auction.auctionlocation, 'description' : auction.description, 'aucid' : auction.id, 'auctiondate' : str(auction.auctiondate)}
                l.append(d)
                currentmngshows[auctionhouse] = l
        context['currentmngshows'] = currentmngshows
        try:
            redis_instance.set('ah_currentmngshows', currentmngshows)
        except:
            pass
    else:
        context['currentmngshows'] = currentmngshows
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    if request.user.is_authenticated:
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
        auctioninfo = redis_instance.get('ah_auctioninfo_%s'%auctionobj.id)
    except:
        auctioninfo = {}
    if auctioninfo.keys().__len__() == 0:
        auctionsqset = Auction.objects.filter(auctionhouse__iexact=auctionobj.auctionhouse).order_by('priority', '-edited')
        auctioninfo = {'auctionname' : auctionobj.auctionname, 'auctionhouse' : auctionobj.auctionhouse, 'auctionlocation' : auctionobj.auctionlocation, 'description' : auctionobj.description, 'auctionurl' : auctionobj.auctionurl, 'lotsurl' : auctionobj.lotslistingurl, 'coverimage' : auctionobj.coverimage, 'auctiondate' : auctionobj.auctiondate, 'auctionid' : auctionobj.auctionid, 'aucid' : auctionobj.id}
        try:
            redis_instance.set('ah_auctioninfo_%s'%auctionobj.id, auctioninfo)
        except:
            pass
    context['auctioninfo'] = auctioninfo
    overviewlots = []
    alllots = []
    try:
        alllots = redis_instance.get('ah_alllots_%s'%auctionobj.id)
        overviewlots = redis_instance.get('ah_overviewlots_%s'%auctionobj.id)
        auctionslist = redis_instance.get('ah_auctionslist_%s'%auctionobj.id)
        relatedartists = redis_instance.get('ah_relatedartists_%s'%auctionobj.id)
    except:
        alllots = []
        overviewlots = []
    if alllots.__len__() == 0:
        # This is going to be a very costly query. Lot (lots table) needs to be indexed on auction field. 
        lotsqset = Lot.objects.filter(auction=auctionobj).order_by('priority')
        lctr = 0
        for lotobj in lotsqset:
            d = {'title' : lotobj.lottitle, 'description' : lotobj.lotdescription, 'artistname' : lotobj.artistname, 'loturl' : lotobj.loturl, 'lotimage' : lotobj.lotimage1, 'medium' : lotobj.medium, 'size' : lotobj.size, 'estimate' : lotobj.estimate, 'soldprice' : lotobj.soldprice, 'currency' : lotobj.currency, 'nationality' : lotobj.artistnationality, 'lid' : lotobj.id}
            if lctr < chunksize:
                overviewlots.append(d)
            else:
                alllots.append(d)
            lctr += 1
        try:
            redis_instance.set('ah_overviewlots_%s'%auctionobj.id, overviewlots)
            redis_instance.set('ah_alllots_%s'%auctionobj.id, alllots)
        except:
            pass
        for auction in auctionsqset:
            d = {'auctionname' : auction.auctionname, 'auctionhouse' : auction.auctionhouse, 'auctionlocation' : auction.auctionlocation, 'description' : auction.description, 'auctionurl' : auction.auctionurl, 'lotsurl' : auction.lotslistingurl, 'coverimage' : auction.coverimage, 'auctionid' : auction.auctionid, 'aucid' : auction.id, 'auctiondate' : auctionobj.auctiondate}
            # Get 'chunksize' number of lots for this auction
            lotsqset = Lot.objects.filter(auction=auction).order_by() # Ordered by priority
            lots = []
            numlots = chunksize
            if numlots > lotsqset.__len__():
                numlots = lotsqset.__len__()
            for lotobj in lotsqset[0:numlots]:
                ld = {'title' : lotobj.lottitle, 'description' : lotobj.lotdescription, 'artistname' : lotobj.artistname, 'loturl' : lotobj.loturl, 'lotimage' : lotobj.lotimage1, 'medium' : lotobj.medium, 'size' : lotobj.size, 'estimate' : lotobj.estimate, 'soldprice' : lotobj.soldprice, 'currency' : lotobj.currency, 'nationality' : lotobj.artistnationality, 'lid' : lotobj.id}
                lots.append(ld)
                if lotobj.artistname not in relatedartists.keys():
                    artistqset = Artist.objects.filter(artistname__iexact=lotobj.artistname)
                    if artistqset.__len__() > 0:
                        relatedartists[lotobj.artistname] = [ artistqset[0].id, lotobj.lottitle, lotobj.lotimage1 ]
            d['lots'] = lots
            auctionslist.append(d)
        try:
            redis_instance.set('ah_auctionslist_%s'%auctionobj.id, auctionslist)
            redis_instance.set('ah_relatedartists_%s'%auctionobj.id, relatedartists)
        except:
            pass
    context['overviewlots'] = overviewlots
    context['alllots'] = alllots
    context['auctionslist'] = auctionslist
    context['relatedartists'] = relatedartists
    if request.user.is_authenticated:
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
    if request.method == 'GET':
        if 'q' in request.GET.keys():
            searchkey = str(request.GET['q']).strip()
    if not searchkey:
        return HttpResponse(json.dumps({'err' : "Invalid Request: Request is missing search key"}))
    #print(searchkey)
    return HttpResponse("{}")


# Presents information on lots available for sale at the given auction
#@cache_page(CACHE_TTL)
def auctiondetails(request):
    pass



