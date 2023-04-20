from django.contrib import admin
from django.urls import include, path
from login import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('registration/', views.signup, name='signup'),
    path('dologin/', views.dologin, name='dologin'),
    # path('profile/', views.showprofile, name='showprofile'),
    path('checklogin/', views.checkloginstatus, name='checkloginstatus'),
    path('logout/', views.dologout, name='dologout'),
    path('follow/', views.followartist, name='followartist'),
    path('unfollow/', views.unfollowartist, name='unfollowartist'),
    path('contactUs/', views.contactUs, name='contactUs'),
    # path('morefollows/', views.morefollows, name='morefollows'),
    path('morefavourites/', views.morefavourites, name='morefavourites'),
    path('termsAndCondition/', views.termsAndCondition, name='termsAndCondition'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('show/', views.show, name='show'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.acctsettings, name='acctsettings'),
    path('myArtist/', views.myArtist, name="myArtist"),
    path('artMarketAnalysis/', views.artMarketAnalysis, name="artMarketAnalysis"),
    path('myArtistDetails/', views.myArtistDetails, name="myArtistDetails"),
    path('myArtwork/', views.myArtwork, name="myArtwork"),
    path('myArtworkDetails/', views.myArtworkDetails, name="myArtworkDetails"),

    # Ajax Call Urls

    path('getTrendingArtist/', views.getTrendingArtist, name="getTrendingArtist"),
    path('getUpcomingAuctions/', views.getUpcomingAuctions, name="getUpcomingAuctions"),
    path('getRecentAuctions/', views.getRecentAuctions, name="getRecentAuctions"),
    path('getFollowedArtists/', views.getFollowedArtists, name='getFollowedArtists'),
    path('getFollowedArtworks/', views.getFollowedArtworks, name='getFollowedArtworks'),
    path('getMyArtistsDetails/', views.getMyArtistsDetails, name='getMyArtistsDetails'),
    path('getMyArtworksDetails/', views.getMyArtworksDetails, name="getMyArtworksDetails"),
    path('getMyArtists/', views.getMyArtists, name='getMyArtists'),
    path('getMyArtworks/', views.getMyArtworks, name='getMyArtworks'),
    path('topPerformanceOfYearCharts/', views.topPerformanceOfYearCharts, name='topPerformanceOfYearCharts'),
    path('topLotsOfMonthForCharts/', views.topLotsOfMonthForCharts, name='topLotsOfMonthForCharts'),
    path('topSalesOfMonthForCharts/', views.topSalesOfMonthForCharts, name='topSalesOfMonthForCharts'),
    path('topArtistsOfMonthForCharts/', views.topArtistsOfMonthForCharts, name='topArtistsOfMonthForCharts'),
    path('topGeographicalLocationsForCharts/', views.topGeographicalLocationsForCharts, name="topGeographicalLocationsForCharts"),
    path('getMyNotificationLogs/', views.getMyNotificationLogs, name='getMyNotificationLogs'),
    path('topUpcomingLotsOfWeek/', views.topUpcomingLotsOfWeek, name='topUpcomingLotsOfWeek'),
    path('stripeWebhooks/', views.stripeWebhooks, name='stripeWebhooks')
]
