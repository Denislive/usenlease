from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create a superuser admin account'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@usenlease.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Lease@2025!")

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'⚠️ Superuser {username} already exists.')
            )
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Superuser {username} created successfully!')
            )