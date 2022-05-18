from django.contrib import admin
from django.urls import include, path
from pricedatabase import views


urlpatterns = [
    path('database/', views.index, name='index'),
    path('details/', views.details, name='details'),
    path('search/', views.search, name='search'),
    path('filter/', views.dofilter, name='dofilter'),
]

