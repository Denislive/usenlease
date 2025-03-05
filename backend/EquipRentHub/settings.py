from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
import base64
import psycopg2
import ssl 

# Load environment variables from .env
load_dotenv()

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent.parent

# Detect if we're in a Docker build environment
DOCKER_BUILD = os.getenv("DOCKER_BUILD", "0") == "1"

# Application domain
DOMAIN_URL = os.getenv('DOMAIN_URL')

# Google Cloud Storage Bucket Name
GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME')

# PORT
PORT = os.getenv("PORT")

# Decode base64 credentials and write to a temporary file
creds_path = os.path.join(BASE_DIR, 'credentials', 'google-credentials.json')
creds_content = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_CONTENT')
if creds_content:
    os.makedirs(os.path.dirname(creds_path), exist_ok=True)
    try:
        creds_content += '=' * (-len(creds_content) % 4)  # Fix padding
        decoded_creds = base64.b64decode(creds_content)
        with open(creds_path, 'wb') as f:
            f.write(decoded_creds)
    except base64.binascii.Error as e:
        print(f"Error decoding Base64 string: {e}")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path

# SECURITY WARNING: Keep secret key hidden
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("The SECRET_KEY environment variable is not set")

DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = ['usenlease.com', 'www.usenlease.com', '.usenlease.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'tinymce',
    'whitenoise.runserver_nostatic',
    'rest_framework_simplejwt.token_blacklist',
    'equipment_management.apps.EquipmentManagementConfig',
    'user_management.apps.UserManagementConfig',
    'storages',
]

# ✅ Only disable Celery Beat in Docker build, not in production!
if not DOCKER_BUILD:
    INSTALLED_APPS.append("django_celery_beat")

# Use REDIS_URL from Heroku with fallback for local development
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Ensure Celery handles SSL correctly for Heroku Redis
if CELERY_BROKER_URL.startswith("rediss://"):
    CELERY_BROKER_USE_SSL = {
        'ssl_cert_reqs': ssl.CERT_NONE  # Use `ssl.CERT_NONE` instead of a string
    }
else:
    CELERY_BROKER_USE_SSL = None  # Use normal Redis if running locally

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'


RECIPIENT_LIST = os.getenv('RECIPIENT_LIST')

# Login URL
LOGIN_URL = '/accounts/user/login'

# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Custom User Model
AUTH_USER_MODEL = 'user_management.User'

# Stripe Keys
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

# Simple JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    "AUTH_COOKIE": "token",
    "AUTH_COOKIE_REFRESH": "refresh",
}

# Email Settings
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')

# Security Settings
CORS_ALLOW_CREDENTIALS = True

# CORS Allowed Origins
AUTH_COOKIE_NAME = os.getenv('AUTH_COOKIE_NAME')
AUTH_COOKIE_REFRESH = os.getenv('AUTH_COOKIE_REFRESH')
AUTH_COOKIE_SAMESITE = os.getenv('AUTH_COOKIE_SAMESITE', 'None')
AUTH_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'
AUTH_COOKIE_PATH = os.getenv('AUTH_COOKIE_PATH')
AUTH_COOKIE_HTTPONLY = os.getenv('AUTH_COOKIE_HTTPONLY')

SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'None')
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_NAME = os.getenv('CSRF_COOKIE_NAME', 'csrftoken')
CSRF_COOKIE_HTTPONLY = os.getenv('CSRF_COOKIE_HTTPONLY', 'False') == 'True'

# CSRF & CORS
CSRF_TRUSTED_ORIGINS = ['https://usenlease.com', 'https://www.usenlease.com']
CORS_ALLOWED_ORIGINS = ['https://usenlease.com', 'https://www.usenlease.com']
CORS_ALLOWED_ORIGIN_REGEXES = [r"^https://(\w+\.)?usenlease\.com$"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
]

# Middleware Configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'EquipRentHub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "static"],
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

WSGI_APPLICATION = 'EquipRentHub.wsgi.application'

# ✅ Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')

if DOCKER_BUILD:
    print("Running in Docker build mode: Using SQLite fallback")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    try:
        DATABASES = {
            'default': dj_database_url.config(default=DATABASE_URL)
        }
    except Exception as e:
        print(f"PostgreSQL configuration failed: {e}. Falling back to SQLite3.")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
# Static & Media Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
