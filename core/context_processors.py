"""
Context processors for Hills Clinic.

Makes site-wide settings available to all templates.
"""

from django.conf import settings
from django.utils.translation import get_language


def site_settings(request):
    """Add site configuration to template context."""
    return {
        'WHATSAPP_NUMBER': getattr(settings, 'HILLS_CLINIC_WHATSAPP', '+923015943329'),
        'CLINIC_EMAIL': getattr(settings, 'HILLS_CLINIC_EMAIL', 'info@hillsclinic.com'),
        'CLINIC_PHONE': getattr(settings, 'HILLS_CLINIC_PHONE', '+92-42-35761234'),
        'CLINIC_ADDRESS': getattr(settings, 'HILLS_CLINIC_ADDRESS', 'Hills Clinic, DHA Phase 5, Lahore, Pakistan'),
        'CLINIC_NAME': getattr(settings, 'WAGTAIL_SITE_NAME', 'Hills Clinic'),
    }


def language_context(request):
    """Add language and RTL context to templates."""
    current_language = get_language() or 'en'
    rtl_languages = getattr(settings, 'RTL_LANGUAGES', ['ar', 'fa'])
    languages_setting = getattr(settings, 'LANGUAGES', [])
    
    # Convert LANGUAGES tuple to list of dicts for template use
    available_languages = [
        {'code': code, 'name': name} 
        for code, name in languages_setting
    ]
    
    # Get the name of the current language
    current_language_name = 'English'
    for lang in available_languages:
        if lang['code'] == current_language[:2]:
            current_language_name = lang['name']
            break
    
    return {
        'CURRENT_LANGUAGE': current_language_name,
        'CURRENT_LANGUAGE_CODE': current_language[:2],
        'IS_RTL': current_language[:2] in rtl_languages,
        'AVAILABLE_LANGUAGES': available_languages,
        'RTL_LANGUAGES': rtl_languages,
    }
