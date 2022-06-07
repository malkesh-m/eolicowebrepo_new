from django.shortcuts import render, redirect
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

from gallery.models import Gallery, Event
from museum.models import Museum, MuseumEvent, MuseumPieces
from login.models import User, Session, WebConfig, Carousel, Follow, Favourite
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse
from artists.models import Artist, Artwork, FeaturedArtist

# Caching related imports and variables
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


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


#@cache_page(CACHE_TTL)
def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    chunksize = 3
    context = {}
    followsdict = {}
    if request.user.is_authenticated:
        followsqset = Follow.objects.filter(user=request.user, status=True).order_by("-updatedon")
        for follow in followsqset:
            artist = follow.artist
            artistname = artist.artistname
            aimg = artist.artistimage
            anat = artist.nationality
            aid = artist.id
            about = artist.description
            followsdict[artistname] = [about, aimg, anat, aid]
    context['follows'] = followsdict
    favouritesdict = {}
    if request.user.is_authenticated:
        favsqset = Favourite.objects.filter(user=request.user).order_by("-updated")
        for fav in favsqset:
            favtype = fav.reference_model
            if favtype == "fineart_artists":
                favmodelid = fav.reference_model_id
                try:
                    artist = Artist.objects.get(id=favmodelid)
                    artistname = artist.artistname
                    aimg = artist.artistimage
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
                    artworkimg = artwork.image1
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
                    if auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                        period = period + " - " + auction.auctionenddate.strftime("%d %b, %Y")
                    auchouseid = auction.auctionhouse_id
                    auchouseobj = AuctionHouse.objects.get(id=auchouseid)
                    housename = auchouseobj.housename
                    aucid = auction.id
                    aucimg = auction.coverimage
                    favouritesdict[auctionname] = ["auction", period, housename, aucid, aucimg, auchouseid]
                except:
                    pass
    context['favourites'] = favouritesdict
    artistsdict = {}
    try:
        artistsdict = pickle.loads(redis_instance.get('h_artistsdict'))
    except:
        pass
    if artistsdict.keys().__len__() == 0:
        artists = FeaturedArtist.objects.all().order_by('-totalsoldprice')
        artistslist = artists[0:8]
        for a in artistslist:
            if a.id == 1: # This is for 'missing' artists
                continue
            aname = a.artist_name
            about = a.description
            aurl = ""
            aimg = a.artistimage
            anat = a.nationality
            aid = a.artist_id
            artistsdict[aname] = [about, aurl, aimg, anat, aid]
        try:
            redis_instance.set('h_artistsdict', pickle.dumps(artistsdict))
        except:
            pass
    context['artists'] = artistsdict
    eventsdict = {}
    try:
        eventsdict = pickle.loads(redis_instance.get('h_eventsdict'))
    except:
        pass
    if eventsdict.keys().__len__() == 0:
        events = Event.objects.all().order_by('priority', '-edited')
        eventslist = events[0:4]
        for e in eventslist:
            ename = e.eventname
            eurl = e.eventurl
            einfo = str(e.eventinfo[0:20]) + "..."
            eperiod = e.eventperiod
            eid = e.id
            eventimage = e.eventimage
            eventsdict[ename] = [eurl, einfo, eperiod, eid, eventimage ]
        try:
            redis_instance.set('h_eventsdict', pickle.dumps(eventsdict))
        except:
            pass
    context['events'] = eventsdict
    museumsdict = {}
    try:
        museumsdict = pickle.loads(redis_instance.get('h_museumsdict'))
    except:
        pass
    if museumsdict.keys().__len__() == 0:
        museumsqset = Museum.objects.all().order_by('priority', '-edited')
        museumslist = museumsqset[0:4]
        for mus in museumslist:
            mname = mus.museumname
            murl = mus.museumurl
            minfo = str(mus.description[0:20]) + "..."
            mlocation = mus.location
            mid = mus.id
            mimage = mus.coverimage
            museumsdict[mname] = [murl, minfo, mlocation, mid, mimage ]
        try:
            redis_instance.set('h_museumsdict', pickle.dumps(museumsdict))
        except:
            pass
    context['museums'] = museumsdict
    upcomingauctions = {}
    try:
        upcomingauctions = pickle.loads(redis_instance.get('h_upcomingauctions'))
    except:
        pass
    if upcomingauctions.keys().__len__() == 0:
        auctionsqset = Auction.objects.all().order_by('-auctionstartdate')
        actr = 0
        srcPattern = re.compile("src=(.*)$")
        curdate = datetime.datetime.now()
        for auction in auctionsqset:
            if auction.auctionstartdate < curdate: # Past auction - leave it.
                continue
            lotsqset = Lot.objects.filter(auction_id=auction.id)
            if lotsqset.__len__() == 0:
                continue
            imageloc = auction.coverimage
            lotobj = lotsqset[0]
            if imageloc == "":
                imageloc = lotobj.lotimage1
                spc = re.search(srcPattern, imageloc)
                if spc:
                    imageloc = spc.groups()[0]
                    imageloc = imageloc.replace("%3A", ":").replace("%2F", "/")
            auchouseobj = None
            auchousename, ahlocation = "", ""
            try:
                auchouseobj = AuctionHouse.objects.get(id=auction.auctionhouse_id)
                auchousename = auchouseobj.housename
                ahlocation = auchouseobj.location
            except:
                pass
            auctionperiod = ""
            if auction.auctionstartdate.strftime("%d %b, %Y") != "01 Jan, 0001" and auction.auctionstartdate.strftime("%d %b, %Y") != "01 Jan, 1":
                auctionperiod = auction.auctionstartdate.strftime("%d %b, %Y")
                if auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                    auctionperiod += " - " + auction.auctionenddate.strftime("%d %b, %Y")
            d = {'auctionname' : auction.auctionname, 'auctionid' : auction.auctionid, 'auctionhouse' : auchousename, 'location' : ahlocation, 'coverimage' : imageloc, 'aucid' : auction.id, 'auctionperiod' : auctionperiod, 'auctionurl' : auction.auctionurl, 'lid' : lotobj.id, 'ahid' : auction.auctionhouse_id}
            upcomingauctions[auction.auctionname] = d
            actr += 1
            if actr >= chunksize:
                break
        try:
            redis_instance.set('h_upcomingauctions', pickle.dumps(upcomingauctions))
        except:
            pass
    context['upcomingauctions'] = upcomingauctions
    auctionhouses = []
    try:
        auctionhouses = pickle.loads(redis_instance.get('h_auctionhouses'))
    except:
        pass
    if auctionhouses.__len__() == 0:
        auchousesqset = AuctionHouse.objects.all()
        actr = 0
        for auchouse in auchousesqset:
            auchousename = auchouse.housename
            auctionsqset = Auction.objects.filter(auctionhouse_id=auchouse.id)
            if auctionsqset.__len__() == 0:
                continue
            print(auctionsqset[0].coverimage)
            d = {'housename' : auchouse.housename, 'aucid' : auctionsqset[0].id, 'location' : auchouse.location, 'description' : '', 'coverimage' : auctionsqset[0].coverimage, 'ahid' : auchouse.id}
            auctionhouses.append(d)
            actr += 1
            if actr >= chunksize:
                break
        try:
            redis_instance.set('h_auctionhouses', pickle.dumps(auctionhouses))
        except:
            pass
    context['auctionhouses'] = auctionhouses
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('homepage.html')
    return HttpResponse(template.render(context, request))


#@cache_page(CACHE_TTL)
def showlogin(request):
    return HttpResponse("")


def signup(request):
    if request.method == 'POST':
        context = {}
        username = request.POST.get('username').strip()
        email = request.POST.get('emailid').strip()
        raw_password = request.POST.get('password1').strip()
        password2 = request.POST.get('password2').strip()
        # Validate user inputs here...
        if username == "":
            return HttpResponse(json.dumps({'error' : 'Username cannot be empty string'}))
        emailPattern = re.compile("^\w+\.?\w*@\w+\.\w{3,4}$")
        eps = re.search(emailPattern, email)
        if not eps:
            return HttpResponse(json.dumps({'error' : 'Email entered is not valid'}))
        if raw_password != password2:
            return HttpResponse(json.dumps({'error' : 'Passwords do not match'}))
        newuser = djUser.objects.create_user(username=username, email=email, password=raw_password)
        user = authenticate(username=username, password=raw_password)
        login(request, user)
        return HttpResponse(json.dumps({'error' : ''})) # Later this should be changed to 'profile' as we want the user to go to the user's profile page after login.
    else:
        context = {}
    return render(request, 'registration.html', context)


def dologin(request):
    if request.method == 'POST':
        context = {}
        username = request.POST.get('username')
        raw_password = request.POST.get('passwd')
        user = authenticate(username=username, password=raw_password)
        if user is not None:
            login(request, user)
        else:
            return HttpResponse(0)
        return HttpResponseRedirect("/login/index/") # Later this should be changed to 'profile' as we want the user to go to the user's profile page after login.
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


#@cache_page(CACHE_TTL)
def about(request):
    if request.method == 'GET':
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
        if request.user.is_authenticated and request.user.is_staff:
            context['adminuser'] = 1
        else:
            context['adminuser'] = 0
        template = loader.get_template('about.html')
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Incorrect request method")


#@cache_page(CACHE_TTL)
def contactus(request):
    if request.method == 'GET':
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
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
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
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
    artist = None
    try:
        artist = Artist.objects.get(id=aid)
    except:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : divid, 'aid' : aid})) # Operation failed! Can't proceed without an artist.
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
    follow.status = True # Explicitly set it True, just in case we had an existing record with a False value.
    try:
        follow.save()
        return HttpResponse(json.dumps({'msg' : 1, 'div_id' : divid, 'aid' : aid})) # Successfully following...
    except:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : divid, 'aid' : aid})) # Failed again.


@login_required(login_url="/login/show/")
def unfollowartist(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
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
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : '', 'aid' : ''})) # Operation failed!
    artist = None
    try:
        artist = Artist.objects.get(id=aid)
    except:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : divid, 'aid' : aid})) # Operation failed! Can't proceed without an artist.
    followqset = Follow.objects.filter(artist=artist, user=request.user)
    follow = None
    if followqset.__len__() > 0:
        follow = followqset[0]
    else:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : divid, 'aid' : aid})) # The user was not following this artist.
    follow.status = False # This means user left the artist.
    follow.user_session_key = sessionkey
    try:
        follow.save()
        return HttpResponse(json.dumps({'msg' : 1, 'div_id' : divid, 'aid' : aid})) # Successfully left...
    except:
        return HttpResponse(json.dumps({'msg' : 0, 'div_id' : divid, 'aid' : aid})) # Failed again.


@login_required(login_url="/login/show/")
def morefollows(request):
    if request.method != 'GET':
        return HttpResponse(json.dumps({'msg' : 0, 'aid' : ''})) # Operation failed!
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
        aimg = artist.artistimage
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
    context['pages'] = {'prevpage' : prevpage, 'nextpage' : nextpage, 'firstpage' : firstpage, 'displayedprevpage1' : displayedprevpage1, 'displayedprevpage2' : displayedprevpage2, 'displayednextpage1' : displayednextpage1, 'displayednextpage2' : displayednextpage2, 'currentpage' : int(page)}
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('morefollows.html')
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login/show/")
def morefavourites(request):
    if request.method != 'GET':
        return HttpResponse(json.dumps({'msg' : 0, 'aid' : ''})) # Operation failed!
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
                aimg = artist.artistimage
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
                artworkimg = artwork.image1
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
                if auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 0001" and auction.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
                    period = period + " - " + auction.auctionenddate.strftime("%d %b, %Y")
                auchouseid = auction.auctionhouse_id
                auchouseobj = AuctionHouse.objects.get(id=auchouseid)
                housename = auchouseobj.housename
                aucid = auction.id
                aucimg = auction.coverimage
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
    context['pages'] = {'prevpage' : prevpage, 'nextpage' : nextpage, 'firstpage' : firstpage, 'displayedprevpage1' : displayedprevpage1, 'displayedprevpage2' : displayedprevpage2, 'displayednextpage1' : displayednextpage1, 'displayednextpage2' : displayednextpage2, 'currentpage' : int(page)}
    if request.user.is_authenticated and request.user.is_staff:
        context['adminuser'] = 1
    else:
        context['adminuser'] = 0
    template = loader.get_template('morefavourites.html')
    return HttpResponse(template.render(context, request))







