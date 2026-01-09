# Fix migration for patient reviews - correct procedure_type values

from django.db import migrations


def fix_procedure_types(apps, schema_editor):
    PatientReview = apps.get_model('cms', 'PatientReview')
    
    # Fix procedure types to use valid choices
    PatientReview.objects.filter(patient_initials='M.K.').update(procedure_type='lon', height_gained='8cm (Femur)')
    PatientReview.objects.filter(patient_initials='J.R.').update(procedure_type='internal', height_gained='6cm (Tibia)')
    PatientReview.objects.filter(patient_initials='A.S.').update(procedure_type='lon', height_gained='12cm (Femur + Tibia)')
    PatientReview.objects.filter(patient_initials='S.T.').update(procedure_type='internal', height_gained='7cm (Femur)')
    PatientReview.objects.filter(patient_initials='R.M.').update(procedure_type='internal', height_gained='8cm (Femur)')
    PatientReview.objects.filter(patient_initials='D.L.').update(procedure_type='lon', height_gained='5cm (Tibia)')


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_seed_patient_reviews'),
    ]

    operations = [
        migrations.RunPython(fix_procedure_types, migrations.RunPython.noop),
    ]
