"""
Admin configuration for portal app.
"""

from django.contrib import admin
from .models import PortalUpload, ConsentRecord, AuditLog


@admin.register(PortalUpload)
class PortalUploadAdmin(admin.ModelAdmin):
    list_display = ['patient', 'upload_type', 'title', 'is_verified', 'virus_scan_result', 'uploaded_at']
    list_filter = ['upload_type', 'is_verified', 'virus_scan_result', 'visible_to_patient', 'uploaded_at']
    search_fields = ['patient__user__email', 'title', 'description']
    readonly_fields = ['file_size', 'mime_type', 'uploaded_at', 'updated_at', 'verified_at', 'verified_by']
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Upload Information', {
            'fields': ('patient', 'upload_type', 'file', 'title', 'description')
        }),
        ('File Metadata', {
            'fields': ('file_size', 'mime_type'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verified_at')
        }),
        ('Security', {
            'fields': ('virus_scanned', 'virus_scan_result')
        }),
        ('Privacy', {
            'fields': ('visible_to_patient', 'shared_with_staff')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_verified', 'scan_virus']
    
    def mark_verified(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_verified=True, verified_by=request.user, verified_at=timezone.now())
        self.message_user(request, f"{queryset.count()} uploads marked as verified.")
    mark_verified.short_description = "Mark as verified"
    
    def scan_virus(self, request, queryset):
        for upload in queryset:
            upload.scan_for_virus()
        self.message_user(request, f"{queryset.count()} files queued for virus scan.")
    scan_virus.short_description = "Scan for viruses"


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'consent_type', 'granted', 'is_active', 'granted_at', 'revoked_at']
    list_filter = ['consent_type', 'granted', 'granted_at']
    search_fields = ['patient__user__email', 'consent_text']
    readonly_fields = ['granted_at', 'ip_address']
    date_hierarchy = 'granted_at'
    
    fieldsets = (
        ('Consent Information', {
            'fields': ('patient', 'consent_type', 'granted')
        }),
        ('Consent Details', {
            'fields': ('consent_text', 'patient_signature', 'ip_address')
        }),
        ('Validity', {
            'fields': ('granted_at', 'expires_at', 'revoked_at', 'revocation_reason')
        }),
        ('Related Content', {
            'fields': ('related_upload', 'related_success_story'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['revoke_consent']
    
    def revoke_consent(self, request, queryset):
        for consent in queryset:
            consent.revoke(reason="Revoked by administrator")
        self.message_user(request, f"{queryset.count()} consents revoked.")
    revoke_consent.short_description = "Revoke consent"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'patient', 'action', 'resource_type', 'is_suspicious']
    list_filter = ['action', 'resource_type', 'is_suspicious', 'timestamp']
    search_fields = ['user__email', 'patient__user__email', 'details']
    readonly_fields = ['timestamp', 'user', 'patient', 'action', 'resource_type', 'resource_id', 
                       'ip_address', 'user_agent', 'details', 'is_suspicious']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        """Audit logs cannot be added manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Audit logs cannot be modified."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Audit logs should not be deleted (immutable)."""
        return False
