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
from artists.models import Artist, Artwork
from auctions.models import Auction, Lot

# Caching related imports and variables
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


#@login_required(login_url='/login/show/')
#@cache_page(CACHE_TTL)
def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 4
    context = {}
    gallerytypes = []
    gallerylocations = {}
    allgalleries = {}
    filtergalleries = []
    try:
        galleriesdict1 = pickle.loads(redis_instance.get('g_galleries1'))
        galleriesdict2 = pickle.loads(redis_instance.get('g_galleries2'))
        galleriesdict3 = pickle.loads(redis_instance.get('g_galleries3'))
        galleriesdict4 = pickle.loads(redis_instance.get('g_galleries4'))
        galleriesdict5 = pickle.loads(redis_instance.get('g_galleries5'))
        gallerytypes = pickle.loads(redis_instance.get('g_gallerytypes'))
        gallerylocations = pickle.loads(redis_instance.get('g_gallerylocations'))
        allgalleries = pickle.loads(redis_instance.get('g_allgalleries'))
        filtergalleries = pickle.loads(redis_instance.get('g_filtergalleries'))
        context['galleries1'] = galleriesdict1
        context['galleries2'] = galleriesdict2
        context['galleries3'] = galleriesdict3
        context['galleries4'] = galleriesdict4
        context['galleries5'] = galleriesdict5
        context['gallerytypes'] = gallerytypes
        context['gallerylocations'] = gallerylocations
        context['allgalleries'] = allgalleries
        context['filtergalleries'] = filtergalleries
    except:
        pass
    if gallerytypes.__len__() == 0 and filtergalleries.__len__() == 0:
        # Find out the distinct gallery types available
        gtypesqset = Gallery.objects.order_by().values_list('gallerytype').distinct()
        lastctr1 = int(page) * chunksize
        lastctr2 = int(page) * chunksize
        lastctr3 = int(page) * chunksize
        lastctr4 = int(page) * chunksize
        lastctr5 = int(page) * chunksize
        #print(gtypesqset)
        galleries1 = Gallery.objects.filter(gallerytype=gtypesqset[0][0])
        galleries2 = Gallery.objects.filter(gallerytype=gtypesqset[1][0])
        galleries3 = Gallery.objects.filter(gallerytype=gtypesqset[2][0])
        galleries4 = Gallery.objects.filter(gallerytype=gtypesqset[3][0])
        galleries5 = Gallery.objects.filter(gallerytype=gtypesqset[4][0])
        startctr1 = lastctr1 - chunksize
        startctr2 = lastctr2 - chunksize
        startctr3 = lastctr3 - chunksize
        startctr4 = lastctr4 - chunksize
        startctr5 = lastctr5 - chunksize
        if lastctr1 > galleries1.__len__():
            lastctr1 = galleries1.__len__()
        if lastctr2 > galleries2.__len__():
            lastctr2 = galleries2.__len__()
        if lastctr3 > galleries3.__len__():
            lastctr3 = galleries3.__len__()
        if lastctr4 > galleries4.__len__():
            lastctr4 = galleries4.__len__()
        if lastctr5 > galleries5.__len__():
            lastctr5 = galleries5.__len__()
        gallerieslist1 = galleries1[startctr1:lastctr1]
        gallerieslist2 = galleries2[startctr2:lastctr2]
        gallerieslist3 = galleries3[startctr3:lastctr3]
        gallerieslist4 = galleries4[startctr4:lastctr4]
        gallerieslist5 = galleries5[startctr5:lastctr5]
        galleriesdict = {}
        for g in gallerieslist1[startctr1:lastctr1]:
            gname = g.galleryname
            gloc = g.location
            gimg = g.coverimage
            gurl = g.galleryurl
            gid = g.id
            if gloc.__len__() > 23:
                location = gloc[:23] + "..."
            else:
                location = gloc
            galleriesdict[gname] = [location, gimg, gurl, gid, gtypesqset[0][0]]
            glocparts = gloc.split(",")
            for gloc in glocparts:
                gloc = gloc.strip()
                if gloc == "":
                    continue
                gallerylocations[gloc] = 1
            allgalleries[gname] = [gloc, gimg, gurl, gid, gtypesqset[0][0]]
            filtergalleries.append(gname)
        context = {'galleries1' : galleriesdict}
        try:
            redis_instance.set('g_galleries1', pickle.dumps(galleriesdict))
        except:
            pass
        galleriesdict = {}
        for g in gallerieslist2[startctr2:lastctr2]:
            gname = g.galleryname
            gloc = g.location
            gimg = g.coverimage
            gurl = g.galleryurl
            gid = g.id
            if gloc.__len__() > 23:
                location = gloc[:23] + "..."
            else:
                location = gloc
            galleriesdict[gname] = [location, gimg, gurl, gid, gtypesqset[1][0]]
            glocparts = gloc.split(",")
            for gloc in glocparts:
                gloc = gloc.strip()
                if gloc == "":
                    continue
                gallerylocations[gloc] = 1
            allgalleries[gname] = [gloc, gimg, gurl, gid, gtypesqset[0][0]]
            filtergalleries.append(gname)
        context['galleries2'] = galleriesdict
        try:
            redis_instance.set('g_galleries2', pickle.dumps(galleriesdict))
        except:
            pass
        galleriesdict = {}
        for g in gallerieslist3[startctr3:lastctr3]:
            gname = g.galleryname
            gloc = g.location
            gimg = g.coverimage
            gurl = g.galleryurl
            gid = g.id
            if gloc.__len__() > 23:
                location = gloc[:23] + "..."
            else:
                location = gloc
            galleriesdict[gname] = [location, gimg, gurl, gid, gtypesqset[2][0]]
            glocparts = gloc.split(",")
            for gloc in glocparts:
                gloc = gloc.strip()
                if gloc == "":
                    continue
                gallerylocations[gloc] = 1
            allgalleries[gname] = [gloc, gimg, gurl, gid, gtypesqset[0][0]]
            filtergalleries.append(gname)
        context['galleries3'] = galleriesdict
        try:
            redis_instance.set('g_galleries3', pickle.dumps(galleriesdict))
        except:
            pass
        galleriesdict = {}
        for g in gallerieslist4[startctr4:lastctr4]:
            gname = g.galleryname
            gloc = g.location
            gimg = g.coverimage
            gurl = g.galleryurl
            gid = g.id
            if gloc.__len__() > 23:
                location = gloc[:23] + "..."
            else:
                location = gloc
            galleriesdict[gname] = [location, gimg, gurl, gid, gtypesqset[3][0]]
            glocparts = gloc.split(",")
            for gloc in glocparts:
                gloc = gloc.strip()
                if gloc == "":
                    continue
                gallerylocations[gloc] = 1
            allgalleries[gname] = [gloc, gimg, gurl, gid, gtypesqset[0][0]]
            filtergalleries.append(gname)
        context['galleries4'] = galleriesdict
        try:
            redis_instance.set('g_galleries4', pickle.dumps(galleriesdict))
        except:
            pass
        galleriesdict = {}
        for g in gallerieslist5[startctr5:lastctr5]:
            gname = g.galleryname
            gloc = g.location
            gimg = g.coverimage
            gurl = g.galleryurl
            gid = g.id
            if gloc.__len__() > 23:
                location = gloc[:23] + "..."
            else:
                location = gloc
            galleriesdict[gname] = [location, gimg, gurl, gid, gtypesqset[4][0]]
            glocparts = gloc.split(",")
            for gloc in glocparts:
                gloc = gloc.strip()
                if gloc == "":
                    continue
                gallerylocations[gloc] = 1
            allgalleries[gname] = [gloc, gimg, gurl, gid, gtypesqset[0][0]]
            filtergalleries.append(gname)
        context['galleries5'] = galleriesdict
        try:
            redis_instance.set('g_galleries5', pickle.dumps(galleriesdict))
        except:
            pass
        context['gallerylocations'] = gallerylocations
        context['allgalleries'] = allgalleries
        context['filtergalleries'] = filtergalleries
        context['gallerytypes'] = [gtypesqset[0][0], gtypesqset[1][0], gtypesqset[2][0], gtypesqset[3][0], gtypesqset[4][0]]
        gallerytypeslist = [gtypesqset[0][0], gtypesqset[1][0], gtypesqset[2][0], gtypesqset[3][0], gtypesqset[4][0]]
        try:
            redis_instance.set('g_gallerylocations', pickle.dumps(gallerylocations))
            redis_instance.set('g_allgalleries', pickle.dumps(allgalleries))
            redis_instance.set('g_filtergalleries', pickle.dumps(filtergalleries))
            redis_instance.set('g_gallerytypes', pickle.dumps(gallerytypeslist))
        except:
            pass
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('gallery.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    gid = None
    if request.method == 'GET':
        if 'gid' in request.GET.keys():
            gid = str(request.GET['gid'])
        page = "1"
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    if not gid:
        return HttpResponse("Invalid Request: Request is missing gid")
    galleryobj = None
    try:
        galleryobj = Gallery.objects.get(id=gid)
    except:
        return HttpResponse("Could not identify a gallery with Id %s"%gid)
    context = {}
    # Get gallery information
    galleryname = galleryobj.galleryname
    glocation = galleryobj.location
    gurl = galleryobj.galleryurl
    gimage = galleryobj.coverimage
    gid = galleryobj.id
    context['gallery'] = {'galleryname' : galleryname, 'gallerylocation' : glocation, 'galleryurl' : gurl, 'galleryimage' : gimage, 'gid' : gid}
    latestevent = {}
    eventsprioritylist = []
    previousevents = []
    try:
        latestevent = pickle.loads(redis_instance.get('g_latestevent_%s'%gid))
        eventsprioritylist = pickle.loads(redis_instance.get('g_eventsprioritylist_%s'%gid))
        previousevents = pickle.loads(redis_instance.get('g_previousevents_%s'%gid))
    except:
        pass
    eventsqset = []
    if latestevent.keys().__len__() == 0 or previousevents.__len__() == 0:
        # Get latest events for this gallery. Also order by 'priority'.
        eventsqset = Event.objects.filter(gallery=galleryobj).order_by('-eventstartdate', 'priority')
        if eventsqset.__len__() > 0:
            latestevent['eventname'] = eventsqset[0].eventname
            latestevent['eventurl'] = eventsqset[0].eventurl
            latestevent['eventinfo'] = eventsqset[0].eventinfo
            latestevent['eventtype'] = eventsqset[0].eventtype
            latestevent['eventstatus'] = eventsqset[0].eventstatus
            latestevent['eventperiod'] = eventsqset[0].eventperiod
            latestevent['eventimage'] = eventsqset[0].eventimage
            latestevent['eventlocation'] = eventsqset[0].eventlocation
            latestevent['eventid'] = eventsqset[0].id
            eventsprioritylist.append(eventsqset[0].eventname)
        try:
            redis_instance.set('g_latestevent_%s'%gid, pickle.dumps(latestevent))
        except:
            pass
        if eventsqset.__len__() > 1:
            for eqset in eventsqset[1:]:
                pevent = {}
                pevent['eventname'] = eqset.eventname
                pevent['eventurl'] = eqset.eventurl
                pevent['eventinfo'] = eqset.eventinfo
                pevent['eventtype'] = eqset.eventtype
                pevent['eventstatus'] = eqset.eventstatus
                pevent['eventperiod'] = eqset.eventperiod
                pevent['eventimage'] = eqset.eventimage
                pevent['eventlocation'] = eqset.eventlocation
                pevent['eventid'] = eqset.id
                previousevents.append(pevent)
                eventsprioritylist.append(eqset.eventname)
        try:
            redis_instance.set('g_previousevents_%s'%gid, pickle.dumps(previousevents))
            redis_instance.set('g_previouseventselection_%s'%gid, pickle.dumps(previousevents[0:4]))
        except:
            pass
    context['latestevent'] = latestevent
    context['previousevents'] = previousevents
    context['previouseventselection'] = previousevents[0:4]
    artistslist = []
    try:
        artistslist = pickle.loads(redis_instance.get('g_artistslist_%s'%gid))
    except:
        pass
    if artistslist.__len__() == 0:
        # Showing 20 artists from the latest featured event only.
        try:
            artistsqset = Artist.objects.filter(event=eventsqset[0]).order_by('-edited', 'priority')
        except:
            artistsqset = []
        max_len = 20
        if artistsqset.__len__() < max_len:
            max_len = artistsqset.__len__()
        for artist in artistsqset[:max_len]:
            adict = {'artistname' : artist.artistname, 'artisturl' : artist.profileurl, 'artistid' : artist.id}
            artistslist.append(adict)
        try:
            redis_instance.set('g_artistslist_%s'%gid, pickle.dumps(artistslist))
        except:
            pass
    context['artists'] = artistslist
    nationalities = []
    try:
        nationalities = pickle.loads(redis_instance.get('g_nationalities_%s'%gid))
    except:
        pass
    if nationalities.__len__() == 0:
        try:
            natqset = Artist.objects.filter(event=eventsqset[0]).order_by().values_list('nationality').distinct()
        except:
            natqset = []
        for nat in natqset:
            nationalities.append(nat[0])
        try:
            redis_instance.set('g_nationalities_%s'%gid, pickle.dumps(nationalities))
        except:
            pass
    context['nationalities'] = nationalities
    # Find all artists belonging to this gallery
    allartists = []
    try:
        allartists = pickle.loads(redis_instance.get('g_allartists_%s'%gid))
    except:
        pass
    if eventsqset.__len__() > 0:
        for evobj in eventsqset:
            artistsqset = Artist.objects.filter(event=evobj).order_by('-edited', 'priority')
            for artist in artistsqset:
                adict = {'artistname' : artist.artistname, 'artisturl' : artist.profileurl, 'artistid' : artist.id}
                allartists.append(adict)
        try:
            redis_instance.set('g_allartists_%s'%gid, pickle.dumps(allartists))
        except:
            pass
    context['allartists'] = allartists
    # Find all artworks belonging to the gallery in an eventwise manner. Artworks will be listed as per 'priority' values.
    # This, along with 'eventsprioritylist' values will list artworks in an eventwise manner, with top priority events on top.
    artcollen = 4
    artrowlen = 7
    startctr = int(page) * artcollen * artrowlen - (artcollen * artrowlen)
    endctr = startctr + (artcollen * artrowlen)
    allartworks1, allartworks2, allartworks3, allartworks4, allartworks = {}, {}, {}, {}, {} # Event names as keys and list of artworks as values.
    filterartists = {}
    try:
        allartworks1 = pickle.loads(redis_instance.get('g_allartworks1_%s'%gid))
        allartworks2 = pickle.loads(redis_instance.get('g_allartworks2_%s'%gid))
        allartworks3 = pickle.loads(redis_instance.get('g_allartworks3_%s'%gid))
        allartworks4 = pickle.loads(redis_instance.get('g_allartworks4_%s'%gid))
        allartworks = pickle.loads(redis_instance.get('g_allartworks_%s'%gid))
        filterartists = pickle.loads(redis_instance.get('g_filterartists_%s'%gid))
    except:
        pass
    if allartworks.keys().__len__() == 0 or filterartists.keys().__len__() == 0:
        artworksqset = Artwork.objects.filter(gallery=galleryobj).order_by('-edited', 'priority')
        for ename in eventsprioritylist:
            allartworks1[ename] = []
            allartworks2[ename] = []
            allartworks3[ename] = []
            allartworks4[ename] = []
            allartworks[ename] = []
        ctr = 1
        for awork in artworksqset[startctr:endctr]:
            evname = awork.event.eventname
            l0 = allartworks[evname]
            d0 = {'artworkname' : str(awork.artworkname), 'creationdate' : str(awork.creationdate), 'gallery' : awork.gallery.galleryname, 'artistname' : str(awork.artistname), 'artistbirthyear' : str(awork.artistbirthyear), 'artistdeathyear' : str(awork.artistdeathyear), 'artistnationality' : str(awork.artistnationality), 'size' : str(awork.size), 'estimate' : str(awork.estimate), 'soldprice' : str(awork.soldprice), 'medium' : str(awork.medium), 'signature' : str(awork.signature), 'letterofauthenticity' : str(awork.letterofauthenticity), 'description' : str(awork.description), 'provenance' : str(awork.provenance), 'literature' : str(awork.literature), 'exhibitions' : str(awork.exhibitions), 'image' : str(awork.image1), 'workurl' : str(awork.workurl), 'awid' : awork.id}
            filterartists[str(awork.artistname)] = 1
            l0.append(d0)
            allartworks[evname] = l0
            if ctr % 4 == 0:
                l = allartworks4[evname]
                d = {'artworkname' : str(awork.artworkname), 'creationdate' : str(awork.creationdate), 'gallery' : awork.gallery.galleryname, 'artistname' : str(awork.artistname), 'artistbirthyear' : str(awork.artistbirthyear), 'artistdeathyear' : str(awork.artistdeathyear), 'artistnationality' : str(awork.artistnationality), 'size' : str(awork.size), 'estimate' : str(awork.estimate), 'soldprice' : str(awork.soldprice), 'medium' : str(awork.medium), 'signature' : str(awork.signature), 'letterofauthenticity' : str(awork.letterofauthenticity), 'description' : str(awork.description), 'provenance' : str(awork.provenance), 'literature' : str(awork.literature), 'exhibitions' : str(awork.exhibitions), 'image' : str(awork.image1), 'workurl' : str(awork.workurl), 'awid' : awork.id}
                l.append(d)
                allartworks4[evname] = l
            elif ctr % 3 == 0:
                l = allartworks3[evname]
                d = {'artworkname' : str(awork.artworkname), 'creationdate' : str(awork.creationdate), 'gallery' : awork.gallery.galleryname, 'artistname' : str(awork.artistname), 'artistbirthyear' : str(awork.artistbirthyear), 'artistdeathyear' : str(awork.artistdeathyear), 'artistnationality' : str(awork.artistnationality), 'size' : str(awork.size), 'estimate' : str(awork.estimate), 'soldprice' : str(awork.soldprice), 'medium' : str(awork.medium), 'signature' : str(awork.signature), 'letterofauthenticity' : str(awork.letterofauthenticity), 'description' : str(awork.description), 'provenance' : str(awork.provenance), 'literature' : str(awork.literature), 'exhibitions' : str(awork.exhibitions), 'image' : str(awork.image1), 'workurl' : str(awork.workurl), 'awid' : awork.id}
                l.append(d)
                allartworks3[evname] = l
            elif ctr % 2 == 0:
                l = allartworks2[evname]
                d = {'artworkname' : str(awork.artworkname), 'creationdate' : str(awork.creationdate), 'gallery' : awork.gallery.galleryname, 'artistname' : str(awork.artistname), 'artistbirthyear' : str(awork.artistbirthyear), 'artistdeathyear' : str(awork.artistdeathyear), 'artistnationality' : str(awork.artistnationality), 'size' : str(awork.size), 'estimate' : str(awork.estimate), 'soldprice' : str(awork.soldprice), 'medium' : str(awork.medium), 'signature' : str(awork.signature), 'letterofauthenticity' : str(awork.letterofauthenticity), 'description' : str(awork.description), 'provenance' : str(awork.provenance), 'literature' : str(awork.literature), 'exhibitions' : str(awork.exhibitions), 'image' : str(awork.image1), 'workurl' : str(awork.workurl), 'awid' : awork.id}
                l.append(d)
                allartworks2[evname] = l
            elif ctr % 1 == 0:
                l = allartworks1[evname]
                d = {'artworkname' : str(awork.artworkname), 'creationdate' : str(awork.creationdate), 'gallery' : awork.gallery.galleryname, 'artistname' : str(awork.artistname), 'artistbirthyear' : str(awork.artistbirthyear), 'artistdeathyear' : str(awork.artistdeathyear), 'artistnationality' : str(awork.artistnationality), 'size' : str(awork.size), 'estimate' : str(awork.estimate), 'soldprice' : str(awork.soldprice), 'medium' : str(awork.medium), 'signature' : str(awork.signature), 'letterofauthenticity' : str(awork.letterofauthenticity), 'description' : str(awork.description), 'provenance' : str(awork.provenance), 'literature' : str(awork.literature), 'exhibitions' : str(awork.exhibitions), 'image' : str(awork.image1), 'workurl' : str(awork.workurl), 'awid' : awork.id}
                l.append(d)
                allartworks1[evname] = l
            ctr += 1
            if ctr > 1 and ctr % 4 == 1: # Basically, if ctr==5, then reset to 1.
                ctr = 1
        try:
            redis_instance.set('g_allartworks1_%s'%gid, pickle.dumps(allartworks1))
            redis_instance.set('g_allartworks2_%s'%gid, pickle.dumps(allartworks2))
            redis_instance.set('g_allartworks3_%s'%gid, pickle.dumps(allartworks3))
            redis_instance.set('g_allartworks4_%s'%gid, pickle.dumps(allartworks4))
            redis_instance.set('g_allartworks_%s'%gid, pickle.dumps(allartworks))
            redis_instance.set('g_filterartists_%s'%gid, pickle.dumps(filterartists))
        except:
            pass
    context['allartworks1'] = allartworks1
    context['allartworks2'] = allartworks2
    context['allartworks3'] = allartworks3
    context['allartworks4'] = allartworks4
    context['allartworks'] = allartworks
    context['filterartists'] = filterartists
    context['eventsprioritylist'] = eventsprioritylist
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('gallery_details.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def eventdetails(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    gevid = None
    if request.method == 'GET':
        if 'gevid' in request.GET.keys():
            gevid = str(request.GET['gevid'])
    if not gevid:
        return HttpResponse("Invalid Request: Request is missing gevid")
    geventobj = None
    try:
        geventobj = Event.objects.get(id=gevid)
    except:
        return HttpResponse("Could not identify a gallery event with Id %s"%gevid)
    context = {}
    eventdata = {'eventname' : geventobj.eventname, 'eventinfo' : geventobj.eventinfo, 'eventperiod' : geventobj.eventperiod, 'eventtype' : geventobj.eventtype, 'eventimage' : geventobj.eventimage, 'eventlocation' : geventobj.eventlocation, 'gid' : geventobj.gallery.id, 'gevid' : geventobj.id}
    context['eventinfo'] = eventdata
    galobj = geventobj.gallery
    otherevents = {} # These will be events from the same gallery as the one in eventinfo.
    eventsqset = Event.objects.filter(gallery=galobj).order_by('priority', '-edited')
    for gev in eventsqset:
        eventname = gev.eventname
        d = {'eventinfo' : gev.eventinfo, 'eventperiod' : gev.eventperiod, 'eventtype' : gev.eventtype, 'eventimage' : gev.eventimage, 'eventlocation' : gev.eventlocation, 'gid' : gev.gallery.id, 'eventid' : gev.id}
        otherevents[eventname] = d
    context['otherevents'] = otherevents
    artists = []
    artistsqset = Artist.objects.filter(event=geventobj).order_by('priority', '-edited')
    for artist in artistsqset:
        d = {'artistname' : artist.artistname, 'nationality' : artist.nationality, 'birthdate' : artist.birthdate, 'deathdate' : artist.deathdate, 'about' : artist.about, 'artistimage' : artist.squareimage, 'artistid' : artist.id}
        artists.append(d)
    context['artists'] = artists
    # Get all artworks from the selected event
    artworksqset = Artwork.objects.filter(event=geventobj).order_by('priority', '-edited')
    allartworks1 = {}
    allartworks2 = {}
    allartworks3 = {}
    allartworks4 = {}
    actr = 0
    for artwork in artworksqset:
        eventname = artwork.event.eventname
        if actr == 0:
            if eventname in allartworks1.keys():
                l = allartworks1[eventname]
                d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'awid' : artwork.id}
                l.append(d)
                allartworks1[eventname] = l
            else:
                l = []
                d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'awid' : artwork.id}
                l.append(d)
                allartworks1[eventname] = l
        elif actr == 1:
            if eventname in allartworks2.keys():
                l = allartworks2[eventname]
                d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'awid' : artwork.id}
                l.append(d)
                allartworks2[eventname] = l
            else:
                l = []
                d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'awid' : artwork.id}
                l.append(d)
                allartworks2[eventname] = l
        elif actr == 2:
            if eventname in allartworks3.keys():
                l = allartworks3[eventname]
                d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'awid' : artwork.id}
                l.append(d)
                allartworks3[eventname] = l
            else:
                l = []
                d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'awid' : artwork.id}
                l.append(d)
                allartworks3[eventname] = l
        elif actr == 3:
            if eventname in allartworks4.keys():
                l = allartworks4[eventname]
                d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'awid' : artwork.id}
                l.append(d)
                allartworks4[eventname] = l
            else:
                l = []
                d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'awid' : artwork.id}
                l.append(d)
                allartworks4[eventname] = l
        if actr == 3:
            actr = 0
        else:
            actr += 1
    context['allartworks1'] = allartworks1
    context['allartworks2'] = allartworks2
    context['allartworks3'] = allartworks3
    context['allartworks4'] = allartworks4
    # Get all artists whose works are in the same event as the selected event.
    allartists = []
    for artist in artistsqset:
        d = {'artistname' : artist.artistname, 'nationality' : artist.nationality, 'birthdate' : artist.birthdate, 'deathdate' : artist.deathdate, 'about' : artist.about, 'artistimage' : artist.squareimage, 'artistid' : artist.id}
        allartists.append(d)
    context['allartists'] = allartists
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('event_details.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def artworkdetails(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    awid = None
    if request.method == 'GET':
        if 'awid' in request.GET.keys():
            awid = str(request.GET['awid'])
    if not awid:
        return HttpResponse("Invalid Request: Request is missing awid")
    artworkobj = None
    try:
        artworkobj = Artwork.objects.get(id=awid)
    except:
        return HttpResponse("Could not identify a artwork with Id %s"%awid)
    context = {}
    artworkinfo = {'artworkname' : artworkobj.artworkname, 'creationdate' : artworkobj.creationdate, 'artistname' : artworkobj.artistname, 'artistbirthyear' : artworkobj.artistbirthyear, 'artistdeathyear' : artworkobj.artistdeathyear, 'artistnationality' : artworkobj.artistnationality, 'size' : artworkobj.size, 'medium' : artworkobj.medium, 'description' : artworkobj.description, 'provenance' : artworkobj.provenance, 'artworkimage' : artworkobj.image1, 'estimate' : artworkobj.estimate, 'soldprice' : artworkobj.soldprice, 'awid' : artworkobj.id}
    context['artworkinfo'] = artworkinfo
    # Get all artworks by the same artist
    allartworks = []
    artworksqset = Artwork.objects.filter(artistname=artworkobj.artistname).order_by('priority', '-edited')
    uniqueartworks = {}
    eventslist = []
    for artwork in artworksqset:
        d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'provenance' : artwork.provenance, 'artworkimage' : artwork.image1, 'estimate' : artwork.estimate, 'soldprice' : artwork.soldprice, 'awid' : artwork.id}
        eventslist.append(artwork.event)
        if artwork.artworkname not in uniqueartworks.keys():
            allartworks.append(d)
            uniqueartworks[artwork.artworkname] = artwork.id
        else:
            pass
    # Only 3 notable artworks are to be shown
    if allartworks.__len__() < 3:
        context['allartworks'] = allartworks
    else:
        context['allartworks'] = allartworks[0:3]
    # Get all events featuring the artist of the selected artwork.
    allevents = []
    relatedartists = []
    for gev in eventslist:
        d = {'eventname' : gev.eventname, 'eventinfo' : gev.eventinfo, 'eventtype' : gev.eventtype, 'eventperiod' : gev.eventperiod, 'eventimage' : gev.eventimage, 'eventlocation' : gev.eventlocation, 'gevid' : gev.id}
        allevents.append(d)
    artistsqset = Artist.objects.filter(event=artworkobj.event)
    uniqueartists = {}
    for artist in artistsqset:
        if artist.artistname not in uniqueartists.keys():
            d = {'artistname' : artist.artistname, 'nationality' : artist.nationality, 'birthdate' : artist.birthdate, 'deathdate' : artist.deathdate, 'about' : artist.about, 'squareimage' : artist.squareimage, 'aid' : artist.id}
            relatedartists.append(d)
            uniqueartists[artist.artistname] = artist.id
    context['allevents'] = allevents
    context['relatedartists'] = relatedartists
    allartworks1 = []
    allartworks2 = []
    allartworks3 = []
    allartworks4 = []
    uniqueartworks = {}
    # Get all artworks by the same artist in 4 lists for 4 columns
    actr = 0
    for artwork in artworksqset:
        if actr == 0:
            d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'provenance' : artwork.provenance, 'artworkimage' : artwork.image1, 'estimate' : artwork.estimate, 'soldprice' : artwork.soldprice, 'awid' : artwork.id}
            if artwork.artworkname not in uniqueartworks.keys():
                allartworks1.append(d)
                uniqueartworks[artwork.artworkname] = artwork.id
        elif actr == 1:
            d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'provenance' : artwork.provenance, 'artworkimage' : artwork.image1, 'estimate' : artwork.estimate, 'soldprice' : artwork.soldprice, 'awid' : artwork.id}
            if artwork.artworkname not in uniqueartworks.keys():
                allartworks2.append(d)
                uniqueartworks[artwork.artworkname] = artwork.id
        elif actr == 2:
            d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'provenance' : artwork.provenance, 'artworkimage' : artwork.image1, 'estimate' : artwork.estimate, 'soldprice' : artwork.soldprice, 'awid' : artwork.id}
            if artwork.artworkname not in uniqueartworks.keys():
                allartworks3.append(d)
                uniqueartworks[artwork.artworkname] = artwork.id
        elif actr == 3:
            d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'provenance' : artwork.provenance, 'artworkimage' : artwork.image1, 'estimate' : artwork.estimate, 'soldprice' : artwork.soldprice, 'awid' : artwork.id}
            if artwork.artworkname not in uniqueartworks.keys():
                allartworks4.append(d)
                uniqueartworks[artwork.artworkname] = artwork.id
        if actr == 3:
            actr = 0
        else:
            actr += 1
    context['allartworks1'] = allartworks1
    context['allartworks2'] = allartworks2
    context['allartworks3'] = allartworks3
    context['allartworks4'] = allartworks4
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('artwork_details.html')
    return HttpResponse(template.render(context, request))

    
def search(request):
    """
    This should return a json response containing a list of dicts.
    The dict keys would be the attributes of an gallery object.
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


