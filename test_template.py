#!/usr/bin/env python
"""Test template rendering"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hillsclinic.settings')
django.setup()

from django.template import Template
from django.template.loader import get_template

try:
    template = get_template('portal/dashboard.html')
    print("✓ Dashboard template loaded successfully")
    print(f"  Template name: {template.template.name}")
except Exception as e:
    print(f"✗ Template error: {e}")
    import traceback
    traceback.print_exc()
