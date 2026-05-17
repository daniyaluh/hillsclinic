"""
Import Cloudinary assets into Wagtail Image model.
Only imports original assets, skips renditions and transformations.
"""
from django.core.management.base import BaseCommand
from wagtail.images.models import Image
import cloudinary
import cloudinary.api
import os
from io import BytesIO
from django.core.files.base import ContentFile
import requests
from PIL import Image as PILImage
import re
from pathlib import PurePosixPath


class Command(BaseCommand):
    help = 'Import only original Cloudinary assets into Wagtail Image model (skip renditions)'

    def _is_original_asset(self, resource):
        """Check if this is an original asset, not a rendition/transformation."""
        public_id = resource.get('public_id', '').lower()
        
        # Skip if marked as derived by Cloudinary
        if resource.get('derived'):
            return False
        
        # Skip common rendition patterns
        rendition_markers = [".fill-", ".width-", ".max-", ".crop-", ".scale-", ".format-"]
        if any(marker in public_id for marker in rendition_markers):
            return False
        
        # Skip if path contains rendition indicators
        if 'rendition' in public_id or 'derivative' in public_id:
            return False
        
        return True

    def _build_title(self, public_id):
        """Extract clean, readable title from public_id."""
        # Get just the filename from path
        filename = PurePosixPath(public_id).name
        
        # Replace underscores/hyphens with spaces
        title = re.sub(r'[_\-]+', ' ', filename)
        
        # Remove file extensions
        title = re.sub(r'\.[a-z]+$', '', title, flags=re.IGNORECASE)
        
        # Remove non-alphanumeric except spaces
        title = re.sub(r'[^a-z0-9\s]', '', title, flags=re.IGNORECASE)
        
        # Normalize whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Fallback if empty
        if not title or len(title) < 2:
            title = "Image"
        
        return title[:100]

    def handle(self, *args, **options):
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        if not cloud_name:
            self.stdout.write(self.style.ERROR("CLOUDINARY_CLOUD_NAME not set"))
            return
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        )
        
        try:
            # Get all resources from Cloudinary
            resources_response = cloudinary.api.resources(max_results=500, type='upload')
            
            if not resources_response:
                self.stdout.write(self.style.WARNING("No response from Cloudinary API"))
                return
            
            total_count = resources_response.get('total_count', 0)
            resources = resources_response.get('resources', [])
            
            self.stdout.write(f"Found {total_count} assets in Cloudinary\n")
            
            if not resources:
                self.stdout.write(self.style.WARNING("No resources to import"))
                return
            
            imported_count = 0
            skipped_count = 0
            
            for resource in resources:
                public_id = resource.get('public_id', '')
                if not public_id:
                    continue
                
                # Skip renditions/transformations
                if not self._is_original_asset(resource):
                    self.stdout.write(f"[SKIP] Rendition: {public_id}")
                    skipped_count += 1
                    continue
                
                title = self._build_title(public_id)

                # Stronger duplicate detection: check existing images by file or title
                from pathlib import PurePosixPath
                base_name = PurePosixPath(public_id).name
                # normalize a compact key from base name to match different variants
                base_key = re.sub(r'[^a-z0-9]', '', base_name.lower())

                if Image.objects.filter(file__icontains=base_key).exists() or Image.objects.filter(title__icontains=base_key).exists():
                    self.stdout.write(f"[DUP] Duplicate or variant exists, skipping: {public_id}")
                    skipped_count += 1
                    continue
                
                try:
                    # Build direct Cloudinary URL
                    url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                    
                    # Download image
                    response = requests.get(url, timeout=10)
                    if response.status_code != 200:
                        self.stdout.write(f"[ERROR] Failed to download: {public_id} ({response.status_code})")
                        continue
                    
                    # Get image dimensions
                    try:
                        img_io = BytesIO(response.content)
                        pil_img = PILImage.open(img_io)
                        width, height = pil_img.size
                        img_format = pil_img.format.lower() if pil_img.format else 'jpg'
                        filename = f"{public_id.split('/')[-1]}.{img_format}"
                    except Exception as e:
                        width, height = 1, 1
                        filename = f"{public_id.split('/')[-1]}.jpg"
                        self.stdout.write(self.style.WARNING(f"[WARN] Could not read image dimensions: {e}"))
                    
                    # Create Wagtail Image
                    image = Image(title=title)
                    image.file.save(
                        filename,
                        ContentFile(response.content),
                        save=False
                    )
                    image.width = width
                    image.height = height
                    image.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"[IMPORTED] {title} ({width}x{height})"))
                    imported_count += 1
                
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"[ERROR] Failed to import {title}: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(f"\n[COMPLETE] Imported {imported_count} images, Skipped {skipped_count} renditions"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
