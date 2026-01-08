"""
Admin configuration for accounts app.
"""

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponseRedirect
from allauth.account.models import EmailAddress
from .models import CustomUser


class PasswordConfirmForm(forms.Form):
    """Form to confirm admin password before deleting users."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'vTextField',
            'placeholder': 'Enter your password to confirm',
            'autofocus': True,
        }),
        label="Your Admin Password",
        help_text="Enter your password to confirm this deletion action."
    )


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
    
    actions = ['delete_users_with_confirmation']
    
    def get_urls(self):
        """Add custom URL for password-confirmed deletion."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'delete-users-confirm/',
                self.admin_site.admin_view(self.delete_users_confirm_view),
                name='accounts_customuser_delete_confirm',
            ),
        ]
        return custom_urls + urls
    
    def delete_users_with_confirmation(self, request, queryset):
        """Redirect to password confirmation page before deleting."""
        # Store selected user IDs in session
        request.session['users_to_delete'] = list(queryset.values_list('id', flat=True))
        request.session['users_to_delete_info'] = [
            f"{u.email or u.username}" for u in queryset
        ]
        return HttpResponseRedirect('../delete-users-confirm/')
    
    delete_users_with_confirmation.short_description = "🗑️ Delete users completely (requires password)"
    
    def delete_users_confirm_view(self, request):
        """View to confirm deletion with password."""
        user_ids = request.session.get('users_to_delete', [])
        user_info = request.session.get('users_to_delete_info', [])
        
        if not user_ids:
            messages.error(request, "No users selected for deletion.")
            return redirect('..')
        
        users = CustomUser.objects.filter(id__in=user_ids)
        
        if request.method == 'POST':
            form = PasswordConfirmForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                
                # Verify admin password
                admin_user = authenticate(
                    request,
                    username=request.user.username,
                    password=password
                )
                
                if admin_user is not None and admin_user == request.user:
                    # Password verified - proceed with deletion
                    count = 0
                    deleted_info = []
                    
                    for user in users:
                        try:
                            email = user.email or user.username
                            
                            # Get related data counts for logging
                            patient = getattr(user, 'patient_profile', None)
                            appointments_count = 0
                            uploads_count = 0
                            
                            if patient:
                                appointments_count = patient.appointments.count()
                                uploads_count = patient.uploads.count()
                            
                            # Delete allauth email addresses
                            EmailAddress.objects.filter(user=user).delete()
                            
                            # Delete user (cascades to Patient, Appointments, Uploads, etc.)
                            user.delete()
                            
                            deleted_info.append(
                                f"{email} (appointments: {appointments_count}, uploads: {uploads_count})"
                            )
                            count += 1
                            
                        except Exception as e:
                            messages.error(request, f"Error deleting {user.email}: {str(e)}")
                    
                    # Clear session
                    del request.session['users_to_delete']
                    del request.session['users_to_delete_info']
                    
                    messages.success(
                        request,
                        f"✅ Successfully deleted {count} user(s) and ALL their data: {', '.join(deleted_info)}"
                    )
                    return redirect('..')
                else:
                    messages.error(request, "❌ Incorrect password. Deletion cancelled.")
        else:
            form = PasswordConfirmForm()
        
        # Gather info about what will be deleted
        deletion_preview = []
        for user in users:
            patient = getattr(user, 'patient_profile', None)
            info = {
                'email': user.email or user.username,
                'name': user.get_full_name() or 'N/A',
                'appointments': patient.appointments.count() if patient else 0,
                'uploads': patient.uploads.count() if patient else 0,
                'has_patient': patient is not None,
            }
            deletion_preview.append(info)
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Confirm User Deletion',
            'form': form,
            'users': deletion_preview,
            'user_count': len(users),
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/accounts/delete_users_confirm.html', context)
