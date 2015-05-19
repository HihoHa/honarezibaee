"""
Django settings for beauty project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from easy_thumbnails.conf import Settings as thumbnail_settings
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import mimetypes

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1dvefn4m+d#qjr3%bu8*r1fuwg%#k_g!b6114es1op2twcr^(7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'm_article',
    'jobs',
    'apis',
    'cookie_user',
    'treebeard',
    'django_summernote',
    'bootstrap3',
    'image_cropping',
    'easy_thumbnails',
    'geoposition',
    'PIL' ,
    'django_wysiwyg',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'beauty.urls'

WSGI_APPLICATION = 'beauty.wsgi.application'

MEDIA_ROOT = os.path.join(BASE_DIR, 'images')

MEDIA_URL = '/images/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'), '/home/ali/Workspace/beauty/env/lib/python2.7/site-packages/treebeard/')

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'beauty',
        'USER': 'postgres',
        'PASSWORD': 'Zibaee1Honar2',
        'HOST': '127.0.0.1',
        'PORT': '64999',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.request',
                               'django.contrib.auth.context_processors.auth',
                               'django.contrib.messages.context_processors.messages',)
SUMMERNOTE_CONFIG = {'direction': 'rtl', }

THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS

GEOPOSITION_MAP_OPTIONS = {
    'scrollwheel': True,
    'center': {'lat': 35.7, 'lng': 51.4},
    'zoom': 13
}

GEOPOSITION_MARKER_OPTIONS = {
    'position': {'lat': 35.7, 'lng': 51.4},
    'zoom': 13
}



mimetypes.add_type("image/svg+xml", ".svg", True)
mimetypes.add_type("image/svg+xml", ".svgz", True)
