"""
Management command to set up blog with sample articles.
Usage: python manage.py setup_blog
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page
from cms.models import BlogIndexPage, BlogPage, HomePage
from datetime import date, timedelta
import json


class Command(BaseCommand):
    help = 'Creates BlogIndexPage and sample blog articles'

    def handle(self, *args, **options):
        # Find the homepage
        try:
            homepage = HomePage.objects.first()
            if not homepage:
                self.stdout.write(self.style.ERROR('No HomePage found. Run setup_homepage first.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error finding HomePage: {e}'))
            return
        
        # Check if blog index already exists
        blog_index = BlogIndexPage.objects.first()
        if blog_index:
            self.stdout.write(self.style.WARNING('BlogIndexPage already exists, skipping creation.'))
        else:
            # Create the blog index page
            blog_index = BlogIndexPage(
                title="Blog",
                slug="blog",
                introduction="<p>Latest insights, research, and educational content about limb lengthening surgery from Hills Clinic medical team.</p>",
                seo_title="Blog - Hills Clinic | Limb Lengthening News & Insights",
                search_description="Explore educational articles, patient stories, and the latest research about limb lengthening surgery from Hills Clinic.",
            )
            homepage.add_child(instance=blog_index)
            blog_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f'Created BlogIndexPage: {blog_index.title}'))
        
        # Sample articles data
        sample_articles = [
            {
                'title': 'Understanding the LON Method: A Comprehensive Guide',
                'slug': 'understanding-lon-method-comprehensive-guide',
                'author': 'Dr. Ahmed Hassan',
                'category': 'procedures',
                'introduction': '<p>The LON (Lengthening Over Nail) method represents one of the most advanced techniques in limb lengthening surgery. This article explores how this hybrid approach combines the best of both external and internal fixation methods.</p>',
                'body': json.dumps([
                    {'type': 'heading', 'value': {'heading_text': 'What is the LON Method?', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>The LON method is a sophisticated surgical technique that combines an external fixator with an internal intramedullary nail. This hybrid approach allows patients to benefit from controlled lengthening while minimizing the time spent with external hardware.</p><p>During the distraction phase, the external fixator guides bone growth at approximately 1mm per day. Once the desired length is achieved, the external fixator is removed while the internal nail provides stability during the consolidation phase.</p>'},
                    {'type': 'heading', 'value': {'heading_text': 'Benefits of LON Method', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p><strong>Reduced External Fixator Time:</strong> Unlike traditional methods, LON significantly reduces the duration of external fixation, typically by 40-50%.</p><p><strong>Greater Stability:</strong> The internal nail provides superior stability during consolidation, reducing the risk of bone deviation.</p><p><strong>Faster Recovery:</strong> Patients can often begin weight-bearing activities sooner than with purely external methods.</p>'},
                ]),
                'days_ago': 5,
            },
            {
                'title': 'Nutrition Guide: Optimizing Bone Healing After Limb Lengthening',
                'slug': 'nutrition-guide-bone-healing-limb-lengthening',
                'author': 'Dr. Sarah Mitchell',
                'category': 'nutrition',
                'introduction': '<p>Proper nutrition plays a crucial role in bone regeneration and healing after limb lengthening surgery. This comprehensive guide covers essential nutrients, meal planning, and dietary recommendations for optimal recovery.</p>',
                'body': json.dumps([
                    {'type': 'heading', 'value': {'heading_text': 'Essential Nutrients for Bone Healing', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p><strong>Calcium:</strong> The primary building block of bone tissue. Adults need 1000-1200mg daily, with increased requirements during bone regeneration. Sources include dairy products, leafy greens, and fortified foods.</p><p><strong>Vitamin D:</strong> Essential for calcium absorption. We recommend 2000-4000 IU daily during recovery. Sunlight exposure and supplements are the primary sources.</p><p><strong>Protein:</strong> Critical for bone matrix formation. Aim for 1.2-1.5g per kg of body weight daily. Quality sources include lean meats, fish, eggs, legumes, and dairy.</p>'},
                    {'type': 'heading', 'value': {'heading_text': 'Foods to Include', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>Your recovery diet should emphasize whole, nutrient-dense foods. Include plenty of leafy green vegetables, fatty fish like salmon and sardines, nuts and seeds, lean proteins, and calcium-rich dairy products. Bone broth is particularly beneficial due to its collagen content.</p>'},
                ]),
                'days_ago': 12,
            },
            {
                'title': 'Recovery Timeline: What to Expect After Height Lengthening Surgery',
                'slug': 'recovery-timeline-height-lengthening-surgery',
                'author': 'Dr. Michael Chen',
                'category': 'recovery',
                'introduction': '<p>Understanding the recovery timeline helps patients prepare mentally and physically for their limb lengthening journey. This article outlines the key phases of recovery from surgery through full return to activities.</p>',
                'body': json.dumps([
                    {'type': 'heading', 'value': {'heading_text': 'Phase 1: Distraction (Lengthening)', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>The distraction phase begins approximately 5-7 days after surgery. During this phase, the bone is gradually lengthened at a rate of about 1mm per day. For a 2-inch (5cm) gain, this phase lasts approximately 50 days. Physical therapy is essential during this time to maintain joint flexibility and muscle strength.</p>'},
                    {'type': 'heading', 'value': {'heading_text': 'Phase 2: Consolidation', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>Once target length is reached, the consolidation phase begins. New bone forms and hardens in the gap created during distraction. This phase typically lasts 2-3 months. Gradual weight-bearing is introduced under physical therapy guidance.</p>'},
                    {'type': 'heading', 'value': {'heading_text': 'Phase 3: Full Recovery', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>Full recovery and return to normal activities typically occurs 6-12 months after surgery. Most patients can return to sports and high-impact activities within one year, though individual timelines vary based on procedure type and personal factors.</p>'},
                ]),
                'days_ago': 20,
            },
            {
                'title': 'New Research: Long-Term Outcomes of Limb Lengthening Surgery',
                'slug': 'research-long-term-outcomes-limb-lengthening',
                'author': 'Dr. Robert Williams',
                'category': 'research',
                'introduction': '<p>A recent multi-center study published in the Journal of Orthopedic Research examines the long-term outcomes of over 1,000 limb lengthening patients over a 10-year follow-up period.</p>',
                'body': json.dumps([
                    {'type': 'heading', 'value': {'heading_text': 'Study Overview', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>The study followed 1,247 patients who underwent limb lengthening surgery between 2010 and 2020 at multiple international centers. Researchers evaluated bone health, joint function, quality of life, and overall satisfaction at various intervals.</p>'},
                    {'type': 'heading', 'value': {'heading_text': 'Key Findings', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p><strong>Success Rate:</strong> 97.3% of patients achieved their target height with no major complications. <strong>Patient Satisfaction:</strong> 94% reported being satisfied or very satisfied with their results at 5-year follow-up. <strong>Bone Strength:</strong> Long-term bone density measurements showed no significant differences from pre-surgical levels.</p>'},
                    {'type': 'heading', 'value': {'heading_text': 'Implications for Patients', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>These findings provide strong evidence for the safety and durability of modern limb lengthening procedures. Patients can be confident that the results achieved are long-lasting and do not compromise bone health in the long term.</p>'},
                ]),
                'days_ago': 8,
            },
            {
                'title': 'Hills Clinic Opens New Rehabilitation Center',
                'slug': 'hills-clinic-opens-new-rehabilitation-center',
                'author': 'Hills Clinic Team',
                'category': 'news',
                'introduction': '<p>Hills Clinic is proud to announce the opening of our state-of-the-art rehabilitation center, designed specifically to support limb lengthening patients through their recovery journey.</p>',
                'body': json.dumps([
                    {'type': 'heading', 'value': {'heading_text': 'World-Class Facilities', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>Our new 5,000 square meter rehabilitation center features the latest physical therapy equipment, hydrotherapy pools, and specialized gait analysis technology. The facility was designed in consultation with leading physical therapists specializing in orthopedic rehabilitation.</p>'},
                    {'type': 'heading', 'value': {'heading_text': 'Comprehensive Care Approach', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>The rehabilitation center integrates seamlessly with our surgical services, providing patients with a comprehensive care experience from consultation through full recovery. Our team of 15 specialized physical therapists work alongside surgeons to create personalized recovery plans.</p>'},
                ]),
                'days_ago': 3,
            },
            {
                'title': 'Managing Pain During Limb Lengthening: Evidence-Based Approaches',
                'slug': 'managing-pain-limb-lengthening-evidence-based',
                'author': 'Dr. Lisa Thompson',
                'category': 'patient-care',
                'introduction': '<p>Effective pain management is essential for a successful limb lengthening experience. This article reviews evidence-based approaches to pain control during the distraction and consolidation phases.</p>',
                'body': json.dumps([
                    {'type': 'heading', 'value': {'heading_text': 'Multimodal Pain Management', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>Modern pain management for limb lengthening employs a multimodal approach, combining multiple techniques to achieve optimal comfort while minimizing medication side effects. This includes scheduled analgesics, nerve blocks, physical therapy, and complementary therapies.</p>'},
                    {'type': 'heading', 'value': {'heading_text': 'Medication Protocols', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>Our protocol emphasizes non-opioid medications as first-line treatment. NSAIDs, acetaminophen, and gabapentinoids form the foundation of our approach. Opioids are reserved for breakthrough pain and are carefully managed to prevent dependence.</p>'},
                    {'type': 'heading', 'value': {'heading_text': 'Non-Pharmacological Approaches', 'size': 'h2'}},
                    {'type': 'paragraph', 'value': '<p>Complementary therapies play a significant role in our pain management strategy. These include therapeutic massage, acupuncture, guided meditation, and sleep optimization. Many patients find these approaches highly effective for managing discomfort.</p>'},
                ]),
                'days_ago': 15,
            },
        ]
        
        # Create sample articles
        created_count = 0
        for article_data in sample_articles:
            # Check if article already exists
            if BlogPage.objects.filter(slug=article_data['slug']).exists():
                self.stdout.write(f'  Article "{article_data["title"]}" already exists, skipping.')
                continue
            
            article = BlogPage(
                title=article_data['title'],
                slug=article_data['slug'],
                author=article_data['author'],
                date=date.today() - timedelta(days=article_data['days_ago']),
                category=article_data['category'],
                introduction=article_data['introduction'],
                body=article_data['body'],
                seo_title=f"{article_data['title']} - Hills Clinic Blog",
                search_description=article_data['introduction'][:155].replace('<p>', '').replace('</p>', ''),
            )
            blog_index.add_child(instance=article)
            article.save_revision().publish()
            created_count += 1
            self.stdout.write(f'  Created article: {article.title}')
        
        self.stdout.write(self.style.SUCCESS(f'\nBlog setup complete! Created {created_count} new articles.'))
        self.stdout.write(f'\nBlog URL: /blog/')
