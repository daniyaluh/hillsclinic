# Generated data migration for patient reviews

from django.db import migrations


def add_patient_reviews(apps, schema_editor):
    PatientReview = apps.get_model('cms', 'PatientReview')
    
    reviews = [
        {
            'patient_initials': 'M.K.',
            'country': 'United States',
            'age': 28,
            'procedure_type': 'LON (Femur)',
            'height_gained': '8cm',
            'surgery_year': 2025,
            'review_text': 'Dr. Khaqan and his team provided exceptional care throughout my entire journey. The results exceeded my expectations. I gained 8cm and my confidence has never been higher. The staff was incredibly supportive and made me feel at home in Pakistan.',
            'rating': 5,
            'is_featured': True,
            'is_published': True,
            'display_order': 1
        },
        {
            'patient_initials': 'J.R.',
            'country': 'United Kingdom',
            'age': 32,
            'procedure_type': 'Precice Stryde (Tibia)',
            'height_gained': '6cm',
            'surgery_year': 2025,
            'review_text': 'I researched clinics worldwide for over 2 years before choosing Hills Clinic. Best decision I ever made. The precision of the Stryde nail and Dr. Khaqans expertise gave me exactly the results I wanted. Recovery was smoother than expected.',
            'rating': 5,
            'is_featured': True,
            'is_published': True,
            'display_order': 2
        },
        {
            'patient_initials': 'A.S.',
            'country': 'Germany',
            'age': 25,
            'procedure_type': 'LON (Femur + Tibia)',
            'height_gained': '12cm',
            'surgery_year': 2024,
            'review_text': 'After my combined femur and tibia lengthening, I am a completely different person. The physical therapy team was amazing and helped me regain full mobility. 12cm taller and living my best life. Thank you Hills Clinic!',
            'rating': 5,
            'is_featured': True,
            'is_published': True,
            'display_order': 3
        },
        {
            'patient_initials': 'S.T.',
            'country': 'Australia',
            'age': 30,
            'procedure_type': 'Internal Nail (Femur)',
            'height_gained': '7cm',
            'surgery_year': 2025,
            'review_text': 'Coming from Australia, I was nervous about having surgery abroad. But from the airport pickup to the final follow-up, everything was seamless. Hamza coordinated everything perfectly. The hospital facilities are world-class.',
            'rating': 5,
            'is_featured': False,
            'is_published': True,
            'display_order': 4
        },
        {
            'patient_initials': 'R.M.',
            'country': 'Canada',
            'age': 27,
            'procedure_type': 'Precice 2 (Femur)',
            'height_gained': '8cm',
            'surgery_year': 2024,
            'review_text': 'The magnetic lengthening with Precice 2 was incredible - no external fixator, minimal scarring. Dr. Khaqan explained every step clearly. I appreciated the honest timeline expectations. Now 8cm taller with full athletic ability restored.',
            'rating': 5,
            'is_featured': False,
            'is_published': True,
            'display_order': 5
        },
        {
            'patient_initials': 'D.L.',
            'country': 'Netherlands',
            'age': 24,
            'procedure_type': 'LON (Tibia)',
            'height_gained': '5cm',
            'surgery_year': 2025,
            'review_text': 'As someone who was very anxious about surgery, the team at Hills Clinic put me completely at ease. Dr. Ayesha and the physiotherapy program were exceptional. Five centimeters may not sound like much but it changed my life.',
            'rating': 5,
            'is_featured': False,
            'is_published': True,
            'display_order': 6
        }
    ]
    
    for r in reviews:
        PatientReview.objects.get_or_create(
            patient_initials=r['patient_initials'],
            country=r['country'],
            defaults=r
        )


def remove_patient_reviews(apps, schema_editor):
    PatientReview = apps.get_model('cms', 'PatientReview')
    PatientReview.objects.filter(
        patient_initials__in=['M.K.', 'J.R.', 'A.S.', 'S.T.', 'R.M.', 'D.L.']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0004_add_patient_review_snippet'),
    ]

    operations = [
        migrations.RunPython(add_patient_reviews, remove_patient_reviews),
    ]
