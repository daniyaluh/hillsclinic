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
            resources = cloudinary.api.resources(max_results=500)
            
            self.stdout.write(f"Found {resources['total_count']} assets in Cloudinary\n")
            
            imported_count = 0
            
            for resource in resources.get('resources', []):
                public_id = resource['public_id']
                filename = f"{public_id}.jpg"
                title = public_id.replace('_', ' ').replace('-', ' ').title()
                
                # Check if already imported
                if Image.objects.filter(title=title).exists():
                    self.stdout.write(f"⊘ Already imported: {title}")
                    continue
                
                try:
                    # Get secure URL
                    url = cloudinary.CloudinaryResource(public_id).build_url(
                        secure=True,
                        resource_type=resource.get('type', 'image')
                    )
                    
                    # Download image
                    response = requests.get(url, timeout=10)
                    if response.status_code != 200:
                        self.stdout.write(f"✗ Failed to download: {title}")
                        continue
                    
                    # Create Image object
                    image = Image(title=title)
                    image.file.save(
                        filename,
                        ContentFile(response.content),
                        save=True
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f"✓ Imported: {title}"))
                    imported_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"✗ Error importing {title}: {e}"))
            
            self.stdout.write(self.style.SUCCESS(f"\n✓ Imported {imported_count} images successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
