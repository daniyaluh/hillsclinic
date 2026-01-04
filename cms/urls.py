"""
CMS app URL configuration for static pages.
"""
from django.urls import path
from . import views

app_name = "cms"

urlpatterns = [
    # Procedures
    path("procedures/", views.ProceduresOverviewView.as_view(), name="procedures"),
    path("procedures/<str:procedure_type>/", views.ProcedureDetailView.as_view(), name="procedure-detail"),
    
    # Information Pages
    path("international/", views.InternationalPatientsView.as_view(), name="international"),
    path("cost/", views.CostFinancingView.as_view(), name="cost"),
    path("recovery/", views.RecoveryView.as_view(), name="recovery"),
    path("success-stories/", views.SuccessStoriesView.as_view(), name="success-stories"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    
    # Legal Pages
    path("privacy/", views.LegalPageView.as_view(), {'page_type': 'privacy'}, name="privacy"),
    path("terms/", views.LegalPageView.as_view(), {'page_type': 'terms'}, name="terms"),
    path("cookies/", views.LegalPageView.as_view(), {'page_type': 'cookies'}, name="cookies"),
]
