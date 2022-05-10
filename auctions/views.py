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
    chunksize = 4
    rows = 6
    featuredsize = 4
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    startctr = (chunksize * rows) * (int(page) -1) + featuredsize
    endctr = (chunksize * rows) * int(page) + featuredsize
    context = {}
    highlightslist = []
    allartists = {}
    allauctions = {}
    featuredauctions = {}
    filterauctions = []
    try:
        highlightslist = pickle.loads(redis_instance.get('ac_highlightslist'))
    except:
        highlightslist = []
    if highlightslist.__len__() == 0:
        highlightsqset = Lot.objects.all().order_by('priority', '-edited')
        for hlobj in highlightsqset[0:chunksize]:
            d = {'title' : hlobj.lottitle, 'loturl' : hlobj.loturl, 'image' : hlobj.lotimage1, 'description' : hlobj.lotdescription, 'artist' : hlobj.artistname}
            highlightslist.append(d)
        try:
            redis_instance.set('ac_highlightslist', pickle.dumps(highlightslist))
        except:
            pass
    context['highlights'] = highlightslist
    try:
        featuredauctions = pickle.loads(redis_instance.get('ac_featuredauctions'))
        filterauctions = pickle.loads(redis_instance.get('ac_filterauctions'))
        allartists = pickle.loads(redis_instance.get('ac_allartists'))
        allauctions = pickle.loads(redis_instance.get('ac_allauctions'))
    except:
        featuredauctions = {}
        filterauctions = []
        allartists = {}
        allauctions = {}
    if allauctions.__len__() == 0:
        auctionsqset = Auction.objects.all().order_by('priority', '-edited')
        try:
            for auction in auctionsqset[rowstartctr:rowendctr]:
                auctionname = auction.auctionname
                auctionurl = auction.auctionurl
                auctionlots = Lot.objects.filter(auction=auction).order_by() # Ordered by priority
                lotslist = []
                for lotobj in auctionlots:
                    d = {'title' : lotobj.lottitle, 'loturl' : lotobj.loturl, 'image' : lotobj.lotimage1, 'description' : lotobj.lotdescription, 'artist' : lotobj.artistname, 'auctionurl' : auctionurl, 'lid' : lotobj.id}
                    lotslist.append(d)
                if lotslist.__len__() > chunksize:
                    featuredauctions[auctionname] = lotslist[0:chunksize]
                else:
                    featuredauctions[auctionname] = lotslist
                filterauctions.append(auctionname)
        except:
            pass
        context['featuredauctions'] = featuredauctions
        context['filterauctions'] = filterauctions
        try:
            redis_instance.set('ac_featuredauctions', pickle.dumps(featuredauctions))
            redis_instance.set('ac_filterauctions', pickle.dumps(filterauctions))
        except:
            pass
        for auction in auctionsqset:
            auctionname = auction.auctionname
            auction_id = auction.id
            allauctions[auctionname] = []
            auctionlots = Lot.objects.filter(auction=auction)
            for lotobj in auctionlots:
                artistname = lotobj.artistname
                if artistname not in allartists.keys():
                    allartists[artistname] = []
                    d = {'title' : lotobj.lottitle, 'loturl' : lotobj.loturl, 'image' : lotobj.lotimage1, 'description' : lotobj.lotdescription, 'lid' : lotobj.id, 'artist' : lotobj.artistname}
                    allartists[artistname].append(d)
                    allauctions[auctionname].append(d)
                else:
                    l = allartists[artistname]
                    d = {'title' : lotobj.lottitle, 'loturl' : lotobj.loturl, 'image' : lotobj.lotimage1, 'description' : lotobj.lotdescription, 'lid' : lotobj.id, 'artist' : lotobj.artistname}
                    l.append(d)
                    allartists[artistname] = l
                    allauctions[auctionname].append(d)
        context['allartists'] = allartists
        context['allauctions'] = allauctions
        try:
            redis_instance.set('ac_allartists', pickle.dumps(allartists))
            redis_instance.set('ac_allauctions', pickle.dumps(allauctions))
        except:
            pass
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('auction.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    lid = None
    if request.method == 'GET':
        if 'lid' in request.GET.keys():
            lid = str(request.GET['lid'])
    if not lid:
        return HttpResponse("Invalid Request: Request is missing lot Id")
    lotobj = None
    try:
        lotobj = Lot.objects.get(id=lid)
    except:
        return HttpResponse("Could not find the lot identified by the lot Id (%s)"%lid)
    chunksize = 4
    rows = 2
    context = {}
    lotinfo = {'title' : lotobj.lottitle, 'description' : lotobj.lotdescription, 'artist' : lotobj.artistname, 'birth' : lotobj.artistbirth, 'death' : lotobj.artistdeath, 'nationality' : lotobj.artistnationality, 'medium' : lotobj.medium, 'size' : lotobj.size, 'auctionname' : lotobj.auction.auctionname, 'estimate' : lotobj.estimate, 'soldprice' : lotobj.soldprice, 'currency' : lotobj.currency, 'provenance' : lotobj.provenance, 'literature' : lotobj.literature, 'exhibitions' : lotobj.exhibited, 'image1' : lotobj.lotimage1, 'image2' : lotobj.lotimage2, 'image3' : lotobj.lotimage3, 'image4' : lotobj.lotimage4, 'url' : lotobj.loturl, 'category' : lotobj.category, 'created' : '', 'lotid' : lotobj.id}
    context['lotinfo'] = lotinfo
    try:
        aboutartist = pickle.loads(redis_instance.get('ac_aboutartist_%s'%lotobj.auction.id))
    except:
        aboutartist = {}
    if aboutartist.keys().__len__() == 0:
        artistqset = Artist.objects.filter(artistname__iexact=lotobj.artistname)
        aboutartist = {'artistname' : '', 'nationality' : '', 'birth' : '', 'death' : '', 'about' : '', 'image' : '', 'aid' : ''}
        if artistqset.__len__() > 0:
            aboutartist = {'artistname' : artistqset[0].artistname, 'nationality' : artistqset[0].nationality, 'birth' : artistqset[0].birthdate, 'death' : artistqset[0].deathdate, 'about' : artistqset[0].about, 'image' : artistqset[0].squareimage, 'aid' : artistqset[0].id}
        context['aboutartist'] = aboutartist
        try:
            redis_instance.set('ac_aboutartist_%s'%lotobj.auction.id, pickle.dumps(aboutartist))
        except:
            pass
    otherworks = [[], [], [], []]
    relatedworks = [[], [], [], []]
    allartists = {}
    try:
        otherworks = pickle.loads(redis_instance.get('ac_otherworks_%s'%lotobj.auction.id))
        relatedworks = pickle.loads(redis_instance.get('ac_relatedworks_%s'%lotobj.auction.id))
        allartists = pickle.loads(redis_instance.get('ac_allartists_%s'%lotobj.auction.id))
    except:
        otherworks = [[], [], [], []]
        relatedworks = [[], [], [], []]
        allartists = {}
    if otherworks[0].__len__() == 0:
        lotsqset = Lot.objects.filter(auction=lotobj.auction).order_by() # Ordered by priority, by default
        numlots = chunksize * rows
        if lotsqset.__len__() < numlots:
            numlots = lotsqset.__len__()
        actr = 0
        rctr = 0
        for lot in lotsqset[0:numlots]:
            d = {'title' : lot.lottitle, 'artist' : lot.artistname, 'image' : lot.lotimage1, 'medium' : lot.medium, 'estimate' : lot.estimate, 'lid' : lot.id}
            l = otherworks[rctr]
            l.append(d)
            otherworks[rctr] = l
            rctr += 1
            if rctr == 4:
                rctr = 0
            if lot.artistname in allartists.keys():
                l = allartists[lot.artistname]
                try:
                    artistobj = Artist.objects.get(artistname__iexact=lot.artistname)
                except:
                    continue # If there is no corresponding artist object, we cannot continue
                l.append({'title' : lot.lottitle, 'image' : lot.lotimage1, 'medium' : lot.medium, 'estimate' : lot.estimate, 'lid' : lot.id, 'aid' : artistobj.id})
                allartists[lot.artistname] = l
            else:
                l = []
                try:
                    artistobj = Artist.objects.get(artistname__iexact=lot.artistname)
                except:
                    continue # If there is no corresponding artist object, we cannot continue
                l.append({'title' : lot.lottitle, 'image' : lot.lotimage1, 'medium' : lot.medium, 'estimate' : lot.estimate, 'lid' : lot.id, 'aid' : artistobj.id})
                allartists[lot.artistname] = l
        context['otherworks'] = otherworks
        try:
            redis_instance.set('ac_otherworks_%s'%lotobj.auction.id, pickle.dumps(otherworks))
        except:
            pass
    if relatedworks[0].__len__() == 0:
        relatedqset = Lot.objects.filter(artistname__iexact=lotobj.artistname).order_by()
        numlots = chunksize * rows
        if relatedqset.__len__() < numlots:
            numlots = relatedqset.__len__()
        rctr = 0
        for lot in relatedqset[0:numlots]:
            d = {'title' : lot.lottitle, 'artist' : lot.artistname, 'image' : lot.lotimage1, 'medium' : lot.medium, 'estimate' : lot.estimate, 'lid' : lot.id}
            l = relatedworks[rctr]
            l.append(d)
            relatedworks[rctr] = l
            rctr += 1
            if rctr == 4:
                rctr = 0
            if lot.artistname in allartists.keys(): # This is the part that would be executed, not the else clause
                l2 = allartists[lot.artistname]
                try:
                    artistobj = Artist.objects.get(artistname__iexact=lot.artistname)
                except:
                    continue # If there is no corresponding artist object, we cannot continue
                l2.append({'title' : lot.lottitle, 'nationality' : lot.artistnationality, 'birth' : lot.artistbirth, 'death' : lot.artistdeath, 'image' : lot.lotimage1, 'medium' : lot.medium, 'estimate' : lot.estimate, 'lid' : lot.id, 'aid' : artistobj.id})
                allartists[lot.artistname] = l2
            else: # This should never be executed. Bad omen... bad things will happen if this is executed.
                l2 = []
                try:
                    artistobj = Artist.objects.get(artistname__iexact=lot.artistname)
                except:
                    continue # If there is no corresponding artist object, we cannot continue
                l2.append({'title' : lot.lottitle, 'nationality' : lot.artistnationality, 'birth' : lot.artistbirth, 'death' : lot.artistdeath, 'image' : lot.lotimage1, 'medium' : lot.medium, 'estimate' : lot.estimate, 'lid' : lot.id, 'aid' : artistobj.id})
                allartists[lot.artistname] = l2
        context['relatedworks'] = relatedworks
        context['allartists'] = allartists
        try:
            redis_instance.set('ac_relatedworks_%s'%lotobj.auction.id, pickle.dumps(relatedworks))
            redis_instance.set('ac_allartists_%s'%lotobj.auction.id, pickle.dumps(allartists))
        except:
            pass
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('auction_details.html')
    return HttpResponse(template.render(context, request))
    

#@cache_page(CACHE_TTL)
def follow(request):
    return HttpResponse("")


def search(request):
    """
    This should return a json response containing a list of dicts.
    The dict keys would be the attributes of an auction object.
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
    return HttpResponse("{}")





