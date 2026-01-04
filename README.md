# Hills Clinic

A modern, mobile-first clinic website built with Django, Wagtail CMS, and Tailwind CSS.

## Documentation

- **Tech Stack**: [docs/tech-stack.md](docs/tech-stack.md)
- **Sitemap & Implementation Details**: [docs/sitemap-implementation.md](docs/sitemap-implementation.md)

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for Tailwind build pipeline, optional)

### Setup

```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Install dependencies (already done)
pip install -r requirements.txt

# 3. Run migrations (already done)
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver
```

### Access Points
- **Public site**: http://localhost:8000/
- **Wagtail CMS**: http://localhost:8000/cms/
- **Django Admin**: http://localhost:8000/admin/

## Project Structure

```
HillsClinic/
├── hillsclinic/       # Django project settings
├── core/              # Core utilities and shared code
├── cms/               # Wagtail page models and blocks
├── booking/           # Appointment booking app
├── portal/            # Patient portal app
├── accounts/          # User authentication app
├── templates/         # Base templates and partials
├── static/            # CSS, JS, images
├── media/             # User uploads (gitignored)
├── docs/              # Project documentation
├── requirements.txt   # Python dependencies
├── manage.py          # Django management
└── .env               # Environment variables (gitignored)
```

## Tech Stack

- **Backend**: Django 6, Wagtail 7, Django REST Framework
- **Frontend**: Tailwind CSS (CDN), HTMX, Alpine.js
- **Database**: SQLite (dev), PostgreSQL (production)
- **Auth**: django-allauth, django-guardian
- **Caching**: Redis (optional)
- **Tasks**: Celery (optional)

