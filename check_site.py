"""Check Wagtail site configuration."""
from wagtail.models import Site, Page
from cms.models import HomePage

# Check site configuration
site = Site.objects.get(is_default_site=True)
print(f"Site: {site}")
print(f"Site hostname: {site.hostname}")
print(f"Site port: {site.port}")
print(f"Site root page: {site.root_page}")
print(f"Root page ID: {site.root_page.id}")
print(f"Root page type: {type(site.root_page)}")
print(f"Root page URL path: {site.root_page.url_path}")

# Check all pages
print("\nAll pages:")
for page in Page.objects.all():
    print(f"  ID {page.id}: {page.title} ({page.content_type}) - depth {page.depth} - {page.url_path}")

# Check if homepage exists
print("\nHomePages:")
for hp in HomePage.objects.all():
    print(f"  {hp.title} - {hp.get_url()}")
