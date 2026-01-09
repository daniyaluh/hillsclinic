from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import FormView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import pytz
import logging

logger = logging.getLogger(__name__)
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import uuid

from .models import Patient, Appointment, TimeSlot, VideoConsultation, Payment
from .forms import ConsultationBookingForm, ContactForm, QuickCallbackForm, VideoConsultationForm
from .payments import PaymentService
from .video_conference import VideoConferenceService


class ConsultationBookingView(LoginRequiredMixin, FormView):
    """Handle consultation booking requests. Requires login first."""
    template_name = 'booking/consultation.html'
    form_class = ConsultationBookingForm
    success_url = reverse_lazy('booking:booking_success')
    login_url = 'account_login'
    redirect_field_name = 'next'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Book Free Consultation'
        return context
    
    def get_initial(self):
        """Pre-fill form with logged-in user data."""
        initial = super().get_initial()
        user = self.request.user
        
        if user.is_authenticated:
            initial['email'] = user.email
            initial['full_name'] = user.get_full_name() or ''
            
            # Get patient data if exists
            try:
                patient = Patient.objects.get(user=user)
                initial['phone'] = patient.phone_number or ''
                initial['country'] = patient.country or ''
                initial['patient_timezone'] = patient.timezone or 'UTC'
            except Patient.DoesNotExist:
                pass
        
        return initial
    
    def form_valid(self, form):
        data = form.cleaned_data
        
        # Use logged-in user
        user = self.request.user
        
        # Parse the full name
        full_name = data.get('full_name', '').strip()
        name_parts = full_name.split() if full_name else []
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        # Update user's name if provided
        if full_name and not user.get_full_name():
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        
        # Create or update patient record
        patient, created = Patient.objects.get_or_create(
            user=user,
            defaults={
                'full_name': full_name,
                'phone_number': data.get('phone', ''),
                'country': data.get('country', ''),
                'timezone': data.get('patient_timezone', 'UTC'),
                'medical_conditions': data.get('medical_conditions', ''),
            }
        )
        
        if not created:
            # Update existing patient info
            if full_name and not patient.full_name:
                patient.full_name = full_name
            if data.get('phone'):
                patient.phone_number = data['phone']
            if data.get('country'):
                patient.country = data['country']
            patient.save()
        
        # Create appointment with payment deadline (patient pays immediately)
        from django.utils import timezone as tz
        appointment = Appointment.objects.create(
            patient=patient,
            appointment_type=data.get('appointment_type', 'consultation'),
            status='pending',
            consultation_method=data.get('consultation_type', 'video'),
            payment_deadline=tz.now() + tz.timedelta(hours=48),  # 48 hours to pay
            patient_notes=f"""
Consultation Request:
- Appointment Type: {data.get('appointment_type', 'consultation')}
- Consultation Method: {data['consultation_type']}
- Current Height: {data.get('current_height', 'Not provided')}
- Desired Height Gain: {data['desired_height_gain']}
- Procedure Interest: {data['procedure_interest']}
- Questions: {data.get('questions', 'None')}
- Referral Source: {data.get('referral_source', 'Not specified')}
- Marketing Consent: {'Yes' if data.get('marketing_consent') else 'No'}
            """.strip()
        )
        
        # Send notifications
        from booking.notification_helpers import notify_appointment_submitted
        notify_appointment_submitted(appointment)
        
        # Send confirmation email (async with Celery in production)
        self._send_confirmation_email(patient, appointment, data)
        
        # Store appointment ID in session for success page
        self.request.session['booking_id'] = str(appointment.id)
        
        return super().form_valid(form)
    
    def _send_confirmation_email(self, patient, appointment, data):
        """Send confirmation email to patient."""
        try:
            logger.info(f"Sending booking confirmation email to {patient.user.email}")
            subject = 'Hills Clinic - Consultation Request Received'
            html_message = render_to_string('booking/emails/confirmation.html', {
                'patient': patient,
                'appointment': appointment,
                'data': data,
            })
            
            send_mail(
                subject=subject,
                message=f'Your consultation request #{appointment.id} has been received. Please complete payment within 48 hours.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[patient.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Booking confirmation email sent successfully to {patient.user.email}")
        except Exception as e:
            # Log error but don't fail the booking
            logger.error(f"Email sending failed for {patient.user.email}: {e}", exc_info=True)


class BookingSuccessView(TemplateView):
    """Confirmation page after successful booking."""
    template_name = 'booking/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.request.session.get('booking_id')
        
        if booking_id:
            try:
                context['appointment'] = Appointment.objects.get(id=booking_id)
            except Appointment.DoesNotExist:
                pass
        
        context['page_title'] = 'Booking Confirmed'
        return context


class ContactView(FormView):
    """Handle general contact form submissions."""
    template_name = 'booking/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('booking:contact_success')
    
    def form_valid(self, form):
        data = form.cleaned_data
        
        # Send email to clinic
        try:
            send_mail(
                subject=f"Website Contact: {data['subject']}",
                message=f"""
New contact form submission:

Name: {data['name']}
Email: {data['email']}
Subject: {data['subject']}

Message:
{data['message']}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL if hasattr(settings, 'CONTACT_EMAIL') else 'info@hillsclinic.com'],
                fail_silently=True,
            )
        except Exception:
            pass
        
        messages.success(self.request, 'Thank you for your message. We will get back to you soon!')
        return super().form_valid(form)


class ContactSuccessView(TemplateView):
    """Success page after contact form submission."""
    template_name = 'booking/contact_success.html'


class QuickCallbackView(View):
    """Handle quick callback requests via HTMX."""
    
    def post(self, request):
        form = QuickCallbackForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            
            # Create a simple appointment/callback request
            Appointment.objects.create(
                appointment_type='callback',
                status='pending',
                notes=f"Callback Request - Phone: {data['phone']}, Best Time: {data['best_time']}"
            )
            
            # Return HTMX response
            return HttpResponse("""
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg">
                    <p class="font-medium">Thank you! We'll call you back soon.</p>
                </div>
            """)
        
        return HttpResponse("""
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
                <p class="font-medium">Please provide a valid phone number.</p>
            </div>
        """, status=400)


class AvailableTimeSlotsView(View):
    """API endpoint to get available time slots for a given date."""
    
    def get(self, request):
        date_str = request.GET.get('date')
        patient_tz = request.GET.get('timezone', 'Asia/Karachi')
        
        if not date_str:
            return JsonResponse({'error': 'Date is required'}, status=400)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
        
        # Get available slots for the date
        slots = TimeSlot.objects.filter(
            date=date,
            is_available=True
        ).order_by('start_time')
        
        # Convert to patient's timezone
        try:
            patient_timezone = pytz.timezone(patient_tz)
        except pytz.exceptions.UnknownTimeZoneError:
            patient_timezone = pytz.timezone('Asia/Karachi')
        
        available_slots = []
        for slot in slots:
            # Combine date and time, localize to Pakistan time, then convert
            pakistan_tz = pytz.timezone('Asia/Karachi')
            slot_datetime = pakistan_tz.localize(
                datetime.combine(slot.date, slot.start_time)
            )
            patient_local = slot_datetime.astimezone(patient_timezone)
            
            available_slots.append({
                'id': str(slot.id),
                'clinic_time': slot.start_time.strftime('%I:%M %p'),
                'patient_time': patient_local.strftime('%I:%M %p'),
                'patient_date': patient_local.strftime('%Y-%m-%d'),
            })
        
        return JsonResponse({
            'date': date_str,
            'timezone': patient_tz,
            'slots': available_slots,
        })


class GenerateICSView(View):
    """Generate ICS calendar file for appointment."""
    
    def get(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        if not appointment.time_slot:
            return HttpResponse('No time slot assigned', status=400)
        
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//Hills Clinic//Appointment//EN')
        cal.add('version', '2.0')
        
        # Create event
        event = Event()
        event.add('summary', f'Hills Clinic - {appointment.get_appointment_type_display()}')
        event.add('description', f"""
Your appointment at Hills Clinic.

Type: {appointment.get_appointment_type_display()}
Status: {appointment.get_status_display()}

Contact: +92 301 5943329
WhatsApp: wa.me/923015943329

Hills Clinic - Limb Lengthening Excellence
        """.strip())
        
        # Set times
        pakistan_tz = pytz.timezone('Asia/Karachi')
        start_dt = pakistan_tz.localize(
            datetime.combine(appointment.time_slot.date, appointment.time_slot.start_time)
        )
        end_dt = pakistan_tz.localize(
            datetime.combine(appointment.time_slot.date, appointment.time_slot.end_time)
        )
        
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        event.add('dtstamp', timezone.now())
        event['uid'] = f'{appointment.id}@hillsclinic.com'
        
        # Add location
        event.add('location', 'Hills Clinic, Islamabad, Pakistan (or Video Call)')
        
        # Add reminder
        from icalendar import Alarm
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', 'Reminder: Hills Clinic Appointment in 1 hour')
        alarm.add('trigger', timedelta(hours=-1))
        event.add_component(alarm)
        
        cal.add_component(event)
        
        # Generate response
        response = HttpResponse(cal.to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = f'attachment; filename="hills-clinic-appointment-{appointment.id}.ics"'
        
        return response


class AppointmentStatusView(View):
    """Check appointment status (for HTMX polling)."""
    
    def get(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        status_colors = {
            'pending': 'yellow',
            'confirmed': 'green',
            'cancelled': 'red',
            'completed': 'blue',
            'no_show': 'gray',
        }
        
        color = status_colors.get(appointment.status, 'gray')
        
        return HttpResponse(f"""
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-{color}-100 text-{color}-800">
                {appointment.get_status_display()}
            </span>
        """)


class AppointmentICSView(View):
    """Generate ICS file for an appointment using integer PK."""
    
    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        
        # Verify the appointment belongs to the current user
        if request.user.is_authenticated:
            if hasattr(request.user, 'patient_profile'):
                if appointment.patient != request.user.patient_profile:
                    return HttpResponse('Unauthorized', status=403)
        
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//Hills Clinic//Appointment System//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        
        # Create event
        event = Event()
        event.add('summary', f'Hills Clinic - {appointment.get_appointment_type_display()}')
        
        # Combine date and time
        start_datetime = datetime.combine(
            appointment.time_slot.date,
            appointment.time_slot.start_time
        )
        end_datetime = datetime.combine(
            appointment.time_slot.date,
            appointment.time_slot.end_time
        )
        
        # Make timezone aware
        pk_tz = pytz.timezone('Asia/Karachi')
        start_datetime = pk_tz.localize(start_datetime)
        end_datetime = pk_tz.localize(end_datetime)
        
        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)
        event.add('dtstamp', timezone.now())
        event['uid'] = f'{appointment.pk}@hillsclinic.com'
        
        # Description
        description = f"""
Appointment Type: {appointment.get_appointment_type_display()}
Method: {appointment.get_consultation_method_display()}
Status: {appointment.get_status_display()}

Please arrive 15 minutes early for in-person appointments.
For video consultations, the link will be sent via email.

If you need to reschedule, please contact us at least 24 hours in advance.
        """
        event.add('description', description.strip())
        
        if appointment.consultation_method == 'in_clinic':
            event.add('location', 'Hills Limb Lengthening Clinic, Karachi, Pakistan')
        elif appointment.meeting_link:
            event.add('location', appointment.meeting_link)
        else:
            event.add('location', 'Video Call (Link to be provided)')
        
        # Add reminder
        from icalendar import Alarm
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', 'Reminder: Hills Clinic Appointment in 1 hour')
        alarm.add('trigger', timedelta(hours=-1))
        event.add_component(alarm)
        
        cal.add_component(event)
        
        # Generate response
        response = HttpResponse(cal.to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = f'attachment; filename="hills-clinic-appointment-{appointment.pk}.ics"'
        
        return response


# =============================================================================
# VIDEO CONSULTATION VIEWS
# =============================================================================

class VideoConsultationBookingView(FormView):
    """Handle video consultation booking with payment."""
    template_name = 'booking/video_consultation_booking.html'
    form_class = VideoConsultationForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Book Video Consultation'
        context['consultation_fee'] = PaymentService.format_amount(PaymentService.CONSULTATION_FEE)
        context['join_instructions'] = VideoConferenceService.get_join_instructions()
        return context
    
    def form_valid(self, form):
        data = form.cleaned_data
        
        # Create video consultation record
        consultation = VideoConsultation.objects.create(
            user=self.request.user if self.request.user.is_authenticated else None,
            patient_name=data['patient_name'],
            patient_email=data['patient_email'],
            patient_phone=data.get('patient_phone', ''),
            patient_country=data.get('patient_country', ''),
            patient_timezone=data.get('patient_timezone', 'UTC'),
            scheduled_date=data['scheduled_date'],
            scheduled_time=data['scheduled_time'],
            duration_minutes=30,
            reason=data['reason'],
            current_height=data.get('current_height', ''),
            desired_height_gain=data.get('desired_height_gain', ''),
            procedure_interest=data.get('procedure_interest', 'undecided'),
            medical_notes=data.get('medical_notes', ''),
            status='pending_payment',
        )
        
        # Create payment record
        payment = Payment.objects.create(
            user=self.request.user if self.request.user.is_authenticated else None,
            email=data['patient_email'],
            payment_type='video_consultation',
            video_consultation=consultation,
            amount=PaymentService.CONSULTATION_FEE / 100,  # Convert cents to dollars
            currency='USD',
            description=f'Video Consultation - {consultation.scheduled_date}',
        )
        
        # Create Stripe checkout session
        try:
            success_url = self.request.build_absolute_uri(
                reverse('booking:payment_success') + f'?session_id={{CHECKOUT_SESSION_ID}}&payment_id={payment.id}'
            )
            cancel_url = self.request.build_absolute_uri(
                reverse('booking:payment_cancelled') + f'?payment_id={payment.id}'
            )
            
            session = PaymentService.create_video_consultation_payment(
                patient_email=data['patient_email'],
                consultation_id=str(consultation.id),
                success_url=success_url,
                cancel_url=cancel_url,
            )
            
            payment.stripe_session_id = session.id
            payment.save()
            
            # Redirect to Stripe Checkout
            return redirect(session.url)
            
        except Exception as e:
            # If Stripe is not configured, show a message
            messages.warning(
                self.request,
                'Online payment is being set up. Please contact us directly to complete your booking.'
            )
            # Store consultation ID for reference
            self.request.session['consultation_id'] = str(consultation.id)
            return redirect('booking:video_consultation_pending', pk=consultation.pk)


class VideoConsultationPendingView(DetailView):
    """Show pending payment info for consultation."""
    model = VideoConsultation
    template_name = 'booking/video_consultation_pending.html'
    context_object_name = 'consultation'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Complete Your Booking'
        context['consultation_fee'] = PaymentService.format_amount(PaymentService.CONSULTATION_FEE)
        return context


class VideoConsultationDetailView(DetailView):
    """Show video consultation details and join link."""
    model = VideoConsultation
    template_name = 'booking/video_consultation_detail.html'
    context_object_name = 'consultation'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Video Consultation Details'
        context['join_instructions'] = VideoConferenceService.get_join_instructions()
        return context


class VideoConsultationJoinView(DetailView):
    """Join video consultation meeting room."""
    model = VideoConsultation
    template_name = 'booking/video_consultation_join.html'
    context_object_name = 'consultation'
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Check if consultation can be joined
        if not self.object.can_join:
            messages.error(request, 'This consultation is not currently active.')
            return redirect('booking:video_consultation_detail', pk=self.object.pk)
        
        # Generate room if not exists
        if not self.object.room_id:
            self.object.generate_meeting_room()
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Join Video Consultation'
        
        # Get display name
        if self.request.user.is_authenticated:
            display_name = self.request.user.get_full_name() or self.request.user.email
        else:
            display_name = self.object.patient_name
        
        context['meeting_config'] = VideoConferenceService.get_meeting_config(
            self.object.room_id,
            display_name,
            is_moderator=self.request.user.is_staff
        )
        return context


# =============================================================================
# PAYMENT VIEWS
# =============================================================================

class PaymentSuccessView(TemplateView):
    """Handle successful payment callback from Stripe."""
    template_name = 'booking/payment_success.html'
    
    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get('payment_id')
        session_id = request.GET.get('session_id')
        
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
                
                # Mark payment as completed
                if payment.status == 'pending':
                    payment.mark_completed()
                
                self.payment = payment
            except Payment.DoesNotExist:
                self.payment = None
        else:
            self.payment = None
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Payment Successful'
        context['payment'] = getattr(self, 'payment', None)
        
        if self.payment and self.payment.video_consultation:
            context['consultation'] = self.payment.video_consultation
        
        return context


class PaymentCancelledView(TemplateView):
    """Handle cancelled payment callback from Stripe."""
    template_name = 'booking/payment_cancelled.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Payment Cancelled'
        
        payment_id = self.request.GET.get('payment_id')
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
                context['payment'] = payment
                if payment.video_consultation:
                    context['consultation'] = payment.video_consultation
            except Payment.DoesNotExist:
                pass
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """Handle Stripe webhook events."""
    
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        
        try:
            event = PaymentService.verify_webhook_signature(payload, sig_header)
        except ValueError:
            return HttpResponse(status=400)
        except Exception:
            return HttpResponse(status=400)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_checkout_completed(session)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._handle_payment_failed(payment_intent)
        
        return HttpResponse(status=200)
    
    def _handle_checkout_completed(self, session):
        """Handle successful checkout session."""
        session_id = session.get('id')
        
        try:
            payment = Payment.objects.get(stripe_session_id=session_id)
            payment.mark_completed(
                payment_intent_id=session.get('payment_intent')
            )
        except Payment.DoesNotExist:
            pass
    
    def _handle_payment_failed(self, payment_intent):
        """Handle failed payment."""
        payment_intent_id = payment_intent.get('id')
        
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            payment.mark_failed()
        except Payment.DoesNotExist:
            pass


class DepositPaymentView(TemplateView):
    """Handle surgery deposit payments."""
    template_name = 'booking/deposit_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Pay Surgery Deposit'
        context['deposit_amount'] = PaymentService.format_amount(PaymentService.DEPOSIT_AMOUNT)
        return context
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'Please provide your email address.')
            return self.get(request, *args, **kwargs)
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=email,
            payment_type='surgery_deposit',
            amount=PaymentService.DEPOSIT_AMOUNT / 100,
            currency='USD',
            description='Surgery Deposit',
        )
        
        try:
            success_url = request.build_absolute_uri(
                reverse('booking:payment_success') + f'?payment_id={payment.id}'
            )
            cancel_url = request.build_absolute_uri(
                reverse('booking:payment_cancelled') + f'?payment_id={payment.id}'
            )
            
            session = PaymentService.create_deposit_payment(
                patient_email=email,
                appointment_id=str(payment.id),
                success_url=success_url,
                cancel_url=cancel_url,
            )
            
            payment.stripe_session_id = session.id
            payment.save()
            
            return redirect(session.url)
            
        except Exception as e:
            messages.error(request, 'Payment processing is currently unavailable. Please contact us directly.')
            return self.get(request, *args, **kwargs)
