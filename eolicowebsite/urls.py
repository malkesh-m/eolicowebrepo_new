"""eolicowebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.views.generic import RedirectView
from django.conf.urls.static import static
import login

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('admin/', include('adminsite.urls')),
    path('login/', include('login.urls')),
    path('gallery/', include('gallery.urls')),
    path('museum/', include('museum.urls')),
    path('artist/', include('artists.urls')),
    path('auction/', include('auctions.urls')),
    path('auctionhouse/', include('auctionhouses.urls')),
    path('price/', include('pricedatabase.urls')),
    path('about/', login.views.about, name='about'),
    path('contactus/', login.views.contactus, name='contactus'),
    path('', login.views.index, name='homeindex'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


