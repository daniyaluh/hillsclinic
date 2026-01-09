"""
CMS app views for static page rendering.

These views provide static versions of CMS pages for when
Wagtail CMS pages haven't been created yet.
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from cms.models import PatientReview, FAQItem


class ProceduresOverviewView(TemplateView):
    """Overview of all limb lengthening procedures."""
    template_name = 'cms/procedures_overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['procedures'] = [
            {
                'name': 'Ilizarov Method',
                'slug': 'ilizarov',
                'description': 'External fixator technique with proven results over decades.',
                'height_gain': '4-6 inches',
                'duration': '6-12 months',
                'price_range': '$3,000 - $4,000',
                'color': 'blue',
                'image': 'https://res.cloudinary.com/dhovspacb/image/upload/c_fill,w_400,h_250,q_auto,f_auto/v1/media/images/p_ilizarov',
            },
            {
                'name': 'Internal Nail (Precice)',
                'slug': 'internal-nails',
                'description': 'Minimally invasive with internal magnetic nails.',
                'height_gain': '3-4 inches',
                'duration': '4-8 months',
                'price_range': '$15,000 - $25,000',
                'color': 'purple',
                'image': 'https://res.cloudinary.com/dhovspacb/image/upload/c_fill,w_400,h_250,q_auto,f_auto/v1/media/images/p_internalnail',
            },
            {
                'name': 'LON Method',
                'slug': 'lon',
                'description': 'Combination of external fixator and internal nail.',
                'height_gain': '4-6 inches',
                'duration': '5-10 months',
                'price_range': '$4,500 - $5,500',
                'color': 'teal',
                'image': 'https://res.cloudinary.com/dhovspacb/image/upload/c_fill,w_400,h_250,q_auto,f_auto/v1/media/images/p_lon',
            },
        ]
        return context


class ProcedureDetailView(TemplateView):
    """Detail view for individual procedures."""
    template_name = 'cms/procedure_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        procedure_type = self.kwargs.get('procedure_type', 'ilizarov')
        
        procedures_data = {
            'ilizarov': {
                'name': 'Ilizarov Method',
                'tagline': 'The Gold Standard in Limb Lengthening',
                'description': 'The Ilizarov technique uses an external circular frame attached to the bone with wires and pins. This time-tested method has been refined over 50+ years and remains the most versatile approach for limb lengthening.',
                'procedure_type': 'ilizarov',
                'height_gain_femur': '6-8 cm (2.5-3 inches)',
                'height_gain_tibia': '5-7 cm (2-2.5 inches)',
                'height_gain_combined': '10-15 cm (4-6 inches)',
                'complication_rate': '<5%',
                'recovery_time': '6-12 months',
                'hospital_stay': '3-5 days',
                'lengthening_rate': '1mm per day',
                'consolidation_index': '30-40 days per cm',
                'pros': [
                    'Most affordable option among all methods',
                    'Proven track record with 50+ years of clinical data',
                    'Suitable for complex deformity corrections',
                    'Allows simultaneous angular and rotational corrections',
                    'No secondary surgery needed for hardware removal',
                    'Maximum height gain potential',
                    'Can be adjusted during treatment',
                ],
                'cons': [
                    'External frame visible during treatment',
                    'Requires daily pin site care and cleaning',
                    'Longer total treatment duration',
                    'May limit some daily activities during lengthening',
                ],
                'ideal_for': 'Patients seeking affordable, proven results with maximum height potential, or those requiring complex corrections.',
                'how_it_works': [
                    {'step': 'Pre-operative Planning', 'description': 'Detailed X-rays and CT scans are taken. Your surgeon plans the exact cut location and frame configuration.'},
                    {'step': 'Surgery (Osteotomy)', 'description': 'Under general anesthesia, the bone is carefully cut (osteotomy) and the circular external fixator is attached using thin wires and pins.'},
                    {'step': 'Latency Period', 'description': '5-7 days of rest allows initial healing and blood supply formation at the bone cut site.'},
                    {'step': 'Distraction Phase', 'description': 'You turn adjustment nuts 4 times daily (0.25mm each), gradually separating the bone ends at 1mm/day. New bone forms in the gap.'},
                    {'step': 'Consolidation Phase', 'description': 'Once desired length is achieved, the frame remains while new bone hardens. This takes 30-40 days per centimeter gained.'},
                    {'step': 'Frame Removal', 'description': 'Once X-rays confirm solid bone formation, the frame is removed in a simple outpatient procedure.'},
                ],
                'candidacy': [
                    'Adults aged 18-50 with healthy bone quality',
                    'Patients with limb length discrepancy',
                    'Those seeking cosmetic height increase',
                    'Patients with angular deformities requiring correction',
                    'Non-smokers or those willing to quit',
                    'Patients committed to extensive physical therapy',
                ],
                'faq': [
                    {'question': 'Is the Ilizarov method painful?', 'answer': 'Most patients report mild to moderate discomfort that is well-managed with pain medication. The distraction process itself is not painful.'},
                    {'question': 'Can I walk during treatment?', 'answer': 'Yes! Weight-bearing is encouraged and actually helps bone formation. You will use crutches or a walker initially.'},
                    {'question': 'Will there be scars?', 'answer': 'Small pin site scars (2-3mm) will fade significantly over time. Most patients find them barely noticeable after 1-2 years.'},
                    {'question': 'How much height can I gain?', 'answer': 'Typically 5-8cm per bone segment. Combined femur and tibia lengthening can achieve 10-15cm total.'},
                ],
            },
            'internal-nails': {
                'name': 'Internal Nail (PRECICE)',
                'tagline': 'Invisible Lengthening Technology',
                'description': 'The PRECICE internal nail is a revolutionary motorized implant placed inside the bone. Lengthening is achieved externally using a magnetic remote controller, eliminating the need for external hardware.',
                'procedure_type': 'internal',
                'height_gain_femur': '5-8 cm (2-3 inches)',
                'height_gain_tibia': '4-5 cm (1.5-2 inches)',
                'height_gain_combined': '8-10 cm (3-4 inches)',
                'complication_rate': '<3%',
                'recovery_time': '4-8 months',
                'hospital_stay': '1-2 days',
                'lengthening_rate': '0.66-1mm per day',
                'consolidation_index': '25-35 days per cm',
                'pros': [
                    'No external hardware - completely internal',
                    'Lower infection risk (no pin sites)',
                    'Superior cosmetic result during treatment',
                    'Normal clothing and daily activities possible',
                    'Precise, controlled lengthening with magnetic ERC',
                    'Faster consolidation compared to external methods',
                    'Less physical therapy required',
                ],
                'cons': [
                    'Higher initial cost',
                    'Second surgery required for nail removal (optional)',
                    'Limited to straight lengthening (no angular correction)',
                    'Maximum lengthening limited by nail length',
                    'Not suitable for patients with certain metal implants or pacemakers',
                ],
                'ideal_for': 'Patients prioritizing cosmetics and convenience who have budget flexibility and do not require deformity correction.',
                'how_it_works': [
                    {'step': 'Pre-operative Planning', 'description': 'Precise measurements determine the correct nail size. Full-length X-rays and MRI ensure proper sizing.'},
                    {'step': 'Nail Insertion Surgery', 'description': 'Through a small incision, the bone is cut and the magnetic nail is inserted into the medullary canal and secured with screws.'},
                    {'step': 'Latency Period', 'description': '5-7 days of rest for initial healing before lengthening begins.'},
                    {'step': 'Distraction Phase', 'description': 'Using the External Remote Controller (ERC), you activate the internal magnet 3x daily. The nail telescopes apart at a controlled rate.'},
                    {'step': 'Consolidation Phase', 'description': 'The nail remains locked while new bone solidifies. Weight-bearing is gradually increased.'},
                    {'step': 'Optional Nail Removal', 'description': 'After 1-2 years, the nail can be removed electively. Many patients choose to keep it permanently.'},
                ],
                'candidacy': [
                    'Adults aged 18-50 seeking cosmetic lengthening',
                    'Patients without angular deformity',
                    'Those prioritizing aesthetics during treatment',
                    'Patients with adequate bone canal diameter',
                    'Non-smokers with good bone density',
                    'No contraindications to MRI or magnetic devices',
                ],
                'faq': [
                    {'question': 'Is the PRECICE nail visible?', 'answer': 'No, the nail is completely internal. There are only small surgical scars that fade over time.'},
                    {'question': 'Does the ERC device hurt?', 'answer': 'No, the magnetic controller is painless. You simply hold it against your leg for a few minutes each session.'},
                    {'question': 'Can I go through airport security?', 'answer': 'Yes, the nail may trigger metal detectors. We provide a medical card explaining your implant.'},
                    {'question': 'Do I need the nail removed?', 'answer': 'Removal is optional. Many patients keep the nail permanently with no issues.'},
                ],
            },
            'lon': {
                'name': 'LON Method',
                'tagline': 'The Best of Both Worlds',
                'description': 'Lengthening Over Nail (LON) combines external fixation for the lengthening phase with an internal nail for consolidation. This hybrid approach offers excellent height gain with reduced external frame wearing time.',
                'procedure_type': 'lon',
                'height_gain_femur': '6-8 cm (2.5-3 inches)',
                'height_gain_tibia': '5-6 cm (2-2.5 inches)',
                'height_gain_combined': '10-14 cm (4-5.5 inches)',
                'complication_rate': '<4%',
                'recovery_time': '5-9 months',
                'hospital_stay': '3-5 days',
                'lengthening_rate': '1mm per day',
                'consolidation_index': '20-30 days per cm',
                'pros': [
                    'Shorter external frame wearing time (lengthening phase only)',
                    'Good height gain potential similar to Ilizarov',
                    'Faster overall recovery due to internal nail consolidation',
                    'Internal nail provides strength during healing',
                    'Earlier return to activities after frame removal',
                    'Balanced cost-to-benefit ratio',
                ],
                'cons': [
                    'External frame required during lengthening phase',
                    'Two techniques combined means slightly more complexity',
                    'Internal nail may need removal later',
                    'Higher cost than pure Ilizarov method',
                    'Limited angular correction capability',
                ],
                'ideal_for': 'Patients wanting maximum height gain with significantly reduced external frame wearing time and faster consolidation.',
                'how_it_works': [
                    {'step': 'Pre-operative Planning', 'description': 'Measurements for both the external fixator and internal nail are carefully planned using imaging.'},
                    {'step': 'Combined Surgery', 'description': 'The internal nail is inserted first, then the external fixator is applied. The bone is cut (osteotomy) over the nail.'},
                    {'step': 'Latency Period', 'description': '5-7 days before lengthening begins.'},
                    {'step': 'Distraction Phase', 'description': 'Lengthening occurs through the external fixator at 1mm/day while the internal nail slides telescopically.'},
                    {'step': 'Frame Removal & Nail Locking', 'description': 'Once target length is reached, the external frame is removed and the internal nail is locked with screws.'},
                    {'step': 'Consolidation', 'description': 'The locked nail supports the leg while new bone hardens, allowing faster weight-bearing and recovery.'},
                ],
                'candidacy': [
                    'Adults aged 18-50 seeking significant height increase',
                    'Patients wanting to minimize external frame duration',
                    'Those with adequate bone canal for nail insertion',
                    'Patients willing to undergo slightly more complex surgery',
                    'Non-smokers with good overall health',
                    'Commitment to rehabilitation program',
                ],
                'faq': [
                    {'question': 'How long do I wear the external frame?', 'answer': 'Only during the lengthening phase (6-8 weeks typically), compared to 4-6 months with Ilizarov alone.'},
                    {'question': 'Is LON more expensive than Ilizarov?', 'answer': 'Yes, due to the internal nail cost, but less expensive than full PRECICE treatment.'},
                    {'question': 'Can I correct deformities with LON?', 'answer': 'Minor corrections are possible, but significant angular deformities are better treated with Ilizarov.'},
                    {'question': 'What happens after frame removal?', 'answer': 'The internal nail provides immediate stability, allowing faster return to walking without crutches.'},
                ],
            },
        }
        
        context['page'] = procedures_data.get(procedure_type, procedures_data['ilizarov'])
        context['page']['title'] = context['page']['name']
        return context


class InternationalPatientsView(TemplateView):
    """International patients information page."""
    template_name = 'cms/international_center_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = {
            'title': 'International Patient Center',
            'introduction': '<p>We welcome patients from around the world. Our dedicated international team ensures a seamless experience from initial consultation to your journey home.</p>',
        }
        return context


class CostFinancingView(TemplateView):
    """Cost and financing information page."""
    template_name = 'cms/cost_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = {
            'title': 'Cost & Financing',
            'introduction': '<p>Hills Clinic offers world-class limb lengthening at a fraction of Western prices. We believe cost should never be a barrier to achieving your height goals.</p>',
            'min_price': 3000,
            'max_price': 6000,
            'currency': 'USD',
            'full_payment_discount': 10,
        }
        return context


class RecoveryView(TemplateView):
    """Recovery and rehabilitation information page."""
    template_name = 'cms/recovery_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = {
            'title': 'Recovery & Rehabilitation',
            'introduction': '<p>Understanding the recovery process is essential for successful limb lengthening. Our comprehensive rehabilitation program ensures optimal outcomes.</p>',
        }
        return context


class SuccessStoriesView(TemplateView):
    """Success stories index page."""
    template_name = 'cms/success_stories_index_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = {
            'title': 'Success Stories',
            'introduction': '<p>Read inspiring stories from patients who have transformed their lives through limb lengthening surgery at Hills Clinic.</p>',
        }
        # Get actual patient reviews from database
        context['reviews'] = PatientReview.objects.filter(is_published=True).order_by('display_order', '-id')
        context['featured_reviews'] = PatientReview.objects.filter(is_published=True, is_featured=True)
        return context


class FAQView(TemplateView):
    """Frequently asked questions page."""
    template_name = 'cms/faq_static.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = {
            'title': 'Frequently Asked Questions',
        }
        # Get FAQs from database grouped by category
        all_faqs = FAQItem.objects.all().order_by('category', 'order', 'question')
        
        # Group FAQs by category
        faqs_by_category = {}
        for faq in all_faqs:
            if faq.category not in faqs_by_category:
                faqs_by_category[faq.category] = []
            faqs_by_category[faq.category].append(faq)
        
        context['faqs_by_category'] = faqs_by_category
        context['all_faqs'] = all_faqs
        return context


class LegalPageView(TemplateView):
    """View for legal pages (Privacy Policy, Terms of Service, etc.)."""
    template_name = 'cms/legal_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_type = self.kwargs.get('page_type', 'privacy')
        
        legal_content = {
            'privacy': {
                'title': 'Privacy Policy',
                'last_updated': '2026-01-09',
                'sections': [
                    {
                        'id': 'overview',
                        'title': 'Overview',
                        'content': '''
                            <p>Hills Clinic ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website or use our services.</p>
                            <p>Please read this privacy policy carefully. By accessing or using our services, you acknowledge that you have read, understood, and agree to be bound by all the terms of this policy.</p>
                        '''
                    },
                    {
                        'id': 'information-collected',
                        'title': 'Information We Collect',
                        'content': '''
                            <h4>Personal Information</h4>
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
                            </ul>
                        '''
                    },
                    {
                        'id': 'use-of-information',
                        'title': 'How We Use Your Information',
                        'content': '''
                            <p>We use the information we collect to:</p>
                            <ul>
                                <li>Provide and maintain our medical services</li>
                                <li>Process appointments and consultations</li>
                                <li>Communicate with you about your care</li>
                                <li>Send appointment reminders and follow-up information</li>
                                <li>Process payments and billing</li>
                                <li>Improve our website and services</li>
                                <li>Comply with legal and regulatory requirements</li>
                            </ul>
                        '''
                    },
                    {
                        'id': 'data-protection',
                        'title': 'Data Protection & Security',
                        'content': '''
                            <p>We implement appropriate technical and organizational measures to protect your personal information, including:</p>
                            <ul>
                                <li>Encryption of data in transit and at rest</li>
                                <li>Secure access controls and authentication</li>
                                <li>Regular security audits and updates</li>
                                <li>Staff training on data protection</li>
                                <li>HIPAA-compliant data handling practices</li>
                            </ul>
                            <p>However, no method of transmission over the Internet is 100% secure. While we strive to protect your information, we cannot guarantee its absolute security.</p>
                        '''
                    },
                    {
                        'id': 'sharing',
                        'title': 'Information Sharing',
                        'content': '''
                            <p>We may share your information with:</p>
                            <ul>
                                <li><strong>Medical Staff:</strong> Doctors, surgeons, and healthcare providers involved in your care</li>
                                <li><strong>Service Providers:</strong> Third parties who assist with payment processing, appointment scheduling, and communication</li>
                                <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
                            </ul>
                            <p>We will never sell your personal information to third parties for marketing purposes.</p>
                        '''
                    },
                    {
                        'id': 'your-rights',
                        'title': 'Your Rights',
                        'content': '''
                            <p>Depending on your location, you may have the right to:</p>
                            <ul>
                                <li>Access the personal information we hold about you</li>
                                <li>Request correction of inaccurate information</li>
                                <li>Request deletion of your information</li>
                                <li>Withdraw consent for marketing communications</li>
                                <li>Request a copy of your data in a portable format</li>
                            </ul>
                            <p>To exercise these rights, please contact us at privacy@hillsclinic.com</p>
                        '''
                    },
                    {
                        'id': 'contact',
                        'title': 'Contact Us',
                        'content': '''
                            <p>If you have questions about this Privacy Policy, please contact us:</p>
                            <ul>
                                <li><strong>Email:</strong> privacy@hillsclinic.com</li>
                                <li><strong>Phone:</strong> +92-42-35761234</li>
                                <li><strong>Address:</strong> Hills Clinic, DHA Phase 5, Lahore, Pakistan</li>
                            </ul>
                        '''
                    },
                ]
            },
            'terms': {
                'title': 'Terms of Service',
                'last_updated': '2026-01-09',
                'sections': [
                    {
                        'id': 'overview',
                        'title': 'Agreement to Terms',
                        'content': '''
                            <p>These Terms of Service ("Terms") govern your use of the Hills Clinic website and services. By accessing our website or using our services, you agree to these Terms.</p>
                            <p>If you disagree with any part of these Terms, you may not access our website or use our services.</p>
                        '''
                    },
                    {
                        'id': 'medical-disclaimer',
                        'title': 'Medical Disclaimer',
                        'content': '''
                            <p><strong>Important:</strong> The information provided on this website is for general informational purposes only and should not be considered medical advice.</p>
                            <ul>
                                <li>Content is not intended to diagnose, treat, cure, or prevent any disease</li>
                                <li>Always consult with a qualified healthcare provider before making medical decisions</li>
                                <li>Individual results may vary based on personal health conditions</li>
                                <li>Surgery carries inherent risks that will be discussed during consultation</li>
                            </ul>
                        '''
                    },
                    {
                        'id': 'services',
                        'title': 'Our Services',
                        'content': '''
                            <p>Hills Clinic provides:</p>
                            <ul>
                                <li>Medical consultations (in-person, video, and phone)</li>
                                <li>Limb lengthening surgical procedures</li>
                                <li>Post-operative care and rehabilitation</li>
                                <li>Patient portal for managing appointments and documents</li>
                            </ul>
                            <p>All medical services are provided by licensed medical professionals in accordance with Pakistani healthcare regulations.</p>
                        '''
                    },
                    {
                        'id': 'patient-portal',
                        'title': 'Patient Portal Account',
                        'content': '''
                            <p>When you create an account on our patient portal, you agree to:</p>
                            <ul>
                                <li>Provide accurate and complete information</li>
                                <li>Maintain the security of your account credentials</li>
                                <li>Notify us immediately of unauthorized access</li>
                                <li>Take responsibility for activities under your account</li>
                            </ul>
                            <p>We reserve the right to suspend or terminate accounts that violate these Terms.</p>
                        '''
                    },
                    {
                        'id': 'payments',
                        'title': 'Payments & Refunds',
                        'content': '''
                            <p>Our payment policies:</p>
                            <ul>
                                <li>Consultation fees are non-refundable once the consultation is completed</li>
                                <li>Surgery deposits are refundable up to 30 days before scheduled procedure</li>
                                <li>Full payment is required before surgery unless financing is arranged</li>
                                <li>Price quotes are valid for 90 days from issue date</li>
                            </ul>
                            <p>We accept various payment methods including bank transfer, credit cards, and financing options.</p>
                        '''
                    },
                    {
                        'id': 'intellectual-property',
                        'title': 'Intellectual Property',
                        'content': '''
                            <p>All content on this website, including text, images, logos, and design, is the property of Hills Clinic and protected by copyright laws.</p>
                            <p>You may not:</p>
                            <ul>
                                <li>Copy, modify, or distribute our content without permission</li>
                                <li>Use our trademarks or branding without authorization</li>
                                <li>Scrape or extract data from our website</li>
                            </ul>
                        '''
                    },
                    {
                        'id': 'limitation',
                        'title': 'Limitation of Liability',
                        'content': '''
                            <p>To the maximum extent permitted by law:</p>
                            <ul>
                                <li>Hills Clinic is not liable for indirect, incidental, or consequential damages</li>
                                <li>Our liability is limited to the amount paid for services</li>
                                <li>We do not guarantee specific surgical outcomes</li>
                            </ul>
                            <p>This does not affect your statutory rights as a patient.</p>
                        '''
                    },
                    {
                        'id': 'governing-law',
                        'title': 'Governing Law',
                        'content': '''
                            <p>These Terms are governed by the laws of Pakistan. Any disputes shall be resolved in the courts of Lahore, Pakistan.</p>
                            <p>For international patients, we will make reasonable efforts to resolve disputes through mediation before legal proceedings.</p>
                        '''
                    },
                    {
                        'id': 'contact',
                        'title': 'Contact Information',
                        'content': '''
                            <p>For questions about these Terms, contact us:</p>
                            <ul>
                                <li><strong>Email:</strong> legal@hillsclinic.com</li>
                                <li><strong>Phone:</strong> +92-42-35761234</li>
                                <li><strong>Address:</strong> Hills Clinic, DHA Phase 5, Lahore, Pakistan</li>
                            </ul>
                        '''
                    },
                ]
            },
            'cookies': {
                'title': 'Cookie Policy',
                'last_updated': '2026-01-09',
                'sections': [
                    {
                        'id': 'overview',
                        'title': 'What Are Cookies?',
                        'content': '''
                            <p>Cookies are small text files stored on your device when you visit a website. They help websites remember your preferences and improve your experience.</p>
                        '''
                    },
                    {
                        'id': 'cookies-we-use',
                        'title': 'Cookies We Use',
                        'content': '''
                            <p>We use the following types of cookies:</p>
                            <ul>
                                <li><strong>Essential Cookies:</strong> Required for basic website functionality (login, security)</li>
                                <li><strong>Analytics Cookies:</strong> Help us understand how visitors use our site</li>
                                <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
                            </ul>
                        '''
                    },
                    {
                        'id': 'managing-cookies',
                        'title': 'Managing Cookies',
                        'content': '''
                            <p>You can control cookies through your browser settings. However, disabling certain cookies may affect website functionality.</p>
                            <p>Most browsers allow you to:</p>
                            <ul>
                                <li>View and delete existing cookies</li>
                                <li>Block all or third-party cookies</li>
                                <li>Set preferences for specific websites</li>
                            </ul>
                        '''
                    },
                    {
                        'id': 'contact',
                        'title': 'Contact Us',
                        'content': '''
                            <p>For questions about our cookie policy, contact us at privacy@hillsclinic.com</p>
                        '''
                    },
                ]
            },
        }
        
        page_data = legal_content.get(page_type, legal_content['privacy'])
        context['page'] = type('Page', (), page_data)()
        context['sections'] = page_data['sections']
        context['page_type'] = page_type
        
        return context
