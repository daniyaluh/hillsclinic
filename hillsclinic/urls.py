"""
URL configuration for Hills Clinic project.

Routes:
- /admin/         Django admin
- /cms/           Wagtail admin
- /documents/     Wagtail documents
- /api/           REST API
- /accounts/      User authentication (allauth)
- /booking/       Appointment booking
- /portal/        Patient portal
- /sitemap.xml    XML Sitemap
- /robots.txt     Robots exclusion protocol
- /i18n/          Language switching
- /               Wagtail pages (catch-all)
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from core.sitemaps import (
    StaticViewSitemap, ProceduresSitemap, HomepageSitemap, 
    BlogSitemap, DoctorSitemap, TeamPageSitemap
)
from core.views import robots_txt

# Sitemaps configuration
sitemaps = {
    'static': StaticViewSitemap,
    'procedures': ProceduresSitemap,
    'homepage': HomepageSitemap,
    'blog': BlogSitemap,
    'doctors': DoctorSitemap,
    'team': TeamPageSitemap,
}

urlpatterns = [
    # Language switching
    path("i18n/", include("django.conf.urls.i18n")),
    
    # SEO
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    
    # Django admin
    path("admin/", admin.site.urls),
    
    # Wagtail CMS admin
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    
    # REST API
    path("api/", include("rest_framework.urls")),
    
    # Authentication
    path("accounts/", include("allauth.urls")),
    
    # Apps
    path("booking/", include("booking.urls")),
    path("portal/", include("portal.urls")),
    path("staff/", include("staff.urls")),
    path("", include("core.urls")),
    
    # CMS static pages (before Wagtail catch-all)
    path("", include("cms.urls")),
    
    # Wagtail pages (catch-all - must be last)
    path("", include(wagtail_urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

