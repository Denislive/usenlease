from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
import os

class UserManagementConfig(AppConfig):
    name = 'user_management'

    def ready(self):
        # Avoid running this when doing migrations or collectstatic
        if os.environ.get('RUN_MAIN') != 'true':
            return

        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@usenlease.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Lease@2025!")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                is_verified=True  # ✅ Set is_verified to True
            )
            print(f"✅ Superuser {username} created successfully with is_verified=True!")
        else:
            print(f"⚠️ Superuser {username} already exists.")
