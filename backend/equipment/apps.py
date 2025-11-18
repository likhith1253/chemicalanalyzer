from django.apps import AppConfig
import os


class EquipmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'equipment'
    verbose_name = 'Equipment Management'
    
    def ready(self):
        """
        Create default admin user if it doesn't exist.
        This runs after Django is fully initialized.
        """
        # Only run in non-testing environments
        if os.environ.get('DJANGO_SETTINGS_MODULE') and 'test' not in os.environ.get('DJANGO_SETTINGS_MODULE', '').lower():
            try:
                from django.contrib.auth.models import User
                from django.db import transaction
                
                # Use transaction to avoid race conditions
                with transaction.atomic():
                    if not User.objects.filter(username='admin').exists():
                        User.objects.create_superuser(
                            username='admin',
                            email='admin@example.com',
                            password='password',
                            is_superuser=True,
                            is_staff=True
                        )
                        print("✓ Created default admin user: admin/password")
            except Exception as e:
                # Ignore errors during migrations or if DB is not ready
                if 'migrate' not in str(e).lower() and 'table' not in str(e).lower():
                    print(f"Note: Could not create default admin user: {e}")
