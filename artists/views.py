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



def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 9
    rows = 6
    featuredsize = 5
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    startctr = (chunksize * rows) * (int(page) -1) + featuredsize
    endctr = (chunksize * rows) * int(page) + featuredsize
    context = {}
    featuredartists = []
    artistsqset = Artist.objects.all().order_by('-priority', '-edited')
    for artist in artistsqset:
        d = {'artistname' : artist.artistname, 'nationality' : artist.nationality, 'birthdate' : str(artist.birthdate), 'deathdate' : str(artist.deathdate), 'about' : artist.about, 'profileurl' : artist.profileurl, 'squareimage' : artist.squareimage, 'aid' : str(artist.id)}
        artworkqset = Artwork.objects.filter(artistname__icontains=artist.artistname)
        if artworkqset.__len__() == 0:
            continue
        d['artworkname'] = artworkqset[0].artworkname
        d['artworkimage'] = artworkqset[0].image1
        d['artworkdate'] = artworkqset[0].creationdate
        featuredartists.append(d)
    if featuredartists.__len__() > featuredsize:
        context['featuredartists'] = featuredartists[0:featuredsize]
    else:
        context['featuredartists'] = featuredartists
    allartists = []
    rctr = 0
    while rctr < rows:
        allartists.append([])
        rctr += 1
    rctr = 0
    actr = 0
    if artistsqset.__len__() > featuredsize:
        for artist in artistsqset[startctr:endctr]:
            d = {'artistname' : artist.artistname, 'nationality' : artist.nationality, 'birthdate' : str(artist.birthdate), 'deathdate' : str(artist.deathdate), 'about' : artist.about, 'profileurl' : artist.profileurl, 'squareimage' : artist.squareimage, 'aid' : str(artist.id)}
            artworkqset = Artwork.objects.filter(artistname__icontains=artist.artistname)
            if artworkqset.__len__() == 0:
                continue
            d['artworkname'] = artworkqset[0].artworkname
            d['artworkimage'] = artworkqset[0].image1
            d['artworkdate'] = artworkqset[0].creationdate
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
    context['allartists'] = allartists
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    template = loader.get_template('artist.html')
    return HttpResponse(template.render(context, request))


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
    # Get all artworks by the given artist
    allartworks = []
    artworksqset = Artwork.objects.filter(artistname__icontains=artistname).order_by('-priority', '-edited')
    for artwork in artworksqset:
        d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationdate, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'provenance' : artwork.provenance, 'literature' : artwork.literature, 'exhibitions' : artwork.exhibitions, 'href' : artwork.workurl, 'estimate' : artwork.estimate}
        allartworks.append(d)
    artistinfo = {'name' : artistobj.artistname, 'nationality' : artistobj.nationality, 'birthdate' : artistobj.birthdate, 'deathdate' : artistobj.deathdate, 'profileurl' : artistobj.profileurl, 'desctiption' : artistobj.about, 'image' : artistobj.largeimage, 'gender' : artistobj.gender}
    context['allartworks'] = allartworks
    context['artistinfo'] = artistinfo
    relatedartists = [] # List of artists related to the artist under consideration through an event.
    artistevents = {} # All events featuring the artist under consideration.
    artistgalleries = {} # All galleries where artworks of the artist under consideration are displayed.
    eventobj = artistobj.event
    relatedartistqset = Artist.objects.filter(event=eventobj).order_by('-priority', '-edited')
    for artist in relatedartistqset:
        d = {'artistname' : artist.artistname, 'nationality' : artist.nationality, 'birthdate' : str(artist.birthdate), 'deathdate' : str(artist.deathdate), 'about' : artist.about, 'profileurl' : artist.profileurl, 'squareimage' : artist.squareimage, 'aid' : str(artist.id)}
        artworkqset = Artwork.objects.filter(artistname__icontains=artist.artistname).order_by('-priority', '-edited')
        if artworkqset.__len__() == 0:
            continue
        d['artworkname'] = artworkqset[0].artworkname
        d['artworkimage'] = artworkqset[0].image1
        d['artworkdate'] = artworkqset[0].creationdate
        if relatedartists.__len__() < chunksize:
            relatedartists.append(d)
    artworksqset = Artwork.objects.filter(artistname__icontains=artistobj.artistname).order_by('-priority', '-edited')
    for artwork in artworksqset:
        eventname = artwork.event.eventname
        eventurl = artwork.event.eventurl
        eventinfo = artwork.event.eventinfo
        eventperiod = artwork.event.eventperiod
        eventimage = artwork.event.eventimage
        eventlocation = artwork.event.eventlocation
        l = artistevents.keys()
        if l.__len__() < chunksize and eventname not in l:
            artistevents[eventname] = {'eventurl' : eventurl, 'eventinfo' : eventinfo, 'eventperiod' : eventperiod, 'eventimage' : eventimage, 'eventlocation' : eventlocation}
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
    template = loader.get_template('artist_details.html')
    return HttpResponse(template.render(context, request))


def follow(request):
    return HttpResponse("")


