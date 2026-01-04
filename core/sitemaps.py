"""
SEO-related views and sitemaps for Hills Clinic.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static views."""
    priority = 0.5
    changefreq = 'weekly'
    
    def items(self):
        return [
            'cms:procedures',
            'cms:international',
            'cms:cost',
            'cms:recovery',
            'cms:success-stories',
            'cms:faq',
            'cms:privacy',
            'cms:terms',
            'cms:cookies',
            'booking:consultation',
            'booking:contact',
        ]
    
    def location(self, item):
        return reverse(item)


class ProceduresSitemap(Sitemap):
    """Sitemap for procedure detail pages."""
    priority = 0.8
    changefreq = 'monthly'
    
    def items(self):
        return ['ilizarov', 'internal-nail', 'lon']
    
    def location(self, item):
        return reverse('cms:procedure-detail', kwargs={'procedure_type': item})


class BlogSitemap(Sitemap):
    """Sitemap for blog articles."""
    priority = 0.7
    changefreq = 'weekly'
    
    def items(self):
        from cms.models import BlogPage
        return BlogPage.objects.live()
    
    def lastmod(self, obj):
        return obj.last_published_at
    
    def location(self, obj):
        return obj.url


class DoctorSitemap(Sitemap):
    """Sitemap for doctor/team member profiles."""
    priority = 0.7
    changefreq = 'monthly'
    
    def items(self):
        from core.models import Doctor
        return Doctor.objects.filter(is_active=True)
    
    def location(self, obj):
        return obj.get_absolute_url()


class TeamPageSitemap(Sitemap):
    """Sitemap for the team listing page."""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return ['core:team']
    
    def location(self, item):
        return reverse(item)


class HomepageSitemap(Sitemap):
    """Sitemap for the homepage."""
    priority = 1.0
    changefreq = 'daily'
    
    def items(self):
        return ['homepage']
    
    def location(self, item):
        return '/'
