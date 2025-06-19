import os
# from celery.schedules import crontab
# from pathlib import Path


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "__$1ud47e&nyso5h5o3fwnqu4+hfqcply9h$k*h2s34)hn5@nc"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ALLOWED_HOSTS = []

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "485c-197-250-132-101.ngrok-free.app"]

CSRF_TRUSTED_ORIGINS = [
    "https://485c-197-250-132-101.ngrok-free.app"
]



# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "widget_tweaks",
    "apps.corecode",
    "apps.students",
    "apps.staffs",
    "apps.finance",
    "expenditures",
    "event",
    "crispy_forms",
    "bootstrap5",
    'crispy_bootstrap5',  # Add this line
    "bootstrap_themes",
    "django_filters",
    "rest_framework",
    'apps.academics',
    "school_properties",
    "non_staffs",
    "attendace",
    "library",
    "accounts",
    'sms',
    'mpesa',
    'mtaa',
    'location',
    'analytics',
    'debug_toolbar',
    'duty',
    'meetings',
    'channels',
    'website'
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # Add this line
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.corecode.middleware.SiteWideConfigs",
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = "school_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.corecode.context_processors.site_defaults",
                'accounts.context_processors.user_profile_data',  # Add this line
            ],
        },
    },
]

WSGI_APPLICATION = "school_app.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.sqlite3",
#        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'school_db',
        'USER': 'school_user',
        'PASSWORD': 'Kinyota3543',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

MEDIA_URL = "/media/"

# Authentication settings
AUTH_USER_MODEL = 'accounts.CustomUser'

# settings.py
AUTHENTICATION_BACKENDS = [
    'accounts.backends.ParentUserBackend',  # Custom ParentUser backend
    'django.contrib.auth.backends.ModelBackend',  # Default Django backend
]

LOGIN_URL = 'custom_login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

TIME_ZONE = 'Africa/Dar_es_Salaam'  # Replace with your time zone

USE_TZ = True

TIME_FORMAT = 'H:i'  # 24-hour format
USE_L10N = False     # Disable localization formatting if it's interfering


SESSION_COOKIE_AGE = 10800

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "W6",
            "interval": 4,
            "backupCount": 3,
            "encoding": "utf8",
            "filename": os.path.join(BASE_DIR, "debug.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Crispy Forms configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Localization settings
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('sw', 'Kiswahili'),  # Add Kiswahili
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

MPESA_ENVIRONMENT = 'sandbox'  # 'sandbox' for testing, 'production' for live
MPESA_CONSUMER_KEY = 'uJkuyPeG79kC683dwdWRHFkLHJMpF0QJsb5uGJGkwIDjzfow'
MPESA_CONSUMER_SECRET = 'Em5VTQedGUcxL4Nb7ZPgj57fpoAZhEulUfYHGMsLFOm5E4rdBdn8HYxDcUh04QFQ'
MPESA_SHORTCODE = '174379'
MPESA_INITIATOR_NAME = 'josephkinyota'
MPESA_INITIATOR_PASSWORD = 'Kinyota3543'
MPESA_PASSKEY = 'xVCaovZ4'
MPESA_CALLBACK_URL = 'https://fcd2-197-186-8-1.ngrok-free.app/mpesa-callback/'

OPENAI_API_KEY = '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'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 200000000  # Increase this limit based on your requirements

DATA_UPLOAD_MAX_MEMORY_SIZE = None  # Removes the limit

FILE_UPLOAD_MAX_MEMORY_SIZE = 1073741824  # 1GB

ASGI_APPLICATION = 'school_app.asgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}