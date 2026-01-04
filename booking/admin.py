"""
Admin configuration for booking app.
"""

from django.contrib import admin
from .models import TimeSlot, Appointment, Patient, VideoConsultation, Payment


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'country', 'phone_number', 'interested_in_procedure', 'created_at']
    list_filter = ['country', 'interested_in_procedure', 'preferred_language', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'phone_number', 'country']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'whatsapp_number')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'country', 'city', 'timezone', 'preferred_language')
        }),
        ('Medical Information', {
            'fields': ('current_height', 'desired_height_gain', 'medical_conditions', 'medications', 'allergies')
        }),
        ('Preferences', {
            'fields': ('interested_in_procedure',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'end_time', 'timezone', 'slot_type', 'is_available', 'current_bookings', 'max_bookings']
    list_filter = ['is_available', 'slot_type', 'date']
    search_fields = ['date']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Time Information', {
            'fields': ('date', 'start_time', 'end_time', 'timezone')
        }),
        ('Slot Configuration', {
            'fields': ('slot_type', 'max_bookings', 'is_available')
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'time_slot', 'appointment_type', 'status', 'consultation_method', 'created_at']
    list_filter = ['status', 'appointment_type', 'consultation_method', 'created_at']
    search_fields = ['patient__user__email', 'patient__user__first_name', 'patient__user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'reminder_sent_24h', 'reminder_sent_1h']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'time_slot', 'appointment_type', 'status')
        }),
        ('Communication', {
            'fields': ('consultation_method', 'meeting_link')
        }),
        ('Notes', {
            'fields': ('patient_notes', 'doctor_notes')
        }),
        ('Calendar', {
            'fields': ('ics_file',),
            'classes': ('collapse',)
        }),
        ('Reminders', {
            'fields': ('reminder_sent_24h', 'reminder_sent_1h'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['send_confirmation', 'mark_confirmed', 'mark_completed']
    
    def send_confirmation(self, request, queryset):
        for appointment in queryset:
            appointment.send_confirmation_email()
        self.message_user(request, f"{queryset.count()} confirmations sent.")
    send_confirmation.short_description = "Send confirmation emails"
    
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f"{queryset.count()} appointments marked as confirmed.")
    mark_confirmed.short_description = "Mark as confirmed"
    
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} appointments marked as completed.")
    mark_completed.short_description = "Mark as completed"


@admin.register(VideoConsultation)
class VideoConsultationAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'patient_email', 'scheduled_date', 'scheduled_time', 'status', 'procedure_interest', 'created_at']
    list_filter = ['status', 'procedure_interest', 'scheduled_date', 'created_at']
    search_fields = ['patient_name', 'patient_email', 'patient_phone']
    readonly_fields = ['id', 'room_id', 'meeting_url', 'created_at', 'updated_at', 'started_at', 'ended_at']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('user', 'patient_name', 'patient_email', 'patient_phone', 'patient_country', 'patient_timezone')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time', 'duration_minutes', 'status')
        }),
        ('Video Conference', {
            'fields': ('room_id', 'meeting_url'),
            'classes': ('collapse',)
        }),
        ('Consultation Details', {
            'fields': ('reason', 'current_height', 'desired_height_gain', 'procedure_interest', 'medical_notes')
        }),
        ('Doctor Notes', {
            'fields': ('doctor_notes', 'recommendations', 'follow_up_required'),
            'classes': ('collapse',)
        }),
        ('Reminders', {
            'fields': ('reminder_sent_24h', 'reminder_sent_1h'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at', 'started_at', 'ended_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_scheduled', 'mark_completed', 'generate_meeting_rooms']
    
    def mark_scheduled(self, request, queryset):
        for consultation in queryset.filter(status='pending_payment'):
            consultation.status = 'scheduled'
            consultation.generate_meeting_room()
            consultation.save()
        self.message_user(request, f"Consultations marked as scheduled.")
    mark_scheduled.short_description = "Mark as scheduled (skip payment)"
    
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} consultations marked as completed.")
    mark_completed.short_description = "Mark as completed"
    
    def generate_meeting_rooms(self, request, queryset):
        for consultation in queryset.filter(room_id=''):
            consultation.generate_meeting_room()
        self.message_user(request, f"Meeting rooms generated.")
    generate_meeting_rooms.short_description = "Generate meeting rooms"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['email', 'payment_type', 'amount', 'currency', 'status', 'created_at', 'paid_at']
    list_filter = ['status', 'payment_type', 'currency', 'created_at']
    search_fields = ['email', 'stripe_session_id', 'stripe_payment_intent_id']
    readonly_fields = ['id', 'stripe_session_id', 'stripe_payment_intent_id', 'stripe_customer_id', 'created_at', 'updated_at', 'paid_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('user', 'email', 'payment_type', 'amount', 'currency', 'status', 'description')
        }),
        ('Related Records', {
            'fields': ('video_consultation', 'appointment'),
            'classes': ('collapse',)
        }),
        ('Stripe Information', {
            'fields': ('stripe_session_id', 'stripe_payment_intent_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'mark_refunded']
    
    def mark_completed(self, request, queryset):
        for payment in queryset.filter(status='pending'):
            payment.mark_completed()
        self.message_user(request, f"Payments marked as completed.")
    mark_completed.short_description = "Mark as completed"
    
    def mark_refunded(self, request, queryset):
        queryset.update(status='refunded')
        self.message_user(request, f"{queryset.count()} payments marked as refunded.")
    mark_refunded.short_description = "Mark as refunded"