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
from museum.models import Museum, MuseumEvent, MuseumPieces, MuseumArticles
from auctions.models import Auction, Lot
from auctionhouses.models import AuctionHouse


def galleries(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('galleries.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


def gevents(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('gevents.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


def artworks(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('artworks.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


def artists(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('artists.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


def museums(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('museums.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


def mevents(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('mevents.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


def museumpieces(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('museumpieces.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


def auctionhouses(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('auctionhouses.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


def auctions(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('auctions.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass


def lots(request):
    if request.method == 'GET':
        context = {}
        template = loader.get_template('lots.html')
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        pass



