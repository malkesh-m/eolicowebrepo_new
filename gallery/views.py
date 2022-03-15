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
from login.models import User, Session, WebConfig, Carousel
from login.views import getcarouselinfo



# @login_required(login_url='/login/show/')
def index(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = str(request.GET['page'])
    chunksize = 5
    # Find out the distinct gallery types available
    gtypesqset = Gallery.objects.order_by().values_list('gallerytype').distinct()
    lastctr1 = int(page) * chunksize
    lastctr2 = int(page) * chunksize
    lastctr3 = int(page) * chunksize
    lastctr4 = int(page) * chunksize
    lastctr5 = int(page) * chunksize
    #print(gtypesqset)
    galleries1 = Gallery.objects.filter(gallerytype=gtypesqset[0][0])
    galleries2 = Gallery.objects.filter(gallerytype=gtypesqset[1][0])
    galleries3 = Gallery.objects.filter(gallerytype=gtypesqset[2][0])
    galleries4 = Gallery.objects.filter(gallerytype=gtypesqset[3][0])
    galleries5 = Gallery.objects.filter(gallerytype=gtypesqset[4][0])
    startctr1 = lastctr1 - chunksize
    startctr2 = lastctr2 - chunksize
    startctr3 = lastctr3 - chunksize
    startctr4 = lastctr4 - chunksize
    startctr5 = lastctr5 - chunksize
    if lastctr1 > galleries1.__len__():
        lastctr1 = galleries1.__len__()
    if lastctr2 > galleries2.__len__():
        lastctr2 = galleries2.__len__()
    if lastctr3 > galleries3.__len__():
        lastctr3 = galleries3.__len__()
    if lastctr4 > galleries4.__len__():
        lastctr4 = galleries4.__len__()
    if lastctr5 > galleries5.__len__():
        lastctr5 = galleries5.__len__()
    gallerieslist1 = galleries1[startctr1:lastctr1]
    gallerieslist2 = galleries2[startctr2:lastctr2]
    gallerieslist3 = galleries3[startctr3:lastctr3]
    gallerieslist4 = galleries4[startctr4:lastctr4]
    gallerieslist5 = galleries5[startctr5:lastctr5]
    galleriesdict = {}
    for g in gallerieslist1[startctr1:lastctr1]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        gid = g.id
        galleriesdict[gname] = [gloc, gimg, gurl, gid, gtypesqset[0][0]]
    context = {'galleries1' : galleriesdict}
    galleriesdict = {}
    for g in gallerieslist2[startctr2:lastctr2]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        gid = g.id
        galleriesdict[gname] = [gloc, gimg, gurl, gid, gtypesqset[1][0]]
    context['galleries2'] = galleriesdict
    galleriesdict = {}
    for g in gallerieslist3[startctr3:lastctr3]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        gid = g.id
        galleriesdict[gname] = [gloc, gimg, gurl, gid, gtypesqset[2][0]]
    context['galleries3'] = galleriesdict
    galleriesdict = {}
    for g in gallerieslist4[startctr4:lastctr4]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        gid = g.id
        galleriesdict[gname] = [gloc, gimg, gurl, gid, gtypesqset[3][0]]
    context['galleries4'] = galleriesdict
    galleriesdict = {}
    for g in gallerieslist5[startctr5:lastctr5]:
        gname = g.galleryname
        gloc = g.location
        gimg = g.coverimage
        gurl = g.galleryurl
        gid = g.id
        galleriesdict[gname] = [gloc, gimg, gurl, gid, gtypesqset[4][0]]
    context['galleries5'] = galleriesdict
    carouselentries = getcarouselinfo()
    context['carousel'] = carouselentries
    context['gallerytypes'] = [gtypesqset[0][0], gtypesqset[1][0], gtypesqset[2][0], gtypesqset[3][0], gtypesqset[4][0]]
    template = loader.get_template('gallery.html')
    return HttpResponse(template.render(context, request))


def details(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    if request.method == 'GET':
        if 'q' in request.GET.keys():
            gid = str(request.GET['q'])
    context = {}
    template = loader.get_template('gallery_details.html')
    return HttpResponse(template.render(context, request))




    



