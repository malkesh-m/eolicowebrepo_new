from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.views.generic import RedirectView
from admin import views

urlpatterns = [
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
]


