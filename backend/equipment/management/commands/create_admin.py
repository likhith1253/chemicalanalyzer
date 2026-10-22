import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        'Create a superuser from the ADMIN_USERNAME, ADMIN_EMAIL and ADMIN_PASSWORD '
        'environment variables (no default credentials are ever created).'
    )

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME')
        email = os.environ.get('ADMIN_EMAIL', '')
        password = os.environ.get('ADMIN_PASSWORD')

        if not username or not password:
            raise CommandError('Set ADMIN_USERNAME and ADMIN_PASSWORD (and optionally ADMIN_EMAIL).')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists'))
            return

        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS(f'Created superuser "{username}"'))
