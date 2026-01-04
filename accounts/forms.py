"""
Custom forms for accounts app.
"""

from django import forms
from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    """Custom signup form with name field."""
    
    full_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Full Name',
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Move full_name to be the first field
        field_order = ['full_name', 'email', 'password1', 'password2']
        self.order_fields(field_order)
    
    def save(self, request):
        user = super().save(request)
        
        # Parse name and save to user
        full_name = self.cleaned_data.get('full_name', '').strip()
        if full_name:
            name_parts = full_name.split()
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            user.save()
            
            # Also save to patient profile if it exists
            if hasattr(user, 'patient_profile'):
                user.patient_profile.full_name = full_name
                user.patient_profile.save()
        
        return user
