"""
Django settings for chemviz_backend project.
Production-ready configuration.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

# -------------------------------
# Security / Environment
# -------------------------------

import sys
from django.core.exceptions import ImproperlyConfigured


def _env_list(name, default=""):
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


DEBUG = os.getenv('DEBUG', 'False').lower() in ('1', 'true', 'yes')
TESTING = 'pytest' in sys.modules or 'test' in sys.argv

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG or TESTING:
        # Throwaway key for local development and the test-suite only.
        SECRET_KEY = 'insecure-local-development-key-do-not-use-in-production'
    else:
        raise ImproperlyConfigured(
            "SECRET_KEY environment variable is required when DEBUG is off."
        )

# Comma-separated list in the ALLOWED_HOSTS env var; defaults cover local use
# and Render (the platform sets RENDER_EXTERNAL_HOSTNAME).
ALLOWED_HOSTS = _env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver')
if os.getenv('RENDER_EXTERNAL_HOSTNAME'):
    ALLOWED_HOSTS.append(os.environ['RENDER_EXTERNAL_HOSTNAME'])

# Uploads: reject request bodies larger than this before they are buffered.
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB CSV limit enforced by the upload view
DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024


# -------------------------------
# Installed apps
# -------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Local
    'equipment',
]

# -------------------------------
# Middleware
# -------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Whitenoise for static files in production
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chemviz_backend.urls'

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

WSGI_APPLICATION = 'chemviz_backend.wsgi.application'

# -------------------------------
# Database
# -------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# -------------------------------
# Password validation
# -------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------
# Internationalization
# -------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------
# Static & Media
# -------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise optimized storage (Django 4.2+ STORAGES setting)
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

# Media (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Ensure directories exist (safe for dev; ignored in production)
STATIC_ROOT.mkdir(exist_ok=True)
MEDIA_ROOT.mkdir(exist_ok=True)
(MEDIA_ROOT / 'uploads').mkdir(exist_ok=True)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------
# REST Framework
# -------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "240/min",
        "auth": "10/min",      # login / register (per client IP)
        "upload": "20/hour",   # CSV uploads (per user)
        "ai": "20/hour",       # Gemini-backed analysis (per user)
    },
}

# -------------------------------
# CORS & CSRF
# -------------------------------

# The API authenticates with an Authorization header (DRF token), not cookies,
# so cross-origin credentials are not needed and CORS is restricted to an allowlist.
CORS_ALLOWED_ORIGINS = _env_list(
    'CORS_ALLOWED_ORIGINS',
    'https://chemicalanalyzer.vercel.app,http://localhost:5173,http://127.0.0.1:5173',
)
CORS_ALLOW_CREDENTIALS = False

CSRF_TRUSTED_ORIGINS = _env_list(
    'CSRF_TRUSTED_ORIGINS',
    'https://chemicalanalyzer.vercel.app,https://chemicalanalyzer.onrender.com',
)

# -------------------------------
# HTTPS / cookie hardening (production only)
# -------------------------------

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
if not DEBUG and not TESTING:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Path of the Django admin site (override to move it off the default URL).
ADMIN_URL = os.getenv('ADMIN_URL', 'admin/')
