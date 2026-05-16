# Django 500 Error Analysis - Hills Clinic Deployment

## Summary
Your deployment likely crashed due to **multiple Redis dependency issues** combined with **Wagtail page tree initialization problems**. The 500 errors would have appeared 1-2 months in after automatic background tasks tried to access Redis or cache backend.

---

## Critical Issues Found

### 🔴 **ISSUE #1: Redis Dependency Chain Failure (Most Likely Culprit)**

**Location:** [hillsclinic/settings.py](hillsclinic/settings.py#L150-L163)

**Problem:**
```python
# Cache tries to use Redis if REDIS_URL env var exists
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        ...
    }
} if os.getenv("REDIS_URL") else { ... }

# Celery hardcodes Redis URLs without fallback
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")

# Sessions use cached_db backend
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
```

**Why it fails:**
- Render's **free tier** PostgreSQL does NOT include Redis
- When environment variables are missing, Redis defaults to `localhost:6379` (not available)
- Celery tasks fail silently, then Wagtail's background indexing crashes
- If cache backend can't connect, sessions break and users get 500 errors

**Impact:**
- ✗ Background tasks fail
- ✗ Session management crashes
- ✗ Wagtail search indexing breaks
- ✗ Any page that uses `@cached_property` or cache operations fails

---

### 🔴 **ISSUE #2: Missing set_site_domain Custom Command**

**Location:** [render.yaml](render.yaml#L14)

**Problem:**
```yaml
buildCommand: "... && python manage.py set_site_domain && ..."
```

The `set_site_domain` command is called in build but the command file is missing:
- File not found: `accounts/management/commands/set_site_domain.py` ❌
- This would cause the **build to fail** immediately

**Impact:**
- ✗ Deployment would fail at the build step
- ✗ Even if it somehow got past, Django `Site` model would be misconfigured

---

### 🟡 **ISSUE #3: Wagtail Page Tree Initialization Race Condition**

**Location:** [cms/management/commands/setup_homepage.py](cms/management/commands/setup_homepage.py#L31)

**Problem:**
```python
# Command tries to fix/create page tree during deployment
Page.fix_tree()
root = Page.objects.get(depth=1)  # Fails if root doesn't exist
```

**Why it fails:**
- If migrations run but the Wagtail root page isn't created first, this crashes
- Multiple concurrent build processes could corrupt the page tree
- No rollback if the homepage creation fails partway through

**Impact:**
- ✗ Homepage may not exist
- ✗ Admin panel might be inaccessible
- ✗ Any view that references the homepage crashes with 500 error

---

### 🟡 **ISSUE #4: Cloudinary Credentials Not Validated at Startup**

**Location:** [hillsclinic/settings.py](hillsclinic/settings.py#L290-L310)

**Problem:**
```python
if os.getenv("CLOUDINARY_CLOUD_NAME"):
    import cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )
```

**Why it fails:**
- Cloudinary credentials configured but never validated
- If credentials expire or are invalid, media uploads silently fail
- When Django tries to serve/save media files, it crashes with 500 error
- Particularly problematic for doctor photos and patient uploads

**Impact:**
- ✗ Media operations fail silently
- ✗ Any page with images causes 500 error
- ✗ Database migrations with media fields may fail

---

### 🟡 **ISSUE #5: Django Tasks Backend Custom Implementation**

**Location:** [hillsclinic/settings.py](hillsclinic/settings.py#L395-L399)

**Problem:**
```python
TASKS = {
    "default": {
        "BACKEND": "hillsclinic.tasks_backend.SafeDummyBackend"
    }
}
```

**Why it might fail:**
- Custom backend file `hillsclinic/tasks_backend.py` must exist and be correctly implemented
- If this import fails, Django crashes during startup
- Wagtail search indexing depends on this

---

## Timeline of How 500 Error Likely Occurred

1. **Initial Deployment (Week 1):** 
   - Build might have passed if `set_site_domain` was skipped/ignored
   - If not, deployment failed immediately

2. **Running Fine (Weeks 1-2):**
   - Direct page views worked (no cache needed)
   - Django served requests without background tasks

3. **500 Errors Start (Weeks 4-8):**
   - Browser sessions expire → Django tries to use cache backend → Redis missing → 500 error
   - Wagtail background indexing runs → needs Celery → Redis missing → crashes
   - Media operations accumulate errors
   - Logs would show Redis connection refused errors

---

## Root Cause Summary

| Component | Issue | Severity |
|-----------|-------|----------|
| **Redis/Cache** | No Redis in Render free tier | 🔴 Critical |
| **Celery** | Hardcoded Redis defaults | 🔴 Critical |
| **set_site_domain command** | Missing implementation | 🔴 Critical |
| **Wagtail Page Tree** | Initialization race condition | 🟡 High |
| **Cloudinary** | Invalid credentials | 🟡 Medium |
| **Tasks Backend** | Custom implementation fragility | 🟡 Medium |

---

## Recommendations

### Immediate Fixes (Required for re-deployment)

1. **Remove Redis Dependencies:**
   - Switch to database-backed sessions
   - Use synchronous Celery tasks or queue
   - Use dummy cache backend for production

2. **Implement set_site_domain Command:**
   - Create [accounts/management/commands/set_site_domain.py](accounts/management/commands/set_site_domain.py)

3. **Fix Wagtail Setup:**
   - Ensure root page exists before running setup_homepage
   - Use transactions to prevent race conditions

4. **Validate External Services:**
   - Check Cloudinary credentials at startup
   - Test email backend connectivity
   - Validate database connection before accepting requests

### Medium-term Improvements

- Add health checks endpoint
- Implement proper error logging to external service
- Add startup validation script
- Use Render's environment variable management properly
- Consider upgrading from free tier for production

---

## Next Steps

Would you like me to:
1. Fix these issues in the code? ✓ Recommended
2. Create the missing `set_site_domain` command?
3. Add startup validation checks?
4. Update render.yaml for free-tier compatibility?
