"""
Health check and startup validation for external services.
"""
import os
import logging
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


def validate_cloudinary():
    """Validate Cloudinary credentials if configured."""
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    
    if not cloud_name:
        logger.info("Cloudinary not configured - using local file storage")
        return True
    
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    
    if not api_key or not api_secret:
        logger.warning("Cloudinary credentials incomplete - using local file storage")
        return False
    
    try:
        import cloudinary
        import cloudinary.api
        
        # Test credentials by making a minimal API call
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        # Quick validation ping
        cloudinary.api.resources_by_tag("__health_check__", max_results=1)
        logger.info("✓ Cloudinary credentials validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Cloudinary validation failed: {e}")
        logger.warning("Media uploads will fail - check CLOUDINARY_* environment variables")
        return False


def validate_email_backend():
    """Validate email backend configuration."""
    email_backend = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
    
    if "ResendEmailBackend" in email_backend:
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            logger.error("✗ ResendEmailBackend configured but RESEND_API_KEY not set")
            return False
        logger.info("✓ Resend email backend configured")
        return True
    
    logger.info(f"Using email backend: {email_backend}")
    return True


def validate_database():
    """Validate database connection."""
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        logger.info("✓ Database connection validated")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


class Command(BaseCommand):
    help = 'Validate external service configurations'

    def handle(self, *args, **options):
        self.stdout.write("Running startup validation checks...")
        
        checks = [
            ("Database", validate_database),
            ("Email Backend", validate_email_backend),
            ("Cloudinary", validate_cloudinary),
        ]
        
        failed = []
        for name, check_func in checks:
            try:
                if not check_func():
                    failed.append(name)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠ {name} check error: {e}"))
                failed.append(name)
        
        if failed:
            self.stdout.write(self.style.WARNING(f"\n⚠ Some checks failed: {', '.join(failed)}"))
            self.stdout.write(self.style.WARNING("Application may have limited functionality"))
        else:
            self.stdout.write(self.style.SUCCESS("\n✓ All checks passed!"))
