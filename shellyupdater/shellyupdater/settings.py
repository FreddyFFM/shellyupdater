"""
Django settings for shellyupdater project.

Generated by 'django-admin startproject' using Django 1.11.13.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import environ


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get local settings from .env file
env = environ.Env()
# reading .env file
env.read_env()
DEBUG = env.bool('DEBUG', True)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'updates',
    'openhab',  # deactivate the Openhab modul here
    'setter',
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

ROOT_URLCONF = 'shellyupdater.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.openhab_active',
            ],
        },
    },
]

WSGI_APPLICATION = 'shellyupdater.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(env.str('DATABASE_DIR', BASE_DIR), 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# Static Assets DIR
STATICFILES_DIRS = (  # where to find static files
    os.path.join(BASE_DIR, "static-assets"),
)

### LOCAL SETTINGS ARE READ FROM THE .env FILE

# MQTT variables for connection
MQTT_BROKER_ADDRESS = env.str('MQTT_BROKER_ADDRESS')
MQTT_USERNAME = env.str('MQTT_USERNAME')
MQTT_PASSWORD = env.str('MQTT_PASSWORD')
MQTT_SHELLY_ANNOUNCE_TOPIC = env.str('MQTT_SHELLY_ANNOUNCE_TOPIC')
MQTT_SHELLY_COMMAND_TOPIC = env.str('MQTT_SHELLY_COMMAND_TOPIC')
MQTT_SHELLY_BASE_TOPIC = env.str('MQTT_SHELLY_BASE_TOPIC')

#OPENHAB
OPENHAB_REST_BASE_URL = env.str('OPENHAB_REST_BASE_URL')

#GUNICORN START
STARTS_WITH_GUNICORN = env.bool('STARTS_WITH_GUNICORN', False)

# SHELLY-HTTP
HTTP_SHELLY_USERNAME = env.str('HTTP_SHELLY_USERNAME')
HTTP_SHELLY_PASSWORD = env.str('HTTP_SHELLY_PASSWORD')
