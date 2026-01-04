# Hills Clinic Sitemap - Implementation Details

Date: 2025-12-26  
Based on: [SiteMap.txt](../SiteMap.txt)

## Overview
Detailed breakdown of all pages, sections, and features to implement. Organized by user journey and functional domain.

---

## 1. Home Page

### Hero Section
- **Content**: "Transform Your Height, Transform Your Life"
- **CTAs**: "Schedule Consultation", "View Gallery"
- **Tech**: HTMX button actions; modals for quick booking or gallery preview
- **Design**: Full-width, mobile-optimized hero; responsive background image

### Key Statistics (Animated Counters)
- "2-6 inches gain"
- "98%+ Success Rate"
- "40+ Countries"
- "14+ Years"
- **Tech**: Alpine.js intersection observer + count-up animations; server-rendered baseline
- **Performance**: Lazy-load via HTMX or CSS intersection API

### Method Snippets
- Brief intro: Ilizarov vs. Internal Nails comparison
- **Tech**: Clickable/hover cards linking to full Procedures page
- **Content**: Sourced from Wagtail CMS procedure models

### Why Choose Us Section
- "International Standards"
- "Multilingual Support"
- "Cost Savings"
- **Tech**: Icon grid with Heroicons/Lucide; Tailwind responsive layout
- **Design**: mobile-first stacking; expandable details on larger screens

### Testimonial Slider
- Featured quotes: Sarah (UK), Ahmed (UAE)
- **Tech**: HTMX carousel or Alpine.js slider; auto-play with pause on hover
- **Media**: Profile images; fade-in on visibility

### Footer
- Licensing info, Quick Links
- "Licensed Medical Facility" badge
- **Tech**: Static content + dynamic quick links from Wagtail menu
- **Compliance**: Display PMDC certification, ISO/WHO standards badges

---

## 2. Procedures & Treatments

### Page Layout
- **Sidebar/nav**: Procedure categories (Overview, Methods, Outcomes, Risks, FAQ)
- **Main content**: Expandable sections per category

### Limb Lengthening Overview
- **What is Distraction Osteogenesis?**: Definition, mechanism, benefits
- **Am I a Candidate?**:
  - Age requirements (18+)
  - Realistic expectations
  - Bone growth criteria
  - **Tech**: Collapsible FAQ or accordion; link to booking for consultation
- **Conditions Treated**: 
  - Short stature
  - Limb discrepancies
  - Dwarfism
  - **Content**: List + brief descriptions; links to case studies

### Surgical Methods
Three expandable tabs or separate pages:

#### Ilizarov (External)
- "Gold Standard" messaging
- Cost-effective, high precision
- **Content**: Visual diagram or infographic; procedure steps; recovery timeline

#### Internal Nails (PRECICE/STRYDE)
- No visible hardware
- Magnetic rod technology
- Higher comfort
- **Content**: Comparison table vs. Ilizarov; patient testimonials

#### LON Method (Lengthening Over Nails)
- Combined approach
- Faster external removal
- **Content**: Diagram; when recommended; recovery benefits

**Tech for all methods**: 
- Wagtail models for each method
- Responsive comparison tables (Tailwind)
- Embedded videos or image galleries (lazy-loaded)

### Outcomes & Results
- **Height Potential**:
  - Femur: 2-3"
  - Tibia: 2-2.5"
  - Combined: 4-6"
  - **Tech**: Interactive calculator (HTMX + server-side logic) showing ranges per method
- **Permanence & Biomechanics**: 
  - "New bone is permanent"
  - "Strong as original"
  - **Content**: Medical evidence summary; link to success stories

### Risks & Safety
- **Complication Rates**: < 5% minor
- **Managing Risks**:
  - Pin site infections
  - Stiffness
  - **Tech**: Expandable risk items; each with mitigation steps; link to recovery guide
  - **Compliance**: Transparent risk messaging; consent acknowledgement

---

## 3. International Patient Center

### Travel Planning

#### Visa Guide
- **Tourist visa**: 30-90 days
- **Medical visa**: Extended stays, benefits
- **Tech**: Expandable tabs per visa type; downloadable guides (Wagtail documents); link to consulate resources
- **Content**: Localized by patient locale (detect from IP or form selection)

#### Airport Services
- Free pickup from KHI (Karachi), ISB (Islamabad), LHE (Lahore)
- **Tech**: 
  - Display pickup details per airport
  - Booking form integrated (HTMX)
  - WhatsApp/call deep links for coordination

### Accommodation

#### Hospital Suites
- Private rooms, 24/7 nursing, meals included
- **Tech**: Photo gallery with lightbox; pricing from CMS; booking CTA

#### Partner Hotels
- Budget: $15-25/night
- Premium: $50-80/night
- **Tech**: 
  - Hotel directory (list + map view if possible)
  - Links to external booking pages
  - Photos and amenities from CMS

#### Extended Stay Apartments
- $600-1000/month with kitchen
- **Tech**: Apartment listings with images; contact form for inquiries

### Cultural Support

#### Translation Services
- Arabic, Persian, Turkish support
- **Tech**: Contact form to request interpreter; staff availability scheduler

#### Religious Facilities
- Prayer areas, Halal food
- **Tech**: Photo/info section; dietary preferences in booking form

---

## 4. Cost & Financing

### Pricing Breakdown

#### Diagnostic Fees
- X-rays: PKR 2,500
- MRI: PKR 15,000
- **Tech**: Price list table (CMS-managed); currency converter (client-side or server-side)

#### Surgery Packages
- Estimated ranges: $3,000–$6,000 USD
- **Tech**: Expandable card per method; detailed breakdown of costs; CMS-configurable ranges

### Cost Comparison Calculator
- **Interactive table**:
  - Pakistan: $3–6k
  - USA: $75k+
  - UK/Europe: $50k+
  - Turkey: $12k+
- **Tech**: 
  - HTMX form to select country/method
  - Server-side calculation and validation
  - Animated bar chart or table highlighting savings
  - CMS-configurable rates to avoid hardcoding

### Payment Plans

#### Full Payment
- 10% discount upfront
- **Tech**: Option in checkout/booking form

#### 50-50 Plan
- 50% pre-op, 50% post-op
- **Tech**: Payment milestone tracker in patient portal; invoice generation

#### Payment Methods
- Int'l Wire Transfer
- Credit Cards (Stripe integration)
- Cash (on-site)
- **Tech**: 
  - Stripe integration for cards (PCI-compliant)
  - Wire transfer details (document generation)
  - Admin reconciliation dashboard

---

## 5. Recovery & Rehabilitation

### The Timeline (Interactive Module)
- **Stage-based layout**: Surgery Day → Phase 1 → Phase 2 → Phase 3 → Phase 4

#### Surgery Day
- 6:00 AM Prep
- 8:00 AM Surgery
- **Tech**: Timeline node/card; expandable details; estimated duration

#### Phase 1 (Hospital)
- 1 week post-op
- Pain management focus
- **Tech**: Day-by-day breakdown (collapsible); what to expect messaging

#### Phase 2 (Lengthening)
- 1mm/day protocol
- 4 quarter-turns daily
- **Duration**: ~4 months (variable)
- **Tech**: Calendar view showing daily targets; exercise checklist links

#### Phase 3 (Consolidation)
- Hardware removal at Month 10
- Bone hardening phase
- **Tech**: Milestone marker; prep checklist; diet/activity notes

#### Phase 4 (Return to Life)
- Sports/Running at Month 10-12
- **Tech**: Progression guide; exercise readiness assessment

### Exercise Library
- **Phase-specific activities**:
  - Week 1: Ankle pumps, passive stretches
  - Month 2: Swimming, gentle PT
  - Month 4+: Progressive strengthening, walking
- **Tech**: 
  - Filterable list by phase
  - Video demonstrations (hosted on Vimeo/Cloudflare Stream)
  - Text + image guides
  - Print-friendly checklists

### Home Routine
- Morning/Evening checklists
- **Tech**: 
  - Wagtail model for routines
  - HTMX checklist with persistent state (localStorage or backend)
  - Email/SMS reminders (optional)

### Nutrition Guide
- **Targets**:
  - Calcium: 1200mg daily
  - Protein: Per-body-weight calculation
  - Vitamin D: Supplementation guidance
- **Tech**: 
  - Nutritionist-authored content in Wagtail
  - Food list database (searchable)
  - Meal plan templates (downloadable PDFs)
  - Integration with tracking apps (optional)

---

## 6. Success Stories (Case Studies)

### Page Structure
- **Hero**: "Inspiring Journeys", gallery preview
- **Filters**: By location, method, condition, complication-resolved
- **View modes**: Grid, List, Featured carousel

### Video Testimonials
- Categories: 
  - "UK Patient"
  - "Arabic Experience"
  - "Australian Success"
- **Tech**:
  - Embedded videos (Vimeo/Cloudflare Stream)
  - Metadata: Patient name (optional), location, method, duration
  - Transcripts/captions (a11y + SEO)
  - Play button overlay; lazy-load

### Patient Profiles (Detailed Text Cases)
- **Data captured** (Wagtail model):
  - Patient initials/first name (privacy)
  - Location, age
  - Pre/post measurements
  - Procedure method, duration
  - Key milestones and outcomes
  - Challenges overcome
  - Testimonial quote
  - Consent flags (media, face-blur, publication status)

- **Case types**:
  - **International**: Ahmed (Saudi) – 5 inches gained
  - **Medical Professional**: Dr. Fatima (Lahore) – Career impact
  - **Complex Case**: Hassan – Discrepancy correction
  - **Family**: Rahman Father & Son duo
  - **Complication Handled**: David (Australia) – Infection recovery

### Before/After Gallery
- **Tech**:
  - Side-by-side slider (HTMX or Alpine.js)
  - Face-blur toggle (swap between blurred and unblurred variants)
  - Proof of consent (db flag + audit log)
  - Responsive grid for multiple pairs per case
  - Lightbox for full-res viewing

### Consent & Compliance
- **Wagtail fields**:
  - `consent_media_use` (boolean)
  - `consent_face_visible` (boolean)
  - `consent_testimonial_published` (boolean)
  - `revocation_date` (optional; triggers unpublish)
- **Tech**:
  - Audit log entry on consent change
  - Scheduled task: unpublish revoked media
  - Admin dashboard showing consent status

---

## 7. Patient Resources & Articles

### Blog/Articles
- **Topics** (Wagtail blog model):
  - "Height Discrimination: The Hidden Social Challenge" (Career/Dating impact)
  - "Optimal Nutrition for Bone Healing"
  - "Managing Pin Site Infections"
  - "Returning to Sports After Lengthening"
  - etc.
- **Features**:
  - Author, publish date, categories, tags
  - Featured image
  - Reading time estimate
  - Related articles (auto-linked)
  - Search/filter by category/tag
  - Email subscription (optional; low-cost email service)
- **Tech**:
  - Wagtail blog stream block; pagination
  - Schema.org Article markup for SEO
  - RSS feed (auto-generated by Wagtail)

### FAQs
- **Categories**:
  - General (Pain, Scars, Methods, Timeline)
  - International (Visas, Safety, Travel)
  - Recovery (Exercise, Nutrition, Hardware Removal)
  - Cost (Payment, Insurance, Financing)
- **Tech**:
  - Accordion/collapsible items
  - Schema.org FAQ markup
  - Search/filter
  - "Helpful?" votes (optional; Alpine.js)
- **Content**: Wagtail FAQ model (question, answer, category, order)

### Patient Portal (Login Required)
- **Auth**: OIDC (django-allauth) + TOTP MFA
- **Features**:
  - Digital X-ray access: Upload/view/download images
  - Progress photo uploads: Timeline view showing healing
  - Remote PT guidance: Therapist-uploaded instructions + videos
  - Documents: Discharge summary, medication list, clinic contacts
  - Appointment history and upcoming bookings
  - Secure messaging (optional: Django private messages)
- **Tech**:
  - Separate Django app `portal`
  - Per-object RBAC (django-guardian): patients see only their own files
  - File storage in S3/R2 with signed URLs; never public
  - Audit log for all portal actions
  - Session timeout after 15 min inactivity (security)

---

## 8. Legal & Compliance

### Patient Rights Charter
- Right to information
- Right to consent
- Right to quality care
- Right to privacy
- **Tech**: Static Wagtail page; downloadable PDF

### Privacy Policy
- Data collection practices
- HIPAA-equivalent standards
- Photo/testimonial consent process
- Data retention schedule
- **Tech**: Wagtail page; version history; compliance date stamp

### Dispute Resolution
- Mediation process steps
- Arbitration details
- Contact for disputes
- **Tech**: Wagtail page; contact form link

### Licensing & Certifications
- PMDC Certified
- ISO/WHO standards
- Facility accreditation
- **Tech**: Badge images (Wagtail media); certificates/documents (downloadable)

---

## 9. Contact & Booking

### Online Appointment Booking
- **Features**:
  - Interactive calendar showing availability
  - Timezone conversion (detect from browser or user input)
  - Confirm date/time, then details form
  - Confirmation email with ICS attachment
  - SMS reminder (optional)
- **Tech**:
  - Django booking app with Appointment model
  - HTMX-driven multi-step form (avoid full page reloads)
  - `django-timezone-field` for user timezone
  - Celery task: send email/SMS async; generate ICS file
  - Redis throttling: limit bookings per IP/email

### Emergency Hotline
- 24/7 phone numbers (locale-specific)
- **Tech**: Display based on user timezone; clickable tel: links

### Direct Contacts
- WhatsApp (deep link: wa.me/+92...)
- Email: international@hillsclinic.com
- **Tech**: Contact cards with icons; copyable/clickable

### Contact Form
- Name, email, phone, timezone, subject, message
- **Tech**: 
  - HTMX form with client-side validation
  - Server-side sanitization (bleach)
  - Celery task: send to admin + auto-reply
  - Rate limiting: 1 per IP per hour

---

## Database Models (Summary)

### CMS Models (Wagtail)
- `ProcedurePage`: Methods, outcomes, risks, FAQs
- `InternationalCenterPage`: Visa, accommodation, cultural support
- `CostPage`: Pricing, calculator, payment plans
- `RecoveryPage`: Timeline, exercise library, nutrition
- `BlogPage`: Articles with metadata
- `FAQPage`: FAQ items per category
- `SuccessStoryPage`: Case study with consent flags + media

### Core Models (Portal/Booking)
- `User`: Extended Django User; timezone, language preferences
- `Patient`: Linked to User; medical history, consent records
- `Appointment`: Booking slots, confirmation, ICS link
- `PortalUpload`: X-rays, progress photos; consent, audit trail
- `AuditLog`: Immutable log of portal actions (who/what/when)
- `ConsentRecord`: Explicit consent capture for media/testimonials
- `PaymentRecord`: Invoices, payment plan tracking, method

---

## Implementation Roadmap (High-Level)

### Phase 1: CMS & Public Site (Weeks 1–4)
- Set up Wagtail; define page types and models
- Build Home, Procedures, International Center, Cost, Recovery, Articles, Legal pages
- Implement navigation, footer, responsive layouts
- Basic SEO (sitemap.xml, robots.txt, schema.org)

### Phase 2: Booking & Calculator (Weeks 5–6)
- Build booking app: Appointment model, availability logic, HTMX form
- Cost calculator: CMS-configurable ranges, server validation
- Email confirmations + ICS generation (Celery)
- Payment setup (Stripe + wire transfer workflow)

### Phase 3: Patient Portal (Weeks 7–8)
- Auth: OIDC + TOTP MFA setup
- Portal app: Upload, document access, remote PT notes
- Consent lifecycle: Capture, revocation, audit logging
- Secure file serving (signed URLs, virus scanning)

### Phase 4: Success Stories & Media (Weeks 9–10)
- Success story pages with before/after galleries
- Face-blur variants (image processing pipeline in Celery)
- Consent-driven publication (unpublish revoked media)
- Video embedding and optimization

### Phase 5: Polish & Launch (Weeks 11–12)
- Performance tuning (Lighthouse 95+)
- Security hardening (CSP, CORS, rate limiting)
- Accessibility audit (WCAG 2.2 AA)
- Load testing, backup/DR validation
- Staging → Production deployment

---

## Notes
- All content is authored in Wagtail; no hardcoding in templates
- Security headers enforced site-wide
- Consent and audit logs immutable; essential for compliance
- Images optimized to WebP/AVIF; responsive renditions via Wagtail
- Mobile-first Tailwind styles; RTL support baked in
- HTMX for interactivity; minimal JS footprint
