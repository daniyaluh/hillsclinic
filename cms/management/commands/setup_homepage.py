"""
Django management command to set up initial Wagtail site and homepage.
"""
from django.core.management.base import BaseCommand
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

        # Delete existing default pages
        for page in Page.objects.filter(depth=2):
            self.stdout.write(f"Deleting existing page: {page.title}")
            page.delete()

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
                    stat_countries='40+',
                    stat_years='14+',
                    locale=locale,
                )
            )

            # Publish the page
            homepage.save_revision().publish()

            self.stdout.write(self.style.SUCCESS(f"Created and published homepage: {homepage}"))

        # Create or update site
        try:
            site = Site.objects.get(hostname='localhost')
            site.root_page = homepage
            site.is_default_site = True
            site.save()
            self.stdout.write(f"Updated existing site: {site}")
        except Site.DoesNotExist:
            site = Site.objects.create(
                hostname='localhost',
                port=8000,
                site_name='Hills Clinic',
                root_page=homepage,
                is_default_site=True,
            )
            self.stdout.write(self.style.SUCCESS(f"Created new site: {site}"))

        self.stdout.write(self.style.SUCCESS("\nSite configuration:"))
        self.stdout.write(f"  - Hostname: {site.hostname}")
        self.stdout.write(f"  - Port: {site.port}")
        self.stdout.write(f"  - Root page: {site.root_page.title}")
        self.stdout.write(f"  - Homepage URL: {homepage.get_url()}")
        self.stdout.write(self.style.SUCCESS("\nSetup complete! Visit http://127.0.0.1:8000/ to see your site."))
