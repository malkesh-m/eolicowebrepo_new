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
from museum.models import Museum, MuseumEvent, MuseumPieces

def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 5
    rows = 10
    startctr = int(page) * rows - rows + 1
    endctr = int(page) * rows + 1
    latestmuseum = {}
    museumsqset = Museum.objects.all().order_by('-edited', '-priority')
    mtypesqset = Museum.objects.order_by().values_list('museumtype').distinct()
    if endctr > mtypesqset.__len__():
        endctr = mtypesqset.__len__()
    museumtypes = []
    allmuseums = {}
    context = {}
    for mtype in mtypesqset[startctr:endctr]:
        museumtypes.append(mtype[0])
        allmuseums[mtype[0]] = []
    for m in museumsqset[1:]:
        l = allmuseums[m.museumtype]
        if l.__len__() < chunksize:
            d = {'museumname' : m.museumname, 'location' : m.location, 'description' : m.description, 'museumurl' : m.museumurl, 'coverimage' : m.coverimage, 'mid' : m.id}
            l.append(d)
            allmuseums[m.museumtype] = l
        else:
            continue
    context['allmuseums'] = allmuseums
    latestmuseum = {'museumname' : museumsqset[0].museumname, 'location' : museumsqset[0].location, 'description' : museumsqset[0].description, 'museumurl' : museumsqset[0].museumurl, 'coverimage' : museumsqset[0].coverimage, 'mid' : museumsqset[0].id}
    context['latestmuseum'] = latestmuseum
    template = loader.get_template('museum.html')
    return HttpResponse(template.render(context, request))



def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    mid = None
    if request.method == 'GET':
        if 'q' in request.GET.keys():
            mid = str(request.GET['q'])
    if not mid:
        return HttpResponse("Invalid Request: Request is missing mid")
    museumobj = None
    try:
        museumobj = Museum.objects.get(id=mid)
    except:
        return HttpResponse("Could not identify a museum with Id %s"%mid)
    # Find all museum events for the selected museum. Order by 'edited' and 'priority'.
    allmuseumeventsqset = MuseumEvent.objects.filter(museum=museumobj).order_by('-eventstartdate', '-priority')
    chunksize = 6
    latestevent = {}
    allevents = []
    overviewevents = []
    overviewworks = []
    allworks = {}
    topwork = {}
    eventsprioritylist = []
    context = {}
    if allmuseumeventsqset.__len__() > 0:
        latestevent = {'eventname' : allmuseumeventsqset[0].eventname, 'eventperiod' : allmuseumeventsqset[0].eventperiod, 'eventtype' : allmuseumeventsqset[0].eventtype, 'presenter' : allmuseumeventsqset[0].presenter, 'eventinfo' : allmuseumeventsqset[0].eventinfo, 'eventurl' : allmuseumeventsqset[0].eventurl}
        eventsprioritylist.append(allmuseumeventsqset[0].eventname)
    context['latestevent'] = latestevent
    if allmuseumeventsqset.__len__() > 1:
        for museumevt in allmuseumeventsqset[1:]:
            evt = {}
            evt['eventname'] = museumevt.eventname
            evt['eventperiod'] = museumevt.eventperiod
            evt['eventtype'] = museumevt.eventtype
            evt['presenter'] = museumevt.presenter
            evt['eventinfo'] = museumevt.eventinfo
            evt['eventurl'] = museumevt.eventurl
            allevents.append(evt)
            eventsprioritylist.append(museumevt.eventname)
            if overviewevents.__len__() < chunksize:
                overviewevents.append(evt)
    context['allevents'] = allevents
    context['overviewevents'] = overviewevents
    for evname in eventsprioritylist:
        allworks[evname] = []
    piecesqset = MuseumPieces.objects.filter(museum=museumobj).order_by('-edited', '-priority')
    if piecesqset.__len__() > 0:
        topwork = {'piecename' : piecesqset[0].piecename, 'creationdate' : piecesqset[0].creationdate, 'museum' : piecesqset[0].museum.museumname, 'artistname' : piecesqset[0].artistname, 'artistbirthyear' : piecesqset[0].artistbirthyear, 'artistdeathyear' : piecesqset[0].artistdeathyear, 'artistnationality' : piecesqset[0].artistnationality, 'medium' : piecesqset[0].medium, 'size' : piecesqset[0].size, 'edition' : piecesqset[0].edition, 'signature' : piecesqset[0].signature, 'description' : piecesqset[0].description, 'detailurl' : piecesqset[0].detailurl, 'provenance' : piecesqset[0].provenance, 'literature' : piecesqset[0].literature, 'exhibited' : piecesqset[0].exhibited, 'image' : piecesqset[0].image1}
    context['topwork'] = topwork
    for piece in piecesqset[1:]:
        ename = piece.event.eventname
        l = allworks[ename]
        d = {'piecename' : piece.piecename, 'creationdate' : piece.creationdate, 'museum' : piece.museum.museumname, 'artistname' : piece.artistname, 'artistbirthyear' : piece.artistbirthyear, 'artistdeathyear' : piece.artistdeathyear, 'artistnationality' : piece.artistnationality, 'medium' : piece.medium, 'size' : piece.size, 'edition' : piece.edition, 'signature' : piece.signature, 'description' : piece.description, 'detailurl' : piece.detailurl, 'provenance' : piece.provenance, 'literature' : piece.literature, 'exhibited' : piece.exhibited, 'image' : piece.image1}
        l.append(d)
        allworks[ename] = l
        if overviewworks.__len__() < chunksize:
            overviewworks.append(d)
    context['allworks'] = allworks
    context['overviewworks'] = overviewworks
    template = loader.get_template('museum_details.html')
    return HttpResponse(template.render(context, request))

    








