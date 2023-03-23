from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template.context_processors import csrf
from django.views.generic import View
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect, HttpRequest
from django.urls import reverse
from django.template import RequestContext
from django.db.models import Q
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int, is_safe_url
from django.template import Template, Context
from django.template.loader import get_template
from django.core.mail import send_mail
from django.contrib.sessions.backends.db import SessionStore
from threading import Thread
from django.template import loader
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.models import User as djUser, AnonymousUser
from django.contrib.auth.decorators import login_required
import os, sys, re, time, datetime
import simplejson as json
import redis
import pickle
import urllib
# from gallery.models import Gallery, Event
# from museum.models import Museum, MuseumEvent, MuseumPieces
from login.models import User, Session, Favourite, EmailAlerts  # ,WebConfig, Carousel, Follow
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse
from artists.models import Artist, Artwork, FeaturedArtist, LotArtist
from eolicowebsite.utils import connecttoDB, disconnectDB, connectToDb, disconnectDb
# Caching related imports and variables
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.strftime("%d %b, %Y")


def pastUpcomingQueryCreator(request):
    artworkTitle = request.GET.get('artworkTitle')
    lotLowToHigh = request.GET.get('lotLowToHigh')
    lotHighToLow = request.GET.get('lotHighToLow')
    priceLowToHigh = request.GET.get('priceLowToHigh')
    priceHighToLow = request.GET.get('priceHighToLow')
    paintings = request.GET.get('paintings')
    prints = request.GET.get('prints')
    photographs = request.GET.get('photographs')
    miniatures = request.GET.get('miniatures')
    others = request.GET.get('others')
    sold = request.GET.get('sold')
    yetToBeSold = request.GET.get('yetToBeSold')
    boughtIn = request.GET.get('boughtIn')
    withdrawn = request.GET.get('withdrawn')
    fromDate = request.GET.get('fromDate')
    toDate = request.GET.get('toDate')

    whereClause = ''
    orderBy = ''
    orderFlag = False

    if artworkTitle:
        whereClause += f""" AND faa_artwork_title LIKE '%{artworkTitle}%'"""
    if paintings:
        whereClause += f""" AND fal_lot_category = '{paintings}'"""
    if prints:
        whereClause += f""" AND fal_lot_category = '{prints}'"""
    if photographs:
        whereClause += f""" AND fal_lot_category = '{photographs}'"""
    if miniatures:
        whereClause += f""" AND fal_lot_category = '{miniatures}'"""
    if others:
        whereClause += f""" AND fal_lot_category != 'miniatures' AND fal_lot_category != 'photographs' AND fal_lot_category != 'prints' AND fal_lot_category != 'paintings'"""
    if sold:
        whereClause += f""" AND fal_lot_status = '{sold}'"""
    if yetToBeSold:
        whereClause += f""" AND fal_lot_status = '{yetToBeSold}'"""
    if boughtIn:
        whereClause += f""" AND fal_lot_status = '{boughtIn}'"""
    if withdrawn:
        whereClause += f""" AND fal_lot_status = '{withdrawn}'"""
    if fromDate:
        whereClause += f""" AND faa_artwork_start_year = {fromDate}"""
    if toDate:
        whereClause += f""" AND faa_artwork_end_year = {toDate}"""

    if lotLowToHigh:
        orderBy = f""" ORDER BY fal_lot_no"""
        orderFlag = True
    if lotHighToLow:
        orderBy = f""" ORDER BY fal_lot_no DESC"""
        orderFlag = True
    if priceLowToHigh:
        orderBy = f""" ORDER BY fal_lot_sale_price"""
        orderFlag = True
    if priceHighToLow:
        orderBy = f""" ORDER BY fal_lot_sale_price DESC"""
        orderFlag = True
    if orderFlag is False:
        orderBy = f""" ORDER BY faac_auction_start_date DESC"""

    return whereClause + orderBy


@login_required(login_url='/login/show/')
def myArtist(request):
    if request.method != 'GET':
        return HttpResponse('Invalid Request Method!')
    else:
        userobj = request.user
        sessionkey = request.session.session_key
        context = {}
        context['username'] = userobj.username
        return render(request, 'myArtist.html', context)


@login_required(login_url='/login/show/')
def getMyArtists(request):
    if request.method != 'GET':
        return HttpResponse('Invalid Request Method!')
    start = request.GET.get('start')
    limit = request.GET.get('limit')
    getMyArtistsSelectQuery = f"""SELECT fa_artist_ID, fa_artist_name, fa_artist_birth_year, fa_artist_death_year, fa_artist_nationality, fa_artist_image FROM `fineart_artists` INNER JOIN `user_favorites` ON fa_artist_ID = referenced_table_id WHERE reference_table = 'fineart_artists' AND user_id = {request.user.id} LIMIT {limit} OFFSET {start};"""
    connList = connectToDb()
    connList[1].execute(getMyArtistsSelectQuery)
    myArtistsData = connList[1].fetchall()
    disconnectDb(connList)
    return HttpResponse(json.dumps(myArtistsData, default=default))



@login_required(login_url='/login/show/')
def myArtistDetails(request):
    if request.method != 'GET':
        return HttpResponse('Invalid Request Method!')
    else:
        artistId = request.GET.get('aid').replace('"', '')
        userobj = request.user
        sessionkey = request.session.session_key
        context = {}
        context['username'] = userobj.username
        followUnfollowSelectQuery = f"""SELECT user_id FROM user_favorites WHERE user_id = {request.user.id} AND referenced_table_id = {artistId} AND reference_table = 'fineart_artists'"""
        connList = connectToDb()
        connList[1].execute(followUnfollowSelectQuery)
        followUnfollowData = connList[1].fetchone()
        disconnectDb(connList)
        if followUnfollowData:
            context['followUnfollow'] = True
        else:
            context['followUnfollow'] = False
        return render(request, 'myArtistDetails.html', context)


@login_required(login_url='/login/show/')
def myArtwork(request):
    if request.method != 'GET':
        return HttpResponse('Invalid Request Method!')
    else:
        userobj = request.user
        sessionkey = request.session.session_key
        context = {}
        context['username'] = userobj.username
        return render(request, 'myArtwork.html', context)


@login_required(login_url='/login/show/')
def artMarketAnalysis(request):
    if request.method != 'GET':
        return HttpResponse('Invalid Request Method!')
    else:
        userobj = request.user
        sessionkey = request.session.session_key
        context = {}
        context['username'] = userobj.username
        return render(request, 'artMarketAnalysis.html', context)


@login_required(login_url='/login/show/')
def getMyArtworks(request):
    if request.method != 'GET':
        return HttpResponse('Invalid Request Method!')
    start = request.GET.get('start')
    limit = request.GET.get('limit')
    getMyArtworksSelectQuery = f"""SELECT fal_lot_ID, fal_lot_no, cah_auction_house_currency_code, fal_lot_high_estimate, fal_lot_low_estimate, fal_lot_sale_price, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_sale_price_USD, faac_auction_title, faa_artwork_image1, faa_artwork_material, faac_auction_ID, faa_artwork_category, fal_artwork_ID, faa_artwork_title, fa_artist_ID, fa_artist_name, faac_auction_start_date, cah_auction_house_name, cah_auction_house_location FROM `fineart_lots` INNER JOIN `fineart_artworks` ON fal_artwork_ID = faa_artwork_ID INNER JOIN `fineart_auction_calendar` ON fal_auction_ID = faac_auction_ID INNER JOIN `fineart_artists` ON faa_artist_ID = fa_artist_ID INNER JOIN`core_auction_houses` ON faac_auction_house_ID = cah_auction_house_ID INNER JOIN `user_favorites` ON faa_artwork_ID = referenced_table_id WHERE reference_table = 'fineart_artworks' AND user_id = {request.user.id}"""
    whereClauseAndOrderBy = pastUpcomingQueryCreator(request)
    getMyArtworksSelectQuery += whereClauseAndOrderBy + f""" LIMIT {limit} OFFSET {start};"""
    connList = connectToDb()
    connList[1].execute(getMyArtworksSelectQuery)
    myArtworksData = connList[1].fetchall()
    disconnectDb(connList)
    return HttpResponse(json.dumps(myArtworksData, default=default))


@login_required(login_url='/login/show/')
def myArtworkDetails(request):
    if request.method != 'GET':
        return HttpResponse('Invalid Request Method!')
    else:
        lotId = request.GET.get('lid')

        def getFollowUnfollowArtwork():
            followUnfollowSelect = f"""SELECT user_id FROM user_favorites WHERE user_id = {request.user.id} AND reference_table = 'fineart_artworks' AND referenced_table_id = (SELECT fal_artwork_ID FROM fineart_lots WHERE fal_lot_ID = {lotId})"""
            connList = connectToDb()
            connList[1].execute(followUnfollowSelect)
            followUnfollowData = connList[1].fetchone()
            disconnectDb(connList)
            if followUnfollowData:
                context['followUnfollowArtwork'] = True
            else:
                context['followUnfollowArtwork'] = False

        def getFollowUnfollowArtist():
            followUnfollowSelect = f"""SELECT user_id FROM user_favorites WHERE user_id = {request.user.id} AND reference_table = 'fineart_artists' AND referenced_table_id = (SELECT fal_artist_ID FROM fineart_lots WHERE fal_lot_ID = {lotId})"""
            connList = connectToDb()
            connList[1].execute(followUnfollowSelect)
            followUnfollowData = connList[1].fetchone()
            disconnectDb(connList)
            if followUnfollowData:
                context['followUnfollowArtist'] = True
            else:
                context['followUnfollowArtist'] = False

        artworkThread = Thread(target=getFollowUnfollowArtwork)
        artworkThread.start()
        artistThread = Thread(target=getFollowUnfollowArtist)
        artistThread.start()
        userobj = request.user
        sessionkey = request.session.session_key
        context = {}
        context['username'] = userobj.username
        artworkThread.join()
        artistThread.join()
        return render(request, 'myArtworkDetails.html', context)


"""
def getcarouselinfo():
    entrieslist = []
    countqset = WebConfig.objects.filter(paramname="carousel entries count")
    entriescount = countqset[0].paramvalue
    try:
        entrieslist = pickle.loads(redis_instance.get('carouselentries'))
    except:
        pass
    if entrieslist.__len__() == 0:
        carouselqset = Carousel.objects.all().order_by('priority', '-edited')
        for e in range(0, int(entriescount)):
            imgpath = carouselqset[e].imagepath
            title = carouselqset[e].title
            text = carouselqset[e].textvalue
            datatype = carouselqset[e].datatype
            dataid = carouselqset[e].data_id
            d = {'img' : imgpath, 'title' : title, 'text' : text, 'datatype' : datatype, 'data_id' : dataid}
            entrieslist.append(d)
        try:
            redis_instance.set('carouselentries', pickle.dumps(entrieslist))
        except:
            pass
    return entrieslist
"""


def search(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    else:
        searchTerm = request.GET.get('term')
        return HttpResponse(json.dumps([{'id': searchTerm, 'label': searchTerm, 'value': searchTerm}]))


def termsAndCondition(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    else:
        return render(request, 'termsAndCondition.html')


def getcarouselinfo_new():
    entrieslist = []
    entriescount = int(os.environ.get('WEBSITE_CAROUSEL_ENTRIES_COUNT', '5'))  # Default value: 5
    # print("############## " + str(entriescount) + " ########################")
    try:
        entrieslist = pickle.loads(redis_instance.get('com_carouselentries'))
    except:
        pass
    if entrieslist.__len__() == 0:
        connlist = connecttoDB()
        dbconn = connlist[0]
        cursor = connlist[1]
        # Find the 'entriescount' number of artworks sold in last 1 month ordered by decreasing values of 'fal_lot_low_estimate_USD'.
        carouselsql = "select lot.fal_artwork_ID, artwork.faa_artwork_title, artwork.faa_artist_ID, lot.fal_auction_ID, lot.fal_lot_high_estimate_USD, lot.fal_lot_low_estimate_USD, lot.fal_lot_sale_price_USD, lot.fal_lot_material, lot.fal_lot_size_details, lot.fal_lot_provenance, lot.fal_lot_image1, lot.fal_lot_sale_date from fineart_lots lot, fineart_artworks artwork where lot.fal_artwork_ID = artwork.faa_artwork_ID and lot.fal_lot_image1 <> '' and lot.fal_lot_sale_date > DATE_ADD(NOW(), INTERVAL -%s DAY) order by lot.fal_lot_low_estimate_USD desc limit %s" % (
        settings.CAROUSEL_DAYS, entriescount)
        cursor.execute(carouselsql)
        carouselrecords = cursor.fetchall()
        for rec in carouselrecords:
            awid = rec[0]
            awtitle = rec[1]
            artistid = rec[2]
            aucid = rec[3]
            highestimate = str(rec[4])
            lowestimate = str(rec[5])
            soldprice = str(rec[6])
            medium = str(rec[7])
            size = str(rec[8])
            prov = str(rec[9])
            artimg = str(rec[10])
            imagewebpath = settings.IMG_URL_PREFIX + str(artimg)
            saledate = rec[11]
            d = {'artworkid': awid, 'artworkname': awtitle, 'artistid': artistid, 'auctionid': aucid,
                 'highestimate': highestimate, 'lowestimate': lowestimate, 'soldprice': soldprice, 'medium': medium,
                 'sizedetails': size, 'provenance': prov, 'artworkimage': imagewebpath, 'saledate': saledate}
            entrieslist.append(d)
        cursor.close()  # close db cursor
        dbconn.close()  # close db connection.
        try:
            redis_instance.set('com_carouselentries', pickle.dumps(entrieslist))
        except:
            pass
    return entrieslist


def show(request):
    return HttpResponseRedirect("/login/index/")


# @cache_page(CACHE_TTL)
def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    chunksize = 3
    context = {}
    # if request.user.is_authenticated:
    #     connlist = connecttoDB()
    #     dbconn = connlist[0]
    #     cursor = connlist[1]
    #     favouritesdict = {}
    #     favsqset = Favourite.objects.filter(user=request.user).order_by("-updated")
    #     favartistsdict = {}
    #     favartistslist = []
    #     favartworksdict = {}
    #     favartworkslist = []
    #     favauctionsdict = {}
    #     favauctionslist = []
    #     for fav in favsqset:
    #         favtype = fav.reference_model
    #         favmodelid = fav.reference_model_id
    #         if favtype == "fineart_artists":
    #             favartistslist.append(str(favmodelid))
    #         elif favtype == "fineart_artworks":
    #             favartworkslist.append(str(favmodelid))
    #         elif favtype == "fineart_auction_calendar":
    #             favauctionslist.append(str(favmodelid))
    #     artistidsstr = "(" + ",".join(favartistslist) + ")"
    #     if favartistslist.__len__() == 0:
    #         artistidsstr = "()"
    #     artworkidsstr = "(" + ",".join(favartworkslist) + ")"
    #     if favartworkslist.__len__() == 0:
    #         artworkidsstr = "()"
    #     auctionidsstr = "(" + ",".join(favauctionslist) + ")"
    #     if favauctionslist.__len__() == 0:
    #         auctionidsstr = "()"
    #     favartistsql = "select fa_artist_ID, fa_artist_name, fa_artist_nationality, fa_artist_description, fa_artist_image from fineart_artists where fa_artist_ID in %s" % artistidsstr
    #     favartworksql = "select artworkid, artworkname, sizedetails, lotimage1, medium, artist_id, artist_name from fa_artwork_lot_artist where artworkid in %s" % artworkidsstr
    #     favauctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_start_date, faac_auction_end_date, faac_auction_house_ID, faac_auction_image from fineart_auction_calendar where faac_auction_ID in %s" % auctionidsstr
    #     if artistidsstr != "()":
    #         cursor.execute(favartistsql)
    #         favartistsrecords = cursor.fetchall()
    #     else:
    #         favartistsrecords = []
    #     if artworkidsstr != "()":
    #         cursor.execute(favartworksql)
    #         favartworksrecords = cursor.fetchall()
    #     else:
    #         favartworksrecords = []
    #     if auctionidsstr != "()":
    #         cursor.execute(favauctionsql)
    #         favauctionsrecords = cursor.fetchall()
    #     else:
    #         favauctionsrecords = []
    #     for favartistrec in favartistsrecords:
    #         artistid = str(favartistrec[0])
    #         favartistsdict[artistid] = favartistrec
    #     for favartworkrec in favartworksrecords:
    #         artworkid = str(favartworkrec[0])
    #         favartworksdict[artworkid] = favartworkrec
    #     for favauctionrec in favauctionsrecords:
    #         auctionid = str(favauctionrec[0])
    #         favauctionsdict[auctionid] = favauctionrec
    #     for fav in favsqset:
    #         favtype = fav.reference_model
    #         if favtype == "fineart_artists":
    #             favmodelid = fav.reference_model_id
    #             try:
    #                 artist = favartistsdict[str(favmodelid)]
    #                 artistname = artist[1]
    #                 aimg = settings.IMG_URL_PREFIX + str(artist[4])
    #                 anat = artist[2]
    #                 aid = artist[0]
    #                 about = artist[3]
    #                 favouritesdict[artistname] = ["artist", aimg, anat, aid, about]
    #             except:
    #                 pass
    #         elif favtype == "fineart_artworks":
    #             favmodelid = fav.reference_model_id
    #             try:
    #                 artwork = favartworksdict[str(favmodelid)]
    #                 artworkname = artwork[1]
    #                 artist_id = artwork[5]
    #                 artworkimg = settings.IMG_URL_PREFIX + str(artwork[3])
    #                 size = artwork[2]
    #                 medium = artwork[4]
    #                 awid = artwork[0]
    #                 artistname = artwork[6]
    #                 # artist = Artist.objects.get(id=artist_id)
    #                 # artistname = artist.artistname
    #                 favouritesdict[artworkname] = ["artwork", artworkimg, size, medium, artistname, awid, artist_id]
    #             except:
    #                 pass
    #         elif favtype == "fineart_auction_calendar":
    #             favmodelid = fav.reference_model_id
    #             try:
    #                 auction = favauctionsdict[str(favmodelid)]
    #                 auctionname = auction[1]
    #                 period = auction[2].strftime("%d %b, %Y")
    #                 aucenddate = auction[3]
    #                 if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
    #                     period = period + " - " + str(aucenddate)
    #                 auchouseid = auction[4]
    #                 auchouseobj = AuctionHouse.objects.get(id=auchouseid)
    #                 housename = auchouseobj.housename
    #                 aucid = auction[0]
    #                 aucimg = settings.IMG_URL_PREFIX + str(auction[5])
    #                 favouritesdict[auctionname] = ["auction", period, housename, aucid, aucimg, auchouseid]
    #             except:
    #                 pass
    #     context['favourites'] = favouritesdict
    # artistsdict = {}
    # try:
    #     artistsdict = pickle.loads(redis_instance.get('h_artistsdict'))
    # except:
    #     pass
    # if artistsdict.keys().__len__() == 0:
    #     artists = FeaturedArtist.objects.all().order_by('-totalsoldprice')[:6]
    #     for a in artists:
    #         if a.id == 1: # This is for 'missing' artists
    #             continue
    #         aname = a.artist_name
    #         about = a.description
    #         aurl = ""
    #         if a.artistimage is None or a.artistimage == "":
    #             aimg = "/static/images/default_artist.jpg"
    #         else:
    #             aimg = settings.IMG_URL_PREFIX + str(a.artistimage)
    #         anat = a.nationality
    #         aid = a.artist_id
    #         # Check for follows and favourites
    #         if request.user.is_authenticated:
    #             #folqset = Follow.objects.filter(user=request.user, artist__id=a.artist_id)
    #             folqset = []
    #             favqset = Favourite.objects.filter(user=request.user, reference_model="fineart_artists", reference_model_id=a.artist_id)
    #         else:
    #             folqset = []
    #             favqset = []
    #         folflag = 0
    #         if folqset.__len__() > 0:
    #             folflag = 1
    #         favflag = 0
    #         if favqset.__len__() > 0:
    #             favflag = 1
    #         artistsdict[aname] = [about, aurl, aimg, anat, aid, folflag, favflag]
    #     try:
    #         redis_instance.set('h_artistsdict', pickle.dumps(artistsdict))
    #     except:
    #         pass
    # context['artists'] = artistsdict
    # eventsdict = {}
    # try:
    #     eventsdict = pickle.loads(redis_instance.get('h_eventsdict'))
    # except:
    #     pass
    # if eventsdict.keys().__len__() == 0:
    #     events = Event.objects.all().order_by('priority', '-edited')
    #     eventslist = events[0:4]
    #     for e in eventslist:
    #         ename = e.eventname
    #         eurl = e.eventurl
    #         einfo = str(e.eventinfo[0:20]) + "..."
    #         eperiod = e.eventperiod
    #         eid = e.id
    #         eventimage = e.eventimage
    #         eventsdict[ename] = [eurl, einfo, eperiod, eid, eventimage ]
    #     try:
    #         redis_instance.set('h_eventsdict', pickle.dumps(eventsdict))
    #     except:
    #         pass
    # context['events'] = eventsdict
    # museumsdict = {}
    # try:
    #     museumsdict = pickle.loads(redis_instance.get('h_museumsdict'))
    # except:
    #     pass
    # if museumsdict.keys().__len__() == 0:
    #     museumsqset = Museum.objects.all().order_by('priority', '-edited')
    #     museumslist = museumsqset[0:4]
    #     for mus in museumslist:
    #         mname = mus.museumname
    #         murl = mus.museumurl
    #         minfo = str(mus.description[0:20]) + "..."
    #         mlocation = mus.location
    #         mid = mus.id
    #         mimage = mus.coverimage
    #         museumsdict[mname] = [murl, minfo, mlocation, mid, mimage ]
    #     try:
    #         redis_instance.set('h_museumsdict', pickle.dumps(museumsdict))
    #     except:
    #         pass
    # context['museums'] = museumsdict
    # upcomingauctions = {}
    # try:
    #     upcomingauctions = pickle.loads(redis_instance.get('h_upcomingauctions'))
    # except:
    #     pass
    # if upcomingauctions.keys().__len__() == 0:
    #     auctionsqset = Auction.objects.all().order_by('-auctionstartdate')[:6] # Limiting to top 200 only.
    #     actr = 0
    #     srcPattern = re.compile("src=(.*)$")
    #     curdate = datetime.datetime.now()
    #     datenow = str(datetime.date(curdate.year, curdate.month,curdate.day))
    #     aucidlist = []
    #     auchouseidlist = []
    #     for auction in auctionsqset:
    #         if str(auction.auctionstartdate) < datenow: # Past auction - leave it.
    #             continue
    #         aucidlist.append(auction.id)
    #         auchouseidlist.append(auction.auctionhouse_id)
    #     lotsqset = Lot.objects.filter(auction_id__in=aucidlist).order_by('-lowestimateUSD')
    #     lotsbyauctiondict = {}
    #     for lot in lotsqset:
    #         if lot.lotimage1 == '' or lot.lotimage1 is None:
    #             continue
    #         aucid = lot.auction_id
    #         if str(aucid) not in lotsbyauctiondict.keys():
    #             lotsbyauctiondict[str(aucid)] = [lot,]
    #         else:
    #             lotslist = lotsbyauctiondict[str(aucid)]
    #             lotslist.append(lot)
    #             lotsbyauctiondict[str(aucid)] = lotslist
    #     auchousedict = {}
    #     auchouseqset = AuctionHouse.objects.filter(id__in=auchouseidlist)
    #     for auchouse in auchouseqset:
    #         auchousedict[str(auchouse.id)] = auchouse
    #     for auction in auctionsqset:
    #         if str(auction.auctionstartdate) < datenow: # Past auction - leave it.
    #             continue
    #         lotsqset = lotsbyauctiondict[str(auction.id)]
    #         if lotsqset.__len__() == 0:
    #             continue
    #         if auction.coverimage is None or auction.coverimage == "":
    #             imageloc = settings.IMG_URL_PREFIX + str(lotsqset[0].lotimage1)
    #         else:
    #             imageloc = settings.IMG_URL_PREFIX + str(auction.coverimage)
    #         lotobj = lotsqset[0]
    #         if imageloc == settings.IMG_URL_PREFIX:
    #             imageloc = settings.IMG_URL_PREFIX + str(lotobj.lotimage1)
    #             spc = re.search(srcPattern, imageloc)
    #             if spc:
    #                 imageloc = settings.IMG_URL_PREFIX + str(spc.groups()[0])
    #                 imageloc = imageloc.replace("%3A", ":").replace("%2F", "/")
    #         auchouseobj = None
    #         auchousename, ahlocation = "", ""
    #         try:
    #             #print(auction.auctionhouse_id)
    #             auchouseobj = auchousedict[str(auction.auctionhouse_id)]
    #             auchousename = auchouseobj.housename
    #             #print(auchousename)
    #             ahlocation = auchouseobj.location
    #         except:
    #             pass
    #         auctionperiod = ""
    #         if auction.auctionstartdate.strftime("%d %b, %Y") != "01 Jan, 0001" and auction.auctionstartdate.strftime("%d %b, %Y") != "01 Jan, 1":
    #             auctionperiod = auction.auctionstartdate.strftime("%d %b, %Y")
    #             aucenddate = auction.auctionenddate
    #             if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
    #                 auctionperiod += " - " + str(aucenddate)
    #         # Check for favourites
    #         #print(request.user)
    #         favflag = 0
    #         if request.user.is_authenticated:
    #             favqset = Favourite.objects.filter(user=request.user, reference_model="fineart_auction_calendar", reference_model_id=auction.id)
    #             favflag = 0
    #             if favqset.__len__() > 0:
    #                 favflag = 1
    #         d = {'auctionname' : auction.auctionname, 'auctionid' : auction.auctionid, 'auctionhouse' : auchousename, 'location' : ahlocation, 'coverimage' : imageloc, 'aucid' : auction.id, 'auctionperiod' : auctionperiod, 'auctionurl' : auction.auctionurl, 'lid' : lotobj.id, 'ahid' : auction.auctionhouse_id, 'favourite' : favflag}
    #         upcomingauctions[auction.auctionname] = d
    #         actr += 1
    #         if actr >= chunksize:
    #             break
    #     try:
    #         redis_instance.set('h_upcomingauctions', pickle.dumps(upcomingauctions))
    #     except:
    #         pass
    # context['upcomingauctions'] = upcomingauctions
    # auctionhouses = []
    # try:
    #     auctionhouses = pickle.loads(redis_instance.get('h_auctionhouses'))
    # except:
    #     pass
    # if auctionhouses.__len__() == 0:
    #     auchousesqset = AuctionHouse.objects.all()[:12] # Limiting to top 200 only.
    #     actr = 0
    #     auchouseidlist = []
    #     for auchouse in auchousesqset:
    #         auchouseidlist.append(auchouse.id)
    #     aucbyauchousedict = {}
    #     aucqset = Auction.objects.filter(auctionhouse_id__in=auchouseidlist)
    #     for auc in aucqset:
    #         auchouseid = auc.auctionhouse_id
    #         if str(auchouseid) not in aucbyauchousedict.keys():
    #             aucbyauchousedict[str(auchouseid)] = [auc,]
    #         else:
    #             auclist = aucbyauchousedict[str(auchouseid)]
    #             auclist.append(auc)
    #             aucbyauchousedict[str(auchouseid)] = auclist
    #     for auchouse in auchousesqset:
    #         auchousename = auchouse.housename
    #         auctionsqset = aucbyauchousedict[str(auchouse.id)]
    #         if auctionsqset.__len__() == 0:
    #             continue
    #         #print(auctionsqset[0].coverimage)
    #         d = {'housename' : auchouse.housename, 'aucid' : auctionsqset[0].id, 'location' : auchouse.location, 'description' : '', 'coverimage' : settings.IMG_URL_PREFIX + str(auctionsqset[0].coverimage), 'ahid' : auchouse.id}
    #         auctionhouses.append(d)
    #         actr += 1
    #         if actr >= chunksize:
    #             break
    #     try:
    #         redis_instance.set('h_auctionhouses', pickle.dumps(auctionhouses))
    #     except:
    #         pass
    # context['auctionhouses'] = auctionhouses
    # cursor.close()
    # dbconn.close()
    # carouselentries = getcarouselinfo_new()
    # context['carousel'] = carouselentries
    # todayDate = datetime.datetime.now().date()
    # subtractDate = todayDate - datetime.timedelta(days=365)
    # connList = connectToDb()
    # trendingArtistSelectQuery = f"""SELECT fa_artist_ID, SUM(fal_lot_sale_price) AS fal_lot_sale_price, fa_artist_name, fa_artist_birth_year, fa_artist_death_year, fa_artist_nationality, fa_artist_image FROM `fineart_artists` INNER JOIN `fineart_artworks` ON fineart_artists.fa_artist_ID = fineart_artworks.faa_artist_ID INNER JOIN `fineart_lots` ON fineart_artworks.faa_artwork_ID = fineart_lots.fal_artwork_ID WHERE fa_artist_image IS NOT NULL AND fa_artist_image != '' AND fal_lot_sale_date BETWEEN '{subtractDate}' AND '{todayDate}' GROUP BY fa_artist_ID ORDER BY SUM(fal_lot_sale_price) DESC LIMIT 6;"""
    # connList[1].execute(trendingArtistSelectQuery)
    # context['trendingArtists'] = connList[1].fetchall()
    # upcomingAuctionSelectQuery = f"""SELECT faac_auction_ID, faac_auction_title, faac_auction_image, faac_auction_start_date, cah_auction_house_name, cah_auction_house_location FROM `fineart_auction_calendar` INNER JOIN `core_auction_houses` ON fineart_auction_calendar.faac_auction_house_ID = core_auction_houses.cah_auction_house_ID WHERE faac_auction_start_date >= '{todayDate}' AND faac_auction_lot_count IS NOT NULL ORDER BY faac_auction_start_date DESC LIMIT 6;"""
    # connList[1].execute(upcomingAuctionSelectQuery)
    # context['upcomingAuctions'] = connList[1].fetchall()
    # recentAuctionSelectQuery = f"""SELECT faac_auction_ID, faac_auction_title, faac_auction_image, faac_auction_start_date, cah_auction_house_name, cah_auction_house_location FROM `fineart_auction_calendar` INNER JOIN `core_auction_houses` ON fineart_auction_calendar.faac_auction_house_ID = core_auction_houses.cah_auction_house_ID WHERE faac_auction_start_date < '{todayDate}' AND faac_auction_lot_count IS NOT NULL ORDER BY faac_auction_start_date DESC LIMIT 6;"""
    # connList[1].execute(recentAuctionSelectQuery)
    # context['recentAuctions'] = connList[1].fetchall()
    # disconnectDb(connList)
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    userobj = request.user
    context['username'] = userobj.username
    template = loader.get_template('homepage.html')
    return HttpResponse(template.render(context, request))


def getTrendingArtist(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    start = request.GET.get('start')
    limit = request.GET.get('limit')
    todayDate = datetime.datetime.now().date()
    subtractDate = todayDate - datetime.timedelta(days=365)
    connList = connectToDb()
    trendingArtistSelectQuery = f"""SELECT fa_artist_ID, fa_artist_name, fa_artist_birth_year, fa_artist_death_year, fa_artist_nationality, fa_artist_image FROM `fineart_artists` INNER JOIN `fineart_artworks` ON fineart_artists.fa_artist_ID = fineart_artworks.faa_artist_ID INNER JOIN `fineart_lots` ON fineart_artworks.faa_artwork_ID = fineart_lots.fal_artwork_ID WHERE fa_artist_image IS NOT NULL AND fa_artist_image != '' AND fal_lot_sale_date BETWEEN '{subtractDate}' AND '{todayDate}' GROUP BY fa_artist_ID ORDER BY SUM(fal_lot_sale_price) DESC LIMIT {limit} OFFSET {start};"""
    connList[1].execute(trendingArtistSelectQuery)
    trendingArtistData = connList[1].fetchall()
    disconnectDb(connList)
    return HttpResponse(json.dumps(trendingArtistData))




def getUpcomingAuctions(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    start = request.GET.get('start')
    limit = request.GET.get('limit')
    auctionHouseName = request.GET.get('auctionHouseName')
    auctionTitle = request.GET.get('auctionTitle')
    saleDate = request.GET.get('saleDate')
    fromDate = request.GET.get('fromDate')
    toDate = request.GET.get('toDate')
    houses = request.GET.get('houses')
    locations = request.GET.get('locations')
    todayDate = datetime.datetime.now().date()
    upcomingAuctionSelectQuery = f"""SELECT faac_auction_ID, faac_auction_title, faac_auction_image, faac_auction_start_date, cah_auction_house_name, cah_auction_house_location FROM `fineart_auction_calendar` INNER JOIN `core_auction_houses` ON fineart_auction_calendar.faac_auction_house_ID = core_auction_houses.cah_auction_house_ID WHERE faac_auction_start_date >= '{todayDate}'"""
    whereClause = """ """
    orderByClause = """ORDER BY"""
    if auctionHouseName:
        whereClause += f"""AND cah_auction_house_name = "{auctionHouseName}" """
    if auctionTitle:
        whereClause += f"""AND faac_auction_title like '%{auctionTitle}%' """
    if saleDate:
        orderByClause += """ faac_auction_start_date """
    else:
        orderByClause += """ faac_auction_start_date DESC """
    if fromDate:
        whereClause += f""" AND faac_auction_start_date = '{fromDate}' """
    if toDate:
        whereClause += f""" AND faac_auction_end_date = '{toDate}' """
    if houses:
        housesList = houses.split(',')
        for housesName in housesList:
            if housesName != '':
                whereClause += f""" AND cah_auction_house_name = "{housesName}" """
    if locations:
        locationsList = locations.split(',')
        for location in locationsList:
            if location != '':
                whereClause += f""" AND cah_auction_house_location = "{location}" """
    upcomingAuctionSelectQuery += whereClause + orderByClause + f"""LIMIT {limit} OFFSET {start};"""
    connList = connectToDb()
    connList[1].execute(upcomingAuctionSelectQuery)
    upcomingAuctionsData = connList[1].fetchall()
    disconnectDb(connList)
    return HttpResponse(json.dumps(upcomingAuctionsData, default=default))


def getRecentAuctions(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    start = request.GET.get('start')
    limit = request.GET.get('limit')
    auctionHouseName = request.GET.get('auctionHouseName')
    auctionTitle = request.GET.get('auctionTitle')
    saleDate = request.GET.get('saleDate')
    fromDate = request.GET.get('fromDate')
    toDate = request.GET.get('toDate')
    houses = request.GET.get('houses')
    locations = request.GET.get('locations')
    todayDate = datetime.datetime.now().date()
    recentAuctionSelectQuery = f"""SELECT faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_image, faac_auction_start_date, cah_auction_house_name, cah_auction_house_location FROM `fineart_auction_calendar` INNER JOIN `core_auction_houses` ON fineart_auction_calendar.faac_auction_house_ID = core_auction_houses.cah_auction_house_ID WHERE faac_auction_start_date < '{todayDate}'"""
    whereClause = """ """
    orderByClause = """ORDER BY"""
    if auctionHouseName:
        whereClause += f"""AND cah_auction_house_name = "{auctionHouseName}" """
    if auctionTitle:
        whereClause += f"""AND faac_auction_title like '%{auctionTitle}%' """
    if saleDate:
        orderByClause += """ faac_auction_start_date """
    else:
        orderByClause += """ faac_auction_start_date DESC """
    if fromDate:
        whereClause += f""" AND faac_auction_start_date = '{fromDate}' """
    if toDate:
        whereClause += f""" AND faac_auction_end_date = '{toDate}' """
    if houses:
        housesList = houses.split(',')
        for housesName in housesList:
            if housesName != '':
                whereClause += f""" AND cah_auction_house_name = "{housesName}" """
    if locations:
        locationsList = locations.split(',')
        for location in locationsList:
            if location != '':
                whereClause += f""" AND cah_auction_house_location = "{location}" """
    recentAuctionSelectQuery += whereClause + orderByClause + f"""LIMIT {limit} OFFSET {start};"""
    connList = connectToDb()
    connList[1].execute(recentAuctionSelectQuery)
    recentAuctionsData = connList[1].fetchall()
    disconnectDb(connList)
    return HttpResponse(json.dumps(recentAuctionsData, default=default))


@login_required(login_url='/login/show/')
def getFollowedArtists(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    getFollowedArtistsSelectQuery = f"""SELECT COUNT(user_id) as user_artist_followed_counts FROM `user_favorites` WHERE reference_table = 'fineart_artists' AND user_id = {request.user.id}"""
    data = {}

    def getFollowedThisWeekData(followedArtistsSelectQuery):
        followedThisWeekSelectQuery = followedArtistsSelectQuery + f""" AND created BETWEEN '{datetime.datetime.now() - datetime.timedelta(days=7)}' AND '{datetime.datetime.now()}';"""
        connList = connectToDb()
        connList[1].execute(followedThisWeekSelectQuery)
        thisWeekFollowedArtists = connList[1].fetchone()
        disconnectDb(connList)
        data['this_week_followed_artist_counts'] = thisWeekFollowedArtists['user_artist_followed_counts']
    thread = Thread(target=getFollowedThisWeekData, args=(getFollowedArtistsSelectQuery,))
    thread.start()
    connList = connectToDb()
    connList[1].execute(getFollowedArtistsSelectQuery)
    followedArtistsData = connList[1].fetchone()
    disconnectDb(connList)
    data['user_artist_followed_counts'] = followedArtistsData['user_artist_followed_counts']
    thread.join()
    return HttpResponse(json.dumps(data))


@login_required(login_url='/login/show/')
def getMyArtistsDetails(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    getMyArtistsIdSelectQuery = f"""SELECT DISTINCT(fa_artist_ID) AS fa_artist_ID, fa_artist_name FROM `user_favorites` INNER JOIN `fineart_artists` ON referenced_table_id = fa_artist_ID WHERE user_id = {request.user.id} AND reference_table = 'fineart_artists';"""
    connList = connectToDb()
    connList[1].execute(getMyArtistsIdSelectQuery)
    getMyArtistsData = connList[1].fetchall()
    disconnectDb(connList)
    dataList = []

    def dataSelector(getMyArtistData):
        getTotalArtworkSelectQuery = f"""SELECT COUNT(DISTINCT(faa_artwork_ID)) AS totalArtworkData FROM fineart_artworks WHERE faa_artist_ID = {getMyArtistData['fa_artist_ID']};"""
        connList = connectToDb()
        connList[1].execute(getTotalArtworkSelectQuery)
        getTotalArtworkData = connList[1].fetchone()
        getAverageSellingRateSelectQuery = f"""SELECT COUNT(fal_artwork_ID) AS totalSoldArtworkData FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE fal_lot_status = 'sold' AND faa_artist_ID = {getMyArtistData['fa_artist_ID']};"""
        connList[1].execute(getAverageSellingRateSelectQuery)
        getTotalSoldArtworkData = connList[1].fetchone()
        getAverageSellingRate = (int(getTotalSoldArtworkData['totalSoldArtworkData']) * 100) / int(getTotalArtworkData['totalArtworkData'])
        getAverageSellingPriceSelectQuery = f"""SELECT AVG(fal_lot_sale_price_USD) AS averageSellingPrice FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE fal_lot_status = 'sold' AND faa_artist_ID = {getMyArtistData['fa_artist_ID']};"""
        connList[1].execute(getAverageSellingPriceSelectQuery)
        getAverageSellingPrice = connList[1].fetchone()
        getAverageSellingPriceIn12MonthSelectQuery = f"""SELECT AVG(fal_lot_sale_price_USD) averageSellingPriceIn12Month FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE fal_lot_status = 'sold' AND faa_artist_ID = {getMyArtistData['fa_artist_ID']} AND fal_lot_sale_date BETWEEN '{datetime.datetime.now().date() - datetime.timedelta(days=365)}' AND '{datetime.datetime.now().date()}';"""
        connList[1].execute(getAverageSellingPriceIn12MonthSelectQuery)
        getAverageSellingPriceIn12Month = connList[1].fetchone()
        getTotalArtworkSoldIn12MonthSelectQuery = f"""SELECT COUNT(faa_artwork_ID) AS totalArtworkSoldIn12Month FROM fineart_artworks INNER JOIN fineart_lots ON faa_artwork_ID = fal_artwork_ID WHERE faa_artist_ID = {getMyArtistData['fa_artist_ID']} AND fal_lot_status = 'sold' AND fal_lot_sale_date BETWEEN '{datetime.datetime.now().date() - datetime.timedelta(days=365)}' AND '{datetime.datetime.now().date()}';"""
        connList[1].execute(getTotalArtworkSoldIn12MonthSelectQuery)
        getTotalArtworkSoldIn12Month = connList[1].fetchone()
        getTotalArtworkIn12MonthSelectQuery = f"""SELECT COUNT(faa_artwork_ID) AS totalArtworkIn12Month FROM fineart_artworks INNER JOIN fineart_lots ON faa_artwork_ID = fal_artwork_ID WHERE faa_artist_ID = {getMyArtistData['fa_artist_ID']} AND fal_lot_sale_date BETWEEN '{datetime.datetime.now().date() - datetime.timedelta(days=365)}' AND '{datetime.datetime.now().date()}';"""
        connList[1].execute(getTotalArtworkIn12MonthSelectQuery)
        getTotalArtworkIn12Month = connList[1].fetchone()
        getAverageSellingRateIn12Month = 0
        if int(getTotalArtworkSoldIn12Month['totalArtworkSoldIn12Month']) != 0:
            getAverageSellingRateIn12Month = (int(getTotalArtworkSoldIn12Month['totalArtworkSoldIn12Month'] * 100) / int(getTotalArtworkIn12Month['totalArtworkIn12Month']))
        disconnectDb(connList)
        dataList.append({'artistId': getMyArtistData['fa_artist_ID'], 'artistName': getMyArtistData['fa_artist_name'], 'totalArtworkData': getTotalArtworkData['totalArtworkData'], 'averageSellingRate': getAverageSellingRate, 'averageSellingPrice': getAverageSellingPrice['averageSellingPrice'], 'averageSellingPriceInLast12Month': getAverageSellingPriceIn12Month['averageSellingPriceIn12Month'], 'totalArtworkSoldInLast12Month': getTotalArtworkSoldIn12Month['totalArtworkSoldIn12Month'], 'averageSellingRateIn12Month': getAverageSellingRateIn12Month})
    myThreadList = []
    for getMyArtistData in getMyArtistsData:
        thread = Thread(target=dataSelector, args=(getMyArtistData, ))
        thread.start()
        myThreadList.append(thread)
    for myThread in myThreadList:
        myThread.join()
    return HttpResponse(json.dumps(dataList))


@login_required(login_url='/login/show/')
def getMyArtworksDetails(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    getMyArtworksDetailsSelectQuery = f"""SELECT DISTINCT(faa_artwork_ID) AS faa_artwork_ID, faa_artwork_title, fa_artist_name, faa_artwork_category, cah_auction_house_currency_code, fal_lot_high_estimate, fal_lot_low_estimate, fal_lot_sale_price, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_sale_price_USD, fal_lot_no, fal_lot_sale_date, faac_auction_title, cah_auction_house_name, cah_auction_house_location FROM user_favorites INNER JOIN fineart_artworks ON referenced_table_id = faa_artwork_ID INNER JOIN fineart_artists ON faa_artist_ID = fa_artist_ID INNER JOIN fineart_lots ON faa_artwork_ID = fal_artwork_ID INNER JOIN fineart_auction_calendar ON fal_auction_ID = faac_auction_ID INNER JOIN core_auction_houses ON faac_auction_house_id = cah_auction_house_ID WHERE reference_table = 'fineart_artworks' AND user_id = {request.user.id};"""
    connList = connectToDb()
    connList[1].execute(getMyArtworksDetailsSelectQuery)
    getMyArtworksDetailsData = connList[1].fetchall()
    disconnectDb(connList)
    return HttpResponse(json.dumps(getMyArtworksDetailsData, default=default))


@login_required(login_url='/login/show/')
def getFollowedArtworks(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    data = {}
    getFollowedArtworksSelectQuery = f"""SELECT COUNT(DISTINCT(referenced_table_id)) as totalFollowed FROM user_favorites INNER JOIN fineart_artworks ON referenced_table_id = faa_artwork_ID WHERE user_id = {request.user.id} AND reference_table = 'fineart_artworks'"""

    def forPaintings(followedArtworksSelectQuery):
        forPaintingsFollowed = followedArtworksSelectQuery + f""" AND faa_artwork_category = 'paintings'"""
        connList = connectToDb()
        connList[1].execute(forPaintingsFollowed)
        forPaintingsFollowedData = connList[1].fetchone()
        disconnectDb(connList)
        data['forPaintingsFollowed'] = forPaintingsFollowedData['totalFollowed']

    def forSculptures(followedArtworksSelectQuery):
        forSculpturesFollowed = followedArtworksSelectQuery + f""" AND faa_artwork_category = 'sculptures'"""
        connList = connectToDb()
        connList[1].execute(forSculpturesFollowed)
        forSculpturesFollowedData = connList[1].fetchone()
        disconnectDb(connList)
        data['forSculpturesFollowed'] = forSculpturesFollowedData['totalFollowed']

    def forPrints(followedArtworksSelectQuery):
        forPrintsFollowed = followedArtworksSelectQuery + f""" AND faa_artwork_category = 'prints'"""
        connList = connectToDb()
        connList[1].execute(forPrintsFollowed)
        forPrintsFollowedData = connList[1].fetchone()
        disconnectDb(connList)
        data['forPrintsFollowed'] = forPrintsFollowedData['totalFollowed']

    def forWorkOnPaper(followedArtworksSelectQuery):
        forWorkOnPaperFollowed = followedArtworksSelectQuery + f""" AND faa_artwork_category = 'works on paper'"""
        connList = connectToDb()
        connList[1].execute(forWorkOnPaperFollowed)
        forWorkOnPaperFollowedData = connList[1].fetchone()
        disconnectDb(connList)
        data['forWorkOnPaperFollowed'] = forWorkOnPaperFollowedData['totalFollowed']

    def forMiniatures(followedArtworksSelectQuery):
        forMiniaturesFollowed = followedArtworksSelectQuery + f""" AND faa_artwork_category = 'miniatures'"""
        connList = connectToDb()
        connList[1].execute(forMiniaturesFollowed)
        forMiniaturesFollowedData = connList[1].fetchone()
        disconnectDb(connList)
        data['forMiniaturesFollowed'] = forMiniaturesFollowedData['totalFollowed']

    def forPhotographs(followedArtworksSelectQuery):
        forPhotographsFollowed = followedArtworksSelectQuery + f""" AND faa_artwork_category = 'photographs'"""
        connList = connectToDb()
        connList[1].execute(forPhotographsFollowed)
        forPhotographsFollowedData = connList[1].fetchone()
        disconnectDb(connList)
        data['forPhotographsFollowed'] = forPhotographsFollowedData['totalFollowed']

    threadForPaintings = Thread(target=forPaintings, args=(getFollowedArtworksSelectQuery, ))
    threadForPaintings.start()
    threadForSculptures = Thread(target=forSculptures, args=(getFollowedArtworksSelectQuery,))
    threadForSculptures.start()
    threadForPrints = Thread(target=forPrints, args=(getFollowedArtworksSelectQuery,))
    threadForPrints.start()
    threadForWorkOnPaper = Thread(target=forWorkOnPaper, args=(getFollowedArtworksSelectQuery,))
    threadForWorkOnPaper.start()
    threadForMiniatures = Thread(target=forMiniatures, args=(getFollowedArtworksSelectQuery,))
    threadForMiniatures.start()
    threadForPhotographs = Thread(target=forPhotographs, args=(getFollowedArtworksSelectQuery,))
    threadForPhotographs.start()
    connList = connectToDb()
    connList[1].execute(getFollowedArtworksSelectQuery)
    totalFollowedData = connList[1].fetchone()
    disconnectDb(connList)
    data['user_artwork_followed_counts'] = totalFollowedData['totalFollowed']
    threadForPaintings.join()
    threadForSculptures.join()
    threadForPrints.join()
    threadForWorkOnPaper.join()
    threadForMiniatures.join()
    threadForPhotographs.join()
    # data = {'user_artwork_followed_counts': totalFollowedData['totalFollowed'], 'forPaintingsFollowed': forPaintingsFollowedData['totalFollowed'], 'forSculpturesFollowed': forSculpturesFollowedData['totalFollowed'], 'forPrintsFollowed': forPrintsFollowedData['totalFollowed'], 'forWorkOnPaperFollowed': forWorkOnPaperFollowedData['totalFollowed'], 'forPhotographsFollowed': forPhotographsFollowedData['totalFollowed'], 'forMiniaturesFollowed': forMiniaturesFollowedData['totalFollowed']}
    return HttpResponse(json.dumps(data))


def signup(request):
    if request.method == 'POST':
        context = {}
        username = request.POST.get('username').strip()
        email = request.POST.get('emailid').strip()
        raw_password = request.POST.get('password1').strip()
        password2 = request.POST.get('password2').strip()
        # Validate user inputs here...
        if username == "":
            return HttpResponse(json.dumps({'error': 'Username cannot be empty string'}))
        emailPattern = re.compile("^\w+\.?\w*@\w+\.\w{3,4}$")
        eps = re.search(emailPattern, email)
        if not eps:
            return HttpResponse(json.dumps({'error': 'Email entered is not valid'}))
        if raw_password != password2:
            return HttpResponse(json.dumps({'error': 'Passwords do not match'}))
        try:
            newuser = djUser.objects.create_user(username=username, email=email, password=raw_password)
            user = authenticate(username=username, password=raw_password)
            login(request, user)
        except:
            return HttpResponse(json.dumps({'error': sys.exc_info()[1].__str__()}))
        return HttpResponse(json.dumps({'error': ''}))  # Later this should be changed to 'profile' as we want the user to go to the user's profile page after login.
    else:
        context = {}
    return render(request, 'registration.html', context)


@csrf_exempt
def dologin(request):
    if request.method == 'POST':
        context = {}
        username = request.POST.get('username')
        raw_password = request.POST.get('passwd')
        user = authenticate(username=username, password=raw_password)
        print(user)
        if user is not None:
            login(request, user)
        else:
            return HttpResponse(None)
        return HttpResponseRedirect("/login/index/")  # Later this should be changed to 'profile' as we want the user to go to the user's profile page after login.
    else:
        return HttpResponse("Invalid request method")


def dologout(request):
    logout(request)
    return HttpResponseRedirect("/login/index/")


@login_required(login_url='/login/show/')
def showprofile(request):
    context = {}
    return render(request, 'profile.html', context)


def checkloginstatus(request):
    if request.user.is_authenticated:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

    # @cache_page(CACHE_TTL)


def about(request):
    if request.method == 'GET':
        """
        wcqset = WebConfig.objects.filter(paramname="About")
        #wcqset = WebConfig.objects.filter(path="/about/")
        wcobj = None
        if wcqset.__len__() > 0:
            wcobj = wcqset[0]
        context = {'aboutcontent' : ''}
        if wcobj is not None:
            context['aboutcontent'] = wcobj.paramvalue
            context['aboutid'] = wcobj.id
        carouselentries = getcarouselinfo()
        context['carousel'] = carouselentries
        """
        context = {'aboutcontent': ''}
        if request.user.is_authenticated and request.user.is_staff:
            context['adminuser'] = 1
        else:
            context['adminuser'] = 0
        template = loader.get_template('about.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Incorrect request method")


# @cache_page(CACHE_TTL)
def contactus(request):
    if request.method == 'GET':
        """
        wcqset = WebConfig.objects.filter(paramname="ContactUs")
        #wcqset = WebConfig.objects.filter(path="/contactus/")
        wcobj = None
        if wcqset.__len__() > 0:
            wcobj = wcqset[0]
        context = {'contactus' : ''}
        if wcobj is not None:
            context['contactus'] = wcobj.paramvalue
            context['contactid'] = wcobj.id
        carouselentries = getcarouselinfo()
        context['carousel'] = carouselentries
        """
        context = {'contactus': ''}
        if request.user.is_authenticated and request.user.is_staff:
            context['adminuser'] = 1
        else:
            context['adminuser'] = 0
        template = loader.get_template('contactus.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Incorrect request method")


@login_required(login_url="/login/show/")
def followartist(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'msg': 0, 'div_id': '', 'aid': ''}))  # Operation failed!
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'msg': 0, 'div_id': '', 'aid': ''}))  # Operation failed!
    userobj = request.user
    sessionkey = request.session.session_key
    aid, divid = None, None
    requestbody = str(request.body)
    bodycomponents = requestbody.split("&")
    requestdict = {}
    for comp in bodycomponents:
        compparts = comp.split("=")
        if compparts.__len__() > 1:
            compparts[0] = compparts[0].replace("b'", "")
            requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
    if 'aid' in requestdict.keys():
        aid = requestdict['aid']
    if 'div_id' in requestdict.keys():
        divid = requestdict['div_id'].replace("'", "")
    if not aid or not divid:
        return HttpResponse(json.dumps({'msg': 0, 'div_id': '', 'aid': ''}))  # Operation failed!
    artist = None
    try:
        artist = Artist.objects.get(id=aid)
    except:
        return HttpResponse(
            json.dumps({'msg': 0, 'div_id': divid, 'aid': aid}))  # Operation failed! Can't proceed without an artist.
    # Check if there is any existing record for this artist/user combination 
    follow = None
    try:
        follow = Follow.objects.get(artist=artist, user=request.user)
    except:
        pass
    if not follow:
        follow = Follow()
    follow.artist = artist
    follow.user = userobj
    follow.user_session_key = sessionkey
    follow.status = True  # Explicitly set it True, just in case we had an existing record with a False value.
    try:
        follow.save()
        return HttpResponse(json.dumps({'msg': 1, 'div_id': divid, 'aid': aid}))  # Successfully following...
    except:
        return HttpResponse(json.dumps({'msg': 0, 'div_id': divid, 'aid': aid}))  # Failed again.


@login_required(login_url="/login/show/")
def unfollowartist(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'msg': 0, 'div_id': '', 'aid': ''}))  # Operation failed!
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'msg': 0, 'div_id': '', 'aid': ''}))  # Operation failed!
    userobj = request.user
    sessionkey = request.session.session_key
    aid, divid = None, None
    requestbody = str(request.body)
    bodycomponents = requestbody.split("&")
    requestdict = {}
    for comp in bodycomponents:
        compparts = comp.split("=")
        if compparts.__len__() > 1:
            compparts[0] = compparts[0].replace("b'", "")
            requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
    if 'aid' in requestdict.keys():
        aid = requestdict['aid']
    if 'div_id' in requestdict.keys():
        divid = requestdict['div_id'].replace("'", "")
    if not aid or not divid:
        return HttpResponse(json.dumps({'msg': 0, 'div_id': '', 'aid': ''}))  # Operation failed!
    artist = None
    try:
        artist = Artist.objects.get(id=aid)
    except:
        return HttpResponse(json.dumps({'msg': 0, 'div_id': divid, 'aid': aid}))  # Operation failed! Can't proceed without an artist.
    followqset = Follow.objects.filter(artist=artist, user=request.user)
    follow = None
    if followqset.__len__() > 0:
        follow = followqset[0]
    else:
        return HttpResponse(json.dumps({'msg': 0, 'div_id': divid, 'aid': aid}))  # The user was not following this artist.
    follow.status = False  # This means user left the artist.
    follow.user_session_key = sessionkey
    try:
        follow.save()
        return HttpResponse(json.dumps({'msg': 1, 'div_id': divid, 'aid': aid}))  # Successfully left...
    except:
        return HttpResponse(json.dumps({'msg': 0, 'div_id': divid, 'aid': aid}))  # Failed again.


@login_required(login_url="/login/show/")
def morefollows(request):
    if request.method != 'GET':
        return HttpResponse(json.dumps({'msg': 0, 'aid': ''}))  # Operation failed!
    page = 1
    if 'page' in request.GET.keys():
        page = request.GET['page']
    cols = 4
    rows = 5
    startctr = int(page) * rows * cols - rows * cols
    endctr = int(page) * rows * cols
    followqset = Follow.objects.filter(user=request.user).order_by("-updatedon")[startctr:endctr]
    follow = None
    followsdict = {}
    context = {}
    for follow in followqset:
        artist = follow.artist
        artistname = artist.artistname
        aimg = settings.IMG_URL_PREFIX + str(artist.artistimage)
        anat = artist.nationality
        aid = artist.id
        about = artist.description
        followsdict[artistname] = [about, aimg, anat, aid]
    context['follows'] = followsdict
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
    context['pages'] = {'prevpage': prevpage, 'nextpage': nextpage, 'firstpage': firstpage,
                        'displayedprevpage1': displayedprevpage1, 'displayedprevpage2': displayedprevpage2,
                        'displayednextpage1': displayednextpage1, 'displayednextpage2': displayednextpage2,
                        'currentpage': int(page)}
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('morefollows.html')
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login/show/")
def morefavourites(request):
    if request.method != 'GET':
        return HttpResponse(json.dumps({'msg': 0, 'aid': ''}))  # Operation failed!
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/index/")
    page = 1
    if 'page' in request.GET.keys():
        page = request.GET['page']
    cols = 4
    rows = 5
    startctr = int(page) * rows * cols - rows * cols
    endctr = int(page) * rows * cols
    favouritesdict = {}
    context = {}
    favsqset = Favourite.objects.filter(user=request.user).order_by("-updated")[startctr:endctr]
    for fav in favsqset:
        favtype = fav.reference_model
        if favtype == "fineart_artists":
            favmodelid = fav.reference_model_id
            try:
                artist = Artist.objects.get(id=favmodelid)
                artistname = artist.artistname
                aimg = settings.IMG_URL_PREFIX + str(artist.artistimage)
                anat = artist.nationality
                aid = artist.id
                about = artist.description
                favouritesdict[artistname] = ["artist", aimg, anat, aid, about]
            except:
                pass
        elif favtype == "fineart_artworks":
            favmodelid = fav.reference_model_id
            try:
                artwork = Artwork.objects.get(id=favmodelid)
                artworkname = artwork.artworkname
                artist_id = artwork.artist_id
                artworkimg = settings.IMG_URL_PREFIX + str(artwork.image1)
                size = artwork.sizedetails
                medium = artwork.medium
                awid = artwork.id
                artist = Artist.objects.get(id=artist_id)
                artistname = artist.artistname
                favouritesdict[artworkname] = ["artwork", artworkimg, size, medium, artistname, awid, artist_id]
            except:
                pass
        elif favtype == "fineart_auction_calendar":
            favmodelid = fav.reference_model_id
            try:
                auction = Auction.objects.get(id=favmodelid)
                auctionname = auction.auctionname
                period = auction.auctionstartdate.strftime("%d %b, %Y")
                aucenddate = auction.auctionenddate
                if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                    period = period + " - " + str(aucenddate)
                auchouseid = auction.auctionhouse_id
                auchouseobj = AuctionHouse.objects.get(id=auchouseid)
                housename = auchouseobj.housename
                aucid = auction.id
                aucimg = settings.IMG_URL_PREFIX + str(auction.coverimage)
                favouritesdict[auctionname] = ["auction", period, housename, aucid, aucimg, auchouseid]
            except:
                pass
    context['favourites'] = favouritesdict
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
    context['pages'] = {'prevpage': prevpage, 'nextpage': nextpage, 'firstpage': firstpage,
                        'displayedprevpage1': displayedprevpage1, 'displayedprevpage2': displayedprevpage2,
                        'displayednextpage1': displayednextpage1, 'displayednextpage2': displayednextpage2,
                        'currentpage': int(page)}
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    context['username'] = ""
    if request.user.is_authenticated:
        context['username'] = request.user.username
    template = loader.get_template('morefavourites.html')
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login/show/")
def dashboard(request):
    if request.method != 'GET':
        return HttpResponse(json.dumps({'err': 'Invalid method of call'}))  # Operation failed!
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/index/")
        # return HttpResponse(json.dumps({'err' : 'Your login session has expired',})) # Operation failed!
    userobj = request.user
    sessionkey = request.session.session_key
    context = dict()
    # page = 1
    # if 'page' in request.GET.keys():
    #     try:
    #         page = int(request.GET['page'])
    #     except:
    #         pass
    # chunksize = 10 # per page we will show 10 artists and artworks that the user has added as favourites.
    # startctr = page * chunksize - chunksize
    # endctr = page * chunksize
    # favourite_artworks = []
    # favourite_artists = []
    # favourite_auctions = []
    # artistsidlist = []
    # artworksidlist = []
    # auctionsidlist = []
    # artwork_type_counts = {'painting' : 0, 'sculpture' : 0, 'print' : 0, 'workonpaper' : 0}
    # context = {}
    # totalfavouriteartists = 0
    # favouriteartistscurweek = 0
    # totalfavouriteartworks = 0
    # favouriteartworkscurweek = 0
    # totalfavouriteauctions = 0
    # favouriteauctionscurweek = 0
    # curdate = datetime.datetime.now()
    # datelastweek = curdate - datetime.timedelta(days=7)
    # connlist = connecttoDB()
    # dbconn, cursor = connlist[0], connlist[1]
    # allfavouritesqset = Favourite.objects.filter(user=userobj).order_by("-updated")
    # for fav in allfavouritesqset:
    #     favtype = fav.reference_model
    #     if favtype == "fineart_artists":
    #         favmodelid = fav.reference_model_id
    #         artistsidlist.append(favmodelid)
    #         totalfavouriteartists += 1
    #         if fav.created > datelastweek:
    #             favouriteartistscurweek += 1
    #     elif favtype == "fineart_artworks":
    #         favmodelid = fav.reference_model_id
    #         artworksidlist.append(favmodelid)
    #         totalfavouriteartworks += 1
    #         if fav.created > datelastweek:
    #             favouriteartworkscurweek += 1
    #     elif favtype == "fineart_auction_calendar":
    #         favmodelid = fav.reference_model_id
    #         auctionsidlist.append(favmodelid)
    #         totalfavouriteauctions += 1
    #         if fav.created > datelastweek:
    #             favouriteauctionscurweek += 1
    # favartistsqset = Artist.objects.filter(id__in=artistsidlist)
    # favartworksqset = Artwork.objects.filter(id__in=artworksidlist)
    # favauctionsqset = Auction.objects.filter(id__in=auctionsidlist)
    # for favartist in favartistsqset:
    #     favartistid = favartist.id
    #     # Get all artworks by this artist
    #     lotartistqset = LotArtist.objects.filter(artist_id=favartistid)
    #     artistartworkcount = list(lotartistqset).__len__()
    #     curdate = datetime.datetime.now()
    #     datenow = datetime.date(curdate.year, curdate.month,curdate.day)
    #     date12monthsago = datenow - datetime.timedelta(days=365)
    #     artworksoldlast12months = 0
    #     artworksoldtotal = 0
    #     totalsoldusd = 0.00
    #     totalsoldusdlast12months = 0.00
    #     artistname = ''
    #     for lotartist in lotartistqset:
    #         if lotartist.saledate > date12monthsago:
    #             artworksoldlast12months += 1
    #             try:
    #                 totalsoldusdlast12months += float(lotartist.artist_price_usd)
    #             except:
    #                 pass
    #         if lotartist.lotstatus == "sold":
    #             artworksoldtotal += 1
    #             try:
    #                 totalsoldusd += float(lotartist.artist_price_usd)
    #             except:
    #                 pass
    #         artistname = lotartist.artist_name
    #     sellingratefloat = 'NA'
    #     if float(artistartworkcount ) > 0:
    #         sellingratefloat = "{:.3f}".format(artworksoldtotal/artistartworkcount)
    #     avgsalepricefloat = 'NA'
    #     if float(artworksoldtotal) > 0:
    #         avgsalepricefloat = "{:.2f}".format(totalsoldusd/artworksoldtotal)
    #     avgsalepricelast12monthsfloat = 'NA'
    #     if float(artworksoldlast12months) > 0:
    #         avgsalepricelast12monthsfloat = "{:.2f}".format(totalsoldusdlast12months/artworksoldlast12months)
    #     d = {'totalartworks' : artistartworkcount, 'artistname' : artistname, 'artistid' : favartistid, 'totalartworkssold' : artworksoldtotal, 'artworkssoldlast12months' : artworksoldlast12months, 'sellingrate' : sellingratefloat, 'avgsaleprice' : avgsalepricefloat, 'avgsalepricelast12months' : avgsalepricelast12monthsfloat}
    #     favourite_artists.append(d)
    # for favartwork in favartworksqset:
    #     artworkname = favartwork.artworkname
    #     artworkid = favartwork.id
    #     medium = favartwork.medium
    #     if favartwork.category == "paintings":
    #         artwork_type_counts['painting'] += 1
    #     elif favartwork.category == "works on paper":
    #         artwork_type_counts['workonpaper'] += 1
    #     elif favartwork.category == "prints":
    #         artwork_type_counts['print'] += 1
    #     elif favartwork.category == "sculptures":
    #         artwork_type_counts['sculpture'] += 1
    #     sizedetails = favartwork.sizedetails
    #     artworkimage = ""
    #     if favartwork.image1 is not None:
    #         artworkimage = settings.IMG_URL_PREFIX + str(favartwork.image1)
    #     lotqset = LotArtist.objects.filter(artworkid=artworkid)
    #     lowestimateusd, highestimateusd, soldpriceusd = 0.00, 0.00, 0.00
    #     artistname = ""
    #     if list(lotqset).__len__() > 0:
    #         try:
    #             lowestimateusd = float(lotqset[0].lowestimate)
    #         except:
    #             pass
    #         try:
    #             highestimateusd = float(lotqset[0].highestimate)
    #         except:
    #             pass
    #         try:
    #             soldpriceusd = float(lotqset[0].artist_price_usd)
    #         except:
    #             pass
    #         artistname = lotqset[0].artist_name
    #     d = {'artworkname' : artworkname, 'artistname' : artistname, 'artworkid' : artworkid, 'medium' : medium, 'size' : sizedetails, 'lowestimate' : lowestimateusd, 'highestimate' : highestimateusd, 'soldprice' : soldpriceusd, 'artworkimage' : artworkimage}
    #     favourite_artworks.append(d)
    # for favauction in favauctionsqset:
    #     auctionname = favauction.auctionname
    #     auctionperiod = favauction.auctionstartdate.strftime('%d %b, %Y')
    #     if type(favauction.auctionenddate) is datetime.date and favauction.auctionenddate.strftime('%d %b, %Y') != "01 Jan, 0001" and favauction.auctionenddate.strftime('%d %b, %Y') != "01 Jan, 1":
    #         auctionperiod += " - " + favauction.auctionenddate.strftime('%d %b, %Y')
    #     lotcount = favauction.lotcount
    #     coverimage = favauction.coverimage
    #     auchouseobj = AuctionHouse.objects.get(id=favauction.auctionhouse_id) # This is a relatively smaller table, so querying it while iterating favourite auctions shouldn't take much time.
    #     auctionhousename = auchouseobj.housename
    #     d = {'auctionname' : auctionname, 'auctionperiod' : auctionperiod, 'lotcount' : lotcount, 'auctionhousename' : auctionhousename, 'auctionid' : favauction.id}
    #     favourite_auctions.append(d)
    # emailalerts = []
    # emailalerts_artist = 0
    # emailalerts_artwork = 0
    # try:
    #     emailalertsqset = EmailAlerts.objects.filter(user=userobj)
    #     for emailalertobj in emailalertsqset:
    #         d = {'emailcontent' : emailalertobj.emailcontent, 'emaildate' : emailalertobj.emaildate, 'emailstatus' : emailalertobj.sendstatus, 'emailtype' : emailalertobj.emailtype}
    #         emailalerts.append(d)
    #         if emailalertobj.emailtype == 'artist':
    #             emailalerts_artist += 1
    #         elif emailalertobj.emailtype == 'artwork':
    #             emailalerts_artwork += 1
    #         else:
    #             pass
    # except:
    #     pass
    # cursor.close()
    # dbconn.close()
    # context['favourite_artists'] = favourite_artists
    # context['favourite_artworks'] = favourite_artworks
    # context['artwork_type_counts'] = artwork_type_counts
    # context['favourite_auctions'] = favourite_auctions
    # context['totalfavouriteartists'] = totalfavouriteartists
    # context['favouriteartistscurweek'] = favouriteartistscurweek
    # context['totalfavouriteartworks'] = totalfavouriteartworks
    # context['favouriteartworkscurweek'] = favouriteartworkscurweek
    # context['totalfavouriteauctions'] = totalfavouriteauctions
    # context['favouriteauctionscurweek'] = favouriteauctionscurweek
    # context['emailalerts'] = emailalerts
    # context['emailalerts_artwork'] = emailalerts_artwork
    # context['emailalerts_artist'] = emailalerts_artist
    context['username'] = userobj.username
    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login/show/")
def notifications(request):
    if request.method != 'GET':
        return HttpResponse(json.dumps({'err': 'Invalid method of call', }))  # Operation failed!
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/index/")
        # return HttpResponse(json.dumps({'err' : 'Your login session has expired',})) # Operation failed!
    userobj = request.user
    sessionkey = request.session.session_key
    context = {}
    # Add page specific code here
    context['username'] = userobj.username
    template = loader.get_template('notifications.html')
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login/show/")
def acctsettings(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/index/")
        # return HttpResponse(json.dumps({'err' : 'Your login session has expired',})) # Operation failed!
    userobj = request.user
    sessionkey = request.session.session_key
    context = {}
    # Add page specific code here
    context['username'] = userobj.username
    if request.method == 'GET':
        template = loader.get_template('account_settings.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':  # User is trying to save account settings
        pass
