"""
CMS app models for Hills Clinic.

Wagtail page models for content management:
- HomePage
- ProcedurePage
- InternationalCenterPage
- CostPage
- RecoveryPage
- SuccessStoryPage
- BlogPage
- FAQPage
- LegalPage
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


# Custom StreamField blocks
class HeadingBlock(blocks.StructBlock):
    """Heading with customizable level."""
    heading_text = blocks.CharBlock(required=True, max_length=255)
    size = blocks.ChoiceBlock(choices=[
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4'),
    ], default='h2')
    
    class Meta:
        template = 'cms/blocks/heading_block.html'
        icon = 'title'


class ParagraphBlock(blocks.RichTextBlock):
    """Rich text paragraph."""
    class Meta:
        template = 'cms/blocks/paragraph_block.html'
        icon = 'pilcrow'


class ImageBlock(blocks.StructBlock):
    """Image with caption."""
    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=255)
    
    class Meta:
        template = 'cms/blocks/image_block.html'
        icon = 'image'


class CallToActionBlock(blocks.StructBlock):
    """Call to action button."""
    text = blocks.CharBlock(required=True, max_length=50)
    page = blocks.PageChooserBlock(required=False)
    external_url = blocks.URLBlock(required=False)
    button_style = blocks.ChoiceBlock(choices=[
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('outline', 'Outline'),
    ], default='primary')
    
    class Meta:
        template = 'cms/blocks/cta_block.html'
        icon = 'link'


class TestimonialBlock(blocks.StructBlock):
    """Patient testimonial."""
    quote = blocks.TextBlock(required=True)
    patient_name = blocks.CharBlock(required=True, max_length=100)
    location = blocks.CharBlock(required=False, max_length=100)
    procedure = blocks.CharBlock(required=False, max_length=100)
    
    class Meta:
        template = 'cms/blocks/testimonial_block.html'
        icon = 'openquote'


# Base Page class
class BasePage(Page):
    """Abstract base page with common fields."""
    
    class Meta:
        abstract = True


# Home Page
class HomePage(Page):
    """Homepage with hero, statistics, and featured sections."""
    
    hero_title = models.CharField(max_length=255, default="Transform Your Height, Transform Your Life")
    hero_subtitle = models.TextField(blank=True)
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    # Statistics
    stat_height_gain = models.CharField(max_length=50, default="2-6 inches")
    stat_success_rate = models.CharField(max_length=50, default="98%+")
    stat_countries = models.CharField(max_length=50, default="20+")
    stat_years = models.CharField(max_length=50, default="40+")
    
    # Before/After Images
    before_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Before surgery image"
    )
    after_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="After surgery image"
    )
    
    # Doctor Section
    doctor_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Main doctor photo"
    )
    doctor_name = models.CharField(max_length=255, default="Dr. Khaqan Jahangir Janjua")
    doctor_title = models.CharField(max_length=255, default="Pakistan's Premier Limb Lengthening Specialist")
    doctor_description = models.TextField(
        blank=True,
        default="At Hills Clinic, our lead surgeon Dr. Khaqan Jahangir Janjua brings over 40 years of specialized experience in orthopedic and trauma surgery. With training from world-renowned institutions and hundreds of successful procedures, you're in expert hands."
    )
    
    # Content
    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', ParagraphBlock()),
        ('image', ImageBlock()),
        ('cta', CallToActionBlock()),
        ('testimonial', TestimonialBlock()),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_title'),
            FieldPanel('hero_subtitle'),
            FieldPanel('hero_image'),
        ], heading="Hero Section"),
        MultiFieldPanel([
            FieldPanel('stat_height_gain'),
            FieldPanel('stat_success_rate'),
            FieldPanel('stat_countries'),
            FieldPanel('stat_years'),
        ], heading="Statistics"),
        MultiFieldPanel([
            FieldPanel('before_image'),
            FieldPanel('after_image'),
        ], heading="Before & After Images"),
        MultiFieldPanel([
            FieldPanel('doctor_image'),
            FieldPanel('doctor_name'),
            FieldPanel('doctor_title'),
            FieldPanel('doctor_description'),
        ], heading="Doctor Section"),
        FieldPanel('body'),
    ]
    
    max_count = 1
    parent_page_types = []
    
    def get_context(self, request):
        context = super().get_context(request)
        # Add patient reviews for testimonials section
        context['testimonials'] = PatientReview.objects.filter(is_published=True)[:6]
        context['featured_testimonial'] = PatientReview.objects.filter(is_published=True, is_featured=True).first()
        return context
    
    class Meta:
        verbose_name = "Home Page"


# Procedure Page
class ProcedurePage(Page):
    """Procedure information page."""
    
    introduction = RichTextField(blank=True)
    procedure_type = models.CharField(
        max_length=50,
        choices=[
            ('ilizarov', 'Ilizarov (External)'),
            ('internal', 'Internal Nails'),
            ('lon', 'LON Method'),
        ],
        blank=True
    )
    
    # Outcomes
    height_gain_femur = models.CharField(max_length=50, default="2-3 inches", blank=True)
    height_gain_tibia = models.CharField(max_length=50, default="2-2.5 inches", blank=True)
    height_gain_combined = models.CharField(max_length=50, default="4-6 inches", blank=True)
    
    # Safety
    complication_rate = models.CharField(max_length=50, default="<5% minor", blank=True)
    
    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', ParagraphBlock()),
        ('image', ImageBlock()),
        ('cta', CallToActionBlock()),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('procedure_type'),
        MultiFieldPanel([
            FieldPanel('height_gain_femur'),
            FieldPanel('height_gain_tibia'),
            FieldPanel('height_gain_combined'),
        ], heading="Outcomes"),
        FieldPanel('complication_rate'),
        FieldPanel('body'),
    ]
    
    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.FilterField('procedure_type'),
    ]
    
    parent_page_types = ['cms.HomePage']
    
    class Meta:
        verbose_name = "Procedure Page"


# International Patient Center Page
class InternationalCenterPage(Page):
    """Information for international patients."""
    
    introduction = RichTextField(blank=True)
    
    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', ParagraphBlock()),
        ('image', ImageBlock()),
        ('cta', CallToActionBlock()),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('body'),
    ]
    
    parent_page_types = ['cms.HomePage']
    max_count = 1
    
    class Meta:
        verbose_name = "International Patient Center Page"


# Cost & Financing Page
class CostPage(Page):
    """Cost and financing information."""
    
    introduction = RichTextField(blank=True)
    
    # Price ranges (in USD)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, default=3000)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, default=6000)
    currency = models.CharField(max_length=3, default="USD")
    
    # Discounts
    full_payment_discount = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount percentage for full upfront payment"
    )
    
    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', ParagraphBlock()),
        ('image', ImageBlock()),
        ('cta', CallToActionBlock()),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        MultiFieldPanel([
            FieldPanel('min_price'),
            FieldPanel('max_price'),
            FieldPanel('currency'),
            FieldPanel('full_payment_discount'),
        ], heading="Pricing"),
        FieldPanel('body'),
    ]
    
    parent_page_types = ['cms.HomePage']
    max_count = 1
    
    class Meta:
        verbose_name = "Cost & Financing Page"


# Recovery & Rehabilitation Page
class RecoveryPage(Page):
    """Recovery timeline and rehabilitation information."""
    
    introduction = RichTextField(blank=True)
    
    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', ParagraphBlock()),
        ('image', ImageBlock()),
        ('cta', CallToActionBlock()),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('body'),
    ]
    
    parent_page_types = ['cms.HomePage']
    max_count = 1
    
    class Meta:
        verbose_name = "Recovery & Rehabilitation Page"


# Success Story Page
class SuccessStoryPage(Page):
    """Individual patient success story."""
    
    patient_initials = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(100)]
    )
    procedure_method = models.CharField(
        max_length=50,
        choices=[
            ('ilizarov', 'Ilizarov'),
            ('internal', 'Internal Nails'),
            ('lon', 'LON Method'),
        ],
        blank=True
    )
    height_gained = models.CharField(max_length=50, blank=True, help_text="e.g., '5 inches'")
    
    # Consent fields
    consent_media_use = models.BooleanField(default=False)
    consent_face_visible = models.BooleanField(default=False)
    consent_testimonial_published = models.BooleanField(default=False)
    consent_revocation_date = models.DateTimeField(null=True, blank=True)
    
    # Images
    before_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Before photo"
    )
    after_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="After photo"
    )
    
    story = RichTextField(blank=True)
    testimonial_quote = models.TextField(blank=True)
    
    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', ParagraphBlock()),
        ('image', ImageBlock()),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('patient_initials'),
            FieldPanel('location'),
            FieldPanel('age'),
            FieldPanel('procedure_method'),
            FieldPanel('height_gained'),
        ], heading="Patient Info"),
        MultiFieldPanel([
            FieldPanel('consent_media_use'),
            FieldPanel('consent_face_visible'),
            FieldPanel('consent_testimonial_published'),
            FieldPanel('consent_revocation_date'),
        ], heading="Consent & Privacy"),
        MultiFieldPanel([
            FieldPanel('before_image'),
            FieldPanel('after_image'),
        ], heading="Photos"),
        FieldPanel('story'),
        FieldPanel('testimonial_quote'),
        FieldPanel('body'),
    ]
    
    search_fields = Page.search_fields + [
        index.SearchField('story'),
        index.SearchField('testimonial_quote'),
        index.FilterField('procedure_method'),
        index.FilterField('location'),
    ]
    
    parent_page_types = ['cms.SuccessStoriesIndexPage']
    
    class Meta:
        verbose_name = "Success Story"


# Success Stories Index Page
class SuccessStoriesIndexPage(Page):
    """Index page for success stories."""
    
    introduction = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]
    
    parent_page_types = ['cms.HomePage']
    subpage_types = ['cms.SuccessStoryPage']
    max_count = 1
    
    def get_context(self, request):
        context = super().get_context(request)
        # Only show stories with valid consent
        context['stories'] = SuccessStoryPage.objects.live().filter(
            consent_testimonial_published=True,
            consent_revocation_date__isnull=True
        ).order_by('-first_published_at')
        # Add patient reviews (CMS-managed testimonials)
        context['reviews'] = PatientReview.objects.filter(is_published=True)
        context['featured_reviews'] = PatientReview.objects.filter(is_published=True, is_featured=True)
        return context
    
    class Meta:
        verbose_name = "Success Stories Index"


# Blog/Article Page
class BlogPage(Page):
    """Blog article or educational content."""
    
    CATEGORY_CHOICES = [
        ('nutrition', 'Nutrition'),
        ('recovery', 'Recovery'),
        ('procedures', 'Procedures'),
        ('patient-care', 'Patient Care'),
        ('research', 'Research'),
        ('news', 'News'),
        ('general', 'General'),
    ]
    
    author = models.CharField(max_length=255, blank=True)
    date = models.DateField("Post date")
    introduction = RichTextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', ParagraphBlock()),
        ('image', ImageBlock()),
        ('cta', CallToActionBlock()),
    ], use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('author'),
        FieldPanel('date'),
        FieldPanel('category'),
        FieldPanel('featured_image'),
        FieldPanel('introduction'),
        FieldPanel('body'),
    ]
    
    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
        index.FilterField('category'),
        index.FilterField('date'),
    ]
    
    parent_page_types = ['cms.BlogIndexPage']
    
    @property
    def read_time(self):
        """Estimate reading time based on content length."""
        # Count words in introduction and body
        word_count = 0
        if self.introduction:
            word_count += len(self.introduction.split())
        
        # Count words in StreamField body
        for block in self.body:
            if hasattr(block.value, 'source'):  # RichText
                word_count += len(str(block.value.source).split())
            elif hasattr(block.value, 'get'):  # StructBlock
                text = block.value.get('heading_text', '') or block.value.get('text', '') or ''
                word_count += len(str(text).split())
        
        # Average reading speed: 200 words per minute
        minutes = max(1, round(word_count / 200))
        return minutes
    
    class Meta:
        verbose_name = "Blog Article"
        ordering = ['-date']


# Blog Index Page
class BlogIndexPage(Page):
    """Index page for blog articles."""
    
    introduction = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]
    
    parent_page_types = ['cms.HomePage']
    subpage_types = ['cms.BlogPage']
    max_count = 1
    
    def get_context(self, request):
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        
        context = super().get_context(request)
        articles = BlogPage.objects.live().order_by('-date')
        
        # Category filtering
        category = request.GET.get('category')
        if category and category != 'all':
            articles = articles.filter(category=category)
        
        # Search filtering
        search_query = request.GET.get('q')
        if search_query:
            articles = articles.search(search_query)
        
        # Pagination
        paginator = Paginator(articles, 9)  # 9 articles per page
        page_num = request.GET.get('page')
        try:
            articles = paginator.page(page_num)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)
        
        context['articles'] = articles
        context['category'] = category
        context['search_query'] = search_query
        context['categories'] = BlogPage.CATEGORY_CHOICES
        return context
    
    class Meta:
        verbose_name = "Blog Index"


# FAQ Snippet
@register_snippet
class FAQItem(models.Model):
    """Individual FAQ item."""
    
    question = models.CharField(max_length=500)
    answer = RichTextField()
    category = models.CharField(
        max_length=50,
        choices=[
            ('general', 'General'),
            ('international', 'International'),
            ('recovery', 'Recovery'),
            ('cost', 'Cost & Financing'),
        ],
        default='general'
    )
    order = models.IntegerField(default=0)
    
    panels = [
        FieldPanel('question'),
        FieldPanel('answer'),
        FieldPanel('category'),
        FieldPanel('order'),
    ]
    
    def __str__(self):
        return self.question
    
    class Meta:
        ordering = ['category', 'order', 'question']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"


# Patient Review Snippet
@register_snippet
class PatientReview(models.Model):
    """Patient review/testimonial for success stories page."""
    
    PROCEDURE_CHOICES = [
        ('ilizarov', 'Ilizarov Method'),
        ('internal', 'Internal Nail (PRECICE)'),
        ('lon', 'LON Method'),
    ]
    
    # Patient info (privacy-focused - no photos)
    patient_initials = models.CharField(
        max_length=10, 
        help_text="Patient initials for privacy (e.g., 'J.S.')"
    )
    country = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Patient's country (e.g., 'United States', 'UAE')"
    )
    age = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(100)],
        help_text="Patient's age at time of surgery"
    )
    
    # Procedure details
    procedure_type = models.CharField(
        max_length=50,
        choices=PROCEDURE_CHOICES,
        default='ilizarov'
    )
    height_gained = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Height gained (e.g., '+3 inches', '+8cm')"
    )
    surgery_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Year of surgery"
    )
    
    # Review content
    review_text = models.TextField(
        help_text="The patient's review/testimonial text"
    )
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating out of 5 stars"
    )
    
    # Display settings
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this review prominently"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Show this review on the website"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    panels = [
        MultiFieldPanel([
            FieldPanel('patient_initials'),
            FieldPanel('country'),
            FieldPanel('age'),
        ], heading="Patient Information"),
        MultiFieldPanel([
            FieldPanel('procedure_type'),
            FieldPanel('height_gained'),
            FieldPanel('surgery_year'),
        ], heading="Procedure Details"),
        MultiFieldPanel([
            FieldPanel('review_text'),
            FieldPanel('rating'),
        ], heading="Review"),
        MultiFieldPanel([
            FieldPanel('is_featured'),
            FieldPanel('is_published'),
            FieldPanel('display_order'),
        ], heading="Display Settings"),
    ]
    
    def __str__(self):
        return f"{self.patient_initials} - {self.get_procedure_type_display()} ({self.country})"
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Patient Review"
        verbose_name_plural = "Patient Reviews"


# FAQ Page
class FAQPage(Page):
    """FAQ page with categorized questions."""
    
    introduction = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]
    
    parent_page_types = ['cms.HomePage']
    max_count = 1
    
    def get_context(self, request):
        context = super().get_context(request)
        context['faqs'] = FAQItem.objects.all()
        return context
    
    class Meta:
        verbose_name = "FAQ Page"


# Legal/Compliance Page
class LegalPage(Page):
    """Legal, compliance, and policy pages."""
    
    page_type = models.CharField(
        max_length=50,
        choices=[
            ('patient-rights', 'Patient Rights Charter'),
            ('privacy', 'Privacy Policy'),
            ('dispute', 'Dispute Resolution'),
            ('licensing', 'Licensing & Certifications'),
        ],
        blank=True
    )
    
    content = RichTextField(blank=True)
    last_updated = models.DateField(editable=False, auto_now=True)
    
    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', ParagraphBlock()),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('page_type'),
        FieldPanel('content'),
        FieldPanel('body'),
    ]
    
    parent_page_types = ['cms.HomePage']
    
    class Meta:
        verbose_name = "Legal/Compliance Page"
