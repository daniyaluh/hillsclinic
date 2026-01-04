"""
Script to create initial Wagtail homepage.
"""

from wagtail.models import Page, Site, Locale
from cms.models import HomePage

# Get the root page
try:
    root = Page.objects.get(id=1)
    print(f"Found root page: {root}")
except Page.DoesNotExist:
    print("Root page not found!")
    exit(1)

# Delete existing default pages (Welcome to Wagtail, etc.)
for page in Page.objects.filter(depth=2):
    print(f"Deleting existing page: {page.title}")
    page.delete()

# Get or create default locale
locale, created = Locale.objects.get_or_create(language_code='en')
if created:
    print(f"Created locale: {locale}")
else:
    print(f"Using existing locale: {locale}")

# Check if homepage already exists
if HomePage.objects.exists():
    homepage = HomePage.objects.first()
    print(f"Homepage already exists: {homepage.title}")
else:
    # Create homepage
    homepage = HomePage(
        title='Hills Clinic - Limb Lengthening Surgery',
        slug='home',
        hero_title='Transform Your Height, Transform Your Life',
        hero_subtitle='World-class limb lengthening surgery in Pakistan. Expert care, modern technology, life-changing results.',
        stat_height_gain='2-6 inches',
        stat_success_rate='98%+',
        stat_countries='40+',
        stat_years='14+',
        locale=locale,
    )

    # Add as child of root
    root.add_child(instance=homepage)

    # Publish the page
    revision = homepage.save_revision()
    revision.publish()

    print(f"Created and published homepage: {homepage}")

# Create or update site
site, created = Site.objects.get_or_create(
    hostname='localhost',
    defaults={
        'site_name': 'Hills Clinic',
        'root_page': homepage,
        'is_default_site': True,
        'port': 8000,
    }
)

if not created:
    # Update existing site
    site.root_page = homepage
    site.is_default_site = True
    site.save()
    print(f"Updated existing site: {site}")
else:
    print(f"Created new site: {site}")

print(f"Site configuration:")
print(f"  - Hostname: {site.hostname}")
print(f"  - Port: {site.port}")
print(f"  - Root page: {site.root_page.title}")
print(f"  - Homepage URL: {homepage.get_url()}")
print(f"\nSetup complete! Visit http://127.0.0.1:8000/ to see your site.")
