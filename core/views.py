"""
Core app views for Hills Clinic.
"""
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from .models import Doctor, SupportTeamMember


@login_required
def login_redirect_view(request):
    """Redirect users to the appropriate portal after login."""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('staff:dashboard')
    return redirect('portal:dashboard')


def robots_txt(request):
    """Serve robots.txt file."""
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Disallow admin areas",
        "Disallow: /admin/",
        "Disallow: /cms/",
        "Disallow: /portal/",
        "",
        "# Disallow API endpoints",
        "Disallow: /api/",
        "",
        "# Sitemap",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


class TeamPageView(ListView):
    """Team/Our Doctors listing page."""
    model = Doctor
    template_name = 'core/team.html'
    context_object_name = 'doctors'
    
    def get_queryset(self):
        return Doctor.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialties'] = Doctor.SPECIALTY_CHOICES
        # Group doctors by specialty for the page
        doctors = self.get_queryset()
        context['surgeons'] = doctors.filter(specialty='orthopedic-surgeon')
        context['medical_staff'] = doctors.exclude(specialty='orthopedic-surgeon')
        # Add support team members
        context['support_team'] = SupportTeamMember.objects.filter(is_active=True)
        return context


class DoctorDetailView(DetailView):
    """Individual doctor profile page."""
    model = Doctor
    template_name = 'core/doctor_detail.html'
    context_object_name = 'doctor'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Doctor.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get other doctors for "Meet the Team" section
        context['other_doctors'] = Doctor.objects.filter(
            is_active=True
        ).exclude(pk=self.object.pk)[:4]
        return context

