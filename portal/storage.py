"""
Custom storage for patient uploads.

Uses RawMediaCloudinaryStorage which accepts ALL file types (images, PDFs, docs).
The default MediaCloudinaryStorage only works for images.
"""

import os

# Determine which storage to use based on environment
if os.getenv("CLOUDINARY_CLOUD_NAME"):
    from cloudinary_storage.storage import RawMediaCloudinaryStorage
    
    class PatientUploadStorage(RawMediaCloudinaryStorage):
        """
        Storage for patient uploads.
        Uses 'raw' resource type which works for all file formats.
        """
        pass
else:
    from django.core.files.storage import FileSystemStorage
    
    class PatientUploadStorage(FileSystemStorage):
        """Local file storage for development."""
        pass
