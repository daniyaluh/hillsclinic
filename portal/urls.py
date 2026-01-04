"""
Portal app URL configuration.
"""
from django.urls import path
from . import views

app_name = "portal"

urlpatterns = [
    # Dashboard
    path("", views.DashboardView.as_view(), name="dashboard"),
    
    # Documents
    path("documents/", views.DocumentListView.as_view(), name="documents"),
    path("documents/upload/", views.DocumentUploadView.as_view(), name="document-upload"),
    path("documents/<int:pk>/delete/", views.DocumentDeleteView.as_view(), name="document-delete"),
    
    # Consents
    path("consents/", views.ConsentListView.as_view(), name="consents"),
    path("consents/<str:consent_type>/grant/", views.ConsentGrantView.as_view(), name="consent-grant"),
    path("consents/<int:pk>/revoke/", views.ConsentRevokeView.as_view(), name="consent-revoke"),
    
    # Profile
    path("profile/", views.ProfileView.as_view(), name="profile"),
    
    # Appointments
    path("appointments/", views.AppointmentListView.as_view(), name="appointments"),
    path("appointments/<int:pk>/", views.AppointmentDetailView.as_view(), name="appointment-detail"),
    path("appointments/calendar/", views.PatientCalendarView.as_view(), name="calendar"),
    path("appointments/book/", views.AppointmentBookView.as_view(), name="appointment-book"),
    
    # Payments
    path("appointments/<int:pk>/payment/", views.AppointmentPaymentView.as_view(), name="appointment-payment"),
    path("appointments/<int:pk>/payment/stripe/", views.StripePaymentView.as_view(), name="stripe-payment"),
    path("appointments/<int:pk>/payment/stripe/success/", views.StripeSuccessView.as_view(), name="stripe-success"),
    path("appointments/<int:pk>/payment/stripe/cancel/", views.StripeCancelView.as_view(), name="stripe-cancel"),
    
    # Notifications
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
    path("notifications/<int:pk>/read/", views.notification_mark_read, name="notification-read"),
    path("notifications/mark-all-read/", views.notification_mark_all_read, name="notifications-mark-all-read"),
    path("api/notifications/", views.notifications_dropdown, name="api-notifications"),
    
    # API
    path("api/time-slots/", views.AvailableTimeSlotsAPI.as_view(), name="api-time-slots"),
]
