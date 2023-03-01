from django.contrib import admin
from django.urls import include, path
from login import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('registration/', views.signup, name='signup'),
    path('dologin/', views.dologin, name='dologin'),
    #path('profile/', views.showprofile, name='showprofile'),
    path('checklogin/', views.checkloginstatus, name='checkloginstatus'),
    path('logout/', views.dologout, name='dologout'),
    path('follow/', views.followartist, name='followartist'),
    path('unfollow/', views.unfollowartist, name='unfollowartist'),
    #path('morefollows/', views.morefollows, name='morefollows'),
    path('morefavourites/', views.morefavourites, name='morefavourites'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('show/', views.show, name='show'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.acctsettings, name='acctsettings'),
    path('myArtist/', views.myArtist, name="myArtist"),
    path('myArtistDetails/', views.myArtistDetails, name="myArtistDetails"),
    path('myArtwork/', views.myArtwork, name="myArtwork"),
    path('myArtworkDetails/', views.myArtworkDetails, name="myArtworkDetails"),

    # Ajax Call Urls

    path('getTrendingArtist/', views.getTrendingArtist, name="getTrendingArtist"),
    path('getUpcomingAuctions/', views.getUpcomingAuctions, name="getUpcomingAuctions"),
    path('getRecentAuctions/', views.getRecentAuctions, name="getRecentAuctions"),
]

