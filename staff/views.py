"""
Views for Staff/Doctor Portal.

Role Separation:
- Staff: payment_list, time_slot_management, patient_update_name, approve appointments
- Doctor: patient_list, patient_detail, appointment_list, calendar_view, verify_document
- Both: dashboard (shows different content based on role)
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.db import models
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, FileResponse
from datetime import timedelta
import mimetypes

from .decorators import staff_required, doctor_required, is_staff_user, is_doctor_only
from booking.models import Patient, Appointment, TimeSlot, VideoConsultation, Payment
from booking.notifications import send_appointment_confirmed, send_payment_rejected, send_appointment_cancelled
from portal.models import PortalUpload, ConsentRecord


@doctor_required
def dashboard(request):
    """Dashboard with overview - content varies by role."""
    today = timezone.now().date()
    user = request.user
    is_staff = is_staff_user(user)
    is_doctor = is_doctor_only(user)
    
    # Get statistics
    stats = {
        'total_patients': Patient.objects.count(),
        'new_patients_today': Patient.objects.filter(created_at__date=today).count(),
        'new_patients_week': Patient.objects.filter(created_at__gte=today - timedelta(days=7)).count(),
        
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'confirmed_appointments': Appointment.objects.filter(status='confirmed').count(),
        'unscheduled_appointments': Appointment.objects.filter(time_slot__isnull=True, status='pending').count(),
        'todays_appointments': Appointment.objects.filter(
            time_slot__date=today,
            status__in=['pending', 'confirmed']
        ).count(),
        
        'pending_consultations': VideoConsultation.objects.filter(status='pending').count(),
        'scheduled_consultations': VideoConsultation.objects.filter(status='scheduled').count(),
        
        'unverified_documents': PortalUpload.objects.filter(is_verified=False).count(),
        'total_documents': PortalUpload.objects.count(),
        'documents_pending': PortalUpload.objects.filter(is_verified=False).count(),
        'documents_verified': PortalUpload.objects.filter(is_verified=True).count(),
        
        # Payment stats - based on Appointment payment_status
        'total_payments': Appointment.objects.filter(payment_status='verified').count(),
        'pending_payments': Appointment.objects.filter(payment_status__in=['pending', 'submitted']).count(),
        
        # Payment verification stats
        'payments_pending_verification': Appointment.objects.filter(payment_status='submitted').count(),
        'payments_verified': Appointment.objects.filter(payment_status='verified').count(),
        'payments_overdue': Appointment.objects.filter(
            payment_status__in=['pending', 'submitted'],
            payment_deadline__lt=timezone.now()
        ).count(),
    }
    
    # Recent patients
    recent_patients = Patient.objects.select_related('user').order_by('-created_at')[:5]
    
    # Pending consultation requests (no time slot assigned yet)
    pending_requests = Appointment.objects.filter(
        time_slot__isnull=True,
        status='pending'
    ).select_related('patient__user').order_by('-created_at')[:5]
    
    # Appointments with payment pending verification
    pending_payment_verification = Appointment.objects.filter(
        payment_status='submitted'
    ).select_related('patient__user').order_by('-created_at')[:5]
    
    # Upcoming appointments (with time slots)
    upcoming_appointments = Appointment.objects.filter(
        time_slot__date__gte=today,
        status__in=['pending', 'confirmed']
    ).select_related('patient__user', 'time_slot').order_by('time_slot__date', 'time_slot__start_time')[:5]
    
    # Today's video consultations
    todays_consultations = VideoConsultation.objects.filter(
        scheduled_date=today,
        status__in=['scheduled', 'in_progress']
    ).order_by('scheduled_time')[:5]
    
    # Recent documents pending review
    pending_documents = PortalUpload.objects.filter(
        is_verified=False
    ).select_related('patient__user').order_by('-uploaded_at')[:5]
    
    context = {
        'stats': stats,
        'recent_patients': recent_patients,
        'pending_requests': pending_requests,
        'pending_payment_verification': pending_payment_verification,
        'upcoming_appointments': upcoming_appointments,
        'todays_consultations': todays_consultations,
        'pending_documents': pending_documents,
        'is_staff': is_staff,
        'is_doctor': is_doctor,
    }
    
    return render(request, 'staff/dashboard.html', context)


@doctor_required
def patient_list(request):
    """List all patients with search and filtering."""
    patients = Patient.objects.select_related('user').order_by('-created_at')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        patients = patients.filter(
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(country__icontains=search)
        )
    
    # Filter by country
    country = request.GET.get('country', '')
    if country:
        patients = patients.filter(country=country)
    
    # Filter by procedure interest
    procedure = request.GET.get('procedure', '')
    if procedure:
        patients = patients.filter(interested_in_procedure=procedure)
    
    # Pagination
    paginator = Paginator(patients, 20)
    page = request.GET.get('page', 1)
    patients = paginator.get_page(page)
    
    # Get unique countries and procedures for filters
    countries = Patient.objects.values_list('country', flat=True).distinct().order_by('country')
    procedures = Patient.objects.values_list('interested_in_procedure', flat=True).distinct()
    
    context = {
        'patients': patients,
        'search': search,
        'selected_country': country,
        'selected_procedure': procedure,
        'countries': countries,
        'procedures': [p for p in procedures if p],
    }
    
    return render(request, 'staff/patient_list.html', context)


@doctor_required
def patient_detail(request, patient_id):
    """View detailed patient information."""
    patient = get_object_or_404(Patient.objects.select_related('user'), id=patient_id)
    user = request.user
    user_is_staff = is_staff_user(user)
    
    # Handle new appointment creation (staff only)
    if request.method == 'POST' and user_is_staff:
        action = request.POST.get('action')
        if action == 'create_appointment':
            appointment_type = request.POST.get('appointment_type', 'follow_up')
            consultation_method = request.POST.get('consultation_method', 'video')
            notes = request.POST.get('notes', '')
            
            appointment = Appointment.objects.create(
                patient=patient,
                appointment_type=appointment_type,
                consultation_method=consultation_method,
                status='pending',
                patient_notes=notes,
            )
            messages.success(request, f"New {appointment.get_appointment_type_display()} appointment created. Assign a time slot to schedule it.")
            return redirect('staff:appointment_detail', appointment_id=appointment.id)
    
    # Get patient's appointments
    appointments = Appointment.objects.filter(patient=patient).select_related('time_slot').order_by('-created_at')
    
    # Get patient's documents
    documents = PortalUpload.objects.filter(patient=patient).order_by('-uploaded_at')
    
    # Get patient's consents
    consents = ConsentRecord.objects.filter(patient=patient).order_by('-granted_at')
    
    # Get video consultations
    consultations = VideoConsultation.objects.filter(
        patient_email=patient.user.email
    ).order_by('-scheduled_date')
    
    # Get payments from appointments (appointments with payment activity)
    payments = Appointment.objects.filter(
        patient=patient,
        payment_status__in=['submitted', 'verified', 'failed']
    ).exclude(payment_status='pending', payment_proof='').order_by('-created_at')
    
    # Calculate payment totals
    paid_amount = sum(apt.consultation_fee for apt in payments if apt.payment_status == 'verified')
    pending_amount = sum(apt.consultation_fee for apt in payments if apt.payment_status == 'submitted')
    
    # Get surgery readiness status
    surgery_status = ConsentRecord.check_surgery_ready(patient)
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'documents': documents,
        'consents': consents,
        'consultations': consultations,
        'payments': payments,
        'paid_amount': paid_amount,
        'pending_amount': pending_amount,
        'is_staff': user_is_staff,
        'surgery_status': surgery_status,
    }
    
    return render(request, 'staff/patient_detail.html', context)


@staff_required
def patient_update_name(request, patient_id):
    """Update patient's full name."""
    if request.method == 'POST':
        patient = get_object_or_404(Patient, id=patient_id)
        full_name = request.POST.get('full_name', '').strip()
        
        if full_name:
            patient.full_name = full_name
            patient.save()
            
            # Also update user's first/last name
            name_parts = full_name.split()
            patient.user.first_name = name_parts[0] if name_parts else ''
            patient.user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            patient.user.save()
            
            messages.success(request, f"Patient name updated to '{full_name}'.")
        else:
            messages.error(request, "Name cannot be empty.")
        
        return redirect('staff:patient_detail', patient_id=patient_id)
    
    return redirect('staff:patient_detail', patient_id=patient_id)


@doctor_required
def appointment_list(request):
    """List all appointments with filtering."""
    appointments = Appointment.objects.select_related(
        'patient__user', 'time_slot'
    ).order_by('-created_at')  # Order by created_at since time_slot can be None
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        appointments = appointments.filter(status=status)
    
    # Filter by date (only for appointments with time_slot)
    date_filter = request.GET.get('date', '')
    if date_filter:
        appointments = appointments.filter(time_slot__date=date_filter)
    
    # Filter by type
    apt_type = request.GET.get('type', '')
    if apt_type:
        appointments = appointments.filter(appointment_type=apt_type)
    
    # Pagination
    paginator = Paginator(appointments, 20)
    page = request.GET.get('page', 1)
    appointments = paginator.get_page(page)
    
    # Define choices inline
    status_choices = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    type_choices = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
        ('pre_op', 'Pre-operative'),
        ('surgery', 'Surgery'),
        ('post_op', 'Post-operative'),
    ]
    
    context = {
        'appointments': appointments,
        'selected_status': status,
        'selected_date': date_filter,
        'selected_type': apt_type,
        'status_choices': status_choices,
        'type_choices': type_choices,
    }
    
    return render(request, 'staff/appointment_list.html', context)


@doctor_required
def appointment_detail(request, appointment_id):
    """View and update appointment details."""
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient__user', 'time_slot'),
        id=appointment_id
    )
    
    user = request.user
    user_is_staff = is_staff_user(user)
    
    # Get available time slots for scheduling
    today = timezone.now().date()
    available_slots = TimeSlot.objects.filter(
        date__gte=today,
        is_available=True
    ).order_by('date', 'start_time')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Doctor-only actions
        if action == 'add_notes':
            appointment.doctor_notes = request.POST.get('doctor_notes', '')
            appointment.save()
            messages.success(request, "Doctor notes saved.")
        
        # Confirm appointment and assign time slot - available to doctor
        elif action == 'confirm_with_slot':
            # Only allow if payment is verified
            if appointment.payment_status != 'verified':
                messages.error(request, "Cannot assign slot until payment is verified.")
            else:
                slot_id = request.POST.get('time_slot')
                if slot_id:
                    try:
                        slot = TimeSlot.objects.get(id=slot_id, is_available=True)
                        appointment.time_slot = slot
                        appointment.status = 'confirmed'  # Auto-confirm since payment is verified
                        slot.is_available = False  # Mark slot as taken
                        slot.save()
                        appointment.save()
                        # Send confirmation email and notification
                        send_appointment_confirmed(appointment)
                        from booking.notification_helpers import notify_appointment_confirmed
                        notify_appointment_confirmed(appointment)
                        messages.success(request, f"Appointment confirmed for {slot.date} at {slot.start_time}. Confirmation email sent to patient.")
                    except TimeSlot.DoesNotExist:
                        messages.error(request, "Selected time slot is not available.")
                else:
                    messages.error(request, "Please select a time slot.")
        
        # Staff-only actions
        elif user_is_staff:
            if action == 'change_type':
                new_type = request.POST.get('appointment_type')
                valid_types = ['consultation', 'follow_up', 'pre_op', 'surgery', 'post_op']
                if new_type in valid_types:
                    appointment.appointment_type = new_type
                    appointment.save()
                    messages.success(request, f"Appointment type changed to {appointment.get_appointment_type_display()}.")
                else:
                    messages.error(request, "Invalid appointment type.")
            elif action == 'confirm':
                appointment.status = 'confirmed'
                appointment.save()
                messages.success(request, "Appointment confirmed successfully.")
            elif action == 'cancel':
                appointment.status = 'cancelled'
                appointment.save()
                # Send cancellation notification
                from booking.notification_helpers import notify_appointment_cancelled
                notify_appointment_cancelled(appointment)
                messages.success(request, "Appointment cancelled.")
            elif action == 'complete':
                appointment.status = 'completed'
                appointment.save()
                # Send completion notification
                from booking.notification_helpers import notify_appointment_completed
                notify_appointment_completed(appointment)
                messages.success(request, "Appointment marked as completed.")
            elif action == 'assign_slot':
                slot_id = request.POST.get('time_slot')
                if slot_id:
                    try:
                        slot = TimeSlot.objects.get(id=slot_id, is_available=True)
                        appointment.time_slot = slot
                        # Set payment deadline when slot is assigned
                        appointment.payment_deadline = timezone.now() + timezone.timedelta(hours=48)
                        appointment.save()
                        messages.success(request, f"Time slot assigned: {slot.date} at {slot.start_time}. Payment due within 48 hours.")
                    except TimeSlot.DoesNotExist:
                        messages.error(request, "Selected time slot is not available.")
            elif action == 'verify_payment':
                appointment.payment_status = 'verified'
                appointment.payment_confirmed_by = request.user
                appointment.payment_confirmed_at = timezone.now()
                appointment.payment_notes = request.POST.get('payment_notes', '')
                # Don't auto-confirm yet - wait for time slot assignment
                appointment.save()
                # Send notification to patient
                from booking.notification_helpers import notify_payment_verified
                notify_payment_verified(appointment)
                messages.success(request, "Payment verified! Now please assign a time slot to confirm the appointment.")
            elif action == 'reject_payment':
                appointment.payment_status = 'failed'
                payment_notes = request.POST.get('payment_notes', 'Payment rejected by staff')
                appointment.payment_notes = payment_notes
                appointment.save()
                # Send rejection email and notification
                send_payment_rejected(appointment, reason=payment_notes)
                from booking.notification_helpers import notify_payment_rejected
                notify_payment_rejected(appointment, reason=payment_notes)
                messages.warning(request, "Payment rejected. Patient has been notified to retry.")
            else:
                messages.error(request, "Unknown action.")
        else:
            messages.error(request, "You don't have permission to perform this action. Staff access required.")
        
        return redirect('staff:appointment_detail', appointment_id=appointment.id)
    
    context = {
        'appointment': appointment,
        'available_slots': available_slots,
        'is_staff': user_is_staff,
    }
    
    return render(request, 'staff/appointment_detail.html', context)


@doctor_required
def video_consultation_list(request):
    """List all video consultations."""
    consultations = VideoConsultation.objects.order_by('-scheduled_date', '-scheduled_time')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        consultations = consultations.filter(status=status)
    
    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        consultations = consultations.filter(scheduled_date=date_filter)
    
    # Pagination
    paginator = Paginator(consultations, 20)
    page = request.GET.get('page', 1)
    consultations = paginator.get_page(page)
    
    context = {
        'consultations': consultations,
        'selected_status': status,
        'selected_date': date_filter,
    }
    
    return render(request, 'staff/video_consultation_list.html', context)


@doctor_required
def document_list(request):
    """Document management overview with patient grouping."""
    from django.db.models import Count, Q, Max
    
    # Get filter parameters
    verified_filter = request.GET.get('verified', '')
    type_filter = request.GET.get('type', '')
    patient_filter = request.GET.get('patient', '')
    
    # Get patients who have documents
    patients_with_docs = Patient.objects.annotate(
        doc_count=Count('uploads'),
        unverified_count=Count('uploads', filter=Q(uploads__is_verified=False)),
        last_upload=Max('uploads__uploaded_at')
    ).filter(doc_count__gt=0).order_by('-last_upload')
    
    # Apply patient search filter
    if patient_filter:
        patients_with_docs = patients_with_docs.filter(
            Q(user__email__icontains=patient_filter) |
            Q(full_name__icontains=patient_filter)
        )
    
    # Calculate stats
    total_documents = PortalUpload.objects.count()
    unverified_documents = PortalUpload.objects.filter(is_verified=False).count()
    verified_documents = PortalUpload.objects.filter(is_verified=True).count()
    patients_count = patients_with_docs.count()
    
    # Get recent documents for quick access
    recent_documents = PortalUpload.objects.select_related(
        'patient__user', 'verified_by'
    ).order_by('-uploaded_at')[:10]
    
    # Filter recent documents if filters applied
    if verified_filter == 'yes':
        recent_documents = recent_documents.filter(is_verified=True)
    elif verified_filter == 'no':
        recent_documents = recent_documents.filter(is_verified=False)
    
    if type_filter:
        recent_documents = recent_documents.filter(upload_type=type_filter)
    
    # Type choices
    type_choices = PortalUpload._meta.get_field('upload_type').choices
    
    # Pagination for patients
    paginator = Paginator(patients_with_docs, 15)
    page = request.GET.get('page', 1)
    patients_page = paginator.get_page(page)
    
    context = {
        'patients': patients_page,
        'recent_documents': recent_documents,
        'stats': {
            'total': total_documents,
            'unverified': unverified_documents,
            'verified': verified_documents,
            'patients_count': patients_count,
        },
        'type_choices': type_choices,
        'filters': {
            'verified': verified_filter,
            'type': type_filter,
            'patient': patient_filter,
        }
    }
    
    return render(request, 'staff/document_list.html', context)


@doctor_required
def patient_documents(request, patient_id):
    """View all documents for a specific patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    
    documents = PortalUpload.objects.filter(
        patient=patient
    ).select_related('verified_by').order_by('-uploaded_at')
    
    # Filter by verification status
    verified_filter = request.GET.get('verified', '')
    if verified_filter == 'yes':
        documents = documents.filter(is_verified=True)
    elif verified_filter == 'no':
        documents = documents.filter(is_verified=False)
    
    # Filter by type
    type_filter = request.GET.get('type', '')
    if type_filter:
        documents = documents.filter(upload_type=type_filter)
    
    # Stats for this patient
    stats = {
        'total': patient.uploads.count(),
        'verified': patient.uploads.filter(is_verified=True).count(),
        'unverified': patient.uploads.filter(is_verified=False).count(),
    }
    
    # Type choices
    type_choices = PortalUpload._meta.get_field('upload_type').choices
    
    context = {
        'patient': patient,
        'documents': documents,
        'stats': stats,
        'type_choices': type_choices,
        'filters': {
            'verified': verified_filter,
            'type': type_filter,
        }
    }
    
    return render(request, 'staff/patient_documents.html', context)


@doctor_required
def document_detail(request, document_id):
    """View and manage a specific document."""
    document = get_object_or_404(
        PortalUpload.objects.select_related('patient__user', 'verified_by'),
        id=document_id
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'verify':
            document.is_verified = True
            document.verified_by = request.user
            document.verified_at = timezone.now()
            document.save()
            
            # Notify patient about verification
            from portal.models import Notification
            Notification.objects.create(
                user=document.patient.user,
                notification_type='document_verified',
                title='Document Verified',
                message=f'Your {document.get_upload_type_display()} "{document.title}" has been verified by our medical team.',
                action_url='/portal/documents/'
            )
            
            messages.success(request, f"Document '{document.title}' has been verified.")
        
        elif action == 'unverify':
            document.is_verified = False
            document.verified_by = None
            document.verified_at = None
            document.save()
            messages.warning(request, f"Document '{document.title}' verification has been removed.")
        
        elif action == 'update_notes':
            # Staff can add notes/description
            document.description = request.POST.get('notes', '')
            document.save()
            messages.success(request, "Document notes updated.")
        
        return redirect('staff:document_detail', document_id=document_id)
    
    # Get other documents from same patient
    other_documents = PortalUpload.objects.filter(
        patient=document.patient
    ).exclude(id=document.id).order_by('-uploaded_at')[:5]
    
    context = {
        'document': document,
        'other_documents': other_documents,
    }
    
    return render(request, 'staff/document_detail.html', context)


@doctor_required
def verify_document(request, document_id):
    """Verify a patient document - doctors can do this."""
    document = get_object_or_404(PortalUpload, id=document_id)
    
    if request.method == 'POST':
        document.is_verified = True
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.save()
        
        # Notify patient about verification
        from portal.models import Notification
        Notification.objects.create(
            user=document.patient.user,
            notification_type='document_verified',
            title='Document Verified',
            message=f'Your {document.get_upload_type_display()} "{document.title}" has been verified by our medical team.',
            action_url='/portal/documents/'
        )
        
        messages.success(request, f"Document '{document.title}' has been verified.")
    
    # Redirect back to referring page or document list
    referer = request.META.get('HTTP_REFERER', '')
    if 'patient_documents' in referer or f'patients/{document.patient.id}' in referer:
        return redirect('staff:patient_documents', patient_id=document.patient.id)
    
    return redirect('staff:document_list')


@doctor_required
def download_document(request, document_id):
    """Download a patient document - serves file directly."""
    document = get_object_or_404(PortalUpload, id=document_id)
    
    try:
        # Get the file
        file = document.file
        
        # Determine content type
        content_type = document.mime_type or 'application/octet-stream'
        
        # Get filename
        filename = document.title or f"{document.get_upload_type_display()}_{document.id}"
        ext = file.name.split('.')[-1] if '.' in file.name else ''
        if ext and not filename.endswith(f'.{ext}'):
            filename = f"{filename}.{ext}"
        
        # Create response
        response = HttpResponse(file.read(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        messages.error(request, f"Could not download file: {str(e)}")
        return redirect('staff:document_detail', document_id=document_id)


@staff_required
def payment_list(request):
    """List all appointment payments - staff only."""
    # Get appointments with payment activity (not just pending with no action)
    appointments = Appointment.objects.exclude(
        payment_status='pending',
        payment_proof=''
    ).select_related('patient__user').order_by('-created_at')
    
    # Filter by payment status
    status = request.GET.get('status', '')
    if status:
        appointments = appointments.filter(payment_status=status)
    
    # Filter by payment method
    method = request.GET.get('method', '')
    if method:
        appointments = appointments.filter(payment_method=method)
    
    # Pagination
    paginator = Paginator(appointments, 20)
    page = request.GET.get('page', 1)
    appointments = paginator.get_page(page)
    
    # Calculate totals from Appointment model
    total_verified = Appointment.objects.filter(payment_status='verified').count()
    total_revenue = Appointment.objects.filter(payment_status='verified').aggregate(
        total=models.Sum('consultation_fee')
    )['total'] or 0
    pending_payments = Appointment.objects.filter(payment_status__in=['pending', 'submitted']).count()
    
    context = {
        'appointments': appointments,
        'selected_status': status,
        'selected_method': method,
        'total_verified': total_verified,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
    }
    
    return render(request, 'staff/payment_list.html', context)


@doctor_required
def calendar_view(request):
    """Calendar view of appointments - doctors see their schedule."""
    import calendar as cal
    from datetime import datetime
    
    today = timezone.now().date()
    
    # Get month from query params or use current month
    month_param = request.GET.get('month', '')
    if month_param:
        try:
            current_date = datetime.strptime(month_param + '-01', '%Y-%m-%d').date()
        except ValueError:
            current_date = today
    else:
        current_date = today
    
    # Calculate month boundaries
    month_start = current_date.replace(day=1)
    if current_date.month == 12:
        month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
    else:
        month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        next_month = current_date.replace(month=current_date.month + 1, day=1)
    
    if current_date.month == 1:
        prev_month = current_date.replace(year=current_date.year - 1, month=12, day=1)
    else:
        prev_month = current_date.replace(month=current_date.month - 1, day=1)
    
    # Get appointments for current month
    appointments = Appointment.objects.filter(
        time_slot__date__gte=month_start,
        time_slot__date__lte=month_end
    ).select_related('patient__user', 'time_slot')
    
    consultations = VideoConsultation.objects.filter(
        scheduled_date__gte=month_start,
        scheduled_date__lte=month_end
    )
    
    # Build events dictionary by date
    events_by_date = {}
    
    for apt in appointments:
        if apt.time_slot and apt.time_slot.date:
            date_key = apt.time_slot.date
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append({
                'type': 'appointment',
                'title': apt.patient.user.get_full_name() or apt.patient.user.email,
                'time': apt.time_slot.start_time.strftime('%H:%M') if apt.time_slot.start_time else '',
                'status': apt.status,
                'url': f'/staff/appointments/{apt.id}/',
            })
    
    for cons in consultations:
        if cons.scheduled_date:
            date_key = cons.scheduled_date
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append({
                'type': 'consultation',
                'title': cons.appointment.patient.user.get_full_name() or cons.appointment.patient.user.email if cons.appointment else 'Consultation',
                'time': cons.scheduled_time.strftime('%H:%M') if cons.scheduled_time else '',
                'status': cons.status,
                'url': f'/staff/video-consultations/{cons.id}/',
            })
    
    # Build calendar days
    month_calendar = cal.Calendar(firstweekday=0)  # Monday start
    calendar_days = []
    
    for date in month_calendar.itermonthdates(current_date.year, current_date.month):
        day_events = events_by_date.get(date, [])
        calendar_days.append({
            'date': date,
            'is_today': date == today,
            'is_current_month': date.month == current_date.month,
            'events': day_events[:3],  # Show max 3 events
            'event_count': len(day_events),
        })
    
    # Day names
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Upcoming events this month
    upcoming_events = []
    for apt in appointments:
        if apt.time_slot and apt.time_slot.date and apt.time_slot.date >= today:
            upcoming_events.append({
                'type': 'appointment',
                'title': apt.patient.user.get_full_name() or apt.patient.user.email,
                'description': f'{apt.get_appointment_type_display()} - {apt.get_status_display()}',
                'date': apt.time_slot.date,
                'time': apt.time_slot.start_time.strftime('%H:%M') if apt.time_slot.start_time else '',
                'url': f'/staff/appointments/{apt.id}/',
            })
    for cons in consultations:
        if cons.scheduled_date and cons.scheduled_date >= today:
            patient_name = ''
            if cons.appointment:
                patient_name = cons.appointment.patient.user.get_full_name() or cons.appointment.patient.user.email
            upcoming_events.append({
                'type': 'consultation',
                'title': patient_name or 'Video Consultation',
                'description': f'Video Consultation - {cons.get_status_display()}',
                'date': cons.scheduled_date,
                'time': cons.scheduled_time.strftime('%H:%M') if cons.scheduled_time else '',
                'url': f'/staff/video-consultations/{cons.id}/',
            })
    
    # Sort by date
    upcoming_events.sort(key=lambda x: (x['date'], x['time']))
    
    context = {
        'appointments': appointments,
        'consultations': consultations,
        'today': today,
        'current_date': current_date,
        'month_start': month_start,
        'month_end': month_end,
        'prev_month': prev_month,
        'next_month': next_month,
        'calendar_days': calendar_days,
        'day_names': day_names,
        'upcoming_events': upcoming_events[:10],  # Limit to 10
    }
    
    return render(request, 'staff/calendar.html', context)


@doctor_required
def time_slot_management(request):
    """Manage available time slots."""
    today = timezone.now().date()
    
    # Get upcoming time slots
    time_slots = TimeSlot.objects.filter(date__gte=today).order_by('date', 'start_time')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            date = request.POST.get('date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            slot_type = request.POST.get('slot_type', 'consultation')
            max_bookings = int(request.POST.get('max_bookings', 1))
            
            TimeSlot.objects.create(
                date=date,
                start_time=start_time,
                end_time=end_time,
                slot_type=slot_type,
                max_bookings=max_bookings,
                is_available=True
            )
            messages.success(request, "Time slot created successfully.")
        
        elif action == 'toggle':
            slot_id = request.POST.get('slot_id')
            slot = get_object_or_404(TimeSlot, id=slot_id)
            slot.is_available = not slot.is_available
            slot.save()
            status = "enabled" if slot.is_available else "disabled"
            messages.success(request, f"Time slot {status}.")
        
        elif action == 'delete':
            slot_id = request.POST.get('slot_id')
            slot = get_object_or_404(TimeSlot, id=slot_id)
            if slot.current_bookings == 0:
                slot.delete()
                messages.success(request, "Time slot deleted.")
            else:
                messages.error(request, "Cannot delete slot with existing bookings.")
        
        return redirect('staff:time_slots')
    
    # Pagination
    paginator = Paginator(time_slots, 20)
    page = request.GET.get('page', 1)
    time_slots = paginator.get_page(page)
    
    context = {
        'time_slots': time_slots,
        'today': today,
    }
    
    return render(request, 'staff/time_slots.html', context)


# =============================================================================
# CONSENT MANAGEMENT VIEWS
# =============================================================================

@doctor_required
def consent_list(request):
    """View all patient consents with filtering."""
    consents = ConsentRecord.objects.select_related(
        'patient', 'patient__user', 'reviewed_by', 'related_appointment',
        'revocation_reviewed_by'
    ).order_by('-granted_at')
    
    # Filters
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    patient_filter = request.GET.get('patient', '')
    reviewed_filter = request.GET.get('reviewed', '')
    
    if status_filter == 'active':
        consents = consents.filter(granted=True, revoked_at__isnull=True, revocation_requested_at__isnull=True)
    elif status_filter == 'revoked':
        consents = consents.filter(revoked_at__isnull=False)
    elif status_filter == 'denied':
        consents = consents.filter(granted=False, revoked_at__isnull=True)
    elif status_filter == 'revocation_pending':
        consents = consents.filter(revocation_requested_at__isnull=False, revoked_at__isnull=True)
    
    if type_filter:
        consents = consents.filter(consent_type=type_filter)
    
    if patient_filter:
        consents = consents.filter(
            Q(patient__user__email__icontains=patient_filter) |
            Q(patient__full_name__icontains=patient_filter)
        )
    
    if reviewed_filter == 'pending':
        consents = consents.filter(reviewed_by__isnull=True)
    elif reviewed_filter == 'reviewed':
        consents = consents.filter(reviewed_by__isnull=False)
    
    # Pagination
    paginator = Paginator(consents, 20)
    page = request.GET.get('page', 1)
    consents = paginator.get_page(page)
    
    # Stats
    stats = {
        'total': ConsentRecord.objects.count(),
        'active': ConsentRecord.objects.filter(granted=True, revoked_at__isnull=True, revocation_requested_at__isnull=True).count(),
        'pending_review': ConsentRecord.objects.filter(reviewed_by__isnull=True, granted=True).count(),
        'revocation_pending': ConsentRecord.objects.filter(revocation_requested_at__isnull=False, revoked_at__isnull=True).count(),
        'required_pending': ConsentRecord.objects.filter(
            consent_type__in=ConsentRecord.REQUIRED_FOR_SURGERY,
            reviewed_by__isnull=True,
            granted=True
        ).count(),
    }
    
    context = {
        'consents': consents,
        'consent_types': ConsentRecord.CONSENT_TYPE_CHOICES,
        'stats': stats,
        'filters': {
            'status': status_filter,
            'type': type_filter,
            'patient': patient_filter,
            'reviewed': reviewed_filter,
        }
    }
    
    return render(request, 'staff/consent_list.html', context)


@doctor_required
def consent_detail(request, consent_id):
    """View and review a specific consent record."""
    consent = get_object_or_404(
        ConsentRecord.objects.select_related(
            'patient', 'patient__user', 'reviewed_by', 'related_appointment',
            'revocation_reviewed_by'
        ),
        id=consent_id
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'review':
            notes = request.POST.get('staff_notes', '')
            consent.mark_reviewed(staff_user=request.user, notes=notes)
            messages.success(request, "Consent has been marked as reviewed.")
        
        elif action == 'approve_revocation':
            # Approve the revocation request
            consent.approve_revocation(staff_user=request.user)
            messages.success(request, "Revocation request has been approved. The consent is now revoked.")
            
            # Notify patient about revocation approval
            from portal.models import Notification
            Notification.objects.create(
                user=consent.patient.user,
                notification_type='consent_revoked',
                title='Revocation Approved',
                message=f'Your request to revoke "{consent.get_consent_type_display()}" has been approved by our medical team.',
                action_url='/portal/consents/'
            )
        
        return redirect('staff:consent_detail', consent_id=consent_id)
    
    # Get other consents from same patient
    patient_consents = ConsentRecord.objects.filter(
        patient=consent.patient
    ).exclude(id=consent.id).order_by('-granted_at')[:5]
    
    # Check surgery readiness
    surgery_status = ConsentRecord.check_surgery_ready(consent.patient)
    
    context = {
        'consent': consent,
        'patient_consents': patient_consents,
        'surgery_status': surgery_status,
    }
    
    return render(request, 'staff/consent_detail.html', context)


@doctor_required
def patient_consents(request, patient_id):
    """View all consents for a specific patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get all consents for this patient
    consents = ConsentRecord.objects.filter(patient=patient).order_by('-granted_at')
    
    # Get consent status using the model method
    consent_status = ConsentRecord.get_patient_consent_status(patient)
    
    # Check surgery readiness
    surgery_status = ConsentRecord.check_surgery_ready(patient)
    
    # Required consent types with labels
    required_consent_types = [
        (ct[0], ct[1]) for ct in ConsentRecord.CONSENT_TYPE_CHOICES 
        if ct[0] in ConsentRecord.REQUIRED_FOR_SURGERY
    ]
    
    context = {
        'patient': patient,
        'consents': consents,
        'consent_status': consent_status,
        'surgery_status': surgery_status,
        'required_consent_types': required_consent_types,
    }
    
    return render(request, 'staff/patient_consents.html', context)

