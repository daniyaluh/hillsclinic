"""
Custom email backend using Resend HTTP API.

This bypasses SMTP port blocking on Render's free tier by using
HTTP requests instead of SMTP connections.
"""

import logging
import os
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """
    Email backend that sends emails via Resend's HTTP API.
    
    Required environment variable:
    - RESEND_API_KEY: Your Resend API key
    
    Optional environment variable:
    - DEFAULT_FROM_EMAIL: The sender email address
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = os.getenv("RESEND_API_KEY", "")
        
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not self.api_key:
            logger.warning("RESEND_API_KEY not set - emails will not be sent")
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY environment variable is required")
            return 0
        
        try:
            import resend
            resend.api_key = self.api_key
        except ImportError:
            logger.error("resend package not installed")
            if not self.fail_silently:
                raise
            return 0
        
        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(resend, message)
                if sent:
                    num_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email to {message.to}: {e}")
                if not self.fail_silently:
                    raise
        
        return num_sent
    
    def _send(self, resend, message):
        """
        Send a single EmailMessage via Resend API.
        """
        try:
            # Build the email payload
            payload = {
                "from": message.from_email,
                "to": message.to,
                "subject": message.subject,
            }
            
            # Handle HTML vs plain text
            if hasattr(message, 'alternatives') and message.alternatives:
                # This is an EmailMultiAlternatives with HTML content
                for content, mimetype in message.alternatives:
                    if mimetype == 'text/html':
                        payload["html"] = content
                        break
                # Also include plain text version
                if message.body:
                    payload["text"] = message.body
            else:
                # Plain text only
                payload["text"] = message.body
            
            # Add CC and BCC if present
            if message.cc:
                payload["cc"] = message.cc
            if message.bcc:
                payload["bcc"] = message.bcc
            
            # Add reply-to if present
            if message.reply_to:
                payload["reply_to"] = message.reply_to[0] if len(message.reply_to) == 1 else message.reply_to
            
            # Send via Resend API
            result = resend.Emails.send(payload)
            
            logger.info(f"Email sent successfully to {message.to} via Resend (id: {result.get('id', 'unknown')})")
            return True
            
        except Exception as e:
            logger.error(f"Resend API error: {e}")
            raise
