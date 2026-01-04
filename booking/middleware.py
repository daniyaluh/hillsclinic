"""
Middleware for booking app.

Handles automatic status updates for appointments.
"""

from django.utils import timezone
from django.core.cache import cache


class AppointmentStatusMiddleware:
    """
    Middleware to automatically update appointment statuses.
    
    - Cancels unpaid appointments past their deadline
    - Marks confirmed appointments as completed when their time passes
    
    Runs at most once every 5 minutes to avoid performance issues.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only run for authenticated users on relevant paths
        if request.user.is_authenticated:
            path = request.path
            if path.startswith('/portal/') or path.startswith('/staff/'):
                self._update_statuses_if_needed()
        
        response = self.get_response(request)
        return response
    
    def _update_statuses_if_needed(self):
        """Run status updates at most once every 5 minutes."""
        cache_key = 'appointment_status_last_update'
        last_update = cache.get(cache_key)
        
        now = timezone.now()
        
        # Only update if 5 minutes have passed since last update
        if last_update is None or (now - last_update).total_seconds() > 300:
            try:
                from booking.models import Appointment
                Appointment.auto_update_statuses()
                cache.set(cache_key, now, timeout=600)  # Cache for 10 minutes
            except Exception:
                # Silently fail - don't break the request
                pass
