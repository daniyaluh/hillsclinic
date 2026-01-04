"""
Management command to cancel unpaid appointments that have exceeded their payment deadline.

Run this command periodically (e.g., via cron or Windows Task Scheduler):
    python manage.py cancel_unpaid_appointments
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from booking.models import Appointment


class Command(BaseCommand):
    help = 'Cancel appointments where payment deadline has passed and payment is not verified'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cancelled without actually cancelling',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        
        # Find appointments that are:
        # 1. Not cancelled or completed
        # 2. Have a payment deadline that has passed
        # 3. Payment is not verified
        overdue_appointments = Appointment.objects.filter(
            status__in=['pending', 'confirmed'],
            payment_deadline__lt=now,
            payment_status__in=['pending', 'submitted', 'failed']
        ).select_related('patient__user')
        
        count = overdue_appointments.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No overdue unpaid appointments found.'))
            return
        
        self.stdout.write(f'Found {count} overdue unpaid appointment(s):')
        
        for appointment in overdue_appointments:
            patient_email = appointment.patient.user.email
            deadline = appointment.payment_deadline
            
            self.stdout.write(f'  - Appointment #{appointment.id}: {patient_email} (deadline: {deadline})')
            
            if not dry_run:
                appointment.status = 'cancelled'
                appointment.doctor_notes = (
                    (appointment.doctor_notes or '') + 
                    f'\n[Auto-cancelled {now.strftime("%Y-%m-%d %H:%M")}: Payment deadline expired]'
                ).strip()
                appointment.save(update_fields=['status', 'doctor_notes'])
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would have cancelled {count} appointment(s).'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully cancelled {count} appointment(s).'))
