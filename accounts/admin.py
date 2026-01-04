"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('phone_number', 'timezone', 'preferred_language')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'sms_notifications', 'whatsapp_notifications')
        }),
        ('Account Type', {
            'fields': ('is_patient', 'is_doctor', 'is_staff_member')
        }),
    )
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_patient', 'is_doctor', 'is_staff']
    list_filter = BaseUserAdmin.list_filter + ('is_patient', 'is_doctor', 'is_staff_member', 'preferred_language')
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
