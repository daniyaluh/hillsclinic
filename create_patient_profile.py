#!/usr/bin/env python
"""Create patient profile for user"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hillsclinic.settings')
django.setup()

from booking.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='technofriend18@gmail.com')

# Create patient profile
patient, created = Patient.objects.get_or_create(user=user)
print(f'Patient created: {created}')
print(f'Patient ID: {patient.id}')

# Check if it has the relation
user.refresh_from_db()
print(f'User has patient_profile: {hasattr(user, "patient_profile")}')
if hasattr(user, 'patient_profile'):
    print(f'Patient profile ID: {user.patient_profile.id}')
