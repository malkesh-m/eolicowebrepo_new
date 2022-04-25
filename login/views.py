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
from gallery.models import Gallery, Event, Artist, Artwork
from museum.models import Museum, MuseumEvent, MuseumPieces
from login.models import User, Session, WebConfig, Carousel
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse


def getcarouselinfo():
    entrieslist = []
    countqset = WebConfig.objects.filter(paramname="carousel entries count")
    entriescount = countqset[0].paramvalue
    carouselqset = Carousel.objects.all().order_by('priority', '-edited')
    for e in range(0, int(entriescount)):
        imgpath = carouselqset[e].imagepath
        title = carouselqset[e].title
        text = carouselqset[e].textvalue
        datatype = carouselqset[e].datatype
        dataid = carouselqset[e].data_id
        d = {'img' : imgpath, 'title' : title, 'text' : text, 'datatype' : datatype, 'data_id' : dataid}
        entrieslist.append(d)
    return entrieslist


def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    chunksize = 3
    galleries = Gallery.objects.all().order_by('priority', '-edited')
    gallerieslist = galleries[0:4]
    galleriesdict = {}
    for g in gallerieslist:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        gid = g.id
        galleriesdict[gname] = [gloc, gimg, gurl, gid]
    context = {'galleries' : galleriesdict}
    artists = Artist.objects.all().order_by('-edited')
    artistslist = artists[0:4]
    artistsdict = {}
    for a in artistslist:
        aname = a.artistname
        about = a.about
        aurl = a.profileurl
        aimg = a.squareimage
        anat = a.nationality
        aid = a.id
        artistsdict[aname] = [about, aurl, aimg, anat, aid]
    context['artists'] = artistsdict
    events = Event.objects.all().order_by('priority', '-edited')
    eventslist = events[0:4]
    eventsdict = {}
    for e in eventslist:
        ename = e.eventname
        eurl = e.eventurl
        einfo = str(e.eventinfo[0:20]) + "..."
        eperiod = e.eventperiod
        eid = e.id
        eventimage = e.eventimage
        eventsdict[ename] = [eurl, einfo, eperiod, eid, eventimage ]
    context['events'] = eventsdict
    museumsqset = Museum.objects.all().order_by('priority', '-edited')
    museumslist = museumsqset[0:4]
    museumsdict = {}
    for mus in museumslist:
        mname = mus.museumname
        murl = mus.museumurl
        minfo = str(mus.description[0:20]) + "..."
        mlocation = mus.location
        mid = mus.id
        mimage = mus.coverimage
        museumsdict[mname] = [murl, minfo, mlocation, mid, mimage ]
    context['museums'] = museumsdict
    upcomingauctions = {}
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
    context['upcomingauctions'] = upcomingauctions
    auctionhouses = []
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
    context['auctionhouses'] = auctionhouses
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    template = loader.get_template('homepage.html')
    return HttpResponse(template.render(context, request))


def showlogin(request):
    return HttpResponse("")


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
        template = loader.get_template('about.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Incorrect request method")


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
        template = loader.get_template('contactus.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Incorrect request method")







