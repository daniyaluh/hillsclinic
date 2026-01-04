"""
Custom allauth adapter for Hills Clinic.
Handles email sending errors gracefully.
"""

import logging
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter that handles email sending failures gracefully.
    """
    
    def send_mail(self, template_prefix, email, context):
        """
        Override send_mail to catch and log email errors instead of crashing.
        """
        try:
            super().send_mail(template_prefix, email, context)
            logger.info(f"Email sent successfully to {email} (template: {template_prefix})")
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}", exc_info=True)
            # Don't raise the exception - let signup continue
            # The user can request a new verification email later
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Override to handle confirmation email errors gracefully.
        """
        try:
            super().send_confirmation_mail(request, emailconfirmation, signup)
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {e}", exc_info=True)
            # Add a message so user knows email might not have been sent
            if request:
                messages.warning(
                    request, 
                    "We couldn't send the verification email. Please try again later or contact support."
                )
