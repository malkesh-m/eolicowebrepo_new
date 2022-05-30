from django.contrib import admin
from django.urls import include, path
from login import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('show/', views.showlogin, name='showlogin'),
    path('registration/', views.signup, name='signup'),
    path('dologin/', views.dologin, name='dologin'),
    path('profile/', views.showprofile, name='showprofile'),
    path('checklogin/', views.checkloginstatus, name='checkloginstatus'),
]

