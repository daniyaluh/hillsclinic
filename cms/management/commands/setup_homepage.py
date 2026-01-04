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
        
        try:
            # Fix the page tree first (in case previous operations corrupted it)
            self.stdout.write("Fixing page tree structure...")
            Page.fix_tree()
            
            # Get the root page (refresh after fix_tree)
            try:
                root = Page.objects.get(depth=1)
                self.stdout.write(f"Found root page: {root}")
            except Page.DoesNotExist:
                self.stdout.write(self.style.ERROR("Root page not found! Creating one..."))
                # Create a root page if it doesn't exist
                root = Page.add_root(title="Root", slug="root")
                self.stdout.write(f"Created root page: {root}")

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
                for page in Page.objects.filter(depth=2).specific():
                    if not isinstance(page, HomePage):
                        self.stdout.write(f"Removing page: {page.title}")
                        page.delete()
                
                # Fix tree again after deletions
                Page.fix_tree()
                
                # Refresh root reference
                root = Page.objects.get(depth=1)
                
                # Create the homepage with all fields
                homepage = HomePage(
                    title='Hills Clinic - Limb Lengthening Surgery',
                    slug='home',
                    hero_title='Transform Your Height, Transform Your Life',
                    hero_subtitle='World-class limb lengthening surgery in Pakistan. Expert care, modern technology, life-changing results.',
                    stat_height_gain='2-6 inches',
                    stat_success_rate='98%+',
                    stat_countries='20+',
                    stat_years='40+',
                    doctor_name='Dr. Khaqan Jahangir Janjua',
                    doctor_title="Pakistan's Premier Limb Lengthening Specialist",
                    doctor_description='At Hills Clinic, our lead surgeon Dr. Khaqan Jahangir Janjua brings over 40 years of specialized experience in orthopedic and trauma surgery. With training from world-renowned institutions and hundreds of successful procedures, you are in expert hands.',
                    locale=locale,
                )
                
                # Add as child of root
                root.add_child(instance=homepage)
                
                # Publish the page
                homepage.save_revision().publish()
                
                self.stdout.write(self.style.SUCCESS(f"Created and published homepage: {homepage}"))

            # Always ensure site exists and points to homepage
            Site.objects.all().delete()
            
            # Create site with wildcard hostname
            site = Site.objects.create(
                hostname='*',
                port=80,
                site_name='Hills Clinic',
                root_page=homepage,
                is_default_site=True,
            )
            self.stdout.write(self.style.SUCCESS(f"Created site: {site}"))

            self.stdout.write(self.style.SUCCESS("Setup complete!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during setup: {str(e)}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise
