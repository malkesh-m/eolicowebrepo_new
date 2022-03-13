from django.contrib import admin
from django.urls import include, path
from login import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('show/', views.showlogin, name='showlogin'),
]

