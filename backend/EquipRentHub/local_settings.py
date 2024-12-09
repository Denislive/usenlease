from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta
from corsheaders.defaults import default_headers
import os

# Load environment variables from .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'False'

ALLOWED_HOSTS = ['*']

LOGIN_URL = '/accounts/user/login'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTH_USER_MODEL = 'user_management.User'

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Application definition
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
    'rest_framework_simplejwt.token_blacklist',
    'equipment_management.apps.EquipmentManagementConfig',
    'user_management.apps.UserManagementConfig',
]



# Rest JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

# Simple JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    "AUTH_COOKIE": "token",
    "AUTH_COOKIE_REFRESH": "refresh",
}

EMAIL_HOST =  os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Store password securely
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')

# Security Settings
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'None')
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'None')
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_NAME = os.getenv('CSRF_COOKIE_NAME', 'csrftoken')
CSRF_COOKIE_HTTPONLY = os.getenv('CSRF_COOKIE_HTTPONLY', 'False') == 'True'

CORS_ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'True') == 'True'
CORS_ALLOW_HEADERS = os.getenv('CORS_ALLOW_HEADERS', 'content-type,authorization,X-CSRFToken').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:3000').split(',')
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'True') == 'True'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [BASE_DIR / "templates"],
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

import os
from dotenv import load_dotenv

# Load environment variables from .env file

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Attempt PostgreSQL configuration, fallback to SQLite3 if any error occurs
try:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'usenlease_db'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'mysecretpassword'),
            'HOST': os.getenv('POSTGRES_HOST', 'usenlease-db'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
    }
    # Test connection with the PostgreSQL database to ensure availability
    import psycopg2
    connection = psycopg2.connect(
        dbname=DATABASES['default']['NAME'],
        user=DATABASES['default']['USER'],
        password=DATABASES['default']['PASSWORD'],
        host=DATABASES['default']['HOST'],
        port=DATABASES['default']['PORT']
    )
    connection.close()

except Exception:
    print("PostgreSQL configuration failed; falling back to SQLite3.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
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

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
