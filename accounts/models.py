"""
Accounts app models for Hills Clinic.

Custom user model with extended fields:
- CustomUser (extends AbstractUser)
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended user model with additional fields."""
    
    # Contact
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Preferences
    timezone = models.CharField(
        max_length=50,
        default='Asia/Karachi',
        help_text="User's local timezone (IANA timezone name)"
    )
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('ar', 'Arabic'),
            ('fa', 'Persian'),
            ('tr', 'Turkish'),
        ],
        default='en'
    )
    
    # Notifications
    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive email notifications"
    )
    sms_notifications = models.BooleanField(
        default=False,
        help_text="Receive SMS notifications"
    )
    whatsapp_notifications = models.BooleanField(
        default=False,
        help_text="Receive WhatsApp notifications"
    )
    
    # Account Type
    is_patient = models.BooleanField(default=True)
    is_doctor = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return self.email or self.username
