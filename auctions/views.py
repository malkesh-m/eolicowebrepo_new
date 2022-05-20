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
import urllib

from gallery.models import Gallery, Event
from login.models import User, Session, WebConfig, Carousel
from login.views import getcarouselinfo
from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from auctions.models import Auction, Lot
from artists.models import Artist, Artwork
from auctionhouses.models import AuctionHouse

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
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 4
    rows = 6
    featuredsize = 4
    maxpastauctions = 10
    maxupcomingauctions = 4
    maxpastauctionsperrow = 4
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    pastrowstartctr = int(page) * maxpastauctionsperrow * maxpastauctions - maxpastauctionsperrow * maxpastauctions
    pastrowendctr = int(page) * maxpastauctionsperrow * maxpastauctions
    startctr = (chunksize * rows) * (int(page) -1) + featuredsize
    endctr = (chunksize * rows) * int(page) + featuredsize
    context = {}
    allauctions = {}
    featuredauctions = {}
    filterauctions = []
    try:
        featuredauctions = pickle.loads(redis_instance.get('ac_featuredauctions'))
        filterauctions = pickle.loads(redis_instance.get('ac_filterauctions'))
        allauctions = pickle.loads(redis_instance.get('ac_allauctions'))
    except:
        featuredauctions = {}
        filterauctions = []
        allauctions = {}
    curdatetime = datetime.datetime.now()
    if allauctions.__len__() == 0:
        auctionsqset = Auction.objects.all().order_by('-auctionstartdate', 'priority')
        try:
            aucctr = 0
            for auction in auctionsqset[rowstartctr:]:
                if featuredauctions.keys().__len__() > maxupcomingauctions:
                    break
                auctionname = auction.auctionname
                filterauctions.append(auctionname)
                if auction.auctionstartdate <= curdatetime: # this is a past auction, so skip.
                    continue
                if aucctr > rowendctr:
                    break
                aucctr += 1
                auctionurl = auction.auctionurl
                auctionlots = Lot.objects.filter(auction_id=auction.id)
                #if auctionlots.__len__() == 0:
                #    continue
                auctionperiod = auction.auctionstartdate.strftime("%d %b, %Y")
                if auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                    auctionperiod += " - " + auction.auctionenddate.strftime("%d %b, %Y")
                auctionhouse = None
                auctionhousename, ahid, location = "", auction.auctionhouse_id, ""
                try:
                    auctionhouse = AuctionHouse.objects.get(id=auction.auctionhouse_id)
                    auctionhousename = auctionhouse.housename
                    location = auctionhouse.location
                except:
                    pass
                d = {'auctionname' : auctionname, 'image' : auction.coverimage, 'auctionhouse' : auctionhousename, 'auctionurl' : "", 'auctionperiod' : auctionperiod, 'aucid' : auction.id, 'ahid' : ahid, 'location' : location}
                featuredauctions[auctionname] = d
                if featuredauctions.keys().__len__() > chunksize:
                    break
        except:
            pass
        #print(featuredauctions)
        context['featuredauctions'] = featuredauctions
        try:
            redis_instance.set('ac_featuredauctions', pickle.dumps(featuredauctions))
        except:
            pass
        #print(" ########################### " + str(pastrowstartctr) + " ##########################")
        aucctr = 0
        rctr = 0
        allauctions['row0'] = []
        for auction in auctionsqset[pastrowstartctr:]:
            if auction.auctionstartdate > curdatetime:
                continue
            auctionname = auction.auctionname
            filterauctions.append(auctionname)
            auction_id = auction.id
            auctionlots = Lot.objects.filter(auction_id=auction.id)
            #if auctionlots.__len__() == 0:
            #    continue
            if auctionname not in allauctions.keys():
                allauctions[auctionname] = []
            auctionperiod = auction.auctionstartdate.strftime("%d %b, %Y")
            if auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                auctionperiod += " - " + auction.auctionenddate.strftime("%d %b, %Y")
            auctionhouse = None
            auctionhousename, ahid, location = "", auction.auctionhouse_id, ""
            try:
                auctionhouse = AuctionHouse.objects.get(id=auction.auctionhouse_id)
                auctionhousename = auctionhouse.housename
                location = auctionhouse.location
            except:
                pass
            d = {'auctionname' : auctionname, 'image' : auction.coverimage, 'auctionhouse' : auctionhousename, 'auctionurl' : "", 'auctionperiod' : auctionperiod, 'aucid' : auction.id, 'ahid' : ahid, 'location' : location}
            if allauctions.keys().__len__() > maxpastauctionsperrow * maxpastauctions:
                break
            if aucctr % 4 == 0:
                rctr += 1
                allauctions['row' + str(rctr)] = []
            allauctions['row' + str(rctr)].append(d)
            aucctr += 1
        context['allauctions'] = allauctions
        context['filterauctions'] = filterauctions
        #print(allauctions)
        try:
            redis_instance.set('ac_allauctions', pickle.dumps(allauctions))
            redis_instance.set('ac_filterauctions', pickle.dumps(filterauctions))
        except:
            pass
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    prevpage = int(page) - 1
    nextpage = int(page) + 1
    displayedprevpage1 = 0
    displayedprevpage2 = 0
    if prevpage > 0:
        displayedprevpage1 = prevpage - 1
        displayedprevpage2 = prevpage - 2
    displayednextpage1 = nextpage + 1
    displayednextpage2 = nextpage + 2
    firstpage = 1
    context['pages'] = {'prevpage' : prevpage, 'nextpage' : nextpage, 'firstpage' : firstpage, 'displayedprevpage1' : displayedprevpage1, 'displayedprevpage2' : displayedprevpage2, 'displayednextpage1' : displayednextpage1, 'displayednextpage2' : displayednextpage2, 'currentpage' : int(page)}
    template = loader.get_template('auction.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    lid = None
    if request.method == 'GET':
        if 'lid' in request.GET.keys():
            lid = str(request.GET['lid'])
    if not lid:
        return HttpResponse("Invalid Request: Request is missing lot Id")
    lotobj = None
    try:
        lotobj = Lot.objects.get(id=lid)
    except:
        return HttpResponse("Could not find the lot identified by the lot Id (%s)"%lid)
    chunksize = 4
    rows = 2
    context = {}
    artworkobj = None
    try:
        artworkobj = Artwork.objects.get(id=lotobj.artwork_id)
    except:
        pass
    artworkname, artworkdesc, artistname, artistbirth, artistdeath, nationality, createdate, artistid = "", "", "", "", "", "", "", ""
    auctionname, estimate, literature, exhibition = "", "", "", ""
    if artworkobj is not None:
        artworkname = artworkobj.artworkname
        artworkdesc = artworkobj.description
        literature = artworkobj.literature
        exhibition = artworkobj.exhibitions
        createdate = artworkobj.creationstartdate
        try:
            artistobj = Artist.objects.get(id=artworkobj.artist_id)
            artistname = artistobj.artistname
            artistbirth = artistobj.birthyear
            artistdeath = artistobj.deathyear
            nationality = artistobj.nationality
            artistid = artistobj.id
        except:
            pass
    auctionobj = None
    try:
        auctionobj = Auction.objects.get(id=lotobj.auction_id)
        auctionname = auctionobj.auctionname
    except:
        pass
    estimate = str(lotobj.lowestimateUSD)
    if lotobj.highestimateUSD > 0.00:
        estimate += " - " + str(lotobj.highestimateUSD)
    artworkdesc = artworkdesc.replace("<strong><br>Description:</strong><br>", "")
    artworkdesc = artworkdesc.replace("<strong>Description:</strong>", "")
    artworkdesc = artworkdesc.replace("<br>", "")
    artworkdesc = artworkdesc.replace("<strong>", "").replace("</strong>", "")
    lotinfo = {'title' : artworkname, 'description' : artworkdesc, 'artist' : artistname, 'birth' : artistbirth, 'death' : artistdeath, 'nationality' : nationality, 'medium' : lotobj.medium, 'size' : lotobj.sizedetails, 'auctionname' : auctionname, 'estimate' : estimate, 'soldprice' : str(lotobj.soldpriceUSD), 'currency' : "USD", 'provenance' : lotobj.provenance, 'literature' : literature, 'exhibitions' : exhibition, 'image1' : lotobj.lotimage1, 'image2' : lotobj.lotimage2, 'image3' : lotobj.lotimage3, 'image4' : lotobj.lotimage4, 'url' : lotobj.source, 'category' : lotobj.category, 'created' : createdate, 'lotid' : lotobj.id, 'aid' : artistid}
    context['lotinfo'] = lotinfo
    try:
        aboutartist = pickle.loads(redis_instance.get('ac_aboutartist_%s'%lotobj.auction.id))
    except:
        aboutartist = {}
    if aboutartist.keys().__len__() == 0:
        if artistobj is None:
            if artworkobj is not None:
                artistobj = Artist.objects.get(id=artworkobj.artist_id)
            else:
                artistqset = Artist.objects.filter(artistname__iexact=lotobj.artistname)
                artistobj = artistqset[0]
        aboutartist = {'artistname' : '', 'nationality' : '', 'birth' : '', 'death' : '', 'about' : '', 'image' : '', 'aid' : ''}
        if artistobj is not None:
            aboutartist = {'artistname' : artistobj.artistname, 'nationality' : artistobj.nationality, 'birth' : artistobj.birthyear, 'death' : artistobj.deathyear, 'about' : artistobj.description, 'image' : artistobj.artistimage, 'aid' : artistobj.id}
        context['aboutartist'] = aboutartist
        try:
            redis_instance.set('ac_aboutartist_%s'%lotobj.auction.id, pickle.dumps(aboutartist))
        except:
            pass
    otherworks = [[], [], [], []]
    relatedworks = [[], [], [], []]
    allartists = {}
    try:
        otherworks = pickle.loads(redis_instance.get('ac_otherworks_%s'%lotobj.auction.id))
        relatedworks = pickle.loads(redis_instance.get('ac_relatedworks_%s'%lotobj.auction.id))
        allartists = pickle.loads(redis_instance.get('ac_allartists_%s'%lotobj.auction.id))
    except:
        otherworks = [[], [], [], []]
        relatedworks = [[], [], [], []]
        allartists = {}
    if otherworks[0].__len__() == 0:
        lotsqset = Lot.objects.filter(auction_id=lotobj.auction_id).order_by() # Ordered by priority, by default
        numlots = chunksize * rows
        if lotsqset.__len__() < numlots:
            numlots = lotsqset.__len__()
        actr = 0
        rctr = 0
        for lot in lotsqset[0:numlots]:
            artwork = None
            try:
                artwork = Artwork.objects.get(id=lot.artwork_id)
            except:
                continue
            artistname = ""
            try:
                artist = Artist.objects.get(id=artwork.artist_id)
                artistname = artist.artistname
            except:
                pass
            estimate = str(lot.lowestimateUSD)
            if lot.highestimateUSD > 0.00:
                estimate += " - " + str(lot.highestimateUSD)
            d = {'title' : artwork.artworkname, 'artist' : artistname, 'image' : lot.lotimage1, 'medium' : lot.medium, 'estimate' : estimate, 'lid' : lot.id, 'aid' : artwork.artist_id}
            l = otherworks[rctr]
            l.append(d)
            otherworks[rctr] = l
            rctr += 1
            if rctr == 4:
                rctr = 0
            if artistname in allartists.keys():
                l = allartists[artistname]
                l.append({'title' : artwork.artworkname, 'image' : lot.lotimage1, 'medium' : lot.medium, 'estimate' : estimate, 'lid' : lot.id, 'aid' : artist.id})
                allartists[artistname] = l
            else:
                l = []
                l.append({'title' : artwork.artworkname, 'image' : lot.lotimage1, 'medium' : lot.medium, 'estimate' : estimate, 'lid' : lot.id, 'aid' : artist.id})
                allartists[artistname] = l
        context['otherworks'] = otherworks
        try:
            redis_instance.set('ac_otherworks_%s'%lotobj.auction.id, pickle.dumps(otherworks))
        except:
            pass
    if relatedworks[0].__len__() == 0:
        relatedqset = Artwork.objects.filter(artist_id=artistobj.id).order_by() # Getting artworks by the same artist, in any auction.
        numlots = chunksize * rows
        if relatedqset.__len__() < numlots:
            numlots = relatedqset.__len__()
        rctr = 0
        for aw in relatedqset[0:numlots]:
            rel_lotobj = None
            rel_estimate = ""
            rel_lotqset = Lot.objects.filter(artwork_id=aw.id)
            if rel_lotqset.__len__() > 0:
                rel_lotobj = rel_lotqset[0]
                rel_estimate = str(rel_lotobj.lowestimateUSD)
                if rel_lotobj.highestimateUSD > 0.00:
                    rel_estimate += " - " + str(rel_lotobj.highestimateUSD)
            else:
                continue
            rel_artistname = ""
            rel_artist = None
            try:
                rel_artist = Artist.objects.get(id=aw.artist_id)
                rel_artistname = rel_artist.artistname
            except:
                pass
            d = {'title' : aw.artworkname, 'artist' : rel_artistname, 'image' : rel_lotobj.lotimage1, 'medium' : rel_lotobj.medium, 'estimate' : rel_estimate, 'lid' : rel_lotobj.id, 'aid' : aw.artist_id}
            l = relatedworks[rctr]
            l.append(d)
            relatedworks[rctr] = l
            rctr += 1
            if rctr == 4:
                rctr = 0
            if rel_artistname != "" and rel_artistname in allartists.keys(): # This is the part that would be executed, not the else clause
                l2 = allartists[rel_artistname]
                l2.append({'title' : aw.artworkname, 'nationality' : rel_artist.nationality, 'birth' : rel_artist.birthyear, 'death' : rel_artist.deathyear, 'image' : rel_lotobj.lotimage1, 'medium' : rel_lotobj.medium, 'estimate' : rel_estimate, 'lid' : rel_lotobj.id, 'aid' : rel_artist.id})
                allartists[rel_artistname] = l2
            else: # This should never be executed. Bad omen... bad things will happen if this is executed.
                l2 = []
                try:
                    rel_artist = Artist.objects.get(artistname__iexact=rel_artistname)
                except:
                    continue # If there is no corresponding artist object, we cannot continue
                l2.append({'title' : aw.artworkname, 'nationality' : rel_artist.nationality, 'birth' : rel_artist.birthyear, 'death' : rel_artist.deathyear, 'image' : rel_lotobj.lotimage1, 'medium' : rel_lotobj.medium, 'estimate' : rel_estimate, 'lid' : rel_lotobj.id, 'aid' : rel_artist.id})
                allartists[rel_artistname] = l2
        context['relatedworks'] = relatedworks
        context['allartists'] = allartists
        try:
            redis_instance.set('ac_relatedworks_%s'%lotobj.auction.id, pickle.dumps(relatedworks))
            redis_instance.set('ac_allartists_%s'%lotobj.auction.id, pickle.dumps(allartists))
        except:
            pass
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('auction_details.html')
    return HttpResponse(template.render(context, request))
    

#@cache_page(CACHE_TTL)
def follow(request):
    return HttpResponse("")


def search(request):
    """
    This should return a json response containing a list of dicts.
    The dict keys would be the attributes of an auction object.
    """
    if request.method != 'GET':
        return HttpResponse(json.dumps({'err' : "Invalid method of call"}))
    searchkey = None
    if request.method == 'GET':
        if 'q' in request.GET.keys():
            searchkey = str(request.GET['q']).strip()
    if not searchkey or searchkey == "":
        return HttpResponse(json.dumps({'err' : "Invalid Request: Request is missing search key"}))
    #print(searchkey)
    context = {}
    auctionsqset = Auction.objects.filter(auctionname__icontains=searchkey).order_by('priority')
    allauctions = []
    maxsearchresults = 30
    aucctr = 0
    for auctionobj in auctionsqset:
        auctionhouseid = auctionobj.auctionhouse_id
        ahobj = None
        auctionhousename, ahid = "", ""
        try:
            ahobj = AuctionHouse.objects.get(id=auctionhouseid)
            auctionhousename = ahobj.housename
            ahid = ahobj.id
        except:
            pass
        auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
        if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
            auctionperiod += " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
        d = {'auctionname' : auctionobj.auctionname, 'auctionid' : auctionobj.auctionid, 'auctionhouse' : auctionhousename, 'coverimage' : auctionobj.coverimage, 'ahid' : ahid, 'auctionperiod' : auctionperiod, 'aucid' : auctionobj.id, 'lotcount' : str(auctionobj.lotcount)}
        if aucctr > maxsearchresults:
            break
        aucctr += 1
        allauctions.append(d)
    context['allauctions'] = allauctions
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    return HttpResponse(json.dumps(context))



def moreauctions(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    atype = "0"
    if request.method == 'GET':
        if 'atype' in request.GET.keys():
            atype = str(request.GET['atype'])
    if atype != "0" and atype != "1":
        return HttpResponseRedirect("/auction/index/")
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 4
    rows = 6
    featuredsize = 4
    maxauctions = 10
    maxlots = 8
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    startctr = (chunksize * rows) * (int(page) -1) + featuredsize
    endctr = (chunksize * rows) * int(page) + featuredsize
    paststartrowctr = int(page) * (maxauctions * chunksize)
    pastendrowctr = int(page) * (maxauctions * chunksize) + (maxauctions * chunksize)
    context = {}
    #allartists = {}
    allauctions = {}
    filterauctions = []
    curdatetime = datetime.datetime.now()
    try:
        if int(atype) == 0: # get all upcoming auctions
            allauctions = pickle.loads(redis_instance.get('ac_upcomingauctions'))
            rowstartctr = startctr
            rowendctr = endctr
        else:
            allauctions = pickle.loads(redis_instance.get('ac_pastauctions'))
            rowstartctr = paststartrowctr
            rowendctr = pastendrowctr
        filterauctions = pickle.loads(redis_instance.get('ac_filterauctions'))
        #allartists = pickle.loads(redis_instance.get('ac_allartists'))
    except:
        filterauctions = []
        #allartists = {}
        allauctions = {}
    if allauctions.__len__() == 0: # We didn't get any data from redis cache...
        auctionsqset = Auction.objects.all().order_by('-auctionstartdate', 'priority')
        aucctr = 0
        rctr = 0
        allauctions['row0'] = []
        for auction in auctionsqset[rowstartctr:]:
            auctionname = auction.auctionname
            filterauctions.append(auctionname)
            if int(atype) == 1 and auction.auctionstartdate > curdatetime: # This is an upcoming auction, but we want past auctions only.
                continue
            elif int(atype) == 0 and auction.auctionstartdate <= curdatetime: # This is a past auction, we want upcoming only.
                continue
            auction_id = auction.id
            #auctionlots = Lot.objects.filter(auction_id=auction.id)
            #if auctionlots.__len__() == 0:
            #    continue
            aucctr += 1
            if auctionname not in allauctions.keys():
                allauctions[auctionname] = []
            auctionperiod = auction.auctionstartdate.strftime("%d %b, %Y")
            if auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                auctionperiod += " - " + auction.auctionenddate.strftime("%d %b, %Y")
            auctionhouse = None
            auctionhousename, ahid, location = "", auction.auctionhouse_id, ""
            try:
                auctionhouse = AuctionHouse.objects.get(id=auction.auctionhouse_id)
                auctionhousename = auctionhouse.housename
                location = auctionhouse.location
            except:
                pass
            d = {'auctionname' : auctionname, 'image' : auction.coverimage, 'auctionhouse' : auctionhousename, 'auctionurl' : "", 'auctionperiod' : auctionperiod, 'aucid' : auction.id, 'ahid' : ahid, 'location' : location}
            if allauctions.keys().__len__() > maxauctions * chunksize:
                break
            if aucctr % 4 == 0:
                rctr += 1
                allauctions['row' + str(rctr)] = []
            allauctions['row' + str(rctr)].append(d)
            aucctr += 1
        try:
            #redis_instance.set('ac_allartists', pickle.dumps(allartists))
            if int(atype) == 0:
                redis_instance.set('ac_upcomingauctions', pickle.dumps(allauctions))
            elif int(atype) == 1:
                redis_instance.set('ac_pastauctions', pickle.dumps(allauctions))
        except:
            pass
    #context['allartists'] = allartists
    context['allauctions'] = allauctions
    context['filterauctions'] = filterauctions
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    context['atype'] = atype
    prevpage = int(page) - 1
    nextpage = int(page) + 1
    displayedprevpage1 = 0
    displayedprevpage2 = 0
    if prevpage > 0:
        displayedprevpage1 = prevpage - 1
        displayedprevpage2 = prevpage - 2
    displayednextpage1 = nextpage + 1
    displayednextpage2 = nextpage + 2
    firstpage = 1
    context['pages'] = {'prevpage' : prevpage, 'nextpage' : nextpage, 'firstpage' : firstpage, 'displayedprevpage1' : displayedprevpage1, 'displayedprevpage2' : displayedprevpage2, 'displayednextpage1' : displayednextpage1, 'displayednextpage2' : displayednextpage2, 'currentpage' : int(page)}
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('moreauctions.html')
    return HttpResponse(template.render(context, request))



def showauction(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    aucid = ""
    if request.method == 'GET':
        if 'aucid' in request.GET.keys():
            aucid = str(request.GET['aucid'])
    if aucid == "":
        return HttpResponse("ShowAuction: Required parameter (aucid) missing.")
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 4
    rows = 6
    maxselectlots = 4
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    startctr = (chunksize * rows) * (int(page) -1)
    endctr = (chunksize * rows) * int(page)
    context = {}
    allartists = {}
    alllots = []
    selectlots = []
    nationalities = {}
    auctioninfo = {}
    curdatetime = datetime.datetime.now()
    auctionobj = None
    try:
        auctionobj = Auction.objects.get(id=aucid)
    except:
        return HttpResponse("Could not find auction identified by ID %s: %s"%(aucid, sys.exc_info()[1].__str__()))
    auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
    if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
        auctionperiod += " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
    auctioninfo['auctionname'] = auctionobj.auctionname
    auctioninfo['auctionperiod'] = auctionperiod
    auctioninfo['auctionid'] = auctionobj.auctionid
    auctioninfo['coverimage'] = auctionobj.coverimage
    auctioninfo['lotcount'] = auctionobj.lotcount
    auctioninfo['aucid'] = aucid
    housename, ahid = "", ""
    ahobj = None
    try:
        ahobj = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
        housename = ahobj.housename
        ahid = ahobj.id
    except:
        pass
    auctioninfo['auctionhouse'] = housename
    auctioninfo['ahid'] = ahid
    context['auctioninfo'] = auctioninfo
    # We won't be using redis cache in this controller function. It would be a drain on memory if we 
    # start loading the lots info for every auction the user chooses to dig into.
    alllotsqset = Lot.objects.filter(auction_id=aucid)
    if alllotsqset.__len__() == 0:
        context['warning'] = "Could not find any lot/artwork information for '%s'"%auctionobj.auctionname
        template = loader.get_template('showauction.html')
        return HttpResponse(template.render(context, request))
    lotctr = 0
    for lotobj in alllotsqset:
        artwork = None
        try:
            artwork = Artwork.objects.get(id=lotobj.artwork_id)
        except:
            continue # If we could not find the corresponding artwork, then we simply skip it.
            # Ideally, we should be logging this somewhere, and it should be implemented later.
        artistobj = None
        try:
            artistobj = Artist.objects.get(id=artwork.artist_id)
        except:
            continue # Again, if artist could not be identified for the lot, we skip the lot entirely.
            # This too should be logged. TO DO later.
        artistnationality = artistobj.nationality
        nationalities[artistnationality] = 1
        artistname = artistobj.artistname
        lottitle = artwork.artworkname
        estimate = str(lotobj.lowestimateUSD)
        if lotobj.highestimateUSD > 0.00:
            estimate += " - " + str(lotobj.highestimateUSD)
        d = {'lottitle' : lottitle, 'artist' : artistname, 'medium' : lotobj.medium, 'size' : lotobj.sizedetails, 'image' : lotobj.lotimage1, 'description' : artwork.description, 'estimate' : estimate, 'lid' : lotobj.id, 'aid' : artistobj.id}
        if artistname not in allartists.keys():
            allartists[artistname] = artistobj.id
        alllots.append(d)
        if lotctr < maxselectlots:
            selectlots.append(d)
        lotctr += 1
    context['alllots'] = alllots
    context['selectlots'] = selectlots
    context['allartists'] = allartists
    context['nationalities'] = nationalities
    template = loader.get_template('showauction.html')
    return HttpResponse(template.render(context, request))



def morefilter(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'err' : "Invalid method of call"}))
    aucid = None
    medium, size, sizeunit, artist, nationality = "", "", "", "", ""
    requestbody = str(request.body)
    bodycomponents = requestbody.split("&")
    requestdict = {}
    for comp in bodycomponents:
        compparts = comp.split("=")
        if compparts.__len__() > 1:
            compparts[0] = compparts[0].replace("b'", "")
            requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
    endbarPattern = re.compile("\|\s*$")
    if request.method == 'POST':
        if 'aucid' in requestdict.keys():
            aucid = str(requestdict['aucid']).strip()
        if 'medium' in requestdict.keys():
            medium = str(requestdict['medium']).strip()
            medium = endbarPattern.sub("", medium)
        if 'size' in requestdict.keys():
            size = str(requestdict['size']).strip()
            size = endbarPattern.sub("", size)
        if 'sizeunit' in requestdict.keys():
            sizeunit = str(requestdict['sizeunit']).strip()
            sizeunit = endbarPattern.sub("", sizeunit)
        if 'artist' in requestdict.keys():
            artist = str(requestdict['artist']).strip()
            artist = endbarPattern.sub("", artist)
        if 'nationality' in requestdict.keys():
            nationality = str(requestdict['nationality']).strip()
            nationality = endbarPattern.sub("", nationality)
    mediumlist, artistlist, nationalitylist, sizelist = [], [], [], []
    if not aucid:
        return HttpResponse(json.dumps({'err' : "Invalid Request: Request is missing auction ID"}))
    #print(medium)
    mediumlist = medium.split("|")
    artistlist = artist.split("|")
    nationalitylist = nationality.split("|")
    sizelist = size.split("|")
    context = {}
    filteredlots = []
    uniquelots = {}
    auctionobj = None
    maxsearchresults = 50 # No more than 50 records will be sent back. More than 50 records usually end up crashing the browser.
    try:
        auctionobj = Auction.objects.get(id=aucid)
    except:
        return HttpResponse(json.dumps({'err' : "Could not find auction identified by the ID %s"%aucid}))
    lotqset = Lot.objects.filter(auction_id=aucid)
    for lot in lotqset:
        artwork = None
        try:
            artwork = Artwork.objects.get(id=lot.artwork_id)
        except:
            continue # If we can't find the artwork associated with the lot in question, should we go ahead?
            # At this moment I think we shouldn't, since we won't be able to provide much info about the lot.
        if mediumlist.__len__() > 0 or artistlist.__len__() > 0 or nationalitylist.__len__() > 0 or sizelist.__len__() > 0:
            estimatelow = str(lot.lowestimateUSD)
            estimatehigh = str(lot.highestimateUSD)
            estimate = estimatelow + " - " + estimatehigh
            artistobj = None
            artistname, aid = "", ""
            try:
                artistobj = Artist.objects.get(id=artwork.artist_id)
                artistname = artistobj.artistname
                aid = artistobj.id
            except:
                pass
            aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
            if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y") + " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
            d = {'artworkname' : artwork.artworkname, 'artistname' : artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : auctionobj.auctionname, 'aucid' : auctionobj.id, 'aucstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'aucenddate' : auctionobj.auctionenddate.strftime("%d %b, %Y"), 'aucperiod' : aucperiod, 'aid' : aid, 'image' : artwork.image1, 'soldprice' : lot.soldpriceUSD, 'estimate' : estimate, 'lid' : lot.id}
            for medium in mediumlist:
                if medium in artwork.medium.lower():
                    if artwork.artworkname not in uniquelots.keys():
                        filteredlots.append(d)
                        uniquelots[artwork.artworkname] = 1
                    break # We have matched at least one of the selected mediums. So this lot is included in list. Go to next lot.
            try:
                for nationality in nationalitylist:
                    if nationality.lower() in artistobj.nationality.lower():
                        if artwork.artworkname not in uniquelots.keys():
                            filteredlots.append(d)
                            uniquelots[artwork.artworkname] = 1
                        break # We have matched at least one of the selected nationality. So this lot is included in list. Go to next lot.
                for artist_id in artistlist:
                    if artist_id == artistobj.id:
                        if artwork.artworkname not in uniquelots.keys():
                            filteredlots.append(d)
                            uniquelots[artwork.artworkname] = 1
                        break # We have matched at least one of the selected artists. So this lot is included in list. Go to next lot.
            except:
                pass
            if lot.measureunit == sizeunit:
                for sizespec in sizelist:
                    if sizespec == 'small':
                        if lot.height != "" and int(lot.height) < 40:
                            if artwork.artworkname not in uniquelots.keys():
                                filteredlots.append(d)
                                uniquelots[artwork.artworkname] = 1 # Size matches. So this lot is included.
                            break
                    if sizespec == 'medium':
                        if lot.height != "" and int(lot.height) >= 40 and int(lot.height) < 100:
                            if artwork.artworkname not in uniquelots.keys():
                                filteredlots.append(d)
                                uniquelots[artwork.artworkname] = 1 # Size matches. So this lot is included.
                            break
                    if sizespec == 'large':
                        if lot.height != "" and int(lot.height) >= 100:
                            if artwork.artworkname not in uniquelots.keys():
                                filteredlots.append(d)
                                uniquelots[artwork.artworkname] = 1 # Size matches. So this lot is included.
                            break
    context['filteredlots'] = filteredlots
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    return HttpResponse(json.dumps(context))





