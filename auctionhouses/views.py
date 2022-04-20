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

from gallery.models import Gallery, Event, Artist, Artwork
from login.models import User, Session, WebConfig, Carousel
from login.views import getcarouselinfo
from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse



def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 5
    rows = 6
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    fstartctr = int(page) * chunksize
    fendctr = int(page) * chunksize + chunksize
    auctionhousesqset = AuctionHouse.objects.all().order_by('priority', '-edited')
    context = {}
    auctionhouses = [] # Auctions in various auction houses section.
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
    context['auctionhouses'] = auctionhouses
    featuredshows = [] # Featured shows section, will show 5 top priority auctions only.
    #currentmngshows = [] # Current museum and gallery shows section - To be implemented later. Will need association of auctions to galleries and museums.
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
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    template = loader.get_template('auctionhouses.html')
    return HttpResponse(template.render(context, request))


def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    ahid = None
    if request.method == 'GET':
        if 'ahid' in request.GET.keys():
            ahid = str(request.GET['ahid'])
    if not ahid:
        return HttpResponse("Invalid Request: Request is missing auction house Id")
    auchouseobj = None
    try:
        auchouseobj = AuctionHouse.objects.get(id=ahid)
    except:
        return HttpResponse("Could not identify a auction house with Id %s"%ahid)
    auctionsqset = Auction.objects.filter(auctionhouse__iexact=auchouseobj.housename).order_by('priority', '-edited')
    auctionslist = []
    relatedartists = {}
    context = {}
    chunksize = 5
    for auction in auctionsqset:
        d = {'auctionname' : auction.auctionname, 'auctionhouse' : auction.auctionhouse, 'auctionlocation' : auction.auctionlocation, 'description' : auction.description, 'auctionurl' : auction.auctionurl, 'lotsurl' : auction.lotslistingurl, 'coverimage' : auction.coverimage, 'auctionid' : auction.auctionid, 'aid' : auction.id}
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
    context['auctionslist'] = auctionslist
    context['relatedartists'] = relatedartists
    template = loader.get_template('auctionhouse_details.html')
    return HttpResponse(template.render(context, request))


def follow(request):
    return HttpResponse("")



