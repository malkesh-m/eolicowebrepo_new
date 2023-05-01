from django.shortcuts import render
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
from django.template import loader

import os, sys, re, time, datetime
import simplejson as json
import redis
import pickle
import MySQLdb
# from gallery.models import Gallery, Event
from login.models import User, Session, Favourite  # ,WebConfig, Carousel, Follow
from login.views import getcarouselinfo_new
# from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse
from artists.models import Artist, Artwork, LotArtist
from eolicowebsite.utils import connecttoDB, disconnectDB, connectToDb, disconnectDb

# Caching related imports and variables
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def getpredictivehints(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    filterauctionhouses = []
    uniqauctionhouses = {}
    try:
        filterauctionhouses = pickle.loads(redis_instance.get('ah_filterauctionhouses'))
    except:
        filterauctionhouses = []
    if filterauctionhouses.__len__() == 0:
        auctionhousesqset = AuctionHouse.objects.all()
        for auctionhouse in auctionhousesqset:
            if auctionhouse.housename not in uniqauctionhouses.keys():
                auchousename = auctionhouse.housename
                filterauctionhouses.append(auchousename)
                uniqauctionhouses[auchousename] = 1
        try:
            redis_instance.set('ah_filterauctionhouses', pickle.dumps(filterauctionhouses))
        except:
            pass
    message = json.dumps(filterauctionhouses)
    return HttpResponse(message)


# @cache_page(CACHE_TTL)
def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    page = ""
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 100
    rows = 12
    context = {}
    auctionhouses = []  # Auctions in various auction houses section.
    uniqueauctions = {}
    connlist = connecttoDB()
    dbconn, cursor = connlist[0], connlist[1]
    try:
        auctionhouses = pickle.loads(redis_instance.get('ah_auctionhouses'))
    except:
        auctionhouses = []
    if auctionhouses.__len__() == 0:
        auctionhousesqset = AuctionHouse.objects.all()
        uniqauctionhouses = {}
        auctionhousepatterns = [re.compile("sotheby\'?s\,", re.IGNORECASE | re.DOTALL),
                                re.compile("artcurial", re.IGNORECASE | re.DOTALL),
                                re.compile("china\s+guardian", re.IGNORECASE | re.DOTALL),
                                re.compile("christie\'?s", re.IGNORECASE | re.DOTALL),
                                re.compile("bonham\'?s", re.IGNORECASE | re.DOTALL),
                                re.compile("doyle", re.IGNORECASE | re.DOTALL),
                                re.compile("phillips", re.IGNORECASE | re.DOTALL),
                                re.compile("dorotheum", re.IGNORECASE | re.DOTALL),
                                re.compile("poly\s+international", re.IGNORECASE | re.DOTALL),
                                re.compile("tajan", re.IGNORECASE | re.DOTALL)]
        showcounts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for auctionhouse in auctionhousesqset:
            if auctionhouse.housename not in uniqauctionhouses.keys():
                uniqauctionhouses[auctionhouse.housename] = 1
            if page != "":
                if not auctionhouse.housename.startswith(page) and not auctionhouse.housename.startswith(page.upper()):
                    continue
            auchousepass = False
            patternindex = 0
            for auchousepattern in auctionhousepatterns:
                if re.search(auchousepattern, auctionhouse.housename):
                    auchousepass = True
                    break
                patternindex += 1
            if auchousepass == False:  # Auction houses that are not in our featured auctionhousenames would be skipped.
                continue
            if showcounts[patternindex] > 0:  # We show a maximum of 1 branches of an auction house.
                continue
            showcounts[patternindex] += 1
            coverimage = ""
            if patternindex == 0:
                coverimage = "/static/images/auctionhouses/Sotheby-logo.jpg"
            elif patternindex == 1:
                coverimage = "/static/images/auctionhouses/Artcurial-logo.png"
            elif patternindex == 2:
                coverimage = "/static/images/auctionhouses/ChinaGuardian-logo.jpg"
            elif patternindex == 3:
                coverimage = "/static/images/auctionhouses/Christies-logo.png"
            elif patternindex == 4:
                coverimage = "/static/images/auctionhouses/Bonhams-logo.png"
            elif patternindex == 5:
                coverimage = "/static/images/auctionhouses/doyle-logo.jpg"
            elif patternindex == 6:
                coverimage = "/static/images/auctionhouses/Phillips-logo.png"
            elif patternindex == 7:
                coverimage = "/static/images/auctionhouses/Dorotheum-logo.png"
            elif patternindex == 8:
                coverimage = "/static/images/auctionhouses/PolyInternational-logo.png"
            elif patternindex == 9:
                coverimage = "/static/images/auctionhouses/Tajan-logo.png"
            else:
                coverimage = "/static/images/auctionhouses/"
            d = {'housename': auctionhouse.housename, 'houseurl': auctionhouse.houseurl, 'description': '',
                 'coverimage': coverimage, 'ahid': auctionhouse.id, 'location': auctionhouse.location}
            auctionhouses.append(d)
        try:
            redis_instance.set('ah_auctionhouses', pickle.dumps(auctionhouses))
        except:
            pass
    context['auctionhouses'] = auctionhouses
    cursor.close()
    dbconn.close()
    # carouselentries = getcarouselinfo_new()
    # context['carousel'] = carouselentries
    userDict = request.session.get('user')
    if userDict:
        context['username'] = userDict['username']
    template = loader.get_template('auctionhouses.html')
    return HttpResponse(template.render(context, request))


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.strftime("%d %b, %Y")


def getFeaturedAuctionHouses(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    else:
        keyword = request.GET.get('keyword')
        if keyword:
            try:
                filterAuctionHousesData = pickle.loads(redis_instance.get(f'filterAuctionHousesData{keyword}'))
            except:
                filterAuctionHousesData = []
            if len(filterAuctionHousesData) == 0:
                filterAuctionHousesSelectQuery = f"""SELECT cah_auction_house_ID, cah_auction_house_name, cah_auction_house_location FROM core_auction_houses WHERE cah_auction_house_name LIKE '%{keyword}%' ORDER BY cah_auction_house_name;"""
                connList = connectToDb()
                connList[1].execute(filterAuctionHousesSelectQuery)
                filterAuctionHousesData = connList[1].fetchall()
                disconnectDb(connList)
                redis_instance.set(f'filterAuctionHousesData{keyword}', pickle.dumps(filterAuctionHousesData))
            return HttpResponse(json.dumps(filterAuctionHousesData, default=default))
        else:
            try:
                featuredAuctionHousesData = pickle.loads(redis_instance.get('featuredAuctionHouseData'))
            except:
                featuredAuctionHousesData = []
            if len(featuredAuctionHousesData) == 0:
                featuredAuctionHousesSelectQuery = f"""SELECT cah_auction_house_ID, cah_auction_house_name, cah_auction_house_location FROM core_auction_houses WHERE cah_auction_house_ID = 1 OR cah_auction_house_ID = 27 OR cah_auction_house_ID = 36 OR cah_auction_house_ID = 78 OR cah_auction_house_ID = 80 OR cah_auction_house_ID = 560 OR cah_auction_house_ID = 952 OR cah_auction_house_ID = 1076 OR cah_auction_house_ID = 1479 OR cah_auction_house_ID = 1481;"""
                connList = connectToDb()
                connList[1].execute(featuredAuctionHousesSelectQuery)
                featuredAuctionHousesData = connList[1].fetchall()
                disconnectDb(connList)
                for featuredAuctionHouseData in featuredAuctionHousesData:
                    if featuredAuctionHouseData['cah_auction_house_ID'] == 1:
                        featuredAuctionHouseData[
                            'cah_auction_house_image'] = "/static/images/auctionhouses/Phillips-logo.png"
                    if featuredAuctionHouseData['cah_auction_house_ID'] == 27:
                        featuredAuctionHouseData[
                            'cah_auction_house_image'] = "/static/images/auctionhouses/Christies-logo.png"
                    if featuredAuctionHouseData['cah_auction_house_ID'] == 36:
                        featuredAuctionHouseData[
                            'cah_auction_house_image'] = "/static/images/auctionhouses/Sotheby-logo.jpg"
                    if featuredAuctionHouseData['cah_auction_house_ID'] == 78:
                        featuredAuctionHouseData['cah_auction_house_image'] = "/static/images/auctionhouses/doyle-logo.jpg"
                    if featuredAuctionHouseData['cah_auction_house_ID'] == 80:
                        featuredAuctionHouseData[
                            'cah_auction_house_image'] = "/static/images/auctionhouses/Dorotheum-logo.png"
                    if featuredAuctionHouseData['cah_auction_house_ID'] == 560:
                        featuredAuctionHouseData[
                            'cah_auction_house_image'] = "/static/images/auctionhouses/Bonhams-logo.png"
                    if featuredAuctionHouseData['cah_auction_house_ID'] == 952:
                        featuredAuctionHouseData['cah_auction_house_image'] = "/static/images/auctionhouses/Tajan-logo.png"
                    if featuredAuctionHouseData['cah_auction_house_ID'] == 1076:
                        featuredAuctionHouseData[
                            'cah_auction_house_image'] = "/static/images/auctionhouses/Artcurial-logo.png"
                    if featuredAuctionHouseData['cah_auction_house_ID'] == 1479:
                        featuredAuctionHouseData[
                            'cah_auction_house_image'] = "/static/images/auctionhouses/ChinaGuardian-logo.jpg"
                    if featuredAuctionHouseData['cah_auction_house_ID'] == 1481:
                        featuredAuctionHouseData[
                            'cah_auction_house_image'] = "/static/images/auctionhouses/PolyInternational-logo.png"
                redis_instance.set('featuredAuctionHouseData', pickle.dumps(featuredAuctionHousesData))
            return HttpResponse(json.dumps(featuredAuctionHousesData, default=default))


def getAuctionHouses(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    else:
        try:
            auctionHousesData = pickle.loads(redis_instance.get('auctionHousesData'))
        except:
            auctionHousesData = []
        if len(auctionHousesData) == 0:
            auctionHousesSelectQuery = """SELECT * FROM core_auction_houses;"""
            connList = connectToDb()
            connList[1].execute(auctionHousesSelectQuery)
            auctionHousesData = connList[1].fetchall()
            disconnectDb(connList)
            redis_instance.set('auctionHousesData', pickle.loads(auctionHousesData))
        return HttpResponse(json.dumps(auctionHousesData, default=default))


def getCurrentAuctionHouse(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    auctionHouseId = request.GET.get('ahid')
    try:
        currentAuctionHouseData = pickle.loads(redis_instance.get(f'currentAuctionHouseData{auctionHouseId}'))
    except:
        currentAuctionHouseData = []
    if len(currentAuctionHouseData) == 0:
        currentAuctionHousesSelectQuery = f"""SELECT cah_auction_house_name, cah_auction_house_ID FROM core_auction_houses WHERE cah_auction_house_ID = {auctionHouseId}"""
        connList = connectToDb()
        connList[1].execute(currentAuctionHousesSelectQuery)
        currentAuctionHouseData = connList[1].fetchone()
        disconnectDb(connList)
        redis_instance.set(f'currentAuctionHouseData{auctionHouseId}', pickle.dumps(currentAuctionHouseData))
    return HttpResponse(json.dumps(currentAuctionHouseData, default=default))


# def getPastAuctionData(request):
#     if request.method != 'GET':
#         return HttpResponse("Invalid method of call")
#     auctionHouseName = request.GET.get('auctionHouseName')
#     start = request.GET.get('start')
#     limit = request.GET.get('limit')
#     pastAuctionSelectQuery = f"""SELECT faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_image, faac_auction_start_date, cah_auction_house_name, cah_auction_house_location FROM `fineart_auction_calendar` INNER JOIN `core_auction_houses` ON fineart_auction_calendar.faac_auction_house_ID = core_auction_houses.cah_auction_house_ID WHERE cah_auction_house_name = '{auctionHouseName}'"""
#     whereClauseAndOrderBy = pastUpcomigAuctionQueryMaker(request)
#     pastAuctionSelectQuery += whereClauseAndOrderBy + f"""LIMIT {limit} OFFSET {start}"""
#     connList = connectToDb()
#     connList[1].execute(pastAuctionSelectQuery)
#     pastAuctionData = connList[1].fetchall()
#     disconnectDb(connList)
#     return HttpResponse(json.dumps(pastAuctionData, default=default))


# @cache_page(CACHE_TTL)
def index_old(request):
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
    fstartctr = int(page) * chunksize - chunksize
    fendctr = int(page) * chunksize
    context = {}
    auctionhouses = []  # Auctions in various auction houses section.
    filterauctionhouses = []
    maxauctionsperhouse = 4
    maxfeaturedauctionsperhouse = 4
    maxfeaturedshows = 8
    featuredshowscutoffdate = datetime.datetime.now() - datetime.timedelta(
        days=2 * 365)  # date of 2 year back in time. TODO: This should be changed to 3 months later during deployment.
    featuredshows = []  # Featured shows section, will show 5 top priority auctions only.
    currentmngshows = {}  # Current museum and gallery shows section - keys are auction houses, values are list of priority auctions in each house. Will need association of auctions to galleries and museums, which is to be implemented later.
    uniqueauctions = {}
    connlist = connecttoDB()
    dbconn, cursor = connlist[0], connlist[1]
    try:
        filterauctionhouses = pickle.loads(redis_instance.get('ah_filterauctionhouses'))
        auctionhouses = pickle.loads(redis_instance.get('ah_auctionhouses'))
        featuredshows = pickle.loads(redis_instance.get('ah_featuredshows'))
    except:
        filterauctionhouses = []
        auctionhouses = []
        featuredshows = []
    if auctionhouses.__len__() == 0:
        auctionhousesqset = AuctionHouse.objects.all()  # .order_by('-priority')
        if auctionhousesqset.__len__() <= fstartctr:
            fstartctr = 0
        auctionhouseidslist = []
        auctionhouseidsstr = ""
        for auctionhouse in auctionhousesqset:
            auchouseid = str(auctionhouse.id)
            auctionhouseidslist.append(auchouseid)
        # print(auctionhouseidslist)
        auctionhouseidsstr = "(" + ",".join(auctionhouseidslist) + ")"
        auctionhouseauctionsdict = {}
        auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar where faac_auction_house_ID in %s order by faac_auction_start_date desc limit 100" % (
            auctionhouseidsstr)
        # print(auctionsql)
        cursor.execute(auctionsql)
        auctionsqset = cursor.fetchall()
        for auction in auctionsqset:
            auctionhouseid = auction[3]
            # print(auctionhouseid)
            if str(auctionhouseid) in auctionhouseauctionsdict.keys():
                auctionslist = auctionhouseauctionsdict[str(auctionhouseid)]
                if auctionslist.__len__() < maxauctionsperhouse:  # We won't keep more than 'maxauctionsperhouse' records per house.
                    auctionslist.append(auction)
                    auctionhouseauctionsdict[str(auctionhouseid)] = auctionslist
                else:
                    pass
            else:
                auctionslist = [auction, ]
                auctionhouseauctionsdict[str(auctionhouseid)] = auctionslist
        # print(auctionhouseauctionsdict.keys())
        for auctionhouse in auctionhousesqset[fstartctr:]:
            try:
                auctionsqset = auctionhouseauctionsdict[str(auctionhouse.id)]
            except:  # We found a auction house reference in auction model that doesn't exist in auctionhouse model
                continue
            coverimage = ""
            if auctionsqset.__len__() > 0:
                coverimage = settings.IMG_URL_PREFIX + str(auctionsqset[0][8])
            d = {'housename': auctionhouse.housename, 'houseurl': auctionhouse.houseurl, 'description': '',
                 'image': coverimage, 'ahid': auctionhouse.id, 'location': auctionhouse.location}
            auctionslist = []
            for auction in auctionsqset:
                auctionperiod = ""
                if auction[5].strftime("%d %b, %Y") != "01 Jan, 0001" and auction[5].strftime(
                        "%d %b, %Y") != "01 Jan, 1":
                    auctionperiod = auction[5].strftime("%d %b, %Y")
                    aucenddate = auction[6]
                    if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                        auctionperiod += " - " + str(aucenddate)
                d1 = {'auctionname': auction[1], 'coverimage': settings.IMG_URL_PREFIX + str(auction[8]),
                      'auctionurl': '', 'location': auctionhouse.location, 'auctionperiod': auctionperiod,
                      'aucid': auction[0], 'ahid': auctionhouse.id}
                auctionslist.append(d1)
                uniqueauctions[str(auction[0])] = auction[1]
            d['auctionslist'] = auctionslist
            auctionhouses.append(d)
            if auctionhouse.housename not in filterauctionhouses:
                filterauctionhouses.append(auctionhouse.housename)
        context['auctionhouses'] = auctionhouses
        context['filterauctionhouses'] = filterauctionhouses
        try:
            redis_instance.set('ah_auctionhouses', pickle.dumps(auctionhouses))
            redis_instance.set('ah_filterauctionhouses', pickle.dumps(filterauctionhouses))
        except:
            pass
        for auctionhouse in auctionhousesqset:
            try:
                auctionsqset = auctionhouseauctionsdict[str(auctionhouse.id)]
            except:
                continue
            coverimage = ""
            if auctionsqset.__len__() > 0:
                coverimage = settings.IMG_URL_PREFIX + str(auctionsqset[0][8])
            d = {'housename': auctionhouse.housename, 'houseurl': auctionhouse.houseurl, 'description': '',
                 'image': coverimage, 'ahid': auctionhouse.id, 'location': auctionhouse.location}
            auctionslist = []
            for auction in auctionsqset:
                auctionperiod = ""
                featuredshowscutoffdate = datetime.date(featuredshowscutoffdate.year, featuredshowscutoffdate.month,
                                                        featuredshowscutoffdate.day)
                if auction[
                    5] < featuredshowscutoffdate:  # We won't consider auctions that have happened before the last 1 year.
                    continue
                if auction[5].strftime("%d %b, %Y") != "01 Jan, 0001" and auction[5].strftime(
                        "%d %b, %Y") != "01 Jan, 1":
                    auctionperiod = auction[5].strftime("%d %b, %Y")
                    aucenddate = auction[6]
                    if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                        auctionperiod += " - " + str(aucenddate)
                # print(auction[2])
                d1 = {'auctionname': auction[1], 'coverimage': settings.IMG_URL_PREFIX + str(auction[8]),
                      'auctionurl': auction[4], 'location': auctionhouse.location, 'auctionperiod': auctionperiod,
                      'aucid': auction[0], 'ahid': auctionhouse.id, 'housename': auctionhouse.housename,
                      'salecode': auction[2]}
                auctionslist.append(d1)
                uniqueauctions[str(auction[0])] = auction[1]
            d['auctionslist'] = auctionslist
            featuredshows.append(d)
            if featuredshows.__len__() >= maxfeaturedshows:
                break
        context['featuredshows'] = featuredshows
        try:
            redis_instance.set('ah_featuredshows', pickle.dumps(featuredshows))
        except:
            pass
    else:
        context['auctionhouses'] = auctionhouses
        context['featuredshows'] = featuredshows
    try:
        currentmngshows = pickle.loads(redis_instance.get('ah_currentmngshows'))
    except:
        currentmngshows = {}
    if currentmngshows.keys().__len__() == 0:
        maxrecs = maxauctionsperhouse * rows * 4
        auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar order by faac_auction_start_date desc limit %s" % maxrecs
        cursor.execute(auctionsql)
        auctionsqset = cursor.fetchall()
        for auction in auctionsqset:
            if str(auction[0]) in uniqueauctions.keys():
                continue
            else:
                uniqueauctions[str(auction[0])] = auction[1]
            auctionhouse = None
            try:
                auctionhouse = AuctionHouse.objects.get(id=auction[3])
            except:
                continue
            auctionhousename = auctionhouse.housename.title()
            auctionperiod = ""
            if auction[5].strftime("%d %b, %Y") != "01 Jan, 0001" and auction[5].strftime("%d %b, %Y") != "01 Jan, 1":
                auctionperiod = auction[5].strftime("%d %b, %Y")
                aucenddate = auction[6]
                if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                    auctionperiod += " - " + str(aucenddate)
            if auctionhousename in currentmngshows.keys():
                l = currentmngshows[auctionhousename]
                if l.__len__() >= maxauctionsperhouse:
                    continue
                d = {'auctionname': auction[1], 'coverimage': auction[8], 'auctionurl': auctionhouse.houseurl,
                     'location': auctionhouse.location, 'auctionperiod': auctionperiod, 'aucid': auction[0],
                     'ahid': auctionhouse.id, 'salecode': auction[2]}
                l.append(d)
                currentmngshows[auctionhousename] = l
            else:
                l = []
                d = {'auctionname': auction[1], 'coverimage': settings.IMG_URL_PREFIX + str(auction[8]),
                     'auctionurl': auctionhouse.houseurl, 'location': auctionhouse.location,
                     'auctionperiod': auctionperiod, 'aucid': auction[0], 'ahid': auctionhouse.id,
                     'salecode': auction[2]}
                l.append(d)
                currentmngshows[auctionhousename] = l
        context['currentmngshows'] = currentmngshows
        try:
            redis_instance.set('ah_currentmngshows', pickle.dumps(currentmngshows))
        except:
            pass
    else:
        context['currentmngshows'] = currentmngshows
    cursor.close()
    dbconn.close()
    # carouselentries = getcarouselinfo_new()
    # context['carousel'] = carouselentries
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    if request.user:
        userobj = request.user
        context['username'] = userobj.username
    template = loader.get_template('auctionhouses.html')
    return HttpResponse(template.render(context, request))


# @cache_page(CACHE_TTL)
def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    # ahid = -1
    # if request.method == 'GET':
    #     if 'ahid' in request.GET.keys():
    #         ahid = str(request.GET['ahid'])
    # if not ahid:
    #     return HttpResponse("Invalid Request: Request is missing auction house Id")
    # page = 1
    # if request.method == 'GET' and 'page' in request.GET.keys():
    #     try:
    #         page = int(request.GET['page'])
    #     except:
    #         pass
    # upcomingchunk = 4
    # pastchunk = 24
    # upcomingstartctr = upcomingchunk * page - upcomingchunk
    # paststartctr = pastchunk * page - pastchunk
    # commonstartctr = upcomingstartctr + paststartctr
    # currentdate = datetime.datetime.now()
    # context = {}
    # auctionsqset = []
    # try:
    #     auctionsqset = Auction.objects.filter(auctionhouse_id=int(ahid)).order_by('-auctionstartdate')[commonstartctr:commonstartctr+200] # We expect to retrieve the necessary auctions from this 200 records.
    # except:
    #     print("Request Failed while retrieving auctions for the selected auction house: %s"%sys.exc_info()[1].__str__())
    #     return HttpResponse("Request Failed while retrieving auctions for the selected auction house: %s"%sys.exc_info()[1].__str__())
    # auchouseobj = None
    # try:
    #     auchouseobj = AuctionHouse.objects.get(id=int(ahid))
    # except:
    #     print("Failed to retrieve auctionhouse object: %s"%sys.exc_info()[1].__str__())
    #     return HttpResponse("Request Failed: %s"%sys.exc_info()[1].__str__())
    # context['auctionhousename'] = auchouseobj.housename
    # context['auctionhouselocation'] = auchouseobj.location
    # context['auctionhousecountry'] = auchouseobj.location
    # context['ahid'] = ahid
    # upcomingauctions = []
    # pastauctions = []
    # aucctr = 0
    # for auction in auctionsqset:
    #     auctiondate = auction.auctionstartdate
    #     auctiondate = datetime.datetime(auctiondate.year, auctiondate.month, auctiondate.day)
    #     d = {'auctionname' : auction.auctionname, 'aucid' : auction.id, 'salecode' : auction.auctionid, 'auchouseid' : auction.auctionhouse_id, 'auctionhousename' : auchouseobj.housename, 'lotcount' : auction.lotcount, 'auctionimage' : settings.IMG_URL_PREFIX + str(auction.coverimage), 'aucperiod' : ''}
    #     if auction.coverimage is None or auction.coverimage == "":
    #         lotsqset = Lot.objects.filter(auction_id=auction.id)
    #         if lotsqset.__len__() < 1:
    #             aucctr += 1
    #             continue
    #         maxlowestimate = lotsqset[0].lowestimateUSD
    #         lotobj_maxlowestimate = lotsqset[0]
    #         for lot in lotsqset:
    #             if lot.lowestimateUSD is not None and maxlowestimate is not None and lot.lowestimateUSD > maxlowestimate:
    #                 maxlowestimate = lot.lowestimateUSD
    #                 lotobj_maxlowestimate = lot
    #             else:
    #                 pass
    #         d['auctionimage'] = settings.IMG_URL_PREFIX + str(lotobj_maxlowestimate.lotimage1)
    #     aucperiod = auction.auctionstartdate.strftime("%d %b, %Y")
    #     aucenddate = auction.auctionenddate
    #     if str(aucenddate) != "0000-00-00" and aucenddate != "01 Jan, 1":
    #         aucperiod = auction.auctionstartdate.strftime("%d %b, %Y") + " - " + str(aucenddate)
    #     d['aucperiod'] = aucperiod
    #     if auctiondate > currentdate:
    #         if upcomingauctions.__len__() <= upcomingchunk and aucctr >= upcomingstartctr:
    #             upcomingauctions.append(d)
    #     else:
    #         if pastauctions.__len__() <= pastchunk and aucctr >= paststartctr:
    #             pastauctions.append(d)
    #     aucctr += 1
    # context['upcomingauctions'] = upcomingauctions
    # print(pastauctions)
    # context['pastauctions'] = pastauctions
    # if request.user.is_authenticated:
    #    context['favourite_link'] = "%s"%aid
    # else:
    #    context['favourite_link'] = ""
    # prevpage = int(page) - 1
    # nextpage = int(page) + 1
    # displayedprevpage1 = 0
    # displayedprevpage2 = 0
    # if prevpage > 0:
    #     displayedprevpage1 = prevpage - 1
    #     displayedprevpage2 = prevpage - 2
    # displayednextpage1 = nextpage + 1
    # displayednextpage2 = nextpage + 2
    # firstpage = 1
    # context['pages'] = {'prevpage' : prevpage, 'nextpage' : nextpage, 'firstpage' : firstpage, 'displayedprevpage1' : displayedprevpage1, 'displayedprevpage2' : displayedprevpage2, 'displayednextpage1' : displayednextpage1, 'displayednextpage2' : displayednextpage2, 'currentpage' : int(page)}
    context = {}
    userDict = request.session.get('user')
    if userDict:
        context['username'] = userDict['username']
    template = loader.get_template('auctionhouse_details.html')
    return HttpResponse(template.render(context, request))


# @cache_page(CACHE_TTL)
def details_old(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    aucid = None
    if request.method == 'GET':
        if 'aucid' in request.GET.keys():
            aucid = str(request.GET['aucid'])
    if not aucid:
        return HttpResponse("Invalid Request: Request is missing auction Id")
    auctionobj = None
    try:
        auctionobj = Auction.objects.get(id=aucid)
    except:
        return HttpResponse("Could not identify a auction with Id %s" % aucid)
    # Find all auctions from the same auction house as the selected auction
    auctionslist = []
    relatedartists = {}
    context = {}
    auctioninfo = {}
    chunksize = 4
    try:
        auctioninfo = pickle.loads(redis_instance.get('ah_auctioninfo_%s' % auctionobj.id))
    except:
        auctioninfo = {}
    if auctioninfo.keys().__len__() == 0:
        auctionsqset = Auction.objects.filter(auctionhouse_id__iexact=auctionobj.auctionhouse_id).order_by(
            '-auctionstartdate')
        auctionhouse = AuctionHouse.objects.get(id=auctionobj.auctionhouse_id)
        auchousename = auctionhouse.housename
        auctioninfo = {'auctionname': auctionobj.auctionname, 'auctionhouse': auchousename,
                       'auctionlocation': auctionhouse.location, 'auctionurl': auctionobj.auctionurl,
                       'coverimage': settings.IMG_URL_PREFIX + str(auctionobj.coverimage),
                       'auctiondate': auctionobj.auctionstartdate, 'auctionid': auctionobj.auctionid,
                       'aucid': auctionobj.id}
        try:
            redis_instance.set('ah_auctioninfo_%s' % auctionobj.id, pickle.dumps(auctioninfo))
        except:
            pass
    context['auctioninfo'] = auctioninfo
    overviewlots = []
    alllots = []
    try:
        alllots = pickle.loads(redis_instance.get('ah_alllots_%s' % auctionobj.id))
        overviewlots = pickle.loads(redis_instance.get('ah_overviewlots_%s' % auctionobj.id))
        auctionslist = pickle.loads(redis_instance.get('ah_auctionslist_%s' % auctionobj.id))
        relatedartists = pickle.loads(redis_instance.get('ah_relatedartists_%s' % auctionobj.id))
    except:
        alllots = []
        overviewlots = []
    if alllots.__len__() == 0:
        # This is going to be a very costly query. Lot (lots table) needs to be indexed on auction field. 
        lotsqset = Lot.objects.filter(auction_id=auctionobj.id)  # .order_by('priority')
        lctr = 0
        for lotobj in lotsqset:
            artworkobj = Artwork.objects.get(id=lotobj.artwork_id)
            artworkname = artworkobj.artworkname
            artworkdesc = artworkobj.description
            lotartistqset = LotArtist.objects.filter(artist_id=artworkobj.artist_id)
            lotartistobj = lotartistqset[0]
            artistname = lotartistobj.artist_name
            d = {'title': artworkname, 'description': artworkdesc, 'artistname': str(artistname),
                 'loturl': lotobj.source, 'lotimage': settings.IMG_URL_PREFIX + str(lotobj.lotimage1),
                 'medium': lotobj.medium, 'size': lotobj.sizedetails,
                 'estimate': str(lotobj.lowestimateUSD) + " - " + str(lotobj.highestimateUSD),
                 'soldprice': str(lotobj.soldpriceUSD), 'currency': "USD", 'nationality': lotartistobj.nationality,
                 'lid': lotobj.id}
            if lctr < chunksize:
                overviewlots.append(d)
            else:
                alllots.append(d)
            lctr += 1
        try:
            redis_instance.set('ah_overviewlots_%s' % auctionobj.id, pickle.dumps(overviewlots))
            redis_instance.set('ah_alllots_%s' % auctionobj.id, pickle.dumps(alllots))
        except:
            pass
        for auction in auctionsqset:
            auctionhouseobj = AuctionHouse.objects.get(id=auction.auctionhouse_id)
            d = {'auctionname': auction.auctionname, 'auctionhouse': auctionhouseobj.housename,
                 'auctionlocation': auctionhouseobj.location, 'description': '', 'auctionurl': '', 'lotsurl': '',
                 'coverimage': settings.IMG_URL_PREFIX + str(auction.coverimage), 'auctionid': auction.auctionid,
                 'aucid': auction.id, 'auctiondate': auctionobj.auctionstartdate}
            # Get 'chunksize' number of lots for this auction
            lotsqset = Lot.objects.filter(auction_id=auction.id)  # .order_by() # Ordered by priority
            lots = []
            numlots = chunksize
            if numlots > lotsqset.__len__():
                numlots = lotsqset.__len__()
            for lotobj in lotsqset[0:numlots]:
                artworkobj = Artwork.objects.get(id=lotobj.artwork_id)
                artworkname = artworkobj.artworkname
                artworkdesc = artworkobj.description
                lotartistqset = LotArtist.objects.filter(artist_id=artworkobj.artist_id)
                lotartistobj = lotartistqset[0]
                artistname = lotartistobj.artist_name
                ld = {'title': artworkname, 'description': artworkdesc, 'artistname': artistname, 'loturl': '',
                      'lotimage': settings.IMG_URL_PREFIX + str(lotobj.lotimage1), 'medium': lotobj.medium,
                      'size': lotobj.sizedetails,
                      'estimate': str(lotobj.lowestimateUSD) + " - " + str(lotobj.highestimateUSD),
                      'soldprice': lotobj.soldpriceUSD, 'currency': "USD", 'nationality': lotartistobj.nationality,
                      'lid': lotobj.id}
                lots.append(ld)
                if artistname not in relatedartists.keys():
                    artistqset = Artist.objects.filter(artistname__iexact=artistname)
                    if artistqset.__len__() > 0:
                        relatedartists[artistname] = [artistqset[0].id, artworkname,
                                                      settings.IMG_URL_PREFIX + str(lotobj.lotimage1)]
            d['lots'] = lots
            auctionslist.append(d)
        try:
            redis_instance.set('ah_auctionslist_%s' % auctionobj.id, pickle.dumps(auctionslist))
            redis_instance.set('ah_relatedartists_%s' % auctionobj.id, pickle.dumps(relatedartists))
        except:
            pass
    context['overviewlots'] = overviewlots
    context['alllots'] = alllots
    context['auctionslist'] = auctionslist
    context['relatedartists'] = relatedartists
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('auctionhouse_details.html')
    return HttpResponse(template.render(context, request))


# @cache_page(CACHE_TTL)
def follow(request):
    return HttpResponse("")


def search(request):
    """
    This should return a json response containing a list of dicts.
    The dict keys would be the attributes of an auctionhouse object.
    """
    if request.method != 'GET':
        return HttpResponse(json.dumps({'err': "Invalid method of call"}))
    searchkey = None
    page = 1
    if request.method == 'GET':
        if 'q' in request.GET.keys():
            searchkey = str(request.GET['q']).strip()
    if not searchkey:
        return HttpResponse(json.dumps({'err': "Invalid Request: Request is missing search key"}))
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    # print(searchkey)
    maxauctionsperhouse = 8
    startctr = int(page) * maxauctionsperhouse - maxauctionsperhouse
    endctr = int(page) * maxauctionsperhouse
    chunksize = 10  # This number of auction houses (rows of auctions) will be shown per page.
    ahstart = int(page) * chunksize - chunksize
    ahend = int(page) * chunksize
    context = {}
    auctionhousesqset = AuctionHouse.objects.filter(housename__icontains=searchkey)[ahstart:ahend]
    auctionhousematches = []
    auchouseidslist = []
    for auctionhouse in auctionhousesqset:
        auchouseid = auctionhouse.id
        auchouseidslist.append(auchouseid)
    allauctionsqset = Auction.objects.filter(auctionhouse_id__in=auchouseidslist).order_by('-auctionstartdate')[
                      startctr:(ahend - ahstart) * maxauctionsperhouse]
    auctionidslist = []
    auctionsbyauctionhousesdict = {}
    for auction in allauctionsqset:
        aucid = auction.id
        auctionidslist.append(aucid)
        auchouseid = auction.auctionhouse_id
        if str(auchouseid) not in auctionsbyauctionhousesdict.keys():
            auctionsbyauctionhousesdict[str(auchouseid)] = [auction, ]
        else:
            auctionslist = auctionsbyauctionhousesdict[str(auchouseid)]
            auctionslist.append(auction)
            auctionsbyauctionhousesdict[str(auchouseid)] = auctionslist
    alllotsqset = Lot.objects.filter(auction_id__in=auctionidslist)
    lotsbyauctionsdict = {}
    for lot in alllotsqset:
        auctionid = lot.auction_id
        if str(auctionid) not in lotsbyauctionsdict.keys():
            lotsbyauctionsdict[str(auctionid)] = [lot, ]
        else:
            lotslist = lotsbyauctionsdict[str(auctionid)]
            lotslist.append(lot)
            lotsbyauctionsdict[str(auctionid)] = lotslist
    for auctionhouse in auctionhousesqset:
        housename = auctionhouse.housename
        # print(housename + " - " + auctionhouse.location)
        if str(auctionhouse.id) not in auctionsbyauctionhousesdict.keys():
            continue
        auctionsqset = auctionsbyauctionhousesdict[str(auctionhouse.id)]
        d = {'housename': housename, 'houseurl': auctionhouse.houseurl, 'description': '', 'ahid': auctionhouse.id,
             'location': auctionhouse.location}
        auctionslist = []
        coverimage = ""
        if auctionsqset.__len__() == 0:
            continue
        for auction in auctionsqset:
            auctionperiod = ""
            if auction.auctionstartdate.strftime("%d %b, %Y") != "01 Jan, 0001" and auction.auctionstartdate.strftime(
                    "%d %b, %Y") != "01 Jan, 1":
                auctionperiod = auction.auctionstartdate.strftime("%d %b, %Y")
                aucenddate = auction.auctionenddate
                if str(aucenddate) != "0000-00-00" and str(aucenddate) != "01 Jan, 1":
                    auctionperiod += " - " + str(aucenddate)
            if coverimage == "":
                coverimage = settings.IMG_URL_PREFIX + str(auction.coverimage)
                d['coverimage'] = coverimage
            if auction.coverimage is None or auction.coverimage == "":
                if str(auction.id) not in lotsbyauctionsdict.keys():
                    continue
                lotsqset = lotsbyauctionsdict[str(auction.id)]
                if lotsqset.__len__() < 1:
                    continue
                maxlowestimate = lotsqset[0].lowestimateUSD
                lotobj_maxlowestimate = lotsqset[0]
                for lot in lotsqset:
                    if lot.lowestimateUSD is not None and maxlowestimate is not None and lot.lowestimateUSD > maxlowestimate:
                        maxlowestimate = lot.lowestimateUSD
                        lotobj_maxlowestimate = lot
                    else:
                        pass
                d['coverimage'] = settings.IMG_URL_PREFIX + str(lotobj_maxlowestimate.lotimage1)
            d1 = {'auctionname': auction.auctionname, 'coverimage': d['coverimage'], 'auctionurl': '',
                  'location': auctionhouse.location, 'auctionperiod': auctionperiod, 'aucid': auction.id,
                  'ahid': auctionhouse.id}
            auctionslist.append(d1)
        d['auctionslist'] = auctionslist
        auctionhousematches.append(d)
    context['auctionhousematches'] = auctionhousematches
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
    userDict = request.session.get('user')
    if userDict:
        context['username'] = userDict['username']
    return HttpResponse(json.dumps(context))


# Presents information on lots available for sale at the given auction
# @cache_page(CACHE_TTL)
def auctiondetails(request):
    pass
