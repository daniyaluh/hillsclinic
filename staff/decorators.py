"""
Custom decorators for staff portal access control.

Role Separation:
- Staff: Manage appointments, payments, time slots, patient queue
- Doctor: View patients, appointments, calendar, verify documents
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def staff_required(view_func):
    """
    Decorator that checks if user is staff or superuser.
    Used for: payment verification, appointment scheduling, time slot management.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access the staff portal.")
            return redirect('account_login')
        
        # Only allow superusers or staff (NOT just doctors)
        has_access = (
            request.user.is_superuser or 
            request.user.is_staff
        )
        
        if not has_access:
            raise PermissionDenied("You don't have permission to access this page. Staff access required.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def doctor_required(view_func):
    """
    Decorator that checks if user is a doctor, staff, or superuser.
    Used for: viewing patients, appointments, calendar, verifying documents.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('account_login')
        
        # Check if user is superuser, staff, or in 'Doctors' group
        is_doctor = (
            request.user.is_superuser or 
            request.user.is_staff or
            request.user.groups.filter(name='Doctors').exists()
        )
        
        if not is_doctor:
            raise PermissionDenied("You don't have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def is_staff_user(user):
    """Check if user is staff (not just doctor)."""
    return user.is_superuser or user.is_staff


def is_doctor_user(user):
    """Check if user is a doctor."""
    return user.groups.filter(name='Doctors').exists()


def is_doctor_only(user):
    """Check if user is ONLY a doctor (not staff)."""
    return is_doctor_user(user) and not user.is_staff and not user.is_superuser
