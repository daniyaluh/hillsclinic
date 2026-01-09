# Generated migration to seed legal page content
from django.db import migrations


def seed_legal_content(apps, schema_editor):
    """Add Privacy Policy, Terms of Service, and Cookie Policy content."""
    LegalPageSection = apps.get_model('cms', 'LegalPageSection')
    
    sections = [
        # =====================
        # PRIVACY POLICY
        # =====================
        {
            'page_type': 'privacy',
            'section_id': 'overview',
            'title': 'Overview',
            'content': '''<p>Hills Clinic ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website or use our services.</p>
<p>Please read this privacy policy carefully. By accessing or using our services, you acknowledge that you have read, understood, and agree to be bound by all the terms of this policy.</p>''',
            'order': 1,
        },
        {
            'page_type': 'privacy',
            'section_id': 'information-collected',
            'title': 'Information We Collect',
            'content': '''<h4>Personal Information</h4>
<p>We may collect personal information that you voluntarily provide to us when you:</p>
<ul>
<li>Register for an account on our patient portal</li>
<li>Request a consultation or book an appointment</li>
<li>Subscribe to our newsletter</li>
<li>Contact us via email, phone, or WhatsApp</li>
<li>Upload medical documents or images</li>
</ul>
<p>This information may include:</p>
<ul>
<li>Name, email address, phone number</li>
<li>Date of birth, gender, nationality</li>
<li>Medical history and health information</li>
<li>Payment and billing information</li>
<li>Photos and medical images (X-rays, etc.)</li>
</ul>
<h4>Automatically Collected Information</h4>
<p>When you visit our website, we may automatically collect:</p>
<ul>
<li>IP address and browser type</li>
<li>Device information and operating system</li>
<li>Pages visited and time spent on site</li>
<li>Referring website and search terms</li>
</ul>''',
            'order': 2,
        },
        {
            'page_type': 'privacy',
            'section_id': 'use-of-information',
            'title': 'How We Use Your Information',
            'content': '''<p>We use the information we collect to:</p>
<ul>
<li>Provide and maintain our medical services</li>
<li>Process appointments and consultations</li>
<li>Communicate with you about your care</li>
<li>Send appointment reminders and follow-up information</li>
<li>Process payments and billing</li>
<li>Improve our website and services</li>
<li>Comply with legal and regulatory requirements</li>
</ul>''',
            'order': 3,
        },
        {
            'page_type': 'privacy',
            'section_id': 'data-protection',
            'title': 'Data Protection & Security',
            'content': '''<p>We implement appropriate technical and organizational measures to protect your personal information, including:</p>
<ul>
<li>Encryption of data in transit and at rest</li>
<li>Secure access controls and authentication</li>
<li>Regular security audits and updates</li>
<li>Staff training on data protection</li>
<li>HIPAA-compliant data handling practices</li>
</ul>
<p>However, no method of transmission over the Internet is 100% secure. While we strive to protect your information, we cannot guarantee its absolute security.</p>''',
            'order': 4,
        },
        {
            'page_type': 'privacy',
            'section_id': 'sharing',
            'title': 'Information Sharing',
            'content': '''<p>We may share your information with:</p>
<ul>
<li><strong>Medical Staff:</strong> Doctors, surgeons, and healthcare providers involved in your care</li>
<li><strong>Service Providers:</strong> Third parties who assist with payment processing, appointment scheduling, and communication</li>
<li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
</ul>
<p>We will never sell your personal information to third parties for marketing purposes.</p>''',
            'order': 5,
        },
        {
            'page_type': 'privacy',
            'section_id': 'your-rights',
            'title': 'Your Rights',
            'content': '''<p>Depending on your location, you may have the right to:</p>
<ul>
<li>Access the personal information we hold about you</li>
<li>Request correction of inaccurate information</li>
<li>Request deletion of your information</li>
<li>Withdraw consent for marketing communications</li>
<li>Request a copy of your data in a portable format</li>
</ul>
<p>To exercise these rights, please contact us at <a href="mailto:privacy@hillsclinic.com">privacy@hillsclinic.com</a></p>''',
            'order': 6,
        },
        {
            'page_type': 'privacy',
            'section_id': 'contact',
            'title': 'Contact Us',
            'content': '''<p>If you have questions about this Privacy Policy, please contact us:</p>
<ul>
<li><strong>Email:</strong> <a href="mailto:privacy@hillsclinic.com">privacy@hillsclinic.com</a></li>
<li><strong>Phone:</strong> +90 312 XXX XXXX</li>
<li><strong>Address:</strong> Hills Clinic, Ankara, Turkey</li>
</ul>''',
            'order': 7,
        },
        
        # =====================
        # TERMS OF SERVICE
        # =====================
        {
            'page_type': 'terms',
            'section_id': 'agreement',
            'title': 'Agreement to Terms',
            'content': '''<p>These Terms of Service ("Terms") govern your use of the Hills Clinic website and services. By accessing our website or using our services, you agree to these Terms.</p>
<p>If you disagree with any part of these Terms, you may not access our website or use our services.</p>''',
            'order': 1,
        },
        {
            'page_type': 'terms',
            'section_id': 'medical-disclaimer',
            'title': 'Medical Disclaimer',
            'content': '''<p><strong>Important:</strong> The information provided on this website is for general informational purposes only and should not be considered medical advice.</p>
<ul>
<li>Content is not intended to diagnose, treat, cure, or prevent any disease</li>
<li>Always consult with a qualified healthcare provider before making medical decisions</li>
<li>Individual results may vary based on personal health conditions</li>
<li>Surgery carries inherent risks that will be discussed during consultation</li>
</ul>''',
            'order': 2,
        },
        {
            'page_type': 'terms',
            'section_id': 'services',
            'title': 'Our Services',
            'content': '''<p>Hills Clinic provides:</p>
<ul>
<li>Medical consultations (in-person, video, and phone)</li>
<li>Limb lengthening surgical procedures</li>
<li>Post-operative care and rehabilitation</li>
<li>Patient portal for managing appointments and documents</li>
</ul>
<p>All medical services are provided by licensed medical professionals in accordance with Turkish healthcare regulations.</p>''',
            'order': 3,
        },
        {
            'page_type': 'terms',
            'section_id': 'patient-portal',
            'title': 'Patient Portal Account',
            'content': '''<p>When you create an account on our patient portal, you agree to:</p>
<ul>
<li>Provide accurate and complete information</li>
<li>Maintain the security of your account credentials</li>
<li>Notify us immediately of unauthorized access</li>
<li>Take responsibility for activities under your account</li>
</ul>
<p>We reserve the right to suspend or terminate accounts that violate these Terms.</p>''',
            'order': 4,
        },
        {
            'page_type': 'terms',
            'section_id': 'payments',
            'title': 'Payments & Refunds',
            'content': '''<p>Our payment policies:</p>
<ul>
<li>Consultation fees are non-refundable once the consultation is completed</li>
<li>Surgery deposits are refundable up to 30 days before scheduled procedure</li>
<li>Full payment is required before surgery unless financing is arranged</li>
<li>Price quotes are valid for 90 days from issue date</li>
</ul>
<p>We accept various payment methods including bank transfer, credit cards, and financing options.</p>''',
            'order': 5,
        },
        {
            'page_type': 'terms',
            'section_id': 'intellectual-property',
            'title': 'Intellectual Property',
            'content': '''<p>All content on this website, including text, images, logos, and design, is the property of Hills Clinic and protected by copyright laws.</p>
<p>You may not:</p>
<ul>
<li>Copy, modify, or distribute our content without permission</li>
<li>Use our trademarks or branding without authorization</li>
<li>Scrape or extract data from our website</li>
</ul>''',
            'order': 6,
        },
        {
            'page_type': 'terms',
            'section_id': 'limitation',
            'title': 'Limitation of Liability',
            'content': '''<p>To the maximum extent permitted by law:</p>
<ul>
<li>Hills Clinic is not liable for indirect, incidental, or consequential damages</li>
<li>Our liability is limited to the amount paid for services</li>
<li>We do not guarantee specific surgical outcomes</li>
</ul>
<p>This does not affect your statutory rights as a patient.</p>''',
            'order': 7,
        },
        {
            'page_type': 'terms',
            'section_id': 'governing-law',
            'title': 'Governing Law',
            'content': '''<p>These Terms are governed by the laws of Turkey. Any disputes shall be resolved in the courts of Ankara, Turkey.</p>
<p>For international patients, we will make reasonable efforts to resolve disputes through mediation before legal proceedings.</p>''',
            'order': 8,
        },
        {
            'page_type': 'terms',
            'section_id': 'contact',
            'title': 'Contact Information',
            'content': '''<p>For questions about these Terms, contact us:</p>
<ul>
<li><strong>Email:</strong> <a href="mailto:legal@hillsclinic.com">legal@hillsclinic.com</a></li>
<li><strong>Phone:</strong> +90 312 XXX XXXX</li>
<li><strong>Address:</strong> Hills Clinic, Ankara, Turkey</li>
</ul>''',
            'order': 9,
        },
        
        # =====================
        # COOKIE POLICY
        # =====================
        {
            'page_type': 'cookies',
            'section_id': 'what-are-cookies',
            'title': 'What Are Cookies?',
            'content': '''<p>Cookies are small text files stored on your device when you visit a website. They help websites remember your preferences and improve your experience.</p>
<p>Cookies can be "session" cookies (deleted when you close your browser) or "persistent" cookies (remain until they expire or you delete them).</p>''',
            'order': 1,
        },
        {
            'page_type': 'cookies',
            'section_id': 'cookies-we-use',
            'title': 'Cookies We Use',
            'content': '''<p>We use the following types of cookies:</p>
<h4>Essential Cookies</h4>
<p>Required for basic website functionality including:</p>
<ul>
<li>User authentication and login sessions</li>
<li>Security features and fraud prevention</li>
<li>Load balancing and server management</li>
</ul>
<h4>Analytics Cookies</h4>
<p>Help us understand how visitors use our site:</p>
<ul>
<li>Page views and navigation patterns</li>
<li>Time spent on pages</li>
<li>Traffic sources and referrals</li>
</ul>
<h4>Preference Cookies</h4>
<p>Remember your settings and preferences:</p>
<ul>
<li>Language preferences</li>
<li>Display settings</li>
<li>Form auto-fill information</li>
</ul>''',
            'order': 2,
        },
        {
            'page_type': 'cookies',
            'section_id': 'third-party-cookies',
            'title': 'Third-Party Cookies',
            'content': '''<p>Some cookies are placed by third-party services that appear on our pages:</p>
<ul>
<li><strong>Google Analytics:</strong> Website usage statistics</li>
<li><strong>Cloudinary:</strong> Image delivery and optimization</li>
<li><strong>Payment Processors:</strong> Secure payment handling</li>
</ul>
<p>These third parties have their own privacy policies governing the use of cookies.</p>''',
            'order': 3,
        },
        {
            'page_type': 'cookies',
            'section_id': 'managing-cookies',
            'title': 'Managing Cookies',
            'content': '''<p>You can control cookies through your browser settings. However, disabling certain cookies may affect website functionality.</p>
<p>Most browsers allow you to:</p>
<ul>
<li>View and delete existing cookies</li>
<li>Block all or third-party cookies</li>
<li>Set preferences for specific websites</li>
<li>Receive notifications when cookies are set</li>
</ul>
<p>For more information on managing cookies, visit <a href="https://www.allaboutcookies.org" target="_blank" rel="noopener">allaboutcookies.org</a></p>''',
            'order': 4,
        },
        {
            'page_type': 'cookies',
            'section_id': 'contact',
            'title': 'Contact Us',
            'content': '''<p>For questions about our cookie policy, contact us at <a href="mailto:privacy@hillsclinic.com">privacy@hillsclinic.com</a></p>''',
            'order': 5,
        },
    ]
    
    for section_data in sections:
        LegalPageSection.objects.create(**section_data)


def remove_legal_content(apps, schema_editor):
    """Remove seeded legal content."""
    LegalPageSection = apps.get_model('cms', 'LegalPageSection')
    LegalPageSection.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0008_add_legal_page_section'),
    ]

    operations = [
        migrations.RunPython(seed_legal_content, remove_legal_content),
    ]
