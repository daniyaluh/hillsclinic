"""
Import existing images from Cloudinary into Wagtail's Image model.

This command discovers image resources in the configured Cloudinary account
and creates corresponding `wagtailimages.Image` records if they do not
already exist. It avoids creating duplicates by checking the file name.

Usage: python manage.py import_cloudinary_images
"""
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Import images from Cloudinary into Wagtail images (idempotent)'

    def handle(self, *args, **options):
        if not settings.CLOUDINARY_STORAGE.get('CLOUD_NAME') and not getattr(settings, 'CLOUDINARY_STORAGE', None):
            # Fall back to env variable check used elsewhere
            import os
            if not os.getenv('CLOUDINARY_CLOUD_NAME'):
                self.stdout.write(self.style.WARNING('Cloudinary not configured. Skipping import.'))
                return

        try:
            import cloudinary.api
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'cloudinary package not available: {e}'))
            return

        # Lazy import Wagtail image model to avoid import-time errors if Wagtail not installed
        try:
            from wagtail.images import get_image_model
            Image = get_image_model()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Wagtail image model not available: {e}'))
            return

        self.stdout.write('Listing Cloudinary image resources...')

        next_cursor = None
        imported = 0
        skipped = 0
        page = 0

        while True:
            page += 1
            params = {
                'resource_type': 'image',
                'type': 'upload',
                'max_results': 500,
            }
            if next_cursor:
                params['next_cursor'] = next_cursor

            try:
                resp = cloudinary.api.resources(**params)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Cloudinary API error: {e}'))
                return

            resources = resp.get('resources', [])
            self.stdout.write(f'  Page {page}: found {len(resources)} resources')

            for r in resources:
                public_id = r.get('public_id')
                fmt = r.get('format') or 'jpg'
                file_name = f"{public_id}.{fmt}"

                # Check if file already exists in Wagtail images by exact file name
                exists = Image.objects.filter(file=file_name).exists()
                if exists:
                    skipped += 1
                    continue

                # Create a new Image record that references the existing Cloudinary asset
                try:
                    img = Image(title=public_id)
                    # Assign the file name directly; storage backend will resolve it
                    img.file.name = file_name
                    # Optional metadata
                    if 'width' in r:
                        img.width = r.get('width')
                    if 'height' in r:
                        img.height = r.get('height')
                    img.save()
                    imported += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to create image for {file_name}: {e}'))

            next_cursor = resp.get('next_cursor')
            if not next_cursor:
                break

        self.stdout.write(self.style.SUCCESS(f'Import complete: {imported} imported, {skipped} skipped'))
