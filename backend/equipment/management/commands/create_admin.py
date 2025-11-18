from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates a default admin user if it does not exist'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'password'
        email = 'admin@example.com'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created admin user "{username}"'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin user "{username}" already exists'))
