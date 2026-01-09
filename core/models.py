from django.db import models
from django.urls import reverse
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet


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


@register_snippet
class Doctor(models.Model):
    """Doctor/Medical Staff profile - managed via CMS."""
    
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
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Doctor's profile photo"
    )
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
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower = first)")
    
    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('slug'),
            FieldPanel('title'),
            FieldPanel('specialty'),
            FieldPanel('role'),
        ], heading="Basic Information"),
        MultiFieldPanel([
            FieldPanel('photo'),
            FieldPanel('short_bio'),
            FieldPanel('bio'),
        ], heading="Profile"),
        MultiFieldPanel([
            FieldPanel('education'),
            FieldPanel('certifications'),
            FieldPanel('experience_years'),
            FieldPanel('languages'),
        ], heading="Credentials"),
        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('linkedin_url'),
        ], heading="Contact"),
        MultiFieldPanel([
            FieldPanel('is_featured'),
            FieldPanel('is_active'),
            FieldPanel('order'),
        ], heading="Display Settings"),
    ]
    
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


@register_snippet
class SupportTeamMember(models.Model):
    """Support team member profile - managed via CMS."""
    
    ROLE_CHOICES = [
        ('patient-coordinator', 'Patient Coordinator'),
        ('nurse', 'Registered Nurse'),
        ('physical-therapist', 'Physical Therapist'),
        ('nutritionist', 'Nutritionist'),
        ('admin', 'Administrative Staff'),
        ('translator', 'Translator/Interpreter'),
        ('driver', 'Patient Transport'),
        ('accommodation', 'Accommodation Coordinator'),
        ('other', 'Other'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    job_title = models.CharField(max_length=100, help_text="Specific job title")
    
    # Profile
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Team member's photo"
    )
    description = models.TextField(help_text="Brief description of their role and responsibilities")
    
    # Languages (important for international patients)
    languages = models.CharField(max_length=200, blank=True, help_text="Languages spoken, comma-separated")
    
    # Contact
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True, help_text="WhatsApp number if different")
    
    # Display
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower = first)")
    
    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('role'),
            FieldPanel('job_title'),
        ], heading="Basic Information"),
        MultiFieldPanel([
            FieldPanel('photo'),
            FieldPanel('description'),
            FieldPanel('languages'),
        ], heading="Profile"),
        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('phone'),
            FieldPanel('whatsapp'),
        ], heading="Contact"),
        MultiFieldPanel([
            FieldPanel('is_active'),
            FieldPanel('order'),
        ], heading="Display Settings"),
    ]
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Support Team Member"
        verbose_name_plural = "Support Team Members"
    
    def __str__(self):
        return f"{self.name} - {self.job_title}"
    
    @property
    def languages_list(self):
        """Return languages as a list."""
        return [l.strip() for l in self.languages.split(',') if l.strip()]
