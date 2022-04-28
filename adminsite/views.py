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
import shutil
from PIL import Image

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


def resizeimage(imgfilepath, mediadir, targetwidth=1600, targetheight=500):
    im = Image.open(imgfilepath)
    imheight, imwidth = im.size[1], im.size[0]
    resizeheight, resizewidth = targetheight, targetwidth
    if imheight > targetheight:
        resizeheight = targetheight
        resizewidth = resizeheight * imwidth/imheight
    if imwidth > targetwidth:
        resizewidth = targetwidth
        resizeheight = resizewidth * imheight/imwidth
    resized_im = im.resize((int(resizewidth),int(resizeheight)), Image.ANTIALIAS)
    inputfilename = os.path.basename(imgfilepath)
    imgtype = im.format
    if imgtype == 'JPEG':
        outputfilename = inputfilename.split(".")[0] + "_resized.jpg"
    elif imgtype == 'GIF':
        outputfilename = inputfilename.split(".")[0] + "_resized.gif"
    elif imgtype == 'PNG':
        outputfilename = inputfilename.split(".")[0] + "_resized.png"
    else:
        print("Image type is not supported.")
        return None
    outfilepath = mediadir + os.path.sep + outputfilename
    #Save the cropped image
    resized_im.save(outfilepath)
    return outfilepath


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
@csrf_protect
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
            gallery.priority = 5
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
        resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
        imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
        if imagepathparts.__len__() > 0:
            imagepath = settings.MEDIA_URL + imagepathparts[1]
        else:
            imagepath = resizedimagefile
        gallery.coverimage = imagepath
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
            gallery.priority = 5
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
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            gallery.coverimage = imagepath
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
        galleriesqset = Gallery.objects.filter(galleryname__icontains=searchkey).order_by('-edited')
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
        if geventstatus == "":
            geventstatus = "upcoming"
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
            gevent.priority = 5
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
        resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
        imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
        if imagepathparts.__len__() > 0:
            imagepath = settings.MEDIA_URL + imagepathparts[1]
        else:
            imagepath = resizedimagefile
        gevent.eventimage = imagepath
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
        geventsqset = Event.objects.filter(eventname__icontains=searchkey).order_by('-edited')
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
        if geventstatus == "":
            geventstatus = "upcoming"
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
            gevent.priority = 5
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
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            gevent.eventimage = imagepath
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
        artwork.artistname = artistname.title()
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
        artistimage = ""
        if artwork.priority == "":
            artwork.priority = 5
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
            if 'image1' in request.FILES.keys():
                uploadstatus = handleuploadedfile(request.FILES['image1'], imagelocation, image1name)
                resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
                imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
                if imagepathparts.__len__() > 0:
                    imagepath = settings.MEDIA_URL + imagepathparts[1]
                else:
                    imagepath = resizedimagefile
                artwork.image1 = imagepath
                artistimage = artwork.image1
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
            if 'image2' in request.FILES.keys():
                uploadstatus = handleuploadedfile(request.FILES['image2'], imagelocation, image2name)
                resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
                imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
                if imagepathparts.__len__() > 0:
                    imagepath = settings.MEDIA_URL + imagepathparts[1]
                else:
                    imagepath = resizedimagefile
                artwork.image2 = imagepath
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
            if 'image3' in request.FILES.keys():
                uploadstatus = handleuploadedfile(request.FILES['image3'], imagelocation, image3name)
                resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
                imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
                if imagepathparts.__len__() > 0:
                    imagepath = settings.MEDIA_URL + imagepathparts[1]
                else:
                    imagepath = resizedimagefile
                artwork.image3 = imagepath
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
            if 'image4' in request.FILES.keys():
                uploadstatus = handleuploadedfile(request.FILES['image4'], imagelocation, image4name)
                resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
                imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
                if imagepathparts.__len__() > 0:
                    imagepath = settings.MEDIA_URL + imagepathparts[1]
                else:
                    imagepath = resizedimagefile
                artwork.image4 = imagepath
        # Check if the given artist exists in the Artist model
        artistobj = None
        try:
            artistobj = Artist.objects.get(artistname=artistname.title())
        except:
            pass
        if not artistobj: # If the artist doesn't exist...
            artistobj = Artist() # ... then create an Artist record
            artistobj.artistname = artistname.title()
            artistobj.birthdate = artistbirth
            artistobj.deathdate = artistdeath
            artistobj.nationality = artistnationality
            artistobj.about = ""
            artistobj.squareimage = artistimage
            artistobj.largeimage = artistimage
            artistobj.event = geventobj # This is the gallery event associated with the artwork being processed
            artistobj.priority = priority # Priority of this artist will be the same as the priority of the artwork.
        else: # Artist by the given name already exists
            pass
        try:
            artwork.save()
            artistobj.save()
            message = "Successfully added artwork named '%s'"%artworkname.title()
        except:
            message = "Error: Could not create artwork - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)


@login_required(login_url='/admin/login/')
def searchartworks(request):
    if request.method == 'GET':
        context = {}
        searchkey = request.GET.get('searchkey')
        artworksqset = Artwork.objects.filter(artworkname__icontains=searchkey).order_by('-edited')
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
        artwork.artistname = artistname.title()
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
            artwork.priority = 5
        artistimage = ""
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
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image1 = imagepath
            artistimage = artwork.image1
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
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image2 = imagepath
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
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image3 = imagepath
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
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image4 = imagepath
        # Check if the given artist exists in the Artist model
        artistobj = None
        try:
            artistobj = Artist.objects.get(artistname=artistname.title())
        except:
            artistobj = Artist() # Create an Artist record
            artistobj.artistname = artistname.title()
            artistobj.birthdate = artistbirth
            artistobj.deathdate = artistdeath
            artistobj.nationality = artistnationality
            artistobj.about = ""
            artistobj.squareimage = artistimage # Artist image is the same as the first image of this artwork.
            artistobj.largeimage = artistimage
            artistobj.event = geventobj # This is the gallery event associated with the artwork being processed
            artistobj.priority = priority # Priority of this artist will be the same as the priority of the artwork.
        try:
            artwork.save()
            artistobj.save()
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
        artist.artistname = artistname.title()
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
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artist.squareimage = imagepath
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
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artist.largeimage = imagepath
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
        artistsqset = Artist.objects.filter(artistname__icontains=searchkey).order_by('-edited')
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
        try:
            artistsdict['eventid'] = artistqset[0].event.id
        except:
            artistsdict['eventid'] = ""
        artistsdict['artistbirth'] = artistqset[0].birthdate
        artistsdict['artistdeath'] = artistqset[0].deathdate
        artistsdict['gender'] = artistqset[0].gender
        artistsdict['artistprofileurl'] = str(artistqset[0].profileurl)
        artistsdict['priority'] = str(artistqset[0].priority)
        artistsdict['id'] = artistqset[0].id
        artistsdict['squareimage'] = artistqset[0].squareimage
        artistsdict['largeimage'] = artistqset[0].largeimage
        context['artistsdict'] = artistsdict
        try:
            geventsqset = Event.objects.filter(gallery=artistqset[0].event.gallery.id)
        except:
            geventsqset = Event.objects.all()
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
            artistobj.priority = 5
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
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artistobj.squareimage = imagepath
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
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artistobj.largeimage = imagepath
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
        mtypesqset = Museum.objects.order_by().values_list('museumtype').distinct()
        museumtypes = []
        for mtype in mtypesqset:
            museumtypes.append(mtype[0])
        context['museumtypes'] = museumtypes
        template = loader.get_template('museums.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        museumname, museumlocation, museumdescription, museumwebsite, selmuseumtype, museumtype, museumcoverimage, selmuseumpriority = "", "", "", "", "", "", "", ""
        if 'museumname' in request.POST.keys():
            museumname = request.POST['museumname'].strip()
        if 'museumlocation' in request.POST.keys():
            museumlocation = request.POST['museumlocation'].strip()
        if 'museumdescription' in request.POST.keys():
            museumdescription = request.POST['museumdescription'].strip()
        if 'museumwebsite' in request.POST.keys():
            museumwebsite = request.POST['museumwebsite'].strip()
        if 'selmuseumtype' in request.POST.keys():
            selmuseumtype = request.POST['selmuseumtype'].strip()
        if 'museumtype' in request.POST.keys():
            museumtype = request.POST['museumtype'].strip()
        if 'selmuseumpriority' in request.POST.keys():
            selmuseumpriority = request.POST['selmuseumpriority']
        if selmuseumtype == "":
            selmuseumtype = museumtype
        if museumname == "" or selmuseumtype == "":
            message = "Museum name or museum type is empty. Can't create museum."
            return HttpResponse(message)
        museum = Museum()
        #print(museumname + " ########")
        museum.museumname = museumname.title()
        museum.location = museumlocation
        museum.description = museumdescription
        museum.museumurl = museumwebsite
        museum.museumtype = selmuseumtype
        museum.slug = ""
        museum.priority = selmuseumpriority
        if museum.priority == "":
            museum.priority = 5
        imgfile = request.FILES.get("museumcoverimage")
        mimetype = imgfile.content_type
        if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
            return None
        if 'museumcoverimage' in request.FILES.keys():
            coverimage = request.FILES['museumcoverimage'].name
        imagelocation = settings.MUSEUM_FILE_DIR + os.path.sep + museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
        if not os.path.exists(imagelocation):
            mkdir_p(imagelocation)
        uploadstatus = handleuploadedfile(request.FILES['museumcoverimage'], imagelocation, coverimage)
        resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
        imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
        if imagepathparts.__len__() > 0:
            imagepath = settings.MEDIA_URL + imagepathparts[1]
        else:
            imagepath = resizedimagefile
        museum.coverimage = imagepath
        try:
            museum.save()
            message = "Successfully created museum named '%s'"%museumname.title()
        except:
            message = "Error: Could not create museum - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)


@login_required(login_url='/admin/login/')
def searchmuseum(request):
    if request.method == 'GET':
        context = {}
        searchkey = request.GET.get('searchkey')
        museumsqset = Museum.objects.filter(museumname__icontains=searchkey).order_by('-edited')
        museums = {}
        for mus in museumsqset:
            museums[mus.museumname] = mus.id
        museumsjson = json.dumps(museums)
        #print(museumsjson)
        return HttpResponse(museumsjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def editmuseum(request):
    if request.method == 'GET':
        context = {}
        mid = request.GET.get('mid')
        museumsqset = Museum.objects.filter(id=mid)
        if museumsqset.__len__() == 0:
            message = {'Error' : 'Could not find museum with Id %s'%mid}
            resp = json.dumps(message)
            return HttpResponse(resp)
        museum = {}
        museumtypes = []
        museum['museumname'] = museumsqset[0].museumname
        museum['location'] = museumsqset[0].location
        museum['description'] = museumsqset[0].description
        museum['museumurl'] = museumsqset[0].museumurl
        museum['museumtype'] = museumsqset[0].museumtype
        museum['priority'] = museumsqset[0].priority
        museum['coverimage'] = museumsqset[0].coverimage
        museum['id'] = museumsqset[0].id
        context['museum'] = museum
        mtypesqset = Museum.objects.order_by().values_list('museumtype').distinct()
        museumtypes = []
        for mtype in mtypesqset:
            museumtypes.append(mtype[0])
        context['museumtypes'] = museumtypes
        museumjson = json.dumps(context)
        return HttpResponse(museumjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def savemuseum(request):
    if request.method == 'POST':
        museumname, museumlocation, museumdescription, museumwebsite, selmuseumtype, museumtype, museumcoverimage, selmuseumpriority, musid = "", "", "", "", "", "", "", "", ""
        if 'museumname' in request.POST.keys():
            museumname = request.POST['museumname'].strip()
        if 'museumlocation' in request.POST.keys():
            museumlocation = request.POST['museumlocation'].strip()
        if 'museumdescription' in request.POST.keys():
            museumdescription = request.POST['museumdescription'].strip()
        if 'museumwebsite' in request.POST.keys():
            museumwebsite = request.POST['museumwebsite'].strip()
        if 'selmuseumtype' in request.POST.keys():
            selmuseumtype = request.POST['selmuseumtype'].strip()
        if 'museumtype' in request.POST.keys():
            museumtype = request.POST['museumtype'].strip()
        if 'selmuseumpriority' in request.POST.keys():
            selmuseumpriority = request.POST['selmuseumpriority']
        if selmuseumtype == "":
            selmuseumtype = museumtype
        if museumname == "" or selmuseumtype == "":
            message = "Museum name or museum type is empty. Can't save museum."
            return HttpResponse(message)
        if 'mid' in request.POST.keys():
            musid = request.POST['mid'].strip()
        museum = None
        try:
            museum = Museum.objects.get(id=musid)
        except:
            return HttpResponse("Museum with the given Id could not be found")
        museum.museumname = museumname.title()
        museum.location = museumlocation
        museum.description = museumdescription
        #print(museumdescription)
        museum.museumurl = museumwebsite
        museum.museumtype = selmuseumtype
        museum.slug = ""
        museum.priority = selmuseumpriority
        if museum.priority == "":
            museum.priority = 5
        imgfile = request.FILES.get("museumcoverimage")
        if imgfile:
            mimetype = imgfile.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'museumcoverimage' in request.FILES.keys():
                coverimage = request.FILES['museumcoverimage'].name
            imagelocation = settings.MUSEUM_FILE_DIR + os.path.sep + museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['museumcoverimage'], imagelocation, coverimage)
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            museum.coverimage = imagepath
        try:
            museum.save()
            message = "Successfully saved changes to museum named '%s'"%museumname.title()
        except:
            message = "Error: Could not save changes to museum - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)
    else:
        return HttpResponse("Error: Invalid method of call")


@login_required(login_url='/admin/login/')
def mevents(request):
    if request.method == 'GET':
        context = {}
        museumsqset = Museum.objects.all()
        museumsdict = {}
        for museum in museumsqset:
            museumsdict[museum.museumname] = museum.id
        context['museumsdict'] = museumsdict
        eventsqset = MuseumEvent.objects.order_by().values_list('eventtype').distinct()
        allevents = []
        for mev in eventsqset:
            allevents.append(mev[0])
        context['allevents'] = allevents
        template = loader.get_template('mevents.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        meventname, meventlocation, meventinfo, meventstatus, selmeventtype, meventtype, meventcoverimage, selmeventpriority, meventstartdate, meventenddate, museumid = "", "", "", "", "", "", "", "", "", "", ""
        if 'meventname' in request.POST.keys():
            meventname = request.POST['meventname'].strip()
        if 'meventlocation' in request.POST.keys():
            meventlocation = request.POST['meventlocation'].strip()
        if 'meventinfo' in request.POST.keys():
            meventinfo = request.POST['meventinfo'].strip()
        if 'meventstartdate' in request.POST.keys():
            meventstartdate = request.POST['meventstartdate'].strip()
        if 'meventenddate' in request.POST.keys():
            meventenddate = request.POST['meventenddate'].strip()
        if 'selmeventtype' in request.POST.keys():
            selmeventtype = request.POST['selmeventtype'].strip()
        if 'selmeventpriority' in request.POST.keys():
            selmeventpriority = request.POST['selmeventpriority']
        if 'selmeventstatus' in request.POST.keys():
            meventstatus = request.POST['selmeventstatus']
        if 'selmuseumname' in request.POST.keys():
            museumid = request.POST['selmuseumname']
        if meventname == "" or selmeventtype == "":
            message = "Event name or event type is empty. Can't create Event."
            return HttpResponse(message)
        if meventstatus == "":
            meventstatus = "upcoming"
        museumobj = None
        try:
            museumobj = Museum.objects.get(id=museumid)
        except:
            message = "Could not find museum with Id %s"%museumid
            return HttpResponse(message)
        mevent = MuseumEvent()
        mevent.eventname = meventname.title()
        mevent.eventinfo = meventinfo
        mevent.eventtype = selmeventtype
        mevent.eventstatus = meventstatus
        mevent.eventstartdate = meventstartdate
        mevent.eventenddate = meventenddate
        mevent.museum = museumobj
        mevent.priority = selmeventpriority
        mevent.eventperiod = meventstartdate + " - " + meventenddate
        if mevent.priority == "":
            mevent.priority = 5
        imgfile = request.FILES.get("meventcoverimage")
        mimetype = imgfile.content_type
        if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
            return None
        if 'meventcoverimage' in request.FILES.keys():
            coverimage = request.FILES['meventcoverimage'].name
        imagelocation = settings.MUSEUM_FILE_DIR + os.path.sep + mevent.museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + mevent.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
        if not os.path.exists(imagelocation):
            mkdir_p(imagelocation)
        uploadstatus = handleuploadedfile(request.FILES['meventcoverimage'], imagelocation, coverimage)
        resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
        imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
        if imagepathparts.__len__() > 0:
            imagepath = settings.MEDIA_URL + imagepathparts[1]
        else:
            imagepath = resizedimagefile
        mevent.coverimage = imagepath
        try:
            mevent.save()
            message = "Successfully created museum event named '%s'"%meventname.title()
        except:
            message = "Error: Could not create museum event - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)


@login_required(login_url='/admin/login/')
def searchmevents(request):
    if request.method == 'GET':
        context = {}
        searchkey = request.GET.get('searchkey')
        meventsqset = MuseumEvent.objects.filter(eventname__icontains=searchkey).order_by('-edited')
        mevents = {}
        for mev in meventsqset:
            mevents[mev.eventname] = mev.id
        mevjson = json.dumps(mevents)
        return HttpResponse(mevjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def editmevent(request):
    if request.method == 'GET':
        context = {}
        mevid = request.GET.get('evid')
        meventsqset = MuseumEvent.objects.filter(id=mevid)
        if meventsqset.__len__() == 0:
            message = {'Error' : 'Could not find event with Id %s'%mevid}
            resp = json.dumps(message)
            return HttpResponse(resp)
        mevent = {}
        meventtypes = []
        museumsdict = {}
        mevent['eventname'] = meventsqset[0].eventname
        mevent['eventinfo'] = meventsqset[0].eventinfo
        mevent['eventtype'] = meventsqset[0].eventtype
        mevent['eventurl'] = meventsqset[0].eventurl
        mevent['eventstatus'] = meventsqset[0].eventstatus
        mevent['priority'] = meventsqset[0].priority
        mevent['eventstartdate'] = str(meventsqset[0].eventstartdate)
        mevent['eventenddate'] = str(meventsqset[0].eventenddate)
        mevent['coverimage'] = meventsqset[0].coverimage
        mevent['museumname'] = meventsqset[0].museum.museumname
        mevent['id'] = meventsqset[0].id
        context['mevent'] = mevent
        mevtypesqset = MuseumEvent.objects.order_by().values_list('eventtype').distinct()
        for mtype in mevtypesqset:
            meventtypes.append(mtype[0])
        context['meventtypes'] = meventtypes
        museumsqset = Museum.objects.all()
        for mus in museumsqset:
            musname = mus.museumname
            musid = mus.id
            museumsdict[musname] = musid
        context['museumsdict'] = museumsdict
        museumjson = json.dumps(context)
        return HttpResponse(museumjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def savemevent(request):
    if request.method == 'POST':
        meventname, meventlocation, meventinfo, meventstatus, selmeventtype, meventtype, meventcoverimage, selmeventpriority, meventstartdate, meventenddate, museumid, mevid = "", "", "", "", "", "", "", "", "", "", "", ""
        if 'meventname' in request.POST.keys():
            meventname = request.POST['meventname'].strip()
        if 'meventlocation' in request.POST.keys():
            meventlocation = request.POST['meventlocation'].strip()
        if 'meventinfo' in request.POST.keys():
            meventinfo = request.POST['meventinfo'].strip()
        if 'meventstartdate' in request.POST.keys():
            meventstartdate = request.POST['meventstartdate'].strip()
        if 'meventenddate' in request.POST.keys():
            meventenddate = request.POST['meventenddate'].strip()
        if 'selmeventtype' in request.POST.keys():
            selmeventtype = request.POST['selmeventtype'].strip()
        if 'selmeventpriority' in request.POST.keys():
            selmeventpriority = request.POST['selmeventpriority']
        if 'selmeventstatus' in request.POST.keys():
            meventstatus = request.POST['selmeventstatus']
        if 'selmuseumname' in request.POST.keys():
            museumid = request.POST['selmuseumname']
        if 'mevid' in request.POST.keys():
            mevid = request.POST['mevid']
        if meventname == "" or selmeventtype == "":
            message = "Event name or event type is empty. Can't save Event."
            return HttpResponse(message)
        if meventstatus == "":
            meventstatus = "upcoming"
        museumobj = None
        try:
            museumobj = Museum.objects.get(id=museumid)
        except:
            message = "Could not find Museum with Id %s"%museumid
            return HttpResponse(message)
        mevent = None
        try:
            mevent = MuseumEvent.objects.get(id=mevid)
        except:
            message = "Could not find event with Id %s"%mevid
            return HttpResponse(message)
        mevent.eventname = meventname.title()
        mevent.eventinfo = meventinfo
        mevent.eventtype = selmeventtype
        mevent.eventstatus = meventstatus
        mevent.eventstartdate = meventstartdate
        mevent.eventenddate = meventenddate
        mevent.museum = museumobj
        mevent.priority = selmeventpriority
        mevent.eventperiod = meventstartdate + " - " + meventenddate
        if mevent.priority == "":
            mevent.priority = 5
        imgfile = request.FILES.get("meventcoverimage")
        if imgfile:
            mimetype = imgfile.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'meventcoverimage' in request.FILES.keys():
                coverimage = request.FILES['meventcoverimage'].name
            imagelocation = settings.MUSEUM_FILE_DIR + os.path.sep + mevent.museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + mevent.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['meventcoverimage'], imagelocation, coverimage)
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            mevent.coverimage = imagepath
        try:
            mevent.save()
            message = "Successfully saved event named '%s'"%meventname.title()
        except:
            message = "Error: Could not save event - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)
    else:
        return HttpResponse("Error: Invalid method of call")


@login_required(login_url='/admin/login/')
def museumpieces(request):
    if request.method == 'GET':
        context = {}
        museumsqset = Museum.objects.all()
        museumsdict = {}
        for museum in museumsqset:
            museumsdict[museum.museumname] = museum.id
        context['museumsdict'] = museumsdict
        template = loader.get_template('museumpieces.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        artworkname, artistname, galleryid, eventid, artistbirth, artistdeath, artistnationality, medium, size, artworkdescription, signature, authenticity, estimate, soldprice, provenance, literature, exhibitions, artworkurl, priority = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
        if 'artworkname' in request.POST.keys():
            artworkname = request.POST['artworkname'].strip()
        if 'artistname' in request.POST.keys():
            artistname = request.POST['artistname'].strip()
        if 'selmuseumname' in request.POST.keys():
            museumid = request.POST['selmuseumname'].strip()
        if 'selmeventname' in request.POST.keys():
            eventid = request.POST['selmeventname'].strip()
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
        museumobj = None
        try:
            museumobj = Museum.objects.get(id=museumid)
        except:
            message = "Could not find museum with Id %s"%museumid
            return HttpResponse(message)
        meventobj = None
        try:
            meventobj = MuseumEvent.objects.get(id=eventid)
        except:
            message = "Could not find event with Id %s"%eventid
            return HttpResponse(message)
        artwork = MuseumPieces()
        artwork.piecename = artworkname.title()
        artwork.museum = museumobj
        artwork.event = meventobj
        artwork.artistname = artistname.title()
        artwork.artistbirthyear = artistbirth
        artwork.artistdeathyear = artistdeath
        artwork.artistnationality = artistnationality
        artwork.size = size
        #artwork.estimate = estimate
        #artwork.soldprice = soldprice
        artwork.medium = medium
        artwork.signature = signature
        #artwork.letterofauthenticity = authenticity
        artwork.description = artworkdescription
        artwork.provenance = provenance
        artwork.literature = literature
        artwork.exhibited = exhibitions
        artwork.workurl = artworkurl
        artwork.priority = priority
        artwork.creationdate = ""
        if artwork.priority == "":
            artwork.priority = 5
        imgfile1 = request.FILES.get("image1")
        artistimage = ""
        if imgfile1:
            mimetype = imgfile1.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image1' in request.FILES.keys():
                image1name = request.FILES['image1'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + meventobj.museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + meventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image1'], imagelocation, image1name)
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image1 = imagepath
            artistimage = artwork.image1
        imgfile2 = request.FILES.get("image1")
        if imgfile2:
            mimetype = imgfile2.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image2' in request.FILES.keys():
                image2name = request.FILES['image2'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + meventobj.museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + meventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image2'], imagelocation, image2name)
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image2 = imagepath
        imgfile3 = request.FILES.get("image3")
        if imgfile3:
            mimetype = imgfile3.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image3' in request.FILES.keys():
                image3name = request.FILES['image3'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + meventobj.museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + meventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image3'], imagelocation, image3name)
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image3 = imagepath
        imgfile4 = request.FILES.get("image4")
        if imgfile4:
            mimetype = imgfile4.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image4' in request.FILES.keys():
                image4name = request.FILES['image4'].name
            imagelocation = settings.GALLERY_FILE_DIR + os.path.sep + meventobj.museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + meventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image4'], imagelocation, image4name)
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image4 = imagepath
        artistobj = None
        try:
            artistobj = Artist.objects.get(artistname=artistname.title())
        except:
            pass
        if not artistobj: # If the artist doesn't exist...
            artistobj = Artist() # ... then create an Artist record
            artistobj.artistname = artistname.title()
            artistobj.birthdate = artistbirth
            artistobj.deathdate = artistdeath
            artistobj.nationality = artistnationality
            artistobj.about = ""
            artistobj.squareimage = artistimage
            artistobj.largeimage = artistimage
            artistobj.event = None # This should be a gallery event. So for museum, we set it to None
            artistobj.priority = priority # Priority of this artist will be the same as the priority of the artwork.
        else: # Artist by the given name already exists
            pass
        try:
            artwork.save()
            artistobj.save()
            message = "Successfully added artwork named '%s'"%artworkname.title()
        except:
            message = "Error: Could not create artwork - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)


@login_required(login_url='/admin/login/')
def searchmpieces(request):
    if request.method == 'GET':
        context = {}
        searchkey = request.GET.get('searchkey')
        #print(searchkey)
        artworksqset = MuseumPieces.objects.filter(piecename__icontains=searchkey).order_by('-edited')
        artworks = {}
        for art in artworksqset:
            artworks[art.piecename] = art.id
        artworksjson = json.dumps(artworks)
        return HttpResponse(artworksjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def savempieces(request):
    if request.method == 'POST':
        artworkname, artistname, museumid, eventid, artistbirth, artistdeath, artistnationality, medium, size, artworkdescription, signature, authenticity, estimate, soldprice, provenance, literature, exhibitions, artworkurl, priority, awid = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
        if 'artworkname' in request.POST.keys():
            artworkname = request.POST['artworkname'].strip()
        if 'artistname' in request.POST.keys():
            artistname = request.POST['artistname'].strip()
        if 'museumid' in request.POST.keys():
            museumid = request.POST['museumid'].strip()
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
        museumobj = None
        try:
            museumobj = Museum.objects.get(id=museumid)
        except:
            message = "Could not find museum with Id %s"%museumid
            #return HttpResponse(message)
        meventobj = None
        try:
            meventobj = MuseumEvent.objects.get(id=eventid)
        except:
            message = "Could not find event with Id %s"%eventid
            #return HttpResponse(message)
        artworkqset = MuseumPieces.objects.filter(id=awid)
        artwork = None
        if artworkqset.__len__() == 0:
            return HttpResponse("Could not find artwork with Id %s"%awid)
        artwork = artworkqset[0]
        artwork.piecename = artworkname.title()
        artwork.museum = museumobj
        artwork.event = meventobj
        artwork.artistname = artistname.title()
        artwork.artistbirthyear = artistbirth
        artwork.artistdeathyear = artistdeath
        artwork.artistnationality = artistnationality
        artwork.size = size
        #artwork.estimate = estimate
        #artwork.soldprice = soldprice
        artwork.medium = medium
        artwork.signature = signature
        #artwork.letterofauthenticity = authenticity
        artwork.description = artworkdescription
        artwork.provenance = provenance
        artwork.literature = literature
        artwork.exhibited = exhibitions
        artwork.detailurl = artworkurl
        artwork.priority = priority
        artwork.creationdate = ""
        if artwork.priority == "":
            artwork.priority = 5
        imgfile1 = request.FILES.get("image1")
        artistimage = ""
        if imgfile1:
            mimetype = imgfile1.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image1' in request.FILES.keys():
                image1name = request.FILES['image1'].name
            imagelocation = settings.MUSEUM_FILE_DIR + os.path.sep + meventobj.museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + meventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image1'], imagelocation, image1name)
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image1 = imagepath
            artistimage = artwork.image1
        imgfile2 = request.FILES.get("image1")
        if imgfile2:
            mimetype = imgfile2.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image2' in request.FILES.keys():
                image2name = request.FILES['image2'].name
            imagelocation = settings.MUSEUM_FILE_DIR + os.path.sep + meventobj.museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + meventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image2'], imagelocation, image2name)
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image2 = imagepath
        imgfile3 = request.FILES.get("image3")
        if imgfile3:
            mimetype = imgfile3.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image3' in request.FILES.keys():
                image3name = request.FILES['image3'].name
            imagelocation = settings.MUSEUM_FILE_DIR + os.path.sep + meventobj.museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + meventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image3'], imagelocation, image3name)
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image3 = imagepath
        imgfile4 = request.FILES.get("image4")
        if imgfile4:
            mimetype = imgfile4.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return None
            if 'image4' in request.FILES.keys():
                image4name = request.FILES['image4'].name
            imagelocation = settings.MUSEUM_FILE_DIR + os.path.sep + meventobj.museum.museumname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_") + os.path.sep + meventobj.eventname.replace(" ", "_").replace("'", "_").replace(",", "_").replace(".", "_")
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['image4'], imagelocation, image4name)
            resizedimagefile = resizeimage(uploadstatus[0], imagelocation, 640, 480) # Max width is 640 px.
            imagepathparts = resizedimagefile.split(settings.MEDIA_URL)
            if imagepathparts.__len__() > 0:
                imagepath = settings.MEDIA_URL + imagepathparts[1]
            else:
                imagepath = resizedimagefile
            artwork.image4 = imagepath
        artistobj = None
        try:
            artistobj = Artist.objects.get(artistname=artistname.title())
        except:
            pass
        if not artistobj: # If the artist doesn't exist...
            artistobj = Artist() # ... then create an Artist record
            artistobj.artistname = artistname.title()
            artistobj.birthdate = artistbirth
            artistobj.deathdate = artistdeath
            artistobj.nationality = artistnationality
            artistobj.about = ""
            artistobj.squareimage = artistimage
            artistobj.largeimage = artistimage
            artistobj.event = None # This should be a gallery event. So for museum, we set it to None
            artistobj.priority = priority # Priority of this artist will be the same as the priority of the artwork.
        else: # Artist by the given name already exists
            pass
        try:
            artwork.save()
            artistobj.save()
            message = "Successfully saved artwork named '%s'"%artworkname.title()
        except:
            message = "Error: Could not create artwork - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)
    else:
        return HttpResponse("Invalid method of call")


@login_required(login_url='/admin/login/')
def editmpieces(request):
    if request.method == 'GET':
        context = {}
        awid = request.GET.get('awid')
        awqset = MuseumPieces.objects.filter(id=int(awid))
        if awqset.__len__() == 0:
            message = {'Error' : 'Could not find museum piece with Id %s'%awid}
            resp = json.dumps(message)
            return HttpResponse(resp)
        artwork = {}
        mevents = {}
        museumsdict = {}
        artwork['piecename'] = awqset[0].piecename
        artwork['creationdate'] = awqset[0].creationdate
        artwork['museum'] = awqset[0].museum.id
        artwork['event'] = awqset[0].event.id
        artwork['artistname'] = awqset[0].artistname
        artwork['artistbirthyear'] = awqset[0].artistbirthyear
        artwork['artistdeathyear'] = awqset[0].artistdeathyear
        artwork['artistnationality'] = str(awqset[0].artistnationality)
        artwork['size'] = str(awqset[0].size)
        #artwork['estimate'] = awqset[0].estimate
        #artwork['soldprice'] = awqset[0].soldprice
        artwork['medium'] = awqset[0].medium
        artwork['signature'] = awqset[0].signature
        #artwork['letterofauthenticity'] = awqset[0].letterofauthenticity
        artwork['description'] = awqset[0].description
        artwork['provenance'] = awqset[0].provenance
        artwork['literature'] = awqset[0].literature
        artwork['exhibitions'] = awqset[0].exhibited
        artwork['priority'] = awqset[0].priority
        artwork['workurl'] = awqset[0].detailurl
        artwork['image1'] = awqset[0].image1
        artwork['image2'] = awqset[0].image2
        artwork['image3'] = awqset[0].image3
        artwork['image4'] = awqset[0].image4
        artwork['id'] = awqset[0].id
        context['artwork'] = artwork
        musqset = Museum.objects.filter(id=awqset[0].museum.id)
        musobj = musqset[0]
        meventsqset = MuseumEvent.objects.filter(museum=musobj)
        for mev in meventsqset:
            mevents[mev.eventname] = mev.id
        context['mevents'] = mevents
        museumsqset = Museum.objects.all()
        for mus in museumsqset:
            musname = mus.museumname
            musid = mus.id
            museumsdict[musname] = musid
        #print(museumsdict)
        context['museumsdict'] = museumsdict
        museumjson = json.dumps(context)
        return HttpResponse(museumjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def getmevents(request):
    if request.method == 'POST':
        context = {}
        mid = "-1"
        requestbody = str(request.body)
        bodycomponents = requestbody.split("&")
        requestdict = {}
        for comp in bodycomponents:
            compparts = comp.split("=")
            if compparts.__len__() > 1:
                compparts[0] = compparts[0].replace("b'", "")
                requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
        if 'mid' in requestdict.keys():
            mid = requestdict['mid']
        museumsqset = Museum.objects.filter(id=mid)
        museumobj = None
        if museumsqset.__len__() > 0:
            museumobj = museumsqset[0]
        eventsqset = MuseumEvent.objects.filter(museum=museumobj)
        eventsdict = {}
        for event in eventsqset:
            eventsdict[event.eventname] = event.id
        return HttpResponse(json.dumps(eventsdict))
    else:
        return HttpResponse(json.dumps({}))


@login_required(login_url='/admin/login/')
def webconfig(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('webconfig.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        webconfigname, webconfigvalue, webconfigdescription, webconfigpath, webconfigpagename = "", "", "", "", ""
        if 'webconfigname' in request.POST.keys():
            webconfigname = request.POST['webconfigname'].strip()
        if 'webconfigvalue' in request.POST.keys():
            webconfigvalue = request.POST['webconfigvalue'].strip()
        if 'webconfigdescription' in request.POST.keys():
            webconfigdescription = request.POST['webconfigdescription'].strip()
        if 'webconfigpath' in request.POST.keys():
            webconfigpath = request.POST['webconfigpath'].strip()
        if 'webconfigpagename' in request.POST.keys():
            webconfigpagename = request.POST['webconfigpagename'].strip()
        wcobj = WebConfig()
        wcobj.pagename = webconfigpagename
        wcobj.path = webconfigpath
        wcobj.paramname = webconfigname
        wcobj.paramvalue = webconfigvalue
        wcobj.adminuser = request.user
        try:
            wcobj.save()
        except:
            message = "Could not save configuration value. Please contact admin. Error: %s"%sys.exc_info()[1].__str__()
            return HttpResponse(message)
        message = "Saved config param '%s' successfully."%webconfigname
        return HttpResponse(message)
        


@login_required(login_url='/admin/login/')
def searchwebconfig(request):
    if request.method == 'GET':
        context = {}
        searchkey = request.GET.get('searchkey')
        #print(searchkey)
        wcqset = WebConfig.objects.filter(paramname__icontains=searchkey).order_by('-edited')
        wcdict = {}
        for wc in wcqset:
            wcdict[wc.paramname] = wc.id
        wcjson = json.dumps(wcdict)
        return HttpResponse(wcjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def savewebconfig(request):
    if request.method == 'POST':
        webconfigname, webconfigvalue, webconfigpath, webconfigpagename, webconfigdescription = "", "", "", "", ""
        wcid = None
        if 'wcid' in request.POST.keys():
            wcid = request.POST['wcid'].strip()
        if 'webconfigname' in request.POST.keys():
            webconfigname = request.POST['webconfigname'].strip()
        if 'webconfigvalue' in request.POST.keys():
            webconfigvalue = request.POST['webconfigvalue'].strip()
        if 'webconfigpath' in request.POST.keys():
            webconfigpath = request.POST['webconfigpath'].strip()
        if 'webconfigpagename' in request.POST.keys():
            webconfigpagename = request.POST['webconfigpagename'].strip()
        if 'webconfigdescription' in request.POST.keys():
            webconfigdescription = request.POST['webconfigdescription'].strip()
        if webconfigname == "":
            message = "Config param name is empty. Can't create Config Param."
            return HttpResponse(message)
        wcobj = None
        try:
            wcobj = WebConfig.objects.get(id=wcid)
        except:
            message = "Could not find WebConfig with Id %s"%wcid
            return HttpResponse(message)
        wcobj.paramname = webconfigname
        wcobj.paramvalue = webconfigvalue
        wcobj.pagename = webconfigpagename
        wcobj.path = webconfigpath
        wcobj.adminuser = request.user
        try:
            wcobj.save()
            message = "Successfully saved webconfig param named '%s'"%webconfigname
        except:
            message = "Error: Could not create webconfig param - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)
    else:
        return HttpResponse("Invalid method of call")


@login_required(login_url='/admin/login/')
def editwebconfig(request):
    if request.method == 'GET':
        context = {}
        wcid = request.GET.get('wcid')
        wcqset = WebConfig.objects.filter(id=int(wcid))
        if wcqset.__len__() == 0:
            message = {'Error' : 'Could not find webconfig with Id %s'%wcid}
            resp = json.dumps(message)
            return HttpResponse(resp)
        webconfig = {}
        webconfig['webconfigname'] = wcqset[0].paramname
        webconfig['webconfigvalue'] = wcqset[0].paramvalue
        webconfig['webconfigpath'] = wcqset[0].path
        webconfig['webconfigpagename'] = wcqset[0].pagename
        webconfig['id'] = wcqset[0].id
        context['webconfig'] = webconfig
        wcjson = json.dumps(context)
        return HttpResponse(wcjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def carousel(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('carousel.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        carouselitemname, carouselitemtext, carouselimage, seldatatype, seldataentry, selpriority = "", "", "", "", "", ""
        if 'carouselitemname' in request.POST.keys():
            carouselitemname = request.POST['carouselitemname'].strip()
        if 'carouselitemtext' in request.POST.keys():
            carouselitemtext = request.POST['carouselitemtext'].strip()
        if 'seldatatype' in request.POST.keys():
            seldatatype = request.POST['seldatatype'].strip()
        if 'seldataentry' in request.POST.keys():
            seldataentry = request.POST['seldataentry'].strip()
        if 'selpriority' in request.POST.keys():
            selpriority = request.POST['selpriority'].strip()
        carouselobj = Carousel()
        carouselimage = request.FILES.get("carouselimage")
        carouseldir = settings.MEDIA_ROOT + os.path.sep + "carousel"
        if carouselimage:
            mimetype = carouselimage.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return HttpResponse("Uploaded file is not gif, jpeg or png format.")
            if 'carouselimage' in request.FILES.keys():
                carouselimagename = request.FILES['carouselimage'].name
            imagelocation = settings.MEDIA_ROOT + os.path.sep + "carousel"
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['carouselimage'], imagelocation, carouselimagename)
            resizedimagefile = resizeimage(uploadstatus[0], carouseldir, 1500) # Max width is 1500 px.
            carouselobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
        else: # Get the image of the entry
            if seldatatype == "gallery":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = Gallery.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.coverimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carouselobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "gevent":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = Event.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.eventimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carouselobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "museum":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = Museum.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.coverimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carouselobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "mevent":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = MuseumEvent.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.coverimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carouselobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "artist":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = Artist.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.squareimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carouselobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "auction":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = Auction.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.coverimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carouselobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "auctionhouse":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = AuctionHouse.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.coverimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carouselobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
        carouselobj.textvalue = carouselitemtext
        carouselobj.title = carouselitemname
        carouselobj.datatype = seldatatype
        carouselobj.data_id = seldataentry
        carouselobj.priority = selpriority
        try:
            carouselobj.save()
        except:
            message = "Could not save carousel entry. Please contact admin. Error: %s"%sys.exc_info()[1].__str__()
            return HttpResponse(message)
        message = "Saved carousel entry '%s' successfully."%carouselitemname
        return HttpResponse(message)


@login_required(login_url='/admin/login/')
def getcarouselentries(request):
    if request.method == 'POST':
        context = {}
        cardatatype = ""
        if 'seldatatype' in request.POST.keys():
            cardatatype = request.POST['seldatatype']
        dqset = None
        cardict = {}
        if cardatatype == "gallery":
            dqset = Gallery.objects.all()
            for dq in dqset:
                dname = dq.galleryname
                did = dq.id
                cardict[dname] = did
        elif cardatatype == "gevent":
            dqset = Event.objects.all()
            for dq in dqset:
                dname = dq.eventname
                did = dq.id
                cardict[dname] = did
        elif cardatatype == "museum":
            dqset = Museum.objects.all()
            for dq in dqset:
                dname = dq.museumname
                did = dq.id
                cardict[dname] = did
        elif cardatatype == "mevent":
            dqset = MuseumEvent.objects.all()
            for dq in dqset:
                dname = dq.eventname
                did = dq.id
                cardict[dname] = did
        elif cardatatype == "artist":
            dqset = Artist.objects.all()
            for dq in dqset:
                dname = dq.artistname
                did = dq.id
                cardict[dname] = did
        elif cardatatype == "auction":
            dqset = Auction.objects.all()
            for dq in dqset:
                dname = dq.auctionname
                did = dq.id
                cardict[dname] = did
        elif cardatatype == "auctionhouse":
            dqset = AuctionHouse.objects.all()
            for dq in dqset:
                dname = dq.housename
                did = dq.id
                cardict[dname] = did
        return HttpResponse(json.dumps(cardict))
    else:
        return HttpResponse(json.dumps({}))


@login_required(login_url='/admin/login/')
def searchcarousel(request):
    if request.method == 'GET':
        context = {}
        searchkey = request.GET.get('searchkey')
        #print(searchkey)
        carqset = Carousel.objects.filter(title__icontains=searchkey).order_by('priority', '-edited')
        cardict = {}
        for car in carqset:
            cardict[car.title] = car.id
        carjson = json.dumps(cardict)
        return HttpResponse(carjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")


@login_required(login_url='/admin/login/')
def editcarousel(request):
    if request.method == 'GET':
        context = {}
        carid = request.GET.get('carid')
        carqset = Carousel.objects.filter(id=int(carid))
        if carqset.__len__() == 0:
            message = {'Error' : 'Could not find carousel with Id %s'%carid}
            resp = json.dumps(message)
            return HttpResponse(resp)
        carouseldict = {}
        carouseldict['carouselitemname'] = carqset[0].title
        carouseldict['carouselitemtext'] = carqset[0].textvalue
        carouseldict['carouseldatatype'] = carqset[0].datatype
        carouseldict['carouseldataentry'] = carqset[0].data_id
        carouseldict['carouselimage'] = carqset[0].imagepath
        carouseldict['selpriority'] = carqset[0].priority
        carouseldict['id'] = carqset[0].id
        context['carouseldict'] = carouseldict
        carouseldatadict = {}
        if carqset[0].datatype == "gallery":
            dqset = Gallery.objects.all()
            for dq in dqset:
                dname = dq.galleryname
                did = dq.id
                carouseldatadict[dname] = did
        elif carqset[0].datatype == "gevent":
            dqset = Event.objects.all()
            for dq in dqset:
                dname = dq.eventname
                did = dq.id
                carouseldatadict[dname] = did
        elif carqset[0].datatype == "museum":
            dqset = Museum.objects.all()
            for dq in dqset:
                dname = dq.museumname
                did = dq.id
                carouseldatadict[dname] = did
        elif carqset[0].datatype == "mevent":
            dqset = MuseumEvent.objects.all()
            for dq in dqset:
                dname = dq.eventname
                did = dq.id
                carouseldatadict[dname] = did
        elif carqset[0].datatype == "artist":
            dqset = Artist.objects.all()
            for dq in dqset:
                dname = dq.artistname
                did = dq.id
                carouseldatadict[dname] = did
        elif carqset[0].datatype == "auction":
            dqset = Auction.objects.all()
            for dq in dqset:
                dname = dq.auctionname
                did = dq.id
                carouseldatadict[dname] = did
        elif carqset[0].datatype == "auctionhouse":
            dqset = AuctionHouse.objects.all()
            for dq in dqset:
                dname = dq.housename
                did = dq.id
                carouseldatadict[dname] = did
        context['carouseldatadict'] = carouseldatadict
        carjson = json.dumps(context)
        return HttpResponse(carjson)
    else:
        return HttpResponse("{'Error' : 'Invalid method of call'}")

"""
@login_required(login_url='/admin/login/')
def downloadcarouselimage(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    carid = request.GET.get('carid', None)
    if not carid:
        return HttpResponse("Could not find carousel id with the request.")
    try:
        carouselobj = Carousel.objects.get(id=carid)
    except:
        return HttpResponse("Invalid carousel Id sent with request.")
    carouselimagepath = carouselobj.imagepath
    abscarouselimagepath = carouselimagepath.replace("/media", settings.MEDIA_ROOT)
    if 'static' in carouselimagepath:
        abscarouselimagepath = carouselimagepath.replace("/static", settings.STATIC_ROOT)
    print(abscarouselimagepath)
    fp = open(abscarouselimagepath, "rb")
    carouselimage = fp.read()
    fp.close()
    imgfilename = os.path.basename(abscarouselimagepath)
    img = Image.open(abscarouselimagepath)
    imgformat = img.format
    img.close()
    response = HttpResponse(carouselimage, content_type='image/jpeg')
    if imgformat == 'PNG':
        response = HttpResponse(carouselimage, content_type='image/png')
    elif imgformat == 'GIF':
        response = HttpResponse(carouselimage, content_type='image/gif')
    response['Content-Disposition'] = 'attachment; filename={}'.format(imgfilename)
    return response
"""

@login_required(login_url='/admin/login/')
def savecarousel(request):
    if request.method == 'POST':
        carouselitemname, carouselitemtext, carouselimage, seldatatype, seldataentry, selpriority, carid = "", "", "", "", "", "", ""
        if 'carouselitemname' in request.POST.keys():
            carouselitemname = request.POST['carouselitemname'].strip()
        if 'carouselitemtext' in request.POST.keys():
            carouselitemtext = request.POST['carouselitemtext'].strip()
        if 'seldatatype' in request.POST.keys():
            seldatatype = request.POST['seldatatype'].strip()
        if 'seldataentry' in request.POST.keys():
            seldataentry = request.POST['seldataentry'].strip()
        if 'selpriority' in request.POST.keys():
            selpriority = request.POST['selpriority'].strip()
        if 'carid' in request.POST.keys():
            carid = request.POST['carid'].strip()
        if carouselitemname == "":
            message = "Carousel entry name is empty. Can't create carousel entry."
            return HttpResponse(message)
        carobj = None
        try:
            carobj = Carousel.objects.get(id=carid)
        except:
            message = "Could not find Carousel entry with Id %s"%carid
            return HttpResponse(message)
        carobj.title = carouselitemname
        carobj.textvalue = carouselitemtext
        carobj.datatype = seldatatype
        carobj.data_id = seldataentry
        carobj.priority = selpriority
        # Handle image for the carousel entry
        carouselimage = request.FILES.get("carouselimage")
        carouseldir = settings.MEDIA_ROOT + os.path.sep + "carousel"
        if carouselimage:
            mimetype = carouselimage.content_type
            if mimetype != "image/gif" and mimetype != "image/jpeg" and mimetype != "image/png":
                return HttpResponse("Uploaded file is not gif, jpeg or png format.")
            if 'carouselimage' in request.FILES.keys():
                carouselimagename = request.FILES['carouselimage'].name
            imagelocation = settings.MEDIA_ROOT + os.path.sep + "carousel"
            if not os.path.exists(imagelocation):
                mkdir_p(imagelocation)
            uploadstatus = handleuploadedfile(request.FILES['carouselimage'], imagelocation, carouselimagename)
            resizedimagefile = resizeimage(uploadstatus[0], carouseldir, 1500) # Max width is 1500 px.
            carobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
        else: # Get the image of the entry
            if seldatatype == "gallery":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = Gallery.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.coverimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "gevent":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = Event.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.eventimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "museum":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = Museum.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.coverimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "mevent":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = MuseumEvent.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.coverimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "artist":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = Artist.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.squareimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "auction":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = Auction.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.coverimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
            elif seldatatype == "auctionhouse":
                entid = seldataentry
                dqobj = None
                try:
                    dqobj = AuctionHouse.objects.get(id=entid)
                    resizedimagefile = resizeimage(dqobj.coverimage, carouseldir, 1500) # Max width is 1500 px.
                    shutil.copyfile(resizedimagefile, settings.MEDIA_ROOT + os.path.sep + "carousel" + os.path.sep + os.path.basename(resizedimagefile))
                    carobj.imagepath = settings.MEDIA_URL + "carousel/" + os.path.basename(resizedimagefile)
                except:
                    return HttpResponse("Could not find any image for this carousel entry.")
        try:
            carobj.save()
            message = "Successfully saved carousel entry named '%s'"%carouselitemname
        except:
            message = "Error: Could not save carousel entry - %s"%sys.exc_info()[1].__str__()
        return HttpResponse(message)
    else:
        return HttpResponse("Invalid method of call")


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



