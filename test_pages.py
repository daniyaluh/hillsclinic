"""Test script to validate all pages work correctly."""
import requests

BASE_URL = 'http://127.0.0.1:8000'

def test_public_pages():
    """Test all public pages."""
    print("=" * 60)
    print("Testing PUBLIC pages...")
    print("=" * 60)
    
    pages = [
        ('/', 'Homepage'),
        ('/procedures/', 'Procedures'),
        ('/procedures/ilizarov/', 'Ilizarov Procedure'),
        ('/procedures/internal-nail/', 'Internal Nail'),
        ('/procedures/lon/', 'LON Method'),
        ('/international/', 'International'),
        ('/cost/', 'Cost'),
        ('/recovery/', 'Recovery'),
        ('/success-stories/', 'Success Stories'),
        ('/faq/', 'FAQ'),
        ('/booking/consultation/', 'Consultation Booking'),
        ('/booking/contact/', 'Contact'),
        ('/accounts/login/', 'Login'),
        ('/accounts/signup/', 'Signup'),
    ]
    
    for url, name in pages:
        try:
            r = requests.get(f'{BASE_URL}{url}', timeout=5)
            if r.status_code == 200:
                if 'TemplateSyntaxError' in r.text or 'NoReverseMatch' in r.text:
                    print(f"TEMPLATE ERROR - {name} ({url})")
                else:
                    print(f"OK 200 - {name} ({url})")
            else:
                print(f"ERROR {r.status_code} - {name} ({url})")
        except Exception as e:
            print(f"FAIL - {name} ({url}) - {e}")


def test_portal_pages():
    """Test portal pages (requires login)."""
    print("\n" + "=" * 60)
    print("Testing PORTAL pages (authenticated)...")
    print("=" * 60)
    
    s = requests.Session()
    
    # Get CSRF token from login page
    login_page = s.get(f'{BASE_URL}/accounts/login/')
    csrf_token = None
    
    import re
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
    if match:
        csrf_token = match.group(1)
    
    if not csrf_token:
        print("ERROR: Could not get CSRF token")
        return
    
    # Login
    login_resp = s.post(f'{BASE_URL}/accounts/login/', data={
        'csrfmiddlewaretoken': csrf_token,
        'login': 'technofriend18@gmail.com',
        'password': '12345',
    }, allow_redirects=True)
    
    # Check if login worked by accessing portal
    portal_check = s.get(f'{BASE_URL}/portal/', allow_redirects=False)
    if portal_check.status_code == 302:
        print("ERROR: Login failed - still redirecting to login")
        return
    
    print("Logged in successfully!")
    
    pages = [
        ('/portal/', 'Portal Dashboard'),
        ('/portal/profile/', 'Portal Profile'),
        ('/portal/documents/', 'Portal Documents'),
        ('/portal/documents/upload/', 'Portal Document Upload'),
        ('/portal/consents/', 'Portal Consents'),
        ('/portal/appointments/', 'Portal Appointments'),
        ('/portal/appointments/book/', 'Portal Book Appointment'),
    ]
    
    for url, name in pages:
        try:
            r = s.get(f'{BASE_URL}{url}', timeout=5)
            if r.status_code == 200:
                if 'TemplateSyntaxError' in r.text:
                    print(f"TEMPLATE SYNTAX ERROR - {name} ({url})")
                elif 'NoReverseMatch' in r.text:
                    print(f"URL REVERSE ERROR - {name} ({url})")
                elif 'DoesNotExist' in r.text:
                    print(f"MODEL ERROR - {name} ({url})")
                else:
                    print(f"OK 200 - {name} ({url})")
            else:
                print(f"ERROR {r.status_code} - {name} ({url})")
        except Exception as e:
            print(f"FAIL - {name} ({url}) - {e}")


def test_api_endpoints():
    """Test API endpoints."""
    print("\n" + "=" * 60)
    print("Testing API endpoints...")
    print("=" * 60)
    
    s = requests.Session()
    
    # Login first
    login_page = s.get(f'{BASE_URL}/accounts/login/')
    import re
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
    if match:
        csrf_token = match.group(1)
        s.post(f'{BASE_URL}/accounts/login/', data={
            'csrfmiddlewaretoken': csrf_token,
            'login': 'technofriend18@gmail.com',
            'password': '12345',
        }, allow_redirects=True)
    
    # Test time slots API
    r = s.get(f'{BASE_URL}/portal/api/time-slots/?date=2025-12-31')
    if r.status_code == 200:
        print(f"OK 200 - Time Slots API")
    else:
        print(f"ERROR {r.status_code} - Time Slots API")


if __name__ == '__main__':
    test_public_pages()
    test_portal_pages()
    test_api_endpoints()
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
