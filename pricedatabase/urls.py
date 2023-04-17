from django.contrib import admin
from django.urls import include, path
from pricedatabase import views


urlpatterns = [
    path('database/', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('search/', views.search, name='search'),
    path('filter/', views.dofilter, name='dofilter'),
    path('plans/', views.showplans, name='showplans'),

    # AJAX CALL

    path('searchAuctionHouses/', views.searchAuctionHouses, name='searchAuctionHouses'),
    path('searchArtists/', views.searchArtists, name='searchArtists'),
    path('searchArtworks/', views.searchArtworks, name='searchArtworks'),
    path('checkoutSession/', views.checkoutSession, name='checkoutSession'),
]

