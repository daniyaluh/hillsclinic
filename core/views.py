"""
Core app views for Hills Clinic.
"""
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from .models import Doctor, SupportTeamMember
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os


@csrf_exempt
def cloudinary_webhook(request):
    """Receive Cloudinary upload notifications and import/update the image in Wagtail.

    Cloudinary webhook must be configured to POST `public_id` and `version` and `signature`.
    This endpoint verifies the signature and then fetches the resource and upserts
    a `wagtailimages.Image` record so new uploads become available in the CMS in
    near-real-time.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        import cloudinary
        import cloudinary.api
        import cloudinary.utils
    except Exception:
        return JsonResponse({'error': 'cloudinary not available'}, status=500)

    public_id = request.POST.get('public_id') or request.POST.get('payload[public_id]')
    version = request.POST.get('version') or request.POST.get('payload[version]')
    signature = request.POST.get('signature')

    if not public_id or not version or not signature:
        return JsonResponse({'error': 'missing parameters'}, status=400)

    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    if not api_secret:
        return JsonResponse({'error': 'no api secret configured'}, status=500)

    # Verify signature: Cloudinary signs using public_id and version
    expected = cloudinary.utils.api_sign_request({'public_id': public_id, 'version': version}, api_secret)
    if signature != expected:
        return JsonResponse({'error': 'invalid signature'}, status=403)

    # Fetch resource metadata
    try:
        res = cloudinary.api.resource(public_id, resource_type='image', type='upload')
    except Exception as e:
        return JsonResponse({'error': f'cloudinary api error: {e}'}, status=500)

    # Upsert into Wagtail Image model
    try:
        from wagtail.images import get_image_model
        from django.core.files.base import ContentFile
        import requests

        Image = get_image_model()

        # Derive filename and title
        fmt = res.get('format') or 'jpg'
        basename = public_id.split('/')[-1]
        filename = f"{basename}.{fmt}"
        title = basename.replace('_', ' ').replace('-', ' ')

        # Download the original from Cloudinary
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.{fmt}"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return JsonResponse({'error': 'failed to download image'}, status=502)

        # Try to find an existing image by file or title
        exists = Image.objects.filter(file__icontains=basename).first() or Image.objects.filter(title__icontains=basename).first()
        if exists:
            # Update existing image file
            exists.file.save(filename, ContentFile(r.content), save=True)
            return JsonResponse({'status': 'updated'})

        # Create new image
        img = Image(title=title)
        img.file.save(filename, ContentFile(r.content), save=False)
        # Optional: set width/height if available from res
        if 'width' in res:
            img.width = res.get('width')
        if 'height' in res:
            img.height = res.get('height')
        img.save()
        return JsonResponse({'status': 'imported'})

    except Exception as e:
        return JsonResponse({'error': f'upsert failed: {e}'}, status=500)


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


class SupportMemberDetailView(DetailView):
    """Individual support team member profile page."""
    model = SupportTeamMember
    template_name = 'core/support_member_detail.html'
    context_object_name = 'member'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return SupportTeamMember.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get other team members
        context['other_members'] = SupportTeamMember.objects.filter(
            is_active=True
        ).exclude(pk=self.object.pk)[:4]
        # Get doctors for the team section
        context['doctors'] = Doctor.objects.filter(is_active=True)[:2]
        return context

