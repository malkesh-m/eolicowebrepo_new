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
import MySQLdb

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
    pagemap = {'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5, 'f' : 6, 'g' : 7, 'h' : 8, 'i' : 9, 'j' : 10, 'k' : 11, 'l' : 12, 'm' : 13, 'n' : 14, 'o' : 15, 'p' : 16, 'q' : 17, 'r' : 18, 's' : 19, 't' : 20, 'u' : 21, 'v' : 22, 'w' : 23, 'x' : 24, 'y' : 25, 'z' : 26, '-' : 1}
    pageno = "-"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            pageno = str(request.GET['page'])
    try:
        page = pagemap[pageno]
    except:
        page = 1
    chunksize = 4
    rows = 6
    featuredsize = 4
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    startctr = (chunksize * rows) * (int(page) -1) + featuredsize
    endctr = (chunksize * rows) * int(page) + featuredsize
    dbconn = MySQLdb.connect(user="eolicouser",passwd="secretpasswd",host="localhost",db="gaidbpure")
    cursor = dbconn.cursor()
    context = {}
    featuredartists = []
    uniqartistsnames = []
    try:
        featuredartists = pickle.loads(redis_instance.get('at_featuredartists'))
    except:
        featuredartists = []
    uniqartists = {}
    if featuredartists.__len__() == 0:
        artist_view_sql = "create or replace view featured_artists as select fa.fa_artist_ID as artist_id, fa.fa_artist_name as artist_name, fal.fal_lot_sale_price_USD as artist_price_usd, fa.fa_artist_name_prefix as prefix, fa.fa_artist_nationality as nationality, fa.fa_artist_birth_year as birthyear, fa.fa_artist_death_year as deathyear, fa.fa_artist_description as description, fa.fa_artist_aka as aka, fa.fa_artist_bio as bio, fa.fa_artist_image as artistimage, fa.fa_artist_genre as genre from fineart_artists fa, fineart_artworks faa, fineart_lots fal where fa.fa_artist_ID=faa.faa_artist_ID and faa.faa_artwork_ID=fal.fal_artwork_ID"
        cursor.execute(artist_view_sql)
        dbconn.commit()
        whereclause = ""
        if page != 1:
            whereclause = "where artist_name like '" + str(pageno) + "%'"
        getview_sql = "select artist_id, artist_name, sum(artist_price_usd) as price, prefix, nationality, birthyear, deathyear, description, aka, bio, artistimage, genre from featured_artists %s group by artist_id order by price desc"%whereclause
        #print(getview_sql)
        cursor.execute(getview_sql)
        artistsqset = cursor.fetchall()
        for artist in artistsqset:
            artistid = artist[0]
            artistname = artist[1]
            price = artist[2]
            prefix = artist[3]
            nationality = artist[4]
            birthyear = artist[5]
            deathyear = artist[6]
            description = artist[7]
            aka = artist[8]
            bio = artist[9]
            artistimage = artist[10]
            genre = artist[11]
            if artistname not in uniqartists.keys():
                uniqartists[artistname] = [artistid, artistname, float(price), prefix, nationality, birthyear, deathyear, description, aka, bio, artistimage, genre]
            else:
                l = uniqartists[artistname]
                l[2] = float(l[2]) + float(price)
                uniqartists[artistname] = l
        uniqartistsnames = list(uniqartists.keys())
        for artistname in uniqartistsnames[0:featuredsize]:
            artist = uniqartists[artistname]
            artistid = artist[0]
            artistname = artist[1]
            price = artist[2]
            prefix = artist[3]
            nationality = artist[4]
            birthyear = artist[5]
            deathyear = artist[6]
            description = artist[7]
            aka = artist[8]
            bio = artist[9]
            artistimage = artist[10]
            genre = artist[11]
            if nationality == "na":
                nationality = ""
            if birthyear == 0:
                birthyear = ""
            if prefix != "" and prefix != "na":
                prefix = prefix + " "
            d = {'artistname' : artistname, 'nationality' : nationality, 'birthdate' : str(birthyear), 'deathdate' : str(deathyear), 'about' : description, 'profileurl' : '', 'artistimage' : artistimage, 'aid' : str(artistid), 'totalsold' : str(price)}
            artworkqset = Artwork.objects.filter(artist_id=artistid).order_by('priority')
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
    try:
        uniqueartists = pickle.loads(redis_instance.get('at_uniqueartists'))
        uniqueartworks = pickle.loads(redis_instance.get('at_uniqueartworks'))
        allartists = pickle.loads(redis_instance.get('at_allartists'))
    except:
        pass
    if allartists[0].__len__() == 0:
        if uniqartistsnames.__len__() > featuredsize:
            for artistname in uniqartistsnames[startctr:endctr]:
                artist = uniqartists[artistname]
                artistid = artist[0]
                artistname = artist[1]
                price = artist[2]
                prefix = artist[3]
                nationality = artist[4]
                birthyear = artist[5]
                deathyear = artist[6]
                description = artist[7]
                aka = artist[8]
                bio = artist[9]
                artistimage = artist[10]
                genre = artist[11]
                #print(artistname)
                if nationality == "na":
                    nationality = ""
                if birthyear == 0:
                    birthyear = ""
                if prefix != "" and prefix != "na":
                    prefix = prefix + " "
                d = {'artistname' : artistname, 'nationality' : nationality, 'birthdate' : str(birthyear), 'deathdate' : str(deathyear), 'about' : description, 'profileurl' : '', 'artistimage' : artistimage, 'aid' : str(artistid)}
                artworkqset = Artwork.objects.filter(artist_id=artistid).order_by() # Ordered by 'priority' - descending.
                if artworkqset.__len__() == 0:
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
        allartistsqset = Artist.objects.all()
        for artist in allartistsqset[0:2000]:
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
    dbconn.close() # Closing db connection. Don't want unwanted open connections.
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
    yearlylotssold = 0
    sellthrurate = 0.0
    avgsaleprice = 0.00
    salepriceoverestimate = 0
    totallotssold = 0
    totalartworks = 0
    soldlotsprice = 0.00
    try:
        allartworks = pickle.loads(redis_instance.get('at_allartworks_%s'%artistobj.id))
        allartworks1 = pickle.loads(redis_instance.get('at_allartworks1_%s'%artistobj.id))
        allartworks2 = pickle.loads(redis_instance.get('at_allartworks2_%s'%artistobj.id))
        allartworks3 = pickle.loads(redis_instance.get('at_allartworks3_%s'%artistobj.id))
        allartworks4 = pickle.loads(redis_instance.get('at_allartworks4_%s'%artistobj.id))
        yearlylotssold = redis_instance.get('at_yearlylotssold_%s'%artistobj.id)
        sellthrurate = redis_instance.get('at_sellthrurate_%s'%artistobj.id)
        avgsaleprice = redis_instance.get('at_avgsaleprice_%s'%artistobj.id)
        salepriceoverestimate = redis_instance.get('at_salepriceoverestimate_%s'%artistobj.id)
        totallotssold = redis_instance.get('at_totallotssold_%s'%artistobj.id)
    except:
        pass
    uniqueartworks = {}
    actr = 0
    lotqset = list()
    if allartworks.__len__() == 0:
        artworksqset = Artwork.objects.filter(artist_id=aid).order_by('priority')
        date2yearsago = datetime.datetime.now() - datetime.timedelta(days=2*365)
        totaldelta = 0.00
        for artwork in artworksqset:
            lotqset = Lot.objects.filter(artwork_id=artwork.id)
            for lotobj in lotqset:
                saledate = datetime.datetime.combine(lotobj.saledate, datetime.time(0, 0))
                if saledate and saledate > date2yearsago:
                    totallotssold += 1
                    soldlotsprice += float(lotobj.soldprice)
                    midestimate = (float(lotobj.highestimate) + float(lotobj.lowestimate))/2.0
                    if lotobj.soldprice > 0.00:
                        delta = (float(lotobj.soldprice) - float(midestimate))/float(lotobj.soldprice)
                        totaldelta += delta
                totalartworks += 1
            d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationstartdate, 'size' : artwork.sizedetails, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'provenance' : '', 'literature' : artwork.literature, 'exhibitions' : artwork.exhibitions, 'href' : '', 'estimate' : '', 'awid' : artwork.id, 'aid' : aid}
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
        yearlylotssold = int(float(totallotssold)/2.0)
        sellthrurate = (float(totallotssold)/float(totalartworks)) * 100.00
        sellthrurate = '{:.2f}'.format(sellthrurate)
        avgsaleprice = float(soldlotsprice)/float(totallotssold)
        avgsaleprice = '{:.2f}'.format(avgsaleprice)
        salepriceoverestimate = (float(totaldelta)/float(totallotssold)) * 100.00
        salepriceoverestimate = '{:.2f}'.format(salepriceoverestimate)
        try:
            redis_instance.set('at_allartworks_%s'%artistobj.id, pickle.dumps(allartworks))
            redis_instance.set('at_allartworks1_%s'%artistobj.id, pickle.dumps(allartworks1))
            redis_instance.set('at_allartworks2_%s'%artistobj.id, pickle.dumps(allartworks2))
            redis_instance.set('at_allartworks3_%s'%artistobj.id, pickle.dumps(allartworks3))
            redis_instance.set('at_allartworks4_%s'%artistobj.id, pickle.dumps(allartworks4))
            redis_instance.set('at_yearlylotssold_%s'%artistobj.id, yearlylotssold)
            redis_instance.set('at_sellthrurate_%s'%artistobj.id, sellthrurate)
            redis_instance.set('at_avgsaleprice_%s'%artistobj.id, avgsaleprice)
            redis_instance.set('at_totallotssold_%s'%artistobj.id, totallotssold)
            redis_instance.set('at_salepriceoverestimate_%s'%artistobj.id, salepriceoverestimate)
        except:
            pass
    context['yearlylotssold'] = yearlylotssold
    context['sellthrurate'] = sellthrurate
    context['avgsaleprice'] = avgsaleprice
    context['salepriceoverestimate'] = salepriceoverestimate
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
            try:
                lotqsetlist = list(lotqset)
                if lotqsetlist.__len__() == 0:
                    continue
                auctionid = lotqset[0].auction_id
            except:
                continue
            auctionsqset = Auction.objects.filter(id=auctionid)
            if auctionsqset.__len__() == 0:
                continue
            eventname = auctionsqset[0].auctionname
            eventurl = auctionsqset[0].auctionurl
            eventinfo = ''
            eventperiod = auctionsqset[0].auctionstartdate.strftime("%d %b, %Y")
            if auctionsqset[0].auctionenddate.strftime("%d %b, %Y") != '01 Jan, 0001' and auctionsqset[0].auctionenddate.strftime("%d %b, %Y") != '01 Jan, 1':
                eventperiod = eventperiod + " - " + auctionsqset[0].auctionenddate.strftime("%d %b, %Y")
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
    pageno = 1
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            pageno = str(request.GET['page'])
    page = int(pageno)
    chunksize = 4
    rows = 6
    featuredsize = 24
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
        for artist in matchingartistsqset[startctr:endctr]:
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
    filterartists = []
    try:
        filterartists = pickle.loads(redis_instance.get('at_filterartists'))
    except:
        pass
    if filterartists.__len__() == 0:
        allartistsqset = Artist.objects.all()
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


def showartwork(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    awid = None
    if request.method == 'GET':
        if 'awid' in request.GET.keys():
            awid = str(request.GET['awid']).strip()
    if not awid or awid == "":
        return HttpResponse("Invalid Request: Request is missing artwork identifier")
    return HttpResponse("")






