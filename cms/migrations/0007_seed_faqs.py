# Generated migration to seed FAQs
from django.db import migrations


def seed_faqs(apps, schema_editor):
    """Add initial FAQs to the database."""
    FAQItem = apps.get_model('cms', 'FAQItem')
    
    faqs = [
        # General Questions (4)
        {
            'question': 'What is limb lengthening surgery?',
            'answer': '<p>Limb lengthening surgery is a medical procedure that gradually increases the length of bones in the legs or arms. The surgery involves cutting the bone (osteotomy) and using a specialized device to slowly separate the bone ends over time, allowing new bone tissue to form in the gap. This process is called distraction osteogenesis.</p>',
            'category': 'general',
            'order': 1,
        },
        {
            'question': 'Am I a good candidate for limb lengthening?',
            'answer': '<p>Good candidates are typically adults aged 18-50 in good overall health with adequate bone density. We evaluate each patient individually based on:</p><ul><li>Medical history and current health status</li><li>Bone health and density</li><li>Psychological readiness and realistic expectations</li><li>Ability to commit to the lengthy recovery process</li></ul><p>A consultation with our team will determine your suitability for the procedure.</p>',
            'category': 'general',
            'order': 2,
        },
        {
            'question': 'How much height can I gain?',
            'answer': '<p>Typical gains are 2-3 inches (5-8 cm) per bone segment. The femur (thigh bone) and tibia (shin bone) can each be lengthened separately or together:</p><ul><li><strong>Femur only:</strong> 2-3 inches</li><li><strong>Tibia only:</strong> 2-3 inches</li><li><strong>Combined (staged):</strong> 4-6 inches total</li></ul><p>Combined procedures are done in stages for safety, with adequate healing time between surgeries.</p>',
            'category': 'general',
            'order': 3,
        },
        {
            'question': 'What is the age limit for limb lengthening?',
            'answer': '<p>We typically perform surgery on patients aged 18-50. However, bone density and overall health are more important factors than age alone. Patients over 50 may still be candidates if they have good bone health. Younger patients must have completed their natural growth (closed growth plates), which usually occurs by age 18.</p>',
            'category': 'general',
            'order': 4,
        },
        
        # Cost & Financing (3)
        {
            'question': 'How much does limb lengthening cost at Hills Clinic?',
            'answer': '<p>Our all-inclusive packages are significantly more affordable than Western countries:</p><ul><li><strong>Ilizarov Method:</strong> $3,000 - $4,000 USD</li><li><strong>LON Method:</strong> $4,500 - $5,500 USD</li><li><strong>PRECICE (Internal Nail):</strong> $8,000 - $12,000 USD</li></ul><p>Packages include surgery, hospital stay, post-operative care, physiotherapy guidance, and follow-up appointments. This compares to $80,000-$150,000+ in the US or Europe.</p>',
            'category': 'cost',
            'order': 1,
        },
        {
            'question': 'What payment methods do you accept?',
            'answer': '<p>We accept multiple payment methods for your convenience:</p><ul><li>Bank wire transfer (preferred for international patients)</li><li>Credit/debit cards (Visa, Mastercard)</li><li>Cash (USD, EUR, or local currency)</li></ul><p>A deposit is required to secure your surgery date, with the remaining balance due before the procedure. We can also provide documentation for medical financing applications.</p>',
            'category': 'cost',
            'order': 2,
        },
        {
            'question': 'Do you offer payment plans or financing?',
            'answer': '<p>Yes, we offer flexible payment arrangements:</p><ul><li><strong>Deposit:</strong> 30% to secure your surgery date</li><li><strong>Balance:</strong> Due before the procedure begins</li><li><strong>Early payment discount:</strong> 5% off for full payment 30+ days in advance</li></ul><p>We can also provide medical documentation to help you apply for healthcare financing in your home country. Contact us to discuss personalized payment arrangements.</p>',
            'category': 'cost',
            'order': 3,
        },
        
        # Recovery (4)
        {
            'question': 'How long is the total recovery time?',
            'answer': '<p>The complete recovery journey typically takes 6-12 months:</p><ul><li><strong>Lengthening phase:</strong> 2-3 months (bone is gradually lengthened at ~1mm per day)</li><li><strong>Consolidation phase:</strong> 3-6 months (new bone hardens and strengthens)</li><li><strong>Full recovery:</strong> Most patients return to normal activities within 12 months</li></ul><p>You can return home after the lengthening phase, with follow-up care coordinated remotely.</p>',
            'category': 'recovery',
            'order': 1,
        },
        {
            'question': 'Is the surgery painful?',
            'answer': '<p>Pain management is a priority throughout your journey:</p><ul><li><strong>Surgery:</strong> Performed under general anesthesia - you feel nothing</li><li><strong>Post-operative:</strong> Managed with prescription pain medication</li><li><strong>Lengthening phase:</strong> Most patients experience mild to moderate discomfort, well-controlled with medication</li></ul><p>The gradual 1mm/day lengthening rate is specifically designed to minimize pain. Most patients describe it as manageable with proper medication and physiotherapy.</p>',
            'category': 'recovery',
            'order': 2,
        },
        {
            'question': 'Can I walk during the lengthening process?',
            'answer': '<p>Yes! Early mobilization is actually encouraged:</p><ul><li>Patients typically use crutches or a walker during the lengthening phase</li><li>Partial weight-bearing helps stimulate bone growth</li><li>Daily physiotherapy exercises maintain muscle strength and flexibility</li></ul><p>Your specific mobility plan will be customized based on the procedure type and your progress.</p>',
            'category': 'recovery',
            'order': 3,
        },
        {
            'question': 'What are the risks and potential complications?',
            'answer': '<p>Like any surgery, limb lengthening carries some risks. Common complications include:</p><ul><li><strong>Pin site infections:</strong> Usually minor, treated with antibiotics</li><li><strong>Muscle tightness:</strong> Managed with physiotherapy</li><li><strong>Slow bone healing:</strong> Monitored with regular X-rays</li><li><strong>Joint stiffness:</strong> Prevented with daily exercises</li></ul><p>Serious complications are rare with experienced surgeons. Dr. Khaq\'s 40+ years of experience and careful patient selection help minimize risks.</p>',
            'category': 'recovery',
            'order': 4,
        },
        
        # International Patients (3)
        {
            'question': 'Do you help with visa and travel arrangements?',
            'answer': '<p>Yes! Our international patient coordinators provide comprehensive support:</p><ul><li><strong>Visa assistance:</strong> Medical visa invitation letters and documentation</li><li><strong>Airport pickup:</strong> Private transfer from the airport</li><li><strong>Accommodation:</strong> Recommendations for nearby hotels and recovery apartments</li><li><strong>Translation:</strong> Interpreters available for consultations and during your stay</li></ul><p>We\'ve helped patients from over 20 countries navigate the process smoothly.</p>',
            'category': 'international',
            'order': 1,
        },
        {
            'question': 'How long do I need to stay in Turkey?',
            'answer': '<p>The typical stay duration depends on your procedure:</p><ul><li><strong>Initial stay:</strong> 2-3 weeks (surgery + immediate post-op care)</li><li><strong>Lengthening phase:</strong> 2-3 months (can stay locally or return home with proper guidance)</li><li><strong>Follow-up visits:</strong> Periodic check-ups can often be done remotely via video consultation</li></ul><p>Many patients choose to stay for the full lengthening phase, while others return home with detailed self-care instructions.</p>',
            'category': 'international',
            'order': 2,
        },
        {
            'question': 'What languages do your staff speak?',
            'answer': '<p>Our multilingual team can assist you in:</p><ul><li>English (fluent)</li><li>Turkish (native)</li><li>Arabic</li><li>Russian</li><li>Farsi/Persian</li></ul><p>Professional medical interpreters are also available for other languages upon request. All medical documentation can be provided in English.</p>',
            'category': 'international',
            'order': 3,
        },
    ]
    
    for faq_data in faqs:
        FAQItem.objects.create(**faq_data)


def remove_faqs(apps, schema_editor):
    """Remove seeded FAQs."""
    FAQItem = apps.get_model('cms', 'FAQItem')
    FAQItem.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0006_fix_patient_review_procedure_types'),
    ]

    operations = [
        migrations.RunPython(seed_faqs, remove_faqs),
    ]
