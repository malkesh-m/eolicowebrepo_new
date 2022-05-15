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
import urllib

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
            whereclause = "and artist_name like '" + str(pageno) + "%'"
        getview_sql = "select artist_id, artist_name, sum(artist_price_usd) as price, prefix, nationality, birthyear, deathyear, description, aka, bio, artistimage, genre from featured_artists where artistimage is not NULL and artistimage != '' %s group by artist_id order by price desc"%whereclause
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
    lotsinupcomingauctions = []
    lotsinpastauctions = []
    yearlylotssold = 0
    sellthrurate = 0.0
    avgsaleprice = 0.00
    salepriceoverestimate = 0
    totallotssold = 0
    totalartworks = 0
    soldlotsprice = 0.00
    maxpastlots = 25
    try:
        allartworks = pickle.loads(redis_instance.get('at_allartworks_%s'%artistobj.id))
        allartworks1 = pickle.loads(redis_instance.get('at_allartworks1_%s'%artistobj.id))
        allartworks2 = pickle.loads(redis_instance.get('at_allartworks2_%s'%artistobj.id))
        allartworks3 = pickle.loads(redis_instance.get('at_allartworks3_%s'%artistobj.id))
        allartworks4 = pickle.loads(redis_instance.get('at_allartworks4_%s'%artistobj.id))
        lotsinupcomingauctions = pickle.loads(redis_instance.get('at_lotsinupcomingauctions_%s'%artistobj.id))
        lotsinpastauctions = pickle.loads(redis_instance.get('at_lotsinpastauctions_%s'%artistobj.id))
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
        curdatetime = datetime.datetime.now()
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
                auctionobj = None
                try:
                    auctionobj = Auction.objects.get(id=lotobj.auction_id)
                except:
                    continue # If we fail to find the auction, there is no use going ahead.
                auctionstartdate = auctionobj.auctionstartdate
                auctionname = auctionobj.auctionname
                if auctionstartdate > curdatetime: # This is an upcoming auction
                    auchouseobj = None
                    try:
                        auchouseobj = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
                        auchousename = auchouseobj.housename
                    except:
                        auchousename = ""
                    auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                    if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "":
                        auctionperiod += " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
                    d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationstartdate, 'size' : artwork.sizedetails, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'provenance' : '', 'literature' : artwork.literature, 'exhibitions' : artwork.exhibitions, 'href' : '', 'estimate' : '', 'awid' : artwork.id, 'aid' : aid, 'auctionname' : auctionname, 'aucid' : auctionobj.id, 'auctionimage' : auctionobj.coverimage, 'auctionstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'auctionenddate' : auctionobj.auctionenddate.strftime("%d %b, %Y"), 'auchousename' : auchousename, 'estimate' : str(lotobj.lowestimate) + " - " + str(lotobj.highestimate), 'auctionperiod' : auctionperiod}
                    lotsinupcomingauctions.append(d)
                else: # Past auction case
                    auchouseobj = None
                    try:
                        auchouseobj = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
                        auchousename = auchouseobj.housename
                    except:
                        auchousename = ""
                    d = {'artworkname' : artwork.artworkname, 'creationdate' : artwork.creationstartdate, 'size' : artwork.sizedetails, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'provenance' : '', 'literature' : artwork.literature, 'exhibitions' : artwork.exhibitions, 'href' : '', 'estimate' : '', 'awid' : artwork.id, 'aid' : aid, 'auctionname' : auctionname, 'aucid' : auctionobj.id, 'auctionimage' : auctionobj.coverimage, 'auctionstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'auctionenddate' : auctionobj.auctionenddate.strftime("%d %b, %Y"), 'auchousename' : auchousename, 'soldprice' : str(lotobj.soldpriceUSD), 'estimate' : str(lotobj.lowestimate) + " - " + str(lotobj.highestimate)}
                    if maxpastlots > lotsinpastauctions.__len__():
                        lotsinpastauctions.append(d)
                    else:
                        continue
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
            redis_instance.set('at_lotsinupcomingauctions_%s'%artistobj.id, pickle.dumps(lotsinupcomingauctions))
            redis_instance.set('at_lotsinpastauctions_%s'%artistobj.id, pickle.dumps(lotsinpastauctions))
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
    shortlen = 100
    if artistobj.bio is None:
        artistobj.bio = ""
    if artistobj.bio.__len__() < shortlen:
        shortlen = artistobj.bio.__len__()
    shortabout = artistobj.bio[:shortlen] + "..."
    artistinfo = {'name' : prefix + artistobj.artistname, 'nationality' : artistobj.nationality, 'birthdate' : artistobj.birthyear, 'deathdate' : artistobj.deathyear, 'profileurl' : '', 'desctiption' : artistobj.description, 'image' : artistobj.artistimage, 'gender' : '', 'about' : artistobj.bio, 'artistid' : artistobj.id, 'shortabout' : shortabout}
    context['allartworks'] = allartworks
    context['allartworks1'] = allartworks1
    context['allartworks2'] = allartworks2
    context['allartworks3'] = allartworks3
    context['allartworks4'] = allartworks4
    context['lotsinupcomingauctions'] = lotsinupcomingauctions
    context['lotsinpastauctions'] = lotsinpastauctions
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
            if artistobj.id == artist.id: # Same artist, so just skip.
                continue
            prefix = ""
            if artist.prefix != "" and artist.prefix != "na":
                prefix = artist.prefix + " "
            aliveperiod = "b. " + str(artist.birthyear)
            if str(artist.deathyear) != "":
                aliveperiod = str(artist.birthyear) + " - " + str(artist.deathyear)
            d = {'artistname' : prefix + artist.artistname, 'nationality' : artist.nationality, 'birthdate' : str(artist.birthyear), 'deathdate' : str(artist.deathyear), 'about' : artist.bio, 'desctiption' : artistobj.description, 'profileurl' : '', 'image' : artist.artistimage, 'aid' : str(artist.id), 'aliveperiod' : aliveperiod}
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
    artworkobj = None
    try:
        artworkobj = Artwork.objects.get(id=awid)
    except:
        return HttpResponse("Couldn't find artwork identified by the given ID")
    context = {}
    artistobj = None
    try:
        artistobj = Artist.objects.get(id=artworkobj.artist_id)
    except:
        pass
    if artistobj is not None:
        artistname = artistobj.artistname
    else:
        artistname = ""
    description = artworkobj.description
    description = description.replace("<strong><br>Description:</strong>", "")
    description = description.replace("<br>", "")
    shortlen = 30
    if description.__len__() < 30:
        shortlen = description.__len__()
    shortdescription = description[:shortlen] + "..."
    context['artworkinfo'] = {'artworkname' : artworkobj.artworkname, 'artistname' : artistname, 'creationdate' : artworkobj.creationstartdate, 'size' : artworkobj.sizedetails, 'medium' : artworkobj.medium, 'description' : description, 'awid' : artworkobj.id, 'aid' : artistobj.id, 'shortdescription' : shortdescription}
    allartworks = []
    allartworks1 = []
    allartworks2 = []
    allartworks3 = []
    allartworks4 = []
    allevents = []
    try:
        allartworks = pickle.loads(redis_instance.get('at_allartworks_%s'%artistobj.id))
        allartworks1 = pickle.loads(redis_instance.get('at_allartworks1_%s'%artistobj.id))
        allartworks2 = pickle.loads(redis_instance.get('at_allartworks2_%s'%artistobj.id))
        allartworks3 = pickle.loads(redis_instance.get('at_allartworks3_%s'%artistobj.id))
        allartworks4 = pickle.loads(redis_instance.get('at_allartworks4_%s'%artistobj.id))
        allevents = pickle.loads(redis_instance.get('at_allevents_%s'%artworkobj.id))
    except:
        pass
    uniqueartworks = {}
    if allartworks.__len__() == 0:
        artworksqset = Artwork.objects.filter(artist_id=artistobj.id)
        actr = 0
        for artwork in artworksqset:
            creationdate = str(artwork.creationstartdate)
            if creationdate == "0":
                creationdate = ""
            d = {'artworkname' : artwork.artworkname, 'creationdate' : creationdate, 'size' : artwork.sizedetails, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : artwork.image1, 'provenance' : '', 'literature' : artwork.literature, 'exhibitions' : artwork.exhibitions, 'href' : '', 'estimate' : '', 'awid' : artwork.id, 'aid' : artwork.artist_id}
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
            lotqset = Lot.objects.filter(artwork_id=artwork.id)
            for lot in lotqset:
                auctionid = lot.auction_id
                auctionobj = None
                try:
                    auctionobj = Auction.objects.get(id=auctionid)
                except:
                    continue
                eventperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                if auctionobj.auctionenddate.strftime("%d %b, %Y") != '01 Jan, 0001' and auctionobj.auctionenddate.strftime("%d %b, %Y") != '01 Jan, 1':
                    eventperiod = eventperiod + " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
                d2 = {'eventname' : auctionobj.auctionname, 'eventimage' : auctionobj.coverimage, 'eventperiod' : eventperiod, 'aucid' : auctionobj.id}
                allevents.append(d2)
        context['allartworks'] = allartworks
        context['allartworks1'] = allartworks1
        context['allartworks2'] = allartworks2
        context['allartworks3'] = allartworks3
        context['allartworks4'] = allartworks4
        context['allevents'] = allevents
        try:
            redis_instance.set('at_allartworks_%s'%artistobj.id, pickle.dumps(allartworks))
            redis_instance.set('at_allartworks1_%s'%artistobj.id, pickle.dumps(allartworks1))
            redis_instance.set('at_allartworks2_%s'%artistobj.id, pickle.dumps(allartworks2))
            redis_instance.set('at_allartworks3_%s'%artistobj.id, pickle.dumps(allartworks3))
            redis_instance.set('at_allartworks4_%s'%artistobj.id, pickle.dumps(allartworks4))
            redis_instance.set('at_allevents_%s'%artworkobj.id, pickle.dumps(allevents))
        except:
            pass
    relatedartists = []
    try:
        relatedartists = pickle.loads(redis_instance.get('at_relatedartists_%s'%artistobj.id))
    except:
        pass
    if relatedartists.__len__() == 0:
        artistqset = Artist.objects.filter(genre__icontains=artistobj.genre).order_by('priority')
        for artist in artistqset:
            if artistobj.id == artist.id: # Same artist, skip.
                continue
            aliveperiod = "b. " + str(artist.birthyear)
            if str(artist.deathyear) != "":
                aliveperiod = str(artist.birthyear) + " - " + str(artist.deathyear)
            d = {'artistname' : artist.artistname, 'about' : artist.description, 'nationality' : artist.nationality, 'birthyear' : artist.birthyear, 'deathyear' : artist.deathyear, 'squareimage' : artist.artistimage, 'aid' : artist.id, 'aliveperiod' : aliveperiod}
            relatedartists.append(d)
    context['relatedartists'] = relatedartists
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('artist_artworkdetails.html')
    return HttpResponse(template.render(context, request))



def textfilter(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'err' : "Invalid method of call"}))
    searchkey = None
    aid = None
    if request.method == 'POST':
        if 'txtfilter' in request.POST.keys():
            searchkey = str(request.POST['txtfilter']).strip()
        if 'aid' in request.POST.keys():
            aid = str(request.POST['aid']).strip()
    if not searchkey or not aid:
        return HttpResponse(json.dumps({'err' : "Invalid Request: Request is missing search key or artist ID or both"}))
    #print(searchkey)
    context = {}
    pastartworks = []
    artistobj = None
    try:
        artistobj = Artist.objects.get(id=aid)
    except:
        return HttpResponse(json.dumps({'err' : "Could not find artist identified by the ID %s"%aid}))
    artworksbyartistqset = Artwork.objects.filter(artist_id=aid)
    for artwork in artworksbyartistqset:
        lotqset = Lot.objects.filter(artwork_id=artwork.id)
        for lotobj in lotqset:
            try:
                auctionobj = Auction.objects.get(id=lotobj.auction_id)
            except:
                auctionobj = None
            if searchkey.lower() in artwork.artworkname.lower() or searchkey.lower() in artwork.description.lower() or searchkey.lower() in auctionobj.auctionname.lower():
                estimatelow = str(lotobj.lowestimateUSD)
                estimatehigh = str(lotobj.highestimateUSD)
                estimate = estimatelow + " - " + estimatehigh
                if auctionobj is not None:
                    aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                    if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                        aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y") + " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : auctionobj.auctionname, 'aucid' : auctionobj.id, 'aucstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'aucenddate' : auctionobj.auctionenddate.strftime("%d %b, %Y"), 'aucperiod' : aucperiod, 'aid' : aid, 'image' : artwork.image1, 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
                else:
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : '', 'aucid' : '', 'aucstartdate' : '', 'aucenddate' : '', 'aucperiod' : 'NA', 'aid' : aid, 'image' : artwork.image1, 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
                pastartworks.append(d)
    context['pastartworks'] = pastartworks
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    return HttpResponse(json.dumps(context))



def morefilter(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'err' : "Invalid method of call"}))
    searchkey = ""
    aid = None
    medium, size, sizeunit, period, auctionhouse = "", "", "", "", ""
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
        if 'txtfilter' in requestdict.keys():
            searchkey = str(requestdict['txtfilter']).strip()
        if 'aid' in requestdict.keys():
            aid = str(requestdict['aid']).strip()
        if 'medium' in requestdict.keys():
            medium = str(requestdict['medium']).strip()
            medium = endbarPattern.sub("", medium)
        if 'size' in requestdict.keys():
            size = str(requestdict['size']).strip()
            size = endbarPattern.sub("", size)
        if 'sizeunit' in requestdict.keys():
            sizeunit = str(requestdict['sizeunit']).strip()
            sizeunit = endbarPattern.sub("", sizeunit)
        if 'period' in requestdict.keys():
            period = str(requestdict['period']).strip()
            period = endbarPattern.sub("", period)
        if 'auchouse' in requestdict.keys():
            auctionhouse = str(requestdict['auchouse']).strip()
            auctionhouse = endbarPattern.sub("", auctionhouse)
    mediumlist, periodlist, auctionhouselist, sizelist = [], [], [], []
    if not aid:
        return HttpResponse(json.dumps({'err' : "Invalid Request: Request is missing artist ID"}))
    #print(medium)
    mediumlist = medium.split("|")
    periodlist = period.split("|")
    auctionhouselist = auctionhouse.split("|")
    sizelist = size.split("|")
    context = {}
    pastartworks = []
    uniqueartworks = {}
    artistobj = None
    maxsearchresults = 50 # No more than 50 records will be sent back. More than 50 records usually end up crashing the browser.
    try:
        artistobj = Artist.objects.get(id=aid)
    except:
        return HttpResponse(json.dumps({'err' : "Could not find artist identified by the ID %s"%aid}))
    artworksbyartistqset = Artwork.objects.filter(artist_id=aid)
    for artwork in artworksbyartistqset:
        lotqset = Lot.objects.filter(artwork_id=artwork.id)
        for lotobj in lotqset:
            try:
                auctionobj = Auction.objects.get(id=lotobj.auction_id)
            except:
                continue
            if searchkey != "" and (searchkey.lower() in artwork.artworkname.lower() or searchkey.lower() in artwork.description.lower() or searchkey.lower() in auctionobj.auctionname.lower()):
                estimatelow = str(lotobj.lowestimateUSD)
                estimatehigh = str(lotobj.highestimateUSD)
                estimate = estimatelow + " - " + estimatehigh
                if auctionobj is not None:
                    aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                    if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                        aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y") + " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : auctionobj.auctionname, 'aucid' : auctionobj.id, 'aucstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'aucenddate' : auctionobj.auctionenddate.strftime("%d %b, %Y"), 'aucperiod' : aucperiod, 'aid' : aid, 'image' : artwork.image1, 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
                else:
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : '', 'aucid' : '', 'aucstartdate' : '', 'aucenddate' : '', 'aucperiod' : 'NA', 'aid' : aid, 'image' : artwork.image1, 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
                if maxsearchresults < pastartworks.__len__():
                    break
                if artwork.artworkname not in uniqueartworks.keys():
                    pastartworks.append(d)
                    uniqueartworks[artwork.artworkname] = 1
                continue
            if mediumlist.__len__() > 0 or periodlist.__len__() > 0 or auctionhouselist.__len__() > 0 or sizelist.__len__() > 0:
                estimatelow = str(lotobj.lowestimateUSD)
                estimatehigh = str(lotobj.highestimateUSD)
                estimate = estimatelow + " - " + estimatehigh
                if auctionobj is not None:
                    aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                    if auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                        aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y") + " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : auctionobj.auctionname, 'aucid' : auctionobj.id, 'aucstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'aucenddate' : auctionobj.auctionenddate.strftime("%d %b, %Y"), 'aucperiod' : aucperiod, 'aid' : aid, 'image' : artwork.image1, 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
                else:
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : '', 'aucid' : '', 'aucstartdate' : '', 'aucenddate' : '', 'aucperiod' : 'NA', 'aid' : aid, 'image' : artwork.image1, 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
                for medium in mediumlist:
                    if medium in artwork.medium.lower():
                        if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                            pastartworks.append(d)
                            uniqueartworks[artwork.artworkname] = 1
                        break # We have matched at least one of the selected mediums. So this artwork is included in list. Go to next artwork.
                auctionhouseobj = None
                try:
                    auctionhouseobj = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
                    for auctionhousename in auctionhouselist:
                        if auctionhousename == auctionhouseobj.housename.lower():
                            if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                                pastartworks.append(d)
                                uniqueartworks[artwork.artworkname] = 1
                            break # We have matched at least one of the selected auction houses. So this artwork is included in list. Go to next artwork.
                except:
                    pass
                if lotobj.measureunit == sizeunit:
                    for sizespec in sizelist:
                        if sizespec == 'small':
                            if lotobj.height != "" and int(lotobj.height) < 40:
                                if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                                    pastartworks.append(d)
                                    uniqueartworks[artwork.artworkname] = 1 # Size matches. So this artwork is included.
                                break
                        if sizespec == 'medium':
                            if lotobj.height != "" and int(lotobj.height) >= 40 and int(lotobj.height) < 100:
                                if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                                    pastartworks.append(d)
                                    uniqueartworks[artwork.artworkname] = 1 # Size matches. So this artwork is included.
                                break
                        if sizespec == 'large':
                            if lotobj.height != "" and int(lotobj.height) >= 100:
                                if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                                    pastartworks.append(d)
                                    uniqueartworks[artwork.artworkname] = 1 # Size matches. So this artwork is included.
                                break
                artworkcreatedate = str(artwork.creationstartdate)
                numericPattern = re.compile("(\d+)")
                nps = re.search(numericPattern, artworkcreatedate)
                createdatenumber = 0
                if nps:
                    createdatenumber = int(nps.groups()[0])
                for periodspec in periodlist: # Not the perfect way to match, but it will work reasonably well.
                    if periodspec in artworkcreatedate:
                        if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                            pastartworks.append(d)
                            uniqueartworks[artwork.artworkname] = 1 # Period matches directly
                        break
                    elif createdatenumber != 0 and periodspec == "early20" and "19" in artworkcreatedate:
                        if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                            pastartworks.append(d)
                            uniqueartworks[artwork.artworkname] = 1 # Period matches early 19th century
                        break
                    elif createdatenumber != 0 and periodspec == "late19" and "18" in artworkcreatedate:
                        if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                            pastartworks.append(d)
                            uniqueartworks[artwork.artworkname] = 1 # Period matches early 19th century
                        break
                    elif createdatenumber != 0 and periodspec == "mid19" and "18" in artworkcreatedate:
                        if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                            pastartworks.append(d)
                            uniqueartworks[artwork.artworkname] = 1 # Period matches early 19th century
                        break
                    elif createdatenumber != 0 and periodspec == "early19" and "17" in artworkcreatedate:
                        if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                            pastartworks.append(d)
                            uniqueartworks[artwork.artworkname] = 1 # Period matches early 19th century
                        break
                    elif createdatenumber != 0 and periodspec == "18":
                        if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                            pastartworks.append(d)
                            uniqueartworks[artwork.artworkname] = 1 # Period matches early 19th century
                        break
    context['pastartworks'] = pastartworks
    if request.user.is_authenticated:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    return HttpResponse(json.dumps(context))



