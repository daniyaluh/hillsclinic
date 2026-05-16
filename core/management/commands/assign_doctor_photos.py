"""
Django management command to assign Cloudinary images to doctors.
Matches doctor names with image filenames.
"""
from django.core.management.base import BaseCommand
from core.models import Doctor
from wagtail.images.models import Image
import re


class Command(BaseCommand):
    help = 'Automatically assign Cloudinary images to doctor profiles'

    def handle(self, *args, **options):
        doctors = Doctor.objects.filter(photo__isnull=True)
        
        if not doctors.exists():
            self.stdout.write(self.style.WARNING("All doctors already have photos assigned!"))
            return
        
        # Get all available images from Wagtail
        available_images = Image.objects.all()
        
        if not available_images.exists():
            self.stdout.write(self.style.ERROR("No images found in Wagtail!"))
            return
        
        self.stdout.write(f"Found {available_images.count()} images in Wagtail")
        self.stdout.write(f"Found {doctors.count()} doctors without photos\n")
        
        assigned_count = 0
        
        for doctor in doctors:
            # Try to find matching image
            # Look for images with similar names (e.g., "khaqan", "janjua", "hassan", etc.)
            doctor_name_parts = doctor.name.lower().split()
            
            matched_image = None
            
            # Try to find image with matching name
            for image in available_images:
                image_filename = image.title.lower() if hasattr(image, 'title') else str(image).lower()
                
                # Check if any part of doctor's name is in the image filename
                for name_part in doctor_name_parts:
                    if len(name_part) > 3 and name_part in image_filename:
                        matched_image = image
                        break
                
                if matched_image:
                    break
            
            if matched_image:
                doctor.photo = matched_image
                doctor.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {doctor.name} → {matched_image.title}")
                )
                assigned_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"✗ No matching image found for {doctor.name}")
                )
        
        self.stdout.write(f"\n{self.style.SUCCESS(f'Assigned {assigned_count} images successfully!')}")
        if assigned_count < doctors.count():
            self.stdout.write(
                self.style.WARNING(
                    f"Note: {doctors.count() - assigned_count} doctors still need photos to be manually assigned"
                )
            )
