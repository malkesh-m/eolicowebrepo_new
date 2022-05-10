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
from artists.models import Artist, Artwork
from auctions.models import Auction, Lot

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
    try:
        featuredartists = pickle.loads(redis_instance.get('at_featuredartists'))
    except:
        featuredartists = []
    uniqartists = {}
    if featuredartists.__len__() == 0:
        artistsqset = Artist.objects.filter(artistname__istartswith=pageno).order_by('priority', '-edited')
        allartistsqset = Artist.objects.all()
        for artist in artistsqset[0:featuredsize]:
            if artist.artistname.title() not in uniqartists.keys():
                if artist.nationality == "na":
                    artist.nationality = ""
                if artist.birthyear == 0:
                    artist.birthyear = ""
                prefix = ""
                if artist.prefix != "" and artist.prefix != "na":
                    prefix = artist.prefix + " "
                d = {'artistname' : prefix + artist.artistname.title(), 'nationality' : artist.nationality, 'birthdate' : str(artist.birthyear), 'deathdate' : str(artist.deathyear), 'about' : artist.description, 'profileurl' : '', 'artistimage' : artist.artistimage, 'aid' : str(artist.id)}
                artworkqset = Artwork.objects.filter(artist_id=artist.id).order_by('priority')
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
                    d['artworkdate'] = artworkqset[0].creationenddate
                    d['awid'] = artworkqset[0].id
                    d['atype'] = "1" # Artists with available related artwork
                featuredartists.append(d)
                uniqartists[artist.artistname.title()] = 1
        try:
            redis_instance.set('at_featuredartists', pickle.dumps(featuredartists))
        except:
            pass
    else:
        pass
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
    eventtypeslist = []
    try:
        uniqueartists = pickle.loads(redis_instance.get('at_uniqueartists'))
        uniqueartworks = pickle.loads(redis_instance.get('at_uniqueartworks'))
        allartists = pickle.loads(redis_instance.get('at_allartists'))
    except:
        pass
    if allartists[0].__len__() == 0:
        if artistsqset.__len__() > featuredsize:
            for artist in artistsqset[startctr:endctr]:
                #print(artist.artistname)
                if artist.nationality == "na":
                    artist.nationality = ""
                if artist.birthyear == 0:
                    artist.birthyear = ""
                prefix = ""
                if artist.prefix != "" and artist.prefix != "na":
                    prefix = artist.prefix + " "
                d = {'artistname' : prefix + artist.artistname, 'nationality' : artist.nationality, 'birthdate' : str(artist.birthyear), 'deathdate' : str(artist.deathyear), 'about' : artist.description, 'profileurl' : '', 'artistimage' : artist.artistimage, 'aid' : str(artist.id)}
                artworkqset = Artwork.objects.filter(artist_id=artist.id).order_by() # Ordered by 'priority' - descending.
                if artworkqset.__len__() == 0:
                    continue
                if artist.artistname.title() not in uniqueartists.keys():
                    uniqueartists[artist.artistname.title()] = 1
                else:
                    continue
                artworkobj = artworkqset[0]
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
                d['artworkdate'] = artworkobj.creationenddate
                d['awid'] = artworkobj.id
                d['artworkmedium'] = artworkobj.medium
                if actr < chunksize:
                    l = allartists[rctr]
                    l.append(d)
                    allartists[rctr] = l
                    actr += 1
                else:
                    actr = 0
                    rctr += 1
                if rctr == rows:
                    break
            try:
                redis_instance.set('at_allartists', pickle.dumps(allartists))
                redis_instance.set('at_uniqueartists', pickle.dumps(uniqueartists))
                redis_instance.set('at_uniqueartworks', pickle.dumps(uniqueartworks))
            except:
                pass    
    context['allartists'] = allartists
    context['uniqueartists'] = uniqueartists
    context['uniqueartworks'] = uniqueartworks
    filterartists = []
    try:
        filterartists = pickle.loads(redis_instance.get('at_filterartists'))
    except:
        pass
    if filterartists.__len__() == 0:
        for artist in allartistsqset[:2000]:
            filterartists.append(artist.artistname)
        try:
            redis_instance.set('at_filterartists', pickle.dumps(filterartists))
        except:
            pass
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
    try:
        allartworks = pickle.loads(redis_instance.get('at_allartworks_%s'%artistobj.id))
        allartworks1 = pickle.loads(redis_instance.get('at_allartworks1_%s'%artistobj.id))
        allartworks2 = pickle.loads(redis_instance.get('at_allartworks2_%s'%artistobj.id))
        allartworks3 = pickle.loads(redis_instance.get('at_allartworks3_%s'%artistobj.id))
        allartworks4 = pickle.loads(redis_instance.get('at_allartworks4_%s'%artistobj.id))
    except:
        pass
    uniqueartworks = {}
    actr = 0
    if allartworks.__len__() == 0:
        artworksqset = Artwork.objects.filter(artist_id=aid).order_by('priority')
        for artwork in artworksqset:
            d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationstartdate, 'size' : artwork.sizedetails, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'provenance' : '', 'literature' : artwork.literature, 'exhibitions' : artwork.exhibitions, 'href' : '', 'estimate' : '', 'awid' : artwork.id}
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
        try:
            redis_instance.set('at_allartworks_%s'%artistobj.id, pickle.dumps(allartworks))
            redis_instance.set('at_allartworks1_%s'%artistobj.id, pickle.dumps(allartworks1))
            redis_instance.set('at_allartworks2_%s'%artistobj.id, pickle.dumps(allartworks2))
            redis_instance.set('at_allartworks3_%s'%artistobj.id, pickle.dumps(allartworks3))
            redis_instance.set('at_allartworks4_%s'%artistobj.id, pickle.dumps(allartworks4))
        except:
            pass
    prefix = ""
    if artistobj.prefix != "" and artistobj.prefix != "na":
        prefix = artistobj.prefix + " "
    artistinfo = {'name' : prefix + artistobj.artistname, 'nationality' : artistobj.nationality, 'birthdate' : artistobj.birthyear, 'deathdate' : artistobj.deathyear, 'profileurl' : '', 'desctiption' : artistobj.description, 'image' : artistobj.artistimage, 'gender' : '', 'about' : artistobj.bio, 'artistid' : artistobj.id}
    context['allartworks'] = allartworks
    context['allartworks1'] = allartworks1
    context['allartworks2'] = allartworks2
    context['allartworks3'] = allartworks3
    context['allartworks4'] = allartworks4
    context['artistinfo'] = artistinfo
    relatedartists = [] # List of artists related to the artist under consideration through an event.
    artistevents = {} # All events featuring the artist under consideration.
    relatedartistqset = None
    try:
        relatedartists = pickle.loads(redis_instance.get('at_relatedartists_%s'%artistobj.id))
        artistevents = pickle.loads(redis_instance.get('at_artistevents_%s'%artistobj.id))
    except:
        pass
    if relatedartists.__len__() == 0:
        try:
            genre = artistobj.genre
            # Related Artists can be sought out based on the 'genre' or on 'nationality'. Though 'genre' is a better
            # way to seek out "Related" artists, we may use 'nationality' for faster processing. Unfortunately, this
            # is a query that cannot be cached, so it has to be picked up from the DB every time.
            relatedartistqset = Artist.objects.filter(genre__icontains=genre)
        except:
            genre = None
            relatedartistqset = Artist.objects.filter(nationality__icontains=artistobj.nationality)
        for artist in relatedartistqset:
            prefix = ""
            if artist.prefix != "" and artist.prefix != "na":
                prefix = artist.prefix + " "
            d = {'artistname' : prefix + artist.artistname, 'nationality' : artist.nationality, 'birthdate' : str(artist.birthyear), 'deathdate' : str(artist.deathyear), 'about' : artist.bio, 'desctiption' : artistobj.description, 'profileurl' : '', 'image' : artist.artistimage, 'aid' : str(artist.id)}
            artworkqset = Artwork.objects.filter(artist_id=artist.id).order_by('priority', '-edited')
            if artworkqset.__len__() == 0:
                continue
            d['artworkname'] = artworkqset[0].artworkname
            d['artworkimage'] = artworkqset[0].image1
            d['artworkdate'] = artworkqset[0].creationstartdate
            d['artworkdescription'] = artworkqset[0].description
            d['awid'] = artworkqset[0].id
            if relatedartists.__len__() < chunksize:
                relatedartists.append(d)
        for artwork in artworksqset:
            lotqset = Lot.objects.filter(artwork_id=artwork.id)
            if lotqset.__len__() == 0:
                continue
            auctionid = lotqset[0].auction_id
            auctionsqset = Auction.objects.filter(id=auctionid)
            if auctionsqset.__len__() == 0:
                continue
            eventname = auctionsqset[0].auctionname
            eventurl = auctionsqset[0].auctionurl
            eventinfo = ''
            eventperiod = auctionsqset[0].auctionstartdate.strftime("%d %b, %Y") + " - " + auctionsqset[0].auctionenddate.strftime("%d %b, %Y")
            eventimage = auctionsqset[0].coverimage
            eventlocation = ''
            aucid = auctionsqset[0].id
            l = artistevents.keys()
            if l.__len__() < chunksize and eventname not in l:
                artistevents[eventname] = {'eventurl' : eventurl, 'eventinfo' : eventinfo, 'eventperiod' : eventperiod, 'eventimage' : eventimage, 'eventlocation' : eventlocation, 'aucid' : aucid}
        try:
            redis_instance.set('at_relatedartists_%s'%artistobj.id, pickle.dumps(relatedartists))
            redis_instance.set('at_artistevents_%s'%artistobj.id, pickle.dumps(artistevents))
        except:
            pass
    context['relatedartists'] = relatedartists
    context['artistevents'] = artistevents
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
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            pageno = str(request.GET['page'])
    page = int(pageno)
    chunksize = 4
    rows = 6
    featuredsize = 4
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    startctr = (chunksize * rows) * (int(page) -1) + featuredsize
    endctr = (chunksize * rows) * int(page) + featuredsize
    context = {}
    featuredartists = []
    uniqartists = {}
    try:
        featuredartists = pickle.loads(redis_instance.get('at_featuredartists_%s'%searchkey.lower()))
    except:
        featuredartists = []
    uniqartists = {}
    if featuredartists.__len__() == 0:
        matchingartistsqset = Artist.objects.filter(artistname__icontains=searchkey).order_by('priority')
        allartistsqset = Artist.objects.all()
        for artist in matchingartistsqset[0:featuredsize]:
            if artist.artistname.title() not in uniqartists.keys():
                if artist.nationality == "na":
                    artist.nationality = ""
                if artist.birthyear == 0:
                    artist.birthyear = ""
                prefix = ""
                if artist.prefix != "" and artist.prefix != "na":
                    prefix = artist.prefix + " "
                d = {'artistname' : prefix + artist.artistname.title(), 'nationality' : artist.nationality, 'birthdate' : str(artist.birthyear), 'deathdate' : str(artist.deathyear), 'about' : artist.description, 'profileurl' : '', 'artistimage' : artist.artistimage, 'aid' : str(artist.id)}
                artworkqset = Artwork.objects.filter(artist_id=artist.id).order_by('priority')
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
                    d['artworkdate'] = artworkqset[0].creationenddate
                    d['awid'] = artworkqset[0].id
                    d['atype'] = "1" # Artists with available related artwork
                featuredartists.append(d)
                uniqartists[artist.artistname.title()] = 1
        try:
            redis_instance.set('at_featuredartists_%s'%searchkey.lower(), pickle.dumps(featuredartists))
        except:
            pass
    else:
        pass
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
    eventtypeslist = []
    try:
        uniqueartists = pickle.loads(redis_instance.get('at_uniqueartists_%s'%searchkey.lower()))
        uniqueartworks = pickle.loads(redis_instance.get('at_uniqueartworks_%s'%searchkey.lower()))
        allartists = pickle.loads(redis_instance.get('at_allartists_%s'%searchkey.lower()))
    except:
        pass
    if allartists[0].__len__() == 0:
        if matchingartistsqset.__len__() > featuredsize:
            for artist in matchingartistsqset[startctr:endctr]:
                #print(artist.artistname)
                if artist.nationality == "na":
                    artist.nationality = ""
                if artist.birthyear == 0:
                    artist.birthyear = ""
                prefix = ""
                if artist.prefix != "" and artist.prefix != "na":
                    prefix = artist.prefix + " "
                d = {'artistname' : prefix + artist.artistname, 'nationality' : artist.nationality, 'birthdate' : str(artist.birthyear), 'deathdate' : str(artist.deathyear), 'about' : artist.description, 'profileurl' : '', 'artistimage' : artist.artistimage, 'aid' : str(artist.id)}
                artworkqset = Artwork.objects.filter(artist_id=artist.id).order_by() # Ordered by 'priority' - descending.
                if artworkqset.__len__() == 0:
                    continue
                if artist.artistname.title() not in uniqueartists.keys():
                    uniqueartists[artist.artistname.title()] = 1
                else:
                    continue
                artworkobj = artworkqset[0]
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
                d['artworkdate'] = artworkobj.creationenddate
                d['awid'] = artworkobj.id
                d['artworkmedium'] = artworkobj.medium
                if actr < chunksize:
                    l = allartists[rctr]
                    l.append(d)
                    allartists[rctr] = l
                    actr += 1
                else:
                    actr = 0
                    rctr += 1
                if rctr == rows:
                    break
            try:
                redis_instance.set('at_allartists_%s'%searchkey.lower(), pickle.dumps(allartists))
                redis_instance.set('at_uniqueartists_%s'%searchkey.lower(), pickle.dumps(uniqueartists))
                redis_instance.set('at_uniqueartworks_%s'%searchkey.lower(), pickle.dumps(uniqueartworks))
            except:
                pass    
    context['allartists'] = allartists
    context['uniqueartists'] = uniqueartists
    context['uniqueartworks'] = uniqueartworks
    filterartists = []
    try:
        filterartists = pickle.loads(redis_instance.get('at_filterartists'))
    except:
        pass
    if filterartists.__len__() == 0:
        for artist in allartistsqset[:2000]:
            filterartists.append(artist.artistname)
        try:
            redis_instance.set('at_filterartists', pickle.dumps(filterartists))
        except:
            pass
    context['filterartists'] = filterartists
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    #template = loader.get_template('artist.html')
    #return HttpResponse(template.render(context, request))
    return HttpResponse(json.dumps(context))




