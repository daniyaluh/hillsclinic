from django import forms
from django.utils import timezone
from .models import Patient, Appointment, TimeSlot
import pytz


class ConsultationBookingForm(forms.Form):
    """Form for booking a consultation ($10 fee required after booking)."""
    
    # Appointment Type - What the patient is booking for
    appointment_type = forms.ChoiceField(
        choices=[
            ('consultation', 'First Consultation - New patient inquiry'),
            ('follow_up', 'Follow-up - I have consulted before'),
            ('pre_op', 'Pre-operative - Surgery preparation discussion'),
            ('post_op', 'Post-operative - Recovery check-in'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'mr-2 text-teal-600 focus:ring-teal-500',
        }),
        initial='consultation'
    )
    
    # Personal Information
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'Your full name',
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'your.email@example.com',
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': '+92 301 5943329',
        })
    )
    
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'Your country',
        })
    )
    
    # Timezone for scheduling
    patient_timezone = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'x-model': 'selectedTimezone',
        })
    )
    
    consultation_type = forms.ChoiceField(
        choices=[
            ('video', 'Video Call (Zoom/WhatsApp)'),
            ('phone', 'Phone Call'),
            ('whatsapp', 'WhatsApp Chat'),
            ('in_clinic', 'In-Person at Clinic'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'mr-2 text-teal-600 focus:ring-teal-500',
        })
    )
    
    # Medical information
    current_height = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'e.g., 165 cm or 5\'5"',
        })
    )
    
    desired_height_gain = forms.ChoiceField(
        choices=[
            ('3-5', '3-5 cm'),
            ('5-8', '5-8 cm'),
            ('8-10', '8-10 cm'),
            ('10+', '10+ cm'),
            ('unsure', 'Not sure yet'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
        })
    )
    
    procedure_interest = forms.ChoiceField(
        choices=[
            ('ilizarov', 'Ilizarov Method'),
            ('lon', 'LON Method'),
            ('internal', 'Internal Nail (Precice/STRYDE)'),
            ('unsure', 'Need guidance'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
        })
    )
    
    medical_conditions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'Any relevant medical conditions (optional)',
            'rows': 3,
        })
    )
    
    questions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'Any specific questions you would like answered?',
            'rows': 4,
        })
    )
    
    # How did you hear about us
    referral_source = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select an option'),
            ('google', 'Google Search'),
            ('youtube', 'YouTube'),
            ('instagram', 'Instagram'),
            ('facebook', 'Facebook'),
            ('tiktok', 'TikTok'),
            ('friend', 'Friend/Family'),
            ('forum', 'Online Forum'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
        })
    )
    
    # Consent
    privacy_consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded',
        })
    )
    
    marketing_consent = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded',
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate timezone choices
        common_timezones = [
            'Asia/Karachi',  # Pakistan
            'UTC',
            'US/Eastern',
            'US/Pacific',
            'Europe/London',
            'Europe/Paris',
            'Europe/Berlin',
            'Asia/Dubai',
            'Asia/Riyadh',
            'Asia/Kolkata',
            'Asia/Singapore',
            'Australia/Sydney',
            'America/New_York',
            'America/Los_Angeles',
            'America/Chicago',
        ]
        self.fields['patient_timezone'].choices = [
            (tz, tz.replace('_', ' ')) for tz in common_timezones
        ]


class ContactForm(forms.Form):
    """Simple contact form for general inquiries."""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'Your name',
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'your.email@example.com',
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'Subject of your message',
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'Your message...',
            'rows': 6,
        })
    )
    
    privacy_consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded',
        })
    )


class QuickCallbackForm(forms.Form):
    """Quick callback request form (minimal fields)."""
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'Your phone number',
        })
    )
    
    best_time = forms.ChoiceField(
        choices=[
            ('asap', 'As soon as possible'),
            ('morning', 'Morning'),
            ('afternoon', 'Afternoon'),
            ('evening', 'Evening'),
        ],
        widget=forms.Select(attrs={
            'class': 'px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
        })
    )


class VideoConsultationForm(forms.Form):
    """Form for booking a paid video consultation."""
    
    # Personal Information
    patient_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'Your full name',
        })
    )
    
    patient_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'your.email@example.com',
        })
    )
    
    patient_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': '+92 301 5943329',
        })
    )
    
    patient_country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'Your country',
        })
    )
    
    patient_timezone = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
        })
    )
    
    # Scheduling
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
        })
    )
    
    scheduled_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
        })
    )
    
    # Medical Information
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'Briefly describe the reason for your consultation...',
            'rows': 3,
        })
    )
    
    current_height = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'e.g., 165 cm or 5\'5"',
        })
    )
    
    desired_height_gain = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'e.g., 6-8 cm',
        })
    )
    
    procedure_interest = forms.ChoiceField(
        choices=[
            ('undecided', 'Not sure yet'),
            ('ilizarov', 'Ilizarov (External Fixator)'),
            ('internal', 'Internal Lengthening Nail'),
            ('lon', 'LON Method'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
        })
    )
    
    medical_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'Any medical conditions, previous surgeries, or medications we should know about...',
            'rows': 3,
        })
    )
    
    # Consent
    terms_consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded',
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate timezone choices
        common_timezones = [
            ('UTC', 'UTC'),
            ('Asia/Karachi', 'Pakistan (PKT)'),
            ('Asia/Dubai', 'Dubai (GST)'),
            ('Asia/Riyadh', 'Saudi Arabia (AST)'),
            ('Europe/London', 'London (GMT/BST)'),
            ('Europe/Paris', 'Paris (CET)'),
            ('America/New_York', 'New York (EST)'),
            ('America/Los_Angeles', 'Los Angeles (PST)'),
            ('Asia/Tokyo', 'Tokyo (JST)'),
            ('Australia/Sydney', 'Sydney (AEST)'),
        ]
        self.fields['patient_timezone'].choices = common_timezones
    
    def clean_scheduled_date(self):
        date = self.cleaned_data['scheduled_date']
        from django.utils import timezone as tz
        if date < tz.now().date():
            raise forms.ValidationError('Please select a future date.')
        return date
