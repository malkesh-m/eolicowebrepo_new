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
from django.db.models import Avg, Count, Min, Sum

from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.models import User as djUser
from django.contrib.auth.decorators import login_required

import os, sys, re, time, datetime
import simplejson as json
import redis
import pickle
import MySQLdb
import urllib

#from gallery.models import Gallery, Event
from login.models import User, Session, Favourite #, WebConfig, Carousel, Follow
from login.views import getcarouselinfo_new
#from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from artists.models import Artist, Artwork, FeaturedArtist, LotArtist
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
    pagemap = {'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5, 'f' : 6, 'g' : 7, 'h' : 8, 'i' : 9, 'j' : 10, 'k' : 11, 'l' : 12, 'm' : 13, 'n' : 14, 'o' : 15, 'p' : 16, 'q' : 17, 'r' : 18, 's' : 19, 't' : 20, 'u' : 21, 'v' : 22, 'w' : 23, 'x' : 24, 'y' : 25, 'z' : 26, '-' : -1}
    pageno = "-"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            pageno = str(request.GET['page'])
    try:
        page = pagemap[pageno]
    except:
        page = -1
    chunksize = 4
    rows = 4
    featuredsize = 4
    rowstartctr = int(abs(page)) * rows - rows
    rowendctr = int(abs(page)) * rows
    startctr = (chunksize * rows) * (int(abs(page)) -1) + featuredsize
    endctr = (chunksize * rows) * int(abs(page)) + featuredsize
    maxartworkstoconsider = 100
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    cursor = dbconn.cursor()
    context = {}
    featuredartists = []
    uniqartistsnames = []
    artistsstatisticalinfo = {}
    try:
        featuredartists = pickle.loads(redis_instance.get('at_featuredartists'))
    except:
        featuredartists = []
    uniqartists = {}
    if featuredartists.__len__() == 0:
        """
        try:
            artist_view_sql = "create view featured_artists as select fa.fa_artist_ID as artist_id, fa.fa_artist_name as artist_name, fal.fal_lot_sale_price_USD as artist_price_usd, fa.fa_artist_name_prefix as prefix, fa.fa_artist_nationality as nationality, fa.fa_artist_birth_year as birthyear, fa.fa_artist_death_year as deathyear, fa.fa_artist_description as description, fa.fa_artist_aka as aka, fa.fa_artist_bio as bio, fa.fa_artist_image as artistimage, fa.fa_artist_genre as genre from fineart_artists fa, fineart_artworks faa, fineart_lots fal where fa.fa_artist_ID=faa.faa_artist_ID and faa.faa_artwork_ID=fal.fal_artwork_ID"
            cursor.execute(artist_view_sql)
            dbconn.commit()
        except:
            pass # We are here because the view exists. Do nothing.
        whereclause = ""
        if page != 1:
            whereclause = "and artist_name like '" + str(pageno) + "%'"
        getview_sql = "select artist_id, artist_name, sum(artist_price_usd) as price, prefix, nationality, birthyear, deathyear, description, aka, bio, artistimage, genre from featured_artists where artistimage is not NULL and artistimage != '' %s group by artist_id order by price desc"%whereclause
        #print(getview_sql)
        cursor.execute(getview_sql)
        artistsqset = cursor.fetchall()
        """
        date1yearago = datetime.datetime.now() - datetime.timedelta(days=settings.YEARS_FOR_FEATURED_ARTIST*365)
        featuredartistsql = "SELECT A.artist_id, A.artist_name, A.prefix, A.nationality, A.birthyear, A.deathyear, A.description, A.aka, A.bio, A.artistimage, A.genre, A.totalsoldprice, A.id, A.saledate FROM fa_featured_artists A where A.saledate > '%s' ORDER BY A.totalsoldprice DESC LIMIT %s OFFSET %s"%(date1yearago, endctr, startctr)
        #print(featuredartistsql)
        cursor.execute(featuredartistsql)
        artistsqset = cursor.fetchall()
        #artistsqset = FeaturedArtist.objects.all().order_by('-totalsoldprice')[0:endctr]
        if page != -1:
            artistnamestartswithsql = "SELECT A.artist_id, A.artist_name, A.prefix, A.nationality, A.birthyear, A.deathyear, A.description, A.aka, A.bio, A.artistimage, A.genre, A.totalsoldprice, A.id FROM fa_featured_artists A WHERE A.artist_name LIKE '" + str(pageno) + "%' or A.artist_name LIKE '" + str(pageno).upper() + "%' order by A.saledate desc" # TODO: Add condition based on saledate (in the past 12 months only)
            cursor.execute(artistnamestartswithsql)
            artistsqset = cursor.fetchall()
            #artistsqset = FeaturedArtist.objects.filter(artist_name__istartswith=str(pageno)).order_by('-totalsoldprice')[0:endctr]
        for artist in artistsqset:
            artistid = artist[0]
            if artistid in settings.BLACKLISTED_ARTISTS:
                continue
            artistname = artist[1]
            if artistname == "Missing":
                continue
            price = artist[11]
            if price is None:
                price = 0.00
            prefix = artist[2]
            nationality = artist[3]
            birthyear = artist[4]
            deathyear = artist[5]
            description = artist[6]
            aka = artist[7]
            bio = artist[8]
            artistimage = settings.IMG_URL_PREFIX + str(artist[9])
            if artist[9] is None or artist[9] == "":
                artistimage = "/static/images/default_artist.jpg"
            genre = artist[10]
            if artistname not in uniqartists.keys():
                uniqartists[artistname] = [artistid, artistname, float(price), prefix, nationality, birthyear, deathyear, description, aka, bio, artistimage, genre]
            else:
                l = uniqartists[artistname]
                uniqartists[artistname] = l
        uniqartistsnames = list(uniqartists.keys())
        for artistname in uniqartistsnames[0:featuredsize]:
            artist = uniqartists[artistname]
            artistid = artist[0]
            artistname = artist[1]
            price = "{:,}".format(artist[2])
            if not price or price is None:
                price = 0.00
            prefix = artist[3]
            nationality = artist[4]
            birthyear = artist[5]
            deathyear = artist[6]
            birthdeath = ""
            if birthyear != "":
                birthdeath = "b. " + str(birthyear)
            if deathyear != "":
                birthdeath = str(birthyear) + " - " + str(deathyear)
            description = artist[7]
            aka = artist[8]
            bio = artist[9]
            artistimage = str(artist[10])
            genre = artist[11]
            if nationality == "na":
                nationality = ""
            if birthyear == 0:
                birthyear = ""
            if prefix != "" and prefix != "na":
                prefix = prefix + " "
            # Check for follows and favourites
            if request.user.is_authenticated:
                #folqset = Follow.objects.filter(user=request.user, artist__id=artistid)
                favqset = Favourite.objects.filter(user=request.user, reference_model="fineart_artists", reference_model_id=artistid)
                folqset = favqset
            else:
                folqset = []
                favqset = []
            folflag = 0
            if folqset.__len__() > 0:
                folflag = 1
            favflag = 0
            if favqset.__len__() > 0:
                favflag = 1
            bdstring = str(birthyear)
            if deathyear is not None:
                bdstring = bdstring + " - " + str(deathyear)
            else:
                bdstring = "Born " + bdstring
            d = {'artistname' : artistname, 'nationality' : nationality, 'birthdate' : str(birthyear), 'deathdate' : str(deathyear), 'about' : description, 'profileurl' : '', 'artistimage' : artistimage, 'aid' : str(artistid), 'totalsold' : str(price), 'birthdeath' : birthdeath, 'follow' : folflag, 'favourite' : favflag, 'bdstring' : bdstring}
            artworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_start_year, faa_artwork_image1 from fineart_artworks where faa_artist_ID=%s limit %s"%(artistid, maxartworkstoconsider)
            #print(artworksql)
            cursor.execute(artworksql)
            artworkqset = cursor.fetchall()
            if artworkqset.__len__() == 0:
                d['artworkname'] = ""
                d['artworkimage'] = ""
                d['artworkdate'] = ""
                d['awid'] = ""
                d['atype'] = "0" # Artists with no related artwork
            else:
                d['artworkname'] = artworkqset[0][1]
                d['artworkimage'] = settings.IMG_URL_PREFIX + str(artworkqset[0][3])
                d['artworkdate'] = artworkqset[0][2]
                d['awid'] = artworkqset[0][0]
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
    #print("HERE...")
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
                birthdeath = ""
                if birthyear != "":
                    birthdeath = "b. " + str(birthyear)
                if deathyear != "":
                    birthdeath = str(birthyear) + " - " + str(deathyear)
                description = artist[7]
                aka = artist[8]
                bio = artist[9]
                artistimage = str(artist[10])
                genre = artist[11]
                if nationality == "na":
                    nationality = ""
                if birthyear == 0:
                    birthyear = ""
                if prefix != "" and prefix != "na":
                    prefix = prefix + " "
                # Check for follows and favourites
                if request.user.is_authenticated:
                    #folqset = Follow.objects.filter(user=request.user, artist__id=artistid)
                    favqset = Favourite.objects.filter(user=request.user, reference_model="fineart_artists", reference_model_id=artistid)
                    folqset = favqset
                else:
                    folqset = []
                    favqset = []
                folflag = 0
                if folqset.__len__() > 0:
                    folflag = 1
                favflag = 0
                if favqset.__len__() > 0:
                    favflag = 1
                bdstring = str(birthyear)
                if deathyear is not None:
                    bdstring = bdstring + " - " + str(deathyear)
                else:
                    bdstring = "Born " + bdstring
                d = {'artistname' : artistname, 'nationality' : nationality, 'birthdate' : str(birthyear), 'deathdate' : str(deathyear), 'about' : description, 'profileurl' : '', 'artistimage' : artistimage, 'aid' : str(artistid), 'birthdeath' : birthdeath, 'follow' : folflag, 'favourite' : favflag, 'bdstring' : bdstring}
                artworksql1 = "select faa_artwork_ID, faa_artwork_title, faa_artwork_start_year, faa_artwork_image1, faa_artwork_material from fineart_artworks where faa_artist_ID=%s limit %s"%(artistid, maxartworkstoconsider)
                #print(artworksql1)
                cursor.execute(artworksql1)
                artworkqset1 = cursor.fetchall()
                try: # Getting a stupid "Protocol error, expecting EOF" for artistid 90761...
                    if artworkqset1.__len__() == 0:
                        continue
                except:
                    continue
                artworkobj = artworkqset1[0]
                if artworkobj[1].title() not in uniqueartworks.keys():
                    d['artworkname'] = artworkobj[1].title()
                    d['artworkimage'] = settings.IMG_URL_PREFIX + str(artworkobj[3])
                    d['artworkdate'] = artworkobj[2]
                    d['awid'] = artworkobj[0]
                    d['artworkmedium'] = artworkobj[4]
                    uniqueartworks[artworkobj[1].title()] = 1
                else:
                    awctr = 0
                    awfound = 0
                    while awctr < artworkqset1.__len__() - 1: # Iterate over all artworks by the artist under consideration
                        awctr += 1
                        artworkobj2 = artworkqset1[awctr] # Starting from index 1
                        if artworkobj2[1].title() not in uniqueartworks.keys(): # Set flag if we have a new artwork
                            if artworkobj2[3] == "":
                                continue
                            d['artworkimage'] = settings.IMG_URL_PREFIX + str(artworkobj2[3])
                            d['artworkdate'] = artworkobj2[2]
                            d['awid'] = artworkobj2[0]
                            d['artworkmedium'] = artworkobj2[4]
                            d['artworkname'] = artworkobj2[1].title()
                            #print(artworkobj2[1].title())
                            uniqueartworks[artworkobj2[1].title()] = 1
                            awfound = 1
                            break
                    if awfound == 0: # Skip this artist if no new artworks could be found.
                        continue
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
    context['statisticalinfo'] = artistsstatisticalinfo
    filterartists = []
    try:
        filterartists = pickle.loads(redis_instance.get('at_filterartists'))
    except:
        pass
    if filterartists.__len__() == 0:
        allartistsqset = FeaturedArtist.objects.all()[0:20000]
        for artist in allartistsqset:
            if artist.nationality != "" and artist.nationality is not None:
                nationality = artist.nationality
            else:
                nationality = ""
            if artist.birthyear != "" and artist.birthyear is not None and artist.birthyear != 0:
                birthyear = str(artist.birthyear)
            else:
                birthyear = ""
            if artist.deathyear != "" and artist.deathyear is not None and artist.deathyear != 0:
                deathyear = str(artist.deathyear)
            else:
                deathyear = ""
            artistinfo = ""
            if nationality != "":
                artistinfo = artist.artist_name + " (" + nationality + ", "
            else:
                artistinfo = artist.artist_name + " ("
            if birthyear != "":
                artistinfo = artistinfo + birthyear + " - "
            else:
                pass
            if deathyear != "":
                artistinfo = artistinfo + deathyear + ")"
            else:
                artistinfo = artistinfo + ")"
            filterartists.append(artistinfo)
        try:
            redis_instance.set('at_filterartists', pickle.dumps(filterartists))
        except:
            pass
    context['filterartists'] = filterartists
    carouselentries = getcarouselinfo_new()
    context['carousel'] = carouselentries
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    cursor.close()
    dbconn.close() # Closing db connection. Don't want unwanted open connections.
    template = loader.get_template('artist.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    aid = None
    page = 1
    if request.method == 'GET':
        if 'aid' in request.GET.keys():
            aid = str(request.GET['aid'])
    if not aid:
        return HttpResponse("Invalid Request: Request is missing aid")
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = request.GET['page']
    chunksize = 9
    maxrelatedartist = 8
    artistobj = None
    context = {}
    dbconn = MySQLdb.connect(user="websiteadmin",passwd="AVNS_UHIULiqroqLJ4x2ivN_",host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    cursor = dbconn.cursor()
    try:
        artistsql = "SELECT fa_artist_name, fa_artist_ID, fa_artist_name_prefix, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_description, fa_artist_aka, fa_artist_bio, fa_artist_genre, fa_artist_image, fa_artist_record_created from fineart_artists Where fa_artist_ID=%s"%aid
        cursor.execute(artistsql)
        artistobj = list(cursor.fetchone())
        #print("1. %s"%artistsql)
    except:
        context['error'] = "Artist with the given identifier (%s) doesn't exist"%aid
        template = loader.get_template('artist_details.html')
        return HttpResponse(template.render(context, request))
    context['aid'] = aid
    artistname = artistobj[0]
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
    totaldelta = 0.00
    maxpastlots = 25
    maxupcominglots = 8
    maxartworkstoconsider = 100
    artworkstartctr = int(page) * maxartworkstoconsider - maxartworkstoconsider
    artworkendctr = int(page) * maxartworkstoconsider
    try:
        allartworks = pickle.loads(redis_instance.get('at_allartworks_%s'%artistobj[1]))
        allartworks1 = pickle.loads(redis_instance.get('at_allartworks1_%s'%artistobj[1]))
        allartworks2 = pickle.loads(redis_instance.get('at_allartworks2_%s'%artistobj[1]))
        allartworks3 = pickle.loads(redis_instance.get('at_allartworks3_%s'%artistobj[1]))
        allartworks4 = pickle.loads(redis_instance.get('at_allartworks4_%s'%artistobj[1]))
        lotsinupcomingauctions = pickle.loads(redis_instance.get('at_lotsinupcomingauctions_%s'%artistobj[1]))
        lotsinpastauctions = pickle.loads(redis_instance.get('at_lotsinpastauctions_%s'%artistobj[1]))
        yearlylotssold = redis_instance.get('at_yearlylotssold_%s'%artistobj[1])
        sellthrurate = redis_instance.get('at_sellthrurate_%s'%artistobj[1])
        avgsaleprice = redis_instance.get('at_avgsaleprice_%s'%artistobj[1])
        salepriceoverestimate = redis_instance.get('at_salepriceoverestimate_%s'%artistobj[1])
        totallotssold = redis_instance.get('at_totallotssold_%s'%artistobj[1])
    except:
        pass
    uniqueartworks = {}
    actr = 0
    lotqset = list()
    if allartworks.__len__() == 0:
        # The following limited queryset would make the stats slightly inaccurate for some artists (who have more than 500 artworks).
        # Unfortunately, we can't do an exhaustive retrieval since that would not be possible because of time constraints.
        """
        The following sql should be used after adding the column 'last_edited' in 'fa_artwork_lot_artist' table.
        """
        #lotartistsql = "SELECT artist_id, artist_name, artist_price_usd, prefix, nationality, birthyear, deathyear, description, aka, bio, artistimage, genre, saledate, auctionid, lotstatus, medium, sizedetails, lotcategory, lotnum, artworkid, artworkname, highestimate, lowestimate, lotimage1, id FROM fa_artwork_lot_artist Where artist_id=%s order by last_edited desc limit %s offset %s"%(aid, maxartworkstoconsider, artworkstartctr)
        lotartistsql = "SELECT artist_id, artist_name, artist_price_usd, prefix, nationality, birthyear, deathyear, description, aka, bio, artistimage, genre, saledate, auctionid, lotstatus, medium, sizedetails, lotcategory, lotnum, artworkid, artworkname, highestimate, lowestimate, lotimage1, id FROM fa_artwork_lot_artist Where artist_id=%s limit %s offset %s"%(aid, maxartworkstoconsider, artworkstartctr)
        #print("2. %s"%lotartistsql)
        cursor.execute(lotartistsql)
        lotartistqset = cursor.fetchall()
        date2yearsago = datetime.datetime.now() - datetime.timedelta(days=settings.YEARS_FOR_STATS*365)
        totaldelta = 0.00
        curdatetime = datetime.datetime.now()
        upcomingflag = 0
        pastauctionsflag = 0
        artworkidslist = []
        artworkauctionidslist = []
        for lotartist in lotartistqset:
            artworkidslist.append(str(lotartist[19]))
            artworkauctionidslist.append(lotartist[13])
        artworkidsstr = "(" + ",".join(artworkidslist) + ")"
        artworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_requires_review, faa_artwork_start_year, faa_artwork_end_year, faa_artwork_start_year_identifier, faa_artwork_end_year_identifier, faa_artist_ID, faa_artwork_size_details, faa_artwork_material, faa_artwork_edition, faa_artwork_category, faa_artwork_markings, faa_artwork_description, faa_artwork_literature, faa_artwork_exhibition, faa_artwork_image1, faa_artwork_record_created from fineart_artworks where faa_artwork_ID in %s"%artworkidsstr
        #print(artworksql)
        try:
            cursor.execute(artworksql)
            artworksqset = cursor.fetchall()
        except:
            artworksqset = []
        artworkartistdict = {}
        artworkauctiondict = {}
        for artworkrow in artworksqset:
            artworkid = artworkrow[0]
            artworkartistdict[str(artworkid)] = [artworkrow[0], artworkrow[1], artworkrow[2], artworkrow[3], artworkrow[4], artworkrow[5], artworkrow[6], artworkrow[7], artworkrow[8], artworkrow[9], artworkrow[10], artworkrow[11], artworkrow[12], artworkrow[13], artworkrow[14], artworkrow[15], artworkrow[16], artworkrow[17]]
        auctionsqset = Auction.objects.filter(id__in=artworkauctionidslist)
        for auc in auctionsqset:
            aucidstr = str(auc.id)
            artworkauctiondict[aucidstr] = auc
        auchousedict = {}
        uniqueauchouseidlist = []
        for lotartist in lotartistqset:
            try:
                auctionobj = artworkauctiondict[str(lotartist[13])]
            except:
                continue
            auctionhouseid = auctionobj.auctionhouse_id
            if str(auctionhouseid) not in auchousedict.keys():
                uniqueauchouseidlist.append(str(auctionhouseid))
                auchousedict[str(auctionhouseid)] = ""
        auchouseidstr = "(" + ",".join(uniqueauchouseidlist) + ")"
        if uniqueauchouseidlist.__len__() > 0:
            ahsql = "select cah_auction_house_name, cah_auction_house_ID from core_auction_houses where cah_auction_house_ID in %s"%auchouseidstr
            cursor.execute(ahsql)
            auchouseqset = cursor.fetchall()
        else:
            auchouseqset = []
        for auchouserecord in auchouseqset:
            auctionhouseid = auchouserecord[1]
            auchousename = auchouserecord[0]
            auchousedict[str(auctionhouseid)] = auchousename
        for lotartist in lotartistqset:
            if upcomingflag == 1 and pastauctionsflag == 1:
                break
            #for lotobj in lotqset:
            saledate = datetime.datetime.combine(lotartist[12], datetime.time(0, 0))
            if saledate and saledate > date2yearsago:
                totallotssold += 1
                if lotartist[2] is not None:
                    soldlotsprice += float(lotartist[2])
                else:
                    soldlotsprice += 0.00
                if lotartist[21] is not None and lotartist[22] is not None:
                    midestimate = (float(lotartist[21]) + float(lotartist[22]))/2.0
                elif lotartist[21] is not None and lotartist[22] is None:
                    midestimate = (float(lotartist[21]) + 0.00)/2.0
                elif lotartist[21] is None and lotartist[22] is not None:
                    midestimate = (0.00 + float(lotartist[22]))/2.0
                else:
                    midestimate = 0.00
                if lotartist[2] is not None and lotartist[2] > 0.00:
                    delta = (float(lotartist[2]) - float(midestimate))/float(lotartist[2])
                    totaldelta += delta
                totalartworks += 1
            elif saledate and saledate < date2yearsago:
                pass # If saledate is prior to date2yearsago, skip it.
            elif not saledate:
                totalartworks += 1
            auctionobj = None
            try:
                auctionobj = artworkauctiondict[str(lotartist[13])]
            except:
                continue # If we fail to find the auction, there is no use going ahead.
            auctionstartdate = auctionobj.auctionstartdate
            auctionname = auctionobj.auctionname
            curdate = datetime.date(curdatetime.year, curdatetime.month, curdatetime.day)
            if auctionstartdate > curdate: # This is an upcoming auction
                try:
                    auchousename = auchousedict[str(auctionobj.auctionhouse_id)]
                except:
                    auchousename = ""
                auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                aucenddate = auctionobj.auctionenddate
                if str(aucenddate) != "0000-00-00" and str(aucenddate) != "":
                    auctionperiod += " - " + str(aucenddate)
                try:
                    artwork = artworkartistdict[str(lotartist[19])]
                    d = {'artworkname' : lotartist[20], 'creationdate' : artwork[3], 'size' : lotartist[16], 'medium' : lotartist[15], 'description' : artwork[13], 'image' : settings.IMG_URL_PREFIX + str(lotartist[23]), 'provenance' : '', 'literature' : artwork[14], 'exhibitions' : artwork[15], 'href' : '', 'estimate' : '', 'awid' : artwork[0], 'aid' : aid, 'auctionname' : auctionname, 'aucid' : auctionobj.id, 'auctionimage' : settings.IMG_URL_PREFIX + str(auctionobj.coverimage), 'auctionstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'auctionenddate' : str(aucenddate), 'auchousename' : auchousename, 'estimate' : str(lotartist[22]) + " - " + str(lotartist[21]), 'auctionperiod' : auctionperiod}
                except:
                    print("Could not find artwork identified by Id %s"%str(lotartist[19]))
                    continue
                if maxupcominglots > lotsinupcomingauctions.__len__():
                    lotsinupcomingauctions.append(d)
                else:
                    upcomingflag = 1
            else: # Past auction case
                auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                aucenddate = auctionobj.auctionenddate
                if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                    auctionperiod += " - " + str(aucenddate)
                try:
                    auchousename = auchousedict[str(auctionobj.auctionhouse_id)]
                except:
                    auchousename = ""
                try:
                    artwork = artworkartistdict[str(lotartist[19])]
                    d = {'artworkname' : lotartist[20], 'creationdate' : artwork[3], 'size' : lotartist[16], 'medium' : lotartist[15], 'description' : artwork[13], 'image' : settings.IMG_URL_PREFIX + str(lotartist[23]), 'provenance' : '', 'literature' : artwork[14], 'exhibitions' : artwork[15], 'href' : '', 'estimate' : '', 'awid' : artwork[0], 'aid' : aid, 'auctionname' : auctionname, 'aucid' : auctionobj.id, 'auctionimage' : settings.IMG_URL_PREFIX + str(auctionobj.coverimage), 'auctionstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'auctionenddate' : auctionobj.auctionenddate, 'auchousename' : auchousename, 'soldprice' : str(lotartist[2]), 'estimate' : str(lotartist[22]) + " - " + str(lotartist[21]), 'auctionperiod' : auctionperiod}
                except:
                    print("Could not find artwork identified by Id %s"%str(lotartist[19]))
                    continue
                if maxpastlots > lotsinpastauctions.__len__():
                    lotsinpastauctions.append(d)
                else:
                    pastauctionsflag = 1
                    continue
            #break # Expecting one artwork should correspond to one lot obj. Is this assumption correct? If not, this could be  the most expensive call.
            artwork = None
            try:
                artwork = artworkartistdict[str(lotartist[19])]
                d = {'artworkname' : lotartist[20], 'creationdate' : artwork[3], 'size' : lotartist[16], 'medium' : lotartist[15], 'description' : artwork[13], 'image' : settings.IMG_URL_PREFIX + str(lotartist[23]), 'provenance' : '', 'literature' : artwork[14], 'exhibitions' : artwork[15], 'href' : '', 'estimate' : '', 'awid' : artwork[0], 'aid' : aid}
                if artwork[1] not in uniqueartworks.keys():
                    allartworks.append(d)
                    uniqueartworks[artwork[1]] = artwork[0]
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
            except:
                print("Error in artist/details/: %s"%sys.exc_info()[1].__str__())
    yearlylotssold = int(float(totallotssold)/2.0)
    sellthrurate = "NA"
    if totalartworks != 0:
        sellthrurate = (float(totallotssold)/float(totalartworks)) * 100.00
        sellthrurate = '{:.2f}'.format(sellthrurate)
    avgsaleprice = "NA"
    if totallotssold != 0:
        avgsaleprice = float(soldlotsprice)/float(totallotssold)
        avgsaleprice = '{:.2f}'.format(avgsaleprice)
    salepriceoverestimate = "NA"
    if totallotssold != 0:
        salepriceoverestimate = (float(totaldelta)/float(totallotssold)) * 100.00
        salepriceoverestimate = '{:.2f}'.format(salepriceoverestimate)
    try:
        redis_instance.set('at_allartworks_%s'%artistobj[1], pickle.dumps(allartworks))
        redis_instance.set('at_allartworks1_%s'%artistobj[1], pickle.dumps(allartworks1))
        redis_instance.set('at_allartworks2_%s'%artistobj[1], pickle.dumps(allartworks2))
        redis_instance.set('at_allartworks3_%s'%artistobj[1], pickle.dumps(allartworks3))
        redis_instance.set('at_allartworks4_%s'%artistobj[1], pickle.dumps(allartworks4))
        redis_instance.set('at_lotsinupcomingauctions_%s'%artistobj[1], pickle.dumps(lotsinupcomingauctions))
        redis_instance.set('at_lotsinpastauctions_%s'%artistobj[1], pickle.dumps(lotsinpastauctions))
        redis_instance.set('at_yearlylotssold_%s'%artistobj[1], yearlylotssold)
        redis_instance.set('at_sellthrurate_%s'%artistobj[1], sellthrurate)
        redis_instance.set('at_avgsaleprice_%s'%artistobj[1], avgsaleprice)
        redis_instance.set('at_totallotssold_%s'%artistobj[1], totallotssold)
        redis_instance.set('at_salepriceoverestimate_%s'%artistobj[1], salepriceoverestimate)
    except:
        pass
    context['yearlylotssold'] = yearlylotssold
    context['sellthrurate'] = sellthrurate
    context['avgsaleprice'] = avgsaleprice
    context['salepriceoverestimate'] = salepriceoverestimate
    prefix = ""
    if artistobj[2] != "" and artistobj[2] != "na":
        prefix = artistobj[2] + " "
    shortlen = 100
    if artistobj[8] is None:
        artistobj[8] = ""
    if artistobj[8].__len__() < shortlen:
        shortlen = artistobj[8].__len__()
    shortabout = artistobj[8][:shortlen] + "..."
    aimg = settings.IMG_URL_PREFIX + str(artistobj[10])
    if artistobj[10] is None or artistobj[10] == "":
        aimg = "/static/images/default_artist.jpg"
    artistinfo = {'name' : prefix + artistobj[0], 'nationality' : artistobj[3], 'birthdate' : artistobj[4], 'deathdate' : artistobj[5], 'profileurl' : '', 'desctiption' : artistobj[6], 'image' : aimg, 'gender' : '', 'about' : artistobj[8], 'artistid' : artistobj[1], 'shortabout' : shortabout}
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
        relatedartists = pickle.loads(redis_instance.get('at_relatedartists_%s'%artistobj[1]))
        artistevents = pickle.loads(redis_instance.get('at_artistevents_%s'%artistobj[1]))
    except:
        pass
    print("HERE..........")
    if relatedartists.__len__() == 0:
        try:
            if artistobj[9] is not None:
                a_genre = artistobj[9]
                genreparts = a_genre.split(",")
                # Related Artists can be sought out based on the 'genre' or on 'nationality'. Though 'genre' is a better
                # way to seek out "Related" artists, we may use 'nationality' for faster processing. Unfortunately, this
                # is a query that cannot be cached, so it has to be picked up from the DB every time.
                relatedartistqset = []
                for g in genreparts:
                    rartistqset = FeaturedArtist.objects.filter(genre__icontains=g)
                    for artistob in rartistqset:
                        relatedartistqset.append(artistob)
            else:
                relatedartistqset = FeaturedArtist.objects.filter(nationality=artistobj[3])
        except:
            genre = None
            relatedartistqset = FeaturedArtist.objects.filter(nationality=artistobj[3])
        artistidslist = []
        artistidsstr = ""
        for artist in relatedartistqset[:maxrelatedartist]:
            if artistobj[1] == artist.artist_id: # Same artist, so just skip.
                continue
            artistidslist.append(str(artist.artist_id))
        artistidsstr = "(" + ",".join(artistidslist) + ")"
        artworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_start_year, faa_artwork_image1, faa_artwork_description, faa_artist_ID from fineart_artworks where faa_artist_ID in %s"%artistidsstr
        cursor.execute(artworksql)
        artworkqset2 = cursor.fetchall()
        artistartworkdict = {}
        for aw in artworkqset2:
            artid = aw[5]
            if str(artid) not in artistartworkdict.keys():
                artistartworkdict[str(artid)] = [[aw[0], aw[1], aw[2], aw[3], aw[4]],]
        for artist in relatedartistqset[:maxrelatedartist]:
            if artistobj[1] == artist.artist_id: # Same artist, so just skip.
                continue
            #print(artist.id)
            prefix = ""
            if artist.prefix != "" and artist.prefix != "na":
                prefix = artist.prefix + " "
            aliveperiod = "b. " + str(artist.birthyear)
            if str(artist.deathyear) != "":
                aliveperiod = str(artist.birthyear) + " - " + str(artist.deathyear)
            d = {'artistname' : artist.artist_name, 'nationality' : artist.nationality, 'birthdate' : str(artist.birthyear), 'deathdate' : str(artist.deathyear), 'about' : artist.bio, 'desctiption' : artistobj[6], 'profileurl' : '', 'image' : settings.IMG_URL_PREFIX + str(artist.artistimage), 'aid' : str(artist.artist_id), 'aliveperiod' : aliveperiod}
            artworkqset2 = artistartworkdict[str(artist.artist_id)]
            if artworkqset2.__len__() == 0:
                continue
            d['artworkname'] = artworkqset2[0][1]
            d['artworkimage'] = settings.IMG_URL_PREFIX + str(artworkqset2[0][3])
            d['artworkdate'] = artworkqset2[0][2]
            d['artworkdescription'] = artworkqset2[0][4]
            d['awid'] = artworkqset2[0][0]
            if relatedartists.__len__() < chunksize:
                relatedartists.append(d)
            else:
                break
        #for lotartist in lotartistqset[maxartworkstoconsider:maxartworkstoconsider+maxartworkstoconsider]:
        for lotartist in lotartistqset:
            auctionid = lotartist[13]
            auctionsqset = [artworkauctiondict[str(auctionid)],]
            eventname = auctionsqset[0].auctionname
            eventurl = auctionsqset[0].auctionurl
            eventinfo = ''
            eventperiod = auctionsqset[0].auctionstartdate.strftime("%d %b, %Y")
            if type(auctionsqset[0].auctionenddate) != str and auctionsqset[0].auctionenddate.strftime("%d %b, %Y") != '01 Jan, 0001' and auctionsqset[0].auctionenddate.strftime("%d %b, %Y") != '01 Jan, 1':
                eventperiod = eventperiod + " - " + auctionsqset[0].auctionenddate.strftime("%d %b, %Y")
            eventimage = settings.IMG_URL_PREFIX + str(auctionsqset[0].coverimage)
            eventlocation = ''
            aucid = auctionsqset[0].id
            l = artistevents.keys()
            if l.__len__() < chunksize and eventname not in l:
                artistevents[eventname] = {'eventurl' : eventurl, 'eventinfo' : eventinfo, 'eventperiod' : eventperiod, 'eventimage' : eventimage, 'eventlocation' : eventlocation, 'aucid' : aucid}
        try:
            redis_instance.set('at_relatedartists_%s'%artistobj[1], pickle.dumps(relatedartists))
            redis_instance.set('at_artistevents_%s'%artistobj[1], pickle.dumps(artistevents))
        except:
            pass
    context['relatedartists'] = relatedartists
    context['artistevents'] = artistevents
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
    cursor.close()
    dbconn.close()
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
    #print(searchkey + " -------------------------------------")
    pageno = 1
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            pageno = str(request.GET['page'])
    page = int(pageno)
    chunksize = 4
    rows = 6
    featuredsize = 120
    rowstartctr = int(page) * rows - rows
    rowendctr = int(page) * rows
    startctr = (chunksize * rows) * (int(page) -1)
    endctr = (chunksize * rows) * int(page)
    context = {}
    featuredartists = []
    uniqartists = {}
    searchedname = searchkey.split("(")[0]
    searchedname = searchedname.strip()
    try:
        featuredartists = pickle.loads(redis_instance.get('at_featuredartists_%s'%searchedname.lower()))
    except:
        featuredartists = []
    uniqartists = {}
    if featuredartists.__len__() == 0:
        matchingartistsqset = Artist.objects.filter(artistname__icontains=searchedname) #.order_by('priority')
        artistidslist = []
        #print("Matching Artist Qset: %s"%matchingartistsqset.__len__())
        #print("Start Counter: %s"%startctr)
        #print("End Counter: %s"%endctr)
        for artist in matchingartistsqset[startctr:endctr]:
            artistidslist.append(artist.id)
        artistartworksdict = {}
        artworksqset = Artwork.objects.filter(artist_id__in=artistidslist)
        for artwork in artworksqset:
            artistid = str(artwork.artist_id)
            if artistid in artistartworksdict.keys():
                artworkslist = artistartworksdict[artistid]
            else:
                artworkslist = []
            artworkslist.append(artwork)
            artistartworksdict[artistid] = artworkslist
        for artist in matchingartistsqset[startctr:endctr]:
            if artist.artistname.title() not in uniqartists.keys():
                if artist.nationality == "na":
                    artist.nationality = ""
                if artist.birthyear == 0:
                    artist.birthyear = ""
                prefix = ""
                if artist.prefix != "" and artist.prefix != "na":
                    prefix = artist.prefix + " "
                bdstring = str(artist.birthyear)
                if artist.deathyear is not None:
                    bdstring = bdstring + " - " + str(artist.deathyear)
                else:
                    bdstring = "Born " + bdstring
                if artist.artistimage is None or artist.artistimage == "":
                    artist.artistimage = "/static/images/default_artist.jpg"
                else:
                    artist.artistimage = settings.IMG_URL_PREFIX + artist.artistimage
                d = {'artistname' : artist.artistname.title(), 'nationality' : artist.nationality, 'birthdate' : str(artist.birthyear), 'deathdate' : str(artist.deathyear), 'about' : artist.description, 'profileurl' : '', 'artistimage' : str(artist.artistimage), 'aid' : str(artist.id), 'bdstring' : bdstring}
                try:
                    artworkqset = artistartworksdict[str(artist.id)]
                except:
                    artworkqset = []
                if artworkqset.__len__() == 0:
                    #continue
                    d['artworkname'] = ""
                    d['artworkimage'] = ""
                    d['artworkdate'] = ""
                    d['awid'] = ""
                    d['atype'] = "0" # Artists with no related artwork
                else:
                    d['artworkname'] = artworkqset[0].artworkname
                    d['artworkimage'] = settings.IMG_URL_PREFIX + str(artworkqset[0].image1)
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
            if artist.nationality != "" and artist.nationality is not None:
                nationality = artist.nationality
            else:
                nationality = ""
            if artist.birthyear != "" and artist.birthyear is not None and artist.birthyear != 0:
                birthyear = str(artist.birthyear)
            else:
                birthyear = ""
            if artist.deathyear != "" and artist.deathyear is not None and artist.deathyear != 0:
                deathyear = str(artist.deathyear)
            else:
                deathyear = ""
            artistinfo = ""
            if nationality != "":
                artistinfo = artist.artistname + "(" + nationality
            else:
                artistinfo = artist.artistname + "("
            if birthyear != "":
                artistinfo = artistinfo + ", " + birthyear
            else:
                pass
            if deathyear != "":
                artistinfo = artistinfo + " - " + deathyear + ")"
            else:
                artistinfo = artistinfo + ")"
            filterartists.append(artistinfo)
        try:
            redis_instance.set('at_filterartists', pickle.dumps(filterartists))
        except:
            pass
    context['filterartists'] = filterartists
    #carouselentries = getcarouselinfo()
    #context['carousel'] = carouselentries
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
    maxartworkstoshow = 24 # Keep this as multiples of 4.
    maxrelatedartist = 24
    description = artworkobj.description
    description = description.replace("<strong><br>Description:</strong>", "")
    description = description.replace("<br>", "")
    shortlen = 30
    if description.__len__() < 30:
        shortlen = description.__len__()
    shortdescription = description[:shortlen] + "..."
    context['artworkinfo'] = {'artworkname' : artworkobj.artworkname, 'artistname' : artistname, 'creationdate' : artworkobj.creationstartdate, 'size' : artworkobj.sizedetails, 'medium' : artworkobj.medium, 'description' : description, 'awid' : artworkobj.id, 'aid' : artistobj.id, 'shortdescription' : shortdescription, 'artworkimage' : settings.IMG_URL_PREFIX + str(artworkobj.image1)}
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
        artworkidslist = []
        auctionidslist = []
        for artwork in artworksqset:
            artworkidslist.append(artwork.id)
        lotqset = Lot.objects.filter(artwork_id__in=artworkidslist)
        lotartworkdict = {}
        auctionartworkdict = {}
        for lot in lotqset:
            artworkid = str(lot.artwork_id)
            if artworkid in lotartworkdict.keys():
                lotslist = lotartworkdict[artworkid]
            else:
                lotslist = []
            lotslist.append(lot)
            lotartworkdict[artworkid] = lotslist
            auctionidslist.append(lot.auction_id)
        auctionsqset = Auction.objects.filter(id__in=auctionidslist)
        for auc in auctionsqset:
            aucidstr = str(auc.id)
            auctionartworkdict[aucidstr] = auc
        for artwork in artworksqset:
            creationdate = str(artwork.creationstartdate)
            if creationdate == "0":
                creationdate = ""
            # Check for favourites
            if request.user.is_authenticated:
                favqset = Favourite.objects.filter(user=request.user, reference_model="fineart_artworks", reference_model_id=artwork.id)
            else:
                favqset = []
            favflag = 0
            if favqset.__len__() > 0:
                favflag = 1         
            d = {'artworkname' : artwork.artworkname, 'creationdate' : creationdate, 'size' : artwork.sizedetails, 'medium' : artwork.medium, 'description' : artwork.description, 'image' : settings.IMG_URL_PREFIX + str(artwork.image1), 'provenance' : '', 'literature' : artwork.literature, 'exhibitions' : artwork.exhibitions, 'href' : '', 'estimate' : '', 'awid' : artwork.id, 'aid' : artwork.artist_id, 'favourite' : favflag}
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
            lotqset = lotartworkdict[str(artwork.id)]
            for lot in lotqset:
                auctionid = lot.auction_id
                auctionobj = None
                try:
                    auctionobj = auctionartworkdict[str(auctionid)]
                except:
                    continue
                eventperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                aucenddate = auctionobj.auctionenddate
                if str(aucenddate) != '0000-00-00' and str(aucenddate) != '01 Jan, 1':
                    eventperiod = eventperiod + " - " + str(aucenddate)
                d2 = {'eventname' : auctionobj.auctionname, 'eventimage' : settings.IMG_URL_PREFIX + str(auctionobj.coverimage), 'eventperiod' : eventperiod, 'aucid' : auctionobj.id}
                allevents.append(d2)
            if allartworks.__len__() >= maxartworkstoshow:
                break
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
        if artistobj.genre is None and artistobj.nationality is not None:
            artistqset = Artist.objects.filter(nationality=artistobj.nationality)[:maxrelatedartist] #.order_by('priority')
        elif artistobj.genre is not None:
            artistqset = Artist.objects.filter(genre__icontains=artistobj.genre)[:maxrelatedartist] #.order_by('priority')
        else:
            artistqset = list()
        for artist in artistqset:
            if artistobj.id == artist.id: # Same artist, skip.
                continue
            aliveperiod = "b. " + str(artist.birthyear)
            if str(artist.deathyear) != "":
                aliveperiod = str(artist.birthyear) + " - " + str(artist.deathyear)
            if artist.artistimage is None or artist.artistimage == "":
                artist.artistimage = "/static/images/default_artist.jpg"
            else:
                artist.artistimage = settings.IMG_URL_PREFIX + str(artist.artistimage)
            d = {'artistname' : artist.artistname, 'about' : artist.description, 'nationality' : artist.nationality, 'birthyear' : artist.birthyear, 'deathyear' : artist.deathyear, 'squareimage' : str(artist.artistimage), 'aid' : artist.id, 'aliveperiod' : aliveperiod}
            relatedartists.append(d)
    context['relatedartists'] = relatedartists
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('artist_artworkdetails.html')
    return HttpResponse(template.render(context, request))


@csrf_exempt
def textfilter(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'err' : "Invalid method of call"}))
    searchkey = None
    aid = None
    page = 1
    if request.method == 'POST':
        if 'txtfilter' in request.POST.keys():
            searchkey = str(request.POST['txtfilter']).strip()
        if 'aid' in request.POST.keys():
            aid = str(request.POST['aid']).strip()
        if 'pageno' in request.POST.keys():
            page = request.POST['pageno']
    if not searchkey or not aid:
        return HttpResponse(json.dumps({'err' : "Invalid Request: Request is missing search key or artist ID or both"}))
    #print(searchkey)
    if not page or page == "":
        page = 1
    context = {}
    pastartworks = []
    maxartworkstoconsider = 200
    startctr = int(page) * maxartworkstoconsider - maxartworkstoconsider
    endctr = int(page) * maxartworkstoconsider
    artistobj = None
    try:
        artistobj = Artist.objects.get(id=aid)
    except:
        return HttpResponse(json.dumps({'err' : "Could not find artist identified by the ID %s"%aid}))
    context['aid'] = aid
    artworksbyartistqset = Artwork.objects.filter(artist_id=aid)[startctr:endctr]
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
                #print(artwork.artworkname)
                if auctionobj is not None:
                    aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                    aucenddate = auctionobj.auctionenddate
                    if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                        aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y") + " - " + str(aucenddate)
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : auctionobj.auctionname, 'aucid' : auctionobj.id, 'aucstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'aucenddate' : str(aucenddate), 'auctionperiod' : aucperiod, 'aid' : aid, 'image' : settings.IMG_URL_PREFIX + str(artwork.image1), 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
                else:
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : '', 'aucid' : '', 'aucstartdate' : '', 'aucenddate' : '', 'aid' : aid, 'image' : settings.IMG_URL_PREFIX + str(artwork.image1), 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate, 'auctionperiod' : ''}
                pastartworks.append(d)
    context['pastartworks'] = pastartworks
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
    return HttpResponse(json.dumps(context))


@csrf_exempt
def morefilter(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'err' : "Invalid method of call"}))
    searchkey = ""
    aid = None
    page = 1
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
        if 'pageno' in requestdict.keys():
            page = requestdict['pageno']
            page = page.replace("'", "")
    if not page or page == "":
        page = 1
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
    maxartworkstoconsider = 2000
    startctr = int(page) * maxsearchresults - maxsearchresults
    endctr = int(page) * maxsearchresults
    try:
        artistobj = Artist.objects.get(id=aid)
    except:
        return HttpResponse(json.dumps({'err' : "Could not find artist identified by the ID %s"%aid}))
    context['aid'] = aid
    artworksbyartistqset = Artwork.objects.filter(artist_id=aid)[startctr:endctr]
    #print(artworksbyartistqset.__len__())
    lotartworkdict = {}
    artworkidslist = []
    lotauctiondict = {}
    auctionidslist = []
    for artwork in artworksbyartistqset:
        if str(artwork.id) not in lotartworkdict.keys():
            lotartworkdict[str(artwork.id)] = []
            artworkidslist.append(artwork.id)
    lotqset = Lot.objects.filter(artwork_id__in=artworkidslist)
    for lotobj in lotqset:
        if str(lotobj.auction_id) not in lotauctiondict.keys():
            lotauctiondict[str(lotobj.auction_id)] = ""
            auctionidslist.append(lotobj.auction_id)
        if str(lotobj.artwork_id) in lotartworkdict.keys():
            awlist = lotartworkdict[str(lotobj.artwork_id)]
        else:
            awlist = []
        awlist.append(lotobj)
        lotartworkdict[str(lotobj.artwork_id)] = awlist
    auctionqset = Auction.objects.filter(id__in=auctionidslist)
    for auctionobj in auctionqset:
        lotauctiondict[str(auctionobj.id)] = auctionobj
    for artwork in artworksbyartistqset:
        if maxsearchresults < pastartworks.__len__():
            break
        lotqset = lotartworkdict[str(artwork.id)]
        #print(artwork.artworkname)
        for lotobj in lotqset:
            try:
                auctionobj = lotauctiondict[str(lotobj.auction_id)]
                #auctionobj = Auction.objects.get(id=lotobj.auction_id)
            except:
                continue
            if searchkey != "" and (searchkey.lower() in artwork.artworkname.lower() or searchkey.lower() in artwork.description.lower() or searchkey.lower() in auctionobj.auctionname.lower()):
                estimatelow = str(lotobj.lowestimateUSD)
                estimatehigh = str(lotobj.highestimateUSD)
                estimate = estimatelow + " - " + estimatehigh
                if auctionobj is not None:
                    aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                    aucenddate = auctionobj.auctionenddate
                    if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                        aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y") + " - " + str(aucenddate)
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : auctionobj.auctionname, 'aucid' : auctionobj.id, 'aucstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'aucenddate' : str(aucenddate), 'auctionperiod' : aucperiod, 'aid' : aid, 'image' : settings.IMG_URL_PREFIX + str(artwork.image1), 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
                else:
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : '', 'aucid' : '', 'aucstartdate' : '', 'aucenddate' : '', 'auctionperiod' : '', 'aid' : aid, 'image' : settings.IMG_URL_PREFIX + str(artwork.image1), 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
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
                    aucenddate = auctionobj.auctionenddate
                    if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                        aucperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y") + " - " + str(aucenddate)
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : auctionobj.auctionname, 'aucid' : auctionobj.id, 'aucstartdate' : auctionobj.auctionstartdate.strftime("%d %b, %Y"), 'aucenddate' : str(aucenddate), 'auctionperiod' : aucperiod, 'aid' : aid, 'image' : settings.IMG_URL_PREFIX + str(artwork.image1), 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
                else:
                    d = {'artworkname' : artwork.artworkname, 'artistname' : artistobj.artistname, 'medium' : artwork.medium, 'size' : artwork.sizedetails, 'startdate' : artwork.creationstartdate, 'awid' : artwork.id, 'description' : artwork.description, 'auctionname' : '', 'aucid' : '', 'aucstartdate' : '', 'aucenddate' : '', 'auctionperiod' : '', 'aid' : aid, 'image' : settings.IMG_URL_PREFIX + str(artwork.image1), 'soldprice' : lotobj.soldpriceUSD, 'estimate' : estimate}
                for medium in mediumlist:
                    if medium in artwork.medium.lower():
                        if maxsearchresults > pastartworks.__len__() and artwork.artworkname not in uniqueartworks.keys():
                            pastartworks.append(d)
                            uniqueartworks[artwork.artworkname] = 1
                        break # We have matched at least one of the selected mediums. So this artwork is included in list. Go to next artwork.
                auctionhouseobj = None
                try:
                    print(auctionobj.auctionhouse_id)
                    auctionhouseobj = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
                    for auctionhousename in auctionhouselist:
                        if auctionhousename in auctionhouseobj.housename.lower():
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
    return HttpResponse(json.dumps(context))


#@login_required(login_url='/login/show/')
def showstats(request):
    """
    Check if request.user.is_authenticated is True. If so, compute and send
    the requested statistical info as json string. If not, send a login link
    as json string. Handle other erroneous conditions as appropriate.
    """
    if request.method != 'GET':
        msg = "<h6>Invalid method of call</h6>"
        context = {'stats' : msg, 'aid' : None, 'div_id' : None, 'err' : 'badcall'}
        return HttpResponse(json.dumps(context))
    aid, divid = None, ""
    if 'aid' in request.GET.keys():
        aid = request.GET['aid']
    else:
        msg = "<h6>Required parameter aid missing</h6>"
        context = {'stats' : msg, 'aid' : None, 'div_id' : None, 'err' : 'noaid'}
        return HttpResponse(json.dumps(context))
    if 'div_id' in request.GET.keys():
        divid = request.GET['div_id']
    else:
        msg = "<h6>Required parameter div Id missing</h6>"
        context = {'stats' : msg, 'aid' : None, 'div_id' : None, 'err' : 'nodiv'}
        return HttpResponse(json.dumps(context))
    if not request.user.is_authenticated:
        loginlink = "<h6><a style='color:#000000;bgcolor:#ffffff;' data-toggle='modal' href='#exampleModal-login' aria-controls='exampleModal-login'>Login to view</a></h6>"
        context = {'stats' : loginlink, 'aid' : aid, 'div_id' : divid, 'err' : 'nologin'}
        return HttpResponse(json.dumps(context))
    artistobj = None
    try:
        artistobj = Artist.objects.get(id=aid)
    except:
        msg = "<h6>Could not find artist identified by Id %s.</h6>"%aid
        context = {'stats' : msg, 'aid' : aid, 'div_id' : divid, 'err' : 'noartist'}
        return HttpResponse(json.dumps(context))
    yearlylotssold = 0
    sellthrurate = 0.0
    avgsaleprice = 0.00
    salepriceoverestimate = 0
    totallotssold = 0
    totalartworks = 0
    soldlotsprice = 0.00
    date2yearsago = datetime.datetime.now() - datetime.timedelta(days=2*365)
    totaldelta = 0.00
    curdatetime = datetime.datetime.now()
    lotartistqset = LotArtist.objects.filter(artist_id=aid)
    for lotartist in lotartistqset:
        artworkid = lotartist.artworkid
        saledate = datetime.datetime.combine(lotartist.saledate, datetime.time(0, 0))
        if saledate and saledate > date2yearsago:
            totallotssold += 1
            soldlotsprice += float(lotartist.artist_price_usd)
            midestimate = (float(lotartist.highestimate) + float(lotartist.lowestimate))/2.0
            if lotartist.artist_price_usd > 0.00:
                delta = (float(lotartist.artist_price_usd) - float(midestimate))/float(lotartist.artist_price_usd)
                totaldelta += delta
            totalartworks += 1
        elif saledate and saledate < date2yearsago:
            continue # If saledate is prior to date2yearsago, skip it.
        elif not saledate: # If there is no saledate, we need to check if the auction of this lot was held within the last 2 years or not.
            totalartworks += 1
    yearlylotssold = int(float(totallotssold)/2.0)
    sellthrurate = "NA"
    if totalartworks != 0:
        sellthrurate = (float(totallotssold)/float(totalartworks)) * 100.00
        sellthrurate = '{:.2f}'.format(sellthrurate)
    avgsaleprice = "NA"
    if totallotssold != 0:
        avgsaleprice = float(soldlotsprice)/float(totallotssold)
        avgsaleprice = '{:.2f}'.format(avgsaleprice)
    salepriceoverestimate = "NA"
    if totallotssold != 0:
        salepriceoverestimate = (float(totaldelta)/float(totallotssold)) * 100.00
        salepriceoverestimate = '{:.2f}'.format(salepriceoverestimate)
    statinfo = "<h6>Yearly Lots Sold: %s</h6><h6>Sell Through Rate: %s&percnt;</h6><h6>Avg. Sale Price (US$): %s</h6><h6>Price Over Estimate: %s&percnt;</h6>"%(yearlylotssold, sellthrurate, avgsaleprice, salepriceoverestimate)
    context = {'stats' : statinfo, 'aid' : aid, 'div_id' : divid, 'err' : ''}
    return HttpResponse(json.dumps(context))
    

@login_required(login_url="/login/show/")
def addfavourite(request):
    """
    Add an artist as a 'favourite' by a legit user.
    """
    if request.method != 'POST':
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
    userobj = request.user
    sessionkey = request.session.session_key
    entitytype, aid, divid = None, None, ''
    requestbody = str(request.body)
    bodycomponents = requestbody.split("&")
    requestdict = {}
    for comp in bodycomponents:
        compparts = comp.split("=")
        if compparts.__len__() > 1:
            compparts[0] = compparts[0].replace("b'", "")
            requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
    if 'entityid' in requestdict.keys():
        aid = requestdict['entityid']
    if 'entitytype' in requestdict.keys():
        entitytype = requestdict['entitytype']
    if 'div_id' in requestdict.keys():
        divid = requestdict['div_id'].replace("'", "")
    if not aid or not divid:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
    if entitytype != 'artist':
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
    artist = None
    try:
        artist = Artist.objects.get(id=aid)
    except:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : divid, 'aid' : aid})) # Operation failed! Can't proceed without an artist.
    # Check if the artist is already a 'favourite' of the user...
    favouriteobj = None
    try:
        favouriteqset = Favourite.objects.filter(user=request.user, reference_model='fineart_artists', reference_model_id=aid)
        if favouriteqset.__len__() > 0:
            favouriteobj = favouriteqset[0]
        else:
            favouriteobj = Favourite()
    except:
        favouriteobj = Favourite()
    favouriteobj.user = request.user
    favouriteobj.reference_model = 'fineart_artists'
    favouriteobj.reference_model_id = aid
    try:
        favouriteobj.save()
    except:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
    return HttpResponse(json.dumps({'msg' : 1, 'div_id' : divid, 'aid' : aid})) # Added to favourites!


@login_required(login_url="/login/show/")
def addfavouritework(request):
    """
    Add an artwork as a 'favourite' by a legit user.
    """
    if request.method != 'POST':
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'awid' : ''})) # Operation failed!
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'awid' : ''})) # Operation failed!
    userobj = request.user
    sessionkey = request.session.session_key
    entitytype, awid, divid = None, None, ''
    requestbody = str(request.body)
    bodycomponents = requestbody.split("&")
    requestdict = {}
    for comp in bodycomponents:
        compparts = comp.split("=")
        if compparts.__len__() > 1:
            compparts[0] = compparts[0].replace("b'", "")
            requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
    if 'entityid' in requestdict.keys():
        awid = requestdict['entityid'].replace("'", "")
    if 'entitytype' in requestdict.keys():
        entitytype = requestdict['entitytype'].replace("'", "")
    if 'div_id' in requestdict.keys():
        divid = requestdict['div_id'].replace("'", "")
    if not awid or not divid:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'awid' : ''})) # Operation failed!
    if entitytype != 'artwork':
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'awid' : ''})) # Operation failed!
    artwork = None
    try:
        artwork = Artwork.objects.get(id=awid)
    except:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : divid, 'awid' : awid})) # Operation failed! Can't proceed without an artwork.
    # Check if the artwork is already a 'favourite' of the user...
    favouriteobj = None
    try:
        favouriteqset = Favourite.objects.filter(user=request.user, reference_model='fineart_artworks', reference_model_id=awid)
        if favouriteqset.__len__() > 0:
            favouriteobj = favouriteqset[0]
        else:
            favouriteobj = Favourite()
    except:
        favouriteobj = Favourite()
    favouriteobj.user = request.user
    favouriteobj.reference_model = 'fineart_artworks'
    favouriteobj.reference_model_id = awid
    try:
        favouriteobj.save()
    except:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'awid' : ''})) # Operation failed!
    return HttpResponse(json.dumps({'msg' : 1, 'div_id' : divid, 'awid' : awid})) # Added to favourites!


