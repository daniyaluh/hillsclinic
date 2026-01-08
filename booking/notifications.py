"""
Booking notifications for Hills Clinic.

Functions to send email notifications for appointment status changes.
"""

import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def send_appointment_confirmed(appointment):
    """Send email when appointment is confirmed (payment verified)."""
    try:
        patient = appointment.patient
        subject = f'Hills Clinic - Your Appointment #{appointment.id} is Confirmed!'
        
        logger.info(f"Sending appointment confirmation email to {patient.user.email}")
        
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
            fail_silently=False,
        )
        logger.info(f"Appointment confirmation email sent successfully to {patient.user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send confirmation email to {patient.user.email}: {e}", exc_info=True)
        return False


def send_payment_rejected(appointment, reason=None):
    """Send email when payment is rejected."""
    try:
        patient = appointment.patient
        subject = f'Hills Clinic - Payment Verification Failed for Appointment #{appointment.id}'
        
        logger.info(f"Sending payment rejected email to {patient.user.email}")
        
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
            fail_silently=False,
        )
        logger.info(f"Payment rejected email sent successfully to {patient.user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send payment rejected email to {patient.user.email}: {e}", exc_info=True)
        return False


def send_appointment_cancelled(appointment, reason='unpaid'):
    """Send email when appointment is cancelled (usually due to non-payment)."""
    try:
        patient = appointment.patient
        subject = f'Hills Clinic - Appointment #{appointment.id} Cancelled'
        
        logger.info(f"Sending appointment cancelled email to {patient.user.email}")
        
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
            fail_silently=False,
        )
        logger.info(f"Appointment cancelled email sent successfully to {patient.user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send cancellation email to {patient.user.email}: {e}", exc_info=True)
        return False
