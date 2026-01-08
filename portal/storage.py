"""
Custom Cloudinary storage backend for patient uploads.

This storage handles both images and raw files (PDFs, docs) correctly.
"""

import os
from django.conf import settings

def get_patient_upload_storage():
    """Get the appropriate storage backend."""
    if os.getenv("CLOUDINARY_CLOUD_NAME"):
        from cloudinary_storage.storage import RawMediaCloudinaryStorage
        return RawMediaCloudinaryStorage()
    else:
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage()


# Create storage class that works at import time
try:
    if os.getenv("CLOUDINARY_CLOUD_NAME"):
        from cloudinary_storage.storage import RawMediaCloudinaryStorage
        
        class PatientUploadStorage(RawMediaCloudinaryStorage):
            """
            Custom storage for patient uploads.
            Uses RawMediaCloudinaryStorage which handles all file types correctly
            including PDFs and documents.
            
            RawMediaCloudinaryStorage uploads files with resource_type='raw'
            which works for all file types including images, PDFs, and documents.
            """
            pass
    else:
        from django.core.files.storage import FileSystemStorage
        
        class PatientUploadStorage(FileSystemStorage):
            """Local storage fallback for development."""
            pass
except ImportError:
    # Fallback if cloudinary_storage is not installed
    from django.core.files.storage import FileSystemStorage
    
    class PatientUploadStorage(FileSystemStorage):
        """Local storage fallback."""
        pass
