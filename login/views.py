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
from login.models import User, Session, WebConfig, Carousel


def getcarouselinfo():
    entrieslist = []
    countqset = WebConfig.objects.filter(paramname="carousel entries count")
    entriescount = countqset[0].paramvalue
    carouselqset = Carousel.objects.all()
    for e in range(0, int(entriescount)):
        imgpath = carouselqset[e].imagepath
        title = carouselqset[e].title
        text = carouselqset[e].textvalue
        d = {'img' : imgpath, 'title' : title, 'text' : text}
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
        galleriesdict[gname] = [gloc, gimg, gurl]
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
        artistsdict[aname] = [about, aurl, aimg, anat]
    context['artists'] = artistsdict
    events = Event.objects.all().order_by('priority', '-edited')
    eventslist = events[0:4]
    eventsdict = {}
    for e in eventslist:
        ename = e.eventname
        eurl = e.eventurl
        einfo = str(e.eventinfo[0:20]) + "..."
        eperiod = e.eventperiod
        eventsdict[ename] = [eurl, einfo, eperiod ]
    context['events'] = eventsdict
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    template = loader.get_template('homepage.html')
    return HttpResponse(template.render(context, request))


def showlogin(request):
    return HttpResponse("")



