from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
import base64
import psycopg2

# Load environment variables from .env
load_dotenv()

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent.parent

# Application domain
DOMAIN_URL = os.getenv('DOMAIN_URL')

# Google Cloud Storage Bucket Name
GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME')  # e.g., 'my-app-media'

# PORT 
PORT = os.getenv("PORT")

# Decode the base64 encoded credentials and write to a temporary file
creds_path = os.path.join(BASE_DIR, 'credentials', 'google-credentials.json')
creds_content = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_CONTENT')
if creds_content:
    os.makedirs(os.path.dirname(creds_path), exist_ok=True)
    try:
        # Correct the padding for Base64 string
        creds_content += '=' * (-len(creds_content) % 4)
        decoded_creds = base64.b64decode(creds_content)
        with open(creds_path, 'wb') as f:
            f.write(decoded_creds)
    except base64.binascii.Error as e:
        print(f"Error decoding Base64 string: {e}")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError("The SECRET_KEY environment variable is not set")


DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = [
    #'usenleaseprod-4f2da7430c4d.herokuapp.com',
    'usenlease.com',
    'www.usenlease.com'
    '.usenlease.com',
]

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Use Redis as the message broker
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'


RECIPIENT_LIST = os.getenv('RECIPIENT_LIST')

# Login URL
LOGIN_URL = '/accounts/user/login'

# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Custom User Model
AUTH_USER_MODEL = 'user_management.User'

# Stripe Keys (from .env file)
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

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
    'tinymce',
    'django_celery_beat',


    'whitenoise.runserver_nostatic',
    'rest_framework_simplejwt.token_blacklist',
    'equipment_management.apps.EquipmentManagementConfig',
    'user_management.apps.UserManagementConfig',
    'storages',  # Google Cloud Storage for media
]

# Rest Framework Configuration
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
    "AUTH_COOKIE": "token",
    "AUTH_COOKIE_REFRESH": "refresh",
}

# Email settings
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')

# Security Settings
CORS_ALLOW_CREDENTIALS = True

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

# Explicitly set CSRF_TRUSTED_ORIGINS and CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    'https://usenlease.com',
    'https://www.usenlease.com',
]

CORS_ALLOWED_ORIGINS = [
    'https://usenlease.com',
    'https://www.usenlease.com',
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://(\w+\.)?usenlease\.com$",
]

CORS_ALLOW_CREDENTIALS = True  # If using authentication

CORS_ALLOW_ALL_ORIGINS = False  # Avoid conflicts

# Cross-Origin Resource Sharing headers setup
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

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

# Detect if we're in a Docker build environment
DOCKER_BUILD = os.getenv("DOCKER_BUILD", "0") == "1"


# Database configuration (PostgreSQL on Heroku)
DATABASE_URL = os.getenv('DATABASE_URL')

if DOCKER_BUILD:
    print("Running in Docker build mode: Using dummy database")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.dummy'  # Avoid DB operations in Docker build
        }
    }
else:
    try:
        DATABASES = {
            'default': dj_database_url.config(default=DATABASE_URL)
        }

        # Check if database connection is available
        connection = psycopg2.connect(
            dbname=DATABASES['default']['NAME'],
            user=DATABASES['default']['USER'],
            password=DATABASES['default']['PASSWORD'],
            host=DATABASES['default']['HOST'],
            port=DATABASES['default']['PORT']
        )
        connection.close()

    except Exception as e:
        print(f"PostgreSQL configuration failed: {e}. Falling back to SQLite3.")
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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploads) – use Google Cloud Storage for media
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
# GS_DEFAULT_ACL = 'publicRead'  # Adjust based on your needs
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
