"""
Payment processing module for Hills Clinic.

Integrates with Stripe for:
- Consultation deposits
- Surgery deposits
- Full payments
"""
import stripe
from django.conf import settings
from django.urls import reverse
from decimal import Decimal


# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class PaymentService:
    """Service class for handling Stripe payments."""
    
    CURRENCY = 'usd'
    
    # Payment amounts (in cents for Stripe)
    CONSULTATION_FEE = 15000  # $150
    DEPOSIT_AMOUNT = 100000   # $1,000
    
    @classmethod
    def create_checkout_session(
        cls,
        payment_type: str,
        amount: int,
        patient_email: str,
        appointment_id: int,
        success_url: str,
        cancel_url: str,
        metadata: dict = None
    ):
        """
        Create a Stripe Checkout Session.
        
        Args:
            payment_type: Type of payment (consultation, deposit, full)
            amount: Amount in cents
            patient_email: Customer email
            appointment_id: Related appointment ID
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel
            metadata: Additional metadata
        
        Returns:
            Stripe Checkout Session object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        payment_descriptions = {
            'video_consultation': 'Video Consultation Fee',
            'consultation': 'Initial Consultation Deposit',
            'deposit': 'Surgery Deposit',
            'full': 'Full Payment',
        }
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': cls.CURRENCY,
                    'product_data': {
                        'name': payment_descriptions.get(payment_type, 'Payment'),
                        'description': f'Hills Clinic - {payment_descriptions.get(payment_type, "Payment")}',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            customer_email=patient_email,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'payment_type': payment_type,
                'appointment_id': appointment_id,
                **(metadata or {})
            }
        )
        
        return session
    
    @classmethod
    def create_video_consultation_payment(
        cls,
        patient_email: str,
        consultation_id: int,
        success_url: str,
        cancel_url: str,
    ):
        """Create payment session for video consultation."""
        return cls.create_checkout_session(
            payment_type='video_consultation',
            amount=cls.CONSULTATION_FEE,
            patient_email=patient_email,
            appointment_id=consultation_id,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'consultation_id': consultation_id}
        )
    
    @classmethod
    def create_deposit_payment(
        cls,
        patient_email: str,
        appointment_id: int,
        success_url: str,
        cancel_url: str,
    ):
        """Create payment session for surgery deposit."""
        return cls.create_checkout_session(
            payment_type='deposit',
            amount=cls.DEPOSIT_AMOUNT,
            patient_email=patient_email,
            appointment_id=appointment_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
    
    @classmethod
    def verify_webhook_signature(cls, payload: bytes, sig_header: str) -> dict:
        """
        Verify Stripe webhook signature.
        
        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header
        
        Returns:
            Parsed event data
        """
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        if not webhook_secret:
            raise ValueError("Stripe webhook secret not configured")
        
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        
        return event
    
    @classmethod
    def get_payment_intent(cls, payment_intent_id: str):
        """Retrieve a payment intent from Stripe."""
        return stripe.PaymentIntent.retrieve(payment_intent_id)
    
    @classmethod
    def format_amount(cls, cents: int) -> str:
        """Format cents as dollar string."""
        return f"${cents / 100:.2f}"
