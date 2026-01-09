"""
CMS app views for static page rendering.

These views provide static versions of CMS pages for when
Wagtail CMS pages haven't been created yet.
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from cms.models import PatientReview, FAQItem, LegalPageSection


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
    
    PAGE_TITLES = {
        'privacy': 'Privacy Policy',
        'terms': 'Terms of Service',
        'cookies': 'Cookie Policy',
    }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_type = self.kwargs.get('page_type', 'privacy')
        
        # Get sections from database
        sections = LegalPageSection.objects.filter(page_type=page_type).order_by('order', 'title')
        
        # Create page object with title
        context['page'] = {
            'title': self.PAGE_TITLES.get(page_type, 'Legal'),
            'last_updated': '2026-01-09',
        }
        context['sections'] = sections
        context['page_type'] = page_type
        
        return context
