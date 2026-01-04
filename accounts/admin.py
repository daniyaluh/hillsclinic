"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from allauth.account.models import EmailAddress
from .models import CustomUser


def delete_users_completely(modeladmin, request, queryset):
    """
    Custom admin action to completely delete users including all related data.
    This ensures EmailAddress records from allauth are also deleted.
    """
    count = queryset.count()
    for user in queryset:
        # Delete allauth email addresses first (in case cascade doesn't work)
        EmailAddress.objects.filter(user=user).delete()
        
        # Delete the user (this should cascade to Patient, etc.)
        user.delete()
        
    messages.success(request, f"Successfully deleted {count} user(s) and all related data.")

delete_users_completely.short_description = "Delete selected users completely (including email records)"


# Unregister the default EmailAddress admin and register our custom one
try:
    admin.site.unregister(EmailAddress)
except admin.sites.NotRegistered:
    pass


@admin.register(EmailAddress)
class EmailAddressAdmin(admin.ModelAdmin):
    """Admin for allauth EmailAddress - helps debug orphaned email records."""
    list_display = ['email', 'user', 'verified', 'primary']
    list_filter = ['verified', 'primary']
    search_fields = ['email', 'user__username', 'user__email']
    raw_id_fields = ['user']
    
    actions = ['delete_orphaned_emails']
    
    def delete_orphaned_emails(self, request, queryset):
        """Delete email addresses where user no longer exists."""
        orphaned = queryset.filter(user__isnull=True)
        count = orphaned.count()
        orphaned.delete()
        messages.success(request, f"Deleted {count} orphaned email address(es).")
    
    delete_orphaned_emails.short_description = "Delete orphaned email addresses (no user)"

delete_users_completely.short_description = "Delete selected users completely (including email records)"


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
    
    actions = [delete_users_completely]
