import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = "Set the Django Sites domain and name for link generation (allauth)."

    def add_arguments(self, parser):
        parser.add_argument("--domain", help="Domain like '127.0.0.1:8000' or 'example.com'", default=None)
        parser.add_argument("--name", help="Site display name", default="Hills Clinic")

    def handle(self, *args, **options):
        domain = options["domain"] or os.getenv("SITE_DOMAIN", "127.0.0.1:8000")
        name = options["name"]

        site = Site.objects.get(pk=1)
        site.domain = domain
        site.name = name
        site.save()

        self.stdout.write(self.style.SUCCESS(f"Site updated: domain='{domain}', name='{name}'"))
