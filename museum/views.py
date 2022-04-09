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
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    mtypesqset = Museum.objects.order_by().values_list('museumtype').distinct()
    startctr = (int(page) * rows * chunksize) - (rows * chunksize) + 1
    endctr = int(page) * rows * chunksize
    """
    startctr1 = int(page) * chunksize - chunksize
    startctr2 = int(page) * chunksize - chunksize
    startctr3 = int(page) * chunksize - chunksize
    startctr4 = int(page) * chunksize - chunksize
    startctr5 = int(page) * chunksize - chunksize
    endctr1 = int(page) * chunksize
    endctr2 = int(page) * chunksize
    endctr3 = int(page) * chunksize
    endctr4 = int(page) * chunksize
    endctr5 = int(page) * chunksize
    """
    latestmuseum = {}
    locationsqset = Museum.objects.order_by().values_list('location').distinct()
    mtypesqset = Museum.objects.order_by().values_list('museumtype').distinct()
    museumqset = Museum.objects.all().order_by('-edited', '-priority')
    #museumsqset1 = Museum.objects.filter(museumtype=mtypesqset[(int(page) - 1) * rows][0]).order_by('-edited', '-priority')
    #museumsqset2 = Museum.objects.filter(museumtype=mtypesqset[(int(page) - 1) * rows + 1][0]).order_by('-edited', '-priority')
    #museumsqset3 = Museum.objects.filter(museumtype=mtypesqset[(int(page) - 1) * rows + 2][0]).order_by('-edited', '-priority')
    #museumsqset4 = Museum.objects.filter(museumtype=mtypesqset[(int(page) - 1) * rows + 3][0]).order_by('-edited', '-priority')
    #museumsqset5 = Museum.objects.filter(museumtype=mtypesqset[(int(page) - 1) * rows + 4][0]).order_by('-edited', '-priority')
    if rowendctr > mtypesqset.__len__():
        rowendctr = mtypesqset.__len__()
    museumtypes = []
    allmuseums = {}
    locationslist = []
    galleries = []
    context = {}
    allmtypes = []
    museumsfull = {}
    for mtype in mtypesqset[rowstartctr:rowendctr]:
        museumtypes.append(mtype[0])
        allmuseums[mtype[0]] = []
    for mtype in mtypesqset:
        allmtypes.append(mtype[0])
        museumsfull[mtype[0]] = []
    for loc in locationsqset:
        locparts = loc[0].split(",")
        for iloc in locparts:
            iloc = iloc.strip()
            locationslist.append(iloc)
    """
    if endctr1 > museumsqset1.__len__():
        endctr1 = museumsqset1.__len__()
    if endctr2 > museumsqset2.__len__():
        endctr2 = museumsqset2.__len__()
    if endctr3 > museumsqset3.__len__():
        endctr3 = museumsqset3.__len__()
    if endctr4 > museumsqset4.__len__():
        endctr4 = museumsqset4.__len__()
    if endctr5 > museumsqset5.__len__():
        endctr5 = museumsqset5.__len__()
    museumslist1 = museumsqset1[startctr1:endctr1]
    museumslist2 = museumsqset2[startctr2:endctr2]
    museumslist3 = museumsqset3[startctr3:endctr3]
    museumslist4 = museumsqset4[startctr4:endctr4]
    museumslist5 = museumsqset5[startctr5:endctr5]
    """
    for m in museumqset[startctr:endctr]:
        if m.museumtype in allmuseums.keys():
            l = allmuseums[m.museumtype]
        else:
            l = []
            allmuseums[m.museumtype] = l
        if l.__len__() < chunksize:
            m.description = m.description.replace("\n", "").replace("\r", "")
            d = {'museumname' : m.museumname, 'location' : m.location, 'description' : m.description, 'museumurl' : m.museumurl, 'coverimage' : m.coverimage, 'mid' : m.id}
            l.append(d)
            allmuseums[m.museumtype] = l
        else:
            continue
    emptytypes = []
    for mt in allmuseums.keys():
        if allmuseums[mt].__len__() == 0:
            emptytypes.append(mt)
    for mt in emptytypes:
        del allmuseums[mt]
    context['allmuseums'] = allmuseums
    for m in museumqset:
        if m.museumtype in museumsfull.keys():
            l = museumsfull[m.museumtype]
        else:
            l = []
            museumsfull[m.museumtype] = l
        if l.__len__() < chunksize:
            m.description = m.description.replace("\n", "").replace("\r", "")
            d = {'museumname' : m.museumname, 'location' : m.location, 'description' : m.description, 'museumurl' : m.museumurl, 'coverimage' : m.coverimage, 'mid' : m.id}
            l.append(d)
            museumsfull[m.museumtype] = l
        else:
            continue
    if museumqset.__len__() > 0:
        museumqset[0].description = museumqset[0].description.replace("\n", "").replace("\r", "")
        latestmuseum = {'museumname' : museumqset[0].museumname, 'location' : museumqset[0].location, 'description' : museumqset[0].description, 'museumurl' : museumqset[0].museumurl, 'coverimage' : museumqset[0].coverimage, 'mid' : museumqset[0].id}
    context['latestmuseum'] = latestmuseum
    emptytypes = []
    for mt in museumsfull.keys():
        if museumsfull[mt].__len__() == 0:
            emptytypes.append(mt)
    for mt in emptytypes:
        del museumsfull[mt]
    context['museumsfull'] = museumsfull
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    context['locations'] = locationslist
    context['specialities'] = museumtypes
    template = loader.get_template('museum.html')
    return HttpResponse(template.render(context, request))



def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    mid = None
    if request.method == 'GET':
        if 'mid' in request.GET.keys():
            mid = str(request.GET['mid'])
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
    artistnationalities = {}
    nationalities = []
    filterartists = []
    context = {}
    if allmuseumeventsqset.__len__() > 0:
        latestevent = {'eventname' : allmuseumeventsqset[0].eventname, 'eventperiod' : allmuseumeventsqset[0].eventperiod, 'eventtype' : allmuseumeventsqset[0].eventtype, 'presenter' : allmuseumeventsqset[0].presenter, 'eventinfo' : allmuseumeventsqset[0].eventinfo, 'eventurl' : allmuseumeventsqset[0].eventurl, 'coverimage' : allmuseumeventsqset[0].coverimage}
        eventsprioritylist.append(allmuseumeventsqset[0].eventname)
    context['latestevent'] = latestevent
    if allmuseumeventsqset.__len__() > 1:
        for museumevt in allmuseumeventsqset[1:]:
            evt = {}
            evt['eventname'] = museumevt.eventname
            evt['eventperiod'] = museumevt.eventperiod
            evt['eventtype'] = museumevt.eventtype
            evt['coverimage'] = museumevt.coverimage
            evt['presenter'] = museumevt.presenter
            evt['eventinfo'] = museumevt.eventinfo
            evt['eventurl'] = museumevt.eventurl
            allevents.append(evt)
            mpqset = MuseumPieces.objects.filter(event=museumevt)
            if mpqset.__len__() > 0:
                eventsprioritylist.append(museumevt.eventname)
            if overviewevents.__len__() < chunksize:
                overviewevents.append(evt)
    context['allevents'] = allevents
    context['overviewevents'] = overviewevents
    if eventsprioritylist.__len__() < 4:
        for i in range(eventsprioritylist.__len__(), 4):
            eventsprioritylist.append("")
    context['eventsprioritylist'] = eventsprioritylist
    #print(eventsprioritylist)
    for evname in eventsprioritylist:
        allworks[evname] = []
    piecesqset = MuseumPieces.objects.filter(museum=museumobj).order_by('-edited', '-priority')
    if piecesqset.__len__() > 0:
        topwork = {'piecename' : piecesqset[0].piecename, 'creationdate' : piecesqset[0].creationdate, 'museum' : piecesqset[0].museum.museumname, 'artistname' : piecesqset[0].artistname, 'artistbirthyear' : piecesqset[0].artistbirthyear, 'artistdeathyear' : piecesqset[0].artistdeathyear, 'artistnationality' : piecesqset[0].artistnationality, 'medium' : piecesqset[0].medium, 'size' : piecesqset[0].size, 'edition' : piecesqset[0].edition, 'signature' : piecesqset[0].signature, 'description' : piecesqset[0].description, 'detailurl' : piecesqset[0].detailurl, 'provenance' : piecesqset[0].provenance, 'literature' : piecesqset[0].literature, 'exhibited' : piecesqset[0].exhibited, 'image' : piecesqset[0].image1}
        artistnationalities[piecesqset[0].artistnationality.lower()] = 1
        nationalities.append(piecesqset[0].artistnationality.lower())
        filterartists.append(piecesqset[0].artistname)
    context['topwork'] = topwork
    allartists = {}
    for piece in piecesqset[1:]:
        ename = piece.event.eventname
        l = allworks[ename]
        d = {'piecename' : piece.piecename, 'creationdate' : piece.creationdate, 'museum' : piece.museum.museumname, 'artistname' : piece.artistname, 'artistbirthyear' : piece.artistbirthyear, 'artistdeathyear' : piece.artistdeathyear, 'artistnationality' : piece.artistnationality, 'medium' : piece.medium, 'size' : piece.size, 'edition' : piece.edition, 'signature' : piece.signature, 'description' : piece.description, 'detailurl' : piece.detailurl, 'provenance' : piece.provenance, 'literature' : piece.literature, 'exhibited' : piece.exhibited, 'image' : piece.image1}
        l.append(d)
        allworks[ename] = l
        if overviewworks.__len__() < chunksize:
            overviewworks.append(d)
        if piece.artistname not in allartists.keys():
            allartists[piece.artistname] = 1
        if piece.artistnationality.lower() not in artistnationalities.keys():
            artistnationalities[piece.artistnationality.lower()] = 1
            nationalities.append(piece.artistnationality.lower())
        if piece.artistname not in filterartists:
            filterartists.append(piece.artistname)
    #print(allworks)
    context['allworks'] = allworks
    context['overviewworks'] = overviewworks
    context['allartists'] = allartists
    context['artistnationalities'] = artistnationalities
    context['nationalities'] = nationalities
    context['filterartists'] = filterartists
    allarticles = []
    overviewarticles = []
    articlesqset = MuseumArticles.objects.filter(museum=museumobj).order_by('-edited', '-priority')
    actr = 0
    for article in articlesqset:
        a = {}
        a['articlename'] = article.articlename
        a['writername'] = article.writername
        a['articletype'] = article.articletype
        a['detailurl'] = article.detailurl
        a['published'] = article.published
        a['thumbimage'] = article.thumbimage
        allarticles.append(a)
        if actr < chunksize:
            overviewarticles.append(a)
        actr += 1
    context['allarticles'] = allarticles
    context['overviewarticles'] = overviewarticles
    template = loader.get_template('museum_details.html')
    return HttpResponse(template.render(context, request))

    
def follow(request):
    return HttpResponse("")





