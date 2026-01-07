"""
Custom email backend using Resend HTTP API.

This bypasses SMTP port blocking on Render's free tier by using
HTTP requests instead of SMTP connections.
"""

import logging
import os
import json
from urllib import request, error
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
    
    API_URL = "https://api.resend.com/emails"
    
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
        
        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email to {message.to}: {e}")
                if not self.fail_silently:
                    raise
        
        return num_sent
    
    def _send(self, message):
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
            
            # Add CC if present
            if message.cc:
                payload["cc"] = message.cc
            
            # Add BCC if present
            if message.bcc:
                payload["bcc"] = message.bcc
            
            # Add reply-to if present
            if message.reply_to:
                payload["reply_to"] = message.reply_to[0]
            
            # Make HTTP request to Resend API
            data = json.dumps(payload).encode('utf-8')
            req = request.Request(
                self.API_URL,
                data=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST"
            )
            
            with request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                logger.info(f"Email sent successfully to {message.to} via Resend (id: {result.get('id', 'unknown')})")
                return True
            
        except error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logger.error(f"Resend API HTTP error {e.code}: {error_body}")
            raise Exception(f"Resend API error: {error_body}")
        except Exception as e:
            logger.error(f"Resend API error: {e}")
            raise
