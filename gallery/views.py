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

from gallery.models import Gallery, Event, Artist, Artwork


# @login_required(login_url='/login/show/')
def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    page = "1"
    if request.method == 'POST':
        if 'page' in request.POST.keys():
            page = str(request.POST['page'])
    chunksize = 5 * 3
    lastctr = int(page) * chunksize
    galleries = Gallery.objects.all()
    startctr = lastctr - (chunksize - 1)
    if lastctr > galleries.__len__():
        lastctr = galleries.__len__()
    gallerieslist = galleries[startctr:lastctr]
    galleriesdict = {}
    for g in gallerieslist[0:3]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        galleriesdict[gname] = [gloc, gimg, gurl]
    context = {'galleries1' : galleriesdict}
    galleriesdict = {}
    for g in gallerieslist[3:6]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        galleriesdict[gname] = [gloc, gimg, gurl]
    context['galleries2'] = galleriesdict
    galleriesdict = {}
    for g in gallerieslist[6:9]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        galleriesdict[gname] = [gloc, gimg, gurl]
    context['galleries3'] = galleriesdict
    galleriesdict = {}
    for g in gallerieslist[9:12]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        galleriesdict[gname] = [gloc, gimg, gurl]
    context['galleries4'] = galleriesdict
    galleriesdict = {}
    for g in gallerieslist[12:15]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        galleriesdict[gname] = [gloc, gimg, gurl]
    context['galleries5'] = galleriesdict
    template = loader.get_template('gallery.html')
    return HttpResponse(template.render(context, request))



