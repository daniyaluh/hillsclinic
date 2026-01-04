#!/usr/bin/env python
"""Test dashboard rendering"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hillsclinic.settings')
django.setup()

from django.contrib.auth import get_user_model
from booking.models import Patient, Appointment
from portal.models import PortalUpload

User = get_user_model()

# Find test user
user = User.objects.filter(email__icontains='technofriend').first()

if user:
    print(f"\n✓ User found: {user.email}")
    print(f"  Name: {user.get_full_name()}")
    print(f"  Is active: {user.is_active}")
    
    # Check patient profile
    try:
        patient = user.patient_profile
        print(f"\n✓ Patient profile exists:")
        print(f"  ID: {patient.id}")
        print(f"  Phone: {patient.phone_number or 'Not set'}")
        print(f"  City: {patient.city or 'Not set'}")
        print(f"  Country: {patient.country or 'Not set'}")
        
        # Check appointments
        appts = Appointment.objects.filter(patient=patient)
        print(f"\n✓ Appointments: {appts.count()}")
        for appt in appts:
            print(f"  - {appt.get_appointment_type_display()} on {appt.time_slot.date}")
        
        # Check documents
        docs = PortalUpload.objects.filter(patient=patient)
        print(f"\n✓ Documents: {docs.count()}")
        for doc in docs:
            print(f"  - {doc.get_upload_type_display()}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
else:
    print("\n✗ No user found with email containing 'technofriend'")
    print(f"\nAvailable users:")
    for u in User.objects.all()[:5]:
        print(f"  - {u.email}")
