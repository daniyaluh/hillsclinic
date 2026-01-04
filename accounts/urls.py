"""
URL configuration for accounts app.

Overrides allauth default login view with custom remember me functionality.
"""

from django.urls import path, include
from .views import LoginView

urlpatterns = [
    # Custom login view with remember me
    path('login/', LoginView.as_view(), name='account_login'),
    
    # All other allauth URLs (signup, password reset, etc.)
    path('', include('allauth.urls')),
]
