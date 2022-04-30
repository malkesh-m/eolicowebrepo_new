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
    chunksize = 4
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
    museumqset = Museum.objects.all().order_by('-edited', 'priority')
    #museumsqset1 = Museum.objects.filter(museumtype=mtypesqset[(int(page) - 1) * rows][0]).order_by('-edited', 'priority')
    #museumsqset2 = Museum.objects.filter(museumtype=mtypesqset[(int(page) - 1) * rows + 1][0]).order_by('-edited', 'priority')
    #museumsqset3 = Museum.objects.filter(museumtype=mtypesqset[(int(page) - 1) * rows + 2][0]).order_by('-edited', 'priority')
    #museumsqset4 = Museum.objects.filter(museumtype=mtypesqset[(int(page) - 1) * rows + 3][0]).order_by('-edited', 'priority')
    #museumsqset5 = Museum.objects.filter(museumtype=mtypesqset[(int(page) - 1) * rows + 4][0]).order_by('-edited', 'priority')
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
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
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
    allmuseumeventsqset = MuseumEvent.objects.filter(museum=museumobj).order_by('-eventstartdate', 'priority')
    chunksize = 4
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
        latestevent = {'eventname' : allmuseumeventsqset[0].eventname, 'eventperiod' : allmuseumeventsqset[0].eventperiod, 'eventtype' : allmuseumeventsqset[0].eventtype, 'presenter' : allmuseumeventsqset[0].presenter, 'eventinfo' : allmuseumeventsqset[0].eventinfo, 'eventurl' : allmuseumeventsqset[0].eventurl, 'coverimage' : allmuseumeventsqset[0].coverimage, 'eventid' : str(allmuseumeventsqset[0].id)}
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
            evt['eventid'] = str(museumevt.id)
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
    piecesqset = MuseumPieces.objects.filter(museum=museumobj).order_by('-edited', 'priority')
    if piecesqset.__len__() > 0:
        topwork = {'piecename' : piecesqset[0].piecename, 'creationdate' : piecesqset[0].creationdate, 'museum' : piecesqset[0].museum.museumname, 'artistname' : piecesqset[0].artistname, 'artistbirthyear' : piecesqset[0].artistbirthyear, 'artistdeathyear' : piecesqset[0].artistdeathyear, 'artistnationality' : piecesqset[0].artistnationality, 'medium' : piecesqset[0].medium, 'size' : piecesqset[0].size, 'edition' : piecesqset[0].edition, 'signature' : piecesqset[0].signature, 'description' : piecesqset[0].description, 'detailurl' : piecesqset[0].detailurl, 'provenance' : piecesqset[0].provenance, 'literature' : piecesqset[0].literature, 'exhibited' : piecesqset[0].exhibited, 'image' : piecesqset[0].image1, 'pid' : str(piecesqset[0].id)}
        artistnationalities[piecesqset[0].artistnationality.lower()] = 1
        nationalities.append(piecesqset[0].artistnationality.lower())
        filterartists.append(piecesqset[0].artistname)
    context['topwork'] = topwork
    allartists = {}
    for piece in piecesqset[1:]:
        ename = piece.event.eventname
        l = allworks[ename]
        d = {'piecename' : piece.piecename, 'creationdate' : piece.creationdate, 'museum' : piece.museum.museumname, 'artistname' : piece.artistname, 'artistbirthyear' : piece.artistbirthyear, 'artistdeathyear' : piece.artistdeathyear, 'artistnationality' : piece.artistnationality, 'medium' : piece.medium, 'size' : piece.size, 'edition' : piece.edition, 'signature' : piece.signature, 'description' : piece.description, 'detailurl' : piece.detailurl, 'provenance' : piece.provenance, 'literature' : piece.literature, 'exhibited' : piece.exhibited, 'image' : piece.image1, 'pid' : str(piece.id)}
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
    articlesqset = MuseumArticles.objects.filter(museum=museumobj).order_by('-edited', 'priority')
    actr = 0
    for article in articlesqset:
        a = {}
        a['articlename'] = article.articlename
        a['writername'] = article.writername
        a['articletype'] = article.articletype
        a['detailurl'] = article.detailurl
        a['published'] = article.published
        a['thumbimage'] = article.thumbimage
        a['articleid'] = article.id
        allarticles.append(a)
        if actr < chunksize:
            overviewarticles.append(a)
        actr += 1
    context['allarticles'] = allarticles
    context['overviewarticles'] = overviewarticles
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('museum_details.html')
    return HttpResponse(template.render(context, request))

    
def follow(request):
    return HttpResponse("")



def eventdetails(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    mevid = None
    if request.method == 'GET':
        if 'mevid' in request.GET.keys():
            mevid = str(request.GET['mevid'])
    if not mevid:
        return HttpResponse("Invalid Request: Request is missing mevid")
    meventobj = None
    try:
        meventobj = MuseumEvent.objects.get(id=mevid)
    except:
        return HttpResponse("Could not identify a museum event with Id %s"%mevid)
    context = {}
    eventdata = {'eventname' : meventobj.eventname, 'eventinfo' : meventobj.eventinfo, 'eventperiod' : meventobj.eventperiod, 'eventtype' : meventobj.eventtype, 'eventimage' : meventobj.coverimage, 'eventlocation' : meventobj.presenter, 'mid' : meventobj.museum.id, 'mevid' : meventobj.id}
    context['eventinfo'] = eventdata
    musobj = meventobj.museum
    otherevents = {} # These will be events from the same museum as the one in eventinfo.
    eventsqset = MuseumEvent.objects.filter(museum=musobj).order_by('priority', '-edited')
    for mev in eventsqset:
        eventname = mev.eventname
        d = {'eventinfo' : mev.eventinfo, 'eventperiod' : mev.eventperiod, 'eventtype' : mev.eventtype, 'eventimage' : mev.coverimage, 'eventlocation' : mev.presenter, 'mid' : mev.museum.id, 'eventid' : mev.id}
        otherevents[eventname] = d
    context['otherevents'] = otherevents
    mpiecesqset = MuseumPieces.objects.filter(event=meventobj)
    eventartistnames = []
    for mp in mpiecesqset:
        eventartistnames.append(mp.artistname)
    artists = []
    artistsqset = Artist.objects.filter(artistname__in=eventartistnames)
    for artist in artistsqset:
        d = {'artistname' : artist.artistname, 'nationality' : artist.nationality, 'birthdate' : artist.birthdate, 'deathdate' : artist.deathdate, 'about' : artist.about, 'artistimage' : artist.squareimage, 'artistid' : artist.id}
        artists.append(d)
    context['artists'] = artists
    # Get all artworks from the selected event
    artworksqset = MuseumPieces.objects.filter(event=meventobj).order_by('priority', '-edited')
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
                d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'mpid' : artwork.id}
                l.append(d)
                allartworks1[eventname] = l
            else:
                l = []
                d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'mpid' : artwork.id}
                l.append(d)
                allartworks1[eventname] = l
        elif actr == 1:
            if eventname in allartworks2.keys():
                l = allartworks2[eventname]
                d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'mpid' : artwork.id}
                l.append(d)
                allartworks2[eventname] = l
            else:
                l = []
                d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'mpid' : artwork.id}
                l.append(d)
                allartworks2[eventname] = l
        elif actr == 2:
            if eventname in allartworks3.keys():
                l = allartworks3[eventname]
                d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'mpid' : artwork.id}
                l.append(d)
                allartworks3[eventname] = l
            else:
                l = []
                d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'mpid' : artwork.id}
                l.append(d)
                allartworks3[eventname] = l
        elif actr == 3:
            if eventname in allartworks4.keys():
                l = allartworks4[eventname]
                d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'mpid' : artwork.id}
                l.append(d)
                allartworks4[eventname] = l
            else:
                l = []
                d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'mpid' : artwork.id}
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
    template = loader.get_template('mevent_details.html')
    return HttpResponse(template.render(context, request))



def artworkdetails(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    mpid = None
    if request.method == 'GET':
        if 'mpid' in request.GET.keys():
            mpid = str(request.GET['mpid'])
    if not mpid:
        return HttpResponse("Invalid Request: Request is missing mpid")
    artworkobj = None
    try:
        artworkobj = MuseumPieces.objects.get(id=mpid)
    except:
        return HttpResponse("Could not identify a museum piece with Id %s"%mpid)
    context = {}
    artworkinfo = {'artworkname' : artworkobj.piecename, 'creationdate' : artworkobj.creationdate, 'artistname' : artworkobj.artistname, 'artistbirthyear' : artworkobj.artistbirthyear, 'artistdeathyear' : artworkobj.artistdeathyear, 'artistnationality' : artworkobj.artistnationality, 'size' : artworkobj.size, 'medium' : artworkobj.medium, 'description' : artworkobj.description, 'provenance' : artworkobj.provenance, 'artworkimage' : artworkobj.image1, 'estimate' : "", 'soldprice' : "", 'mpid' : artworkobj.id}
    context['artworkinfo'] = artworkinfo
    # Get all artworks by the same artist
    allartworks = []
    artworksqset = MuseumPieces.objects.filter(artistname=artworkobj.artistname).order_by('priority', '-edited')
    uniqueartworks = {}
    eventslist = []
    for artwork in artworksqset:
        d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'provenance' : artwork.provenance, 'artworkimage' : artwork.image1, 'estimate' : "", 'soldprice' : "", 'mpid' : artwork.id}
        eventslist.append(artwork.event)
        if artwork.piecename not in uniqueartworks.keys():
            allartworks.append(d)
            uniqueartworks[artwork.piecename] = artwork.id
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
    for mev in eventslist:
        d = {'eventname' : mev.eventname, 'eventinfo' : mev.eventinfo, 'eventtype' : mev.eventtype, 'eventperiod' : mev.eventperiod, 'eventimage' : mev.coverimage, 'eventlocation' : mev.presenter, 'mevid' : mev.id}
        allevents.append(d)
    museumeventartistslist = []
    mpqset = MuseumPieces.objects.filter(event=artworkobj.event)
    for mp in mpqset:
        museumeventartistslist.append(mp.artistname)
    artistsqset = Artist.objects.filter(artistname__in=museumeventartistslist)
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
            d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'provenance' : artwork.provenance, 'artworkimage' : artwork.image1, 'estimate' : "", 'soldprice' : "", 'mpid' : artwork.id}
            if artwork.piecename not in uniqueartworks.keys():
                allartworks1.append(d)
                uniqueartworks[artwork.piecename] = artwork.id
        elif actr == 1:
            d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'provenance' : artwork.provenance, 'artworkimage' : artwork.image1, 'estimate' : "", 'soldprice' : "", 'mpid' : artwork.id}
            if artwork.piecename not in uniqueartworks.keys():
                allartworks2.append(d)
                uniqueartworks[artwork.piecename] = artwork.id
        elif actr == 2:
            d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'provenance' : artwork.provenance, 'artworkimage' : artwork.image1, 'estimate' : "", 'soldprice' : "", 'mpid' : artwork.id}
            if artwork.piecename not in uniqueartworks.keys():
                allartworks3.append(d)
                uniqueartworks[artwork.piecename] = artwork.id
        elif actr == 3:
            d = {'artworkname' : artwork.piecename, 'creationdate' : artwork.creationdate, 'artistname' : artwork.artistname, 'artistbirthyear' : artwork.artistbirthyear, 'artistdeathyear' : artwork.artistdeathyear, 'artistnationality' : artwork.artistnationality, 'size' : artwork.size, 'medium' : artwork.medium, 'description' : artwork.description, 'provenance' : artwork.provenance, 'artworkimage' : artwork.image1, 'estimate' : "", 'soldprice' : "", 'mpid' : artwork.id}
            if artwork.piecename not in uniqueartworks.keys():
                allartworks4.append(d)
                uniqueartworks[artwork.piecename] = artwork.id
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
    template = loader.get_template('mpiece_details.html')
    return HttpResponse(template.render(context, request))

    








