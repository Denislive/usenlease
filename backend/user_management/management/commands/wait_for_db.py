# user_management/management/commands/wait_for_db.py

from django.core.management.base import BaseCommand
import time
import psycopg2
from psycopg2 import OperationalError
from django.conf import settings

class Command(BaseCommand):
    help = "Waits for the database to be ready"

    def handle(self, *args, **kwargs):
        while True:
            try:
                conn = psycopg2.connect(
                    dbname=settings.DATABASES['default']['NAME'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD'],
                    host=settings.DATABASES['default']['HOST'],
                    port=settings.DATABASES['default']['PORT'],
                )
                conn.close()
                self.stdout.write(self.style.SUCCESS('Database is ready!'))
                break
            except OperationalError:
                self.stdout.write(self.style.NOTICE('Database unavailable, waiting 1 second...'))
                time.sleep(1)
