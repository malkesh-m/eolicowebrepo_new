from django.contrib import admin
from django.urls import include, path
from gallery import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('eventdetails/', views.eventdetails, name='eventdetails'),
    path('artworkdetails/', views.artworkdetails, name='artworkdetails'),
    path('search/', views.search, name='search'),
]

