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

from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.models import User as djUser
from django.contrib.auth.decorators import login_required

import os, sys, re, time, datetime
import simplejson as json
import redis
import pickle
import urllib
import MySQLdb
import unicodedata, itertools

#from gallery.models import Gallery, Event
from login.models import User, Session, Favourite #,WebConfig, Carousel, Follow
#from login.views import getcarouselinfo
#from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from auctions.models import Auction, Lot
from artists.models import Artist, Artwork
from auctionhouses.models import AuctionHouse

# Caching related imports and variables
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def removecontrolcharacters(s):
    all_chars = (chr(i) for i in range(sys.maxunicode))
    categories = {'Cc'}
    control_chars = ''.join(map(chr, itertools.chain(range(0x00,0x20), range(0x7f,0xa0))))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))
    return control_char_re.sub('', s)


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
    curdate = datetime.date(curdatetime.year, curdatetime.month, curdatetime.day)
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    cursor = dbconn.cursor()
    if allauctions.__len__() == 0:
        auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar order by faac_auction_start_date desc limit 100"
        #print("auctionsql: %s"%auctionsql)
        cursor.execute(auctionsql)
        auctionsqset = cursor.fetchall()
        try:
            auctionhouseidslist = []
            auctionauctionhousesdict = {}
            for auction in auctionsqset[rowstartctr:]:
                if type(auction[5]) == datetime.date and auction[5] <= curdate: # this is a past auction, so skip.
                    continue
                auchouseid = auction[3]
                auctionhouseidslist.append(auchouseid)
            auctionhousesqset = AuctionHouse.objects.filter(id__in=auctionhouseidslist)
            for auchouse in auctionhousesqset:
                auctionauctionhousesdict[str(auchouse.id)] = auchouse
            aucctr = 0
            for auction in auctionsqset[rowstartctr:]:
                if featuredauctions.keys().__len__() > maxupcomingauctions:
                    break
                auctionname = auction[1]
                #print(auctionname)
                salecode = auction[2]
                autocompleteauctionname = auctionname
                autocompleteauctionname = autocompleteauctionname.replace('"', "")
                autocompleteauctionname = removecontrolcharacters(autocompleteauctionname)
                filterauctions.append(autocompleteauctionname)
                if auction[5] <= curdate: # this is a past auction, so skip.
                    continue
                if aucctr > rowendctr:
                    break
                aucctr += 1
                auctionurl = auction[4]
                #auctionlots = Lot.objects.filter(auction_id=auction[0])
                #if auctionlots.__len__() == 0:
                #    continue
                auctionperiod = auction[5].strftime("%d %b, %Y")
                aucenddate = auction[6]
                if str(aucenddate) != "0000-00-00" and aucenddate != "01 Jan, 1":
                    auctionperiod += " - " + str(aucenddate)
                auctionhouse = None
                auctionhousename, ahid, location = "", auction[3], ""
                try:
                    auctionhouse = auctionauctionhousesdict[str(auction[3])]
                    auctionhousename = auctionhouse.housename
                    location = auctionhouse.location
                except:
                    pass
                # Check for favourites
                if request.user.is_authenticated:
                    favqset = Favourite.objects.filter(user=request.user, reference_model="fineart_auction_calendar", reference_model_id=auction[0])
                else:
                    favqset = []
                favflag = 0
                if favqset.__len__() > 0:
                    favflag = 1        
                d = {'auctionname' : auctionname, 'image' : auction[8], 'auctionhouse' : auctionhousename, 'auctionurl' : "", 'auctionperiod' : auctionperiod, 'aucid' : auction[0], 'ahid' : ahid, 'location' : location, 'favourite' : favflag, 'salecode' : salecode}
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
        pastauctionhouseidslist = []
        pastauctionauctionhousesdict = {}
        for auction in auctionsqset[pastrowstartctr:]:
            if type(auction[5]) == datetime.date and auction[5] > curdate:
                continue
            auchouseid = auction[3]
            pastauctionhouseidslist.append(auchouseid)
        auctionhousesqset = AuctionHouse.objects.filter(id__in=pastauctionhouseidslist)
        for auchouse in auctionhousesqset:
            pastauctionauctionhousesdict[str(auchouse.id)] = auchouse
        aucctr = 0
        rctr = 0
        allauctions['row0'] = []
        for auction in auctionsqset[pastrowstartctr:]:
            if auction[5] > curdate:
                continue
            auctionname = auction[1]
            autocompleteauctionname = auctionname
            autocompleteauctionname = autocompleteauctionname.replace('"', "")
            autocompleteauctionname = removecontrolcharacters(autocompleteauctionname)
            filterauctions.append(autocompleteauctionname)
            auction_id = auction[0]
            salecode = auction[2]
            #auctionlots = Lot.objects.filter(auction_id=auction[0])
            #if auctionlots.__len__() == 0:
            #    continue
            if auctionname not in allauctions.keys():
                allauctions[auctionname] = []
            auctionperiod = auction[5].strftime("%d %b, %Y")
            aucenddate = auction[6]
            if str(aucenddate) != "0000-00-00" and aucenddate != "01 Jan, 1":
                auctionperiod += " - " + str(aucenddate)
            auctionhouse = None
            auctionhousename, ahid, location = "", auction[3], ""
            try:
                auctionhouse = pastauctionauctionhousesdict[str(auction[3])]
                auctionhousename = auctionhouse.housename
                location = auctionhouse.location
            except:
                pass
            # Check for favourites
            if request.user.is_authenticated:
                favqset = Favourite.objects.filter(user=request.user, reference_model="fineart_auction_calendar", reference_model_id=auction[0])
            else:
                favqset = []
            favflag = 0
            if favqset.__len__() > 0:
                favflag = 1   
            d = {'auctionname' : auctionname, 'image' : auction[8], 'auctionhouse' : auctionhousename, 'auctionurl' : "", 'auctionperiod' : auctionperiod, 'aucid' : auction[0], 'ahid' : ahid, 'location' : location, 'favourite' : favflag, 'salecode' : salecode}
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
    cursor.close()
    dbconn.close()
    #carouselentries = getcarouselinfo()
    #context['carousel'] = carouselentries
    if request.user.is_authenticated and request.user.is_staff:
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
    #dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    #cursor = dbconn.cursor()
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
        auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
        aucenddate = auction.auctionenddate
        if str(aucenddate) != "0000-00-00" and aucenddate != "01 Jan, 1":
            auctionperiod += " - " + str(aucenddate)
    except:
        pass
    auctionhousename, houselocation = "", ""
    try:
        auctionhouseobj = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
        auctionhousename = auctionhouseobj.housename
        houselocation = auctionhouseobj.location
    except:
        pass
    estimate = str(lotobj.lowestimateUSD)
    if lotobj.highestimateUSD is not None and lotobj.highestimateUSD > 0.00:
        estimate += " - " + str(lotobj.highestimateUSD)
    artworkdesc = artworkdesc.replace("<strong><br>Description:</strong><br>", "")
    artworkdesc = artworkdesc.replace("<strong>Description:</strong>", "")
    artworkdesc = artworkdesc.replace("<br>", "")
    artworkdesc = artworkdesc.replace("<strong>", "").replace("</strong>", "")
    lotinfo = {'title' : artworkname, 'description' : artworkdesc, 'artist' : artistname, 'birth' : artistbirth, 'death' : artistdeath, 'nationality' : nationality, 'medium' : lotobj.medium, 'size' : lotobj.sizedetails, 'auctionname' : auctionname, 'estimate' : estimate, 'soldprice' : str(lotobj.soldpriceUSD), 'currency' : "USD", 'provenance' : lotobj.provenance, 'literature' : literature, 'exhibitions' : exhibition, 'image1' : lotobj.lotimage1, 'image2' : lotobj.lotimage2, 'image3' : lotobj.lotimage3, 'image4' : lotobj.lotimage4, 'url' : lotobj.source, 'category' : lotobj.category, 'created' : createdate, 'lotid' : lotobj.id, 'aid' : artistid, 'lotno' : lotobj.lotid, 'auctionperiod' : auctionperiod, 'housename' : auctionhousename, 'location' : houselocation}
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
        lotsqset = Lot.objects.filter(auction_id=lotobj.auction_id).order_by()
        numlots = chunksize * rows
        if lotsqset.__len__() < numlots:
            numlots = lotsqset.__len__()
        artworkidslist = []
        artistidslist = []
        for lot in lotsqset[0:numlots]:
            awid = lot.artwork_id
            artworkidslist.append(awid)
        artworksqset = Artwork.objects.filter(id__in=artworkidslist)
        artworksdict = {}
        for aw in artworksqset:
            artworksdict[str(aw.id)] = aw
            artistidslist.append(aw.artist_id)
        artistsdict = {}
        artistsqset = Artist.objects.filter(id__in=artistidslist)
        for aobj in artistsqset:
            artistsdict[str(aobj.id)] = aobj
        actr = 0
        rctr = 0
        for lot in lotsqset[0:numlots]:
            artwork = None
            try:
                artwork = artworksdict[str(lot.artwork_id)]
            except:
                continue
            artistname = ""
            try:
                artist = artistsdict[str(artwork.artist_id)]
                artistname = artist.artistname
            except:
                pass
            estimate = str(lot.lowestimateUSD)
            if lot.highestimateUSD is not None and lot.highestimateUSD > 0.00:
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
        relatedqset = Artwork.objects.filter(artist_id=artistobj.id) # Getting artworks by the same artist, in any auction.
        numlots = chunksize * rows
        if relatedqset.__len__() < numlots:
            numlots = relatedqset.__len__()
        rctr = 0
        awidslist = []
        artistsidlist = []
        for aw in relatedqset[0:numlots]:
            awidslist.append(aw.id)
            artistsidlist.append(aw.artist_id)
        rel_lotsdict = {}
        rel_artistsdict = {}
        rel_artistnamedict = {}
        rel_lotqset = Lot.objects.filter(artwork_id__in=awidslist)
        for rel_lot in rel_lotqset:
            rel_lotsdict[str(rel_lot.artwork_id)] = rel_lot
        rel_artistsqset = Artist.objects.filter(id__in=artistsidlist)
        for relartist in rel_artistsqset:
            rel_artistsdict[str(relartist.id)] = relartist
            rel_artistnamedict[relartist.artistname.lower()] = relartist
        for aw in relatedqset[0:numlots]:
            rel_lotobj = None
            rel_estimate = ""
            rel_lotobj = rel_lotsdict[str(aw.id)]
            if rel_lotobj is not None:
                rel_estimate = str(rel_lotobj.lowestimateUSD)
                if rel_lotobj.highestimateUSD is not None and rel_lotobj.highestimateUSD > 0.00:
                    rel_estimate += " - " + str(rel_lotobj.highestimateUSD)
            else:
                continue
            rel_artistname = ""
            rel_artist = None
            try:
                rel_artist = rel_artistsdict[str(aw.artist_id)]
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
                    rel_artist = rel_artistnamedict[rel_artistname.lower()]
                    #rel_artist = Artist.objects.get(artistname__iexact=rel_artistname)
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
    if request.user.is_authenticated and request.user.is_staff:
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
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    cursor = dbconn.cursor()
    auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar where faac_auction_title like '%" + searchkey + "%'";
    cursor.execute(auctionsql)
    auctionsqset = cursor.fetchall()
    #auctionsqset = Auction.objects.filter(auctionname__icontains=searchkey)
    allauctions = []
    maxsearchresults = 30
    aucctr = 0
    auctionhouseidslist = []
    auctionhousesdict = {}
    auctionhouseidsstr = ""
    for auctionobj in auctionsqset:
        auctionhouseid = auctionobj[3]
        auctionhouseidslist.append(str(auctionhouseid))
    auctionhouseidsstr = "(" + ",".join(auctionhouseidslist) + ")"
    if auctionhouseidslist.__len__() == 0: # In case we don't find any matching records, we return with empty list.
        context['allauctions'] = []
        if request.user.is_authenticated and request.user.is_staff:
            context['adminuser'] = 1
        else:
            context['adminuser'] = 0
        return HttpResponse(json.dumps(context))
    ahsql = "select cah_auction_house_name, cah_auction_house_ID from core_auction_houses where cah_auction_house_ID in %s"%auctionhouseidsstr
    #print(ahsql)
    cursor.execute(ahsql)
    auchouserecords = cursor.fetchall()
    for auchouse in auchouserecords:
        auchousename = auchouse[0]
        auchouseid = auchouse[1]
        auctionhousesdict[str(auchouseid)] = auchouse
    for auctionobj in auctionsqset:
        auctionhouseid = auctionobj[3]
        ahobj = None
        auctionhousename, ahid = "", ""
        try:
            ahobj = auctionhousesdict[str(auctionhouseid)]
            auctionhousename = ahobj[0]
            ahid = ahobj[1]
        except:
            pass
        auctionperiod = auctionobj[5].strftime("%d %b, %Y")
        aucenddate = auctionobj[6]
        if str(aucenddate) != "0000-00-00" and aucenddate != "01 Jan, 1":
            auctionperiod += " - " + str(aucenddate)
        lotcount = auctionobj[7]
        if not lotcount:
            lotcount = 0
        d = {'auctionname' : auctionobj[1], 'auctionid' : auctionobj[2], 'auctionhouse' : auctionhousename, 'coverimage' : auctionobj[8], 'ahid' : ahid, 'auctionperiod' : auctionperiod, 'aucid' : auctionobj[0], 'lotcount' : str(lotcount)}
        if aucctr > maxsearchresults:
            break
        aucctr += 1
        allauctions.append(d)
    cursor.close()
    dbconn.close()
    context['allauctions'] = allauctions
    if request.user.is_authenticated and request.user.is_staff:
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
    curdate = datetime.date(curdatetime.year, curdatetime.month, curdatetime.day)
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
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    cursor = dbconn.cursor()
    if allauctions.__len__() == 0: # We didn't get any data from redis cache...
        limitval = 100 #(rowendctr - rowstartctr)
        offsetval = rowstartctr
        auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar order by faac_auction_start_date desc limit %s offset %s"%(limitval, offsetval)
        #print(auctionsql)
        cursor.execute(auctionsql)
        auctionsqset = cursor.fetchall()
        #auctionsqset = Auction.objects.all().order_by('-auctionstartdate')
        aucctr = 0
        rctr = 0
        allauctions['row0'] = []
        auctionhouseidslist = []
        for auction in auctionsqset:
            auchouseid = auction[3]
            auctionhouseidslist.append(auchouseid)
        auchouseqset = AuctionHouse.objects.filter(id__in=auctionhouseidslist)
        auchousedict = {}
        for auchouseobj in auchouseqset:
            auchouseid = str(auchouseobj.id)
            auchousedict[auchouseid] = [auchouseobj.housename, auchouseobj.location]
        for auction in auctionsqset:
            auctionname = auction[1]
            filterauctions.append(auctionname)
            if int(atype) == 1 and type(auction[5]) == datetime.date and auction[5] > curdate: # This is an upcoming auction, but we want past auctions only.
                continue
            elif int(atype) == 0 and type(auction[5]) == datetime.date and auction[5] <= curdate: # This is a past auction, we want upcoming only.
                continue
            auction_id = auction[0]
            #auctionlots = Lot.objects.filter(auction_id=auction[0])
            #if auctionlots.__len__() == 0:
            #    continue
            aucctr += 1
            if auctionname not in allauctions.keys():
                allauctions[auctionname] = []
            auctionperiod = auction[5].strftime("%d %b, %Y")
            aucenddate = auction[6]
            if str(aucenddate) != "0000-00-00" and aucenddate != "01 Jan, 1":
                auctionperiod += " - " + str(aucenddate)
            auctionhouse = None
            auctionhousename, ahid, location = "", auction[3], ""
            try:
                auctionhouse = auchousedict[str(auction[3])]
                auctionhousename = auctionhouse[0]
                location = auctionhouse[1]
            except:
                pass
            # Check for favourites
            if request.user.is_authenticated:
                favqset = Favourite.objects.filter(user=request.user, reference_model="fineart_auction_calendar", reference_model_id=auction[0])
            else:
                favqset = []
            favflag = 0
            if favqset.__len__() > 0:
                favflag = 1   
            d = {'auctionname' : auctionname, 'image' : auction[8], 'auctionhouse' : auctionhousename, 'auctionurl' : "", 'auctionperiod' : auctionperiod, 'salecode' : auction[2], 'aucid' : auction[0], 'ahid' : ahid, 'location' : location, 'favourite' : favflag}
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
    cursor.close()
    dbconn.close()
    #context['allartists'] = allartists
    context['allauctions'] = allauctions
    context['filterauctions'] = filterauctions
    #carouselentries = getcarouselinfo()
    #context['carousel'] = carouselentries
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
    if request.user.is_authenticated and request.user.is_staff:
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
    curdate = datetime.date(curdatetime.year, curdatetime.month, curdatetime.day)
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    cursor = dbconn.cursor()
    auctionobj = None
    try:
        auctionobj = Auction.objects.get(id=aucid)
    except:
        return HttpResponse("Could not find auction identified by ID %s: %s"%(aucid, sys.exc_info()[1].__str__()))
    auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
    aucenddate = auctionobj.auctionenddate
    if str(aucenddate) != "0000-00-00" and aucenddate != "01 Jan, 1":
        auctionperiod += " - " + str(aucenddate)
    auctioninfo['auctionname'] = auctionobj.auctionname
    auctioninfo['auctionperiod'] = auctionperiod
    auctioninfo['auctionid'] = auctionobj.auctionid
    auctioninfo['coverimage'] = auctionobj.coverimage
    lotcount = auctionobj.lotcount
    if not lotcount:
        lotcount = 0
    auctioninfo['lotcount'] = lotcount
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
    lotssql = "select fal_lot_ID, fal_lot_no, fal_sub_lot_no, fal_artwork_ID, fal_auction_ID, fal_lot_sale_date, fal_lot_material, fal_lot_size_details, fal_lot_height, fal_lot_width, fal_lot_depth, fal_lot_measurement_unit, fal_lot_category, fal_lot_high_estimate, fal_lot_low_estimate, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_sale_price, fal_lot_sale_price_USD, fal_lot_price_type, fal_lot_condition, fal_lot_status, fal_lot_provenance, fal_lot_published, fal_lot_image1, fal_lot_image2, fal_lot_image3, fal_lot_image4, fal_lot_image5, fal_lot_record_created, fal_lot_record_updated, fal_lot_record_createdby, fal_lot_record_updatedby, fal_lot_source from fineart_lots where fal_auction_ID=%s"%aucid
    cursor.execute(lotssql)
    alllotsqset = cursor.fetchall()
    if alllotsqset.__len__() == 0:
        context['warning'] = "Could not find any lot/artwork information for '%s'"%auctionobj.auctionname
        template = loader.get_template('showauction.html')
        return HttpResponse(template.render(context, request))
    lotctr = 0
    artworkidslist = []
    lotartworksdict = {}
    artistidslist = []
    artworkartistsdict = {}
    for lotobj in alllotsqset:
        artworkid = lotobj[3]
        artworkidslist.append(artworkid)
    artworksqset = Artwork.objects.filter(id__in=artworkidslist)
    for artwork in artworksqset:
        lotartworksdict[str(artwork.id)] = artwork
        artistid = artwork.artist_id
        artistidslist.append(artistid)
    artistsqset = Artist.objects.filter(id__in=artistidslist)
    for artist in artistsqset:
        artworkartistsdict[str(artist.id)] = artist
    for lotobj in alllotsqset:
        artwork = None
        try:
            artwork = lotartworksdict[str(lotobj[3])]
        except:
            continue # If we could not find the corresponding artwork, then we simply skip it.
            # Ideally, we should be logging this somewhere, and it should be implemented later.
        artistobj = None
        try:
            artistobj = artworkartistsdict[str(artwork.artist_id)]
        except:
            continue # Again, if artist could not be identified for the lot, we skip the lot entirely.
            # This too should be logged. TO DO later.
        artistnationality = artistobj.nationality
        nationalities[artistnationality] = 1
        artistname = artistobj.artistname
        lottitle = artwork.artworkname
        estimate = str(lotobj[16])
        if lotobj[15] is not None and lotobj[15] > 0.00:
            estimate += " - " + str(lotobj[15])
        soldprice = str(lotobj[18])
        # Check for favourites
        if request.user.is_authenticated:
            favqset = Favourite.objects.filter(user=request.user, reference_model="fineart_artworks", reference_model_id=lotobj[3])
        else:
            favqset = []
        favflag = 0
        if favqset.__len__() > 0:
            favflag = 1   
        d = {'lottitle' : lottitle, 'artist' : artistname, 'medium' : lotobj[6], 'size' : lotobj[7], 'image' : lotobj[24], 'description' : artwork.description, 'estimate' : estimate, 'lid' : lotobj[0], 'aid' : artistobj.id, 'lotno' : lotobj[1], 'category' : lotobj[12], 'soldprice' : soldprice, 'awid' : lotobj[3], 'favourite' : favflag}
        if artistname not in allartists.keys():
            allartists[artistname] = artistobj.id
        alllots.append(d)
        if lotctr < maxselectlots:
            selectlots.append(d)
        lotctr += 1
    cursor.close()
    dbconn.close()
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
            aucenddate = auction.auctionenddate
            if str(aucenddate) != "0000-00-00" and aucenddate != "01 Jan, 1":
                aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y") + " - " + str(aucenddate)
            auctionhouseobj = None
            auctionhousename = ""
            try:
                auctionhouseobj = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
                auctionhousename = auctionhouseobj.housename
            except:
                pass
            # Check for favourites
            if request.user.is_authenticated:
                favqset = Favourite.objects.filter(user=request.user, reference_model="fineart_artworks", reference_model_id=lot.artwork_id)
            else:
                favqset = []
            favflag = 0
            if favqset.__len__() > 0:
                favflag = 1   
            d = {'artworkname' : artwork.artworkname, 'artistname' : artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : auctionobj.auctionname, 'aucid' : auctionobj.id, 'aucstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'aucenddate' : str(aucenddate), 'aucperiod' : aucperiod, 'aid' : aid, 'image' : artwork.image1, 'soldprice' : lot.soldpriceUSD, 'estimate' : estimate, 'lid' : lot.id, 'lotno' : lot.lotid, 'category' : lot.category, 'auctionhouse' : auctionhousename, 'favourite' : favflag}
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
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    return HttpResponse(json.dumps(context))


@login_required(login_url="/login/show/")
def addfavourite(request):
    """
    Add an auction as a 'favourite' by a legit user.
    """
    if request.method != 'POST':
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aucid' : ''})) # Operation failed!
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aucid' : ''})) # Operation failed!
    userobj = request.user
    sessionkey = request.session.session_key
    entitytype, aucid, divid = None, None, ''
    requestbody = str(request.body)
    bodycomponents = requestbody.split("&")
    requestdict = {}
    for comp in bodycomponents:
        compparts = comp.split("=")
        if compparts.__len__() > 1:
            compparts[0] = compparts[0].replace("b'", "")
            requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
    if 'entityid' in requestdict.keys():
        aucid = requestdict['entityid']
    if 'entitytype' in requestdict.keys():
        entitytype = requestdict['entitytype']
    if 'div_id' in requestdict.keys():
        divid = requestdict['div_id'].replace("'", "")
    if not aucid or not divid:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aucid' : ''})) # Operation failed!
    if entitytype != 'auction':
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aucid' : ''})) # Operation failed!
    auction = None
    try:
        auction = Auction.objects.get(id=aucid)
    except:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : divid, 'aucid' : aucid})) # Operation failed! Can't proceed without an artist.
    # Check if the auction is already a 'favourite' of the user...
    favouriteobj = None
    try:
        favouriteqset = Favourite.objects.filter(user=request.user, reference_model='fineart_auction_calendar', reference_model_id=aucid)
        if favouriteqset.__len__() > 0:
            favouriteobj = favouriteqset[0]
        else:
            favouriteobj = Favourite()
    except:
        favouriteobj = Favourite()
    favouriteobj.user = request.user
    favouriteobj.reference_model = 'fineart_auction_calendar'
    favouriteobj.reference_model_id = aucid
    try:
        favouriteobj.save()
    except:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aucid' : ''})) # Operation failed!
    return HttpResponse(json.dumps({'msg' : 1, 'div_id' : divid, 'aucid' : aucid})) # Added to favourites!




