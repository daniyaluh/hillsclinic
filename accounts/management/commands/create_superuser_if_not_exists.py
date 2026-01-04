"""
Management command to create superuser from environment variables.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Creates a superuser from environment variables if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@hillsclinic.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
        
        if not password:
            self.stdout.write(self.style.WARNING(
                'DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation.'
            ))
            return
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(f'Superuser {email} already exists.')
            return
        
        User.objects.create_superuser(
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f'Superuser {email} created successfully!'))
