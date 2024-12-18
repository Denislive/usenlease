from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta
from corsheaders.defaults import default_headers
import os
<<<<<<< HEAD
=======
import dj_database_url
import base64
>>>>>>> ec867583 (update settings.py && jenkins)

# Load environment variables from .env
load_dotenv()

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent.parent

# Google Cloud Storage Bucket Name
GS_BUCKET_NAME = os.getenv("GS_BUCKET_NAME")  # e.g., 'my-app-media'

# Decode the base64 encoded credentials and write to a temporary file
creds_path = '/app/backend/credentials/burnished-ether-439413-s1-579bee90267c.json'
creds_content = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_CONTENT')
if creds_content:
    with open(creds_path, 'wb') as f:
        f.write(base64.b64decode(creds_content))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
<<<<<<< HEAD
=======

if not SECRET_KEY:
    raise ValueError("The SECRET_KEY environment variable is not set")
>>>>>>> ec867583 (update settings.py && jenkins)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'False'

<<<<<<< HEAD
ALLOWED_HOSTS = ['*']

DOMAIN_URL = 'http://127.0.0.1:8000'

RECIPIENT_LIST = os.getenv('RECIPIENT_LIST')
=======
# Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'https://usenlease-2f8583d212bc.herokuapp.com',
]

ALLOWED_HOSTS = [
    'usenlease-2f8583d212bc.herokuapp.com',
    'usenlease.com',
    '*'
]
>>>>>>> ec867583 (update settings.py && jenkins)

# Login URL
LOGIN_URL = '/accounts/user/login'

# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Custom User Model
AUTH_USER_MODEL = 'user_management.User'

# Stripe Keys (from .env file)
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
<<<<<<< HEAD
]



# Rest JWT
=======
    'storages',  # Google Cloud Storage for media
]

# Rest Framework Configuration
>>>>>>> ec867583 (update settings.py && jenkins)
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

<<<<<<< HEAD
EMAIL_HOST =  os.getenv('EMAIL_HOST')
=======
# Email settings
EMAIL_HOST = os.getenv('EMAIL_HOST')
>>>>>>> ec867583 (update settings.py && jenkins)
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

<<<<<<< HEAD
=======
# Middleware Configuration
>>>>>>> ec867583 (update settings.py && jenkins)
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

<<<<<<< HEAD
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
=======
# Database configuration (PostgreSQL on Heroku)
try:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL')  # Use DATABASE_URL from Heroku environment
        )
    }

>>>>>>> ec867583 (update settings.py && jenkins)
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

# Static files (CSS, JavaScript, images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

<<<<<<< HEAD
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'
=======
# Media files (uploads) – use Google Cloud Storage for media
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_DEFAULT_ACL = 'publicRead'  # Adjust based on your needs
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"
>>>>>>> ec867583 (update settings.py && jenkins)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
