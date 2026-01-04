import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hillsclinic.settings')
django.setup()

from accounts.models import CustomUser
from allauth.account.models import EmailAddress

# Delete by email
deleted_users, _ = CustomUser.objects.filter(email='technofriend18@gmail.com').delete()
print(f"Deleted {deleted_users} user records")

# Delete email address
deleted_emails, _ = EmailAddress.objects.filter(email='technofriend18@gmail.com').delete()
print(f"Deleted {deleted_emails} email address records")

# Verify
remaining = CustomUser.objects.filter(email='technofriend18@gmail.com').count()
print(f"Remaining accounts with this email: {remaining}")
