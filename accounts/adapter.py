"""
Custom allauth adapter for Hills Clinic.
Handles email sending errors gracefully so signup doesn't crash.
"""

import logging
from allauth.account.adapter import DefaultAccountAdapter

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter that handles email sending failures gracefully.
    If email fails, signup still completes - user can request new verification later.
    """
    
    def send_mail(self, template_prefix, email, context):
        """
        Override send_mail to catch and log email errors instead of crashing.
        """
        try:
            logger.info(f"Attempting to send email to {email} (template: {template_prefix})")
            super().send_mail(template_prefix, email, context)
            logger.info(f"Email sent successfully to {email}")
        except Exception as e:
            # Log the error but don't crash signup
            logger.error(f"Failed to send email to {email}: {e}", exc_info=True)
            # Don't re-raise - let signup continue without email
