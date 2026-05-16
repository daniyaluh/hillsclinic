"""
Import Cloudinary assets into Wagtail Image model.
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


class Command(BaseCommand):
    help = 'Import Cloudinary assets into Wagtail Image model'

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
            
            for resource in resources:
                public_id = resource.get('public_id', '')
                if not public_id:
                    continue
                    
                filename = f"{public_id}.jpg"
                title = public_id.replace('_', ' ').replace('-', ' ').title()
                
                # Check if already imported
                if Image.objects.filter(title=title).exists():
                    self.stdout.write(f"⊘ Already imported: {title}")
                    continue
                
                try:
                    # Build direct Cloudinary URL
                    url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                    
                    # Download image
                    response = requests.get(url, timeout=10)
                    if response.status_code != 200:
                        self.stdout.write(f"✗ Failed to download {url}: {response.status_code}")
                        continue

                    # Determine image size using Pillow
                    try:
                        img_io = BytesIO(response.content)
                        pil_img = PILImage.open(img_io)
                        width, height = pil_img.size
                        img_format = pil_img.format.lower() if pil_img.format else 'jpg'
                        filename = f"{public_id}.{img_format}"
                    except Exception as e:
                        width = None
                        height = None
                        self.stdout.write(self.style.WARNING(f"⚠ Could not determine size for {title}: {e}"))

                    # Create Image object and set dimensions
                    image = Image(title=title)
                    # Save file without committing, so we can set width/height
                    image.file.save(
                        filename,
                        ContentFile(response.content),
                        save=False
                    )

                    # For Wagtail, width and height are required fields
                    if width:
                        image.width = width
                    else:
                        image.width = 1
                    if height:
                        image.height = height
                    else:
                        image.height = 1

                    image.save()
                    self.stdout.write(self.style.SUCCESS(f"✓ Imported: {title} (w={image.width}, h={image.height})"))
                    imported_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"✗ Error importing {title}: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(f"\n✓ Imported {imported_count}/{len(resources)} images successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
