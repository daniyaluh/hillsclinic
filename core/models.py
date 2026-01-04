from django.db import models
from django.urls import reverse
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel


@register_setting
class SiteSettings(BaseSiteSetting):
    """Site-wide settings for logo, favicon, and other branding."""
    
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Site logo displayed in header and footer"
    )
    favicon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Favicon (browser tab icon)"
    )
    
    panels = [
        FieldPanel('logo'),
        FieldPanel('favicon'),
    ]
    
    class Meta:
        verbose_name = "Site Settings"


class Doctor(models.Model):
    """Doctor/Medical Staff profile."""
    
    SPECIALTY_CHOICES = [
        ('orthopedic-surgeon', 'Orthopedic Surgeon'),
        ('anesthesiologist', 'Anesthesiologist'),
        ('physical-therapist', 'Physical Therapist'),
        ('nurse', 'Registered Nurse'),
        ('patient-coordinator', 'Patient Coordinator'),
        ('nutritionist', 'Nutritionist'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=100, help_text="e.g., MD, PhD, DPT")
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES)
    role = models.CharField(max_length=100, help_text="e.g., Lead Surgeon, Physical Therapy Director")
    
    # Profile
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)
    bio = models.TextField(help_text="Full biography")
    short_bio = models.CharField(max_length=300, help_text="Brief description for listings")
    
    # Credentials
    education = models.TextField(blank=True, help_text="Education and training, one per line")
    certifications = models.TextField(blank=True, help_text="Certifications and licenses, one per line")
    experience_years = models.PositiveIntegerField(default=0)
    
    # Languages
    languages = models.CharField(max_length=200, blank=True, help_text="Languages spoken, comma-separated")
    
    # Contact/Social
    email = models.EmailField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Display
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
    
    def __str__(self):
        return f"{self.name}, {self.title}"
    
    def get_absolute_url(self):
        return reverse('core:doctor-detail', kwargs={'slug': self.slug})
    
    @property
    def education_list(self):
        """Return education as a list."""
        return [e.strip() for e in self.education.split('\n') if e.strip()]
    
    @property
    def certifications_list(self):
        """Return certifications as a list."""
        return [c.strip() for c in self.certifications.split('\n') if c.strip()]
    
    @property
    def languages_list(self):
        """Return languages as a list."""
        return [l.strip() for l in self.languages.split(',') if l.strip()]
