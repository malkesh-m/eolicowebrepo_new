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
from django.conf import settings

import os, sys, re, time, datetime

from gallery.models import Gallery, Event, Artist, Artwork
from login.models import User, Session, WebConfig, Carousel
from login.views import getcarouselinfo
from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse

import simplejson as json
import urllib

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout


def output_path():
    return os.path.join(settings.OUTPUT_FILE_DIR, 'csv')


def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)
        os.chmod(path, 0o666)


def handleuploadedfile(uploaded_file, targetdir, filename):
    """
    Handle uploaded file. Returns a list containing the path
    to the uploaded file and a message
    (which would be '' in case of success).
    """
    destinationfile = os.path.sep.join([ targetdir, filename ])
    with open(destinationfile, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
        destination.close()
        os.chmod(targetdir, 0o777)
        os.chmod(destinationfile, 0o777) # Is there a way to club these 'chmod' statements?
    return [ destinationfile, '', filename ]


def showlogin(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('adminlogin.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        username, passwd = "", ""
        if 'username' in request.POST.keys():
            username = request.POST['username'].strip()
        if 'passwd' in request.POST.keys():
            passwd = request.POST['passwd']
        userqset = User.objects.filter(username=username)
        if userqset.__len__() > 0:
            userobj = userqset[0]
            if userobj.check_password(passwd):
                login(request, userobj)
                return HttpResponseRedirect("/admin/galleries/")
            else:
                return HttpResponseRedirect("/admin/login/?2")
    else:
        return HttpResponseRedirect("/admin/login/?1")


@login_required(login_url='/admin/login/')
def galleries(request):
    if request.method == 'GET':
        context = {}
        gtypesqset = Gallery.objects.order_by().values_list('gallerytype').distinct()
        gallerytypes = []
        for gtype in gtypesqset:
            gallerytypes.append(gtype[0])
        context['gallerytypes'] = gallerytypes
        template = loader.get_template('galleries.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        galleryname, gallerylocation, gallerydescription, gallerywebsite, selgallerytype, gallerytype, gallerycoverimage, selgallerypriority = "", "", "", "", "", "", "", ""
        if 'galleryname' in request.POST.keys():
            galleryname = request.POST['galleryname'].strip()
        if 'gallerylocation' in request.POST.keys():
            gallerylocation = request.POST['gallerylocation'].strip()
        if 'gallerydescription' in request.POST.keys():
            gallerydescription = request.POST['gallerydescription'].strip()
        if 'gallerywebsite' in request.POST.keys():
            gallerywebsite = request.POST['gallerywebsite'].strip()
        if 'selgallerytype' in request.POST.keys():
            selgallerytype = request.POST['selgallerytype'].strip()
        if 'gallerytype' in request.POST.keys():
            gallerytype = request.POST['gallerytype'].strip()
        if 'selgallerypriority' in request.POST.keys():
            selgallerypriority = request.POST['selgallerypriority']
        if selgallerytype == "":
            selgallerytype = gallerytype
        """
        requestbody = str(request.body)
        bodycomponents = requestbody.split("&")
        requestdict = {}
        for comp in bodycomponents:
            compparts = comp.split("=")
            if compparts.__len__() > 1:
                compparts[0] = compparts[0].replace("b'", "")
                requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
        """
        if galleryname == "" or selgallerytype == "":
            message = "Gallery name or gallery type is empty. Can't create gallery."
            return HttpResponse(message)
        gallery = Gallery()
        #print(galleryname + " ########")
        gallery.galleryname = galleryname.title()
        gallery.location = gallerylocation
        gallery.description = gallerydescription
        gallery.website = gallerywebsite
        gallery.gallerytype = selgallerytype
        gallery.slug = ""
        gallery.priority = selgallerypriority
        if gallery.priority == "":
            gallery.priority = 1
        imgfile = request.FILES.get("gallerycoverimage")
        mimetype = imgfile.content_type
        if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
            return None
        if 'gallerycoverimage' in request.FILES.keys():
            coverimage = request.FILES['gallerycoverimage'].name
        imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
        if not os.path.exists(imagelocation):
            mkdir_p(imagelocation)
        uploadstatus = handleuploadedfile(request.FILES['gallerycoverimage'], imagelocation, coverimage)
        gallery.coverimage = uploadstatus[0]
        try:
            gallery.save()
            message = "Successfully created gallery named '%s'"%galleryname.title()
        except:
            message = "Error: Could not create gallery - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)


@login_required(login_url='/admin/login/')
def savegallery(request):
    if request.method == 'POST':
        galleryname, gallerylocation, gallerydescription, gallerywebsite, selgallerytype, gallerytype, gallerycoverimage, selgallerypriority, galid = "", "", "", "", "", "", "", "", ""
        if 'galleryname' in request.POST.keys():
            galleryname = request.POST['galleryname'].strip()
        if 'gallerylocation' in request.POST.keys():
            gallerylocation = request.POST['gallerylocation'].strip()
        if 'gallerydescription' in request.POST.keys():
            gallerydescription = request.POST['gallerydescription'].strip()
        if 'gallerywebsite' in request.POST.keys():
            gallerywebsite = request.POST['gallerywebsite'].strip()
        if 'selgallerytype' in request.POST.keys():
            selgallerytype = request.POST['selgallerytype'].strip()
        if 'gallerytype' in request.POST.keys():
            gallerytype = request.POST['gallerytype'].strip()
        if 'selgallerypriority' in request.POST.keys():
            selgallerypriority = request.POST['selgallerypriority']
        if selgallerytype == "":
            selgallerytype = gallerytype
        if galleryname == "" or selgallerytype == "":
            message = "Gallery name or gallery type is empty. Can't create gallery."
            return HttpResponse(message)
        if 'gid' in request.POST.keys():
            galid = request.POST['gid'].strip()
        gallery = None
        try:
            gallery = Gallery.objects.get(id=galid)
        except:
            return HttpResponse("Gallery with the given Id could not be found")
        gallery.galleryname = galleryname.title()
        gallery.location = gallerylocation
        gallery.description = gallerydescription
        #print(gallerydescription)
        gallery.website = gallerywebsite
        gallery.gallerytype = selgallerytype
        gallery.slug = ""
        gallery.priority = selgallerypriority
        if gallery.priority == "":
            gallery.priority = 1
        imgfile = request.FILES.get("gallerycoverimage")
        if imgfile:
            mimetype = imgfile.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'gallerycoverimage' in request.FILES.keys():
                coverimage = request.FILES['gallerycoverimage'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['gallerycoverimage'], imagelocation, coverimage)
            gallery.coverimage = uploadstatus[0]
        try:
            gallery.save()
            message = "Successfully saved changes to gallery named '%s'"%galleryname.title()
        except:
            message = "Error: Could not save changes to gallery - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)
    else:
        return HttpResponse("Error: Invalid method of call")


@login_required(login_url='/admin/login/')
def searchgalleries(request):
    if request.method == 'GET':
        context = {}
        searchkey = request.GET.get('searchkey')
        galleriesqset = Gallery.objects.filter(galleryname__icontains=searchkey)
        galleries = {}
        for gal in galleriesqset:
            galleries[gal.galleryname] = gal.id
        galleriesjson = json.dumps(galleries)
        return HttpResponse(galleriesjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def editgallery(request):
    if request.method == 'GET':
        context = {}
        gid = request.GET.get('gid')
        galleriesqset = Gallery.objects.filter(id=gid)
        if galleriesqset.__len__() == 0:
            message = {'Error' : 'Could not find gallery with Id %s'%gid}
            resp = json.dumps(message)
            return HttpResponse(resp)
        gallery = {}
        gallerytypes = []
        gallery['galleryname'] = galleriesqset[0].galleryname
        gallery['location'] = galleriesqset[0].location
        gallery['description'] = galleriesqset[0].description
        gallery['galleryurl'] = galleriesqset[0].galleryurl
        gallery['website'] = galleriesqset[0].website
        gallery['gallerytype'] = galleriesqset[0].gallerytype
        gallery['priority'] = galleriesqset[0].priority
        gallery['coverimage'] = galleriesqset[0].coverimage
        gallery['id'] = galleriesqset[0].id
        context['gallery'] = gallery
        gtypesqset = Gallery.objects.order_by().values_list('gallerytype').distinct()
        gallerytypes = []
        for gtype in gtypesqset:
            gallerytypes.append(gtype[0])
        context['gallerytypes'] = gallerytypes
        galleryjson = json.dumps(context)
        return HttpResponse(galleryjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def gevents(request):
    if request.method == 'GET':
        context = {}
        galleriesqset = Gallery.objects.all()
        galleriesdict = {}
        for gallery in galleriesqset:
            galleriesdict[gallery.galleryname] = gallery.id
        context['galleriesdict'] = galleriesdict
        eventsqset = Event.objects.order_by().values_list('eventtype').distinct()
        allevents = []
        for gev in eventsqset:
            allevents.append(gev[0])
        context['allevents'] = allevents
        template = loader.get_template('gevents.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        geventname, geventlocation, geventinfo, geventstatus, selgeventtype, geventtype, geventcoverimage, selgeventpriority, geventstartdate, geventenddate, galleryid = "", "", "", "", "", "", "", "", "", "", ""
        if 'geventname' in request.POST.keys():
            geventname = request.POST['geventname'].strip()
        if 'geventlocation' in request.POST.keys():
            geventlocation = request.POST['geventlocation'].strip()
        if 'geventinfo' in request.POST.keys():
            geventinfo = request.POST['geventinfo'].strip()
        if 'geventstartdate' in request.POST.keys():
            geventstartdate = request.POST['geventstartdate'].strip()
        if 'geventenddate' in request.POST.keys():
            geventenddate = request.POST['geventenddate'].strip()
        if 'selgeventtype' in request.POST.keys():
            selgeventtype = request.POST['selgeventtype'].strip()
        if 'selgeventpriority' in request.POST.keys():
            selgeventpriority = request.POST['selgeventpriority']
        if 'selgeventstatus' in request.POST.keys():
            geventstatus = request.POST['selgeventstatus']
        if 'selgalleryname' in request.POST.keys():
            galleryid = request.POST['selgalleryname']
        if geventname == "" or selgeventtype == "":
            message = "Event name or event type is empty. Can't create Event."
            return HttpResponse(message)
        galleryobj = None
        try:
            galleryobj = Gallery.objects.get(id=galleryid)
        except:
            message = "Could not find gallery with Id %s"%galleryid
            return HttpResponse(message)
        gevent = Event()
        gevent.eventname = geventname.title()
        gevent.eventlocation = geventlocation
        gevent.eventinfo = geventinfo
        gevent.eventtype = selgeventtype
        gevent.eventstatus = geventstatus
        gevent.eventstartdate = geventstartdate
        gevent.eventenddate = geventenddate
        gevent.gallery = galleryobj
        gevent.priority = selgeventpriority
        gevent.eventperiod = geventstartdate + " - " + geventenddate
        if gevent.priority == "":
            gevent.priority = 1
        imgfile = request.FILES.get("geventcoverimage")
        mimetype = imgfile.content_type
        if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
            return None
        if 'geventcoverimage' in request.FILES.keys():
            coverimage = request.FILES['geventcoverimage'].name
        imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + gevent.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + gevent.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
        if not os.path.exists(imagelocation):
            mkdir_p(imagelocation)
        uploadstatus = handleuploadedfile(request.FILES['geventcoverimage'], imagelocation, coverimage)
        gevent.eventimage = uploadstatus[0]
        try:
            gevent.save()
            message = "Successfully created event named '%s'"%geventname.title()
        except:
            message = "Error: Could not create gallery - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)


@login_required(login_url='/admin/login/')
def searchgevents(request):
    if request.method == 'GET':
        context = {}
        searchkey = request.GET.get('searchkey')
        geventsqset = Event.objects.filter(eventname__icontains=searchkey)
        gevents = {}
        for gev in geventsqset:
            gevents[gev.eventname] = gev.id
        gevjson = json.dumps(gevents)
        return HttpResponse(gevjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


def editgevent(request):
    if request.method == 'GET':
        context = {}
        gevid = request.GET.get('evid')
        geventsqset = Event.objects.filter(id=gevid)
        if geventsqset.__len__() == 0:
            message = {'Error' : 'Could not find event with Id %s'%gevid}
            resp = json.dumps(message)
            return HttpResponse(resp)
        gevent = {}
        geventtypes = []
        galleriesdict = {}
        gevent['eventname'] = geventsqset[0].eventname
        gevent['location'] = geventsqset[0].eventlocation
        gevent['eventinfo'] = geventsqset[0].eventinfo
        gevent['eventtype'] = geventsqset[0].eventtype
        gevent['eventurl'] = geventsqset[0].eventurl
        gevent['eventstatus'] = geventsqset[0].eventstatus
        gevent['priority'] = geventsqset[0].priority
        gevent['eventstartdate'] = str(geventsqset[0].eventstartdate)
        gevent['eventenddate'] = str(geventsqset[0].eventenddate)
        gevent['coverimage'] = geventsqset[0].eventimage
        gevent['galleryname'] = geventsqset[0].gallery.galleryname
        gevent['id'] = geventsqset[0].id
        context['gevent'] = gevent
        gevtypesqset = Event.objects.order_by().values_list('eventtype').distinct()
        for gtype in gevtypesqset:
            geventtypes.append(gtype[0])
        context['geventtypes'] = geventtypes
        galleriesqset = Gallery.objects.all()
        for gal in galleriesqset:
            galname = gal.galleryname
            galid = gal.id
            galleriesdict[galname] = galid
        context['galleriesdict'] = galleriesdict
        galleryjson = json.dumps(context)
        return HttpResponse(galleryjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def savegevent(request):
    if request.method == 'POST':
        geventname, geventlocation, geventinfo, geventstatus, selgeventtype, geventtype, geventcoverimage, selgeventpriority, geventstartdate, geventenddate, galleryid, gevid = "", "", "", "", "", "", "", "", "", "", "", ""
        if 'geventname' in request.POST.keys():
            geventname = request.POST['geventname'].strip()
        if 'geventlocation' in request.POST.keys():
            geventlocation = request.POST['geventlocation'].strip()
        if 'geventinfo' in request.POST.keys():
            geventinfo = request.POST['geventinfo'].strip()
        if 'geventstartdate' in request.POST.keys():
            geventstartdate = request.POST['geventstartdate'].strip()
        if 'geventenddate' in request.POST.keys():
            geventenddate = request.POST['geventenddate'].strip()
        if 'selgeventtype' in request.POST.keys():
            selgeventtype = request.POST['selgeventtype'].strip()
        if 'selgeventpriority' in request.POST.keys():
            selgeventpriority = request.POST['selgeventpriority']
        if 'selgeventstatus' in request.POST.keys():
            geventstatus = request.POST['selgeventstatus']
        if 'selgalleryname' in request.POST.keys():
            galleryid = request.POST['selgalleryname']
        if 'gevid' in request.POST.keys():
            gevid = request.POST['gevid']
        if geventname == "" or selgeventtype == "":
            message = "Event name or event type is empty. Can't create Event."
            return HttpResponse(message)
        galleryobj = None
        try:
            galleryobj = Gallery.objects.get(id=galleryid)
        except:
            message = "Could not find gallery with Id %s"%galleryid
            return HttpResponse(message)
        gevent = None
        try:
            gevent = Event.objects.get(id=gevid)
        except:
            message = "Could not find event with Id %s"%gevid
            return HttpResponse(message)
        gevent.eventname = geventname.title()
        gevent.eventlocation = geventlocation
        gevent.eventinfo = geventinfo
        gevent.eventtype = selgeventtype
        gevent.eventstatus = geventstatus
        gevent.eventstartdate = geventstartdate
        gevent.eventenddate = geventenddate
        gevent.gallery = galleryobj
        gevent.priority = selgeventpriority
        gevent.eventperiod = geventstartdate + " - " + geventenddate
        if gevent.priority == "":
            gevent.priority = 1
        imgfile = request.FILES.get("geventcoverimage")
        if imgfile:
            mimetype = imgfile.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'geventcoverimage' in request.FILES.keys():
                coverimage = request.FILES['geventcoverimage'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + gevent.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + gevent.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['geventcoverimage'], imagelocation, coverimage)
            gevent.eventimage = uploadstatus[0]
        try:
            gevent.save()
            message = "Successfully saved event named '%s'"%geventname.title()
        except:
            message = "Error: Could not save event - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)
    else:
        return HttpResponse("Error: Invalid method of call")


@login_required(login_url='/admin/login/')
def artworks(request):
    if request.method == 'GET':
        context = {}
        galleriesqset = Gallery.objects.all()
        galleriesdict = {}
        for gallery in galleriesqset:
            galleriesdict[gallery.galleryname] = gallery.id
        context['galleriesdict'] = galleriesdict
        template = loader.get_template('artworks.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        artworkname, artistname, galleryid, eventid, artistbirth, artistdeath, artistnationality, medium, size, artworkdescription, signature, authenticity, estimate, soldprice, provenance, literature, exhibitions, artworkurl, priority = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
        if 'artworkname' in request.POST.keys():
            artworkname = request.POST['artworkname'].strip()
        if 'artistname' in request.POST.keys():
            artistname = request.POST['artistname'].strip()
        if 'selgalleryname' in request.POST.keys():
            galleryid = request.POST['selgalleryname'].strip()
        if 'selgeventname' in request.POST.keys():
            eventid = request.POST['selgeventname'].strip()
        if 'artistbirth' in request.POST.keys():
            artistbirth = request.POST['artistbirth'].strip()
        if 'artistdeath' in request.POST.keys():
            artistdeath = request.POST['artistdeath'].strip()
        if 'artistnationality' in request.POST.keys():
            artistnationality = request.POST['artistnationality']
        if 'medium' in request.POST.keys():
            medium = request.POST['medium']
        if 'size' in request.POST.keys():
            size = request.POST['size']
        if 'artworkdescription' in request.POST.keys():
            artworkdescription = request.POST['artworkdescription']
        if 'signature' in request.POST.keys():
            signature = request.POST['signature']
        if 'authenticity' in request.POST.keys():
            authenticity = request.POST['authenticity']
        if 'estimate' in request.POST.keys():
            estimate = request.POST['estimate']
        if 'soldprice' in request.POST.keys():
            soldprice = request.POST['soldprice']
        if 'provenance' in request.POST.keys():
            provenance = request.POST['provenance']
        if 'literature' in request.POST.keys():
            literature = request.POST['literature']
        if 'exhibitions' in request.POST.keys():
            exhibitions = request.POST['exhibitions']
        if 'artworkurl' in request.POST.keys():
            artworkurl = request.POST['artworkurl']
        if 'selartworkpriority' in request.POST.keys():
            priority = request.POST['selartworkpriority']
        if artworkname == "" or artistname == "":
            message = "Artwork name or Artist's name is empty. Can't create Artwork."
            return HttpResponse(message)
        galleryobj = None
        try:
            galleryobj = Gallery.objects.get(id=galleryid)
        except:
            message = "Could not find gallery with Id %s"%galleryid
            return HttpResponse(message)
        geventobj = None
        try:
            geventobj = Event.objects.get(id=eventid)
        except:
            message = "Could not find event with Id %s"%eventid
            return HttpResponse(message)
        artwork = Artwork()
        artwork.artworkname = artworkname.title()
        artwork.gallery = galleryobj
        artwork.event = geventobj
        artwork.artistname = artistname
        artwork.artistbirthyear = artistbirth
        artwork.artistdeathyear = artistdeath
        artwork.artistnationality = artistnationality
        artwork.size = size
        artwork.estimate = estimate
        artwork.soldprice = soldprice
        artwork.medium = medium
        artwork.signature = signature
        artwork.letterofauthenticity = authenticity
        artwork.description = artworkdescription
        artwork.provenance = provenance
        artwork.literature = literature
        artwork.exhibitions = exhibitions
        artwork.workurl = artworkurl
        artwork.priority = priority
        artwork.creationdate = ""
        if artwork.priority == "":
            artwork.priority = 1
        imgfile1 = request.FILES.get("image1")
        if imgfile1:
            mimetype = imgfile1.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image1' in request.FILES.keys():
                image1name = request.FILES['image1'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + geventobj.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + geventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image1'], imagelocation, image1name)
            artwork.image1 = uploadstatus[0]
        imgfile2 = request.FILES.get("image1")
        if imgfile2:
            mimetype = imgfile2.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image2' in request.FILES.keys():
                image2name = request.FILES['image2'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + geventobj.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + geventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image2'], imagelocation, image2name)
            artwork.image2 = uploadstatus[0]
        imgfile3 = request.FILES.get("image3")
        if imgfile3:
            mimetype = imgfile3.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image3' in request.FILES.keys():
                image3name = request.FILES['image3'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + geventobj.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + geventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image3'], imagelocation, image3name)
            artwork.image3 = uploadstatus[0]
        imgfile4 = request.FILES.get("image4")
        if imgfile4:
            mimetype = imgfile4.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image4' in request.FILES.keys():
                image4name = request.FILES['image4'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + geventobj.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + geventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image4'], imagelocation, image4name)
            artwork.image4 = uploadstatus[0]
        try:
            artwork.save()
            message = "Successfully added artwork named '%s'"%artworkname.title()
        except:
            message = "Error: Could not create artwork - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)


@login_required(login_url='/admin/login/')
def searchartworks(request):
    if request.method == 'GET':
        context = {}
        searchkey = request.GET.get('searchkey')
        artworksqset = Artwork.objects.filter(artworkname__icontains=searchkey)
        artworks = {}
        for art in artworksqset:
            artworks[art.artworkname] = art.id
        artworksjson = json.dumps(artworks)
        return HttpResponse(artworksjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def editartwork(request):
    if request.method == 'GET':
        context = {}
        awid = request.GET.get('awid')
        awqset = Artwork.objects.filter(id=awid)
        if awqset.__len__() == 0:
            message = {'Error' : 'Could not find artwork with Id %s'%awid}
            resp = json.dumps(message)
            return HttpResponse(resp)
        artwork = {}
        gevents = {}
        galleriesdict = {}
        artwork['artworkname'] = awqset[0].artworkname
        artwork['creationdate'] = awqset[0].creationdate
        artwork['gallery'] = awqset[0].gallery.id
        artwork['event'] = awqset[0].event.id
        artwork['artistname'] = awqset[0].artistname
        artwork['artistbirthyear'] = awqset[0].artistbirthyear
        artwork['artistdeathyear'] = awqset[0].artistdeathyear
        artwork['artistnationality'] = str(awqset[0].artistnationality)
        artwork['size'] = str(awqset[0].size)
        artwork['estimate'] = awqset[0].estimate
        artwork['soldprice'] = awqset[0].soldprice
        artwork['medium'] = awqset[0].medium
        artwork['signature'] = awqset[0].signature
        artwork['letterofauthenticity'] = awqset[0].letterofauthenticity
        artwork['description'] = awqset[0].description
        artwork['provenance'] = awqset[0].provenance
        artwork['literature'] = awqset[0].literature
        artwork['exhibitions'] = awqset[0].exhibitions
        artwork['priority'] = awqset[0].priority
        artwork['workurl'] = awqset[0].workurl
        artwork['image1'] = awqset[0].image1
        artwork['image2'] = awqset[0].image2
        artwork['image3'] = awqset[0].image3
        artwork['image4'] = awqset[0].image4
        artwork['id'] = awqset[0].id
        context['artwork'] = artwork
        galqset = Gallery.objects.filter(id=awqset[0].gallery.id)
        galobj = galqset[0]
        geventsqset = Event.objects.filter(gallery=galobj)
        for gev in geventsqset:
            gevents[gev.eventname] = gev.id
        context['gevents'] = gevents
        galleriesqset = Gallery.objects.all()
        for gal in galleriesqset:
            galname = gal.galleryname
            galid = gal.id
            galleriesdict[galname] = galid
        context['galleriesdict'] = galleriesdict
        galleryjson = json.dumps(context)
        return HttpResponse(galleryjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def saveartwork(request):
    if request.method == 'POST':
        artworkname, artistname, galleryid, eventid, artistbirth, artistdeath, artistnationality, medium, size, artworkdescription, signature, authenticity, estimate, soldprice, provenance, literature, exhibitions, artworkurl, priority, awid = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
        if 'artworkname' in request.POST.keys():
            artworkname = request.POST['artworkname'].strip()
        if 'artistname' in request.POST.keys():
            artistname = request.POST['artistname'].strip()
        if 'galleryid' in request.POST.keys():
            galleryid = request.POST['galleryid'].strip()
        if 'eventid' in request.POST.keys():
            eventid = request.POST['eventid'].strip()
        if 'artistbirth' in request.POST.keys():
            artistbirth = request.POST['artistbirth'].strip()
        if 'artistdeath' in request.POST.keys():
            artistdeath = request.POST['artistdeath'].strip()
        if 'artistnationality' in request.POST.keys():
            artistnationality = request.POST['artistnationality']
        if 'medium' in request.POST.keys():
            medium = request.POST['medium']
        if 'size' in request.POST.keys():
            size = request.POST['size']
        if 'artworkdescription' in request.POST.keys():
            artworkdescription = request.POST['artworkdescription']
        if 'signature' in request.POST.keys():
            signature = request.POST['signature']
        if 'authenticity' in request.POST.keys():
            authenticity = request.POST['authenticity']
        if 'estimate' in request.POST.keys():
            estimate = request.POST['estimate']
        if 'soldprice' in request.POST.keys():
            soldprice = request.POST['soldprice']
        if 'provenance' in request.POST.keys():
            provenance = request.POST['provenance']
        if 'literature' in request.POST.keys():
            literature = request.POST['literature']
        if 'exhibitions' in request.POST.keys():
            exhibitions = request.POST['exhibitions']
        if 'artworkurl' in request.POST.keys():
            artworkurl = request.POST['artworkurl']
        if 'priority' in request.POST.keys():
            priority = request.POST['priority']
        if 'awid' in request.POST.keys():
            awid = request.POST['awid']
        if artworkname == "" or artistname == "":
            message = "Artwork name or Artist's name is empty. Can't create Artwork."
            return HttpResponse(message)
        galleryobj = None
        try:
            galleryobj = Gallery.objects.get(id=galleryid)
        except:
            message = "Could not find gallery with Id %s"%galleryid
            #return HttpResponse(message)
        geventobj = None
        try:
            geventobj = Event.objects.get(id=eventid)
        except:
            message = "Could not find event with Id %s"%eventid
            #return HttpResponse(message)
        artworkqset = Artwork.objects.filter(id=awid)
        artwork = None
        if artworkqset.__len__() == 0:
            return HttpResponse("Could not find artwork with Id %s"%awid)
        artwork = artworkqset[0]
        artwork.artworkname = artworkname.title()
        artwork.gallery = galleryobj
        artwork.event = geventobj
        artwork.artistname = artistname
        artwork.artistbirthyear = artistbirth
        artwork.artistdeathyear = artistdeath
        artwork.artistnationality = artistnationality
        artwork.size = size
        artwork.estimate = estimate
        artwork.soldprice = soldprice
        artwork.medium = medium
        artwork.signature = signature
        artwork.letterofauthenticity = authenticity
        artwork.description = artworkdescription
        artwork.provenance = provenance
        artwork.literature = literature
        artwork.exhibitions = exhibitions
        artwork.workurl = artworkurl
        artwork.priority = priority
        artwork.creationdate = ""
        if artwork.priority == "":
            artwork.priority = 1
        imgfile1 = request.FILES.get("image1")
        if imgfile1:
            mimetype = imgfile1.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image1' in request.FILES.keys():
                image1name = request.FILES['image1'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + geventobj.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + geventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image1'], imagelocation, image1name)
            artwork.image1 = uploadstatus[0]
        imgfile2 = request.FILES.get("image1")
        if imgfile2:
            mimetype = imgfile2.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image2' in request.FILES.keys():
                image2name = request.FILES['image2'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + geventobj.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + geventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image2'], imagelocation, image2name)
            artwork.image2 = uploadstatus[0]
        imgfile3 = request.FILES.get("image3")
        if imgfile3:
            mimetype = imgfile3.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image3' in request.FILES.keys():
                image3name = request.FILES['image3'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + geventobj.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + geventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image3'], imagelocation, image3name)
            artwork.image3 = uploadstatus[0]
        imgfile4 = request.FILES.get("image4")
        if imgfile4:
            mimetype = imgfile4.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image4' in request.FILES.keys():
                image4name = request.FILES['image4'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + geventobj.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + geventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image4'], imagelocation, image4name)
            artwork.image4 = uploadstatus[0]
        try:
            artwork.save()
            message = "Successfully saved artwork named '%s'"%artworkname.title()
        except:
            message = "Error: Could not create artwork - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)
    else:
        return HttpResponse("Invalid method of call")


@csrf_protect
@login_required(login_url='/admin/login/')
def getevents(request):
    if request.method == 'POST':
        context = {}
        gid = "-1"
        requestbody = str(request.body)
        bodycomponents = requestbody.split("&")
        requestdict = {}
        for comp in bodycomponents:
            compparts = comp.split("=")
            if compparts.__len__() > 1:
                compparts[0] = compparts[0].replace("b'", "")
                requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
        if 'gid' in requestdict.keys():
            gid = requestdict['gid']
        galleriesqset = Gallery.objects.filter(id=gid)
        galleryobj = None
        if galleriesqset.__len__() > 0:
            galleryobj = galleriesqset[0]
        eventsqset = Event.objects.filter(gallery=galleryobj)
        eventsdict = {}
        for event in eventsqset:
            eventsdict[event.eventname] = event.id
        return HttpResponse(json.dumps(eventsdict))
    else:
        return HttpResponse(json.dumps({}))


@login_required(login_url='/admin/login/')
def artists(request):
    if request.method == 'GET':
        context = {}
        galleriesqset = Gallery.objects.all()
        galleriesdict = {}
        for gallery in galleriesqset:
            galleriesdict[gallery.galleryname] = gallery.id
        context['galleriesdict'] = galleriesdict
        eventsqset = Event.objects.all()
        eventsdict = {}
        for ev in eventsqset:
            eventsdict[ev.eventname] = ev.id
        context['eventsdict'] = eventsdict
        template = loader.get_template('artists.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        artistname, artistnationality, aboutartist, artistbirth, artistdeath, artistgender, artistevent, artistpriority, artistprofileurl = "", "", "", "", "", "", "", "", ""
        if 'artistname' in request.POST.keys():
            artistname = request.POST['artistname'].strip()
        if 'artistnationality' in request.POST.keys():
            artistnationality = request.POST['artistnationality'].strip()
        if 'aboutartist' in request.POST.keys():
            aboutartist = request.POST['aboutartist'].strip()
        if 'artistbirth' in request.POST.keys():
            artistbirth = request.POST['artistbirth'].strip()
        if 'artistdeath' in request.POST.keys():
            artistdeath = request.POST['artistdeath'].strip()
        if 'selgender' in request.POST.keys():
            artistgender = request.POST['selgender'].strip()
        if 'seleventname' in request.POST.keys():
            artistevent = request.POST['seleventname'].strip()
        if 'selartistpriority' in request.POST.keys():
            artistpriority = request.POST['selartistpriority']
        if 'artistprofileurl' in request.POST.keys():
            artistprofileurl = request.POST['artistprofileurl']
        if artistname == "":
            message = "Artist's name is empty. Can't create Artist."
            return HttpResponse(message)
        eventobj = None
        try:
            eventobj = Event.objects.get(id=artistevent)
        except:
            pass
        artist = Artist()
        artist.artistname = artistname
        artist.nationality = artistnationality
        artist.birthdate = artistbirth
        artist.deathdate = artistdeath
        artist.about = aboutartist
        artist.profileurl = artistprofileurl
        artist.gender = artistgender
        artist.event = eventobj
        artist.priority = artistpriority
        artist.profileurl = artistprofileurl
        artistcoverimage = request.FILES.get("artistcoverimage")
        if artistcoverimage:
            mimetype = artistcoverimage.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'artistcoverimage' in request.FILES.keys():
                coverimagename = request.FILES['artistcoverimage'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + eventobj.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + eventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['artistcoverimage'], imagelocation, coverimagename)
            artist.squareimage = uploadstatus[0]
        artistlargeimage = request.FILES.get("artistlargeimage")
        if artistlargeimage:
            mimetype = artistlargeimage.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'artistlargeimage' in request.FILES.keys():
                largeimagename = request.FILES['artistlargeimage'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + eventobj.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + eventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['artistlargeimage'], imagelocation, largeimagename)
            artist.largeimage = uploadstatus[0]
        try:
            artist.save()
            message = "Successfully created artist named %s"%artistname
        except:
            message = "Could not create artist object - Error: %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)


@login_required(login_url='/admin/login/')
def searchartists(request):
    if request.method == 'GET':
        context = {}
        searchkey = request.GET.get('searchkey')
        artistsqset = Artist.objects.filter(artistname__icontains=searchkey)
        artists = {}
        for art in artistsqset:
            artists[art.artistname] = art.id
        artistsjson = json.dumps(artists)
        #print(artistsjson)
        return HttpResponse(artistsjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def editartist(request):
    if request.method == 'GET':
        context = {}
        aid = request.GET.get('aid')
        artistqset = Artist.objects.filter(id=aid)
        if artistqset.__len__() == 0:
            message = {'Error' : 'Could not find artist with Id %s'%aid}
            resp = json.dumps(message)
            return HttpResponse(resp)
        artistsdict = {}
        eventsdict = {}
        artistsdict['artistname'] = artistqset[0].artistname
        artistsdict['nationality'] = artistqset[0].nationality
        artistsdict['about'] = artistqset[0].about
        artistsdict['eventid'] = artistqset[0].event.id
        artistsdict['artistbirth'] = artistqset[0].birthdate
        artistsdict['artistdeath'] = artistqset[0].deathdate
        artistsdict['gender'] = artistqset[0].gender
        artistsdict['artistprofileurl'] = str(artistqset[0].profileurl)
        artistsdict['priority'] = str(artistqset[0].priority)
        artistsdict['id'] = artistqset[0].id
        context['artistsdict'] = artistsdict
        geventsqset = Event.objects.filter(gallery=artistqset[0].event.gallery.id)
        for gev in geventsqset:
            eventsdict[gev.eventname] = gev.id
        context['eventsdict'] = eventsdict
        artistjson = json.dumps(context)
        return HttpResponse(artistjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def saveartist(request):
    if request.method == 'POST':
        artistname, aboutartist, artistnationality, artistbirth, artistdeath, artistgender, priority, artisturl = "", "", "", "", "", "", "", ""
        eventid = ""
        if 'artistname' in request.POST.keys():
            artistname = request.POST['artistname'].strip()
        if 'aboutartist' in request.POST.keys():
            aboutartist = request.POST['aboutartist'].strip()
        if 'artistnationality' in request.POST.keys():
            artistnationality = request.POST['artistnationality'].strip()
        if 'artistbirth' in request.POST.keys():
            artistbirth = request.POST['artistbirth'].strip()
        if 'artistdeath' in request.POST.keys():
            artistdeath = request.POST['artistdeath'].strip()
        if 'selgender' in request.POST.keys():
            artistgender = request.POST['selgender'].strip()
        if 'seleventname' in request.POST.keys():
            eventid = request.POST['seleventname']
        if 'selartistpriority' in request.POST.keys():
            priority = request.POST['selartistpriority']
        if 'artistprofileurl' in request.POST.keys():
            artisturl = request.POST['artistprofileurl']
        if 'aid' in request.POST.keys():
            aid = request.POST['aid']
        if artistname == "":
            message = "Artist name is empty. Can't save Artist."
            return HttpResponse(message)
        gevent = None
        try:
            gevent = Event.objects.get(id=eventid)
        except:
            message = "Could not find event with Id %s"%eventid
            return HttpResponse(message)
        artistobj = None
        try:
            artistobj = Artist.objects.get(id=aid)
        except:
            message = "Could not find artist with Id %s"%aid
            return HttpResponse(message)
        artistobj.artistname = artistname.title()
        artistobj.nationality = artistnationality
        artistobj.birthdate = artistbirth
        artistobj.deathdate = artistdeath
        artistobj.about = aboutartist
        artistobj.profileurl = artisturl
        artistobj.gender = artistgender
        artistobj.event = gevent
        artistobj.priority = priority
        if artistobj.priority == "":
            artistobj.priority = 1
        imgfile = request.FILES.get("artistcoverimage")
        if imgfile:
            mimetype = imgfile.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'artistcoverimage' in request.FILES.keys():
                coverimage = request.FILES['artistcoverimage'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + gevent.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + gevent.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['artistcoverimage'], imagelocation, coverimage)
            artistobj.squareimage = uploadstatus[0]
        imgfile = request.FILES.get("artistlargeimage")
        if imgfile:
            mimetype = imgfile.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'artistlargeimage' in request.FILES.keys():
                largeimage = request.FILES['artistlargeimage'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + gevent.gallery.galleryname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + gevent.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['artistlargeimage'], imagelocation, largeimage)
            artistobj.largeimage = uploadstatus[0]
        try:
            artistobj.save()
            message = "Successfully saved artist named '%s'"%artistobj.artistname.title()
        except:
            message = "Error: Could not save artist - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)
    else:
        return HttpResponse("Error: Invalid method of call")


@login_required(login_url='/admin/login/')
def museums(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('museums.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


@login_required(login_url='/admin/login/')
def mevents(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('mevents.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


@login_required(login_url='/admin/login/')
def museumpieces(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('museumpieces.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


@login_required(login_url='/admin/login/')
def auctionhouses(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('auctionhouses.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


@login_required(login_url='/admin/login/')
def auctions(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('auctions.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


@login_required(login_url='/admin/login/')
def lots(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('lots.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass



