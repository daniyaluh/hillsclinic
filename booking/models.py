"""
Booking app models for Hills Clinic.

Models for appointment scheduling and patient management:
- TimeSlot
- Appointment
- Patient
- VideoConsultation
- Payment
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils import timezone
import uuid
import pytz

User = get_user_model()


class TimeSlot(models.Model):
    """Available appointment time slots."""
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    timezone = models.CharField(
        max_length=50,
        default='Asia/Karachi',
        help_text="Timezone for this slot (IANA timezone name)"
    )
    is_available = models.BooleanField(default=True)
    slot_type = models.CharField(
        max_length=50,
        choices=[
            ('consultation', 'Initial Consultation'),
            ('follow_up', 'Follow-up'),
            ('surgery', 'Surgery Date'),
        ],
        default='consultation'
    )
    max_bookings = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = [['date', 'start_time', 'timezone']]
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"
    
    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time} ({self.timezone})"
    
    @property
    def current_bookings(self):
        """Count current bookings for this slot."""
        return self.appointments.filter(status__in=['confirmed', 'pending']).count()
    
    @property
    def is_full(self):
        """Check if slot is fully booked."""
        return self.current_bookings >= self.max_bookings


class Patient(models.Model):
    """Extended patient information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    whatsapp_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Name (stored separately from User for flexibility)
    full_name = models.CharField(max_length=200, blank=True, help_text="Patient's full name")
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        blank=True
    )
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(
        max_length=50,
        default='Asia/Karachi',
        help_text="Patient's local timezone"
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
    
    # Profile Picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="Patient's profile picture"
    )
    
    # Medical Information
    current_height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current height in centimeters"
    )
    desired_height_gain = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Desired height gain in centimeters"
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kilograms"
    )
    blood_type = models.CharField(
        max_length=5,
        choices=[
            ('O+', 'O+'),
            ('O-', 'O-'),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
        ],
        blank=True,
        help_text="Blood type"
    )
    medical_conditions = models.TextField(
        blank=True,
        help_text="Pre-existing medical conditions"
    )
    medications = models.TextField(
        blank=True,
        help_text="Current medications"
    )
    allergies = models.TextField(
        blank=True,
        help_text="Known allergies"
    )
    current_medications = models.TextField(
        blank=True,
        help_text="Current medications (duplicate for compatibility)"
    )
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_relation = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Preferences
    interested_in_procedure = models.CharField(
        max_length=50,
        choices=[
            ('ilizarov', 'Ilizarov (External)'),
            ('internal', 'Internal Nails'),
            ('lon', 'LON Method'),
            ('undecided', 'Not Sure Yet'),
        ],
        default='undecided',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
    
    def __str__(self):
        return f"{self.get_display_name()} - {self.country}"
    
    def get_display_name(self):
        """Get patient's display name - prioritize full_name, then user name, then email."""
        if self.full_name:
            return self.full_name
        if self.user.get_full_name():
            return self.user.get_full_name()
        return self.user.email


class Appointment(models.Model):
    """Patient appointment booking."""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    time_slot = models.ForeignKey(
        TimeSlot, 
        on_delete=models.CASCADE, 
        related_name='appointments',
        null=True,
        blank=True,
        help_text="Time slot for confirmed appointments. Null for initial consultation requests."
    )
    
    # Appointment Details
    appointment_type = models.CharField(
        max_length=50,
        choices=[
            ('consultation', 'Initial Consultation'),
            ('follow_up', 'Follow-up'),
            ('pre_op', 'Pre-operative Assessment'),
            ('surgery', 'Surgery'),
            ('post_op', 'Post-operative Check'),
        ],
        default='consultation'
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Confirmation'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
            ('completed', 'Completed'),
            ('no_show', 'No Show'),
        ],
        default='pending'
    )
    
    # Communication
    consultation_method = models.CharField(
        max_length=20,
        choices=[
            ('video', 'Video Call'),
            ('phone', 'Phone Call'),
            ('whatsapp', 'WhatsApp Chat'),
            ('in_clinic', 'In-Person at Clinic'),
        ],
        default='video'
    )
    meeting_link = models.URLField(blank=True, help_text="Video call link (Zoom, Google Meet, etc.)")
    
    # Notes
    patient_notes = models.TextField(
        blank=True,
        help_text="Patient's questions or concerns"
    )
    doctor_notes = models.TextField(
        blank=True,
        help_text="Doctor's internal notes"
    )
    
    # Calendar Integration
    ics_file = models.FileField(
        upload_to='appointments/ics/',
        blank=True,
        null=True,
        help_text="ICS calendar file for download"
    )
    
    # Reminders
    reminder_sent_24h = models.BooleanField(default=False)
    reminder_sent_1h = models.BooleanField(default=False)
    
    # Payment Information
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('submitted', 'Payment Submitted'),
        ('verified', 'Payment Verified'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('easypaisa', 'EasyPaisa'),
        ('jazzcash', 'JazzCash'),
        ('bank_transfer', 'Bank Transfer'),
        ('stripe', 'Stripe (Card)'),
    ]
    
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10.00,
        help_text="Consultation fee in USD"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True
    )
    payment_proof = models.ImageField(
        upload_to='payment_proofs/',
        null=True,
        blank=True,
        help_text="Screenshot of payment (for EasyPaisa/JazzCash/Bank)"
    )
    payment_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Payment must be completed before this time"
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Stripe Payment Intent ID"
    )
    payment_confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_payments'
    )
    payment_confirmed_at = models.DateTimeField(null=True, blank=True)
    payment_notes = models.TextField(blank=True, help_text="Notes about payment verification")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['time_slot__date', 'time_slot__start_time']
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
    
    def __str__(self):
        if self.time_slot:
            return f"{self.patient.user.email} - {self.time_slot} ({self.get_status_display()})"
        return f"{self.patient.user.email} - Unscheduled ({self.get_status_display()})"
    
    def set_payment_deadline(self):
        """Set payment deadline to 48 hours from now."""
        self.payment_deadline = timezone.now() + timezone.timedelta(hours=48)
        self.save(update_fields=['payment_deadline'])
    
    def is_payment_overdue(self):
        """Check if payment deadline has passed."""
        if self.payment_status == 'verified':
            return False
        if self.payment_deadline and timezone.now() > self.payment_deadline:
            return True
        return False
    
    def cancel_if_unpaid(self):
        """Cancel appointment if payment is overdue."""
        if self.is_payment_overdue() and self.status not in ['cancelled', 'completed']:
            self.status = 'cancelled'
            self.doctor_notes = (self.doctor_notes or '') + '\n[Auto-cancelled: Payment deadline expired]'
            self.save(update_fields=['status', 'doctor_notes'])
            return True
        return False
    
    def is_past_appointment(self):
        """Check if appointment time has passed."""
        if not self.time_slot:
            return False
        from datetime import datetime, timedelta
        slot_end = timezone.make_aware(
            datetime.combine(self.time_slot.date, self.time_slot.end_time)
        )
        # Consider appointment past if end time + 1 hour has passed
        return timezone.now() > slot_end + timedelta(hours=1)
    
    def complete_if_past(self):
        """Mark appointment as completed if time has passed."""
        if self.status == 'confirmed' and self.is_past_appointment():
            self.status = 'completed'
            self.save(update_fields=['status'])
            return True
        return False
    
    @classmethod
    def auto_update_statuses(cls):
        """Auto-update all appointments: cancel unpaid, complete past ones."""
        from datetime import datetime, timedelta
        now = timezone.now()
        
        # 1. Cancel unpaid appointments past deadline
        unpaid_cancelled = cls.objects.filter(
            status__in=['pending', 'confirmed'],
            payment_deadline__lt=now,
            payment_status__in=['pending', 'submitted', 'failed']
        ).update(status='cancelled')
        
        # 2. Complete past confirmed appointments (with time slots)
        past_completed = 0
        past_appointments = cls.objects.filter(
            status='confirmed',
            time_slot__isnull=False
        ).select_related('time_slot', 'patient__user')
        
        for apt in past_appointments:
            slot_end = timezone.make_aware(
                datetime.combine(apt.time_slot.date, apt.time_slot.end_time)
            )
            if now > slot_end + timedelta(hours=1):
                apt.status = 'completed'
                apt.save(update_fields=['status'])
                # Send notification to patient
                try:
                    from booking.notification_helpers import notify_appointment_completed
                    notify_appointment_completed(apt)
                except Exception:
                    pass  # Don't fail auto-update if notification fails
                past_completed += 1
        
        return {'unpaid_cancelled': unpaid_cancelled, 'past_completed': past_completed}
    
    def get_patient_local_time(self):
        """Convert appointment time to patient's timezone."""
        slot_tz = pytz.timezone(self.time_slot.timezone)
        patient_tz = pytz.timezone(self.patient.timezone)
        
        # Combine date and time
        naive_datetime = timezone.datetime.combine(
            self.time_slot.date,
            self.time_slot.start_time
        )
        
        # Localize to slot timezone
        slot_datetime = slot_tz.localize(naive_datetime)
        
        # Convert to patient timezone
        patient_datetime = slot_datetime.astimezone(patient_tz)
        
        return patient_datetime
    
    def send_confirmation_email(self):
        """Send appointment confirmation email with ICS file."""
        # TODO: Implement with Celery task
        pass
    
    def send_reminder(self, hours_before):
        """Send appointment reminder."""
        # TODO: Implement with Celery task
        pass


class VideoConsultation(models.Model):
    """Video consultation booking and management."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Patient info (can be linked user or guest)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='video_consultations'
    )
    patient_name = models.CharField(max_length=255)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=20, blank=True)
    patient_country = models.CharField(max_length=100, blank=True)
    patient_timezone = models.CharField(max_length=50, default='UTC')
    
    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=30)
    
    # Status
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    
    # Video conference details
    room_id = models.CharField(max_length=100, blank=True)
    meeting_url = models.URLField(blank=True)
    
    # Consultation details
    reason = models.TextField(help_text="Reason for consultation")
    current_height = models.CharField(max_length=20, blank=True)
    desired_height_gain = models.CharField(max_length=20, blank=True)
    procedure_interest = models.CharField(
        max_length=50,
        choices=[
            ('ilizarov', 'Ilizarov (External Fixator)'),
            ('internal', 'Internal Lengthening Nail'),
            ('lon', 'LON Method'),
            ('undecided', 'Not Sure Yet'),
        ],
        default='undecided'
    )
    medical_notes = models.TextField(blank=True, help_text="Relevant medical history")
    
    # Doctor notes (after consultation)
    doctor_notes = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    
    # Reminders
    reminder_sent_24h = models.BooleanField(default=False)
    reminder_sent_1h = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']
        verbose_name = "Video Consultation"
        verbose_name_plural = "Video Consultations"
    
    def __str__(self):
        return f"{self.patient_name} - {self.scheduled_date} {self.scheduled_time}"
    
    def get_absolute_url(self):
        return reverse('booking:video_consultation_detail', kwargs={'pk': self.pk})
    
    def get_join_url(self):
        return reverse('booking:video_consultation_join', kwargs={'pk': self.pk})
    
    @property
    def scheduled_datetime(self):
        """Get combined datetime object."""
        return timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
    
    @property
    def is_upcoming(self):
        """Check if consultation is in the future."""
        now = timezone.now()
        scheduled = timezone.make_aware(
            self.scheduled_datetime,
            timezone.get_current_timezone()
        )
        return scheduled > now
    
    @property
    def can_join(self):
        """Check if the meeting can be joined (10 min before to 30 min after start)."""
        if self.status not in ['scheduled', 'in_progress']:
            return False
        
        now = timezone.now()
        scheduled = timezone.make_aware(
            self.scheduled_datetime,
            timezone.get_current_timezone()
        )
        
        # Allow joining 10 minutes before
        earliest_join = scheduled - timezone.timedelta(minutes=10)
        # Allow joining up to duration + 15 minutes after
        latest_join = scheduled + timezone.timedelta(minutes=self.duration_minutes + 15)
        
        return earliest_join <= now <= latest_join
    
    def generate_meeting_room(self):
        """Generate video meeting room."""
        from .video_conference import VideoConferenceService
        self.room_id, self.meeting_url = VideoConferenceService.create_consultation_room(self)
        self.save(update_fields=['room_id', 'meeting_url'])
    
    def start_consultation(self):
        """Mark consultation as started."""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def end_consultation(self):
        """Mark consultation as completed."""
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save(update_fields=['status', 'ended_at'])


class Payment(models.Model):
    """Payment records for consultations and deposits."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Link to user/patient
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    email = models.EmailField()
    
    # Payment type
    PAYMENT_TYPE_CHOICES = [
        ('video_consultation', 'Video Consultation Fee'),
        ('consultation_deposit', 'Consultation Deposit'),
        ('surgery_deposit', 'Surgery Deposit'),
        ('full_payment', 'Full Payment'),
        ('other', 'Other'),
    ]
    payment_type = models.CharField(max_length=30, choices=PAYMENT_TYPE_CHOICES)
    
    # Related records
    video_consultation = models.ForeignKey(
        VideoConsultation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    appointment = models.ForeignKey(
        'Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Stripe integration
    stripe_session_id = models.CharField(max_length=255, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
    
    def __str__(self):
        return f"{self.email} - {self.get_payment_type_display()} - ${self.amount}"
    
    @property
    def amount_cents(self):
        """Return amount in cents for Stripe."""
        return int(self.amount * 100)
    
    def mark_completed(self, payment_intent_id: str = None):
        """Mark payment as completed."""
        self.status = 'completed'
        self.paid_at = timezone.now()
        if payment_intent_id:
            self.stripe_payment_intent_id = payment_intent_id
        self.save()
        
        # Update related consultation status
        if self.video_consultation and self.video_consultation.status == 'pending_payment':
            self.video_consultation.status = 'scheduled'
            self.video_consultation.generate_meeting_room()
            self.video_consultation.save()
    
    def mark_failed(self):
        """Mark payment as failed."""
        self.status = 'failed'
        self.save()
