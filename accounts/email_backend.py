"""
Custom email backend using Brevo (Sendinblue) HTTP API.

This bypasses SMTP port blocking on Render's free tier by using
HTTP requests instead of SMTP connections.

Brevo allows sending from their shared domain without requiring
your own verified domain - perfect for getting started.
"""

import logging
import os
import json
from urllib import request, error
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class BrevoEmailBackend(BaseEmailBackend):
    """
    Email backend that sends emails via Brevo's HTTP API.
    
    Required environment variable:
    - BREVO_API_KEY: Your Brevo API key
    
    Optional environment variable:
    - DEFAULT_FROM_EMAIL: The sender email address
    """
    
    API_URL = "https://api.brevo.com/v3/smtp/email"
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = os.getenv("BREVO_API_KEY", "")
        
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not self.api_key:
            logger.warning("BREVO_API_KEY not set - emails will not be sent")
            if not self.fail_silently:
                raise ValueError("BREVO_API_KEY environment variable is required")
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
        Send a single EmailMessage via Brevo API.
        """
        try:
            # Parse from email
            from_email = message.from_email
            from_name = "Hills Clinic"
            if '<' in from_email and '>' in from_email:
                # Format: "Name <email@domain.com>"
                parts = from_email.split('<')
                from_name = parts[0].strip().strip('"')
                from_email = parts[1].strip('>')
            
            # Build the email payload
            payload = {
                "sender": {
                    "name": from_name,
                    "email": from_email
                },
                "to": [{"email": email} for email in message.to],
                "subject": message.subject,
            }
            
            # Handle HTML vs plain text
            if hasattr(message, 'alternatives') and message.alternatives:
                # This is an EmailMultiAlternatives with HTML content
                for content, mimetype in message.alternatives:
                    if mimetype == 'text/html':
                        payload["htmlContent"] = content
                        break
                # Also include plain text version
                if message.body:
                    payload["textContent"] = message.body
            else:
                # Plain text only
                payload["textContent"] = message.body
            
            # Add CC if present
            if message.cc:
                payload["cc"] = [{"email": email} for email in message.cc]
            
            # Add BCC if present
            if message.bcc:
                payload["bcc"] = [{"email": email} for email in message.bcc]
            
            # Add reply-to if present
            if message.reply_to:
                payload["replyTo"] = {"email": message.reply_to[0]}
            
            # Make HTTP request to Brevo API
            data = json.dumps(payload).encode('utf-8')
            req = request.Request(
                self.API_URL,
                data=data,
                headers={
                    "accept": "application/json",
                    "api-key": self.api_key,
                    "content-type": "application/json",
                },
                method="POST"
            )
            
            with request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                logger.info(f"Email sent successfully to {message.to} via Brevo (messageId: {result.get('messageId', 'unknown')})")
                return True
            
        except error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logger.error(f"Brevo API HTTP error {e.code}: {error_body}")
            raise Exception(f"Brevo API error: {error_body}")
        except Exception as e:
            logger.error(f"Brevo API error: {e}")
            raise
