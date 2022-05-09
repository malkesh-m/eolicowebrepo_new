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
from django.contrib.auth import logout
from django.template import loader

import os, sys, re, time, datetime
import simplejson as json
import redis

from gallery.models import Gallery, Event, Artist, Artwork
from museum.models import Museum, MuseumEvent, MuseumPieces
from login.models import User, Session, WebConfig, Carousel
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse

# Caching related imports and variables
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def getcarouselinfo():
    entrieslist = []
    countqset = WebConfig.objects.filter(paramname="carousel entries count")
    entriescount = countqset[0].paramvalue
    try:
        entrieslist = redis_instance.get('carouselentries')
    except:
        pass
    if entrieslist.__len__() == 0:
        carouselqset = Carousel.objects.all().order_by('priority', '-edited')
        for e in range(0, int(entriescount)):
            imgpath = carouselqset[e].imagepath
            title = carouselqset[e].title
            text = carouselqset[e].textvalue
            datatype = carouselqset[e].datatype
            dataid = carouselqset[e].data_id
            d = {'img' : imgpath, 'title' : title, 'text' : text, 'datatype' : datatype, 'data_id' : dataid}
            entrieslist.append(d)
        try:
            redis_instance.set('carouselentries', entrieslist)
        except:
            pass
    return entrieslist


#@cache_page(CACHE_TTL)
def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    chunksize = 3
    galleriesdict = {}
    try:
        galleriesdict = redis_instance.get('h_galleriesdict')
    except:
        pass
    if galleriesdict.keys().__len__() == 0:
        galleries = Gallery.objects.all().order_by('priority', '-edited')
        gallerieslist = galleries[0:4]
        for g in gallerieslist:
            gname = g.galleryname
            gloc = g.location
            gimg = g.coverimage
            gurl = g.galleryurl
            gid = g.id
            galleriesdict[gname] = [gloc, gimg, gurl, gid]
        try:
            redis_instance.set('h_galleriesdict', galleriesdict)
        except:
            pass
    context = {'galleries' : galleriesdict}
    artistsdict = {}
    try:
        artistsdict = redis_instance.get('h_artistsdict')
    except:
        pass
    if artistsdict.keys().__len__() == 0:
        artists = Artist.objects.all().order_by('-edited')
        artistslist = artists[0:4]
        for a in artistslist:
            aname = a.artistname
            about = a.about
            aurl = a.profileurl
            aimg = a.squareimage
            anat = a.nationality
            aid = a.id
            artistsdict[aname] = [about, aurl, aimg, anat, aid]
        try:
            redis_instance.set('h_artistsdict', artistsdict)
        except:
            pass
    context['artists'] = artistsdict
    eventsdict = {}
    try:
        eventsdict = redis_instance.get('h_eventsdict')
    except:
        pass
    if eventsdict.keys().__len__() == 0:
        events = Event.objects.all().order_by('priority', '-edited')
        eventslist = events[0:4]
        for e in eventslist:
            ename = e.eventname
            eurl = e.eventurl
            einfo = str(e.eventinfo[0:20]) + "..."
            eperiod = e.eventperiod
            eid = e.id
            eventimage = e.eventimage
            eventsdict[ename] = [eurl, einfo, eperiod, eid, eventimage ]
        try:
            redis_instance.set('h_eventsdict', eventsdict)
        except:
            pass
    context['events'] = eventsdict
    museumsdict = {}
    try:
        museumsdict = redis_instance.get('h_museumsdict')
    except:
        pass
    if museumsdict.keys().__len__() == 0:
        museumsqset = Museum.objects.all().order_by('priority', '-edited')
        museumslist = museumsqset[0:4]
        for mus in museumslist:
            mname = mus.museumname
            murl = mus.museumurl
            minfo = str(mus.description[0:20]) + "..."
            mlocation = mus.location
            mid = mus.id
            mimage = mus.coverimage
            museumsdict[mname] = [murl, minfo, mlocation, mid, mimage ]
        try:
            redis_instance.set('h_museumsdict', museumsdict)
        except:
            pass
    context['museums'] = museumsdict
    upcomingauctions = {}
    try:
        upcomingauctions = redis_instance.get('h_upcomingauctions')
    except:
        pass
    if upcomingauctions.keys().__len__() == 0:
        auctionsqset = Auction.objects.all().order_by('priority', '-edited')
        actr = 0
        srcPattern = re.compile("src=(.*)$")
        for auction in auctionsqset:
            lotsqset = Lot.objects.filter(auction=auction).order_by('priority', '-edited')
            if lotsqset.__len__() == 0:
                continue
            lotobj = lotsqset[0]
            imageloc = lotobj.lotimage1
            spc = re.search(srcPattern, imageloc)
            if spc:
                imageloc = spc.groups()[0]
                imageloc = imageloc.replace("%3A", ":").replace("%2F", "/")
            d = {'auctionname' : auction.auctionname, 'auctionid' : auction.auctionid, 'auctionhouse' : auction.auctionhouse, 'location' : auction.auctionlocation, 'coverimage' : imageloc, 'aucid' : auction.id, 'description' : auction.description, 'auctionurl' : auction.auctionurl, 'lid' : lotobj.id}
            upcomingauctions[auction.auctionname] = d
            actr += 1
            if actr >= chunksize:
                break
        try:
            redis_instance.set('h_upcomingauctions', upcomingauctions)
        except:
            pass
    context['upcomingauctions'] = upcomingauctions
    auctionhouses = []
    try:
        auctionhouses = redis_instance.get('h_auctionhouses')
    except:
        pass
    if auctionhouses.__len__() == 0:
        auchousesqset = AuctionHouse.objects.all().order_by('priority', '-edited')
        actr = 0
        for auchouse in auchousesqset:
            auchousename = auchouse.housename
            auctionsqset = Auction.objects.filter(auctionhouse__iexact=auchousename)
            if auctionsqset.__len__() == 0:
                continue
            print(auctionsqset[0].coverimage)
            d = {'housename' : auchouse.housename, 'aucid' : auctionsqset[0].id, 'location' : auchouse.location, 'description' : auchouse.description, 'coverimage' : auctionsqset[0].coverimage}
            auctionhouses.append(d)
            actr += 1
            if actr >= chunksize:
                break
        try:
            redis_instance.set('h_auctionhouses', auctionhouses)
        except:
            pass
    context['auctionhouses'] = auctionhouses
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('homepage.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def showlogin(request):
    return HttpResponse("")


#@cache_page(CACHE_TTL)
def about(request):
    if request.method == 'GET':
        wcqset = WebConfig.objects.filter(paramname="About")
        #wcqset = WebConfig.objects.filter(path="/about/")
        wcobj = None
        if wcqset.__len__() > 0:
            wcobj = wcqset[0]
        context = {'aboutcontent' : ''}
        if wcobj is not None:
            context['aboutcontent'] = wcobj.paramvalue
            context['aboutid'] = wcobj.id
        carouselentries = getcarouselinfo()
        context['carousel'] = carouselentries
        if request.user.is_authenticated:
            context['adminuser'] = 1
        else:
            context['adminuser'] = 0
        template = loader.get_template('about.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Incorrect request method")


#@cache_page(CACHE_TTL)
def contactus(request):
    if request.method == 'GET':
        wcqset = WebConfig.objects.filter(paramname="ContactUs")
        #wcqset = WebConfig.objects.filter(path="/contactus/")
        wcobj = None
        if wcqset.__len__() > 0:
            wcobj = wcqset[0]
        context = {'contactus' : ''}
        if wcobj is not None:
            context['contactus'] = wcobj.paramvalue
            context['contactid'] = wcobj.id
        carouselentries = getcarouselinfo()
        context['carousel'] = carouselentries
        if request.user.is_authenticated:
            context['adminuser'] = 1
        else:
            context['adminuser'] = 0
        template = loader.get_template('contactus.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Incorrect request method")







