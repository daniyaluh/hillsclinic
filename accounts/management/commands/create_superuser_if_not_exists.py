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
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        
        if not password:
            self.stdout.write(self.style.WARNING(
                'DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation.'
            ))
            return
        
        user = User.objects.filter(email=email).first()
        
        if user:
            self.stdout.write(f'Superuser {email} already exists.')
            # Ensure email is verified for existing superuser
            self._verify_email(user, email)
            return
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'User with username {username} already exists.')
            return
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f'Superuser {email} created successfully!'))
        
        # Mark email as verified for superuser (so they don't need to verify)
        self._verify_email(user, email)
    
    def _verify_email(self, user, email):
        """Mark the superuser's email as verified in allauth EmailAddress table."""
        try:
            from allauth.account.models import EmailAddress
            
            email_address, created = EmailAddress.objects.get_or_create(
                user=user,
                email=email,
                defaults={'verified': True, 'primary': True}
            )
            
            if not email_address.verified:
                email_address.verified = True
                email_address.primary = True
                email_address.save()
                self.stdout.write(self.style.SUCCESS(f'Email {email} marked as verified.'))
            elif created:
                self.stdout.write(self.style.SUCCESS(f'Email {email} created and verified.'))
            else:
                self.stdout.write(f'Email {email} already verified.')
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not verify email: {e}'))
