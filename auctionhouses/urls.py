from django.contrib import admin
from django.urls import include, path
from auctionhouses import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('follow/', views.follow, name='follow'),
    path('auctiondetails/', views.auctiondetails, name='auctiondetails'),
    path('search/', views.search, name='search'),
]

