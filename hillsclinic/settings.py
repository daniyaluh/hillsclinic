"""
Django settings for Hills Clinic project.

Configured for Django 6 + Wagtail + DRF + django-allauth + django-guardian.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# SECURITY
# =============================================================================
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-only-change-in-production")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "http://localhost:8000").split(",")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")

# Custom User Model
AUTH_USER_MODEL = "accounts.CustomUser"

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.postgres",
    
    # Wagtail CMS
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    
    # Wagtail dependencies
    "modelcluster",
    "taggit",
    
    # Third-party
    "rest_framework",
    "django_htmx",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "guardian",
    "django_redis",
    "cloudinary_storage",
    "cloudinary",
    
    # Project apps
    "core.apps.CoreConfig",
    "cms.apps.CmsConfig",
    "booking.apps.BookingConfig",
    "portal.apps.PortalConfig",
    "accounts.apps.AccountsConfig",
    "staff.apps.StaffConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "booking.middleware.AppointmentStatusMiddleware",  # Auto-complete past appointments
]

ROOT_URLCONF = "hillsclinic.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                "core.context_processors.site_settings",
                "core.context_processors.language_context",
            ],
        },
    },
]

WSGI_APPLICATION = "hillsclinic.wsgi.application"
ASGI_APPLICATION = "hillsclinic.asgi.application"

# =============================================================================
# DATABASE
# =============================================================================
# Default: SQLite for development. Use PostgreSQL in production.
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

# Use DATABASE_URL if provided (for Render, Railway, Heroku, etc.)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )

# =============================================================================
# CACHING (Redis)
# =============================================================================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
} if os.getenv("REDIS_URL") else {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Session backend (use cache in production)
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# =============================================================================
# AUTHENTICATION
# =============================================================================
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "guardian.backends.ObjectPermissionBackend",
]

SITE_ID = 1

# django-allauth settings (production-grade email verification)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
# Email verification is mandatory - users must verify email to login
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = False  # POST-only confirmation (secure)
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3  # Token expires in 3 days
ACCOUNT_SESSION_REMEMBER = None  # None = show checkbox, True = always remember, False = never remember
ACCOUNT_FORMS = {
    "signup": "accounts.forms.CustomSignupForm",
}
ACCOUNT_ADAPTER = "accounts.adapter.CustomAccountAdapter"  # Custom adapter to handle email errors
LOGIN_REDIRECT_URL = "/login-redirect/"  # Smart redirect: staff → /staff/, patients → /portal/
ACCOUNT_SIGNUP_REDIRECT_URL = "/portal/"  # Go directly to portal after signup
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https" if not DEBUG else "http"

# Session settings for "Remember Me"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days when "Remember Me" is checked
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Don't expire on browser close if remembered

# Rate limiting (modern allauth syntax)
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/5m",  # 5 failed login attempts per 5 minutes
}

# django-guardian
ANONYMOUS_USER_NAME = None

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Karachi"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =============================================================================
# INTERNATIONALIZATION (i18n)
# =============================================================================
LANGUAGES = [
    ("en", "English"),
    ("ar", "العربية"),  # Arabic
    ("tr", "Türkçe"),   # Turkish
    ("ru", "Русский"),  # Russian
    ("fa", "فارسی"),    # Persian/Farsi
]

# RTL (Right-to-Left) languages
RTL_LANGUAGES = ['ar', 'fa']

LOCALE_PATHS = [BASE_DIR / "locale"]

# Language cookie settings
LANGUAGE_COOKIE_NAME = 'hills_language'
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60  # 1 year

# =============================================================================
# STATIC & MEDIA FILES
# =============================================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise for static file serving
# Use Cloudinary for media storage in production
if os.getenv("CLOUDINARY_CLOUD_NAME"):
    import cloudinary
    
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )
    
    # MediaCloudinaryStorage for site images (doctor photos, logos, before/after)
    # Patient uploads use RawMediaCloudinaryStorage via custom storage in portal/models.py
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
        "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
        "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =============================================================================
# WAGTAIL SETTINGS
# =============================================================================
WAGTAIL_SITE_NAME = "Hills Clinic"
WAGTAILADMIN_BASE_URL = os.getenv("WAGTAIL_BASE_URL", "http://localhost:8000")

# Search backend
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Image settings
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Embeds (for video testimonials)
WAGTAILEMBEDS_RESPONSIVE_HTML = True

# =============================================================================
# DJANGO REST FRAMEWORK
# =============================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# =============================================================================
# EMAIL
# =============================================================================
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@hillsclinic.com")
EMAIL_FILE_PATH = os.getenv("EMAIL_FILE_PATH", str(BASE_DIR / "tmp" / "emails"))

# Create file-based email directory automatically in development
if EMAIL_BACKEND == "django.core.mail.backends.filebased.EmailBackend":
    os.makedirs(EMAIL_FILE_PATH, exist_ok=True)

# =============================================================================
# SECURITY SETTINGS (production)
# =============================================================================
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# =============================================================================
# LOGGING
# =============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "django.mail": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "allauth": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "wagtail": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# =============================================================================
# DJANGO TASKS (for Wagtail search indexing)
# =============================================================================
# Custom backend to avoid Python 3.12 typing bug in django_tasks
TASKS = {
    "default": {
        "BACKEND": "hillsclinic.tasks_backend.SafeDummyBackend"
    }
}

# =============================================================================
# CELERY (for background tasks)
# =============================================================================
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# SITE CONFIGURATION
# =============================================================================
HILLS_CLINIC_WHATSAPP = os.getenv("WHATSAPP_NUMBER", "+923015943329")
HILLS_CLINIC_EMAIL = os.getenv("CLINIC_EMAIL", "info@hillsclinic.com")
HILLS_CLINIC_PHONE = os.getenv("CLINIC_PHONE", "+92-42-35761234")
HILLS_CLINIC_ADDRESS = os.getenv("CLINIC_ADDRESS", "Hills Clinic, DHA Phase 5, Lahore, Pakistan")

# =============================================================================
# STRIPE PAYMENT CONFIGURATION
# =============================================================================
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Payment amounts (in cents)
STRIPE_CONSULTATION_FEE = int(os.getenv("STRIPE_CONSULTATION_FEE", "15000"))  # $150
STRIPE_DEPOSIT_AMOUNT = int(os.getenv("STRIPE_DEPOSIT_AMOUNT", "100000"))  # $1,000
