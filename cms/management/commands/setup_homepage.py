"""
Django management command to set up initial Wagtail site and homepage.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from wagtail.models import Page, Site, Locale
from cms.models import HomePage


class Command(BaseCommand):
    help = 'Creates initial Wagtail homepage and site configuration'

    def handle(self, *args, **options):
        # Get the root page
        try:
            root = Page.objects.get(id=1)
            self.stdout.write(f"Found root page: {root}")
        except Page.DoesNotExist:
            self.stdout.write(self.style.ERROR("Root page not found!"))
            return

        # Get or create default locale
        locale, created = Locale.objects.get_or_create(language_code='en')
        if created:
            self.stdout.write(f"Created locale: {locale}")
        else:
            self.stdout.write(f"Using existing locale: {locale}")

        # Check if homepage already exists
        homepage = HomePage.objects.first()
        
        if homepage:
            self.stdout.write(f"Homepage already exists: {homepage.title}")
        else:
            # First, delete all sites so we can delete the welcome page
            self.stdout.write("Removing existing sites...")
            Site.objects.all().delete()
            
            # Delete existing default pages using raw SQL to avoid signal issues
            self.stdout.write("Removing default Wagtail welcome page...")
            with connection.cursor() as cursor:
                # Delete any non-root, non-HomePage pages at depth 2
                cursor.execute("""
                    DELETE FROM wagtailcore_page 
                    WHERE depth = 2 AND id NOT IN (SELECT page_ptr_id FROM cms_homepage)
                """)
            
            # Create homepage using proper Wagtail methods
            self.stdout.write("Creating new homepage...")
            
            homepage = root.add_child(
                instance=HomePage(
                    title='Hills Clinic - Limb Lengthening Surgery',
                    slug='home',
                    hero_title='Transform Your Height, Transform Your Life',
                    hero_subtitle='World-class limb lengthening surgery in Pakistan. Expert care, modern technology, life-changing results.',
                    stat_height_gain='2-6 inches',
                    stat_success_rate='98%+',
                    stat_countries='20+',
                    stat_years='40+',
                    locale=locale,
                )
            )

            # Publish the page
            homepage.save_revision().publish()

            self.stdout.write(self.style.SUCCESS(f"Created and published homepage: {homepage}"))

        # Delete all existing sites and create fresh one
        Site.objects.all().delete()
        
        # Create site - use wildcard to work for any hostname
        site = Site.objects.create(
            hostname='*',
            port=80,
            site_name='Hills Clinic',
            root_page=homepage,
            is_default_site=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Created site: {site}"))

        self.stdout.write(self.style.SUCCESS("\nSite configuration:"))
        self.stdout.write(f"  - Hostname: {site.hostname}")
        self.stdout.write(f"  - Port: {site.port}")
        self.stdout.write(f"  - Root page: {site.root_page.title}")
        self.stdout.write(self.style.SUCCESS("\nSetup complete!"))
