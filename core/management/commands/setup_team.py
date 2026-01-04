"""
Management command to set up the lead surgeon data.
Run: python manage.py setup_team
"""
from django.core.management.base import BaseCommand
from core.models import Doctor


class Command(BaseCommand):
    help = 'Creates the lead surgeon profile for Hills Clinic'

    def handle(self, *args, **options):
        self.stdout.write('Setting up Hills Clinic lead surgeon...')
        
        # First, remove all existing doctors
        deleted_count = Doctor.objects.all().delete()[0]
        if deleted_count:
            self.stdout.write(f'Removed {deleted_count} existing doctor records')
        
        doctors_data = [
            {
                'name': 'Dr. Khaqan Jahangir Janjua',
                'slug': 'dr-khaqan-jahangir-janjua',
                'title': 'MBBS, FRCS, FIAS, FICS',
                'specialty': 'orthopedic-surgeon',
                'role': 'Lead Surgeon',
                'short_bio': 'Lead surgeon with 40 years of experience in orthopedic and trauma surgery, specializing in limb lengthening procedures.',
                'bio': '''Dr. Khaqan Jahangir Janjua is Pakistan's premier limb lengthening specialist with over 40 years of experience in orthopedic and trauma surgery. As the lead surgeon at Hills Clinic, he has transformed countless lives through his expertise in limb lengthening procedures.

Dr. Janjua completed his MBBS followed by a Graduate Diploma in Surgery and obtained his FRCS (Fellow of the Royal College of Surgeons). He further enhanced his qualifications with FIAS (Fellow of the International Association of Surgeons), FICS (Fellow of the International College of Surgeons), and a Trauma Fellowship.

His advanced training includes MMed Sci in Trauma Surgery, CCD (Certification in Clinical Densitometry), ALTS (Advanced Life Trauma Support), ALS (Advanced Life Support), and PALS (Pediatric Advanced Life Support).

With four decades of surgical experience and hundreds of successful limb lengthening procedures, Dr. Janjua brings unparalleled expertise to every case. His commitment to patient care, combined with his surgical precision, has made Hills Clinic a leading destination for patients from over 40 countries seeking limb lengthening surgery.

Dr. Janjua is known for his compassionate approach to patient care, ensuring that every individual receives personalized attention throughout their transformative journey.''',
                'education': 'MBBS\nGraduate Diploma in Surgery\nFRCS (Fellow of the Royal College of Surgeons)\nTrauma Fellowship\nMMed Sci (Trauma Surgery)',
                'certifications': 'FIAS (Fellow of the International Association of Surgeons)\nFICS (Fellow of the International College of Surgeons)\nCCD (Clinical Densitometry Certification)\nALTS (Advanced Life Trauma Support)\nALS (Advanced Life Support)\nPALS (Pediatric Advanced Life Support)',
                'experience_years': 40,
                'languages': 'English, Urdu',
                'email': 'dr.khaqan@hillsclinic.com',
                'is_featured': True,
                'order': 1,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for doctor_data in doctors_data:
            doctor, created = Doctor.objects.update_or_create(
                slug=doctor_data['slug'],
                defaults=doctor_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {doctor.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'  Updated: {doctor.name}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Lead surgeon setup complete!'))
        self.stdout.write(f'  Total: {Doctor.objects.count()} surgeon(s) in database')
