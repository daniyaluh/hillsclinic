from django.core.management.base import BaseCommand
from wagtail.images.models import Image


class Command(BaseCommand):
    help = "Delete all Image records from Wagtail Image model"

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually delete the records (default is dry-run)',
        )

    def handle(self, *args, **options):
        images = Image.objects.all()
        count = images.count()

        if options['apply']:
            images.delete()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Deleted {count} Image records from database')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] Would delete {count} Image records')
            )
            self.stdout.write('Run with --apply to actually delete')
