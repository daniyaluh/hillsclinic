"""
Portal app models for Hills Clinic.

Models for patient portal functionality:
- PortalUpload
- ConsentRecord
- AuditLog
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import os

from portal.storage import PatientUploadStorage

User = get_user_model()


def upload_to_patient_folder(instance, filename):
    """Upload patient files to their specific folder."""
    # Get file extension
    ext = filename.split('.')[-1]
    # Rename file to avoid conflicts
    filename = f"{instance.upload_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return f'patient_uploads/{instance.patient.id}/{filename}'


class PortalUpload(models.Model):
    """Patient document and media uploads."""
    
    patient = models.ForeignKey(
        'booking.Patient',
        on_delete=models.CASCADE,
        related_name='uploads'
    )
    
    upload_type = models.CharField(
        max_length=50,
        choices=[
            ('xray', 'X-Ray'),
            ('photo', 'Photo'),
            ('medical_record', 'Medical Record'),
            ('id_document', 'ID Document'),
            ('insurance', 'Insurance Document'),
            ('other', 'Other'),
        ]
    )
    
    file = models.FileField(
        upload_to=upload_to_patient_folder,
        storage=PatientUploadStorage(),
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'dcm']
            )
        ],
        help_text="Allowed: PDF, JPG, PNG, GIF, DOC, DOCX, DCM (DICOM)"
    )
    
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    
    # File Metadata
    file_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Security
    is_verified = models.BooleanField(
        default=False,
        help_text="Staff has verified this document"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_uploads'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    virus_scanned = models.BooleanField(default=False)
    virus_scan_result = models.CharField(
        max_length=20,
        choices=[
            ('clean', 'Clean'),
            ('infected', 'Infected'),
            ('pending', 'Pending'),
        ],
        default='pending'
    )
    
    # Privacy
    visible_to_patient = models.BooleanField(
        default=True,
        help_text="Whether patient can see this file"
    )
    shared_with_staff = models.BooleanField(
        default=True,
        help_text="Whether staff can access this file"
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Portal Upload"
        verbose_name_plural = "Portal Uploads"
    
    def __str__(self):
        return f"{self.patient.user.email} - {self.get_upload_type_display()} ({self.uploaded_at.date()})"
    
    def save(self, *args, **kwargs):
        """Auto-populate file metadata on save."""
        if self.file:
            self.file_size = self.file.size
            # Get file extension as basic mime type
            ext = os.path.splitext(self.file.name)[1].lower()
            mime_types = {
                '.pdf': 'application/pdf',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.dcm': 'application/dicom',
            }
            self.mime_type = mime_types.get(ext, 'application/octet-stream')
        super().save(*args, **kwargs)
    
    def scan_for_virus(self):
        """Trigger virus scan (to be implemented with ClamAV or similar)."""
        # TODO: Implement with Celery task + ClamAV
        pass


class ConsentRecord(models.Model):
    """Patient consent tracking for media usage and testimonials."""
    
    patient = models.ForeignKey(
        'booking.Patient',
        on_delete=models.CASCADE,
        related_name='consents'
    )
    
    CONSENT_TYPE_CHOICES = [
        # Procedure Consents (Required)
        ('procedure_consent', 'Surgery Procedure Consent'),
        ('anesthesia_consent', 'Anesthesia Consent'),
        ('risks_acknowledgment', 'Risks & Complications Acknowledgment'),
        # Media Consents (Optional)
        ('media_use', 'Media Use (Photos/Videos)'),
        ('testimonial', 'Testimonial Publication'),
        ('face_visible', 'Face Visible in Media'),
        ('before_after', 'Before/After Photos'),
        # Other Consents
        ('research', 'Research Participation'),
        ('marketing', 'Marketing Communications'),
        ('data_sharing', 'Data Sharing with Partners'),
    ]
    
    # Which consents are required before surgery
    REQUIRED_FOR_SURGERY = ['procedure_consent', 'anesthesia_consent', 'risks_acknowledgment']
    
    consent_type = models.CharField(
        max_length=50,
        choices=CONSENT_TYPE_CHOICES
    )
    
    granted = models.BooleanField(
        default=False,
        help_text="Whether consent is granted or denied"
    )
    
    # Consent Details
    consent_text = models.TextField(
        help_text="Full text of consent agreement shown to patient"
    )
    patient_signature = models.CharField(
        max_length=255,
        blank=True,
        help_text="Digital signature or typed name"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address when consent was given"
    )
    
    # Validity
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional expiration date for consent"
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When consent was revoked, if applicable"
    )
    revocation_reason = models.TextField(blank=True)
    
    # Revocation Review (patient requests, staff approves)
    revocation_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When patient requested revocation"
    )
    revocation_reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revocation_reviewed_consents',
        help_text="Staff member who reviewed the revocation request"
    )
    revocation_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Staff Review
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_consents',
        help_text="Staff member who reviewed this consent"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    staff_notes = models.TextField(
        blank=True,
        help_text="Internal notes from staff review"
    )
    
    # Audit Trail
    related_upload = models.ForeignKey(
        PortalUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consent_records'
    )
    related_success_story = models.ForeignKey(
        'cms.SuccessStoryPage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consent_records'
    )
    related_appointment = models.ForeignKey(
        'booking.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consent_records',
        help_text="Appointment this consent is related to"
    )
    
    class Meta:
        ordering = ['-granted_at']
        verbose_name = "Consent Record"
        verbose_name_plural = "Consent Records"
    
    def __str__(self):
        status = "Granted" if self.granted else "Denied"
        if self.revoked_at:
            status = "Revoked"
        elif self.revocation_requested_at:
            status = "Revocation Pending"
        return f"{self.patient.user.email} - {self.get_consent_type_display()} ({status})"
    
    @property
    def is_active(self):
        """Check if consent is currently active."""
        if not self.granted or self.revoked_at:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
    
    @property
    def is_revocation_pending(self):
        """Check if revocation is pending review."""
        return self.revocation_requested_at is not None and self.revoked_at is None
    
    @property
    def is_reviewed(self):
        """Check if consent has been reviewed by staff."""
        return self.reviewed_by is not None
    
    @property
    def is_required_for_surgery(self):
        """Check if this consent type is required for surgery."""
        return self.consent_type in self.REQUIRED_FOR_SURGERY
    
    def request_revocation(self, reason=""):
        """Request revocation (pending staff review)."""
        self.revocation_requested_at = timezone.now()
        self.revocation_reason = reason
        self.save()
    
    def approve_revocation(self, staff_user):
        """Approve revocation request."""
        self.revoked_at = timezone.now()
        self.revocation_reviewed_by = staff_user
        self.revocation_reviewed_at = timezone.now()
        self.save()
    
    def revoke(self, reason=""):
        """Revoke consent."""
        self.revoked_at = timezone.now()
        self.revocation_reason = reason
        self.save()
    
    def mark_reviewed(self, staff_user, notes=""):
        """Mark consent as reviewed by staff."""
        self.reviewed_by = staff_user
        self.reviewed_at = timezone.now()
        self.staff_notes = notes
        self.save()
    
    @classmethod
    def get_patient_consent_status(cls, patient):
        """Get consent status summary for a patient."""
        consent_status = {}
        for consent_type, label in cls.CONSENT_TYPE_CHOICES:
            latest = cls.objects.filter(
                patient=patient,
                consent_type=consent_type
            ).order_by('-granted_at').first()
            
            consent_status[consent_type] = {
                'label': label,
                'record': latest,
                'is_active': latest.is_active if latest else False,
                'is_required': consent_type in cls.REQUIRED_FOR_SURGERY,
            }
        return consent_status
    
    @classmethod
    def check_surgery_ready(cls, patient):
        """Check if patient has all required consents for surgery."""
        missing = []
        for consent_type in cls.REQUIRED_FOR_SURGERY:
            latest = cls.objects.filter(
                patient=patient,
                consent_type=consent_type,
                granted=True,
                revoked_at__isnull=True
            ).order_by('-granted_at').first()
            
            if not latest or not latest.is_active:
                missing.append(dict(cls.CONSENT_TYPE_CHOICES).get(consent_type, consent_type))
        
        return {
            'ready': len(missing) == 0,
            'missing': missing,
            'total_required': len(cls.REQUIRED_FOR_SURGERY),
            'completed': len(cls.REQUIRED_FOR_SURGERY) - len(missing),
        }


class AuditLog(models.Model):
    """Immutable audit log for compliance and security."""
    
    # Who
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    patient = models.ForeignKey(
        'booking.Patient',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="Patient whose data was accessed or modified"
    )
    
    # What
    action = models.CharField(
        max_length=50,
        choices=[
            ('view', 'View'),
            ('create', 'Create'),
            ('update', 'Update'),
            ('delete', 'Delete'),
            ('download', 'Download'),
            ('share', 'Share'),
            ('export', 'Export'),
            ('login', 'Login'),
            ('logout', 'Logout'),
            ('failed_login', 'Failed Login'),
        ]
    )
    
    resource_type = models.CharField(
        max_length=50,
        help_text="Type of resource (e.g., 'Appointment', 'PortalUpload')"
    )
    resource_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID of the resource"
    )
    
    # When & Where
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Context
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context about the action"
    )
    
    # Security
    is_suspicious = models.BooleanField(
        default=False,
        help_text="Flagged by security monitoring"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['patient', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        user_str = self.user.email if self.user else "Anonymous"
        patient_str = f" (Patient: {self.patient.user.email})" if self.patient else ""
        return f"{user_str} - {self.action} {self.resource_type}{patient_str} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        """Prevent updates to audit logs (immutable)."""
        if self.pk:
            raise ValueError("Audit logs cannot be modified after creation")
        super().save(*args, **kwargs)


class Notification(models.Model):
    """User notifications for appointments, payments, and other events."""
    
    NOTIFICATION_TYPES = [
        # Patient notifications
        ('appointment_submitted', 'Appointment Request Submitted'),
        ('payment_verified', 'Payment Verified'),
        ('payment_rejected', 'Payment Rejected'),
        ('appointment_confirmed', 'Appointment Confirmed'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('slot_assigned', 'Time Slot Assigned'),
        ('reminder', 'Appointment Reminder'),
        ('document_verified', 'Document Verified'),
        # Staff notifications
        ('new_appointment', 'New Appointment Request'),
        ('payment_submitted', 'Payment Proof Submitted'),
        ('document_uploaded', 'Document Uploaded'),
        ('consent_granted', 'Consent Granted'),
        ('consent_revoked', 'Consent Revoked'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES
    )
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Link to related object
    related_appointment = models.ForeignKey(
        'booking.Appointment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # URL to redirect when clicked
    action_url = models.CharField(max_length=500, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @classmethod
    def create_for_user(cls, user, notification_type, title, message, appointment=None, action_url=''):
        """Create a notification for a user."""
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_appointment=appointment,
            action_url=action_url
        )
    
    @classmethod
    def create_for_staff(cls, notification_type, title, message, appointment=None, action_url=''):
        """Create notifications for all staff members."""
        staff_users = User.objects.filter(is_staff=True)
        notifications = []
        for user in staff_users:
            notifications.append(cls(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_appointment=appointment,
                action_url=action_url
            ))
        return cls.objects.bulk_create(notifications)
    
    @classmethod
    def unread_count(cls, user):
        """Get unread notification count for a user."""
        return cls.objects.filter(user=user, is_read=False).count()
