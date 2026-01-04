"""
URL configuration for Staff Portal.
"""

from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:patient_id>/update-name/', views.patient_update_name, name='patient_update_name'),
    path('patients/<int:patient_id>/consents/', views.patient_consents, name='patient_consents'),
    
    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    
    # Video Consultations
    path('consultations/', views.video_consultation_list, name='consultation_list'),
    
    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:document_id>/', views.document_detail, name='document_detail'),
    path('documents/<int:document_id>/verify/', views.verify_document, name='verify_document'),
    path('patients/<int:patient_id>/documents/', views.patient_documents, name='patient_documents'),
    
    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    
    # Consents
    path('consents/', views.consent_list, name='consent_list'),
    path('consents/<int:consent_id>/', views.consent_detail, name='consent_detail'),
    
    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),
    
    # Time Slots
    path('time-slots/', views.time_slot_management, name='time_slots'),
]
