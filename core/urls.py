"""
URL configuration for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('login-redirect/', views.login_redirect_view, name='login-redirect'),
    path('team/', views.TeamPageView.as_view(), name='team'),
    path('team/<slug:slug>/', views.DoctorDetailView.as_view(), name='doctor-detail'),
]
