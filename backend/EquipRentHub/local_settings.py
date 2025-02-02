from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
import base64

# Load environment variables from .env
load_dotenv()

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent.parent


# Environment: 'development' or 'production'
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENVIRONMENT == 'development'

# Application domain
DOMAIN_URL = os.getenv('DOMAIN_URL', 'http://localhost:3000')

if not DEBUG:
    # Google Cloud Storage Bucket Name
    GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME')  # e.g., 'my-app-media'

    # Decode the base64 encoded credentials and write to a temporary file
    creds_path = os.path.join(BASE_DIR, 'credentials', 'google-credentials.json')
    creds_content = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_CONTENT')
    if creds_content:
        os.makedirs(os.path.dirname(creds_path), exist_ok=True)
        with open(creds_path, 'wb') as f:
            f.write(base64.b64decode(creds_content))

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError("The SECRET_KEY environment variable is not set")


if  DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS')

RECIPIENT_LIST = os.getenv('RECIPIENT_LIST')

# Login URL
LOGIN_URL = '/accounts/user/login'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

else:
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
    'AUTH_HEADER_TYPES': ('Bearer',),
    "AUTH_COOKIE": "token",
    "AUTH_COOKIE_REFRESH": "refresh",
}

# Email settings
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Store password securely
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')

# Security Settings
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'None')
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'None')
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'
SECURE_SSL_REDIRECT = False

CSRF_COOKIE_NAME = os.getenv('CSRF_COOKIE_NAME', 'csrftoken')
CSRF_COOKIE_HTTPONLY = os.getenv('CSRF_COOKIE_HTTPONLY', 'False') == 'True'

# Security Settings
if ENVIRONMENT == 'production':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

SESSION_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SAMESITE = 'None'

# CORS and CSRF
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:3000').split(',')


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

# Database configuration (PostgreSQL on Heroku)
DATABASE_URL = os.getenv('DATABASE_URL')
print(f"DATABASE_URL={DATABASE_URL}")  # Debug print

try:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL
        )
    }
    print(f"DATABASES={DATABASES}")  # Debug print

    import psycopg2
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

if not DEBUG:
    # Media files (uploads) – use Google Cloud Storage for media
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_DEFAULT_ACL = 'publicRead'  # Adjust based on your needs
    MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Debugging and logging
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
