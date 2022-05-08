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

from gallery.models import Gallery, Event, Artist, Artwork
from login.models import User, Session, WebConfig, Carousel
from login.views import getcarouselinfo
from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles

# Caching related imports and variables
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


#@cache_page(CACHE_TTL)
def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    pagemap = {'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5, 'f' : 6, 'g' : 7, 'h' : 8, 'i' : 9, 'j' : 10, 'k' : 11, 'l' : 12, 'm' : 13, 'n' : 14, 'o' : 15, 'p' : 16, 'q' : 17, 'r' : 18, 's' : 19, 't' : 20, 'u' : 21, 'v' : 22, 'w' : 23, 'x' : 24, 'y' : 25, 'z' : 26}
    pageno = "a"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            pageno = str(request.GET['page'])
    page = pagemap[pageno]
    chunksize = 4
    rows = 6
    featuredsize = 4
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    startctr = (chunksize * rows) * (int(page) -1) + featuredsize
    endctr = (chunksize * rows) * int(page) + featuredsize
    context = {}
    featuredartists = []
    artistsqset = Artist.objects.filter(artistname__istartswith=pageno).order_by('priority', '-edited')
    allartistsqset = Artist.objects.all()
    uniqartists = {}
    for artist in artistsqset[0:featuredsize]:
        if artist.artistname.title() not in uniqartists.keys():
            d = {'artistname' : artist.artistname.title(), 'nationality' : artist.nationality, 'birthdate' : str(artist.birthdate), 'deathdate' : str(artist.deathdate), 'about' : artist.about, 'profileurl' : artist.profileurl, 'squareimage' : artist.squareimage, 'aid' : str(artist.id)}
            artworkqset = Artwork.objects.filter(artistname__icontains=artist.artistname).order_by('priority')
            if artworkqset.__len__() == 0:
                #continue
                d['artworkname'] = ""
                d['artworkimage'] = ""
                d['artworkdate'] = ""
                d['awid'] = ""
                d['atype'] = "0" # Artists with no related artwork
            else:
                d['artworkname'] = artworkqset[0].artworkname
                d['artworkimage'] = artworkqset[0].image1
                d['artworkdate'] = artworkqset[0].creationdate
                d['awid'] = artworkqset[0].id
                d['atype'] = "1" # Artists with available related artwork
            featuredartists.append(d)
            uniqartists[artist.artistname.title()] = 1
    context['featuredartists'] = featuredartists
    allartists = []
    rctr = 0
    while rctr < rows:
        allartists.append([]) # 'allartists' is a list of lists, and the inner list contains dicts specified by the variable 'd' below.
        rctr += 1
    rctr = 0
    actr = 0
    uniqueartists = {}
    uniqueartworks = {}
    eventtypesdict = {}
    eventtypeslist = []
    if artistsqset.__len__() > featuredsize:
        for artist in artistsqset[startctr:endctr]:
            #print(artist.artistname)
            d = {'artistname' : artist.artistname, 'nationality' : artist.nationality, 'birthdate' : str(artist.birthdate), 'deathdate' : str(artist.deathdate), 'about' : artist.about, 'profileurl' : artist.profileurl, 'squareimage' : artist.squareimage, 'aid' : str(artist.id)}
            artworkqset = Artwork.objects.filter(artistname__icontains=artist.artistname).order_by() # Ordered by 'priority' - descending.
            if artworkqset.__len__() == 0:
                continue
            if artist.artistname.title() not in uniqueartists.keys():
                uniqueartists[artist.artistname.title()] = 1
            else:
                continue
            artworkobj = artworkqset[0]
            eventtype = artworkobj.event.eventtype
            if artworkobj.artworkname.title() not in uniqueartworks.keys():
                d['artworkname'] = artworkobj.artworkname.title()
                #print(d['artworkname'])
                uniqueartworks[artworkobj.artworkname.title()] = 1
            else:
                awctr = 0
                awfound = 0
                while awctr < artworkqset.__len__() - 1: # Iterate over all artworks by the artist under consideration
                    awctr += 1
                    artworkobj = artworkqset[awctr]
                    if artworkobj.artworkname.title() not in uniqueartworks.keys(): # Set flag if we have a new artwork
                        awfound = 1
                        break
                if awfound: # Add artwork if it has not been encountered before.
                    uniqueartworks[artworkobj.artworkname.title()] = 1
                    d['artworkname'] = artworkobj.artworkname.title()
                else: # Skip this artist if no new artworks could be found.
                    continue
            d['artworkimage'] = artworkobj.image1
            d['artworkdate'] = artworkobj.creationdate
            d['awid'] = artworkobj.id
            d['artworkmedium'] = artworkobj.medium
            d['artworkestimate'] = artworkobj.estimate
            d['eventtype'] = eventtype
            if actr < chunksize:
                l = allartists[rctr]
                l.append(d)
                allartists[rctr] = l
                actr += 1
                if eventtype in eventtypesdict.keys():
                    eventtypesdict[eventtype] += 1
                else:
                    eventtypesdict[eventtype] = 1
            else:
                actr = 0
                rctr += 1
            if rctr == rows:
                break
    context['allartists'] = allartists
    context['eventtypes'] = eventtypesdict
    context['uniqueartists'] = uniqueartists
    context['uniqueartworks'] = uniqueartworks
    filterartists = []
    for artist in allartistsqset[:2000]:
        filterartists.append(artist.artistname)
    context['filterartists'] = filterartists
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('artist.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    aid = None
    if request.method == 'GET':
        if 'aid' in request.GET.keys():
            aid = str(request.GET['aid'])
    if not aid:
        return HttpResponse("Invalid Request: Request is missing aid")
    chunksize = 9
    artistobj = None
    context = {}
    try:
        artistobj = Artist.objects.get(id=aid)
    except:
        context['error'] = "Artist with the given identifier (%s) doesn't exist"%aid
        template = loader.get_template('artist_details.html')
        return HttpResponse(template.render(context, request))
    artistname = artistobj.artistname
    # Get all artworks by the given artist.
    allartworks = []
    allartworks1 = []
    allartworks2 = []
    allartworks3 = []
    allartworks4 = []
    artworksqset = Artwork.objects.filter(artistname=artistname.title()).order_by('priority')
    uniqueartworks = {}
    actr = 0
    for artwork in artworksqset:
        d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'provenance' : artwork.provenance, 'literature' : artwork.literature, 'exhibitions' : artwork.exhibitions, 'href' : artwork.workurl, 'estimate' : artwork.estimate, 'awid' : artwork.id}
        if artwork.artworkname not in uniqueartworks.keys():
            allartworks.append(d)
            uniqueartworks[artwork.artworkname] = artwork.id
            if actr == 0:
                allartworks1.append(d)
            elif actr == 1:
                allartworks2.append(d)
            elif actr == 2:
                allartworks3.append(d)
            elif actr == 3:
                allartworks4.append(d)
                actr = 0
                continue
            actr += 1
    artistinfo = {'name' : artistobj.artistname, 'nationality' : artistobj.nationality, 'birthdate' : artistobj.birthdate, 'deathdate' : artistobj.deathdate, 'profileurl' : artistobj.profileurl, 'desctiption' : artistobj.about, 'image' : artistobj.largeimage, 'gender' : artistobj.gender, 'about' : artistobj.about, 'artistid' : artistobj.id}
    context['allartworks'] = allartworks
    context['allartworks1'] = allartworks1
    context['allartworks2'] = allartworks2
    context['allartworks3'] = allartworks3
    context['allartworks4'] = allartworks4
    context['artistinfo'] = artistinfo
    relatedartists = [] # List of artists related to the artist under consideration through an event.
    artistevents = {} # All events featuring the artist under consideration.
    artistgalleries = {} # All galleries where artworks of the artist under consideration are displayed.
    relatedartistqset = None
    try:
        eventobj = artistobj.event
        # Related Artists can be sought out based on the 'event' or on 'nationality'. Though 'event' is a better
        # way to seek out "Related" artists, we may use 'nationality' for faster processing. Unfortunately, this
        # is a query that cannot be cached, so it has to be picked up from the DB every time.
        relatedartistqset = Artist.objects.filter(event=eventobj)
    except:
        eventobj = None
        relatedartistqset = Artist.objects.filter(nationality__icontains=artistobj.nationality)
    for artist in relatedartistqset:
        d = {'artistname' : artist.artistname, 'nationality' : artist.nationality, 'birthdate' : str(artist.birthdate), 'deathdate' : str(artist.deathdate), 'about' : artist.about, 'profileurl' : artist.profileurl, 'squareimage' : artist.squareimage, 'aid' : str(artist.id)}
        artworkqset = Artwork.objects.filter(artistname__icontains=artist.artistname).order_by('priority', '-edited')
        if artworkqset.__len__() == 0:
            continue
        d['artworkname'] = artworkqset[0].artworkname
        d['artworkimage'] = artworkqset[0].image1
        d['artworkdate'] = artworkqset[0].creationdate
        d['artworkdescription'] = artworkqset[0].description
        d['awid'] = artworkqset[0].id
        if relatedartists.__len__() < chunksize:
            relatedartists.append(d)
    for artwork in artworksqset:
        eventname = artwork.event.eventname
        eventurl = artwork.event.eventurl
        eventinfo = artwork.event.eventinfo
        eventperiod = artwork.event.eventperiod
        eventimage = artwork.event.eventimage
        eventlocation = artwork.event.eventlocation
        evid = artwork.event.id
        l = artistevents.keys()
        if l.__len__() < chunksize and eventname not in l:
            artistevents[eventname] = {'eventurl' : eventurl, 'eventinfo' : eventinfo, 'eventperiod' : eventperiod, 'eventimage' : eventimage, 'eventlocation' : eventlocation, 'evid' : evid}
        galleryname = artwork.gallery.galleryname
        location = artwork.gallery.location
        description = artwork.gallery.description
        galleryurl = artwork.gallery.galleryurl
        coverimage = artwork.gallery.coverimage
        l = artistgalleries.keys()
        if l.__len__() < chunksize and galleryname not in l:
            artistgalleries[galleryname] = {'location' : location, 'description' : description, 'galleryurl' : galleryurl, 'coverimage' : coverimage}
    context['relatedartists'] = relatedartists
    context['artistevents'] = artistevents
    context['artistgalleries'] = artistgalleries
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('artist_details.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def follow(request):
    return HttpResponse("")


def search(request):
    """
    This should return a json response containing a list of dicts.
    The dict keys would be the attributes of an artist object.
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




