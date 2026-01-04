"""
Booking notifications for Hills Clinic.

Functions to send email notifications for appointment status changes.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_appointment_confirmed(appointment):
    """Send email when appointment is confirmed (payment verified)."""
    try:
        patient = appointment.patient
        subject = f'Hills Clinic - Your Appointment #{appointment.id} is Confirmed!'
        
        html_message = render_to_string('booking/emails/appointment_confirmed.html', {
            'patient': patient,
            'appointment': appointment,
        })
        
        send_mail(
            subject=subject,
            message=f"Your appointment #{appointment.id} has been confirmed. Check your portal for details.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.user.email],
            html_message=html_message,
            fail_silently=True,
        )
        return True
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")
        return False


def send_payment_rejected(appointment, reason=None):
    """Send email when payment is rejected."""
    try:
        patient = appointment.patient
        subject = f'Hills Clinic - Payment Verification Failed for Appointment #{appointment.id}'
        
        # Build payment URL
        payment_url = f"{settings.SITE_URL}/portal/appointments/{appointment.id}/payment/" if hasattr(settings, 'SITE_URL') else "#"
        
        html_message = render_to_string('booking/emails/payment_rejected.html', {
            'patient': patient,
            'appointment': appointment,
            'reason': reason,
            'payment_url': payment_url,
        })
        
        send_mail(
            subject=subject,
            message=f"We could not verify your payment for appointment #{appointment.id}. Please retry.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.user.email],
            html_message=html_message,
            fail_silently=True,
        )
        return True
    except Exception as e:
        print(f"Failed to send payment rejected email: {e}")
        return False


def send_appointment_cancelled(appointment, reason='unpaid'):
    """Send email when appointment is cancelled (usually due to non-payment)."""
    try:
        patient = appointment.patient
        subject = f'Hills Clinic - Appointment #{appointment.id} Cancelled'
        
        # Build booking URL
        booking_url = f"{settings.SITE_URL}/consultation/" if hasattr(settings, 'SITE_URL') else "#"
        
        html_message = render_to_string('booking/emails/appointment_cancelled.html', {
            'patient': patient,
            'appointment': appointment,
            'reason': reason,
            'booking_url': booking_url,
        })
        
        send_mail(
            subject=subject,
            message=f"Your appointment #{appointment.id} has been cancelled. Book a new one at {booking_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.user.email],
            html_message=html_message,
            fail_silently=True,
        )
        return True
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")
        return False
