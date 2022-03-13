from django.contrib import admin
from django.urls import include, path
from gallery import views


urlpatterns = [
    path('index/', views.index, name='index'),
]

