"""
Production email verification settings for Hills Clinic.

Key security features:
- 3-day token expiration (prevents long-lived tokens)
- POST-only confirmation (prevents accidental clicks)
- Login attempt rate limiting (5 attempts per 5 minutes)
- Mandatory email verification (prevents disposable emails)
- Unique email enforcement (prevents duplicate accounts)
- Secure SMTP via Gmail App Password
"""

# Email Verification Flow
# ======================
# 1. User signs up at /accounts/signup/
# 2. Verification email sent to their address
# 3. User clicks link in email (valid for 3 days)
# 4. Redirected to /accounts/confirm-email/ page
# 5. User clicks "Confirm Email" button to finalize
# 6. Account activated, auto-login on confirmation
# 7. Redirected to dashboard

# Rate Limiting
# =============
# - Login attempts: Max 5 failures per 5 minutes
# - Email resend: Uses allauth's built-in limits
# - Signup: No rate limit, but email verification required

# Troubleshooting
# ===============
# Token expired? User can request resend at /accounts/email/
# Wrong email? Can change before confirmation at /accounts/email/
# Never received email? Check spam folder or resend via /accounts/email/

# Production Checklist
# ====================
# [ ] Update SECRET_KEY in .env (use Django's get_random_secret_key())
# [ ] Set DEBUG=False in .env
# [ ] Update ALLOWED_HOSTS for your domain
# [ ] Use HTTPS (set ACCOUNT_DEFAULT_HTTP_PROTOCOL=https)
# [ ] Enable 2FA on Gmail account
# [ ] Test email delivery end-to-end
# [ ] Monitor failed login attempts
# [ ] Set up email bouncing/unsubscribe handling
# [ ] Consider adding reCAPTCHA to signup form
