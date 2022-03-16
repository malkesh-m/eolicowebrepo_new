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



# @login_required(login_url='/login/show/')
def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 5
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
        galleriesdict[gname] = [gloc, gimg, gurl, gid, gtypesqset[0][0]]
    context = {'galleries1' : galleriesdict}
    galleriesdict = {}
    for g in gallerieslist2[startctr2:lastctr2]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        gid = g.id
        galleriesdict[gname] = [gloc, gimg, gurl, gid, gtypesqset[1][0]]
    context['galleries2'] = galleriesdict
    galleriesdict = {}
    for g in gallerieslist3[startctr3:lastctr3]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        gid = g.id
        galleriesdict[gname] = [gloc, gimg, gurl, gid, gtypesqset[2][0]]
    context['galleries3'] = galleriesdict
    galleriesdict = {}
    for g in gallerieslist4[startctr4:lastctr4]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        gid = g.id
        galleriesdict[gname] = [gloc, gimg, gurl, gid, gtypesqset[3][0]]
    context['galleries4'] = galleriesdict
    galleriesdict = {}
    for g in gallerieslist5[startctr5:lastctr5]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        gid = g.id
        galleriesdict[gname] = [gloc, gimg, gurl, gid, gtypesqset[4][0]]
    context['galleries5'] = galleriesdict
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    context['gallerytypes'] = [gtypesqset[0][0], gtypesqset[1][0], gtypesqset[2][0], gtypesqset[3][0], gtypesqset[4][0]]
    template = loader.get_template('gallery.html')
    return HttpResponse(template.render(context, request))


def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    gid = None
    if request.method == 'GET':
        if 'q' in request.GET.keys():
            gid = str(request.GET['q'])
    if not gid:
        return HttpResponse("Invalid Request: Request is missing gid")
    try:
        galleryobj = Gallery.objects.get(id=gid)
    except:
        return HttpResponse("Could not identify a gallery with Id %s"%gid)
    # Get latest events for this gallery. Also order by 'priority'.
    context = {}
    eventsqset = Event.objects.filter(gallery=galleryobj).order_by('-eventstartdate', 'priority')
    latestevent = {}
    if eventsqset.__len__() > 0:
        latestevent['eventname'] = eventsqset[0].eventname
        latestevent['eventurl'] = eventsqset[0].eventurl
        latestevent['eventinfo'] = eventsqset[0].eventinfo
        latestevent['eventtype'] = eventsqset[0].eventtype
        latestevent['eventstatus'] = eventsqset[0].eventstatus
        latestevent['eventperiod'] = eventsqset[0].eventperiod
        latestevent['eventimage'] = eventsqset[0].eventimage
        latestevent['eventlocation'] = eventsqset[0].eventlocation
    context['latestevent'] = latestevent
    previousevents = []
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
            previousevents.append(pevent)
    context['previousevents'] = previousevents
    # Showing 20 artists from the latest featured event only.
    artistsqset = Artist.objects.filter(event=eventsqset[0]).order_by('-edited', 'priority')
    artistslist = []
    max_len = 20
    if artistsqset.__len__() < max_len:
        max_len = artistsqset.__len__()
    for artist in artistsqset[:max_len]:
        adict = {'artistname' : artist.artistname, 'artisturl' : artist.profileurl}
        artistslist.append(adict)
    context['artists'] = artistslist
    allartists = []
    # Find all artists belonging to this gallery
    for evobj in eventsqset:
        artistsqset = Artist.objects.filter(event=evobj).order_by('-edited', 'priority')
        for artist in artistsqset:
            adict = {'artistname' : artist.artistname, 'artisturl' : artist.profileurl}
            allartists.append(adict)
    context['allartists'] = artistslist
    template = loader.get_template('gallery_details.html')
    return HttpResponse(template.render(context, request))




    



