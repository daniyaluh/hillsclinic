"""
Booking app URL configuration.
"""
from django.urls import path
from . import views

app_name = "booking"

urlpatterns = [
    # Booking pages
    path('consultation/', views.ConsultationBookingView.as_view(), name='consultation'),
    path('success/', views.BookingSuccessView.as_view(), name='booking_success'),
    
    # Contact
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success/', views.ContactSuccessView.as_view(), name='contact_success'),
    
    # Video Consultation
    path('video-consultation/', views.VideoConsultationBookingView.as_view(), name='video_consultation_booking'),
    path('video-consultation/<uuid:pk>/', views.VideoConsultationDetailView.as_view(), name='video_consultation_detail'),
    path('video-consultation/<uuid:pk>/pending/', views.VideoConsultationPendingView.as_view(), name='video_consultation_pending'),
    path('video-consultation/<uuid:pk>/join/', views.VideoConsultationJoinView.as_view(), name='video_consultation_join'),
    
    # Payments
    path('payment/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/cancelled/', views.PaymentCancelledView.as_view(), name='payment_cancelled'),
    path('payment/deposit/', views.DepositPaymentView.as_view(), name='deposit_payment'),
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    
    # HTMX endpoints
    path('callback/', views.QuickCallbackView.as_view(), name='quick_callback'),
    
    # API endpoints
    path('api/slots/', views.AvailableTimeSlotsView.as_view(), name='available_slots'),
    path('api/appointment/<uuid:appointment_id>/status/', views.AppointmentStatusView.as_view(), name='appointment_status'),
    
    # Calendar file
    path('calendar/<uuid:appointment_id>.ics', views.GenerateICSView.as_view(), name='generate_ics'),
    path('appointment/<int:pk>/ics/', views.AppointmentICSView.as_view(), name='ics'),
]
