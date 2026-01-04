"""
Notification helper functions for Hills Clinic.

Centralized functions to create notifications for various events.
"""

from django.contrib.auth import get_user_model
from portal.models import Notification

User = get_user_model()


def notify_appointment_submitted(appointment):
    """Notify patient that their appointment request was submitted."""
    Notification.create_for_user(
        user=appointment.patient.user,
        notification_type='appointment_submitted',
        title='Appointment Request Submitted',
        message=f'Your consultation request #{appointment.id} has been submitted. Please complete payment within 48 hours.',
        appointment=appointment,
        action_url=f'/portal/appointments/{appointment.id}/payment/'
    )
    
    # Notify staff about new appointment
    Notification.create_for_staff(
        notification_type='new_appointment',
        title='New Appointment Request',
        message=f'New consultation request from {appointment.patient.full_name or appointment.patient.user.email}.',
        appointment=appointment,
        action_url=f'/staff/appointments/{appointment.id}/'
    )


def notify_payment_submitted(appointment):
    """Notify staff that payment proof was submitted."""
    Notification.create_for_staff(
        notification_type='payment_submitted',
        title='Payment Proof Submitted',
        message=f'Payment proof submitted for appointment #{appointment.id} by {appointment.patient.full_name or appointment.patient.user.email}.',
        appointment=appointment,
        action_url=f'/staff/appointments/{appointment.id}/'
    )


def notify_payment_verified(appointment):
    """Notify patient that their payment was verified."""
    Notification.create_for_user(
        user=appointment.patient.user,
        notification_type='payment_verified',
        title='Payment Verified',
        message=f'Your payment for appointment #{appointment.id} has been verified. A doctor will assign your time slot soon.',
        appointment=appointment,
        action_url='/portal/appointments/'
    )


def notify_payment_rejected(appointment, reason=None):
    """Notify patient that their payment was rejected."""
    message = f'Your payment for appointment #{appointment.id} could not be verified.'
    if reason:
        message += f' Reason: {reason}'
    message += ' Please resubmit payment.'
    
    Notification.create_for_user(
        user=appointment.patient.user,
        notification_type='payment_rejected',
        title='Payment Verification Failed',
        message=message,
        appointment=appointment,
        action_url=f'/portal/appointments/{appointment.id}/payment/'
    )


def notify_slot_assigned(appointment):
    """Notify patient that a time slot was assigned."""
    slot = appointment.time_slot
    if slot:
        slot_str = f'{slot.date.strftime("%B %d, %Y")} at {slot.start_time.strftime("%I:%M %p")}'
    else:
        slot_str = 'TBD'
    
    Notification.create_for_user(
        user=appointment.patient.user,
        notification_type='slot_assigned',
        title='Appointment Time Scheduled',
        message=f'Your appointment #{appointment.id} is scheduled for {slot_str}.',
        appointment=appointment,
        action_url='/portal/appointments/calendar/'
    )


def notify_appointment_confirmed(appointment):
    """Notify patient that their appointment is confirmed."""
    slot = appointment.time_slot
    if slot:
        slot_str = f'{slot.date.strftime("%B %d, %Y")} at {slot.start_time.strftime("%I:%M %p")}'
    else:
        slot_str = 'Check your portal for details'
    
    Notification.create_for_user(
        user=appointment.patient.user,
        notification_type='appointment_confirmed',
        title='Appointment Confirmed!',
        message=f'Your consultation appointment is confirmed for {slot_str}.',
        appointment=appointment,
        action_url='/portal/appointments/'
    )


def notify_appointment_cancelled(appointment, reason=None):
    """Notify patient that their appointment was cancelled."""
    message = f'Your appointment #{appointment.id} has been cancelled.'
    if reason:
        message += f' Reason: {reason}'
    
    Notification.create_for_user(
        user=appointment.patient.user,
        notification_type='appointment_cancelled',
        title='Appointment Cancelled',
        message=message,
        appointment=appointment,
        action_url='/portal/appointments/'
    )


def notify_appointment_completed(appointment):
    """Notify patient that their appointment has been completed."""
    slot = appointment.time_slot
    if slot:
        slot_str = f'{slot.date.strftime("%B %d, %Y")}'
    else:
        slot_str = ''
    
    message = f'Your consultation appointment'
    if slot_str:
        message += f' on {slot_str}'
    message += ' has been completed. Thank you for choosing Hills Clinic!'
    
    Notification.create_for_user(
        user=appointment.patient.user,
        notification_type='appointment_confirmed',  # Reuse confirmed type with green icon
        title='Consultation Completed',
        message=message,
        appointment=appointment,
        action_url='/portal/appointments/'
    )
