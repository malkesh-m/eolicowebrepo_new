from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.views.generic import RedirectView
from adminsite import views

urlpatterns = [
    path('login/', views.showlogin, name='showlogin'),
    path('galleries/', views.galleries, name='galleries'),
    path('gevents/', views.gevents, name='gevents'),
    path('artists/', views.artists, name='artists'),
    path('artworks/', views.artworks, name='artworks'),
    path('museums/', views.museums, name='museums'),
    path('mevents/', views.mevents, name='mevents'),
    path('museumpieces/', views.museumpieces, name='museumpieces'),
    path('auctionhouses/', views.auctionhouses, name='auctionhouses'),
    path('auctions/', views.auctions, name='auctions'),
    path('lots/', views.lots, name='lots'),
    path('getevents/', views.getevents, name='getevents'),
    path('searchgallery/', views.searchgalleries, name='searchgalleries'),
    path('editgallery/', views.editgallery, name='editgallery'),
    path('savegallery/', views.savegallery, name='savegallery'),
    path('searchgevents/', views.searchgevents, name='searchgevents'),
    path('editgevent/', views.editgevent, name='editgevent'),
    path('savegevent/', views.savegevent, name='savegevent'),
    path('searchartworks/', views.searchartworks, name='searchartworks'),
    path('editartwork/', views.editartwork, name='editartwork'),
    path('saveartwork/', views.saveartwork, name='saveartwork'),
    path('searchartists/', views.searchartists, name='searchartists'),
    path('editartist/', views.editartist, name='editartist'),
    path('saveartist/', views.saveartist, name='saveartist'),
    path('searchmuseum/', views.searchmuseum, name='searchmuseum'),
    path('editmuseum/', views.editmuseum, name='editmuseum'),
    path('savemuseum/', views.savemuseum, name='savemuseum'),
    path('searchmevents/', views.searchmevents, name='searchmevents'),
    path('editmevent/', views.editmevent, name='editmevent'),
    path('savemevent/', views.savemevent, name='savemevent'),
    path('searchmpieces/', views.searchmpieces, name='searchmpieces'),
    path('savempieces/', views.savempieces, name='savempieces'),
    path('editmpieces/', views.editmpieces, name='editmpieces'),
    path('getmevents/', views.getmevents, name='getmevents'),
    path('webconfig/', views.webconfig, name='webconfig'),
    path('searchwebconfig/', views.searchwebconfig, name='searchwebconfig'),
    path('savewebconfig/', views.savewebconfig, name='savewebconfig'),
    path('editwebconfig/', views.editwebconfig, name='editwebconfig'),
    path('carousel/', views.carousel, name='carousel'),
    path('getcarouselentries/', views.getcarouselentries, name='getcarouselentries'),
    path('searchcarousel/', views.searchcarousel, name='searchcarousel'),
    path('editcarousel/', views.editcarousel, name='editcarousel'),
    path('savecarousel/', views.savecarousel, name='savecarousel'),
    #path('downloadcarouselimage/', views.downloadcarouselimage, name='downloadcarouselimage'),
]


