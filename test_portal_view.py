#!/usr/bin/env python
"""Simple test to access portal view"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hillsclinic.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
client = Client()

# Try to get portal without login
response = client.get('/portal/')
print(f"Portal access (not logged in): {response.status_code}")
print(f"  Redirected to: {response.url if response.status_code == 302 else 'No redirect'}")

# Login and try again
user = User.objects.get(email='technofriend18@gmail.com')
client.force_login(user)

response = client.get('/portal/')
print(f"\nPortal access (logged in): {response.status_code}")
if response.status_code == 200:
    print("  ✓ Page loaded successfully")
    content = response.content.decode('utf-8')
    if 'Welcome,' in content:
        print("  ✓ Welcome message found")
    if 'Patient ID:' in content:
        print("  ✓ Patient ID found")
    if 'Upcoming Appointments' in content:
        print("  ✓ Appointments section found")
    print(f"\n  Content length: {len(content)} bytes")
elif response.status_code == 302:
    print(f"  Redirected to: {response.url}")
else:
    print(f"  Error: {response.status_code}")
