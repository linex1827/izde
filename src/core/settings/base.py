from datetime import timedelta
import os.path
from pathlib import Path
from core.settings.env_reader import env, csv
from core.settings.themes import *
from core.settings.cors import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BASE_URL = 'http://161.35.223.168'
SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env("ALLOWED_HOSTS", cast=csv())

DEBUG = env("DEBUG", default=False, cast=bool)

LOCAL_APPS = [
    'apps.common.apps.CommonConfig',
    'apps.profiles.apps.ProfilesConfig',
    'apps.vendors.apps.VendorsConfig',
    'apps.houserent.apps.HouserentConfig',
    'apps.reviews.apps.ReviewsConfig',
    'apps.travels.apps.TravelsConfig',
    'apps.analytics.apps.AnalyticsConfig',
    'apps.notification.apps.NotificationConfig',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'coreapi',
    'corsheaders',
    'debug_toolbar',
    'rest_framework_simplejwt',
    'drf_yasg',
    'simple_history',
    'django_celery_beat',
]

THEME_APPS = [
    'jazzmin',
    'channels',
]

INSTALLED_APPS = [
    *THEME_APPS,
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'simple_history.middleware.HistoryRequestMiddleware'
]

if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = 'core.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env('CHANNEL_LAYER_REDIS_URL')],
        },
    },
}

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

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Asia/Bishkek"
DATE_FORMAT = "%Y-%m-%d"

SMALL_THUMBNAIL_SIZE = 512, 512
MEDIUM_THUMBNAIL_SIZE = 1024, 1024
LARGE_THUMBNAIL_SIZE = 2048, 2048

USE_I18N = True

USE_TZ = False

STATIC_URL = 'back_static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'back_static')

MEDIA_URL = '/back_media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'back_media')

AUTH_USER_MODEL = 'profiles.CustomUser'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=180),
    "ROTATE_REFRESH_TOKENS": True,

    "SIGNING_KEY": SECRET_KEY,

    "AUTH_HEADER_TYPES": ("Bearer",)
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': 'apps.common.exception_handlers.unified_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

# REDIS
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL'),
    }
}

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT', cast=int),
    }
}


# EMAIL
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = env('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env('CELERY_BROKER_URL')
CELERY_BEAT_SCHEDULER = env('CELERY_BEAT_SCHEDULER')

# CELERY_BEAT_SCHEDULE = {
#     'delete_expired_order': {
#         'task': 'apps.profiles.tasks.broker.clean_up_expired_orders',
#         'schedule': 180,
#     },
#     'delete_expired_offer': {
#         'task': 'apps.profiles.tasks.broker.clean_up_expired_orders',
#         'schedule': 180,
#     },
# }

CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in env('CSRF_TRUSTED_ORIGINS').split(',')]
CORS_ALLOW_ALL_ORIGINS = env('CORS_ALLOW_ALL_ORIGINS', cast=bool)




