"""
Portal app forms for Hills Clinic.

Forms for patient portal functionality:
- Document uploads
- Consent management
- Profile updates
- Appointment booking
"""

from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from PIL import Image
import os

from .models import PortalUpload, ConsentRecord
from booking.models import Patient, TimeSlot, Appointment


class PaymentProofForm(forms.Form):
    """Form for uploading payment proof screenshot."""
    
    PAYMENT_METHOD_CHOICES = [
        ('easypaisa', 'EasyPaisa'),
        ('jazzcash', 'JazzCash'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
        })
    )
    
    payment_proof = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100',
            'accept': 'image/*'
        }),
        help_text='Upload a screenshot of your payment confirmation'
    )
    
    def clean_payment_proof(self):
        proof = self.cleaned_data.get('payment_proof')
        if proof:
            # Check file size (max 5MB)
            max_size = 5 * 1024 * 1024
            if proof.size > max_size:
                raise forms.ValidationError('Image size must be less than 5MB.')
            
            # Validate it's an image
            try:
                img = Image.open(proof)
                img.verify()
                proof.seek(0)
            except Exception:
                raise forms.ValidationError('Invalid image file. Please upload a valid image.')
        return proof


class DocumentUploadForm(forms.ModelForm):
    """Form for uploading patient documents."""
    
    class Meta:
        model = PortalUpload
        fields = ['upload_type', 'file', 'title', 'description']
        widgets = {
            'upload_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            }),
            'file': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100',
                'accept': '.pdf,.jpg,.jpeg,.png,.gif,.doc,.docx,.dcm'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': 'e.g., Left Leg X-Ray - Front View'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'rows': 3,
                'placeholder': 'Any additional details about this document...'
            }),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            max_size = 10 * 1024 * 1024  # 10MB in bytes
            if file.size > max_size:
                raise forms.ValidationError('File size must be less than 10MB.')
            
            # Validate file extension
            ext = os.path.splitext(file.name)[1].lower()
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.dcm']
            if ext not in allowed_extensions:
                raise forms.ValidationError(f'File type not allowed. Allowed: {", ".join(allowed_extensions)}')
            
            # For images, validate they can be opened
            if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                try:
                    img = Image.open(file)
                    img.verify()
                    file.seek(0)  # Reset file pointer after verify
                except Exception:
                    raise forms.ValidationError('Invalid image file. Please upload a valid image.')
        return file


class ProfilePictureForm(forms.ModelForm):
    """Form for uploading profile picture."""
    
    class Meta:
        model = Patient
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'profile-picture-input'
            })
        }
    
    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Check file size (max 5MB)
            max_size = 5 * 1024 * 1024
            if picture.size > max_size:
                raise forms.ValidationError('Image size must be less than 5MB.')
            
            # Validate it's an image
            try:
                img = Image.open(picture)
                img.verify()
                picture.seek(0)
                
                # Check dimensions
                img = Image.open(picture)
                if img.width > 2000 or img.height > 2000:
                    raise forms.ValidationError('Image dimensions should not exceed 2000x2000 pixels.')
                picture.seek(0)
            except Exception as e:
                if 'Image' not in str(e):
                    raise forms.ValidationError('Invalid image file. Please upload a valid image.')
                raise
        return picture


class ConsentForm(forms.Form):
    """Form for granting/updating consent."""
    
    # Note: consent_type is passed via URL, not form field
    
    granted = forms.ChoiceField(
        choices=[('True', 'Grant'), ('', 'Deny')],
        required=False,
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio text-teal-600 focus:ring-teal-500'
        })
    )
    
    signature = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'placeholder': 'Type your full legal name as signature'
        })
    )
    
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-5 w-5 text-teal-600 rounded focus:ring-teal-500'
        }),
        label='I have read and understood the consent agreement'
    )
    
    def clean_granted(self):
        """Convert string value to boolean."""
        value = self.cleaned_data.get('granted')
        return value == 'True'


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating patient profile information."""
    
    class Meta:
        model = Patient
        fields = [
            'phone_number', 'whatsapp_number', 'date_of_birth', 'gender',
            'country', 'city', 'timezone', 'preferred_language',
            'current_height', 'desired_height_gain', 'medical_conditions',
            'medications', 'allergies', 'interested_in_procedure'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': '+92 301 5943329'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': '+92 301 5943329'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': 'Pakistan'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': 'Karachi'
            }),
            'timezone': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            }, choices=[
                ('Asia/Karachi', 'Pakistan (PKT)'),
                ('Asia/Dubai', 'UAE (GST)'),
                ('Asia/Riyadh', 'Saudi Arabia (AST)'),
                ('Europe/London', 'UK (GMT/BST)'),
                ('America/New_York', 'US Eastern (EST/EDT)'),
                ('America/Los_Angeles', 'US Pacific (PST/PDT)'),
                ('Asia/Kolkata', 'India (IST)'),
                ('Europe/Berlin', 'Central Europe (CET/CEST)'),
            ]),
            'preferred_language': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            }),
            'current_height': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': '165',
                'step': '0.01'
            }),
            'desired_height_gain': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': '8',
                'step': '0.01'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'rows': 3,
                'placeholder': 'List any pre-existing medical conditions...'
            }),
            'medications': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'rows': 3,
                'placeholder': 'List current medications...'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'rows': 3,
                'placeholder': 'List any known allergies...'
            }),
            'interested_in_procedure': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            }),
        }
    
    def clean_current_height(self):
        height = self.cleaned_data.get('current_height')
        if height and (height < 100 or height > 250):
            raise forms.ValidationError('Height must be between 100cm and 250cm.')
        return height
    
    def clean_desired_height_gain(self):
        gain = self.cleaned_data.get('desired_height_gain')
        if gain and (gain < 2 or gain > 20):
            raise forms.ValidationError('Height gain must be between 2cm and 20cm.')
        return gain


class ExtendedProfileForm(forms.ModelForm):
    """Extended profile form with all medical fields including emergency contact."""
    
    class Meta:
        model = Patient
        fields = [
            'full_name', 'profile_picture', 'phone_number', 'whatsapp_number', 'date_of_birth', 'gender',
            'country', 'city', 'timezone', 'preferred_language',
            'current_height', 'desired_height_gain', 'weight', 'blood_type',
            'medical_conditions', 'medications', 'allergies', 'interested_in_procedure',
            'emergency_contact_name', 'emergency_contact_relation', 'emergency_contact_phone'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': 'Enter your full name'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'profile-picture-input'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': '+92 301 5943329'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': '+92 301 5943329'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': 'Pakistan'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': 'Karachi'
            }),
            'timezone': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            }, choices=[
                ('Asia/Karachi', 'Pakistan (PKT)'),
                ('Asia/Dubai', 'UAE (GST)'),
                ('Asia/Riyadh', 'Saudi Arabia (AST)'),
                ('Europe/London', 'UK (GMT/BST)'),
                ('America/New_York', 'US Eastern (EST/EDT)'),
                ('America/Los_Angeles', 'US Pacific (PST/PDT)'),
                ('Asia/Kolkata', 'India (IST)'),
                ('Europe/Berlin', 'Central Europe (CET/CEST)'),
            ]),
            'preferred_language': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            }),
            'current_height': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': '165',
                'step': '0.01'
            }),
            'desired_height_gain': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': '8',
                'step': '0.01'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': '70',
                'step': '0.1'
            }),
            'blood_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'rows': 3,
                'placeholder': 'List any pre-existing medical conditions...'
            }),
            'medications': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'rows': 3,
                'placeholder': 'List current medications...'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'rows': 3,
                'placeholder': 'List any known allergies...'
            }),
            'interested_in_procedure': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': 'Full name of emergency contact'
            }),
            'emergency_contact_relation': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': 'e.g., Spouse, Parent, Sibling'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
                'placeholder': '+92 301 5943329'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional except none (all are profile enhancements)
        for field_name in self.fields:
            self.fields[field_name].required = False


class AppointmentBookingForm(forms.Form):
    """Form for booking appointments from the portal."""
    
    appointment_type = forms.ChoiceField(
        choices=[
            ('consultation', 'Initial Consultation'),
            ('follow_up', 'Follow-up'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio text-teal-600 focus:ring-teal-500'
        })
    )
    
    preferred_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'type': 'date'
        })
    )
    
    time_slot = forms.ModelChoiceField(
        queryset=TimeSlot.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500',
            'rows': 3,
            'placeholder': 'Any specific concerns or questions for the doctor...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        date = kwargs.pop('date', None)
        super().__init__(*args, **kwargs)
        
        if date:
            # Get available time slots for the selected date
            self.fields['time_slot'].queryset = TimeSlot.objects.filter(
                date=date,
                is_available=True
            ).exclude(
                appointments__status__in=['confirmed', 'pending']
            )

