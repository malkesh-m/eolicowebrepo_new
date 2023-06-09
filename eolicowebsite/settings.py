"""
Django settings for eolicowebsite project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import os, sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-zqriz2*)du)t+po@j3a1$dbkiw3(_*n7iw8p=ou&_%8-g60&fe'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_COOKIE_HTTPONLY = False

# Application definition
SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'login',
    'authentication',
    # 'gallery',
    # 'museum',
    'artists',
    'auctions',
    'auctionhouses',
    'adminsite',
    'pricedatabase',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

sentry_sdk.init(
    dsn="https://ef95d89643d94fadbeef998e8df9462e@o4505085847011328.ingest.sentry.io/4505086124490752",
    integrations=[
        DjangoIntegration(),
    ],
    traces_sample_rate=1.0,
    send_default_pii=True
)

STRIPE_PUBLISHABLE_KEY = 'pk_test_51Mc8AISFFk9gA4NXsPbnD899P7tSd1d7mUy0lcmZtFlMY78KWNRYhtVdxzecyFCB1ZaSagcwhwWn2BBhaqQ58rFG00WoOeW7gE'
STRIPE_SECRET_KEY = 'sk_test_51Mc8AISFFk9gA4NXvmfOKNjA1C9Zmg5FVGQ2EIdHaHN5J13sJJ1aTg2s2wj2P2nXrgcBntsNqfO2hWeEOaPPfOVA00pMLcAiOd'
STRIPE_WEBHOOKS_SECRET = 'whsec_38e3524f0ec97709dc2649c8fcc860786271411d86bc59cf61e13f98cbaefbfa'
STRIPE_LIVE_MODE = False

CAPTCHA_SECRET_KEY = '6Le4XrYlAAAAAAxx-NkBJBxvvrj-_GVxXA1Bwdoh'

ROOT_URLCONF = 'eolicowebsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, "templates"),
)

WSGI_APPLICATION = 'eolicowebsite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'gaidbpure', 
        'USER': 'eolicouser',  
        'PASSWORD': 'secretpasswd', 
        'HOST': 'localhost',  
        'PORT': '3306',
    }
}
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'artb_Artbider_Prod',
        'USER': 'artb_Admin',
        'PASSWORD': 'cDLCntgtsjAOP%tw',
        'HOST': '191.101.0.14',
        'PORT': '3306',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "eolico"
    }
}
CACHE_TTL = 60 * 60

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_ROOT = os.path.join('', '/login/static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = '/media/'

GALLERY_FILE_DIR = MEDIA_ROOT + os.path.sep + "images" + os.path.sep + "galleries"
MUSEUM_FILE_DIR = MEDIA_ROOT + os.path.sep + "images" + os.path.sep + "museums"
AUCTION_FILE_DIR = MEDIA_ROOT + os.path.sep + "images" + os.path.sep + "auctions"
AUCTIONHOUSE_FILE_DIR = MEDIA_ROOT + os.path.sep + "images" + os.path.sep + "auctionhouses"

CURRENCIES = ['USD', 'GBP', 'EUR', 'AUD', 'INR', 'HKD', 'CAD', 'JPY']
BLACKLISTED_ARTISTS = [1, ]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PDB_ARTWORKSLIMIT = 500
PDB_ARTISTSLIMIT = 200
PDB_MAXSEARCHRESULT = 200
PDB_LATESTPERIOD = 1000  # 365

IMG_URL_PREFIX = "https://f000.backblazeb2.com/file/fineart-images/"
CAROUSEL_DAYS = 3000
YEARS_FOR_STATS = 6  # production value 2
YEARS_FOR_FEATURED_ARTIST = 6  # production value 1
