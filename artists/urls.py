from django.contrib import admin
from django.urls import include, path
from artists import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('follow/', views.follow, name='follow'),
    path('search/', views.search, name='search'),
    path('artworkdetails/', views.showartwork, name='showartwork'),
    path('textfilter/', views.textfilter, name='textfilter'),
    path('morefilter/', views.morefilter, name='morefilter'),
    path('showstats/', views.showstats, name='showstats'),
    path('favourite/', views.addfavourite, name='addfavourite'),
    path('favouritework/', views.addfavouritework, name='addfavouritework'),

    #     AJAX CALL

    path('searchArtists/', views.searchArtists, name='searchArtists'),
]
