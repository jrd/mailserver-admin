"""
Django settings for mailserveradmin project.
"""
from os import getenv
from pathlib import Path
from re import (
    DOTALL,
    compile,
)
from socket import (
    gethostbyname_ex,
    gethostname,
)

from django.template import base

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = getenv('DJANGO_SECRET_KEY', 'ec0x-y(=w&lc$p-i(qv)4i-tuiuizxx&_@wujzr12xzaa#hags')
DEBUG = getenv('DJANGO_DEBUG', 'False').lower() in ('true', '1', 'on')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {  # catch all for all loggers
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': getenv('DJANGO_LOG_LEVEL', 'INFO' if DEBUG else 'WARNING'),
            'propagate': False,
        },
        'werkzeug': {
            'handlers': ['console'],
            'level': getenv('DJANGO_RUNSERVER_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO'),
            'propagate': False,
        },
        'asyncio': {
            'level': 'WARNING',
        },
    },
}

ALLOWED_HOSTS = [
    '127.0.0.1',
]
INTERNAL_IPS = [
    '127.0.0.1',
]
if DEBUG:
    INTERNAL_IPS += [
        # tricks to have debug toolbar when developing with docker
        *[ip[:-1] + '1' for ip in gethostbyname_ex(gethostname())[2]]
    ]
try:
    from django_extensions.apps import DjangoExtensionsConfig
    assert(DjangoExtensionsConfig)
    django_extensions_available = True
except ImportError:
    django_extensions_available = False
try:
    from debug_toolbar.middleware import DebugToolbarMiddleware
    assert(DebugToolbarMiddleware)
    debug_toolbar_available = True
except ImportError:
    debug_toolbar_available = False

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
if debug_toolbar_available:
    INSTALLED_APPS.append('django_extensions')
if debug_toolbar_available:
    INSTALLED_APPS.append('debug_toolbar')
INSTALLED_APPS += [
    'fontawesome-free',
    'mailserveradmin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
]
if debug_toolbar_available:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
MIDDLEWARE += [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DB_TYPES = {
    'mysql': 'django.db.backends.mysql',
    'postgres': 'django.db.backends.postgresql',
}
DATABASES = {
    'default': {
        'ENGINE': DB_TYPES[getenv('DJANGO_DB_TYPE', 'mysql')],
        'HOST': getenv('DJANGO_DB_HOST', 'db'),
        'PORT': getenv('DJANGO_DB_PORT', ''),  # default port
        'NAME': getenv('DJANGO_DB_NAME', 'mailserver'),
        'USER': getenv('DJANGO_DB_USER', 'mailserver'),
        'PASSWORD': getenv('DJANGO_DB_PASSWORD', 'changeme'),
    }
}

AUTH_USER_MODEL = 'mailserveradmin.MailUser'
AUTHENTICATION_BACKENDS = (
    'mailserveradmin.auth.MailAuthBackend',
)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

ROOT_URLCONF = 'mailserveradmin.config.urls'
LOGIN_REDIRECT_URL = 'mailserveradmin:domain-list'
LOGOUT_REDIRECT_URL = 'mailserveradmin:login'

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
# allow multiline tags in templates
base.tag_re = compile(base.tag_re.pattern, DOTALL)

WSGI_APPLICATION = 'mailserveradmin.config.wsgi.application'

SESSION_COOKIE_AGE = 30 * 86400  # 30 days
if getenv('DJANGO_NO_HTTPS', 'False').lower() not in ('true', '1', 'on'):
    SECURE_HSTS_SECONDS = 365 * 86400  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
SILENCED_SYSTEM_CHECKS = []
SILENCED_SYSTEM_CHECKS.append('security.W008')  # SECURE_SSL_REDIRECT is not True
SILENCED_SYSTEM_CHECKS.append('security.W018')  # DJANGO_DEBUG is not False
SILENCED_SYSTEM_CHECKS.append('auth.W004')  # MailUser.name is not unique (but it’s ok, it’s unique for superusers)

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = getenv('DJANGO_TZ', 'UTC')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# If proxied, which is often the case
USE_X_FORWARDED_HOST = True

WEBMAIL_URL = getenv('DJANGO_WEBMAIL_URL', '')
VENDOR_NAME = getenv('DJANGO_VENDOR_NAME', 'Sources')
VENDOR_URL = getenv('DJANGO_VENDOR_URL', 'https://github.com/jrd/mailserver-admin')
HIDE_VERSION = getenv('DJANGO_HIDE_VERSION', str(not DEBUG)).lower() in ('true', '1', 'on')

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
