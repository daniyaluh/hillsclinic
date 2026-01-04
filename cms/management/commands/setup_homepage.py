"""
Django management command to set up initial Wagtail site and homepage.
"""
from django.core.management.base import BaseCommand
from django.db.models.signals import post_save
from wagtail.models import Page, Site, Locale
from cms.models import HomePage


class Command(BaseCommand):
    help = 'Creates initial Wagtail homepage and site configuration'

    def handle(self, *args, **options):
        # Disconnect modelsearch signal to avoid Python 3.12 bug
        try:
            from modelsearch.signal_handlers import post_save_signal_handler
            post_save.disconnect(post_save_signal_handler)
            self.stdout.write("Disconnected modelsearch signals")
        except Exception:
            pass
        
        # Fix the page tree first (in case previous operations corrupted it)
        self.stdout.write("Fixing page tree structure...")
        Page.fix_tree()
        
        # Get the root page (refresh after fix_tree)
        try:
            root = Page.objects.get(depth=1)
            self.stdout.write(f"Found root page: {root}")
        except Page.DoesNotExist:
            self.stdout.write(self.style.ERROR("Root page not found!"))
            return

        # Get or create default locale
        locale, created = Locale.objects.get_or_create(language_code='en')
        self.stdout.write(f"Using locale: {locale}")

        # Check if homepage already exists
        homepage = HomePage.objects.first()
        
        if homepage:
            self.stdout.write(f"Homepage already exists: {homepage.title}")
        else:
            self.stdout.write("Creating new homepage...")
            
            # Delete any existing sites first (to avoid FK issues)
            Site.objects.all().delete()
            
            # Delete any non-HomePage pages at depth 2 (like Welcome page)
            # Use Wagtail's delete method, not raw SQL
            for page in Page.objects.filter(depth=2).specific():
                if not isinstance(page, HomePage):
                    self.stdout.write(f"Removing page: {page.title}")
                    page.delete()
            
            # Fix tree again after deletions
            Page.fix_tree()
            
            # Refresh root reference
            root = Page.objects.get(depth=1)
            
            # Create the homepage
            homepage = HomePage(
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
            
            # Add as child of root
            root.add_child(instance=homepage)
            
            # Publish the page
            homepage.save_revision().publish()
            
            self.stdout.write(self.style.SUCCESS(f"Created and published homepage: {homepage}"))

        # Delete all existing sites and create fresh one
        Site.objects.all().delete()
        
        # Create site
        site = Site.objects.create(
            hostname='*',
            port=80,
            site_name='Hills Clinic',
            root_page=homepage,
            is_default_site=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Created site: {site}"))

        self.stdout.write(self.style.SUCCESS("Setup complete!"))
