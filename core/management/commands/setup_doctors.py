"""
Django management command to set up initial doctors/team members.
"""
from django.core.management.base import BaseCommand
from core.models import Doctor


class Command(BaseCommand):
    help = 'Creates initial doctor and support team members'

    def handle(self, *args, **options):
        # Check if doctors already exist
        if Doctor.objects.exists():
            self.stdout.write(self.style.WARNING("Doctors already exist. Skipping..."))
            return
        
        # Create Lead Surgeon
        lead_surgeon = Doctor.objects.create(
            name="Dr. Khaqan Jahangir Janjua",
            slug="dr-khaqan-jahangir-janjua",
            title="MBBS, FCPS (Ortho), FICS",
            specialty="orthopedic-surgeon",
            role="Lead Surgeon & Director",
            bio="""Dr. Khaqan Jahangir Janjua is Pakistan's leading limb lengthening surgeon with over 40 years of experience in orthopedic surgery. He trained at some of the world's most prestigious medical institutions and has performed over 500 successful limb lengthening procedures.

His expertise spans all major limb lengthening techniques including the Ilizarov method, LON (Lengthening Over Nail), and the latest internal magnetic nail technology. Dr. Janjua is known for his meticulous surgical technique and compassionate patient care.

He has treated patients from over 20 countries and continues to advance the field through ongoing research and training.""",
            short_bio="Pakistan's premier limb lengthening surgeon with 40+ years of experience and 500+ successful procedures.",
            education="""MBBS - King Edward Medical University, Lahore
FCPS (Orthopedic Surgery) - College of Physicians & Surgeons Pakistan
Fellowship in Ilizarov Technique - Russia
Advanced Training in Limb Lengthening - Germany""",
            certifications="""Fellow, College of Physicians & Surgeons Pakistan
Fellow, International College of Surgeons
Member, Pakistan Orthopedic Association
Member, AO Foundation""",
            experience_years=40,
            languages="English, Urdu, Punjabi",
            is_featured=True,
            is_active=True,
            order=1
        )
        self.stdout.write(self.style.SUCCESS(f"Created: {lead_surgeon.name}"))
        
        # Create Support Staff 1 - Patient Coordinator
        coordinator = Doctor.objects.create(
            name="Ayesha Khan",
            slug="ayesha-khan",
            title="MBA, Healthcare Management",
            specialty="patient-coordinator",
            role="International Patient Coordinator",
            bio="""Ayesha Khan serves as the International Patient Coordinator at Hills Clinic, ensuring a seamless experience for patients traveling from abroad. She handles all aspects of patient coordination including visa assistance, airport pickup, accommodation arrangements, and communication throughout the treatment journey.

With her background in healthcare management and fluency in English and Urdu, Ayesha has helped hundreds of international patients navigate their limb lengthening journey with confidence and ease.""",
            short_bio="Dedicated to making your international medical journey smooth and stress-free.",
            education="MBA in Healthcare Management - LUMS",
            certifications="Certified Medical Tourism Professional",
            experience_years=8,
            languages="English, Urdu, Arabic",
            is_featured=False,
            is_active=True,
            order=2
        )
        self.stdout.write(self.style.SUCCESS(f"Created: {coordinator.name}"))
        
        # Create Support Staff 2 - Physical Therapist
        physio = Doctor.objects.create(
            name="Dr. Hassan Ali",
            slug="hassan-ali",
            title="DPT, MSPT",
            specialty="physical-therapist",
            role="Head of Rehabilitation",
            bio="""Dr. Hassan Ali leads the physical therapy and rehabilitation program at Hills Clinic. His specialized protocols for limb lengthening recovery help patients regain full mobility and strength after surgery.

Dr. Hassan works closely with each patient to create personalized rehabilitation plans, monitoring progress and adjusting therapy as needed. His expertise ensures optimal recovery outcomes and helps patients return to their active lifestyles.""",
            short_bio="Expert in post-operative rehabilitation for limb lengthening patients.",
            education="""Doctor of Physical Therapy - University of Lahore
Master of Science in Physical Therapy - UVAS""",
            certifications="""Licensed Physical Therapist
Certified in Orthopedic Manual Therapy
Member, Pakistan Physical Therapy Association""",
            experience_years=12,
            languages="English, Urdu",
            is_featured=False,
            is_active=True,
            order=3
        )
        self.stdout.write(self.style.SUCCESS(f"Created: {physio.name}"))
        
        self.stdout.write(self.style.SUCCESS("All team members created successfully!"))
