from django.contrib import admin
from django.urls import include, path
from login import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('registration/', views.signup, name='signup'),
    path('dologin/', views.dologin, name='dologin'),
    #path('profile/', views.showprofile, name='showprofile'),
    path('checklogin/', views.checkloginstatus, name='checkloginstatus'),
    path('logout/', views.dologout, name='dologout'),
    path('follow/', views.followartist, name='followartist'),
    path('unfollow/', views.unfollowartist, name='unfollowartist'),
    path('morefollows/', views.morefollows, name='morefollows'),
    path('morefavourites/', views.morefavourites, name='morefavourites'),
]

