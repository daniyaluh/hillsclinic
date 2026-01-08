"""
Portal app views for Hills Clinic.

Views for patient portal functionality:
- Dashboard
- Document management
- Consent management
- Profile management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q

from .models import PortalUpload, ConsentRecord, AuditLog, Notification
from .forms import DocumentUploadForm, ConsentForm, ProfileUpdateForm, ExtendedProfileForm, AppointmentBookingForm
from booking.models import Patient, Appointment, TimeSlot


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_action(user, action, resource_type, resource_id=None, patient=None, details=None, request=None):
    """Create an audit log entry."""
    AuditLog.objects.create(
        user=user,
        patient=patient,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500] if request else '',
        details=details or {}
    )


class PatientRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user has a patient profile."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Staff users should use the staff portal
        if request.user.is_staff or request.user.is_superuser:
            return redirect('staff:dashboard')
        
        # Check if user has a patient profile
        if not hasattr(request.user, 'patient_profile'):
            # Create one if it doesn't exist
            Patient.objects.get_or_create(user=request.user)
        
        return super().dispatch(request, *args, **kwargs)


class DashboardView(PatientRequiredMixin, TemplateView):
    """Patient dashboard showing overview of appointments, documents, etc."""
    template_name = 'portal/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.request.user.patient_profile
        
        # Upcoming appointments (with time slots scheduled)
        context['upcoming_appointments'] = Appointment.objects.filter(
            patient=patient,
            time_slot__date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).select_related('time_slot').order_by('time_slot__date', 'time_slot__start_time')[:5]
        
        # Pending requests (no time slot yet - awaiting doctor confirmation)
        context['pending_requests'] = Appointment.objects.filter(
            patient=patient,
            time_slot__isnull=True,
            status='pending'
        ).order_by('-created_at')[:5]
        
        # Past appointments
        context['past_appointments'] = Appointment.objects.filter(
            patient=patient,
            status='completed'
        ).select_related('time_slot').order_by('-time_slot__date')[:3]
        
        # Recent uploads
        context['recent_uploads'] = PortalUpload.objects.filter(
            patient=patient,
            visible_to_patient=True
        ).order_by('-uploaded_at')[:5]
        
        # Documents count
        context['documents_count'] = PortalUpload.objects.filter(
            patient=patient
        ).count()
        
        # Active consents
        context['active_consents'] = ConsentRecord.objects.filter(
            patient=patient,
            granted=True,
            revoked_at__isnull=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )
        
        # Patient profile completeness
        profile_fields = ['phone_number', 'date_of_birth', 'country', 'current_height']
        filled = sum(1 for f in profile_fields if getattr(patient, f))
        context['profile_completeness'] = int((filled / len(profile_fields)) * 100)
        
        # Log dashboard view
        log_action(
            user=self.request.user,
            action='view',
            resource_type='Dashboard',
            patient=patient,
            request=self.request
        )
        
        return context


class DocumentListView(PatientRequiredMixin, ListView):
    """List patient's uploaded documents."""
    template_name = 'portal/documents/list.html'
    context_object_name = 'documents'
    paginate_by = 12
    
    def get_queryset(self):
        patient = self.request.user.patient_profile
        queryset = PortalUpload.objects.filter(
            patient=patient,
            visible_to_patient=True
        ).order_by('-uploaded_at')
        
        # Filter by type
        upload_type = self.request.GET.get('type')
        if upload_type:
            queryset = queryset.filter(upload_type=upload_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upload_types'] = PortalUpload._meta.get_field('upload_type').choices
        context['current_type'] = self.request.GET.get('type', '')
        return context


class DocumentUploadView(PatientRequiredMixin, CreateView):
    """Upload a new document."""
    template_name = 'portal/documents/upload.html'
    form_class = DocumentUploadForm
    success_url = reverse_lazy('portal:documents')
    
    def form_valid(self, form):
        form.instance.patient = self.request.user.patient_profile
        response = super().form_valid(form)
        
        # Log upload
        log_action(
            user=self.request.user,
            action='create',
            resource_type='PortalUpload',
            resource_id=self.object.id,
            patient=self.request.user.patient_profile,
            request=self.request,
            details={'upload_type': self.object.upload_type, 'file_name': self.object.file.name}
        )
        
        messages.success(self.request, 'Document uploaded successfully!')
        return response


class DocumentDeleteView(PatientRequiredMixin, DeleteView):
    """Delete a document."""
    template_name = 'portal/documents/delete.html'
    success_url = reverse_lazy('portal:documents')
    context_object_name = 'document'
    
    def get_queryset(self):
        # Only allow deleting own documents
        return PortalUpload.objects.filter(patient=self.request.user.patient_profile)
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        
        # Log deletion
        log_action(
            user=request.user,
            action='delete',
            resource_type='PortalUpload',
            resource_id=obj.id,
            patient=request.user.patient_profile,
            request=request,
            details={'upload_type': obj.upload_type, 'file_name': obj.file.name}
        )
        
        messages.success(request, 'Document deleted successfully.')
        return super().delete(request, *args, **kwargs)


class DocumentDownloadView(PatientRequiredMixin, DetailView):
    """Download a document - serves file directly."""
    
    def get_queryset(self):
        # Only allow downloading own documents
        return PortalUpload.objects.filter(patient=self.request.user.patient_profile)
    
    def get(self, request, *args, **kwargs):
        document = self.get_object()
        
        try:
            file = document.file
            content_type = document.mime_type or 'application/octet-stream'
            
            filename = document.title or f"{document.get_upload_type_display()}_{document.id}"
            ext = file.name.split('.')[-1] if '.' in file.name else ''
            if ext and not filename.endswith(f'.{ext}'):
                filename = f"{filename}.{ext}"
            
            response = HttpResponse(file.read(), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            messages.error(request, f"Could not download file: {str(e)}")
            return redirect('portal:documents')


class ConsentListView(PatientRequiredMixin, ListView):
    """List patient's consent records."""
    template_name = 'portal/consent/list.html'
    context_object_name = 'consents'
    
    def get_queryset(self):
        return ConsentRecord.objects.filter(
            patient=self.request.user.patient_profile
        ).order_by('-granted_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Group consents by type and get latest for each
        patient = self.request.user.patient_profile
        consent_types = dict(ConsentRecord._meta.get_field('consent_type').choices)
        
        consent_status = {}
        surgery_consents = {}
        other_consents = {}
        
        for consent_type, label in consent_types.items():
            latest = ConsentRecord.objects.filter(
                patient=patient,
                consent_type=consent_type
            ).order_by('-granted_at').first()
            
            consent_info = {
                'type': consent_type,
                'label': label,
                'record': latest,
                'is_active': latest.is_active if latest else False,
                'is_surgery_required': consent_type in ConsentRecord.REQUIRED_FOR_SURGERY
            }
            
            consent_status[consent_type] = consent_info
            
            if consent_type in ConsentRecord.REQUIRED_FOR_SURGERY:
                surgery_consents[consent_type] = consent_info
            else:
                other_consents[consent_type] = consent_info
        
        context['consent_status'] = consent_status
        context['surgery_consents'] = surgery_consents
        context['other_consents'] = other_consents
        
        # Get surgery readiness status
        context['surgery_status'] = ConsentRecord.check_surgery_ready(patient)
        
        return context


class ConsentGrantView(PatientRequiredMixin, TemplateView):
    """Grant or update consent."""
    template_name = 'portal/consent/grant.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consent_type = self.kwargs.get('consent_type')
        
        # Get consent text based on type - includes surgery-required consents
        consent_texts = {
            # Surgery required consents
            'procedure_consent': """
            INFORMED CONSENT FOR LIMB LENGTHENING SURGERY
            
            I, the undersigned patient, hereby consent to undergo limb lengthening surgery at Hills Clinic. 
            I understand that this is a complex orthopedic procedure that involves:
            
            1. Surgical placement of internal or external lengthening devices
            2. A gradual lengthening process over several weeks/months
            3. Physical therapy and rehabilitation
            4. Multiple follow-up visits and potential additional procedures
            
            I have been informed of the nature, purpose, and expected outcomes of the procedure. 
            I have had the opportunity to ask questions and have received satisfactory answers.
            
            I understand that no guarantee has been made about the results of the surgery.
            """,
            'anesthesia_consent': """
            CONSENT FOR ANESTHESIA
            
            I consent to the administration of anesthesia as deemed necessary by the anesthesiologist 
            for my limb lengthening surgery.
            
            I understand that anesthesia involves risks including but not limited to:
            - Allergic reactions to medications
            - Nausea and vomiting
            - Respiratory complications
            - In rare cases, more serious complications
            
            I have disclosed my complete medical history, allergies, and current medications.
            I agree to follow all pre-operative instructions regarding fasting and medication.
            """,
            'risks_acknowledgment': """
            ACKNOWLEDGMENT OF RISKS AND COMPLICATIONS
            
            I acknowledge that I have been informed of the potential risks and complications 
            associated with limb lengthening surgery, including but not limited to:
            
            - Infection at surgical site or pin sites
            - Nerve damage or nerve pain
            - Blood clots (DVT/PE)
            - Bone healing complications (non-union, malunion)
            - Joint stiffness or contractures
            - Chronic pain
            - Need for additional surgeries
            - Cosmetic irregularities
            - Muscle weakness
            - Psychological adjustment challenges
            
            I understand these risks and have had the opportunity to discuss them with my surgeon.
            I voluntarily choose to proceed with the surgery.
            """,
            # Other consents
            'media_use': """
            I grant Hills Clinic permission to use photographs and videos of my limb lengthening 
            procedure for educational, promotional, and marketing purposes. I understand that my 
            identity may be visible in these materials unless I specifically request face obscuring.
            """,
            'testimonial': """
            I grant Hills Clinic permission to publish my testimonial, including quotes and my 
            experience with the procedure, on their website, social media, and marketing materials.
            """,
            'face_visible': """
            I grant Hills Clinic permission to show my face in photographs, videos, and other 
            media used for educational and promotional purposes. I understand I can revoke this 
            consent at any time.
            """,
            'before_after': """
            I grant Hills Clinic permission to use my before and after photographs to demonstrate 
            the results of limb lengthening procedures. These images may be used on the website, 
            in presentations, and in marketing materials.
            """,
            'research': """
            I consent to my anonymized medical data being used for research purposes to advance 
            the field of limb lengthening surgery. My personal identity will not be disclosed 
            in any research publications.
            """,
            'marketing': """
            I consent to receive marketing communications from Hills Clinic including newsletters, 
            promotional offers, and updates about new procedures and services.
            """,
            'data_sharing': """
            I consent to my medical information being shared with partner healthcare providers, 
            laboratories, and imaging centers as necessary for my care. All sharing will comply 
            with applicable privacy laws and regulations.
            """,
        }
        
        context['consent_type'] = consent_type
        context['consent_type_display'] = dict(ConsentRecord._meta.get_field('consent_type').choices).get(consent_type, consent_type)
        context['consent_text'] = consent_texts.get(consent_type, '')
        context['is_surgery_required'] = consent_type in ConsentRecord.REQUIRED_FOR_SURGERY
        
        # Use the form passed in kwargs if available (for POST with errors), else create new
        if 'form' not in kwargs:
            context['form'] = ConsentForm()
        
        return context
    
    def post(self, request, *args, **kwargs):
        form = ConsentForm(request.POST)
        consent_type = self.kwargs.get('consent_type')
        
        if form.is_valid():
            patient = request.user.patient_profile
            
            # Get consent text from context
            context = self.get_context_data()
            consent_text = context.get('consent_text', '')
            
            # Create consent record
            consent = ConsentRecord.objects.create(
                patient=patient,
                consent_type=consent_type,
                granted=form.cleaned_data['granted'],
                consent_text=consent_text,
                patient_signature=form.cleaned_data['signature'],
                ip_address=get_client_ip(request)
            )
            
            # Log consent action
            log_action(
                user=request.user,
                action='create',
                resource_type='ConsentRecord',
                resource_id=consent.id,
                patient=patient,
                request=request,
                details={'consent_type': consent_type, 'granted': consent.granted}
            )
            
            # Notify staff about new consent (especially surgery-required ones)
            if consent.granted:
                consent_label = consent.get_consent_type_display()
                patient_name = patient.full_name or patient.user.email
                
                Notification.create_for_staff(
                    notification_type='consent_granted',
                    title=f'Consent Granted: {consent_label}',
                    message=f'{patient_name} has granted {consent_label}.',
                    action_url=f'/staff/consents/{consent.id}/'
                )
            
            status = 'granted' if consent.granted else 'denied'
            messages.success(request, f'Consent {status} successfully.')
            return redirect('portal:consents')
        
        return self.render_to_response(self.get_context_data(form=form))


class ConsentRevokeView(PatientRequiredMixin, TemplateView):
    """Request revocation of a previously granted consent (pending staff review)."""
    template_name = 'portal/consent/revoke.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consent = get_object_or_404(
            ConsentRecord,
            pk=self.kwargs.get('pk'),
            patient=self.request.user.patient_profile
        )
        context['consent'] = consent
        return context
    
    def post(self, request, *args, **kwargs):
        consent = get_object_or_404(
            ConsentRecord,
            pk=self.kwargs.get('pk'),
            patient=request.user.patient_profile
        )
        
        reason = request.POST.get('reason', '')
        consent_label = consent.get_consent_type_display()
        patient = request.user.patient_profile
        patient_name = patient.full_name or patient.user.email
        
        # Request revocation (pending staff review) instead of immediate revoke
        consent.request_revocation(reason=reason)
        
        # Log revocation request
        log_action(
            user=request.user,
            action='update',
            resource_type='ConsentRecord',
            resource_id=consent.id,
            patient=patient,
            request=request,
            details={'action': 'revocation_requested', 'reason': reason}
        )
        
        # Notify staff about consent revocation request (needs review)
        Notification.create_for_staff(
            notification_type='consent_revoked',
            title=f'Revocation Request: {consent_label}',
            message=f'{patient_name} has requested to revoke {consent_label}. Please review.' + (f' Reason: {reason}' if reason else ''),
            action_url=f'/staff/consents/{consent.id}/'
        )
        
        messages.success(request, 'Your revocation request has been submitted and is pending review. You can contact us on WhatsApp for more details.')
        return redirect('portal:consents')


class ProfileView(PatientRequiredMixin, UpdateView):
    """View and update patient profile."""
    template_name = 'portal/profile.html'
    form_class = ExtendedProfileForm
    success_url = reverse_lazy('portal:profile')
    
    def get_object(self):
        return self.request.user.patient_profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.get_object()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Log profile update
        log_action(
            user=self.request.user,
            action='update',
            resource_type='Patient',
            resource_id=self.object.id,
            patient=self.object,
            request=self.request,
            details={'updated_fields': list(form.changed_data)}
        )
        
        messages.success(self.request, 'Profile updated successfully!')
        return response


class AppointmentListView(PatientRequiredMixin, ListView):
    """List patient's appointments."""
    template_name = 'portal/appointments.html'
    context_object_name = 'appointments'
    
    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.request.user.patient_profile
        ).select_related('time_slot').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Split into upcoming, pending (no slot), and past
        now = timezone.now()
        all_appointments = list(self.get_queryset())
        
        # Pending requests (no time slot yet - awaiting doctor to assign slot)
        context['pending_requests'] = [
            a for a in all_appointments 
            if a.time_slot is None and a.status in ['pending', 'confirmed']
        ]
        
        # Upcoming (has time slot in future and not cancelled/completed)
        context['upcoming'] = [
            a for a in all_appointments 
            if a.time_slot and a.time_slot.date >= now.date() and a.status in ['pending', 'confirmed']
        ]
        
        # Past (completed, cancelled, or time slot in the past)
        context['past'] = [
            a for a in all_appointments 
            if (a.time_slot and a.time_slot.date < now.date()) or a.status in ['completed', 'cancelled', 'no_show']
        ]
        
        return context


class AppointmentDetailView(PatientRequiredMixin, DetailView):
    """View details of a specific appointment."""
    template_name = 'portal/appointment_detail.html'
    context_object_name = 'appointment'
    
    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.request.user.patient_profile
        ).select_related('time_slot', 'patient')


class AppointmentBookView(PatientRequiredMixin, TemplateView):
    """Book a new appointment from the portal."""
    template_name = 'portal/appointments/book.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AppointmentBookingForm()
        
        # Get available dates for the next 30 days
        from datetime import timedelta
        today = timezone.now().date()
        end_date = today + timedelta(days=30)
        
        context['today'] = today
        
        available_dates = TimeSlot.objects.filter(
            date__gte=today,
            date__lte=end_date,
            is_available=True
        ).exclude(
            appointments__status__in=['confirmed', 'pending']
        ).values_list('date', flat=True).distinct()
        
        context['available_dates'] = [d.isoformat() for d in available_dates]
        return context
    
    def post(self, request, *args, **kwargs):
        from datetime import datetime
        
        appointment_type = request.POST.get('appointment_type', 'consultation')
        date_str = request.POST.get('preferred_date')
        time_slot_id = request.POST.get('time_slot')
        notes = request.POST.get('notes', '')
        
        try:
            time_slot = TimeSlot.objects.get(
                pk=time_slot_id,
                is_available=True
            )
            
            # Check if slot is still available
            existing = Appointment.objects.filter(
                time_slot=time_slot,
                status__in=['confirmed', 'pending']
            ).exists()
            
            if existing:
                messages.error(request, 'This time slot is no longer available. Please choose another.')
                return redirect('portal:appointment-book')
            
            # Create appointment
            appointment = Appointment.objects.create(
                patient=request.user.patient_profile,
                time_slot=time_slot,
                appointment_type=appointment_type,
                patient_notes=notes,
                status='pending'
            )
            
            # Log the action
            log_action(
                user=request.user,
                action='create',
                resource_type='Appointment',
                resource_id=appointment.id,
                patient=request.user.patient_profile,
                request=request,
                details={
                    'appointment_type': appointment_type,
                    'date': time_slot.date.isoformat(),
                    'time': str(time_slot.start_time)
                }
            )
            
            messages.success(request, 'Appointment booked successfully! We will confirm it shortly.')
            return redirect('portal:appointments')
            
        except TimeSlot.DoesNotExist:
            messages.error(request, 'Invalid time slot selected. Please try again.')
            return redirect('portal:appointment-book')


class AvailableTimeSlotsAPI(PatientRequiredMixin, TemplateView):
    """API to get available time slots for a specific date."""
    
    def get(self, request, *args, **kwargs):
        from datetime import datetime
        
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': 'Date required'}, status=400)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
        
        # Get available slots for this date
        slots = TimeSlot.objects.filter(
            date=date,
            is_available=True
        ).exclude(
            appointments__status__in=['confirmed', 'pending']
        ).order_by('start_time')
        
        slot_data = [
            {
                'id': slot.id,
                'start_time': slot.start_time.strftime('%I:%M %p'),
                'end_time': slot.end_time.strftime('%I:%M %p'),
                'display': f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"
            }
            for slot in slots
        ]
        
        return JsonResponse({'slots': slot_data})


class AppointmentPaymentView(PatientRequiredMixin, TemplateView):
    """Payment page for appointment - choose payment method."""
    template_name = 'portal/payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = get_object_or_404(
            Appointment,
            pk=self.kwargs['pk'],
            patient=self.request.user.patient_profile
        )
        context['appointment'] = appointment
        
        # Determine if patient is from Pakistan (local payment) or international (Stripe)
        patient = self.request.user.patient_profile
        is_pakistan = patient.country.lower() in ['pakistan', 'pk', 'پاکستان']
        context['is_pakistan'] = is_pakistan
        
        # Import form
        from .forms import PaymentProofForm
        context['form'] = PaymentProofForm()
        
        # Payment details for Pakistan
        context['payment_details'] = {
            'easypaisa': {
                'account': '03228610593',
                'name': 'Hills Clinic',
            },
            'jazzcash': {
                'account': '03228610593',
                'name': 'Hills Clinic',
            },
            'bank': {
                'bank_name': 'HBL (Habib Bank Limited)',
                'account_title': 'Hills Clinic Pvt Ltd',
                'account_number': '1234567890123',
                'iban': 'PK12HABB1234567890123',
            }
        }
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle payment proof upload."""
        from .forms import PaymentProofForm
        
        appointment = get_object_or_404(
            Appointment,
            pk=self.kwargs['pk'],
            patient=request.user.patient_profile
        )
        
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            appointment.payment_method = form.cleaned_data['payment_method']
            appointment.payment_proof = form.cleaned_data['payment_proof']
            appointment.payment_status = 'submitted'
            appointment.save()
            
            # Send notification to staff
            from booking.notification_helpers import notify_payment_submitted
            notify_payment_submitted(appointment)
            
            # Log the action
            log_action(
                user=request.user,
                action='update',
                resource_type='Appointment',
                resource_id=appointment.id,
                patient=request.user.patient_profile,
                request=request,
                details={'action': 'payment_proof_uploaded', 'method': appointment.payment_method}
            )
            
            messages.success(request, 'Payment proof submitted! Our team will verify it within 24 hours.')
            return redirect('portal:appointments')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


class StripePaymentView(PatientRequiredMixin, TemplateView):
    """Create Stripe checkout session for international payments."""
    
    def get(self, request, *args, **kwargs):
        import stripe
        from django.conf import settings
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        appointment = get_object_or_404(
            Appointment,
            pk=self.kwargs['pk'],
            patient=request.user.patient_profile
        )
        
        # Create Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Hills Clinic Consultation Fee',
                            'description': f'Initial consultation appointment',
                        },
                        'unit_amount': int(appointment.consultation_fee * 100),  # Stripe uses cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(
                    f'/portal/appointments/{appointment.id}/payment/stripe/success/'
                ) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(
                    f'/portal/appointments/{appointment.id}/payment/stripe/cancel/'
                ),
                customer_email=request.user.email,
                metadata={
                    'appointment_id': appointment.id,
                    'patient_email': request.user.email,
                }
            )
            
            # Store payment intent
            appointment.stripe_payment_intent_id = checkout_session.payment_intent or checkout_session.id
            appointment.payment_method = 'stripe'
            appointment.save()
            
            return redirect(checkout_session.url)
            
        except stripe.error.StripeError as e:
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('portal:appointment-payment', pk=appointment.id)


class StripeSuccessView(PatientRequiredMixin, TemplateView):
    """Handle successful Stripe payment."""
    template_name = 'portal/payment_success.html'
    
    def get(self, request, *args, **kwargs):
        import stripe
        from django.conf import settings
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        appointment = get_object_or_404(
            Appointment,
            pk=self.kwargs['pk'],
            patient=request.user.patient_profile
        )
        
        session_id = request.GET.get('session_id')
        if session_id:
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status == 'paid':
                    appointment.payment_status = 'verified'
                    appointment.payment_confirmed_at = timezone.now()
                    appointment.payment_notes = f'Stripe payment confirmed. Session: {session_id}'
                    appointment.save()
                    
                    # Log the action
                    log_action(
                        user=request.user,
                        action='update',
                        resource_type='Appointment',
                        resource_id=appointment.id,
                        patient=request.user.patient_profile,
                        request=request,
                        details={'action': 'stripe_payment_verified', 'session_id': session_id}
                    )
                    
                    messages.success(request, 'Payment successful! Your appointment is now confirmed.')
            except stripe.error.StripeError:
                messages.warning(request, 'Could not verify payment. Our team will confirm manually.')
        
        return redirect('portal:appointments')


class StripeCancelView(PatientRequiredMixin, TemplateView):
    """Handle cancelled Stripe payment."""
    
    def get(self, request, *args, **kwargs):
        appointment = get_object_or_404(
            Appointment,
            pk=self.kwargs['pk'],
            patient=request.user.patient_profile
        )
        
        messages.warning(request, 'Payment was cancelled. You can try again or choose a different payment method.')
        return redirect('portal:appointment-payment', pk=appointment.id)


class PatientCalendarView(PatientRequiredMixin, TemplateView):
    """Visual calendar view for patient's appointments."""
    template_name = 'portal/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.request.user.patient_profile
        
        import calendar
        from datetime import date, timedelta
        
        # Get month from query param or use current month
        month_param = self.request.GET.get('month')
        if month_param:
            try:
                year, month = map(int, month_param.split('-'))
                current_month = date(year, month, 1)
            except (ValueError, AttributeError):
                current_month = date.today().replace(day=1)
        else:
            current_month = date.today().replace(day=1)
        
        # Previous and next months for navigation
        if current_month.month == 1:
            prev_month = current_month.replace(year=current_month.year - 1, month=12)
        else:
            prev_month = current_month.replace(month=current_month.month - 1)
        
        if current_month.month == 12:
            next_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            next_month = current_month.replace(month=current_month.month + 1)
        
        # Get calendar for the month
        cal = calendar.Calendar(firstweekday=0)  # Monday start
        month_days = cal.monthdatescalendar(current_month.year, current_month.month)
        
        # Get all appointments for this patient in the visible range
        first_day = month_days[0][0]
        last_day = month_days[-1][-1]
        
        appointments = Appointment.objects.filter(
            patient=patient,
            time_slot__date__gte=first_day,
            time_slot__date__lte=last_day
        ).select_related('time_slot').order_by('time_slot__date', 'time_slot__start_time')
        
        # Create a lookup by date
        appointments_by_date = {}
        for apt in appointments:
            if apt.time_slot:
                apt_date = apt.time_slot.date
                if apt_date not in appointments_by_date:
                    appointments_by_date[apt_date] = []
                appointments_by_date[apt_date].append(apt)
        
        # Build calendar days
        today = date.today()
        calendar_days = []
        for week in month_days:
            for day in week:
                calendar_days.append({
                    'date': day,
                    'is_current_month': day.month == current_month.month,
                    'is_today': day == today,
                    'appointments': appointments_by_date.get(day, [])
                })
        
        # Appointments this month (with time slots)
        appointments_this_month = Appointment.objects.filter(
            patient=patient,
            time_slot__date__year=current_month.year,
            time_slot__date__month=current_month.month
        ).select_related('time_slot').order_by('time_slot__date', 'time_slot__start_time')
        
        context['current_month'] = current_month
        context['prev_month'] = prev_month
        context['next_month'] = next_month
        context['weekdays'] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        context['calendar_days'] = calendar_days
        context['appointments_this_month'] = appointments_this_month
        
        return context


# =============================================================================
# NOTIFICATION VIEWS
# =============================================================================

class NotificationListView(LoginRequiredMixin, ListView):
    """List all notifications for the logged-in user."""
    template_name = 'portal/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.unread_count(self.request.user)
        return context


def notification_mark_read(request, pk):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    # Redirect to action URL if set, otherwise back to notifications
    if notification.action_url:
        return redirect(notification.action_url)
    return redirect('portal:notifications')


def notification_mark_all_read(request):
    """Mark all notifications as read for the user."""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'All notifications marked as read.')
    return redirect('portal:notifications')


def notifications_dropdown(request):
    """Return recent notifications for dropdown (AJAX)."""
    if not request.user.is_authenticated:
        return JsonResponse({'notifications': [], 'unread_count': 0})
    
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    data = {
        'unread_count': Notification.unread_count(request.user),
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message[:100] + '...' if len(n.message) > 100 else n.message,
                'is_read': n.is_read,
                'action_url': n.action_url,
                'created_at': n.created_at.strftime('%b %d, %H:%M'),
                'type': n.notification_type,
            }
            for n in notifications
        ]
    }
    return JsonResponse(data)
