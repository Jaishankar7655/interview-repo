# project/settings.py

import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Load environment variables from .env (if present)
# -----------------------------
# This makes settings work identically whether the app is launched via
# gunicorn (systemd), `manage.py`, or the dev server.
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    # python-dotenv is optional; env vars can also be provided by the OS/systemd.
    pass

# -----------------------------
# Secrets from .env
# -----------------------------
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    get_random_secret_key()  # fallback if .env missing
)

# Defaults are production-safe: DEBUG is off unless explicitly enabled.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        'ALLOWED_HOSTS', '34.229.200.54,localhost,127.0.0.1'
    ).split(',')
    if h.strip()
]

# Origins trusted for CSRF (needed for POST forms when DEBUG=False / behind Nginx).
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        'CSRF_TRUSTED_ORIGINS', 'http://34.229.200.54'
    ).split(',')
    if o.strip()
]

# -----------------------------
# Installed Apps
# -----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
]

# -----------------------------
# Middleware
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

# -----------------------------
# Templates
# -----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'project.wsgi.application'

# -----------------------------
# Database (SQLite)
# -----------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('SQLITE_PATH', BASE_DIR / 'db.sqlite3'),
    }
}

# -----------------------------
# Password Validators
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------
# Internationalization
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# Static and Media
# -----------------------------
STATIC_URL = '/static/'
# Include the project-level static dir only if it exists (avoids warnings).
STATICFILES_DIRS = [
    d for d in [os.path.join(BASE_DIR, 'static')] if os.path.isdir(d)
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # for collectstatic

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -----------------------------
# Default primary key field type
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
