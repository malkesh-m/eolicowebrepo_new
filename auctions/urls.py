from django.contrib import admin
from django.urls import include, path
from auctions import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('follow/', views.follow, name='follow'),
    path('search/', views.search, name='search'),
    path('moreauctions/', views.moreauctions, name='moreauctions'),
    path('showauction/', views.showauction, name='showauction'),
    path('morefilter/', views.morefilter, name='morefilter'),
    path('favourite/', views.addfavourite, name='addfavourite'),

    #     AJAX CALL

    path('getAuctionHousesOrLocations/', views.getAuctionHousesOrLocations, name='getAuctionHousesOrLocations'),
    path('getAuctionDetails/', views.getAuctionDetails, name="getAuctionDetails"),
    path('getAuctionArtworksData/', views.getAuctionArtworksData, name="getAuctionArtworksData"),
]
