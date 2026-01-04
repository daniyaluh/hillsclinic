# Hills Clinic Tech Stack

Date: 2025-12-26

## Overview
A fast, secure, mobile-first stack optimized for international patients, strong SEO, privacy/compliance, and low cost. Centered on Django + Wagtail with server-side rendering, minimal JS, and a clean separation of public content vs. secure patient portal.

## Goals
- Fast SSR pages, global caching/CDN, responsive media
- Strong security: RBAC, consent lifecycle, audit logs, encryption
- Modern, accessible UI with RTL support (Arabic/Persian)
- Mobile-first UX and performance budgets
- Minimize cost with open-source tooling and free tiers

## Frontend
- Rendering: Django templates + Wagtail pages (SSR)
- Styling: Tailwind CSS; Headless UI; daisyUI; Heroicons/Lucide (free)
- Interactivity: HTMX + Alpine.js for forms, modals, swaps, calculators
- Accessibility: WCAG 2.2 AA; semantic components; keyboard/focus management
- Internationalization: Django i18n + Wagtail locales; RTL support

## CMS & Content
- CMS: Wagtail (open-source) for structured content and multilingual publishing
- Content models: Procedures, Methods (Ilizarov/Internal/LON), International Center, Cost & Financing, Rehab Timeline, Success Stories, Testimonials, FAQs, Articles, Legal & Compliance
- Media governance: Consent flags on assets; face-blur variants; metadata; responsive image renditions (WebP/AVIF)

## Backend
- Framework: Django 5 (ASGI) + Django Rest Framework (APIs)
- Background workers: Celery + Redis (emails, ICS generation, image processing, virus scans)
- Server: Nginx reverse proxy → Gunicorn/Uvicorn workers; HTTP/2 + Brotli
- API docs: drf-spectacular (OpenAPI)

## Data & Storage
- Database: PostgreSQL (open-source) with ORM-only access; pgbouncer for connection pooling
- Cache & sessions: Redis for cache, sessions, rate limiting, and throttling
- Object storage: Cloudflare R2 or S3-compatible storage via django-storages; signed URLs for protected assets
- CDN/TLS: Cloudflare (free) for global caching, TLS, image optimization; Let’s Encrypt certificates

## Auth & Security
- Auth: django-allauth (email/password), MFA via django-two-factor-auth (TOTP)
- RBAC: django-guardian for per-object permissions (patients, media)
- Hardening: django-csp, django-axes (brute-force protection), secure cookies (HttpOnly/SameSite), DRF throttling, input sanitization (bleach)
- Upload safety: Mime/size validation; ClamAV scan in Celery; store only in object storage
- Consent lifecycle: Explicit capture; revocation unpublishes public variants; immutable audit trail
- Privacy & compliance: GDPR-friendly cookie consent, data export/delete; documented Patient Rights, Privacy Policy, Dispute Resolution

## Integrations
- Email: Brevo/SendGrid (free tiers) or self-hosted Mailu/Postfix (deliverability trade-offs)
- SMS/WhatsApp: WhatsApp deep links (free); Twilio SMS (optional, paid)
- Calendar: ICS attachments; optional sync to Google/Microsoft later
- Analytics: Umami or Matomo (open-source, privacy-friendly)
- Search & reporting (optional): OpenSearch/Elasticsearch for search; ClickHouse for analytics

## Observability & Ops
- Error tracking: Sentry (free tier)
- Uptime: Uptime Kuma (self-hosted)
- Metrics/logs: Prometheus/Grafana or Application Insights; structured logs
- CI/CD: GitHub Actions (tests/builds/deploys)
- Hosting: Single VPS + Docker Compose (Nginx, Django, Redis, Postgres) to start; scale to managed DB/CDN later
- Backups/DR: Nightly Postgres dumps; object storage versioning; restore drills; geo-redundant storage for media

## Performance & Accessibility Targets
- JS budget: Public pages < 150KB JS; HTMX over heavy SPA bundles
- Caching: Redis page + fragment cache; Cloudflare edge caching; responsive images + lazy loading
- DB tuning: Indexes; select_related/prefetch_related; slow-query profiling
- SEO: schema.org (FAQ, Article, MedicalProcedure), sitemap.xml, robots.txt, hreflang
- Accessibility: AA contrast; 44px touch targets; RTL layouts validated

## Mobile Responsiveness
- Mobile-first styles; breakpoints: sm, md, lg, xl, 2xl
- Fluid layouts and clamp() for typography; single-column forms on mobile
- Sticky top bar, clear CTA; large tap targets; input masks and numeric keyboards
- Media: responsive srcset, AVIF/WebP, lazy load; non-blocking fonts (display=swap)

## Database Replaceability & Scale Path
- Portability: Strict ORM usage; avoid vendor-specific features; UUID IDs; reversible migrations
- Scale-up (Postgres-first): pgbouncer, Redis caching, read replicas, partitioning (e.g., pg_partman)
- Managed Postgres: Migrate to managed service for HA/backup; later Postgres-compatible distributed DBs (CockroachDB/YugabyteDB) if necessary
- Migration playbook: CDC (Debezium/logical replication), dual-write, shadow reads, canary cutover, validation, rollback plan

## Cost-Minimization
- Free CDN/TLS: Cloudflare + Let’s Encrypt
- Open-source core: Django, Wagtail, DRF, Redis, Postgres, Celery
- Free tiers: Sentry, GitHub Actions; Umami analytics; Uptime Kuma
- Hosting: Start on a single VPS with Docker Compose; upgrade gradually

## Viable Alternative (if JS-heavy team)
- Next.js + Headless CMS (Sanity/Contentful) + NestJS or .NET API; excellent edge performance; higher ops complexity vs. Django’s integrated approach

## Notes
- Reserve React for truly complex portal modules; prefer HTMX/Alpine.js for most interactivity
- Enforce security headers and rate limits early; maintain auditability for portal actions
- Treat images/X-rays as sensitive; store in object storage; serve via signed URLs; face-blur variants by default
